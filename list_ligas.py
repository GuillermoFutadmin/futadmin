from app import app
from models import Liga
with app.app_context():
    ligas = Liga.query.all()
    for l in ligas:
        print(f"ID: {l.id}, Name: {l.nombre}, TipoCliente: {l.tipo_cliente}")
