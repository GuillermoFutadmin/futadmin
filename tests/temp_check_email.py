import os
import sys
# Añadir el directorio raíz al path para poder importar app y models
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import app
from models import Equipo

with app.app_context():
    eq = Equipo.query.filter(Equipo.nombre.ilike('%Meteoros%')).first()
    if eq:
        print(f"ID: {eq.id}")
        print(f"Nombre: {eq.nombre}")
        print(f"Responsable: {eq.responsable}")
        print(f"Email: '{eq.email}'")
    else:
        print("Equipo 'Meteoros' no encontrado.")
