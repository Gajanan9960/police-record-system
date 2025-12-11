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
    
    # 1. Update Case table
    print("Checking 'case' table...")
    cursor.execute('PRAGMA table_info("case")')
    columns = [info[1] for info in cursor.fetchall()]
    print(f"Columns in 'case': {columns}")
    
    if 'approved_by_id' not in columns:
        print("Adding 'approved_by_id' to 'case' table...")
        cursor.execute('ALTER TABLE "case" ADD COLUMN approved_by_id INTEGER REFERENCES user(id)')
        print("Added 'approved_by_id'.")
    else:
        print("'approved_by_id' already exists.")
    
    # 2. Update CaseEvidence table
    print("Checking 'case_evidence' table...")
    cursor.execute('PRAGMA table_info("case_evidence")')
    columns = [info[1] for info in cursor.fetchall()]
    
    if 'verified_by_id' not in columns:
        print("Adding 'verified_by_id' to 'case_evidence' table...")
        cursor.execute('ALTER TABLE "case_evidence" ADD COLUMN verified_by_id INTEGER REFERENCES user(id)')
        
    if 'is_locked' not in columns:
        print("Adding 'is_locked' to 'case_evidence' table...")
        cursor.execute('ALTER TABLE "case_evidence" ADD COLUMN is_locked BOOLEAN DEFAULT 0')

    # 3. Create AuditLog table
    print("Checking 'audit_log' table...")
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='audit_log'")
    if not cursor.fetchone():
        print("Creating 'audit_log' table...")
        cursor.execute("""
            CREATE TABLE audit_log (
                id INTEGER PRIMARY KEY,
                user_id INTEGER NOT NULL,
                action VARCHAR(100) NOT NULL,
                target_type VARCHAR(50),
                target_id INTEGER,
                details TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY(user_id) REFERENCES user(id)
            )
        """)
    else:
        print("'audit_log' table already exists.")

    conn.commit()
    print("Migration successful!")
        
    conn.close()

except Exception as e:
    print(f"Migration failed: {e}")
    import traceback
    traceback.print_exc()
