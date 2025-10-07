"""
Add ai_model_config table for persisting AI model configuration

This migration:
1. Creates the ai_model_config table with JSON column for model_priority_order
2. Creates index on selected_model for performance
"""

from sqlalchemy import text

def upgrade(connection):
    """Add ai_model_config table"""

    # Create ai_model_config table
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS ai_model_config (
            id SERIAL PRIMARY KEY,
            selected_model VARCHAR(255),
            model_priority_order JSONB DEFAULT '[]'::jsonb,
            provider_preference VARCHAR(50) DEFAULT 'auto',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """))

    # Create index for selected_model
    connection.execute(text("""
        CREATE INDEX IF NOT EXISTS idx_ai_model_config_selected_model
        ON ai_model_config(selected_model)
    """))

    print("✅ AI Model Config table created successfully")

def downgrade(connection):
    """Remove ai_model_config table"""

    # Drop index
    connection.execute(text("""
        DROP INDEX IF EXISTS idx_ai_model_config_selected_model
    """))

    # Drop table
    connection.execute(text("""
        DROP TABLE IF EXISTS ai_model_config
    """))

    print("✅ AI Model Config table removed successfully")

if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

    from app.database.connection import engine

    with engine.connect() as conn:
        with conn.begin():
            upgrade(conn)
            print("Migration completed!")
