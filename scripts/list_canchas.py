from app import app, db
from models import Cancha

with app.app_context():
    canchas = Cancha.query.all()
    for c in canchas:
        print(f"ID: {c.id}, Nombre: {c.nombre}, Liga ID: {c.liga_id}")
