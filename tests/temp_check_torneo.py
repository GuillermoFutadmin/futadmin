import psycopg2

conn=None
try:
    conn = psycopg2.connect("postgresql://postgres:Gd012354R1.@localhost:5432/futadmin")
    cur = conn.cursor()
    cur.execute("SELECT id, nombre, liga_id FROM torneos WHERE nombre ILIKE '%Municipal%'")
    rows = cur.fetchall()
    for row in rows:
        print(f"ID: {row[0]}, Nombre: {row[1]}, LigaID: {row[2]}")
    if not rows:
        print("No se encontró el torneo.")
    cur.close()
except Exception as e:
    print(f"Error: {e}")
finally:
    if conn:
        conn.close()
