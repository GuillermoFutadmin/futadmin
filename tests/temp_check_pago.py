import psycopg2

conn=None
try:
    conn = psycopg2.connect("postgresql://postgres:Gd012354R1.@localhost:5432/futadmin")
    cur = conn.cursor()
    # Check last payment for Meteoros 100 (id 138)
    cur.execute("SELECT id, monto, fecha, tipo FROM pagos WHERE inscripcion_id IN (SELECT id FROM inscripciones WHERE equipo_id = 138) ORDER BY id DESC LIMIT 1")
    row = cur.fetchone()
    if row:
        print(f"Último Pago - ID: {row[0]}, Monto: {row[1]}, Fecha: {row[2]}, Tipo: {row[3]}")
    else:
        print("No se encontraron pagos para este equipo.")
    cur.close()
except Exception as e:
    print(f"Error: {e}")
finally:
    if conn:
        conn.close()
