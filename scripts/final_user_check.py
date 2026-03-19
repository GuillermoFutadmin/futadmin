from app import app
from models import Usuario
with app.app_context():
    u = Usuario.query.filter(Usuario.email.ilike('lector_ligamayor@futadmin.com')).first()
    if u:
        print(f"ENCONTRADO: {u.email} (ID: {u.id}, Rol: {u.rol})")
    else:
        print("NO ENCONTRADO (Incluso con ilike)")
        # Listar parecidos
        all_u = Usuario.query.all()
        print("Correos existentes:")
        for x in all_u:
            print(f"- {x.email}")
