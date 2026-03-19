from app import app
from models import db, Liga, Torneo, Equipo, Jugador

def extract_combos():
    with app.app_context():
        ligas = Liga.query.all()
        for liga in ligas:
            equipos_qty = len(Equipo.query.filter_by(liga_id=liga.id).all())
            print(f"Liga ID: {liga.id} - Nombre: '{liga.nombre}' - Equipos: {equipos_qty}")
            
if __name__ == "__main__":
    extract_combos()
