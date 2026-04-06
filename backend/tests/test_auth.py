"""
Tests for authentication mutations: register and login.

Critical path: these are the entry points for every user session.
"""
import pytest


REGISTER_MUTATION = """
mutation Register($input: RegisterInput!) {
    register(input: $input) {
        user {
            id
            email
            isActive
        }
        accessToken
        tokenType
    }
}
"""

LOGIN_MUTATION = """
mutation Login($input: LoginInput!) {
    login(input: $input) {
        user {
            id
            email
            isActive
        }
        accessToken
        tokenType
    }
}
"""


class TestRegister:
    """Register mutation tests."""

    @pytest.mark.asyncio
    async def test_register_creates_user(self, execute_query):
        """A new user can register and receives a valid JWT."""
        result = await execute_query(
            REGISTER_MUTATION,
            variables={"input": {"email": "new@example.com", "password": "securepass123"}},
        )
        assert result.errors is None, f"GraphQL errors: {result.errors}"

        data = result.data["register"]
        assert data["user"]["email"] == "new@example.com"
        assert data["user"]["isActive"] is True
        assert data["accessToken"]  # non-empty string
        assert data["tokenType"] == "bearer"

    @pytest.mark.asyncio
    async def test_register_duplicate_email_fails(self, execute_query):
        """Registering with an already-taken email returns an error."""
        variables = {"input": {"email": "dup@example.com", "password": "pass123"}}

        # First registration succeeds
        result1 = await execute_query(REGISTER_MUTATION, variables=variables)
        assert result1.errors is None

        # Second registration with same email fails
        result2 = await execute_query(REGISTER_MUTATION, variables=variables)
        assert result2.errors is not None
        assert any("already exists" in str(e) for e in result2.errors)


class TestLogin:
    """Login mutation tests."""

    @pytest.mark.asyncio
    async def test_login_with_valid_credentials(self, execute_query, test_user):
        """A registered user can log in and gets a JWT."""
        result = await execute_query(
            LOGIN_MUTATION,
            variables={"input": {"email": "test@example.com", "password": "testpassword123"}},
        )
        assert result.errors is None, f"GraphQL errors: {result.errors}"

        data = result.data["login"]
        assert data["user"]["email"] == "test@example.com"
        assert data["accessToken"]
        assert data["tokenType"] == "bearer"

    @pytest.mark.asyncio
    async def test_login_with_wrong_password(self, execute_query, test_user):
        """Login with incorrect password returns an error."""
        result = await execute_query(
            LOGIN_MUTATION,
            variables={"input": {"email": "test@example.com", "password": "wrongpassword"}},
        )
        assert result.errors is not None
        assert any("Incorrect email or password" in str(e) for e in result.errors)

    @pytest.mark.asyncio
    async def test_login_nonexistent_user(self, execute_query):
        """Login with an email that does not exist returns an error."""
        result = await execute_query(
            LOGIN_MUTATION,
            variables={"input": {"email": "nobody@example.com", "password": "whatever"}},
        )
        assert result.errors is not None
        assert any("Incorrect email or password" in str(e) for e in result.errors)
