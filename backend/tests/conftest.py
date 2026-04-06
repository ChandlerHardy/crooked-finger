"""
Test infrastructure for Crooked Finger backend.

Sets up an in-memory SQLite database and provides fixtures for:
- Database sessions (isolated per test)
- Authenticated GraphQL context
- FastAPI test client
"""
import os

# Must set DATABASE_URL before any app module is imported, because
# app.database.connection creates the SQLAlchemy engine at import time.
os.environ["DATABASE_URL"] = "sqlite://"
os.environ["SECRET_KEY"] = "test-secret-key-for-testing"
os.environ["ADMIN_SECRET"] = "test-admin-secret"
os.environ["ENVIRONMENT"] = "test"
os.environ["DEBUG"] = "True"

import pytest
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session

from app.database.models import Base
from app.database import connection as db_connection
from app.utils.auth import get_password_hash, create_access_token


# ---------------------------------------------------------------------------
# SQLite in-memory engine shared across a test session
# ---------------------------------------------------------------------------

_test_engine = create_engine(
    "sqlite://",
    connect_args={"check_same_thread": False},
)

# Enable WAL-like behavior: SQLite needs PRAGMA foreign_keys per connection
@event.listens_for(_test_engine, "connect")
def _set_sqlite_pragma(dbapi_conn, connection_record):
    cursor = dbapi_conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON")
    cursor.close()

TestSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=_test_engine,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def _create_tables():
    """Create all tables before each test, drop after."""
    Base.metadata.create_all(bind=_test_engine)
    yield
    Base.metadata.drop_all(bind=_test_engine)


@pytest.fixture()
def db_session() -> Session:
    """Provide a clean database session for a test."""
    session = TestSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        session.close()


@pytest.fixture(autouse=True)
def _patch_get_db(monkeypatch):
    """
    Monkeypatch get_db everywhere it is imported so that mutations
    and queries use the test database instead of the real one.
    """
    def _override_get_db():
        session = TestSessionLocal()
        try:
            yield session
        finally:
            session.close()

    # Patch in the connection module (canonical location)
    monkeypatch.setattr(db_connection, "get_db", _override_get_db)

    # Patch everywhere get_db was imported by value
    from app.schemas import mutations as mut_mod
    from app.schemas import queries as qry_mod

    monkeypatch.setattr(mut_mod, "get_db", _override_get_db)
    monkeypatch.setattr(qry_mod, "get_db", _override_get_db)


# ---------------------------------------------------------------------------
# User helpers
# ---------------------------------------------------------------------------

@pytest.fixture()
def test_user(db_session):
    """Create and return a test user in the database."""
    from app.database.models import User
    from datetime import datetime

    user = User(
        email="test@example.com",
        hashed_password=get_password_hash("testpassword123"),
        is_active=True,
        is_verified=False,
        is_admin=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture()
def auth_token(test_user) -> str:
    """Return a valid JWT for the test user."""
    return create_access_token(data={"sub": test_user.email})


@pytest.fixture()
def auth_headers(auth_token) -> dict:
    """Return HTTP headers with a valid Bearer token."""
    return {"Authorization": f"Bearer {auth_token}"}


# ---------------------------------------------------------------------------
# Strawberry schema execution helper
# ---------------------------------------------------------------------------

@pytest.fixture()
def execute_query():
    """
    Return an async callable that executes a GraphQL operation against
    the Strawberry schema with optional authentication context.
    """
    from app.schemas.schema import schema

    async def _execute(query: str, variables: dict = None, user=None):
        context = {}
        if user:
            context["user"] = user
        result = await schema.execute(
            query,
            variable_values=variables,
            context_value=context,
        )
        return result

    return _execute


# ---------------------------------------------------------------------------
# FastAPI test client
# ---------------------------------------------------------------------------

@pytest.fixture()
def client():
    """Provide a synchronous TestClient for the FastAPI app."""
    from starlette.testclient import TestClient
    from app.main import app

    with TestClient(app) as c:
        yield c
