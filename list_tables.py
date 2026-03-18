import sqlite3
import os

db_path = 'instance/futadmin.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    print(f"Tablas en {db_path}:")
    for t in tables:
        print(t[0])
    conn.close()
