"""
Add conversations table and update chat_messages

This migration:
1. Creates the conversations table
2. Adds conversation_id column to chat_messages
3. Creates indexes for performance
"""

from sqlalchemy import text

def upgrade(connection):
    """Add conversations table and conversation_id to chat_messages"""

    # Create conversations table
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS conversations (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) DEFAULT 'New Chat',
            user_id INTEGER REFERENCES users(id),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """))

    # Add conversation_id column to chat_messages
    connection.execute(text("""
        ALTER TABLE chat_messages
        ADD COLUMN IF NOT EXISTS conversation_id INTEGER REFERENCES conversations(id)
    """))

    # Create indexes for performance
    connection.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_conversations_user_id
        ON conversations(user_id)
    """))

    connection.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_chat_messages_conversation_id
        ON chat_messages(conversation_id)
    """))

    print("✅ Conversations table created successfully")

def downgrade(connection):
    """Remove conversations table and conversation_id column"""

    # Drop indexes
    connection.execute(text("""
        DROP INDEX IF EXISTS idx_chat_messages_conversation_id
    """))

    connection.execute(text("""
        DROP INDEX IF EXISTS idx_conversations_user_id
    """))

    # Drop conversation_id column from chat_messages
    connection.execute(text("""
        ALTER TABLE chat_messages
        DROP COLUMN IF EXISTS conversation_id
    """))

    # Drop conversations table
    connection.execute(text("""
        DROP TABLE IF EXISTS conversations
    """))

    print("✅ Conversations table removed successfully")

if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

    from app.database.connection import engine

    with engine.connect() as conn:
        with conn.begin():
            upgrade(conn)
            print("Migration completed!")
