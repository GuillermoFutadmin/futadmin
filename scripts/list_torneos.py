from app import app, Torneo
with app.app_context():
    torneos = Torneo.query.all()
    for t in torneos:
        print(f"ID: {t.id} | Nombre: {t.nombre} | Horario: {t.horario_juego}")
