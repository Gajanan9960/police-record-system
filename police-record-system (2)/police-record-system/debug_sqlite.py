import sqlite3
import os

db_path = os.path.join('instance', 'police.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

try:
    print("Trying: ALTER TABLE \"case\" ADD COLUMN approved_by_id INTEGER REFERENCES user(id) ...")
    cursor.execute('ALTER TABLE "case" ADD COLUMN approved_by_id INTEGER REFERENCES user(id)')
    print("Success with double quotes and FK!")
    conn.rollback()
except Exception as e:
    print(f"Failed with double quotes and FK: {e}")

try:
    print("Trying: ALTER TABLE `case` ...")
    cursor.execute('ALTER TABLE `case` ADD COLUMN test_col2 INTEGER')
    print("Success with backticks!")
    conn.rollback()
except Exception as e:
    print(f"Failed with backticks: {e}")

try:
    print("Trying: ALTER TABLE [case] ...")
    cursor.execute('ALTER TABLE [case] ADD COLUMN test_col3 INTEGER')
    print("Success with brackets!")
    conn.rollback()
except Exception as e:
    print(f"Failed with brackets: {e}")

conn.close()
