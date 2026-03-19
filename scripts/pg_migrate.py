import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

DB_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
print(f"Usando URI: {DB_URI}")

try:
    conn = psycopg2.connect(DB_URI)
    conn.autocommit = True
    cursor = conn.cursor()
    
    # 1. Verificar columnas en 'equipos'
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name = 'equipos';
    """)
    columns = [row[0] for row in cursor.fetchall()]
    print(f"Columnas en 'equipos': {columns}")
    
    # 2. Agregar 'uid' si falta
    if 'uid' not in columns:
        print("Agregando columna 'uid' a 'equipos'...")
        cursor.execute("ALTER TABLE equipos ADD COLUMN uid VARCHAR(20) UNIQUE;")
    else:
        print("Columna 'uid' ya existe.")
        
    # 3. Intentar poblar UIDs si hay nulos
    cursor.execute("SELECT id FROM equipos WHERE uid IS NULL;")
    ids_sin_uid = cursor.fetchall()
    if ids_sin_uid:
        print(f"Poblando {len(ids_sin_uid)} UIDs...")
        import random, string
        chars = string.ascii_uppercase + string.digits
        for (eid,) in ids_sin_uid:
            while True:
                new_uid = ''.join(random.choices(chars, k=15))
                # Verificar unicidad (simplificado)
                cursor.execute("SELECT 1 FROM equipos WHERE uid = %s", (new_uid,))
                if not cursor.fetchone():
                    cursor.execute("UPDATE equipos SET uid = %s WHERE id = %s", (new_uid, eid))
                    break
        print("UIDs poblados.")

    conn.close()
    print("Migración PostgreSQL completada.")

except Exception as e:
    print(f"Error en migración PostgreSQL: {e}")
