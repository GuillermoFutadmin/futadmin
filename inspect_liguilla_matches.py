from app import app, db
from models import Torneo, Partido

def inspect_matches(torneo_id):
    with app.app_context():
        torneo = Torneo.query.get(torneo_id)
        print(f"\n--- {torneo.nombre} (ID: {torneo_id}) ---")
        
        partidos = Partido.query.filter_by(torneo_id=torneo_id).order_by(Partido.jornada.asc()).all()
        for p in partidos:
            print(f"  J{p.jornada} | Fase: {p.fase} | Estado: {p.estado} | {p.equipo_local_id} vs {p.equipo_visitante_id} | Ganador: {p.ganador_id}")

if __name__ == "__main__":
    for tid in [11, 12]:
        inspect_matches(tid)
