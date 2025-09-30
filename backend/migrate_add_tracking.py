"""Migration script to add character/token tracking columns to ai_model_usage table"""
import sqlite3
import os

# Find the database file
possible_paths = [
    './crooked_finger.db',
    '../crooked_finger.db',
    'crooked_finger.db',
    'backend/crooked_finger.db'
]

db_path = None
for path in possible_paths:
    if os.path.exists(path):
        db_path = path
        break

if not db_path:
    print("❌ Database file not found. Searching...")
    # Search for the file
    for root, dirs, files in os.walk('/Users/chandlerhardy/repos/crooked-finger'):
        if 'crooked_finger.db' in files:
            db_path = os.path.join(root, 'crooked_finger.db')
            print(f"✅ Found database at: {db_path}")
            break

if not db_path:
    print("❌ Could not find crooked_finger.db")
    exit(1)

print(f"📊 Migrating database at: {db_path}")

# Connect to database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check if columns already exist
cursor.execute("PRAGMA table_info(ai_model_usage)")
columns = [col[1] for col in cursor.fetchall()]

print(f"Current columns: {columns}")

# Add columns if they don't exist
columns_to_add = [
    ('total_input_characters', 'INTEGER DEFAULT 0'),
    ('total_output_characters', 'INTEGER DEFAULT 0'),
    ('total_input_tokens', 'INTEGER DEFAULT 0'),
    ('total_output_tokens', 'INTEGER DEFAULT 0')
]

for col_name, col_type in columns_to_add:
    if col_name not in columns:
        try:
            cursor.execute(f"ALTER TABLE ai_model_usage ADD COLUMN {col_name} {col_type}")
            print(f"✅ Added column: {col_name}")
        except sqlite3.OperationalError as e:
            print(f"⚠️  Could not add {col_name}: {e}")
    else:
        print(f"ℹ️  Column {col_name} already exists")

conn.commit()
conn.close()

print("✅ Migration complete!")
