import random
from app import app, db, Partido, EventoPartido, Jugador

def sync_match_goals(partido):
    # Get current goals from the match score
    target_local = partido.goles_local or 0
    target_vis = partido.goles_visitante or 0
    
    # Get all goal events for this match
    goal_events = EventoPartido.query.filter_by(partido_id=partido.id, tipo='Gol').all()
    
    # Separate goal events by team
    local_events = [e for e in goal_events if e.equipo_id == partido.equipo_local_id]
    vis_events = [e for e in goal_events if e.equipo_id == partido.equipo_visitante_id]
    
    # --- Sync Local Goals ---
    if len(local_events) > target_local:
        # Too many events, delete the excess (pop from the end)
        excess = len(local_events) - target_local
        for i in range(excess):
            ev_to_delete = local_events.pop()
            db.session.delete(ev_to_delete)
            print(f"Partido {partido.id}: Eliminado 1 gol excedente del Local.")
            
    elif len(local_events) < target_local:
        # Too few events, add missing goals
        missing = target_local - len(local_events)
        jugadores = Jugador.query.filter_by(equipo_id=partido.equipo_local_id).all()
        for i in range(missing):
            j_id = random.choice(jugadores).id if jugadores else None
            new_ev = EventoPartido(
                partido_id=partido.id,
                equipo_id=partido.equipo_local_id,
                jugador_id=j_id,
                minuto=random.randint(1, 90),
                periodo=random.choice([1, 2]),
                tipo='Gol'
            )
            db.session.add(new_ev)
            print(f"Partido {partido.id}: Agregado 1 gol faltante al Local.")

    # --- Sync Visitante Goals ---
    if len(vis_events) > target_vis:
        excess = len(vis_events) - target_vis
        for i in range(excess):
            ev_to_delete = vis_events.pop()
            db.session.delete(ev_to_delete)
            print(f"Partido {partido.id}: Eliminado 1 gol excedente del Visitante.")
            
    elif len(vis_events) < target_vis:
        missing = target_vis - len(vis_events)
        jugadores = Jugador.query.filter_by(equipo_id=partido.equipo_visitante_id).all()
        for i in range(missing):
            j_id = random.choice(jugadores).id if jugadores else None
            new_ev = EventoPartido(
                partido_id=partido.id,
                equipo_id=partido.equipo_visitante_id,
                jugador_id=j_id,
                minuto=random.randint(1, 90),
                periodo=random.choice([1, 2]),
                tipo='Gol'
            )
            db.session.add(new_ev)
            print(f"Partido {partido.id}: Agregado 1 gol faltante al Visitante.")

def run_sync_all():
    with app.app_context():
        # Encuentra todos los partidos jugados
        partidos = Partido.query.filter_by(estado='Played').all()
        count = 0
        for p in partidos:
            sync_match_goals(p)
            count += 1
        db.session.commit()
        print(f"Sincronización completada. {count} partidos procesados.")

if __name__ == '__main__':
    run_sync_all()
