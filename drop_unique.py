from app import app
from models import db, Jugador
from sqlalchemy import text

with app.app_context():
    try:
        # Drop unique constraint on curp
        db.session.execute(text("ALTER TABLE jugadores DROP CONSTRAINT IF EXISTS jugadores_curp_key"))
        db.session.commit()
        print("Constraint dropped (if existed)")
    except Exception as e:
        print(f"Error: {e}")
