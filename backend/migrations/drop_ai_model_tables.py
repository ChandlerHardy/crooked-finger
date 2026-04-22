"""
Drop ai_model_usage and ai_model_config tables (Phase 3 housekeeping)

These tables were created by the Gemini-era AI cascade that was removed in
Phase 2 (z.ai migration). The ORM models and all callers were deleted; only
the bare tables remain on the server. This migration drops them safely.

Run on OCI:
    cd /home/ubuntu/crooked-finger
    docker-compose -f docker-compose.backend.yml exec backend \
        python migrations/drop_ai_model_tables.py
"""

from sqlalchemy import text


def upgrade(connection):
    """Drop the Gemini-era AI tracking tables."""
    connection.execute(text("DROP TABLE IF EXISTS ai_model_usage"))
    connection.execute(text("DROP TABLE IF EXISTS ai_model_config"))
    print("Done: ai_model_usage and ai_model_config dropped (if they existed)")


def downgrade(connection):
    """Restore tables — run add_ai_model_config.py to recreate ai_model_config."""
    # ai_model_usage had no dedicated migration; recreate minimal schema here.
    connection.execute(text("""
        CREATE TABLE IF NOT EXISTS ai_model_usage (
            id SERIAL PRIMARY KEY,
            model_name VARCHAR(255),
            request_count INTEGER DEFAULT 0,
            total_input_characters INTEGER DEFAULT 0,
            total_output_characters INTEGER DEFAULT 0,
            total_input_tokens INTEGER DEFAULT 0,
            total_output_tokens INTEGER DEFAULT 0,
            date DATE DEFAULT CURRENT_DATE,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """))
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
    print("Downgrade complete: ai_model_usage and ai_model_config recreated")


if __name__ == "__main__":
    import sys
    import os
    sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

    from app.database.connection import engine

    with engine.connect() as conn:
        with conn.begin():
            upgrade(conn)
            print("Migration completed!")
