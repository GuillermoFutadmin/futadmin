import sqlite3
import os

db_files = ['database.db', 'futadmin.db', 'instance/futadmin.db']

def check_db(db_path):
    if not os.path.exists(db_path):
        return f"{db_path}: No existe"
    
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [t[0] for t in cursor.fetchall()]
        
        counts = {}
        for t in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {t}")
            counts[t] = cursor.fetchone()[0]
        
        conn.close()
        return f"{db_path}: {counts}"
    except Exception as e:
        return f"{db_path}: Error ({e})"

print("--- REVISIÓN EXHAUSTIVA DE BASES DE DATOS LOCALES ---")
for dbf in db_files:
    print(check_db(dbf))
