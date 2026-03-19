from app import app
from models import Usuario
with app.app_context():
    users = Usuario.query.all()
    for u in users:
        print(f"[{u.id}] {u.nombre} - {u.email} ({u.rol})")
