
from app import app, db
from sqlalchemy import inspect
import json

with app.app_context():
    inspector = inspect(db.engine)
    columns = inspector.get_columns('canchas')
    col_names = [c['name'] for c in columns]
    print(f"COLUMNS IN 'canchas': {col_names}")
    
    # Try a simple query
    from models import Cancha
    try:
        count = Cancha.query.count()
        print(f"Cancha count: {count}")
    except Exception as e:
        print(f"Query failed: {e}")
