from app import app, db
from models import Torneo, Partido

def avanzar_ronda():
    with app.app_context():
        torneo = Torneo.query.filter_by(nombre='Torneo Rapido 2026').first()
        if not torneo:
            print("Torneo no encontrado.")
            return

        partidos_actuales = Partido.query.filter_by(torneo_id=torneo.id).all()
        max_jornada = max(p.jornada for p in partidos_actuales)
        ronda_actual = Partido.query.filter_by(torneo_id=torneo.id, jornada=max_jornada).all()
        
        if any(p.estado != 'Played' for p in ronda_actual):
            print("Aún hay partidos sin jugar.")
            return

        ganadores_ids = [p.ganador_id for p in ronda_actual if p.ganador_id]
        print(f"Ganadores: {ganadores_ids}")
        
        nueva_jornada = max_jornada + 1
        proxima_fase = 'Ronda Final'
        
        nuevos_partidos = []
        # Caso especial: 3 equipos (Triangular o 1 pasa directo)
        if len(ganadores_ids) == 3:
            # Opción: Local vs Visitante, y el 3ero espera.
            p1 = Partido(
                torneo_id=torneo.id, liga_id=torneo.liga_id, jornada=nueva_jornada,
                equipo_local_id=ganadores_ids[0], equipo_visitante_id=ganadores_ids[1],
                estado='Scheduled', fase='Semifinal Especial', hora="09:00"
            )
            # El 3ero podría jugar después o pasar a la final. 
            # Para fines de "juego", pondremos un segundo partido donde el 3ero juega contra el ganador del primero (simulado)
            # Pero por ahora solo generamos el siguiente programado.
            db.session.add(p1)
            nuevos_partidos.append(p1)
        else:
            for i in range(0, len(ganadores_ids), 2):
                if i + 1 < len(ganadores_ids):
                    nuevo = Partido(
                        torneo_id=torneo.id, liga_id=torneo.liga_id, jornada=nueva_jornada,
                        equipo_local_id=ganadores_ids[i], equipo_visitante_id=ganadores_ids[i+1],
                        estado='Scheduled', fase='Siguiente Fase', hora="10:00"
                    )
                    nuevos_partidos.append(nuevo)
                    db.session.add(nuevo)
        
        db.session.commit()
        print(f"Generados {len(nuevos_partidos)} partidos.")

if __name__ == "__main__":
    avanzar_ronda()
