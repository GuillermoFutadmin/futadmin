
from app import app
from models import db, Equipo, Jugador, Torneo

def repair_data():
    with app.app_context():
        print("Iniciando reparacion de datos...")
        
        # 1. Reparar Equipos
        equipos_reparados = 0
        equipos_huerfanos = Equipo.query.filter_by(liga_id=None).all()
        for e in equipos_huerfanos:
            if e.torneo and e.torneo.liga_id:
                e.liga_id = e.torneo.liga_id
                equipos_reparados += 1
                print(f"  Equipo '{e.nombre}' vinculado a Liga ID: {e.liga_id}")
        
        # 2. Reparar Jugadores
        jugadores_reparados = 0
        jugadores_huerfanos = Jugador.query.filter_by(liga_id=None).all()
        for j in jugadores_huerfanos:
            if j.equipo and j.equipo.liga_id:
                j.liga_id = j.equipo.liga_id
                jugadores_reparados += 1
                print(f"  Jugador '{j.nombre}' vinculado a Liga ID: {j.liga_id}")
            elif j.equipo and j.equipo.torneo and j.equipo.torneo.liga_id:
                j.liga_id = j.equipo.torneo.liga_id
                jugadores_reparados += 1
                print(f"  Jugador '{j.nombre}' vinculado a Liga ID (vía torneo): {j.liga_id}")
        
        db.session.commit()
        print(f"\nResumen:")
        print(f"  - Equipos reparados: {equipos_reparados}")
        print(f"  - Jugadores reparados: {jugadores_reparados}")
        print("Proceso completado.")

if __name__ == "__main__":
    repair_data()
