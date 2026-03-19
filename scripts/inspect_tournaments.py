from app import app, db
from models import Torneo, Partido

with app.app_context():
    # Buscamos los torneos por nombre parcial para coincidir con lo que ve el usuario
    t1 = Torneo.query.filter(Torneo.nombre.ilike('%Rapido%')).first()
    t2 = Torneo.query.filter(Torneo.nombre.ilike('%Socer%')).first()
    
    torneos = [t for t in [t1, t2] if t]
    
    for t in torneos:
        # Partidos con fase eliminatoria
        # El dashboard verifica: p.fase && p.fase !== 'Fase de Grupos'
        # Pero suele ser 'Semifinal', 'Final', '8vos de Final', etc.
        kn = Partido.query.filter(
            Partido.torneo_id == t.id,
            Partido.fase != None,
            Partido.fase != 'Regular',
            Partido.fase != 'Fase de Grupos'
        ).count()
        
        print(f"Torneo: {t.nombre}")
        print(f"  ID: {t.id}")
        print(f"  Formato: {t.formato}")
        print(f"  Knockout Matches: {kn}")
        
        if kn > 0:
            sample_kn = Partido.query.filter(
                Partido.torneo_id == t.id,
                Partido.fase != None,
                Partido.fase != 'Regular',
                Partido.fase != 'Fase de Grupos'
            ).first()
            print(f"  Ejemplo fase: {sample_kn.fase}")
        else:
            print("  No tiene fases de eliminatoria (solo regular o sin partidos).")
        print("-" * 20)
