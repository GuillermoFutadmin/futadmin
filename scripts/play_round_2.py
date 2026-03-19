import random
from app import app, db, Partido

def simular_8vos():
    with app.app_context():
        # Torneo Rápido 2026 es el que queremos (buscaremos por nombre para ser seguros)
        from models import Torneo
        torneo = Torneo.query.filter_by(nombre='Torneo Rapido 2026').first()
        if not torneo:
            print("Torneo no encontrado.")
            return
            
        partidos = Partido.query.filter_by(torneo_id=torneo.id, estado='Scheduled').all()
        
        if not partidos:
            print(f"No hay partidos programados en el torneo {torneo.nombre} (ID: {torneo.id}).")
            return

        print(f"Simulando {len(partidos)} partidos de 8vos de Final para '{torneo.nombre}'...")
        
        for p in partidos:
            goles_l = random.randint(0, 4)
            goles_v = random.randint(0, 4)
            
            # Asegurar desempate
            penales_l = 0
            penales_v = 0
            if goles_l == goles_v:
                penales_l = random.randint(3, 5)
                penales_v = random.randint(3, 5)
                while penales_l == penales_v:
                    penales_v = random.randint(3, 5)
            
            p.goles_local = goles_l
            p.goles_visitante = goles_v
            p.penales_local = penales_l if penales_l > 0 else None
            p.penales_visitante = penales_v if penales_v > 0 else None
            p.estado = 'Played'
            
            if goles_l > goles_v or (penales_l > penales_v if penales_l > 0 else False):
                p.ganador_id = p.equipo_local_id
            else:
                p.ganador_id = p.equipo_visitante_id
                
            print(f"  - {p.equipo_local.nombre} {goles_l}({penales_l}) vs {p.equipo_visitante.nombre} {goles_v}({penales_v}) -> Ganador: {p.ganador_id}")
            
        db.session.commit()
        print("Resultados guardados con éxito.")

if __name__ == "__main__":
    simular_8vos()
