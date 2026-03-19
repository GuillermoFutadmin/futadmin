from app import app
from models import db, Usuario, Liga, Cancha, Arbitro, Torneo, Equipo, Jugador, Inscripcion, Pago, GrupoEntrenamiento, AlumnoEntrenamiento, Partido, EventoPartido, AsistenciaPartido, PagoCancha, PagoCombo, LigaExpansion, Configuracion
from sqlalchemy import inspect

def sync_schema():
    with app.app_context():
        inspector = inspect(db.engine)
        models = [Usuario, Liga, Cancha, Arbitro, Torneo, Equipo, Jugador, Inscripcion, Pago, GrupoEntrenamiento, AlumnoEntrenamiento, Partido, EventoPartido, AsistenciaPartido, PagoCancha, PagoCombo, LigaExpansion, Configuracion]
        
        for model in models:
            table_name = model.__tablename__
            if table_name in inspector.get_table_names():
                existing_columns = [col['name'] for col in inspector.get_columns(table_name)]
                for col in model.__table__.columns:
                    if col.name not in existing_columns:
                        # Obtenemos la representación SQL del tipo
                        col_type = col.type.compile(dialect=db.engine.dialect)
                        print(f"Agregando columna {table_name}.{col.name} ({col_type})")
                        try:
                            # Evitamos problemas con TEXT/VARCHAR agregando un default seguro temporal o permitiendo nulls
                            db.session.execute(db.text(f"ALTER TABLE {table_name} ADD COLUMN {col.name} {col_type}"))
                            db.session.commit()
                            print(f"-> Éxito")
                        except Exception as e:
                            db.session.rollback()
                            print(f"-> Error: {e}")

if __name__ == "__main__":
    sync_schema()
