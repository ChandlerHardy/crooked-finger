#!/usr/bin/env python3
"""
Database migration: Add image_data column to crochet_projects table
Run this script to add image support to existing databases

Usage: python migrations/add_image_data_column.py
"""

from sqlalchemy import create_engine, text
from app.core.config import settings

def migrate():
    """Add image_data column to crochet_projects table"""
    print("🔄 Running migration: add_image_data_column")

    engine = create_engine(settings.database_url)

    with engine.connect() as conn:
        # Check if column already exists
        result = conn.execute(text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name='crochet_projects' AND column_name='image_data'
        """))

        if result.fetchone():
            print("✅ Column 'image_data' already exists, skipping migration")
            return

        # Add the column
        print("📝 Adding 'image_data' column to crochet_projects table...")
        conn.execute(text("""
            ALTER TABLE crochet_projects
            ADD COLUMN image_data TEXT
        """))
        conn.commit()

        print("✅ Migration completed successfully!")
        print("📸 Projects can now store image data as JSON arrays of base64 strings")

if __name__ == "__main__":
    try:
        migrate()
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        exit(1)
