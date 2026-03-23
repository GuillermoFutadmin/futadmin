import os
from app import app
from models import db, Usuario, Liga, Configuracion, bcrypt
import sys

def init():
    with app.app_context():
        try:
            print("--- Iniciando Script de Inicialización ---")
            db_url = app.config.get('SQLALCHEMY_DATABASE_URI') or "None"
            print(f"DATABASE_URI detectada: {db_url[:40]}...")
            
            # 1. Manual Migrations Fallback (Execute before any ORM queries)
            print("Paso 1: Aplicando mutaciones manuales (Fallback)...")
            manual_queries = [
                "ALTER TABLE jugadores ADD COLUMN IF NOT EXISTS fecha_nacimiento DATE;",
                "ALTER TABLE alumnos_entrenamiento ADD COLUMN IF NOT EXISTS fecha_nacimiento DATE;",
                "ALTER TABLE torneos ADD COLUMN IF NOT EXISTS archived BOOLEAN DEFAULT FALSE;",
                "ALTER TABLE usuarios ADD COLUMN IF NOT EXISTS telegram_id VARCHAR(50) UNIQUE;",
                "ALTER TABLE equipos ADD COLUMN IF NOT EXISTS puntos_legacy INTEGER DEFAULT 0;",
                "ALTER TABLE equipos ADD COLUMN IF NOT EXISTS goles_f_legacy INTEGER DEFAULT 0;",
                "ALTER TABLE equipos ADD COLUMN IF NOT EXISTS goles_c_legacy INTEGER DEFAULT 0;",
                "ALTER TABLE equipos ADD COLUMN IF NOT EXISTS amarillas_legacy INTEGER DEFAULT 0;",
                "ALTER TABLE equipos ADD COLUMN IF NOT EXISTS rojas_legacy INTEGER DEFAULT 0;",
                "ALTER TABLE jugadores ADD COLUMN IF NOT EXISTS goles_legacy INTEGER DEFAULT 0;",
                "ALTER TABLE jugadores ADD COLUMN IF NOT EXISTS amarillas_legacy INTEGER DEFAULT 0;",
                "ALTER TABLE jugadores ADD COLUMN IF NOT EXISTS rojas_legacy INTEGER DEFAULT 0;",
                "ALTER TABLE equipos ADD COLUMN IF NOT EXISTS saldo_arbitraje_legacy FLOAT DEFAULT 0.0;",
                "ALTER TABLE pagos ADD COLUMN IF NOT EXISTS comprobante_url VARCHAR(255);"
            ]
            
            for q in manual_queries:
                try:
                    db.session.execute(db.text(q))
                    db.session.commit()
                    print(f"Éxito: {q}")
                except Exception as e:
                    db.session.rollback()
                    print(f"Nota: {q} falló o ya existe: {e}")

            # 2. Flask-Migrate Upgrade (If available)
            try:
                from flask_migrate import upgrade
                upgrade()
                print("Éxito: Flask-Migrate upgrade completado.")
            except Exception as migrate_e:
                print(f"Aviso: Flask-Migrate no disponible o falló: {migrate_e}")
                db.create_all()

            # 3. Verificar y crear administradores
            for admin_email in ['admin@futadmin.com']:
                admin = Usuario.query.filter_by(email=admin_email).first()
                if not admin:
                    print(f"Paso 2: Creando usuario administrador: {admin_email}")
                    hashed_pw = bcrypt.generate_password_hash('Gd012354R1.').decode('utf-8')
                    new_admin = Usuario(
                        nombre='Administrador Global',
                        email=admin_email,
                        password_hash=hashed_pw,
                        rol='admin',
                        activo=True
                    )
                    db.session.add(new_admin)
                    db.session.commit()
                    print(f"Éxito: Usuario {admin_email} creado.")
                else:
                    print(f"Paso 2: El usuario {admin_email} ya existe.")
                
            # 4. Crear configuración básica si no existe
            privacy = Configuracion.query.get('privacy_policy')
            if not privacy:
                print("Paso 3: Creando configuración inicial...")
                db.session.add(Configuracion(clave='privacy_policy', valor='Política de Privacidad de FutAdmin Pro.'))
                db.session.commit()
                print("Éxito: Configuración inicial creada.")
            else:
                print("Paso 3: Configuración inicial ya existe.")

            print("--- Inicialización Completada con Éxito ---")
            
        except Exception as e:
            print(f"ERROR CRÍTICO EN INICIALIZACIÓN: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(0) 

if __name__ == "__main__":
    init()
