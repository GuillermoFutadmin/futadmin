from app import app
from models import Arbitro
with app.app_context():
    arbs = Arbitro.query.all()
    for a in arbs:
        print(f"[{a.id}] {a.nombre} - {a.password} ({a.telegram_id})")
