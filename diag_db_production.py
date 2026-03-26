from app import app, db
from models import Liga, PagoCombo, LigaExpansion, Usuario
import traceback

with app.app_context():
    print("--- Diagnóstico de Base de Datos ---")
    try:
        print(f"Ligas: {Liga.query.count()}")
        print(f"Usuarios: {Usuario.query.count()}")
        try:
            print(f"Pagos: {PagoCombo.query.count()}")
        except Exception as e:
            print(f"ERROR PagoCombo: {e}")
            
        try:
            print(f"Expansiones: {LigaExpansion.query.count()}")
        except Exception as e:
            print(f"ERROR LigaExpansion: {e}")
            
        # Intentar crear tablas por si acaso
        print("Intentando db.create_all()...")
        db.create_all()
        print("db.create_all() completado.")
        
    except Exception as e:
        print(f"CRITICAL: {e}")
        traceback.print_exc()
