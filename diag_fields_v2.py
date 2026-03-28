import os
from dotenv import load_dotenv
load_dotenv()

from app import app
from models import Torneo, Cancha, CanchaDetalle

with app.app_context():
    # Use torneo ID 19 from the previous error log screenshot
    t = Torneo.query.get(19)
    if t:
        print(f"Torneo: {t.id} - {t.nombre}")
        print(f"Liga ID: {t.liga_id}")
        
        canchas = Cancha.query.filter_by(liga_id=t.liga_id).all()
        print(f"\nSedes (Cancha) en Liga {t.liga_id}:")
        for c in canchas:
            print(f" - ID: {c.id}, Nombre: {c.nombre}")
            
        detalles = CanchaDetalle.query.filter_by(liga_id=t.liga_id).all()
        print(f"\nCampos (CanchaDetalle) en Liga {t.liga_id}:")
        for d in detalles:
            print(f" - ID: {d.id}, Nombre: {d.nombre}, Sede ID: {d.sede_id}, Activa: {d.activa}")
    else:
        print("Torneo 19 not found.")
