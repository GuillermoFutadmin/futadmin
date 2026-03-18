import sqlite3
import os

def migrate_db(db_path):
    if not os.path.exists(db_path):
        print(f"No se encontró {db_path}")
        return
    
    print(f"Migrando {db_path}...")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Obtener columnas actuales de 'equipos'
    cursor.execute("PRAGMA table_info(equipos);")
    columns = [row[1] for row in cursor.fetchall()]
    
    # 2. Agregar columnas faltantes
    missing_cols = [
        ("uid", "VARCHAR(20)"),
        ("email", "VARCHAR(100)"),
        ("colonia", "VARCHAR(100)"),
        ("colonia_geojson", "TEXT"),
        ("grupo", "VARCHAR(50)"),
        ("liga_id", "INTEGER")
    ]
    
    for col_name, col_type in missing_cols:
        if col_name not in columns:
            print(f"Agregando columna {col_name}...")
            try:
                cursor.execute(f"ALTER TABLE equipos ADD COLUMN {col_name} {col_type};")
            except Exception as e:
                print(f"Error agregando {col_name}: {e}")
        else:
            print(f"Columna {col_name} ya existe.")
            
    conn.commit()
    conn.close()
    print("Migración completada.")

# Intentar con ambos posibles archivos
migrate_db('futadmin.db')
migrate_db('instance/futadmin.db')
