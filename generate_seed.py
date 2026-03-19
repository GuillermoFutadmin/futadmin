from app import app
from models import db, Usuario, Cancha, Liga, Torneo, Equipo, Jugador, Arbitro
import json
import datetime

def quote(val):
    if val is None: return "None"
    if isinstance(val, bool): return "True" if val else "False"
    if isinstance(val, (int, float)): return str(val)
    if isinstance(val, datetime.date) and not isinstance(val, datetime.datetime): return repr(val.strftime('%Y-%m-%d'))
    if isinstance(val, datetime.datetime): return repr(val.strftime('%Y-%m-%d %H:%M:%S'))
    return repr(str(val))

def export():
    with app.app_context():
        lines = []
        lines.append("from app import app")
        lines.append("from models import db, Usuario, Cancha, Liga, Arbitro, Torneo, Equipo, Jugador")
        lines.append("import datetime")
        lines.append("import json")
        lines.append("def inject_local_data():")
        lines.append("    with app.app_context():")
        
        # El orden correcto para evitar foreign key constraint errors:
        # Liga (padre de muchos) -> Usuario -> Cancha -> Arbitro -> Torneo -> Equipo -> Jugador
        models = [Liga, Usuario, Cancha, Arbitro, Torneo, Equipo, Jugador]
        
        lines.append("        print('--- Vaciando tablas previas (TRUNCATE) ---')")
        lines.append("        if 'postgresql' in db.engine.url.drivername:")
        lines.append("            tables = ', '.join([m.__tablename__ for m in [Liga, Usuario, Cancha, Arbitro, Torneo, Equipo, Jugador]])")
        lines.append("            db.session.execute(db.text(f'TRUNCATE TABLE {tables} CASCADE'))")
        lines.append("            db.session.commit()")
        
        lines.append("        with db.session.no_autoflush:")
        for model in models:
            model_name = model.__tablename__
            lines.append(f"            print('--- Insertando {model_name} ---')")
            records = model.query.all()
            for rec in records:
                # get all column values
                kwargs = []
                for col in model.__table__.columns:
                    val = getattr(rec, col.name)
                    # dates handling
                    if isinstance(val, datetime.date) and not isinstance(val, datetime.datetime):
                        kwargs.append(f"{col.name}=datetime.datetime.strptime({quote(val.strftime('%Y-%m-%d'))}, '%Y-%m-%d').date()")
                    elif isinstance(val, datetime.datetime):
                        kwargs.append(f"{col.name}=datetime.datetime.strptime({quote(val.strftime('%Y-%m-%d %H:%M:%S'))}, '%Y-%m-%d %H:%M:%S')")
                    elif isinstance(val, dict) or isinstance(val, list):
                        kwargs.append(f"{col.name}={quote(json.dumps(val))}")
                    else:
                        kwargs.append(f"{col.name}={quote(val)}")
                
                kwargs_str = ", ".join(kwargs)
                lines.append(f"            if not {model.__name__}.query.get({rec.id}):")
                lines.append(f"                obj = {model.__name__}({kwargs_str})")
                lines.append(f"                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)")
                lines.append(f"                db.session.add(obj)")
            lines.append(f"            db.session.commit()")
                
        lines.append("        print('--- Ajustando secuencias de PostgreSQL ---')")
        lines.append("        if 'postgresql' in db.engine.url.drivername:")
        lines.append("            for table_name in [m.__tablename__ for m in [Usuario, Liga, Cancha, Arbitro, Torneo, Equipo, Jugador]]:")
        lines.append("                try:")
        lines.append("                    db.session.execute(db.text(f\"SELECT setval('{table_name}_id_seq', coalesce((SELECT max(id) FROM {table_name}), 1), (SELECT max(id) FROM {table_name}) IS NOT NULL);\"))")
        lines.append("                except Exception as e:")
        lines.append("                    db.session.rollback()")
        lines.append("                    print(f'No se pudo ajustar secuencia {table_name}_id_seq: {e}')")
        lines.append("        db.session.commit()")
        
        lines.append("if __name__ == '__main__':")
        lines.append("    inject_local_data()")
            
        with open("seed_local_to_prod.py", "w", encoding="utf-8") as f:
            f.write("\n".join(lines))
        print("Script seed_local_to_prod.py generado exitosamente!")

if __name__ == "__main__":
    export()
