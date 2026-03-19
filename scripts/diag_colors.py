
from app import app
from models import Equipo, Torneo, Liga

with app.app_context():
    print("--- DIAGNÓSTICO DE COLORES ---")
    torneos = Torneo.query.all()
    for t in torneos:
        color = t.liga.color if t.liga else "SIN LIGA (Default: #00ff88)"
        print(f"TORNEO: {t.nombre} | ID: {t.id} | LIGA_ID: {t.liga_id} | COLOR: {color}")
    
    equipos = Equipo.query.all()
    for e in equipos:
        l_color = e.liga.color if e.liga else "SIN LIGA"
        t_l_color = e.torneo.liga.color if e.torneo and e.torneo.liga else "TORNEO SIN LIGA"
        print(f"EQUIPO: {e.nombre} | ID: {e.id} | LIGA_ID: {e.liga_id} | TORNEO_ID: {e.torneo_id} | LIGA_COLOR: {l_color} | T_L_COLOR: {t_l_color}")
