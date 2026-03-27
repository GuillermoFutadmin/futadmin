from app import app
from models import Liga

try:
    with app.app_context():
        l = Liga.query.first()
        if l:
            print(l.to_dict())
        else:
            print("No ligas found")
except Exception as e:
    import traceback
    traceback.print_exc()
