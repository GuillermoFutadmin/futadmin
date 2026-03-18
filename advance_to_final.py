from app import app, auto_avanzar_ronda, auto_schedule_torneo
from models import Torneo, Partido

def advance_tournament(torneo_id):
    with app.app_context():
        torneo = Torneo.query.get(torneo_id)
        print(f"Advancing: {torneo.nombre}")
        
        # 1. Advance to generate next round (Final)
        success = auto_avanzar_ronda(torneo_id)
        if success:
            print(f"  Advancement success. Final generated.")
            # 2. Schedule the Final
            sched_success = auto_schedule_torneo(torneo_id)
            print(f"  Scheduling success: {sched_success}")
        else:
            print("  Advancement failed or already at final.")

if __name__ == "__main__":
    for tid in [11, 12]:
        advance_tournament(tid)
