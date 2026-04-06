"""
Tests for conversation mutations and queries.

Critical path: conversations are the primary container for chat messages
and sync across web and iOS clients.
"""
import pytest


CREATE_CONVERSATION = """
mutation CreateConversation($input: CreateConversationInput!) {
    createConversation(input: $input) {
        id
        title
        userId
        messageCount
    }
}
"""

LIST_CONVERSATIONS = """
query Conversations {
    conversations {
        id
        title
        userId
        messageCount
    }
}
"""

DELETE_CONVERSATION = """
mutation DeleteConversation($conversationId: Int!) {
    deleteConversation(conversationId: $conversationId)
}
"""


class TestCreateConversation:
    """Create conversation mutation tests."""

    @pytest.mark.asyncio
    async def test_create_conversation_authenticated(self, execute_query, test_user):
        """An authenticated user can create a conversation."""
        result = await execute_query(
            CREATE_CONVERSATION,
            variables={"input": {"title": "My Granny Square Chat"}},
            user=test_user,
        )
        assert result.errors is None, f"GraphQL errors: {result.errors}"

        data = result.data["createConversation"]
        assert data["title"] == "My Granny Square Chat"
        assert data["userId"] == test_user.id
        assert data["messageCount"] == 0

    @pytest.mark.asyncio
    async def test_create_conversation_default_title(self, execute_query, test_user):
        """A conversation created without a title gets the default."""
        result = await execute_query(
            CREATE_CONVERSATION,
            variables={"input": {}},
            user=test_user,
        )
        assert result.errors is None, f"GraphQL errors: {result.errors}"
        assert result.data["createConversation"]["title"] == "New Chat"

    @pytest.mark.asyncio
    async def test_create_conversation_unauthenticated(self, execute_query):
        """Creating a conversation without auth returns an error."""
        result = await execute_query(
            CREATE_CONVERSATION,
            variables={"input": {"title": "Sneaky"}},
            user=None,
        )
        assert result.errors is not None
        assert any("Authentication required" in str(e) for e in result.errors)


class TestListConversations:
    """Conversation listing query tests."""

    @pytest.mark.asyncio
    async def test_list_conversations_returns_user_conversations(
        self, execute_query, test_user
    ):
        """Listing conversations returns only the authenticated user's data."""
        # Create two conversations
        await execute_query(
            CREATE_CONVERSATION,
            variables={"input": {"title": "Chat 1"}},
            user=test_user,
        )
        await execute_query(
            CREATE_CONVERSATION,
            variables={"input": {"title": "Chat 2"}},
            user=test_user,
        )

        result = await execute_query(LIST_CONVERSATIONS, user=test_user)
        assert result.errors is None, f"GraphQL errors: {result.errors}"

        conversations = result.data["conversations"]
        assert len(conversations) == 2
        titles = {c["title"] for c in conversations}
        assert titles == {"Chat 1", "Chat 2"}

    @pytest.mark.asyncio
    async def test_list_conversations_unauthenticated_returns_empty(self, execute_query):
        """An unauthenticated request gets an empty list, not an error."""
        result = await execute_query(LIST_CONVERSATIONS, user=None)
        assert result.errors is None
        assert result.data["conversations"] == []


class TestDeleteConversation:
    """Delete conversation mutation tests."""

    @pytest.mark.asyncio
    async def test_delete_conversation(self, execute_query, test_user):
        """An authenticated user can delete their own conversation."""
        # Create a conversation
        create_result = await execute_query(
            CREATE_CONVERSATION,
            variables={"input": {"title": "To Be Deleted"}},
            user=test_user,
        )
        conv_id = create_result.data["createConversation"]["id"]

        # Delete it
        delete_result = await execute_query(
            DELETE_CONVERSATION,
            variables={"conversationId": conv_id},
            user=test_user,
        )
        assert delete_result.errors is None
        assert delete_result.data["deleteConversation"] is True

        # Verify it is gone
        list_result = await execute_query(LIST_CONVERSATIONS, user=test_user)
        assert len(list_result.data["conversations"]) == 0
