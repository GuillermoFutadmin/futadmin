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
            
            print("Paso 1: Aplicando migraciones a PostgreSQL...")
            try:
                from flask_migrate import upgrade
                upgrade()
                print("Éxito: Migraciones aplicadas correctamente.")
            except Exception as migrate_e:
                print(f"Aviso: Falló o no configurado Flask-Migrate ({migrate_e}). Ejecutando db.create_all() como fallback.")
                db.create_all()

            # Verificar y crear administradores
            for admin_email in ['admin@futadmin.com', 'admin@adminfutbol.com']:
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
