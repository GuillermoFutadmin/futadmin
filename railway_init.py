import os
from app import app, db
from models import Usuario, Liga, Configuracion
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

def init():
    with app.app_context():
        print("Iniciando creación de tablas en PostgreSQL...")
        db.create_all()
        print("Tablas creadas exitosamente.")

        # Verificar si ya existe el admin
        admin_email = 'admin@futadmin.com'
        admin = Usuario.query.filter_by(email=admin_email).first()
        if not admin:
            print(f"Creando usuario administrador: {admin_email}")
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
            print("Usuario administrador creado.")
        else:
            print("El usuario administrador ya existe.")
            
        # Crear configuración básica si no existe
        privacy = Configuracion.query.get('privacy_policy')
        if not privacy:
            db.session.add(Configuracion(clave='privacy_policy', valor='Política de Privacidad de FutAdmin Pro.'))
            db.session.commit()
            print("Configuración inicial creada.")

if __name__ == "__main__":
    init()
