import psycopg2

conn=None
try:
    conn = psycopg2.connect("postgresql://postgres:Gd012354R1.@localhost:5432/futadmin")
    cur = conn.cursor()
    cur.execute("SELECT column_name FROM information_schema.columns WHERE table_name = 'equipos'")
    columns = [col[0] for col in cur.fetchall()]
    print(f"Columnas en 'equipos': {columns}")
    
    cur.execute("SELECT id, nombre, email FROM equipos WHERE nombre ILIKE '%Meteoros%'")
    rows = cur.fetchall()
    for row in rows:
        print(f"ID: {row[0]}, Nombre: {row[1]}, Email: '{row[2]}'")
    cur.close()
except Exception as e:
    print(f"Error: {e}")
finally:
    if conn:
        conn.close()
