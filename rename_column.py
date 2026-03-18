from app import app
from models import db
from sqlalchemy import text

with app.app_context():
    try:
        # Rename column curp to seudonimo
        db.session.execute(text("ALTER TABLE jugadores RENAME COLUMN curp TO seudonimo"))
        db.session.commit()
        print("Column renamed successfully")
    except Exception as e:
        db.session.rollback()
        print(f"Error: {e}")
