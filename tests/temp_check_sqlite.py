import sqlite3
import os

for db_name in ['futadmin.db', 'database.db']:
    if not os.path.exists(db_name):
        print(f"--- {db_name} no existe ---")
        continue
    print(f"--- {db_name} ---")
    try:
        conn = sqlite3.connect(db_name)
        cur = conn.cursor()
        cur.execute("SELECT id, monto, fecha, tipo FROM pagos ORDER BY id DESC LIMIT 5")
        rows = cur.fetchall()
        for row in rows:
            print(row)
        cur.close()
        conn.close()
    except Exception as e:
        print(f"Error en {db_name}: {e}")
