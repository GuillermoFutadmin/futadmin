import psycopg2

conn=None
try:
    conn = psycopg2.connect("postgresql://postgres:Gd012354R1.@localhost:5432/futadmin")
    cur = conn.cursor()
    cur.execute("SELECT id, jornada, equipo_local_id, equipo_visitante_id FROM partidos WHERE torneo_id = 12 AND jornada = 5")
    rows = cur.fetchall()
    for row in rows:
        print(f"ID: {row[0]}, J: {row[1]}, Local: {row[2]}, Visitante: {row[3]}")
    if not rows:
        print("No se encontraron partidos para J5 en este torneo.")
    cur.close()
except Exception as e:
    print(f"Error: {e}")
finally:
    if conn:
        conn.close()
