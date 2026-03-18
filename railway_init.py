import os
from app import app
from models import db, Usuario, Liga, Configuracion, bcrypt
import sys

def init():
    with app.app_context():
        try:
            print("--- Iniciando Script de Inicialización ---")
            print(f"DATABASE_URL: {os.getenv('SQLALCHEMY_DATABASE_URI')[:20]}...")
            
            print("Paso 1: Creando tablas en PostgreSQL...")
            db.create_all()
            print("Éxito: Tablas creadas o ya existentes.")

            # Verificar si ya existe el admin
            admin_email = 'admin@futadmin.com'
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
                print("Éxito: Usuario administrador creado.")
            else:
                print("Paso 2: El usuario administrador ya existe.")
                
            # Crear configuración básica si no existe
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
            # No salimos con error para que gunicorn al menos intente arrancar, 
            # pero el log dirá qué falló.
            sys.exit(0) 

if __name__ == "__main__":
    init()
