import strawberry
from datetime import datetime
from typing import Optional
from strawberry.types import Info
from app.database.connection import get_db
from app.database import models
from app.schemas.types import (
    User, AuthResponse, CrochetProject,
    RegisterInput, LoginInput, CreateProjectInput
)
from app.utils.auth import (
    get_password_hash, authenticate_user, create_access_token
)
from app.core.config import settings

@strawberry.type
class Mutation:
    @strawberry.field
    async def register(
        self,
        input: RegisterInput
    ) -> AuthResponse:
        """Register a new user"""
        db = next(get_db())
        try:
            # Check if user already exists
            existing_user = db.query(models.User).filter(models.User.email == input.email).first()
            if existing_user:
                raise Exception("User with this email already exists")

            # Create new user
            hashed_password = get_password_hash(input.password)
            db_user = models.User(
                email=input.email,
                hashed_password=hashed_password,
                is_active=True,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            db.add(db_user)
            db.commit()
            db.refresh(db_user)

            # Create access token
            access_token = create_access_token(data={"sub": db_user.email})

            return AuthResponse(
                user=User(
                    id=db_user.id,
                    email=db_user.email,
                    is_active=db_user.is_active,
                    is_verified=db_user.is_verified,
                    is_admin=db_user.is_admin,
                    created_at=db_user.created_at,
                    updated_at=db_user.updated_at,
                    last_login=db_user.last_login
                ),
                access_token=access_token,
                token_type="bearer"
            )
        finally:
            db.close()

    @strawberry.field
    async def login(
        self,
        input: LoginInput
    ) -> AuthResponse:
        """Login user"""
        db = next(get_db())
        try:
            user = authenticate_user(db, input.email, input.password)
            if not user:
                raise Exception("Incorrect email or password")

            # Update last login
            user.last_login = datetime.utcnow()
            db.commit()

            # Create access token
            access_token = create_access_token(data={"sub": user.email})

            return AuthResponse(
                user=User(
                    id=user.id,
                    email=user.email,
                    is_active=user.is_active,
                    is_verified=user.is_verified,
                    is_admin=user.is_admin,
                    created_at=user.created_at,
                    updated_at=user.updated_at,
                    last_login=user.last_login
                ),
                access_token=access_token,
                token_type="bearer"
            )
        finally:
            db.close()

    @strawberry.field
    async def create_project(
        self,
        info: Info,
        input: CreateProjectInput
    ) -> CrochetProject:
        """Create a new crochet project"""
        user = info.context.get("user")
        if not user:
            raise Exception("Authentication required")

        db = next(get_db())
        try:
            db_project = models.CrochetProject(
                name=input.name,
                pattern_text=input.pattern_text,
                difficulty_level=input.difficulty_level,
                estimated_time=input.estimated_time,
                yarn_weight=input.yarn_weight,
                hook_size=input.hook_size,
                notes=input.notes,
                is_completed=False,
                user_id=user.id,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )

            db.add(db_project)
            db.commit()
            db.refresh(db_project)

            return CrochetProject(
                id=db_project.id,
                name=db_project.name,
                pattern_text=db_project.pattern_text,
                translated_text=db_project.translated_text,
                difficulty_level=db_project.difficulty_level,
                estimated_time=db_project.estimated_time,
                yarn_weight=db_project.yarn_weight,
                hook_size=db_project.hook_size,
                notes=db_project.notes,
                is_completed=db_project.is_completed,
                user_id=db_project.user_id,
                created_at=db_project.created_at,
                updated_at=db_project.updated_at
            )
        finally:
            db.close()