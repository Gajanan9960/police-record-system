import sqlite3
import os

# Path to database
db_path = os.path.join('instance', 'police.db')

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

print(f"Migrating database at {db_path}...")

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Check if column already exists
    cursor.execute("PRAGMA table_info(user)")
    columns = [info[1] for info in cursor.fetchall()]
    
    if 'email' in columns:
        print("Column 'email' already exists in 'user' table.")
    else:
        print("Adding 'email' column to 'user' table...")
        cursor.execute("ALTER TABLE user ADD COLUMN email VARCHAR(120)")
        cursor.execute("CREATE UNIQUE INDEX IF NOT EXISTS ix_user_email ON user (email)")
        conn.commit()
        print("Migration successful!")
        
    conn.close()

except Exception as e:
    print(f"Migration failed: {e}")
