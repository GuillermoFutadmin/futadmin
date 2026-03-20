from flask import Flask, render_template, jsonify, request, url_for, session, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_wtf.csrf import CSRFProtect
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta, date
from sqlalchemy import or_
from dotenv import load_dotenv
from flask_talisman import Talisman
from werkzeug.middleware.proxy_fix import ProxyFix
import os, secrets, uuid, math, requests
from PIL import Image

# Cargar variables de entorno desde .env
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = Flask(__name__, static_folder=os.path.join(BASE_DIR, 'static'))
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_port=1, x_prefix=1)
# IMPORTANTE: El Secret Key DEBE ser el mismo para todos los workers
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
if not app.config['SECRET_KEY']:
    print("ADVERTENCIA CRÍTICA: FLASK_SECRET_KEY no detectada. Usando llave volátil (esto romperá sesiones en Railway).")
    app.config['SECRET_KEY'] = 'dev-key-fallback-replace-me'

db_url = os.getenv('DATABASE_URL') or os.getenv('SQLALCHEMY_DATABASE_URI') or 'sqlite:///futadmin.db'
if db_url.startswith("postgres://"):
    db_url = db_url.replace("postgres://", "postgresql://", 1)
app.config['SQLALCHEMY_DATABASE_URI'] = db_url

# Log de diagnóstico en el arranque
print(f"--- Arrancando Aplicación FutAdmin ---")
print(f"DATABASE_URI Configurada: {db_url[:40]}...")
if db_url.startswith("sqlite"):
    print("ADVERTENCIA: Usando SQLite. Si estás en Railway, verifica que DATABASE_URL esté ligada.")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_COOKIE_SECURE'] = True
app.config['SESSION_COOKIE_HTTPONLY'] = True
app.config['SESSION_COOKIE_SAMESITE'] = 'None' # Máxima compatibilidad con Secure=True
app.config['SESSION_COOKIE_NAME'] = 'futadmin_session_prod_v2'
app.config['PERMANENT_SESSION_LIFETIME'] = 86400 * 7 # 7 días

@app.after_request
def add_security_headers(response):
    response.headers['Vary'] = 'Cookie'
    return response

app.config['UPLOAD_FOLDER'] = os.path.join(BASE_DIR, 'static', 'uploads')
app.config['TELEGRAM_BOT_TOKEN'] = os.getenv('TELEGRAM_BOT_TOKEN')
app.config['MAX_CONTENT_LENGTH'] = int(os.getenv('MAX_CONTENT_LENGTH', 2 * 1024 * 1024))

# Inicializar Talisman para headers de seguridad y SSL (si SSL_REQUIRED=True)
talisman = Talisman(app, 
    force_https=os.getenv('SSL_REQUIRED', 'False') == 'True',
    content_security_policy=None,
    frame_options=None # Permitir que Telegram abra la app en un iframe (necesario para TWA)
)

os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

@app.route('/api/debug_uploads')
def debug_uploads():
    import os
    folder = app.config.get('UPLOAD_FOLDER', 'No folder')
    exists = os.path.exists(folder)
    files = os.listdir(folder) if exists else []
    
    # Intentar escribir un archivo de prueba para verificar persistencia real
    test_file = os.path.join(folder, 'persistence_test.txt')
    write_ok = False
    try:
        with open(test_file, 'w') as f:
            f.write(f'Test at {datetime.now()}')
        write_ok = True
    except:
        write_ok = False

    return jsonify({
        "upload_folder": folder,
        "exists": exists,
        "is_writable": os.access(folder, os.W_OK) if exists else False,
        "test_write_ok": write_ok,
        "files_count": len(files),
        "files_preview": files[:20],
        "base_dir": BASE_DIR,
        "current_working_dir": os.getcwd()
    }), 200

# Ruta de salud para Railway Healthcheck (excluida de SSL redirect y auth)
@app.route('/health')
@talisman(force_https=False)
def healthcheck():
    return jsonify({'status': 'ok'}), 200

from models import db, bcrypt, Torneo, Equipo, Jugador, Inscripcion, Pago, GrupoEntrenamiento, AlumnoEntrenamiento, Partido, EventoPartido, Arbitro, Cancha, Usuario, apply_liga_filter, get_liga_id, check_torneos_limit, get_role_limits, Liga, PagoCombo, Configuracion, LigaExpansion
from utils import paginate_query
from routes.entrenamientos import entrenamientos_bp
from routes.canchas import canchas_bp
from routes.pagos_cancha import pagos_cancha_bp
from routes.users import users_bp
from routes.arbitros import arbitros_bp
from routes.anonymize import anonymize_bp

bcrypt.init_app(app)
csrf = CSRFProtect(app)

# Registrar Blueprints
app.register_blueprint(entrenamientos_bp, url_prefix='/api/entrenamientos')
app.register_blueprint(canchas_bp)
app.register_blueprint(pagos_cancha_bp)
app.register_blueprint(users_bp)
app.register_blueprint(arbitros_bp)
app.register_blueprint(anonymize_bp)
csrf.exempt(entrenamientos_bp)
csrf.exempt(canchas_bp)
csrf.exempt(pagos_cancha_bp)
csrf.exempt(users_bp)
csrf.exempt(arbitros_bp)
csrf.exempt(anonymize_bp)

@app.route('/telegram_app')
@app.route('/telegram')
def telegram_app_view():
    return render_template('telegram_app.html')

db.init_app(app)
from flask_migrate import Migrate
migrate = Migrate(app, db)

LAST_STATS_ERROR = "No errors yet"

@app.before_request
def check_login():
    # Rutas que no requieren login
    public_routes = ['users.login_view', 'users.login', 'users.privacy_view', 'static', 'healthcheck', 'debug_stats', 'diag_db', 'debug_uploads']
    if request.endpoint in public_routes or not request.endpoint:
        return
    
    # Permitir si el usuario está en sesión
    if 'user_id' not in session:
        # Exenciones para la App de Telegram (tienen su propia auth)
        if request.path in ['/telegram_app', '/telegram'] or request.path.startswith('/api/telegram/'):
            return

        print(f"DEBUG AUTH: 401 en {request.path} - Session: {list(session.keys())}")
        if request.path.startswith('/api/'):
            return jsonify({"error": "No autenticado"}), 401
        return redirect(url_for('users.login_view'))

@app.errorhandler(Exception)
def handle_exception(e):
    # Pasar las excepciones HTTP de Werkzeug (404, 405, etc.) sin modificar
    from werkzeug.exceptions import HTTPException
    if isinstance(e, HTTPException):
        return e
    
    import traceback
    tb = traceback.format_exc()
    global LAST_STATS_ERROR
    LAST_STATS_ERROR = f"Global Exception: {e}\n{tb}"
    print(f"CRITICAL UNHANDLED ERROR: {e}\n{tb}")
    
    # Return JSON for API routes
    if request.path.startswith('/api/'):
        return jsonify({"error": "Internal Server Error", "details": str(e), "trace": tb}), 500
    
    # Or text for others
    return f"Internal Server Error: {str(e)}", 500

# Los modelos han sido movidos a models.py



# Helpers moved to models.py and imported above

@app.route('/diag_db')
def diag_db():
    """Endpoint de diagnóstico público para contar registros sin filtros de liga."""
    try:
        from sqlalchemy import text
        with db.engine.connect() as con:
            torneos_total = con.execute(text("SELECT COUNT(*) FROM torneos")).scalar()
            torneos_archived = con.execute(text("SELECT COUNT(*) FROM torneos WHERE archived = TRUE")).scalar()
            torneos_null = con.execute(text("SELECT COUNT(*) FROM torneos WHERE archived IS NULL")).scalar()
            equipos_total = con.execute(text("SELECT COUNT(*) FROM equipos")).scalar()
            jugadores_total = con.execute(text("SELECT COUNT(*) FROM jugadores")).scalar()
            ligas_total = con.execute(text("SELECT COUNT(*) FROM ligas")).scalar()
        return jsonify({
            "torneos_total": torneos_total,
            "torneos_archived_true": torneos_archived,
            "torneos_archived_null": torneos_null,
            "equipos_total": equipos_total,
            "jugadores_total": jugadores_total,
            "ligas_total": ligas_total,
            "last_error": LAST_STATS_ERROR
        })
    except Exception as e:
        import traceback
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

@app.route('/api/all_equipos', methods=['GET'])
def get_all_equipos():
    query = Equipo.query
    query = apply_liga_filter(query, Equipo)
    equipos = query.all()
    return jsonify([{"id": e.id, "nombre": e.nombre} for e in equipos])

@app.route('/api/admin/seed_data')
def admin_seed_data():
    # Solo el administrador global puede poblar datos de prueba
    if session.get('user_rol') != 'admin':
        return jsonify({"error": "No autorizado"}), 403
    
    try:
        from scripts.seed_combos import seed_data
        seed_data()
        return jsonify({"success": "Inyección de 3 combos más recientes completada exitosamente.", "tip": "Recuerda dar F5 para ver los equipos nuevos."}), 200
    except Exception as e:
        return jsonify({"error": f"Fallo al inyectar: {str(e)}"}), 500

@app.route('/api/admin/seed_local')
def admin_seed_local():
    if session.get('user_rol') != 'admin':
        return jsonify({"error": "No autorizado"}), 403
    
    try:
        # 1. Sincronizar esquema automáticamente
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        from models import Usuario, Liga, Cancha, Arbitro, Torneo, Equipo, Jugador, Inscripcion, Pago, GrupoEntrenamiento, AlumnoEntrenamiento, Partido, EventoPartido, AsistenciaPartido, PagoCancha, PagoCombo, LigaExpansion, Configuracion
        models_sync = [Usuario, Liga, Cancha, Arbitro, Torneo, Equipo, Jugador, Inscripcion, Pago, GrupoEntrenamiento, AlumnoEntrenamiento, Partido, EventoPartido, AsistenciaPartido, PagoCancha, PagoCombo, LigaExpansion, Configuracion]
        for m in models_sync:
            t_name = m.__tablename__
            if t_name in inspector.get_table_names():
                existing_cols = [c['name'] for c in inspector.get_columns(t_name)]
                for col in m.__table__.columns:
                    if col.name not in existing_cols:
                        c_type = col.type.compile(dialect=db.engine.dialect)
                        try:
                            db.session.execute(db.text(f"ALTER TABLE {t_name} ADD COLUMN {col.name} {c_type}"))
                            db.session.commit()
                        except Exception:
                            db.session.rollback()

        # 2. Inyectar datos
        import seed_local_to_prod
        seed_local_to_prod.inject_local_data()
        return jsonify({"success": "Estructura reparada e inyección de datos locales completada exitosamente.", "tip": "Revisa el dashboard para confirmar."}), 200
    except Exception as e:
        import traceback
        return jsonify({"error": f"Fallo al inyectar: {str(e)}", "trace": traceback.format_exc()}), 500

@app.route('/api/admin/fix_db')
def admin_fix_db():
    if session.get('user_rol') != 'admin':
        return jsonify({"error": "No autorizado"}), 403
    try:
        from sqlalchemy import inspect
        inspector = inspect(db.engine)
        from models import Usuario, Liga, Cancha, Arbitro, Torneo, Equipo, Jugador, Inscripcion, Pago, GrupoEntrenamiento, AlumnoEntrenamiento, Partido, EventoPartido, AsistenciaPartido, PagoCancha, PagoCombo, LigaExpansion, Configuracion
        models = [Usuario, Liga, Cancha, Arbitro, Torneo, Equipo, Jugador, Inscripcion, Pago, GrupoEntrenamiento, AlumnoEntrenamiento, Partido, EventoPartido, AsistenciaPartido, PagoCancha, PagoCombo, LigaExpansion, Configuracion]
        log = []
        for model in models:
            table_name = model.__tablename__
            if table_name in inspector.get_table_names():
                existing_columns = [c['name'] for c in inspector.get_columns(table_name)]
                for col in model.__table__.columns:
                    if col.name not in existing_columns:
                        col_type = col.type.compile(dialect=db.engine.dialect)
                        try:
                            # Add column safely
                            db.session.execute(db.text(f"ALTER TABLE {table_name} ADD COLUMN {col.name} {col_type}"))
                            db.session.commit()
                            log.append(f"Éxito: {table_name}.{col.name}")
                        except Exception as e:
                            db.session.rollback()
                            log.append(f"Error en {table_name}.{col.name}: {e}")
        return jsonify({"success": "Sincronización de esquema finalizada.", "log": log}), 200
    except Exception as e:
        import traceback
        return jsonify({"error": str(e), "trace": traceback.format_exc()}), 500

@app.route('/api/debug_prod')
def debug_prod():
    # Ruta de diagnóstico que combina info básica (pública) y stats (admin)
    is_admin = session.get('user_rol') == 'admin'
    
    db_uri = app.config.get('SQLALCHEMY_DATABASE_URI', 'None')
    # Protegemos la URI de la BD
    masked_uri = db_uri[:25] + "..." + db_uri[-10:] if len(db_uri) > 35 else "Confidencial"
    
    data = {
        "database_type": "PostgreSQL" if "postgresql" in db_uri else "SQLite/Other",
        "db_masked": masked_uri,
        "session_active": 'user_id' in session,
        "user_rol": session.get('user_rol'),
        "secret_key_stable": app.config['SECRET_KEY'] != 'dev-key-fallback-replace-me'
    }

    if is_admin:
        try:
            data["counts"] = {
                "ligas": Liga.query.count(),
                "usuarios": Usuario.query.count(),
                "canchas": Cancha.query.count()
            }
        except Exception as e:
            data["error_stats"] = str(e)

    return jsonify(data)

@app.route('/api/admin/check_db')
def admin_check_db():
    if session.get('user_rol') != 'admin':
        return jsonify({"error": "No autorizado"}), 403
    
    counts = {
        "ligas": Liga.query.count(),
        "torneos": Torneo.query.count(),
        "torneos_activos": Torneo.query.filter_by(activo=True).count(),
        "equipos": Equipo.query.count(),
        "jugadores": Jugador.query.count(),
        "canchas": Cancha.query.count(),
        "usuarios": Usuario.query.count(),
        "database_uri_prefix": app.config.get('SQLALCHEMY_DATABASE_URI', '')[:20]
    }
    return jsonify(counts)

# --- Ruta de Subida de Archivos ---

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/api/upload', methods=['POST'])
@csrf.exempt
def upload_file():
    if 'file' not in request.files:
        return jsonify({"error": "No se envió ningún archivo"}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({"error": "Nombre de archivo vacío"}), 400
    
    # Validación extra de tamaño (redundante con MAX_CONTENT_LENGTH pero útil para respuesta personalizada)
    file.seek(0, os.SEEK_END)
    size = file.tell()
    if size > app.config['MAX_CONTENT_LENGTH']:
        return jsonify({"error": f"Archivo demasiado grande. Máximo {app.config['MAX_CONTENT_LENGTH']//(1024*1024)}MB"}), 413
    file.seek(0)

    if file and allowed_file(file.filename):
        # Sanitizar nombre
        ext = file.filename.rsplit('.', 1)[1].lower()
        # Cargar imagen y comprimir para ahorrar espacio (Max 800px, 70% calidad)
        try:
            img = Image.open(file)
            # Convertir a RGB si es necesario (para JPEG/compatibilidad)
            if img.mode in ("RGBA", "P"):
                img = img.convert("RGB")
            
            max_size = (800, 800)
            img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Forzamos extensión a jpg para consistencia y ahorro
            unique_name = f"{uuid.uuid4().hex}.jpg"
            save_path = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
            
            img.save(save_path, "JPEG", optimize=True, quality=70)
            url = f"/static/uploads/{unique_name}"
            return jsonify({"url": url}), 201
        except Exception as e:
            print(f"Error comprimiendo imagen: {e}")
            # Fallback: guardar tal cual si falla Pillow
            file.seek(0)
            file.save(save_path)
            url = f"/static/uploads/{unique_name}"
            return jsonify({"url": url}), 201
    return jsonify({"error": "Formato de archivo no permitido"}), 400

# --- Rutas API: Equipos ---

@app.route('/api/equipos', methods=['GET', 'POST'])
@csrf.exempt
def handle_equipos():
    if request.method == 'POST':
        data = request.json
        torneo_id = data.get('torneo_id')
        if not torneo_id:
            return jsonify({"error": "Se requiere un ID de torneo"}), 400
        
        torneo = Torneo.query.get(torneo_id)
        if not torneo:
            return jsonify({"error": "Torneo no encontrado"}), 404

        nuevo = Equipo(
            nombre=data.get('nombre'),
            torneo_id=torneo_id,
            escudo_url=data.get('escudo_url'),
            colonia=data.get('colonia'),
            colonia_geojson=data.get('colonia_geojson'),
            liga_id=torneo.liga_id
        )
        db.session.add(nuevo)
        db.session.flush() # Obtener id de equipo

        # Crear Inscripción Automática (Inscripción Rápida)
        monto_pactado = float(torneo.costo_inscripcion or 0)
        nueva_ins = Inscripcion(
            torneo_id=torneo_id,
            equipo_id=nuevo.id,
            monto_pactado_inscripcion=monto_pactado
        )
        db.session.add(nueva_ins)
        db.session.flush()

        # Procesar Abono Inicial si existe
        abono_inicial = float(data.get('abono_inicial', 0))
        pago_id = None
        if abono_inicial > 0:
            nuevo_pago = Pago(
                inscripcion_id=nueva_ins.id,
                monto=abono_inicial,
                tipo='Inscripcion',
                metodo=data.get('metodo_pago', 'Efectivo'),
                fecha=datetime.utcnow()
            )
            db.session.add(nuevo_pago)
            db.session.flush()
            pago_id = nuevo_pago.id
        
        db.session.commit()

        # Hook: Crear cuenta si se solicita
        crear_cuenta = data.get('crear_cuenta', False)
        rol_solicitado = data.get('rol', 'equipo')
        email_equipo = data.get('email')
        
        if crear_cuenta and email_equipo:
            existing = Usuario.query.filter_by(email=email_equipo).first()
            if not existing:
                hashed_pw = bcrypt.generate_password_hash('equipo123').decode('utf-8')
                new_user = Usuario(
                    nombre=f"Delegado {nuevo.nombre}",
                    email=email_equipo,
                    password_hash=hashed_pw,
                    rol=rol_solicitado,
                    liga_id=torneo.liga_id,
                    activo=True
                )
                db.session.add(new_user)
            else:
                existing.rol = rol_solicitado
            db.session.commit()

        # Resolver sede del torneo
        import string as _str, random as _rnd
        if torneo and torneo.cancha:
            nombre_cancha = torneo.cancha.strip()
            cancha_obj = Cancha.query.filter(Cancha.nombre.ilike(nombre_cancha)).first()
            sede_nombre_eq = cancha_obj.nombre if cancha_obj else torneo.cancha
        else:
            sede_nombre_eq = "Por definir"

        # Generar folio alfanumérico
        folio = 'FUT-' + ''.join(_rnd.choices(_str.ascii_uppercase + _str.digits, k=6))

        # Generar datos del ticket virtual COMPLETO
        ticket_data = {
            "pago_id": pago_id or nueva_ins.id,
            "folio": folio,
            "fecha": datetime.utcnow().strftime('%d/%m/%Y %H:%M'),
            "equipo": nuevo.nombre,
            "torneo": torneo.nombre,
            "sede": sede_nombre_eq,
            "monto_abonado": abono_inicial,
            "tipo": "Inscripción Inicial",
            "metodo": data.get('metodo_pago', 'Efectivo'),
            "monto_pactado": monto_pactado,
            "total_pagado": abono_inicial,
            "saldo_pendiente": monto_pactado - abono_inicial,
            "premios": torneo.premios or "",
            "reglamento": torneo.reglamento or "",
            "clausulas": torneo.clausulas or "",
            "fecha_inicio_torneo": torneo.fecha_inicio.strftime('%d/%m/%Y') if torneo.fecha_inicio else "Pendiente"
        }

        return jsonify({
            "id": nuevo.id, 
            "nombre": nuevo.nombre, 
            "torneo_id": nuevo.torneo_id,
            "ticket": ticket_data
        }), 201
    
    torneo_id = request.args.get('torneo_id', type=int)
    query = Equipo.query
    query = apply_liga_filter(query, Equipo)
    
    if torneo_id:
        query = query.filter_by(torneo_id=torneo_id)
    
    rol = session.get('user_rol')
    return paginate_query(query, renderer=lambda e: e.to_dict(user_rol=rol))

@app.route('/api/equipos/<int:id>', methods=['GET', 'DELETE', 'PUT'])
@csrf.exempt
def handle_equipo_single(id):
    equipo = apply_liga_filter(Equipo.query, Equipo).filter_by(id=id).first_or_404()
    if request.method == 'GET':
        rol = session.get('user_rol')
        return jsonify(equipo.to_dict(user_rol=rol))
    if request.method == 'DELETE':
        db.session.delete(equipo)
        db.session.commit()
        return jsonify({"success": True})
    if (request.method == 'PUT'):
        data = request.json
        equipo.nombre = data.get('nombre', equipo.nombre)
        
        # Solo actualizar torneo_id si se proporciona un valor válido (no null/empty)
        new_torneo_id = data.get('torneo_id')
        if new_torneo_id:
            equipo.torneo_id = new_torneo_id
            
        equipo.escudo_url = data.get('escudo_url', equipo.escudo_url)
        equipo.colonia = data.get('colonia', equipo.colonia)
        equipo.email = data.get('email', equipo.email)
        equipo.grupo = data.get('grupo', equipo.grupo)
        
        if 'colonia_geojson' in data:
            equipo.colonia_geojson = data.get('colonia_geojson')
            
        new_uid = data.get('uid')
        if new_uid and new_uid != equipo.uid:
            # Verificar si el nuevo UID ya está en uso
            exists = Equipo.query.filter(Equipo.uid == new_uid, Equipo.id != equipo.id).first()
            if exists:
                return jsonify({"error": f"El ID '{new_uid}' ya está siendo utilizado por otro equipo."}), 400
            equipo.uid = new_uid

        db.session.commit()
        rol = session.get('user_rol')
        return jsonify(equipo.to_dict(user_rol=rol))

# --- Rutas API: Jugadores ---

@app.route('/api/jugadores', methods=['GET', 'POST'])
@csrf.exempt
def handle_jugadores():
    if request.method == 'POST':
        data = request.json
        if not data.get('equipo_id'):
            return jsonify({"error": "Se requiere un ID de equipo"}), 400
        
        # Manejo de campos numéricos para evitar errores de tipo en PostgreSQL
        numero = data.get('numero')
        
        # Normalizar Seudónimo a None si está vacío
        seudonimo = data.get('seudonimo')
        if seudonimo == "": seudonimo = None
        
        try:
            # Heredar liga_id del equipo o de la sesión
            equipo = db.session.get(Equipo, data.get('equipo_id'))
            l_id = equipo.liga_id if equipo else session.get('liga_id')

            nuevo = Jugador(
                nombre=data.get('nombre'),
                seudonimo=seudonimo,
                telefono=data.get('telefono'),
                posicion=data.get('posicion'),
                numero=int(numero) if numero and str(numero).isdigit() else None,
                foto_url=data.get('foto_url'),
                es_portero=data.get('es_portero', False),
                es_capitan=data.get('es_capitan', False),
                equipo_id=data.get('equipo_id'),
                liga_id=l_id
            )
            db.session.add(nuevo)
            
            # Hook: Crear usuario equipo si se solicita explícitamente
            crear_cuenta = data.get('crear_cuenta', False)
            rol_solicitado = data.get('rol', 'equipo')
            email = data.get('email') or data.get('telefono') # Usar teléfono como fallback si no hay email (opcional, pero el user pidió email usualmente)
            
            if crear_cuenta and email:
                existing = Usuario.query.filter_by(email=email).first()
                if not existing:
                    from flask_bcrypt import Bcrypt
                    bcrypt = Bcrypt()
                    hashed_pw = bcrypt.generate_password_hash('equipo123').decode('utf-8')
                    new_user = Usuario(
                        nombre=nuevo.nombre,
                        email=email,
                        password_hash=hashed_pw,
                        rol=rol_solicitado,
                        liga_id=nuevo.liga_id,
                        activo=True
                    )
                    db.session.add(new_user)

            db.session.commit()
            return jsonify({"id": nuevo.id, "nombre": nuevo.nombre}), 201
        except Exception as e:
            db.session.rollback()
            print(f"Error POST /api/jugadores: {e}")
            return jsonify({"error": str(e)}), 500
    
    equipo_id = request.args.get('equipo_id', type=int)
    query = Jugador.query
    query = apply_liga_filter(query, Jugador)
    
    if equipo_id:
        query = query.filter(Jugador.equipo_id == equipo_id)
    
    return paginate_query(query, renderer=lambda j: j.to_dict())

@app.route('/api/jugadores/<int:id>', methods=['GET', 'DELETE', 'PUT'])
@csrf.exempt
def handle_jugador_single(id):
    jugador = apply_liga_filter(Jugador.query, Jugador).filter_by(id=id).first_or_404()
    if request.method == 'GET':
        return jsonify(jugador.to_dict())
    if request.method == 'DELETE':
        db.session.delete(jugador)
        db.session.commit()
        return jsonify({"success": True})
    if request.method == 'PUT':
        data = request.json
        jugador.nombre = data.get('nombre', jugador.nombre)
        # Normalizar Seudónimo
        seudonimo = data.get('seudonimo')
        if seudonimo == "": jugador.seudonimo = None
        else: jugador.seudonimo = data.get('seudonimo', jugador.seudonimo)

        jugador.telefono = data.get('telefono', jugador.telefono)
        jugador.posicion = data.get('posicion', jugador.posicion)
        
        # Manejo de campos numéricos
        numero = data.get('numero')
        jugador.numero = int(numero) if numero and str(numero).isdigit() else (None if numero == "" else jugador.numero)
        
        jugador.foto_url = data.get('foto_url', jugador.foto_url)
        jugador.es_portero = data.get('es_portero', jugador.es_portero)
        jugador.es_capitan = data.get('es_capitan', jugador.es_capitan)
        jugador.equipo_id = data.get('equipo_id', jugador.equipo_id)
        
        try:
            db.session.commit()
            return jsonify({"id": jugador.id, "nombre": jugador.nombre})
        except Exception as e:
            db.session.rollback()
            print(f"Error PUT /api/jugadores/{id}: {e}")
            return jsonify({"error": str(e)}), 500

# --- Rutas API: Inscripciones y Pagos ---

@app.route('/api/inscripciones', methods=['GET', 'POST'])
@csrf.exempt
def handle_inscripciones():
    if request.method == 'POST':
        # Control de Permisos: Solo cuentas principales
        p_roles = ['admin', 'ejecutivo', 'dueño_liga', 'super_arbitro', 'equipo']
        if session.get('user_rol') not in p_roles:
            return jsonify({"error": "Solo las cuentas principales pueden realizar inscripciones."}), 403
            
        data = request.json
        torneo_id = data.get('torneo_id')
        equipo_id = data.get('equipo_id')
        
        if not torneo_id or not equipo_id:
            return jsonify({"error": "Faltan datos de torneo o equipo"}), 400
            
        # Verificar si ya existe
        existente = Inscripcion.query.filter_by(torneo_id=torneo_id, equipo_id=equipo_id).first()
        if existente:
            return jsonify({"error": "El equipo ya está inscrito en este torneo"}), 400
            
        torneo = Torneo.query.get(torneo_id)
        equipo = Equipo.query.get(equipo_id)
        
        monto_pactado = data.get('monto_pactado', torneo.costo_inscripcion if torneo else 0)
        abono_inicial = data.get('abono_inicial', 0)
        metodo_pago = data.get('metodo_pago', 'Efectivo')
        
        nueva = Inscripcion(
            torneo_id=torneo_id,
            equipo_id=equipo_id,
            monto_pactado_inscripcion=monto_pactado,
            liga_id=torneo.liga_id if torneo else None
        )
        db.session.add(nueva)
        db.session.flush() # Para obtener el ID de la nueva inscripción
        
        if abono_inicial > 0:
            nuevo_pago = Pago(
                inscripcion_id=nueva.id,
                monto=abono_inicial,
                tipo='Inscripcion',
                metodo=metodo_pago,
                comentario='Abono inicial de inscripción',
                liga_id=nueva.liga_id,
                torneo_id=torneo_id
            )
            db.session.add(nuevo_pago)
            db.session.flush()
            
        # Calcular saldos para el ticket (siempre)
        pagado_ins = db.session.query(db.func.sum(Pago.monto)).filter_by(inscripcion_id=nueva.id, tipo='Inscripcion').scalar() or 0
        
        reglas_cancha = ""
        cancha_asignada = None
        if torneo and torneo.cancha:
            nombre_cancha = torneo.cancha.strip()
            cancha_asignada = Cancha.query.filter(Cancha.nombre.ilike(nombre_cancha)).first()
            if cancha_asignada and cancha_asignada.notas:
                reglas_cancha = f"REGLAS DE LA SEDE ({cancha_asignada.nombre}):\n{cancha_asignada.notas}"
            sede_nombre = cancha_asignada.nombre if cancha_asignada else torneo.cancha
        else:
            sede_nombre = "Por definir"

        import string as _str2, random as _rnd2
        folio_ins = 'FUT-' + ''.join(_rnd2.choices(_str2.ascii_uppercase + _str2.digits, k=6))

        ticket_data = {
            "pago_id": nueva.id,
            "folio": folio_ins,
            "fecha": datetime.utcnow().strftime('%d/%m/%Y %H:%M'),
            "equipo": equipo.nombre if equipo else "Equipo",
            "torneo": torneo.nombre if torneo else "Torneo",
            "sede": sede_nombre.strip() if sede_nombre else "Por definir",
            "monto_abonado": float(abono_inicial),
            "tipo": "Registro de Inscripción",
            "metodo": metodo_pago,
            "monto_pactado": float(nueva.monto_pactado_inscripcion),
            "total_pagado": float(pagado_ins),
            "saldo_pendiente": float(nueva.monto_pactado_inscripcion - pagado_ins),
            "premios": torneo.premios if torneo else "",
            "reglamento": torneo.reglamento if torneo else "",
            "clausulas": (torneo.clausulas if torneo and torneo.clausulas else "") + ("\n\n" + reglas_cancha if reglas_cancha else "")
        }
        
        db.session.commit()
        return jsonify({
            "id": nueva.id, 
            "success": True,
            "ticket": ticket_data
        }), 201

    # GET handling
    torneo_id = request.args.get('torneo_id', type=int)
    if not torneo_id:
        return jsonify({"error": "Se requiere ID de torneo"}), 400
        
    # Sincronización Automática: Asegurar que todos los equipos del torneo tengan una Inscripcion
    torneo = db.session.get(Torneo, torneo_id)
    if torneo:
        equipos_sin_ins = Equipo.query.filter(
            Equipo.torneo_id == torneo_id,
            ~Equipo.id.in_(db.session.query(Inscripcion.equipo_id).filter(Inscripcion.torneo_id == torneo_id))
        ).all()
        
        for eq in equipos_sin_ins:
            nueva_ins = Inscripcion(
                torneo_id=torneo_id,
                equipo_id=eq.id,
                monto_pactado_inscripcion=float(torneo.costo_inscripcion or 0),
                liga_id=torneo.liga_id
            )
            db.session.add(nueva_ins)
        
        # Sincronización JIT de liga_id para inscripciones huérfanas
        ins_missing_liga = Inscripcion.query.filter_by(torneo_id=torneo_id, liga_id=None).all()
        for i in ins_missing_liga:
            i.liga_id = torneo.liga_id
        
        # Sincronización JIT de liga_id para pagos del torneo
        pagos_missing_liga = Pago.query.filter_by(torneo_id=torneo_id, liga_id=None).all()
        for p in pagos_missing_liga:
            p.liga_id = torneo.liga_id

        if equipos_sin_ins or ins_missing_liga or pagos_missing_liga:
            db.session.commit()
            # Refrescar torneo para asegurar que los cambios son visibles
            db.session.refresh(torneo)

    query = Inscripcion.query
    query = apply_liga_filter(query, Inscripcion)
    
    if torneo_id:
        try:
            t_id = int(torneo_id)
            query = query.filter_by(torneo_id=t_id)
        except:
            return jsonify({"error": "ID de torneo inválido"}), 400

    # Define t_id and costo_arbitraje here, as they are used in the renderer
    t_id = int(torneo_id)
    costo_arbitraje = float(torneo.costo_arbitraje or 0) if torneo else 0

    # --- OPTIMIZACIÓN: Precarga de datos masiva (Bulk Loading) para evitar N+1 queries ---
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    pagination = query.paginate(page=page, per_page=per_page, error_out=False)
    inscritos = pagination.items
    
    ins_ids = [i.id for i in inscritos]
    equipo_ids = [i.equipo_id for i in inscritos]
    
    # 1. Totales de pago por inscripción y tipo
    pagos_totales_raw = db.session.query(
        Pago.inscripcion_id, Pago.tipo, db.func.sum(Pago.monto)
    ).filter(Pago.inscripcion_id.in_(ins_ids)).group_by(Pago.inscripcion_id, Pago.tipo).all()
    
    pagos_totales_map = {}
    for p_iid, p_tipo, p_monto in pagos_totales_raw:
        if p_iid not in pagos_totales_map: pagos_totales_map[p_iid] = {}
        pagos_totales_map[p_iid][p_tipo] = float(p_monto or 0)
        
    # 2. Partidos relevantes para los equipos de la página
    partidos_raw = Partido.query.filter(
        Partido.torneo_id == t_id,
        Partido.estado.in_(['Scheduled', 'Live', 'Played']),
        or_(Partido.equipo_local_id.in_(equipo_ids), Partido.equipo_visitante_id.in_(equipo_ids))
    ).order_by(Partido.jornada.asc()).all()
    
    partidos_map = {eid: [] for eid in equipo_ids}
    for p in partidos_raw:
        if p.equipo_local_id in partidos_map:
            partidos_map[p.equipo_local_id].append(p)
        if p.equipo_visitante_id in partidos_map:
            if p.equipo_visitante_id != p.equipo_local_id:
                partidos_map[p.equipo_visitante_id].append(p)
            
    # 3. Pagos específicos por partido (Arbitraje)
    pagos_partido_raw = db.session.query(
        Pago.inscripcion_id, 
        (Pago.partidoid if hasattr(Pago, 'partidoid') else Pago.partido_id), 
        db.func.sum(Pago.monto),
        db.func.max(Pago.id) # Add last pago ID for reference
    ).filter(
        Pago.inscripcion_id.in_(ins_ids), 
        (Pago.partidoid if hasattr(Pago, 'partidoid') else Pago.partido_id).isnot(None), 
        Pago.tipo == 'Arbitraje'
    ).group_by(Pago.inscripcion_id, Pago.partidoid if hasattr(Pago, 'partidoid') else Pago.partido_id).all()
    
    pagos_partido_map = {}
    for p_iid, p_pid, p_monto, p_last_id in pagos_partido_raw:
        pagos_partido_map[(p_iid, p_pid)] = {"monto": float(p_monto or 0), "id": p_last_id}
        
    # 4. Historial de pagos para la vista detallada
    pagos_lista_raw = Pago.query.filter(Pago.inscripcion_id.in_(ins_ids)).order_by(Pago.fecha.desc()).all()
    historial_map = {iid: [] for iid in ins_ids}
    for pg in pagos_lista_raw:
        historial_map[pg.inscripcion_id].append(pg)

    # 5. Mapa de información de partidos para consulta rápida de rivales
    partido_info_lookup = {p.id: p for p in partidos_raw}

    def renderer_ins_optimized(ins):
        iid = ins.id
        eid = ins.equipo_id
        totales = pagos_totales_map.get(iid, {})
        pagado_ins = totales.get('Inscripcion', 0)
        pagado_arb = totales.get('Arbitraje', 0)
        
        partidos_equipo = partidos_map.get(eid, [])
        partidos_jugados = sum(1 for p in partidos_equipo if p.estado == 'Played')
        partidos_programados = len(partidos_equipo)
        partidos_pendientes = partidos_programados - partidos_jugados
        
        esperado_arb = partidos_programados * costo_arbitraje
        saldo_arb = esperado_arb - pagado_arb
        
        detalle_partidos = []
        for p in partidos_equipo:
            rival_nombre = "Desconocido"
            if p.equipo_local_id == eid:
                rival_nombre = p.equipo_visitante.nombre if p.equipo_visitante else "Desconocido"
            else:
                rival_nombre = p.equipo_local.nombre if p.equipo_local else "Desconocido"
            
            p_pago_data = pagos_partido_map.get((iid, p.id), {"monto": 0, "id": None})
            monto_pagado_partido = p_pago_data["monto"]
            ultimo_pago_id = p_pago_data["id"]
            
            detalle_partidos.append({
                "partido_id": p.id,
                "jornada": p.jornada,
                "rival": rival_nombre,
                "fecha": p.fecha.strftime('%d/%m/%Y') if p.fecha else "Pendiente",
                "estado": p.estado,
                "tarifa": costo_arbitraje,
                "pagado": monto_pagado_partido,
                "saldo": costo_arbitraje - monto_pagado_partido,
                "ultimo_pago_id": ultimo_pago_id
            })

        return {
            "id": iid,
            "torneo_id": ins.torneo_id,
            "equipo_id": eid,
            "equipo_nombre": ins.equipo.nombre if ins.equipo else f"Equipo {eid}",
            "monto_pactado": ins.monto_pactado_inscripcion,
            "pagado_inscripcion": pagado_ins,
            "pagado_arbitraje": pagado_arb,
            "saldo_inscripcion": float(ins.monto_pactado_inscripcion - pagado_ins),
            "partidos_jugados": partidos_jugados,
            "partidos_programados": partidos_programados,
            "partidos_pendientes": partidos_pendientes,
            "tarifa_arbitraje": costo_arbitraje,
            "esperado_arbitraje": esperado_arb,
            "saldo_arbitraje": saldo_arb,
            "detalle_partidos": detalle_partidos,
            "historial_pagos": [{
                "id": pg.id,
                "monto": pg.monto,
                "tipo": pg.tipo,
                "fecha": pg.fecha.strftime('%d/%m/%Y') if pg.fecha else "??",
                "metodo": pg.metodo,
                "partido_id": pg.partido_id,
                "rival": (
                    (partido_info_lookup[pg.partido_id].equipo_visitante.nombre if partido_info_lookup[pg.partido_id].equipo_local_id == eid else partido_info_lookup[pg.partido_id].equipo_local.nombre)
                    if pg.partido_id in partido_info_lookup and pg.tipo == 'Arbitraje' else None
                )
            } for pg in historial_map.get(iid, [])]
        }

    items = [renderer_ins_optimized(item) for item in inscritos]
    return jsonify({
        'items': items,
        'pagination': {
            'page': pagination.page,
            'per_page': pagination.per_page,
            'total_items': pagination.total,
            'total_pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }
    })

@app.route('/api/inscripciones/<int:inscripcion_id>', methods=['PUT', 'PATCH'])
@csrf.exempt
def update_inscripcion(inscripcion_id):
    # Control de Permisos: Solo cuentas principales
    p_roles = ['admin', 'ejecutivo', 'dueño_liga', 'super_arbitro', 'equipo']
    if session.get('user_rol') not in p_roles:
        return jsonify({"error": "Solo las cuentas principales pueden modificar inscripciones."}), 403

    data = request.json
    ins = Inscripcion.query.get(inscripcion_id)
    if not ins:
        return jsonify({"error": "Inscripción no encontrada"}), 404
        
    if 'monto_pactado' in data:
        ins.monto_pactado_inscripcion = float(data['monto_pactado'])
        
    try:
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/pagos', methods=['POST'])
@csrf.exempt
def handle_pagos():
    data = request.json
    print(f"DEBUG PAGOS - Data received: {data}")
    
    inscripcion_id = data.get('inscripcion_id')
    monto = data.get('monto')
    tipo = data.get('tipo')
    
    print(f"DEBUG PAGOS - Fields: inscripcion_id={inscripcion_id}, monto={monto}, tipo={tipo}")
    
    if not inscripcion_id or not monto or not tipo:
        print(f"DEBUG PAGOS - Missing fields check failed. data: {data}")
        return jsonify({"error": "Datos incompletos para la donación"}), 400
        
    try:
        ins = Inscripcion.query.get(inscripcion_id)
        if not ins:
            return jsonify({"error": "Inscripción no encontrada"}), 404
            
        # Control de Permisos: Solo cuentas principales
        p_roles = ['admin', 'ejecutivo', 'dueño_liga', 'super_arbitro', 'equipo']
        if session.get('user_rol') not in p_roles:
            return jsonify({"error": "Solo las cuentas principales pueden registrar donaciones."}), 403

        nuevo_pago = Pago(
            inscripcion_id=inscripcion_id,
            monto=float(monto),
            tipo=tipo,
            metodo=data.get('metodo', 'Efectivo'),
            comentario=data.get('comentario', ''),
            partido_id=data.get('partido_id'),
            liga_id=ins.liga_id,
            torneo_id=ins.torneo_id
        )
        db.session.add(nuevo_pago)
        db.session.commit()
        
        # Enviar notificación Telegram si hay árbitro vinculado
        if nuevo_pago.tipo == 'Arbitraje' and nuevo_pago.partido_id:
            try:
                send_telegram_ticket_notification(nuevo_pago)
            except Exception as te:
                print(f"Error enviando notificación Telegram: {te}")
        
        # Datos enriquecidos para el ticket
        ins = Inscripcion.query.get(inscripcion_id)
        torneo = ins.torneo
        
        # Calcular saldos actuales
        pagado_ins = db.session.query(db.func.sum(Pago.monto)).filter_by(inscripcion_id=ins.id, tipo='Inscripcion').scalar() or 0
        pagado_arb = db.session.query(db.func.sum(Pago.monto)).filter_by(inscripcion_id=ins.id, tipo='Arbitraje').scalar() or 0
        
        reglas_cancha = ""
        cancha_asignada = None
        if torneo and torneo.cancha:
            nombre_cancha = torneo.cancha.strip()
            cancha_asignada = Cancha.query.filter(Cancha.nombre.ilike(nombre_cancha)).first()
            if cancha_asignada and cancha_asignada.notas:
                reglas_cancha = f"REGLAS DE LA SEDE ({cancha_asignada.nombre}):\n{cancha_asignada.notas}"
            sede_nombre = cancha_asignada.nombre if cancha_asignada else torneo.cancha
        else:
            sede_nombre = "Por definir"

        import string as _str3, random as _rnd3
        folio_pago = 'FUT-' + ''.join(_rnd3.choices(_str3.ascii_uppercase + _str3.digits, k=6))

        # Información del partido si existe
        partido_info = None
        if nuevo_pago.partido_id:
            from models import Partido
            p = Partido.query.get(nuevo_pago.partido_id)
            if p:
                partido_info = {
                    "rivales": f"{p.equipo_local.nombre} vs {p.equipo_visitante.nombre}",
                    "jornada": p.jornada,
                    "fecha": p.fecha.strftime('%d/%m/%Y') if p.fecha else "S/F"
                }

        return jsonify({
            "success": True,
            "pago_id": nuevo_pago.id,
            "folio": folio_pago,
            "equipo": ins.equipo.nombre,
            "torneo": torneo.nombre,
            "sede": sede_nombre.strip() if sede_nombre else "Por definir",
            "monto_abonado": float(nuevo_pago.monto),
            "tipo": nuevo_pago.tipo,
            "fecha": nuevo_pago.fecha.strftime('%d/%m/%Y %H:%M'),
            "metodo": nuevo_pago.metodo,
            "monto_pactado": float(ins.monto_pactado_inscripcion),
            "total_pagado": float(pagado_ins) if nuevo_pago.tipo == 'Inscripcion' else float(pagado_arb),
            "saldo_pendiente": float(ins.monto_pactado_inscripcion - pagado_ins) if nuevo_pago.tipo == 'Inscripcion' else 0,
            "partido": partido_info,
            "premios": torneo.premios or "",
            "reglamento": torneo.reglamento or "",
            "clausulas": (torneo.clausulas if torneo and torneo.clausulas else "") + ("\n\n" + reglas_cancha if reglas_cancha else ""),
            "fecha_inicio_torneo": torneo.fecha_inicio.strftime('%d/%m/%Y') if torneo.fecha_inicio else "Pendiente"
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

def send_telegram_ticket_notification(pago):
    """Envía un resumen de pago vía Telegram al árbitro o administrador si están configurados."""
    token = app.config.get('TELEGRAM_BOT_TOKEN')
    if not token: return
    
    # 1. Obtener árbitro del partido
    from models import Partido, Arbitro
    p = Partido.query.get(pago.partido_id)
    if not p or not p.arbitro or not p.arbitro.telegram_id:
        return # No hay a quien enviar
        
    chat_id = p.arbitro.telegram_id
    
    mensaje = (
        f"✅ *PAGO DE ARBITRAJE RECIBIDO*\n\n"
        f"💰 *Monto:* ${pago.monto:,.2f}\n"
        f"⚽ *Partido:* {p.equipo_local.nombre} vs {p.equipo_visitante.nombre}\n"
        f"📅 *Jornada:* {p.jornada}\n"
        f"🛡️ *Torneo:* {p.torneo.nombre}\n"
        f"🏦 *Método:* {pago.metodo}\n"
        f"🔖 *Comentario:* {pago.comentario or 'S/C'}\n\n"
        f"¡Gracias por tu servicio! ⚽🛡️"
    )
    
    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": mensaje,
        "parse_mode": "Markdown"
    }
    
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Telegram API Error: {e}")

@app.route('/api/pagos/<int:id>', methods=['DELETE'])
@csrf.exempt
def handle_pago_delete(id):
    # Control de Permisos
    if session.get('user_rol') not in ['admin', 'ejecutivo', 'dueño_liga', 'super_arbitro']:
        return jsonify({"error": "No tiene permisos para anular pagos."}), 403
        
    pago = Pago.query.get_or_404(id)
    try:
        db.session.delete(pago)
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# El modelo Partido ha sido movido a models.py

# --- API Routes: Matches ---

# La función get_partidos ha sido consolidada en una versión única y paginada más adelante en el archivo.

@app.route('/api/partidos/<int:id>', methods=['PUT', 'DELETE'])
@csrf.exempt
def handle_partido(id):
    partido = Partido.query.get_or_404(id)
    if request.method == 'DELETE':
        db.session.delete(partido)
        db.session.commit()
        return jsonify({'success': True})
    if request.method == 'PUT':
        data = request.json
        if 'fecha' in data and data['fecha']:
            try:
                partido.fecha = datetime.strptime(data['fecha'], '%Y-%m-%d').date()
            except ValueError:
                pass
        if 'hora' in data:
            partido.hora = data['hora']
        if 'cancha' in data:
            partido.cancha = data['cancha']
        if 'arbitro_id' in data:
            partido.arbitro_id = data['arbitro_id'] or None
        if 'goles_local' in data and data['goles_local'] is not None:
            partido.goles_local = int(data['goles_local'])
        if 'goles_visitante' in data and data['goles_visitante'] is not None:
            partido.goles_visitante = int(data['goles_visitante'])
        if 'estado' in data:
            partido.estado = data['estado']
        
        db.session.commit()
        
        # Sincronizar eventos de gol con el marcador
        sync_match_goals(partido)
        db.session.commit()
        
        # Intentar inicio de liguilla automática si es liga regular al marcar como jugado
        if partido.estado == 'Played':
            check_and_start_liguilla_auto(partido.torneo_id)
            
        return jsonify(partido.to_dict())

def sync_match_goals(partido):
    import random
    target_local = partido.goles_local or 0
    target_vis = partido.goles_visitante or 0
    
    goal_events = EventoPartido.query.filter_by(partido_id=partido.id, tipo='Gol').all()
    local_events = [e for e in goal_events if e.equipo_id == partido.equipo_local_id]
    vis_events = [e for e in goal_events if e.equipo_id == partido.equipo_visitante_id]
    
    if len(local_events) > target_local:
        for _ in range(len(local_events) - target_local):
            db.session.delete(local_events.pop())
    elif len(local_events) < target_local:
        jugadores = Jugador.query.filter_by(equipo_id=partido.equipo_local_id).all()
        for _ in range(target_local - len(local_events)):
            j_id = random.choice(jugadores).id if jugadores else None
            db.session.add(EventoPartido(partido_id=partido.id, equipo_id=partido.equipo_local_id, jugador_id=j_id, minuto=random.randint(1, 90), periodo=random.choice([1, 2]), tipo='Gol'))

    if len(vis_events) > target_vis:
        for _ in range(len(vis_events) - target_vis):
            db.session.delete(vis_events.pop())
    elif len(vis_events) < target_vis:
        jugadores = Jugador.query.filter_by(equipo_id=partido.equipo_visitante_id).all()
        for _ in range(target_vis - len(vis_events)):
            j_id = random.choice(jugadores).id if jugadores else None
            db.session.add(EventoPartido(partido_id=partido.id, equipo_id=partido.equipo_visitante_id, jugador_id=j_id, minuto=random.randint(1, 90), periodo=random.choice([1, 2]), tipo='Gol'))

def expand_training_dates(grupo):
    """
    Expands a training group's schedule into individual sessions with dates.
    Robustly supports 2 and 3 letter day abbreviations.
    """
    # Expanded map to support 2-letter (lu, ma, mi...) and 3-letter (lun, mar, mie...)
    days_map = {
        'lu': 0, 'ma': 1, 'mi': 2, 'ju': 3, 'vi': 4, 'sa': 5, 'do': 6,
        'lun': 0, 'mar': 1, 'mie': 2, 'mié': 2, 'jue': 3, 'vie': 4, 'sab': 5, 'sáb': 5, 'dom': 6
    }
    
    selected_weekdays = []
    if grupo.dias:
        # Split by comma or slash and clean up
        dias_list = [d.strip().lower() for d in grupo.dias.replace('/', ',').split(',')]
        for d in dias_list:
            if not d: continue
            # Try 3 letters first, then 2
            found = False
            for length in [3, 2]:
                short = d[:length]
                if short in days_map:
                    selected_weekdays.append(days_map[short])
                    found = True
                    break
    
    # If no days recognized, but it has some text, maybe it's full name
    if not selected_weekdays and grupo.dias:
        full_days = {'lunes': 0, 'martes': 1, 'miercoles': 2, 'miércoles': 2, 'jueves': 3, 'viernes': 4, 'sabado': 5, 'sábado': 5, 'domingo': 6}
        for k, v in full_days.items():
            if k in grupo.dias.lower():
                selected_weekdays.append(v)

    if not selected_weekdays:
        return []

    # Default start date to today if not set, to ensure visibility
    start_proj = grupo.fecha_inicio or date.today()
    
    sessions = []
    current_date = start_proj
    
    # End date: group's end date or 4 months from now
    limit_date = date.today() + timedelta(days=120)
    end_date = grupo.fecha_fin or limit_date
    if end_date > limit_date: end_date = limit_date
    
    max_days = 150 # Safety limit
    day_count = 0
    
    while current_date <= end_date and day_count < max_days:
        if current_date.weekday() in selected_weekdays:
            # Parse horario for start/end
            hora_inicio = "17:00"
            hora_fin = None
            raw_horario = (grupo.horario or "").lower()
            
            if " a " in raw_horario:
                parts = raw_horario.split(" a ")
                hora_inicio = parts[0].strip()
                hora_fin = parts[1].strip()
            elif "-" in raw_horario:
                parts = raw_horario.split("-")
                hora_inicio = parts[0].strip()
                hora_fin = parts[1].strip()
            elif raw_horario:
                hora_inicio = raw_horario.strip()

            # Ensure HH:MM (Robust parsing)
            def clean_time(t):
                try:
                    if not t: return None
                    t = str(t).strip().replace(".", ":")
                    parts = t.split()
                    if not parts: return None
                    t = parts[0]
                    if ":" not in t:
                        # Try to handle just "15" -> "15:00"
                        digits = "".join(filter(str.isdigit, t))
                        if not digits: return None
                        return f"{digits.zfill(2)}:00"
                    
                    p = t.split(":")
                    h = "".join(filter(str.isdigit, p[0])) or "00"
                    m = "".join(filter(str.isdigit, p[1])) if len(p) > 1 else "00"
                    return f"{h.zfill(2)}:{m.zfill(2)[:2]}"
                except:
                    return None

            h_start = clean_time(hora_inicio) or "17:00"
            h_end = clean_time(hora_fin)

            sessions.append({
                "id": f"train_{grupo.id}_{current_date.strftime('%Y%m%d')}",
                "type": "Training",
                "title": f"👟 {grupo.nombre}",
                "equipo_local": grupo.nombre,
                "equipo_visitante": "Entrenamiento",
                "fecha": current_date.strftime('%Y-%m-%d'),
                "hora": h_start,
                "hora_fin": h_end,
                "horario_texto": grupo.horario,
                "cancha": grupo.cancha or "Principal",
                "estado": "Scheduled",
                "color": "#3b82f6",
                "grupo_id": grupo.id,
                "categoria": grupo.categoria or "General",
                "torneo_name": "Academia"
            })
        current_date += timedelta(days=1)
        day_count += 1
        
    return sessions

@app.route('/api/entrenamientos/grupos', methods=['GET'])
def get_training_groups():
    """Returns training groups with pagination and league filter."""
    torneo_id = request.args.get('torneo_id', type=int)
    
    query = GrupoEntrenamiento.query.filter_by(activo=True)
    query = apply_liga_filter(query, GrupoEntrenamiento)
    
    if torneo_id:
        query = query.filter_by(torneo_id=torneo_id)
        
    return paginate_query(query)

@app.route('/api/calendar/all', methods=['GET'])
def get_calendar_all():
    """Returns both matches and training sessions for the calendar."""
    torneo_id = request.args.get('torneo_id')
    include_training = request.args.get('training', 'true').lower() == 'true'
    category_filter = request.args.get('categoria')
    
    # 1. Fetch matches
    result = []
    if torneo_id != 'none':
        query = Partido.query
        query = apply_liga_filter(query, Partido)
            
        if torneo_id and torneo_id != 'all':
            query = query.filter_by(torneo_id=int(torneo_id))
        
        partidos = query.all()
        result = [p.to_dict() for p in partidos]
    
    # 2. Fetch and expand training sessions if requested
    if include_training:
        query_g = GrupoEntrenamiento.query.filter_by(activo=True)
        # Filtrado Multi-tenant para entrenamientos
        query_g = apply_liga_filter(query_g, GrupoEntrenamiento)
        
        if category_filter and category_filter != 'all':
            query_g = query_g.filter_by(categoria=category_filter)
            
        grupos = query_g.all()
        for g in grupos:
            result.extend(expand_training_dates(g))
            
    return jsonify(result)

@app.route('/api/entrenamientos/categorias', methods=['GET'])
def get_training_categories():
    """Returns list of unique training categories."""
    cats = db.session.query(GrupoEntrenamiento.categoria).filter(GrupoEntrenamiento.categoria != None).distinct().all()
    return jsonify([c[0] for c in cats if c[0]])

@app.route('/api/partidos', methods=['GET'])
def get_partidos():
    """Returns all matches, with pagination and filtering."""
    from sqlalchemy.orm import joinedload
    query = Partido.query.options(
        joinedload(Partido.torneo),
        joinedload(Partido.equipo_local),
        joinedload(Partido.equipo_visitante),
        joinedload(Partido.arbitro)
    )
    query = apply_liga_filter(query, Partido)

    torneo_id = request.args.get('torneo_id', type=int)
    if torneo_id:
        query = query.filter_by(torneo_id=torneo_id)

    estado = request.args.get('estado')
    if estado:
        query = query.filter_by(estado=estado)

    jornada = request.args.get('jornada', type=int)
    if jornada:
        query = query.filter_by(jornada=jornada)

    fecha = request.args.get('fecha')
    if fecha:
        try:
            fecha_dt = datetime.strptime(fecha, '%Y-%m-%d').date()
            query = query.filter_by(fecha=fecha_dt)
        except ValueError:
            pass

    start_date_str = request.args.get('start_date')
    end_date_str = request.args.get('end_date')
    if start_date_str and end_date_str:
        try:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
            query = query.filter(Partido.fecha.between(start_date, end_date))
        except ValueError:
            pass

    # Soporte para filtrar por equipo específico en el listado general
    equipo_id = request.args.get('equipo_id', type=int)
    if equipo_id:
        from sqlalchemy import or_
        query = query.filter(or_(Partido.equipo_local_id == equipo_id, Partido.equipo_visitante_id == equipo_id))

    # Filtro de solo pendientes de arbitraje
    solo_pendientes = request.args.get('solo_pendientes', '0') == '1'
    if solo_pendientes and equipo_id:
        # Excluir partidos que ya tengan un pago de Arbitraje registrado para esta inscripción
        # Buscamos la inscripción del equipo en este torneo (o liga si aplica)
        # Nota: handle_pago asocia pagos via inscripcion_id
        from models import Inscripcion, Pago
        pago_exists = db.session.query(Pago.partido_id).filter(
            Pago.tipo == 'Arbitraje',
            Pago.partido_id.isnot(None),
            Pago.inscripcion_id.in_(
                db.session.query(Inscripcion.id).filter(Inscripcion.equipo_id == equipo_id)
            )
        )
        query = query.filter(~Partido.id.in_(pago_exists))

    query = query.order_by(Partido.fecha.desc(), Partido.hora.desc(), Partido.id.desc())
    return paginate_query(query)

@app.route('/api/partidos_equipo', methods=['GET'])
def get_partidos_equipo():
    """Returns matches for a specific team (whether home or away)."""
    equipo_id = request.args.get('equipo_id', type=int)
    if not equipo_id:
        return jsonify({"error": "Se requiere equipo_id"}), 400
        
    query = Partido.query.filter(
        or_(Partido.equipo_local_id == equipo_id, Partido.equipo_visitante_id == equipo_id)
    ).order_by(Partido.fecha.desc(), Partido.id.desc())
    
    return paginate_query(query)

# --- API Route: Detalles del Partido (Goles y Tarjetas) ---

@app.route('/api/partido/<int:partido_id>/detalles', methods=['GET'])
def get_partido_detalles(partido_id):
    """Returns goals and cards for a specific match from eventos_partido table."""
    partido = apply_liga_filter(Partido.query, Partido).filter_by(id=partido_id).first_or_404()
    eventos = EventoPartido.query.filter_by(partido_id=partido_id).order_by(EventoPartido.minuto).all()

    goles = []
    tarjetas = []

    for ev in eventos:
        if ev.tipo == 'Gol':
            goles.append({
                'jugador': ev.jugador.nombre if ev.jugador else 'Desconocido',
                'equipo': ev.equipo.nombre if ev.equipo else '',
                'minuto': ev.minuto,
                'periodo': ev.periodo,
            })
        elif ev.tipo in ('Amarilla', 'Roja'):
            tarjetas.append({
                'jugador': ev.jugador.nombre if ev.jugador else 'Desconocido',
                'equipo': ev.equipo.nombre if ev.equipo else '',
                'minuto': ev.minuto,
                'tipo': ev.tipo,
                'nota': ev.nota or '',
            })

    return jsonify({
        'partido_id': partido_id,
        'estado': partido.estado,
        'arbitro': partido.arbitro.nombre if (hasattr(partido, 'arbitro') and partido.arbitro) else 'Por asignar',
        'goles_local': partido.goles_local,
        'goles_visitante': partido.goles_visitante,
        'goles': goles,
        'tarjetas': tarjetas,
    })

@app.route('/api/torneos/<int:torneo_id>/generar_rol', methods=['POST'])
@csrf.exempt
def generar_rol(torneo_id):
    torneo = apply_liga_filter(Torneo.query, Torneo).filter_by(id=torneo_id).first_or_404()
    equipos = Equipo.query.filter_by(torneo_id=torneo_id).all()
    
    if len(equipos) < 2:
        return jsonify({'error': 'Se necesitan al menos 2 equipos para generar el rol.'}), 400

    try:
        partidos_existentes = Partido.query.filter_by(torneo_id=torneo_id).all()
        for p in partidos_existentes:
            # NO eliminar partidos jugados, en curso o con marcador registrado
            has_score = p.goles_local is not None or p.goles_visitante is not None
            if p.estado in ['Played', 'Live'] or has_score:
                continue
            
            # ELIMINACIÓN EN CASCADA MANUAL: Borrar eventos asociados
            EventoPartido.query.filter_by(partido_id=p.id).delete()
            
            db.session.delete(p)
        db.session.flush()
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': f'No se pudieron eliminar los partidos previos: {str(e)}'}), 500

    arbitros = Arbitro.query.filter_by(activo=True).all()
    arbitro_oficial_id = torneo.arbitro_id
    formato = torneo.formato or "Liga"
    tipo_rol = request.args.get('tipo', 'ida')
    teams_per_group = request.args.get('teams_per_group', 4, type=int)
    
    # Debug log
    print(f"DEBUG: Generando rol formato={formato}, tipo={tipo_rol}, teams_per_group={teams_per_group}")

    partidos_creados = []
    ab_idx = 0
    
    # Mapa de partidos que ya existen y no queremos duplicar
    partidos_protegidos = {
        (p.equipo_local_id, p.equipo_visitante_id, p.jornada, p.fase) 
        for p in Partido.query.filter_by(torneo_id=torneo_id).filter(
            or_(Partido.estado.in_(['Played', 'Live']), Partido.goles_local != None, Partido.goles_visitante != None)
        ).all()
    }

    if formato == "Liga":
        if len(equipos) % 2 != 0: equipos.append(None)
        n = len(equipos)
        iteraciones = 2 if tipo_rol == 'doble' else 1
        jornada_offset = 0
        for vuelta in range(iteraciones):
            temp_equipos = list(equipos)
            for round_num in range(1, n):
                j_num = round_num + jornada_offset
                for i in range(n // 2):
                    loc, vis = temp_equipos[i], temp_equipos[n - 1 - i]
                    if loc and vis:
                        l_id, v_id = (vis.id, loc.id) if vuelta == 1 else (loc.id, vis.id)
                        
                        # Saltar si ya existe un partido jugado para esta combinación
                        if (l_id, v_id, j_num, "Regular") in partidos_protegidos:
                            continue
                            
                        arb_id = arbitro_oficial_id or (arbitros[ab_idx % len(arbitros)].id if arbitros else None)
                        if not arbitro_oficial_id and arbitros: ab_idx += 1
                        p = Partido(
                            torneo_id=torneo_id, 
                            jornada=j_num, 
                            equipo_local_id=l_id, 
                            equipo_visitante_id=v_id, 
                            arbitro_id=arb_id,
                            liga_id=torneo.liga_id
                        )
                        db.session.add(p)
                        partidos_creados.append(p)
                temp_equipos.insert(1, temp_equipos.pop())
            jornada_offset += (n - 1)

    elif formato == "Eliminación Directa":
        import random
        random.shuffle(equipos)
        n_e = len(equipos)
        fase = "Final" if n_e <= 2 else ("Semifinal" if n_e <= 4 else ("4tos de Final" if n_e <= 8 else ("8vos de Final" if n_e <= 16 else "Ronda Eliminatoria")))
        for i in range(0, n_e - 1, 2):
            l_id, v_id = equipos[i].id, equipos[i+1].id
            
            # Saltar si ya existe un partido jugado para esta combinación en jornada 1
            if (l_id, v_id, 1, fase) in partidos_protegidos:
                continue
                
            arb_id = arbitro_oficial_id or (arbitros[ab_idx % len(arbitros)].id if arbitros else None)
            if not arbitro_oficial_id and arbitros: ab_idx += 1
            p = Partido(
                torneo_id=torneo_id, 
                jornada=1, 
                equipo_local_id=l_id, 
                equipo_visitante_id=v_id, 
                arbitro_id=arb_id, 
                fase=fase,
                liga_id=torneo.liga_id
            )
            db.session.add(p)
            partidos_creados.append(p)

    elif formato == "Fase de Grupos":
        import random
        # Reparto automático o limpieza si se solicita
        # Forzamos limpieza si se pasó el parámetro teams_per_group para asegurar reparto fresco
        if teams_per_group > 0:
            for e in equipos:
                e.grupo = None
            db.session.flush()

        # Reparto automático si nadie tiene grupo (que ahora será siempre si hay teams_per_group)
        if not any(e.grupo for e in equipos):
            random.shuffle(equipos)
            num_e = len(equipos)
            # Calculamos cuántos grupos debería haber para que el tamaño sea cercano al pedido
            # pero evitando que queden equipos solos
            num_grupos = max(1, num_e // teams_per_group)
            
            letras = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            for idx, e in enumerate(equipos):
                # Reparto balanceado usando el operador módulo sobre el número de grupos calculado
                g_idx = idx % num_grupos
                e.grupo = f"Grupo {letras[g_idx % len(letras)]}"
        
        grupos = {}
        for e in equipos:
            g = e.grupo or "Sin Grupo"
            if g not in grupos: grupos[g] = []
            grupos[g].append(e)

        iteraciones = 2 if tipo_rol == 'doble' else 1
        for g_name, g_teams in grupos.items():
            if len(g_teams) < 2: continue
            j_offset = 0
            for v in range(iteraciones):
                pool = list(g_teams)
                if len(pool) % 2 != 0: pool.append(None)
                n_p = len(pool)
                # Round Robin dentro del grupo
                for r in range(n_p - 1):
                    j_num = r + 1 + j_offset
                    for i in range(n_p // 2):
                        loc, vis = pool[i], pool[n_p - 1 - i]
                        if loc and vis:
                            # Invertir localía en la segunda vuelta
                            l_id, v_id = (vis.id, loc.id) if v == 1 else (loc.id, vis.id)
                            
                            # Saltar si ya existe un partido jugado
                            if (l_id, v_id, j_num, "Fase de Grupos") in partidos_protegidos:
                                continue
                                
                            arb_id = arbitro_oficial_id or (arbitros[ab_idx % len(arbitros)].id if arbitros else None)
                            if not arbitro_oficial_id and arbitros: ab_idx += 1
                            
                            p = Partido(
                                torneo_id=torneo_id, 
                                jornada=j_num, 
                                equipo_local_id=l_id, 
                                equipo_visitante_id=v_id, 
                                arbitro_id=arb_id, 
                                fase="Fase de Grupos",
                                liga_id=torneo.liga_id
                            )
                            db.session.add(p)
                            partidos_creados.append(p)
                    # Rotación de pool
                    pool.insert(1, pool.pop())
                # El offset de jornada debe avanzar después de cada vuelta completa del grupo
                j_offset += (n_p - 1)

    db.session.commit()
    return jsonify({'success': True, 'partidos_generados': len(partidos_creados)})

@app.route('/api/torneos/<int:torneo_id>/auto_grupos', methods=['POST'])
@csrf.exempt
def auto_distribuir_grupos(torneo_id):
    try:
        data = request.json or {}
        num_grupos = int(data.get('num_grupos', 2))
        torneo = Torneo.query.get_or_404(torneo_id)
        equipos = Equipo.query.filter_by(torneo_id=torneo_id).all()
        
        if not equipos:
            return jsonify({"success": False, "message": "No hay equipos inscritos"}), 400
            
        import random
        random.shuffle(equipos)
        
        letras = "ABCDEFGH"
        for i, equipo in enumerate(equipos):
            g_idx = i % num_grupos
            equipo.grupo = f"Grupo {letras[g_idx % len(letras)]}"
            
        db.session.commit()
        return jsonify({"success": True, "message": f"Equipos distribuidos en {num_grupos} grupos."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

@app.route('/api/torneos/<int:torneo_id>/auto_schedule', methods=['POST'])
@csrf.exempt
def auto_schedule_torneo(torneo_id):
    import math
    from datetime import timedelta
    
    torneo = apply_liga_filter(Torneo.query, Torneo).filter_by(id=torneo_id).first_or_404()
    partidos = Partido.query.filter_by(torneo_id=torneo_id).order_by(Partido.jornada, Partido.id).all()
    
    if not partidos:
        return jsonify({'error': 'No hay partidos generados para este torneo.'}), 400

    data = request.json or {}
    manual_weekdays = data.get('allowed_weekdays')
    manual_start_time = data.get('start_time')
    manual_end_time = data.get('end_time')
    max_matches_per_day = data.get('max_matches_per_day')

    # 1. Parse tournament settings
    if manual_weekdays is not None and isinstance(manual_weekdays, list) and len(manual_weekdays) > 0:
        allowed_weekdays = sorted(list(set([int(x) for x in manual_weekdays])))
    else:
        # Parse from string
        day_map = {
            0: ["lunes", "lun", "lu"],
            1: ["martes", "mar", "ma"],
            2: ["miercoles", "miércoles", "mier", "mié", "mie", "mi"],
            3: ["jueves", "jue", "ju"],
            4: ["viernes", "vie", "vi"],
            5: ["sabado", "sábado", "sab", "sáb", "sa"],
            6: ["domingo", "dom", "do"]
        }
        allowed_weekdays = []
        search_text = f"{(torneo.dias_juego or '')} {(torneo.horario_juego or '')}".lower()
        for day_num, patterns in day_map.items():
            if any(p in search_text for p in patterns):
                allowed_weekdays.append(day_num)
        
        if not allowed_weekdays:
            allowed_weekdays = [5, 6] # Default Sat/Sun
        allowed_weekdays = sorted(list(set(allowed_weekdays)))
    
    # Time range logic
    start_time_str = manual_start_time if manual_start_time else "08:00"
    end_time_str = manual_end_time if manual_end_time else "20:00"
    
    if not manual_start_time or not manual_end_time:
        try:
            horario_raw = getattr(torneo, 'horario_juego', '')
            if " a " in horario_raw:
                parts = horario_raw.split(" a ")
                time_part_start = parts[0].split()[-1]
                time_part_end = parts[1].split()[0]
                if ":" in time_part_start: start_time_str = time_part_start
                if ":" in time_part_end: end_time_str = time_part_end
        except:
            pass

    # Match duration
    tiempos = int(torneo.num_tiempos or 2)
    dur_min = int(torneo.duracion_tiempo or 25)
    descanso = int(torneo.descanso or 10)
    match_duration_total = (tiempos * dur_min) + descanso
    
    # 2. Group matches by jornada
    from collections import defaultdict
    jornadas = defaultdict(list)
    for p in partidos:
        jornadas[p.jornada].append(p)
    
    sorted_jornada_numbers = sorted(jornadas.keys())
    
    # 3. Scheduling state
    current_date = torneo.fecha_inicio or datetime.now().date()
    
    # Helper functions
    def get_minutes(time_str):
        try:
            h, m = map(int, time_str.split(':'))
            return h * 60 + m
        except:
            return 480 # 08:00 default
            
    def format_minutes(total_min):
        h = (total_min // 60) % 24
        m = total_min % 60
        return f"{h:02d}:{m:02d}"

    start_min = get_minutes(start_time_str)
    end_min = get_minutes(end_time_str)

    # Move to the first allowed weekday starting from fecha_inicio
    while current_date.weekday() not in allowed_weekdays:
        current_date += timedelta(days=1)

    for j_num in sorted_jornada_numbers:
        jornada_matches = jornadas[j_num]
        if not jornada_matches: continue

        # Distribute matches across allowed days
        day_dates = {}
        for w_day in allowed_weekdays:
            days_to_add = (w_day - current_date.weekday() + 7) % 7
            day_dates[w_day] = current_date + timedelta(days=days_to_add)

        # Track time and count per day
        day_current_min = {w_day: start_min for w_day in allowed_weekdays}
        day_match_count = {w_day: 0 for w_day in allowed_weekdays}
        
        # Primero, identificar partidos que NO se mueven para ocupar sus horarios
        for p in jornada_matches:
            has_score = p.goles_local is not None or p.goles_visitante is not None
            if p.estado != 'Scheduled' or has_score:
                for w_day, d_date in day_dates.items():
                    if p.fecha == d_date and p.hora:
                        p_min = get_minutes(p.hora)
                        if p_min >= day_current_min[w_day]:
                            day_current_min[w_day] = p_min + match_duration_total
                        day_match_count[w_day] += 1

        # Segundo, programar los que SÍ son pendientes
        pending_matches = [p for p in jornada_matches if p.estado == 'Scheduled' and p.goles_local is None and p.goles_visitante is None]
        current_w_idx = 0
        
        for p in pending_matches:
            # Buscar el siguiente día disponible
            max_attempts = len(allowed_weekdays) * 3
            attempts = 0
            
            while attempts < max_attempts:
                w_day = allowed_weekdays[current_w_idx % len(allowed_weekdays)]
                
                over_max_count = max_matches_per_day and day_match_count[w_day] >= max_matches_per_day
                over_time = (day_current_min[w_day] + match_duration_total) > end_min
                
                if not over_max_count and not over_time:
                    break
                    
                current_w_idx += 1
                attempts += 1
                
            w_day = allowed_weekdays[current_w_idx % len(allowed_weekdays)]
            
            p.fecha = day_dates[w_day]
            p.hora = format_minutes(day_current_min[w_day])
            p.cancha = torneo.cancha or "Cancha Principal"
            
            day_current_min[w_day] += match_duration_total
            day_match_count[w_day] += 1
            # Eliminado: current_w_idx += 1 
            # Esto permite que el sistema llene un día completo antes de saltar al siguiente.

        # Advance current_date to the NEXT week
        current_date = min(day_dates.values()) + timedelta(days=7)
        while current_date.weekday() not in allowed_weekdays:
            current_date += timedelta(days=1)
        
    db.session.commit()
    return jsonify({'success': True, 'scheduled_count': len(partidos)})

# Los modelos de eventos y árbitros han sido movidos a models.py


def auto_avanzar_ronda(torneo_id):
    """Lógica para avanzar automáticamente a la siguiente ronda en torneos de eliminación."""
    torneo = Torneo.query.get(torneo_id)
    if not torneo:
        return False
        
    # Si el formato no es Eliminación Directa, solo permitimos avanzar si ya estamos en fases finales (Liguilla)
    if torneo.formato != "Eliminación Directa":
        # Verificar si el último partido tiene fase (ej: 4tos de Final)
        ultimo = Partido.query.filter_by(torneo_id=torneo_id).order_by(Partido.jornada.desc()).first()
        if not ultimo or not ultimo.fase:
            return False
        
    # Obtener la jornada actual (máxima jornada que tiene partidos)
    ultimo_partido = Partido.query.filter_by(torneo_id=torneo_id).order_by(Partido.jornada.desc()).first()
    if not ultimo_partido:
        return False
        
    jornada_actual = ultimo_partido.jornada
    
    # Verificar si todos los partidos de esta jornada han terminado
    partidos_ronda = Partido.query.filter_by(torneo_id=torneo_id, jornada=jornada_actual).all()
    if not all(p.estado == 'Played' for p in partidos_ronda):
        return False
        
    # Verificar si ya se generó la siguiente jornada
    siguiente_existe = Partido.query.filter_by(torneo_id=torneo_id, jornada=jornada_actual + 1).first()
    if siguiente_existe:
        return False
        
    # Recopilar ganadores y perdedores
    ganadores = []
    perdedores = []
    for p in partidos_ronda:
        winner_id = p.ganador_id
        # Si no hay ganador_id explícito, intentar determinar por goles
        if not winner_id:
            gl = p.goles_local or 0
            gv = p.goles_visitante or 0
            if gl > gv: winner_id = p.equipo_local_id
            elif gv > gl: winner_id = p.equipo_visitante_id
            else:
                # Si sigue en empate, no se puede avanzar automáticamente sin definir ganador (penales)
                return False
                
        ganadores.append(winner_id)
        loser_id = p.equipo_visitante_id if winner_id == p.equipo_local_id else p.equipo_local_id
        perdedores.append(loser_id)
        
    if len(ganadores) < 2:
        # Torneo terminado o insuficientes ganadores
        return True
        
    # Aplicar regla de Mejor Perdedor si hay número impar
    if len(ganadores) % 2 != 0 and len(partidos_ronda) > 0:
        # Criterio: El que haya tenido mejor desempeño entre los perdedores de esta ronda
        # Clasificamos a los perdedores por: 1. Goles anotados, 2. Penales anotados
        stats_perdedores = []
        for p in partidos_ronda:
            loser_id = p.equipo_local_id if p.ganador_id == p.equipo_visitante_id else p.equipo_visitante_id
            goles = p.goles_local if loser_id == p.equipo_local_id else p.goles_visitante
            penales = p.penales_local if loser_id == p.equipo_local_id else p.penales_visitante
            stats_perdedores.append({
                'id': loser_id,
                'goles': goles or 0,
                'penales': penales or 0
            })
        
        # Ordenar: primero por goles desc, luego por penales desc
        stats_perdedores.sort(key=lambda x: (x['goles'], x['penales']), reverse=True)
        lucky_loser = stats_perdedores[0]['id']
        ganadores.append(lucky_loser)
        
    # Generar nueva ronda
    partidos_nuevos = []
    n_ganadores = len(ganadores)
    
    # Determinar nombre de fase
    if n_ganadores <= 2: fase_nueva = "Final"
    elif n_ganadores <= 4: fase_nueva = "Semifinal"
    elif n_ganadores <= 8: fase_nueva = "4tos de Final"
    elif n_ganadores <= 16: fase_nueva = "8vos de Final"
    else: fase_nueva = "Siguiente Ronda"
    
    for i in range(0, n_ganadores - 1, 2):
        nuevo_p = Partido(
            torneo_id=torneo_id,
            jornada=jornada_actual + 1,
            equipo_local_id=ganadores[i],
            equipo_visitante_id=ganadores[i+1],
            fase=fase_nueva,
            liga_id=torneo.liga_id
        )
        db.session.add(nuevo_p)
        partidos_nuevos.append(nuevo_p)
        
    db.session.commit()
    return True


@app.route('/api/partido/<int:id>/players', methods=['GET'])
def get_match_players(id):
    partido = Partido.query.get_or_404(id)
    local_players = Jugador.query.filter_by(equipo_id=partido.equipo_local_id).all()
    visitante_players = Jugador.query.filter_by(equipo_id=partido.equipo_visitante_id).all()
    
    # Obtener asistencias actuales para este partido
    asistencias = AsistenciaPartido.query.filter_by(partido_id=id).all()
    asistencia_map = {a.jugador_id: a.presente for a in asistencias}
    
    return jsonify({
        "local": [{
            "id": j.id, 
            "nombre": j.nombre, 
            "numero": j.numero,
            "presente": asistencia_map.get(j.id, False)
        } for j in local_players],
        "visitante": [{
            "id": j.id, 
            "nombre": j.nombre, 
            "numero": j.numero,
            "presente": asistencia_map.get(j.id, False)
        } for j in visitante_players]
    })

# --- Rutas API ---

def sync_torneo_children_liga(torneo_id, new_liga_id):
    """Sincroniza el liga_id de todos los hijos de un torneo cuando cambia su liga."""
    if not new_liga_id: return
    
    # 1. Equipos
    Equipo.query.filter_by(torneo_id=torneo_id).update({Equipo.liga_id: new_liga_id})
    db.session.flush()
    
    # 2. Jugadores (join con Equipos)
    equipos_ids = [e.id for e in Equipo.query.filter_by(torneo_id=torneo_id).all()]
    if equipos_ids:
        Jugador.query.filter(Jugador.equipo_id.in_(equipos_ids)).update({Jugador.liga_id: new_liga_id}, synchronize_session=False)
    
    # 3. Partidos
    Partido.query.filter_by(torneo_id=torneo_id).update({Partido.liga_id: new_liga_id})
    
    # 4. Inscripciones y Pagos
    Inscripcion.query.filter_by(torneo_id=torneo_id).update({Inscripcion.liga_id: new_liga_id})
    Pago.query.filter_by(torneo_id=torneo_id).update({Pago.liga_id: new_liga_id})
    
    # 5. Eventos y Asistencias
    partidos_ids = [p.id for p in Partido.query.filter_by(torneo_id=torneo_id).all()]
    if partidos_ids:
        EventoPartido.query.filter(EventoPartido.partido_id.in_(partidos_ids)).update({EventoPartido.liga_id: new_liga_id}, synchronize_session=False)
        AsistenciaPartido.query.filter(AsistenciaPartido.partido_id.in_(partidos_ids)).update({AsistenciaPartido.liga_id: new_liga_id}, synchronize_session=False)

@app.route('/api/torneos', methods=['GET', 'POST'])
@csrf.exempt
def handle_torneos():
    if request.method == 'POST':
        data = request.json
        print(f"DEBUG POST /api/torneos: {data}")
        
        # Verificar límites del plan
        liga_id = session.get('liga_id')
        user_rol = session.get('user_rol')
        can_create, msg = check_torneos_limit(liga_id, user_rol)
        if not can_create:
            return jsonify({"success": False, "error": msg}), 403
            
        # Determinar el liga_id real basado en la Cancha (sede) elegida
        nuevo_liga_id = session.get('liga_id')
        nombre_cancha = data.get('cancha')
        if nombre_cancha:
            # Búsqueda más robusta: trim y ilike
            cancha_obj = Cancha.query.filter(db.func.trim(Cancha.nombre).ilike(nombre_cancha.strip())).first()
            if cancha_obj and cancha_obj.liga_id:
                nuevo_liga_id = cancha_obj.liga_id
        
        # Si el usuario es admin y no hay liga_id en sesión ni en cancha, nuevo_liga_id podría ser None.
        # En ese caso, dejamos que el modelo maneje el default.

        nuevo = Torneo(
            nombre=data.get('nombre'),
            tipo=data.get('tipo'),
            costo_inscripcion=data.get('costo_inscripcion', 0),
            costo_arbitraje=data.get('costo_arbitraje', 0),
            fecha_inicio=datetime.strptime(data['fecha_inicio'], '%Y-%m-%d') if data.get('fecha_inicio') else datetime.utcnow(),
            activo=data.get('activo', True),
            imagen_url=data.get('imagen_url'),
            reglamento=data.get('reglamento'),
            clausulas=data.get('clausulas'),
            premios=data.get('premios'),
            num_tiempos=data.get('num_tiempos', 2),
            duracion_tiempo=data.get('duracion_tiempo', 20),
            descanso=data.get('descanso', 10),
            jugadores_totales=data.get('jugadores_totales', 15),
            jugadores_campo=data.get('jugadores_campo', 7),
            arbitro_id=data.get('arbitro_id'), # Responsable principal
            dias_juego=data.get('dias_juego'),
            horario_juego=data.get('horario_juego'),
            cancha=data.get('cancha'),
            formato=data.get('formato', 'Liga'),
            liga_id=nuevo_liga_id # Asignar el liga_id de la sede o el de sesión por defecto
        )
        db.session.add(nuevo)
        
        # Hook: Crear cuenta DUENO DE LIGA si se solicita
        crear_cuenta = data.get('crear_cuenta', False)
        rol_solicitado = data.get('rol', 'dueno_liga')
        owner_email = data.get('owner_email') or (Arbitro.query.get(nuevo.arbitro_id).email if nuevo.arbitro_id and Arbitro.query.get(nuevo.arbitro_id) else None)
        
        if crear_cuenta and owner_email:
            existing = Usuario.query.filter_by(email=owner_email).first()
            if not existing:
                hashed_pw = bcrypt.generate_password_hash('fut123').decode('utf-8')
                arb_nombre = Arbitro.query.get(nuevo.arbitro_id).nombre if nuevo.arbitro_id else nuevo.nombre
                new_user = Usuario(
                    nombre=arb_nombre,
                    email=owner_email,
                    password_hash=hashed_pw,
                    rol=rol_solicitado,
                    liga_id=nuevo.liga_id,
                    activo=True
                )
                db.session.add(new_user)
            else:
                existing.rol = rol_solicitado

        # Hook: Crear Cuenta General de Liga
        if data.get('crear_cuenta_general') and data.get('general_email'):
            gen_email = data['general_email']
            gen_password = data.get('general_password') or 'liga123'
            existing_gen = Usuario.query.filter_by(email=gen_email).first()
            if not existing_gen:
                hashed_gen = bcrypt.generate_password_hash(gen_password).decode('utf-8')
                gen_user = Usuario(
                    nombre=f'Acceso Gral. — {nuevo.nombre}',
                    email=gen_email,
                    password_hash=hashed_gen,
                    rol='equipo',
                    liga_id=nuevo.liga_id,
                    activo=True
                )
                db.session.add(gen_user)

        db.session.commit()
        return jsonify(nuevo.to_dict()), 201
    
    from sqlalchemy.orm import joinedload
    query = Torneo.query.options(joinedload(Torneo.liga))
    query = apply_liga_filter(query, Torneo)
    return paginate_query(query)

@app.route('/api/torneos/<int:id>', methods=['GET', 'DELETE', 'PATCH', 'PUT'])
@csrf.exempt
def handle_torneo_single(id):
    torneo = apply_liga_filter(Torneo.query, Torneo).filter_by(id=id).first_or_404()
    if request.method == 'GET':
        return jsonify(torneo.to_dict())
        
    if request.method == 'DELETE':
        try:
            # Reemplazar Hard Delete por Soft Delete (Archivado)
            torneo.archived = True
            torneo.activo = False # Opcional: también lo desactivamos
            db.session.commit()
            print(f"Torneo {id} archivado correctamente.")
            return jsonify({"success": True, "message": "Torneo archivado (espacio liberado)"})
        except Exception as e:
            db.session.rollback()
            print(f"Error archiving torneo {id}: {e}")
            return jsonify({"error": str(e)}), 500
    
    if request.method == 'PUT':
        data = request.json
        print(f"DEBUG PUT /api/torneos/{id}: {data}")
        torneo.nombre = data.get('nombre', torneo.nombre)
        torneo.tipo = data.get('tipo', torneo.tipo)
        torneo.costo_inscripcion = float(data.get('costo_inscripcion', torneo.costo_inscripcion))
        torneo.costo_arbitraje = float(data.get('costo_arbitraje', torneo.costo_arbitraje))
        if data.get('fecha_inicio'):
            torneo.fecha_inicio = datetime.strptime(data.get('fecha_inicio'), '%Y-%m-%d')
        torneo.imagen_url = data.get('imagen_url', torneo.imagen_url)
        torneo.reglamento = data.get('reglamento', torneo.reglamento)
        torneo.clausulas = data.get('clausulas', torneo.clausulas)
        torneo.premios = data.get('premios', torneo.premios)
        if 'num_tiempos' in data and data['num_tiempos']:
            torneo.num_tiempos = int(data['num_tiempos'])
        if 'duracion_tiempo' in data and data['duracion_tiempo']:
            torneo.duracion_tiempo = int(data['duracion_tiempo'])
        if 'descanso' in data and data['descanso']:
            torneo.descanso = int(data['descanso'])
        if 'arbitro_id' in data:
            torneo.arbitro_id = data.get('arbitro_id') or None
        torneo.dias_juego = data.get('dias_juego', torneo.dias_juego)
        torneo.horario_juego = data.get('horario_juego', torneo.horario_juego)
        torneo.cancha = data.get('cancha', torneo.cancha)
        torneo.formato = data.get('formato', torneo.formato)
        if 'activo' in data:
            torneo.activo = data.get('activo')
        
        # Adoptar liga basado en la sede si es necesario
        nombre_cancha = data.get('cancha')
        old_liga_id = torneo.liga_id
        if nombre_cancha:
            # Búsqueda más robusta: trim y ilike
            cancha_obj = Cancha.query.filter(db.func.trim(Cancha.nombre).ilike(nombre_cancha.strip())).first()
            if cancha_obj and cancha_obj.liga_id:
                # Si el usuario es de admin y elige una sede, adoptamos su ligaID
                # O si el torneo no tiene liga asignada aún
                if not torneo.liga_id or session.get('user_rol') == 'admin':
                    torneo.liga_id = cancha_obj.liga_id
        
        # Sincronizar hijos si la liga cambió
        if torneo.liga_id != old_liga_id:
            sync_torneo_children_liga(torneo.id, torneo.liga_id)
        
        # Hook: Crear cuenta DUENO DE LIGA si se solicita
        crear_cuenta = data.get('crear_cuenta', False)
        rol_solicitado = data.get('rol', 'dueno_liga')
        owner_email = data.get('owner_email') or (Arbitro.query.get(torneo.arbitro_id).email if torneo.arbitro_id and Arbitro.query.get(torneo.arbitro_id) else None)

        if crear_cuenta and owner_email:
            existing = Usuario.query.filter_by(email=owner_email).first()
            if not existing:
                hashed_pw = bcrypt.generate_password_hash('fut123').decode('utf-8')
                arb_nombre = Arbitro.query.get(torneo.arbitro_id).nombre if torneo.arbitro_id else torneo.nombre
                new_user = Usuario(
                    nombre=arb_nombre,
                    email=owner_email,
                    password_hash=hashed_pw,
                    rol=rol_solicitado,
                    liga_id=torneo.liga_id,
                    activo=True
                )
                db.session.add(new_user)
            else:
                existing.rol = rol_solicitado

        # Hook: Crear Cuenta General de Liga
        if data.get('crear_cuenta_general') and data.get('general_email'):
            gen_email = data['general_email']
            gen_password = data.get('general_password') or 'liga123'
            existing_gen = Usuario.query.filter_by(email=gen_email).first()
            if not existing_gen:
                hashed_gen = bcrypt.generate_password_hash(gen_password).decode('utf-8')
                gen_user = Usuario(
                    nombre=f'Acceso Gral. — {torneo.nombre}',
                    email=gen_email,
                    password_hash=hashed_gen,
                    rol='equipo',
                    liga_id=torneo.liga_id,
                    activo=True
                )
                db.session.add(gen_user)

        db.session.commit()
        return jsonify(torneo.to_dict())

@app.route('/api/torneos/archived', methods=['GET'])
@csrf.exempt
def get_archived_torneos():
    user_rol = str(session.get('user_rol') or '').lower()
    if user_rol not in ['admin', 'ejecutivo', 'colaborador']:
        return jsonify({"error": "No autorizado"}), 403
        
    # En esta ruta sí queremos ver los archivados
    query = Torneo.query.filter_by(archived=True)
    query = apply_liga_filter(query, Torneo, ignore_archived=True)
    torneos = query.all()
    return jsonify([t.to_dict() for t in torneos])

@app.route('/api/torneos/<int:id>/restore', methods=['POST'])
@csrf.exempt
def restore_torneo(id):
    # Buscar el torneo incluso si está archivado
    torneo = Torneo.query.get_or_404(id)
    
    # Seguridad: verificar que pertenece a la liga del usuario
    l_id = session.get('liga_id')
    user_rol = str(session.get('user_rol') or '').lower()
    if user_rol not in ['admin', 'ejecutivo', 'colaborador'] and torneo.liga_id != l_id:
        return jsonify({"error": "No autorizado"}), 403

    # Verificar si al restaurar no excedemos el límite (porque volverá a ocupar un slot)
    can_restore, msg = check_torneos_limit(torneo.liga_id, user_rol)
    if not can_restore:
        return jsonify({"success": False, "error": f"No se puede restaurar: {msg}"}), 403

    torneo.archived = False
    torneo.activo = True
    db.session.commit()
    return jsonify({"success": True, "message": "Torneo restaurado correctamente", "torneo": torneo.to_dict()})

@app.route('/api/torneos/<int:id>/permanent', methods=['DELETE'])
@csrf.exempt
def permanent_delete_torneo(id):
    torneo = Torneo.query.get_or_404(id)
    
    # Seguridad
    l_id = session.get('liga_id')
    user_rol = str(session.get('user_rol') or '').lower()
    if user_rol not in ['admin', 'ejecutivo', 'colaborador'] and torneo.liga_id != l_id:
        return jsonify({"error": "No autorizado"}), 403

    try:
        # Aquí se podrían agregar limpiezas en cascada si no están en el modelo
        db.session.delete(torneo)
        db.session.commit()
        return jsonify({"success": True, "message": "Torneo eliminado permanentemente"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@app.route('/api/torneos/<int:id>/partidos', methods=['GET'])
def get_torneo_partidos(id):
    partidos = Partido.query.filter_by(torneo_id=id).order_by(Partido.jornada.asc(), Partido.fecha.asc()).all()
    return jsonify([p.to_dict() for p in partidos])

@app.route('/api/torneos/<int:id>/inicializar', methods=['POST'])
@csrf.exempt
def inicializar_torneo_knockout(id):
    torneo = Torneo.query.get_or_404(id)
    if torneo.formato != "Eliminación Directa":
        return jsonify({"success": False, "message": "Solo disponible para Eliminación Directa"}), 400
        
    # Verificar si ya hay partidos
    existentes = Partido.query.filter_by(torneo_id=id).first()
    if existentes:
        return jsonify({"success": False, "message": "El torneo ya tiene partidos generados"}), 400
        
    equipos = Equipo.query.filter_by(torneo_id=id).all()
    if len(equipos) < 2:
        return jsonify({"success": False, "message": "Se necesitan al menos 2 equipos"}), 400
        
    import random
    random.shuffle(equipos)
    
    n = len(equipos)
    # Determinar fase inicial
    if n <= 2: fase = "Final"
    elif n <= 4: fase = "Semifinal"
    elif n <= 8: fase = "4tos de Final"
    elif n <= 16: fase = "8vos de Final"
    else: fase = "1ra Ronda"
    
    # Programación de horarios
    # Intervalo: tiempos * duracion + descanso + 5 buffer
    intervalo = (torneo.num_tiempos * torneo.duracion_tiempo) + torneo.descanso + 5
    current_time = datetime.combine(torneo.fecha_inicio.date(), datetime.strptime(torneo.horario_juego or "08:00", "%H:%M").time())
    
    nuevos_partidos = []
    # Manejar BYEs si es impar
    if n % 2 != 0:
        # El primero descansa o pasa directo
        bye_team = equipos.pop()
        # Podríamos crear un partido "Played" o simplemente dejarlo para la siguiente ronda
        # Por simplicidad, este equipo esperará a la siguiente ronda
        n = len(equipos)

    for i in range(0, n, 2):
        p = Partido(
            torneo_id=id,
            jornada=1,
            equipo_local_id=equipos[i].id,
            equipo_visitante_id=equipos[i+1].id,
            fase=fase,
            fecha=current_time.date(),
            hora=current_time.strftime("%H:%M"),
            cancha=torneo.cancha,
            liga_id=torneo.liga_id
        )
        db.session.add(p)
        nuevos_partidos.append(p)
        current_time += timedelta(minutes=intervalo)
        
    db.session.commit()
    return jsonify({"success": True, "message": f"Sorteo realizado. {len(nuevos_partidos)} partidos generados."})

@app.route('/api/torneos/<int:id>/avanzar_ronda', methods=['POST'])
@csrf.exempt
def force_avanzar_ronda(id):
    success = auto_avanzar_ronda(id)
    if success:
        return jsonify({"success": True, "message": "Siguiente ronda generada correctamente"})
    return jsonify({"success": False, "message": "No se pudo avanzar (partidos pendientes o empate sin definir)"}), 400

@csrf.exempt
def run_inicializar_liguilla(id, top_n=8):
    torneo = Torneo.query.get_or_404(id)
    # data = request.json or {}
    # top_n = int(data.get('top_n', 8))
    
    # 1. Obtener Standings actualizados
    equipos_obj = Equipo.query.filter_by(torneo_id=id).all()
    partidos_obj = Partido.query.filter_by(torneo_id=id, estado='Played').all()
    
    standings = {}
    for eq in equipos_obj:
        standings[eq.id] = {"id": eq.id, "pts": 0, "dg": 0, "gf": 0}
    
    for p in partidos_obj:
        if p.equipo_local_id in standings and p.equipo_visitante_id in standings:
            gl = p.goles_local or 0
            gv = p.goles_visitante or 0
            standings[p.equipo_local_id]["gf"] += gl
            standings[p.equipo_local_id]["dg"] += (gl - gv)
            standings[p.equipo_visitante_id]["gf"] += gv
            standings[p.equipo_visitante_id]["dg"] += (gv - gl)
            if gl > gv: standings[p.equipo_local_id]["pts"] += 3
            elif gv > gl: standings[p.equipo_visitante_id]["pts"] += 3
            else:
                standings[p.equipo_local_id]["pts"] += 1
                standings[p.equipo_visitante_id]["pts"] += 1
    
    sorted_teams = sorted(standings.values(), key=lambda x: (x["pts"], x["dg"], x["gf"]), reverse=True)
    clasificados = [t['id'] for t in sorted_teams[:top_n]]
    
    if len(clasificados) < 2:
        return jsonify({"success": False, "message": "No hay suficientes equipos para una liguilla"}), 400

    # 2. Determinar fase y jornada
    if top_n <= 2: fase = "Final"
    elif top_n <= 4: fase = "Semifinal"
    else: fase = "4tos de Final"
    
    max_jornada = db.session.query(db.func.max(Partido.jornada)).filter_by(torneo_id=id).scalar() or 0
    nueva_jornada = max_jornada + 1

    # 3. Crear emparejamientos (1 vs N, 2 vs N-1...)
    nuevos = []
    for i in range(top_n // 2):
        local_id = clasificados[i]
        visitante_id = clasificados[top_n - 1 - i]
        
        p = Partido(
            torneo_id=id,
            jornada=nueva_jornada,
            equipo_local_id=local_id,
            equipo_visitante_id=visitante_id,
            fase=fase,
            estado='Scheduled',
            liga_id=torneo.liga_id
        )
        db.session.add(p)
        nuevos.append(p)
    
    # 4. Auto-scheduling logic (integrated from auto_schedule_torneo)
    import math
    from datetime import timedelta
    
    # Settings
    day_map = {0:["lunes","lun"], 1:["martes","mar"], 2:["miercoles","mié","mie"], 3:["jueves","jue"], 4:["viernes","vie"], 5:["sabado","sab"], 6:["domingo","dom"]}
    allowed_weekdays = []
    search_text = f"{(torneo.dias_juego or '')} {(torneo.horario_juego or '')}".lower()
    for day_num, patterns in day_map.items():
        if any(p in search_text for p in patterns): allowed_weekdays.append(day_num)
    if not allowed_weekdays: allowed_weekdays = [5, 6]
    allowed_weekdays = sorted(list(set(allowed_weekdays)))

    start_min = 480 # 08:00 default
    match_duration_total = (int(torneo.num_tiempos or 2) * int(torneo.duracion_tiempo or 25)) + int(torneo.descanso or 10)
    
    # Determinar fecha de inicio para la Liguilla (después del último partido jugado)
    last_match = Partido.query.filter_by(torneo_id=id).order_by(Partido.fecha.desc()).first()
    current_date = (last_match.fecha + timedelta(days=1)) if last_match and last_match.fecha else (torneo.fecha_inicio or datetime.now().date())
    
    while current_date.weekday() not in allowed_weekdays:
        current_date += timedelta(days=1)
        
    day_dates = {}
    for w_day in allowed_weekdays:
        days_to_add = (w_day - current_date.weekday() + 7) % 7
        day_dates[w_day] = current_date + timedelta(days=days_to_add)

    day_current_min = {w_day: start_min for w_day in allowed_weekdays}

    for idx, p in enumerate(nuevos):
        w_day = allowed_weekdays[idx % len(allowed_weekdays)]
        p.fecha = day_dates[w_day]
        h = (day_current_min[w_day] // 60) % 24
        m = day_current_min[w_day] % 60
        p.hora = f"{h:02d}:{m:02d}"
        p.cancha = torneo.cancha or "Cancha Principal"
        day_current_min[w_day] += match_duration_total
    
    try:
        db.session.commit()
        return True, f"Liguilla inicializada ({fase}). {len(nuevos)} partidos creados y programados en Jornada {nueva_jornada}."
    except Exception as e:
        db.session.rollback()
        return False, str(e)

@app.route('/api/torneos/<int:id>/inicializar_liguilla', methods=['POST'])
@csrf.exempt
def inicializar_liguilla_api(id):
    data = request.json or {}
    success, message = run_inicializar_liguilla(id, top_n=int(data.get('top_n', 8)))
    if success:
        return jsonify({"success": True, "message": message})
    return jsonify({"success": False, "message": message}), 500

def check_and_start_liguilla_auto(torneo_id):
    torneo = Torneo.query.get(torneo_id)
    if not torneo or torneo.formato not in ["Liga", "Fase de Grupos"]:
        return
    
    # Verificar si faltan partidos por jugar de la fase regular
    # (Excluimos los que ya tienen fase definida como liguilla)
    pendientes = Partido.query.filter(
        Partido.torneo_id == torneo_id, 
        Partido.estado != 'Played',
        or_(Partido.fase == 'Regular', Partido.fase == None, Partido.fase == 'Fase de Grupos')
    ).first()

    if pendientes:
        print(f"DEBUG: Torneo {torneo_id} aún tiene partidos pendientes: {pendientes.id}")
        return 
        
    # Si llegamos aquí, se terminó la fase regular. 
    # Solo si no se ha iniciado ya la liguilla (verificar si hay partidos de fases finales)
    ya_liguilla = Partido.query.filter(
        Partido.torneo_id == torneo_id, 
        Partido.fase.in_(['8vos de Final', '4tos de Final', 'Semifinal', 'Final'])
    ).first()
    
    if ya_liguilla:
        return

    # Determinamos top_n dinámico basado en equipos total
    num_equipos = len(torneo.equipos)
    if num_equipos >= 16: top_n = 16
    elif num_equipos >= 8: top_n = 8
    elif num_equipos >= 4: top_n = 4
    else: top_n = 2

    print(f"DEBUG: Iniciando liguilla automática para torneo {torneo_id} con Top {top_n}")
    run_inicializar_liguilla(torneo_id, top_n=top_n)

@app.route('/api/torneos/<int:id>/standings', methods=['GET'])
def get_torneo_standings(id):
    torneo = Torneo.query.get_or_404(id)
    equipos = Equipo.query.filter_by(torneo_id=id).all()
    partidos = Partido.query.filter_by(torneo_id=id, estado='Played').all()
    
    standings = {}
    for eq in equipos:
        standings[eq.id] = {
            "id": eq.id,
            "nombre": eq.nombre,
            "escudo_url": eq.escudo_url,
            "pj": 0, "g": 0, "e": 0, "p": 0,
            "gf": 0, "gc": 0, "dg": 0, "pts": 0,
            "recent": [] # Last 5 results
        }
    
    # Sort matches by date to get recent form
    partidos.sort(key=lambda x: (x.fecha or datetime.min.date(), x.hora or ""))
    
    for p in partidos:
        if p.equipo_local_id not in standings or p.equipo_visitante_id not in standings:
            continue
            
        loc = standings[p.equipo_local_id]
        vis = standings[p.equipo_visitante_id]
        
        gl = p.goles_local or 0
        gv = p.goles_visitante or 0
        
        loc["pj"] += 1
        vis["pj"] += 1
        loc["gf"] += gl
        loc["gc"] += gv
        vis["gf"] += gv
        vis["gc"] += gl
        
        if gl > gv:
            loc["g"] += 1; loc["pts"] += 3; loc["recent"].append("W")
            vis["p"] += 1; vis["recent"].append("L")
        elif gv > gl:
            vis["g"] += 1; vis["pts"] += 3; vis["recent"].append("W")
            loc["p"] += 1; loc["recent"].append("L")
        else:
            loc["e"] += 1; loc["pts"] += 1; loc["recent"].append("D")
            vis["e"] += 1; vis["pts"] += 1; vis["recent"].append("D")

    for s in standings.values():
        s["dg"] = s["gf"] - s["gc"]
        s["recent"] = s["recent"][-5:]
        
    sorted_standings = sorted(standings.values(), key=lambda x: (x["pts"], x["dg"], x["gf"]), reverse=True)
    return jsonify(sorted_standings)

@app.route('/api/torneos/<int:id>/leaderboard', methods=['GET'])
def get_torneo_leaderboard(id):
    # ... existing implementation ...
    # (keeping the existing one for compatibility, but the code below will be identical)
    return run_leaderboard_query(id)

def run_leaderboard_query(id):
    # Goles
    goles = db.session.query(
        Jugador.nombre, 
        Equipo.nombre.label('equipo_nombre'),
        Equipo.escudo_url,
        db.func.count(EventoPartido.id).label('total')
    ).join(EventoPartido, Jugador.id == EventoPartido.jugador_id)\
     .join(Equipo, Jugador.equipo_id == Equipo.id)\
     .join(Partido, EventoPartido.partido_id == Partido.id)\
     .filter(Partido.torneo_id == id, EventoPartido.tipo == 'Gol')\
     .group_by(Jugador.id, Equipo.id)\
     .order_by(db.text('total DESC'))\
     .limit(10).all()

    # Amarillas
    amarillas = db.session.query(
        Jugador.nombre, 
        Equipo.nombre.label('equipo_nombre'),
        Equipo.escudo_url,
        db.func.count(EventoPartido.id).label('total')
    ).join(EventoPartido, Jugador.id == EventoPartido.jugador_id)\
     .join(Equipo, Jugador.equipo_id == Equipo.id)\
     .join(Partido, EventoPartido.partido_id == Partido.id)\
     .filter(Partido.torneo_id == id, EventoPartido.tipo == 'Amarilla')\
     .group_by(Jugador.id, Equipo.id)\
     .order_by(db.text('total DESC'))\
     .limit(10).all()

    # Rojas
    rojas = db.session.query(
        Jugador.nombre, 
        Equipo.nombre.label('equipo_nombre'),
        Equipo.escudo_url,
        db.func.count(EventoPartido.id).label('total')
    ).join(EventoPartido, Jugador.id == EventoPartido.jugador_id)\
     .join(Equipo, Jugador.equipo_id == Equipo.id)\
     .join(Partido, EventoPartido.partido_id == Partido.id)\
     .filter(Partido.torneo_id == id, EventoPartido.tipo == 'Roja')\
     .group_by(Jugador.id, Equipo.id)\
     .order_by(db.text('total DESC'))\
     .limit(10).all()

    # Porteros
    partidos = Partido.query.filter_by(torneo_id=id, estado='Played').all()
    stats_equipo = {}
    for p in partidos:
        l_id = p.equipo_local_id
        if l_id not in stats_equipo: stats_equipo[l_id] = {'gc': 0, 'cs': 0, 'pj': 0}
        stats_equipo[l_id]['gc'] += (p.goles_visitante or 0)
        stats_equipo[l_id]['pj'] += 1
        if (p.goles_visitante or 0) == 0: stats_equipo[l_id]['cs'] += 1
        v_id = p.equipo_visitante_id
        if v_id not in stats_equipo: stats_equipo[v_id] = {'gc': 0, 'cs': 0, 'pj': 0}
        stats_equipo[v_id]['gc'] += (p.goles_local or 0)
        stats_equipo[v_id]['pj'] += 1
        if (p.goles_local or 0) == 0: stats_equipo[v_id]['cs'] += 1

    porteros_raw = Jugador.query.join(Equipo).filter(Equipo.torneo_id == id, Jugador.es_portero == True).all()
    porteros_vistos_equipo = set()
    porteros_list = []
    for port in porteros_raw:
        if port.equipo_id not in porteros_vistos_equipo and port.equipo_id in stats_equipo:
            st = stats_equipo[port.equipo_id]
            porteros_list.append({"jugador": port.nombre, "equipo": port.equipo.nombre, "escudo": port.equipo.escudo_url, "total": st['gc'], "cs": st['cs'], "pj": st['pj']})
            porteros_vistos_equipo.add(port.equipo_id)
    porteros_list = sorted(porteros_list, key=lambda x: (x["total"], -x["cs"]))[:10]

    return jsonify({
        "goles": [{"jugador": row[0], "equipo": row[1], "escudo": row[2], "total": row[3]} for row in goles],
        "amarillas": [{"jugador": row[0], "equipo": row[1], "escudo": row[2], "total": row[3]} for row in amarillas],
        "rojas": [{"jugador": row[0], "equipo": row[1], "escudo": row[2], "total": row[3]} for row in rojas],
        "porteros": porteros_list
    })

@app.route('/api/torneos/<int:id>/report', methods=['GET'])
def get_torneo_report(id):
    # Combinar Standings, Líderes y Detalles básicos en un solo objeto para el reporte PDF
    torneo = Torneo.query.get_or_404(id)
    
    # Standings
    standings_response = get_torneo_standings(id)
    standings_data = standings_response.get_json()
    
    # Leaderboard
    leaderboard_response = run_leaderboard_query(id)
    leaderboard_data = leaderboard_response.get_json()
    
    # Campeón (buscar el último ganador de la Final si existe)
    final = Partido.query.filter_by(torneo_id=id, fase='Final', estado='Played').first()
    campeon = None
    if final:
        winner = Equipo.query.get(final.ganador_id) if final.ganador_id else None
        if winner:
            campeon = winner.nombre
    
    return jsonify({
        "torneo": torneo.to_dict(),
        "campeon": campeon,
        "standings": standings_data,
        "leaderboard": leaderboard_data
    })

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('users.login_view'))
    return render_template('index.html', 
                          user_name=session.get('user_name'), 
                          user_rol=session.get('user_rol'))

@app.route('/calendario')
def calendario():
    return render_template('calendar.html',
                          user_name=session.get('user_name'),
                          user_rol=session.get('user_rol'))

@app.route('/api/stats')
@csrf.exempt
def get_stats():
    import traceback
    try:
        return _get_stats_impl()
    except Exception as e:
        tb = traceback.format_exc()
        global LAST_STATS_ERROR
        LAST_STATS_ERROR = f"{e}\n{tb}"
        print(f"ERROR /api/stats: {e}\n{tb}")
        return jsonify({"error": str(e), "trace": tb}), 500

@app.route('/debug_stats')
@csrf.exempt
def debug_stats():
    global LAST_STATS_ERROR
    return f"<pre>{LAST_STATS_ERROR}</pre>"

def _get_stats_impl():
    # --- Torneos activos (protegidos en caso de que columnas opcionales no existan) ---
    try:
        query_t = Torneo.query.filter_by(activo=True)
        query_t = apply_liga_filter(query_t, Torneo)
        active_tournaments = query_t.all()
    except Exception as et:
        print(f"WARN get_stats torneos query: {et}")
        # Fallback sin filtro de archived
        try:
            active_tournaments = Torneo.query.filter(Torneo.activo == True).all()
        except Exception as et2:
            print(f"WARN get_stats torneos fallback: {et2}")
            active_tournaments = []
    
    torneos_detalle = []
    from sqlalchemy import func, distinct, case
    
    try:
        # Optimizamos: Obtenemos conteos agrupados en lugar de traer todos los objetos Partido
        # Usamos COALESCE para evitar Nones que rompan la lógica matemática en Python
        stats_query = db.session.query(
            Partido.torneo_id,
            func.count(Partido.id).label('total'),
            func.coalesce(func.sum(case([(Partido.estado == 'Played', 1)], else_=0)), 0).label('jugados'),
            func.count(distinct(Partido.jornada)).label('jornadas')
        ).group_by(Partido.torneo_id).filter(Partido.torneo_id.in_([t.id for t in active_tournaments])).all() if active_tournaments else []
        
        stats_map = {s.torneo_id: s for s in stats_query}
        
        for t in active_tournaments:
            s = stats_map.get(t.id)
            total = getattr(s, 'total', 0) or 0
            jugados = getattr(s, 'jugados', 0) or 0
            jornadas = getattr(s, 'jornadas', 0) or 0
            
            torneos_detalle.append({
                "id": t.id,
                "nombre": t.nombre,
                "tipo": t.tipo,
                "jornadas_totales": jornadas,
                "partidos_jugados": jugados,
                "partidos_pendientes": max(0, total - jugados)
            })
    except Exception as es:
        print(f"ERROR en optimización de stats: {es}")
        # Fallback a lista vacía para no romper toda la respuesta si falla el cálculo agrupado
        torneos_detalle = [{"id": t.id, "nombre": t.nombre, "tipo": t.tipo, "error": True} for t in active_tournaments]

    # Stats generales filtradas
    try:
        query_j = Jugador.query
        query_j = apply_liga_filter(query_j, Jugador)
    except Exception as ej:
        print(f"WARN get_stats jugador filter: {ej}")
        query_j = Jugador.query
    
    try:
        query_e = Equipo.query
        query_e = apply_liga_filter(query_e, Equipo)
    except Exception as ee:
        print(f"WARN get_stats equipo filter: {ee}")
        query_e = Equipo.query

    # Limits and current counts
    user_rol = session.get('user_rol')
    liga_id = session.get('liga_id')
    limits = get_role_limits(user_rol)
    
    # Agregar extras de la liga si existen
    if liga_id:
        liga = Liga.query.get(liga_id)
        if liga:
            if 'canchas' in limits:
                limits['canchas'] += (liga.extra_canchas or 0)
            if 'torneos' in limits:
                limits['torneos'] += (liga.extra_torneos or 0)
            elif 'torneos_per_cancha' in limits:
                # Si es por cancha, el extra se suma al final en el check,
                # pero aquí podemos devolverlo para visualización
                limits['extra_torneos'] = liga.extra_torneos or 0
    
    try:
        current_counts = {
            'canchas': Cancha.query.filter_by(liga_id=liga_id).count() if liga_id else Cancha.query.count(),
            'torneos': Torneo.query.filter_by(liga_id=liga_id, archived=False).count() if liga_id else Torneo.query.filter_by(archived=False).count(),
            'users': Usuario.query.filter_by(liga_id=liga_id).count() if liga_id else Usuario.query.count(),
            'entrenadores': Usuario.query.filter_by(liga_id=liga_id, rol='entrenador').count() if liga_id else Usuario.query.filter_by(rol='entrenador').count()
        }
    except Exception as e:
        print(f'Error calculando current_counts: {e}')
        current_counts = {'canchas': 0, 'torneos': 0, 'users': 0}

    # Geo Stats: Venues and Teams by State and Municipality (NACIONAL - Sin filtros de liga)
    geo_stats = {}
    try:
        # Sedes por estado y municipio (Global)
        venues_query = Cancha.query.all()
        for c in venues_query:
            st = c.estado or "Otro"
            mun = c.municipio or "Otro"
            key = f"{st}|{mun}"
            if key not in geo_stats:
                geo_stats[key] = {"estado": st, "municipio": mun, "sedes": 0, "sedes_lista": [], "equipos": 0, "equipos_lista": []}
            geo_stats[key]["sedes"] += 1
            if c.nombre not in geo_stats[key]["sedes_lista"]:
                geo_stats[key]["sedes_lista"].append(c.nombre)

        # Equipos por estado y municipio (Global)
        teams_query = Equipo.query.all()
        for e in teams_query:
            torneo = Torneo.query.get(e.torneo_id) if e.torneo_id else None
            if torneo and torneo.cancha:
                # Normalizar búsqueda para ignorar espacios al inicio/final
                cancha_nombre = torneo.cancha.strip()
                cancha_ref = Cancha.query.filter(Cancha.nombre.ilike(f"%{cancha_nombre}%")).first()
                
                if cancha_ref:
                    st = cancha_ref.estado or "Otro"
                    mun = cancha_ref.municipio or "Otro"
                    key = f"{st}|{mun}"
                    if key not in geo_stats:
                        geo_stats[key] = {"estado": st, "municipio": mun, "sedes": 0, "sedes_lista": [], "equipos": 0, "equipos_lista": []}
                    
                    # Evitar duplicados
                    team_ids = [item['id'] for item in geo_stats[key]["equipos_lista"]]
                    if e.id not in team_ids:
                        # Calcular desempeño rápido (con protección para que no rompa el mapa)
                        pj = 0
                        eventos = 0
                        wins = 0
                        total_goles = 0
                        try:
                            pj = Partido.query.filter(
                                (Partido.equipo_local_id == e.id) | (Partido.equipo_visitante_id == e.id),
                                Partido.estado == 'Played'
                            ).count()
                            
                            # Sumar goles de los marcadores (Fuente primaria solicitada por Ing)
                            partidos_played = Partido.query.filter(
                                (Partido.equipo_local_id == e.id) | (Partido.equipo_visitante_id == e.id),
                                Partido.estado == 'Played'
                            ).all()
                            
                            goles_sumados = 0
                            wins = 0
                            for p in partidos_played:
                                if p.equipo_local_id == e.id:
                                    goles_sumados += (p.goles_local or 0)
                                    if (p.goles_local or 0) > (p.goles_visitante or 0):
                                        wins += 1
                                elif p.equipo_visitante_id == e.id:
                                    goles_sumados += (p.goles_visitante or 0)
                                    if (p.goles_visitante or 0) > (p.goles_local or 0):
                                        wins += 1
                            
                            # Mantener eventos como referencia si se requiere detalle manual luego
                            eventos = EventoPartido.query.filter_by(equipo_id=e.id, tipo='Goal').count()
                            # Si los goles sumados son 0 pero los eventos > 0 (poco probable con esta fuente), usar eventos.
                            total_goles = max(goles_sumados, eventos)
                        except Exception as te:
                            print(f"Error stats equipo {e.id}: {te}")

                        geo_stats[key]["equipos"] += 1
                        geo_stats[key]["equipos_lista"].append({
                            "id": e.id,
                            "nombre": e.nombre,
                            "escudo_url": e.escudo_url or 'https://cdn-icons-png.flaticon.com/512/53/53283.png',
                            "colonia": e.colonia,
                            "colonia_geojson": e.colonia_geojson,
                            "liga_nombre": e.liga.nombre if e.liga else "Independiente",
                            "color": e.color,
                            "stats": {
                                "goles": total_goles,
                                "pj": pj,
                                "victorias": wins
                            }
                        })
    except Exception as ge:
        print(f"Error calculando geo_stats: {ge}")

    try:
        total_jugadores = query_j.count()
    except Exception as e:
        print(f"WARN total_jugadores: {e}")
        total_jugadores = 0

    try:
        total_equipos = query_e.count()
    except Exception as e:
        print(f"WARN total_equipos: {e}")
        total_equipos = 0

    return jsonify({
        "torneos_activos": len(active_tournaments),
        "total_jugadores": total_jugadores,
        "total_equipos": total_equipos,
        "torneos_detalle": torneos_detalle,
        "limits": limits,
        "current_counts": current_counts,
        "geo_stats": list(geo_stats.values()),
        "user_rol": user_rol
    })

@app.route('/api/ligas/<int:id>/extras', methods=['PUT'])
@csrf.exempt
def update_liga_extras(id):
    if session.get('user_rol') not in ['admin', 'ejecutivo']:
        return jsonify({"error": "No autorizado"}), 403
        
    liga = Liga.query.get_or_404(id)
    data = request.json
    
    if 'extra_canchas' in data:
        new_val = max(0, int(data['extra_canchas']))
        if new_val > (liga.extra_canchas or 0):
            diff = new_val - (liga.extra_canchas or 0)
            exp = LigaExpansion(liga_id=liga.id, tipo='extra_canchas', cantidad=diff, monto_adicional=diff * 290)
            db.session.add(exp)
        liga.extra_canchas = new_val
        
    if 'extra_torneos' in data:
        new_val = max(0, int(data['extra_torneos']))
        if new_val > (liga.extra_torneos or 0):
            diff = new_val - (liga.extra_torneos or 0)
            exp = LigaExpansion(liga_id=liga.id, tipo='extra_torneos', cantidad=diff, monto_adicional=diff * 85)
            db.session.add(exp)
        liga.extra_torneos = new_val
        
    db.session.commit()
    return jsonify({
        "success": True, 
        "liga": liga.to_dict(),
        "monto_total_mensual": liga.monto_total_mensual
    })

@app.route('/api/combo-pagos', methods=['GET', 'POST'])
@csrf.exempt
def handle_combo_pagos():
    user_rol = session.get('user_rol')
    liga_id = session.get('liga_id')
    
    if request.method == 'POST':
        # Permitir a admin/ejecutivo (globales) y a dueños/equipos (para su propia liga)
        data = request.json
        target_liga_id = data.get('liga_id')
        
        if user_rol not in ['admin', 'ejecutivo']:
            if user_rol not in ['dueño_liga', 'super_arbitro', 'equipo'] or str(target_liga_id) != str(liga_id):
                return jsonify({"error": "No autorizado para realizar esta aportación"}), 403
            
        try:

            nuevo_pago = PagoCombo(
                liga_id=data['liga_id'],
                monto=data['monto'],
                metodo=data.get('metodo'),
                comprobante_url=data.get('comprobante_url'),
                notas=data.get('notas'),
                mes_pagado=data.get('mes_pagado'),
                cantidad_meses=int(data.get('cantidad_meses', 1))
            )
            db.session.add(nuevo_pago)
            db.session.commit()
            return jsonify(nuevo_pago.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 400

    # GET: Listar pagos
    query = PagoCombo.query
    if user_rol not in ['admin', 'ejecutivo']:
        query = query.filter_by(liga_id=liga_id)
        
    pagos = [p.to_dict() for p in query.order_by(PagoCombo.fecha.desc()).all()]
    return jsonify(pagos)

@app.route('/api/combo-pagos/<int:pago_id>', methods=['PUT', 'DELETE'])
@csrf.exempt
def handle_combo_pago_single(pago_id):
    if session.get('user_rol') not in ['admin', 'ejecutivo']:
        return jsonify({"error": "No autorizado"}), 403
        
    pago = PagoCombo.query.get_or_404(pago_id)
    
    if request.method == 'DELETE':
        try:
            db.session.delete(pago)
            db.session.commit()
            return jsonify({"success": True, "message": "Aportación eliminada correctamente"})
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 400
            
    if request.method == 'PUT':
        data = request.json
        try:
            pago.monto = data.get('monto', pago.monto)
            pago.metodo = data.get('metodo', pago.metodo)
            pago.mes_pagado = data.get('mes_pagado', pago.mes_pagado)
            pago.notas = data.get('notas', pago.notas)
            pago.comprobante_url = data.get('comprobante_url', pago.comprobante_url)
            pago.cantidad_meses = int(data.get('cantidad_meses', pago.cantidad_meses))
            
            db.session.commit()
            return jsonify(pago.to_dict())
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 400

@app.route('/api/admin/verify-password', methods=['POST'])
@csrf.exempt
def admin_verify_password():
    password = request.json.get('password')
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({"success": False, "error": "No hay sesión activa"}), 401
        
    user = Usuario.query.get(user_id)
    if not user or user.rol != 'admin':
         # También permitir si es la master password
         master_pass = os.getenv('MASTER_PASSWORD')
         if master_pass and password == master_pass:
             return jsonify({"success": True})
         return jsonify({"success": False, "error": "No autorizado"}), 403
         
    # Verificar contra la contraseña del admin actual
    if bcrypt.check_password_hash(user.password_hash, password) or (os.getenv('MASTER_PASSWORD') and password == os.getenv('MASTER_PASSWORD')):
        return jsonify({"success": True})
        
    return jsonify({"success": False, "error": "Contraseña incorrecta"}), 401
    
# Las rutas de entrenamientos han sido movidas a routes/entrenamientos.py

# Las rutas de entrenamientos han sido movidas a routes/entrenamientos.py



# --- Rutas API: Configuración ---

@app.route('/api/config', methods=['GET'])
def get_config():
    clave = request.args.get('clave')
    if clave:
        conf = Configuracion.query.get(clave)
        return jsonify(conf.to_dict() if conf else {"clave": clave, "valor": ""})
    
    configs = Configuracion.query.all()
    return jsonify({c.clave: c.valor for c in configs})

@app.route('/api/config', methods=['POST'])
@csrf.exempt
def update_config():
    if session.get('user_rol') not in ['admin', 'ejecutivo']:
        return jsonify({"error": "No autorizado"}), 403
    
    data = request.json
    clave = data.get('clave')
    valor = data.get('valor')
    
    if not clave:
        return jsonify({"error": "Clave requerida"}), 400
    
    conf = Configuracion.query.get(clave)
    if not conf:
        conf = Configuracion(clave=clave, valor=valor)
        db.session.add(conf)
    else:
        conf.valor = valor
    
    db.session.commit()
    return jsonify({"success": True, "config": conf.to_dict()})

@app.route('/api/corte-diario', methods=['GET'])
def get_corte_diario():
    if session.get('user_rol') not in ['admin', 'ejecutivo', 'dueño_liga', 'super_arbitro']:
        return jsonify({"error": "No autorizado"}), 403
    
    try:
        from datetime import date
        start_date = request.args.get('start_date') or date.today().strftime('%Y-%m-%d')
        end_date = request.args.get('end_date') or start_date
        l_id = get_liga_id()

        # 1. PagoCombo (Suscripciones / Administrativos)
        from models import PagoCombo, Liga
        q_combos_sum = db.session.query(db.func.sum(PagoCombo.monto)).filter(db.func.date(PagoCombo.fecha).between(start_date, end_date))
        if l_id: q_combos_sum = q_combos_sum.filter(PagoCombo.liga_id == l_id)
        pagos_combos_total = q_combos_sum.scalar() or 0
        
        # Detalle administrativo
        q_combos = db.session.query(PagoCombo, Liga.nombre).join(Liga, PagoCombo.liga_id == Liga.id).filter(db.func.date(PagoCombo.fecha).between(start_date, end_date))
        if l_id: q_combos = q_combos.filter(PagoCombo.liga_id == l_id)
        trans_combos = q_combos.all()

        lista_combos = []
        for p, liga_nombre in trans_combos:
            concepto = f"Suscripción: {liga_nombre}"
            # Identificar si es crecimiento de paquete por las notas
            if p.notas and ("crecimiento" in p.notas.lower() or "aumento" in p.notas.lower() or "expansión" in p.notas.lower()):
                concepto = f"🚀 Crecimiento: {liga_nombre} ({p.notas})"
            elif p.notas:
                concepto = f"Admin: {p.notas} ({liga_nombre})"

            lista_combos.append({
                "fecha": p.fecha.strftime('%d/%m/%Y'),
                "concepto": concepto,
                "monto": float(p.monto),
                "metodo": p.metodo or "N/A",
                "tipo": "Administrativo"
            })

        # 2. Operativos (Canchas + Inscripciones/Arbitrajes)
        from routes.pagos_cancha import PagoCancha
        q_canchas_sum = db.session.query(db.func.sum(PagoCancha.monto)).filter(db.func.date(PagoCancha.fecha).between(start_date, end_date))
        if l_id: q_canchas_sum = q_canchas_sum.filter(PagoCancha.liga_id == l_id)
        pagos_cancha_total = q_canchas_sum.scalar() or 0
        
        from models import Pago, Equipo
        q_grales_sum = db.session.query(db.func.sum(Pago.monto)).filter(db.func.date(Pago.fecha).between(start_date, end_date))
        if l_id: q_grales_sum = q_grales_sum.filter(Pago.liga_id == l_id)
        pagos_grales_total = q_grales_sum.scalar() or 0

        # Detalle operativo
        q_canchas = db.session.query(PagoCancha).filter(db.func.date(PagoCancha.fecha).between(start_date, end_date))
        if l_id: q_canchas = q_canchas.filter(PagoCancha.liga_id == l_id)
        trans_canchas = q_canchas.all()

        lista_canchas = [{
            "fecha": p.fecha.strftime('%d/%m/%Y'),
            "concepto": p.cancha.nombre if p.cancha else "Renta Cancha",
            "monto": float(p.monto),
            "metodo": p.metodo or "N/A",
            "tipo": "Operativo (Sede)"
        } for p in trans_canchas]

        q_grales = db.session.query(Pago).filter(db.func.date(Pago.fecha).between(start_date, end_date))
        if l_id: q_grales = q_grales.filter(Pago.liga_id == l_id)
        trans_grales = q_grales.all()

        lista_grales = []
        for p in trans_grales:
            concepto = f"{p.tipo}: General"
            if p.inscripcion and p.inscripcion.equipo:
                concepto = f"{p.tipo}: {p.inscripcion.equipo.nombre}"
            elif p.alumno:
                concepto = f"{p.tipo}: {p.alumno.nombre}"
            
            lista_grales.append({
                "fecha": p.fecha.strftime('%d/%m/%Y'),
                "concepto": concepto,
                "monto": float(p.monto),
                "metodo": p.metodo or "N/A",
                "tipo": "Operativo (Competencia)"
            })

        operativo_total = float(pagos_cancha_total) + float(pagos_grales_total)
        total = float(pagos_combos_total) + operativo_total

        return jsonify({
            "start_date": start_date,
            "end_date": end_date,
            "total_dia": total,
            "total_administrativo": float(pagos_combos_total),
            "total_operativo": operativo_total,
            "transacciones": {
                "administrativas": lista_combos,
                "operativas": lista_canchas + lista_grales
            }
        })
    except Exception as e:
        print(f"Error en corte diario: {e}")
        # En caso de error técnico, devolvemos 0 para no romper el dashboard
        return jsonify({
            "total_dia": 0,
            "error": str(e),
            "detalles": {"pagos_combos": 0, "pagos_cancha": 0, "pagos_grales": 0}
        }), 200

@app.route('/api/admin/payment-alerts', methods=['GET'])
def get_payment_alerts():
    try:
        # 1. Deudas de Operatividad (Inscripciones de equipos en torneos)
        query_insc = Inscripcion.query.filter(Inscripcion.saldo_pendiente > 0)
        query_insc = apply_liga_filter(query_insc, Inscripcion)
        operative_debts = []
        for ins in query_insc.all():
            try:
                # Obtener info de contacto de la liga
                liga_info = ins.liga
                equipo_info = ins.equipo
                
                operative_debts.append({
                    "id": ins.id,
                    "tipo": "Operativa",
                    "entidad": equipo_info.nombre if equipo_info else "Equipo Desconocido",
                    "equipo_id": ins.equipo_id,
                    "liga_id": ins.liga_id,
                    "liga_nombre": liga_info.nombre if liga_info else "—",
                    "liga_email": liga_info.email if liga_info else "",
                    "liga_telefono": liga_info.telefono if liga_info else "",
                    "subdominio": liga_info.subdominio if liga_info else "",
                    "torneo": ins.torneo.nombre if ins.torneo else "Torneo",
                    "saldo_pendiente": float(ins.saldo_pendiente or 0),
                    "monto_total": float(ins.monto_pactado_inscripcion or 0)
                })
            except Exception as e_row:
                print(f"Error procesando fila de deuda operativa: {e_row}")

        # 2. Deudas de Combos/Suscripciones (Nivel Administrativo)
        user_rol = str(session.get('user_rol') or '').lower()
        subscription_debts = []
        upcoming_expirations = []
        
        # Las deudas de suscripción solo son visibles para admin/ejecutivo
        if user_rol in ['admin', 'ejecutivo']:
            from datetime import timedelta
            ligas = Liga.query.filter_by(activa=True).all()
            today = date.today()
            limit_date = today + timedelta(days=10)
            for liga in ligas:
                try:
                    vencimiento_str = liga.vencimiento_actual
                    if vencimiento_str:
                        vencimiento = datetime.strptime(vencimiento_str, '%Y-%m-%d').date()
                        
                        debt_item = {
                            "id": liga.id,
                            "tipo": "Suscripción",
                            "entidad": liga.nombre,
                            "liga_nombre": liga.nombre,
                            "email": liga.email,
                            "telefono": liga.telefono,
                            "subdominio": liga.subdominio,
                            "concepto": f"Combo Mensual",
                            "monto": float(liga.monto_total_mensual or 0),
                            "vencimiento": vencimiento_str
                        }

                        if vencimiento < today:
                            debt_item["saldo_pendiente"] = float(liga.monto_total_mensual or 0)
                            subscription_debts.append(debt_item)
                        elif today <= vencimiento <= limit_date:
                            debt_item["dias_restantes"] = (vencimiento - today).days
                            upcoming_expirations.append(debt_item)
                except Exception as e_row:
                    print(f"Error calculando deuda de liga {liga.id}: {e_row}")

        return jsonify({
            "operative": operative_debts,
            "subscription": subscription_debts,
            "upcoming": upcoming_expirations,
            "total_alerts": len(operative_debts) + len(subscription_debts) + len(upcoming_expirations)
        })
    except Exception as e:
        print(f"Error en /api/admin/payment-alerts: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/equipos/<int:id>/stats-summary', methods=['GET'])
def get_equipo_stats_summary(id):
    try:
        equipo = Equipo.query.get_or_404(id)
        
        # Partidos y Récord
        partidos = Partido.query.filter(
            db.or_(Partido.equipo_local_id == id, Partido.equipo_visitante_id == id),
            Partido.estado == 'Finalizado'
        ).all()
        
        jugados = len(partidos)
        ganados = 0
        perdidos = 0
        empatados = 0
        goles_favor = 0
        goles_contra = 0
        
        for p in partidos:
            if p.ganador_id == id:
                ganados += 1
            elif p.ganador_id is not None:
                perdidos += 1
            else:
                empatados += 1
            
            if p.equipo_local_id == id:
                goles_favor += (p.goles_local or 0)
                goles_contra += (p.goles_visitante or 0)
            else:
                goles_favor += (p.goles_visitante or 0)
                goles_contra += (p.goles_local or 0)

        # Disciplina y Goleador (Desde eventos)
        eventos = EventoPartido.query.filter(EventoPartido.equipo_id == id).all()
        amarillas = len([e for e in eventos if e.tipo == 'Tarjeta Amarilla'])
        rojas = len([e for e in eventos if e.tipo == 'Tarjeta Roja'])
        
        # Goleador estrella
        goles = [e for e in eventos if e.tipo == 'Gol' and e.jugador_id]
        from collections import Counter
        goleador_stats = Counter([g.jugador_id for g in goles]).most_common(1)
        
        estrella_nombre = "Sin anotaciones"
        estrella_goles = 0
        if goleador_stats:
            j_id, count = goleador_stats[0]
            j = Jugador.query.get(j_id)
            if j:
                estrella_nombre = j.nombre
                estrella_goles = count

        # Solo incluir UID si el rol es administrativo
        rol = (session.get('user_rol') or '').lower()
        uid_val = None
        if rol in ['admin', 'ejecutivo', 'dueño_liga']:
            uid_val = equipo.uid or f"EQ-{equipo.id:06d}"

        return jsonify({
            "uid": uid_val,
            "nombre": equipo.nombre,
            "record": {
                "jj": jugados,
                "jg": ganados,
                "jp": perdidos,
                "je": empatados
            },
            "goles": {
                "favor": goles_favor,
                "contra": goles_contra,
                "dif": goles_favor - goles_contra
            },
            "disciplina": {
                "amarillas": amarillas,
                "rojas": rojas
            },
            "estrella": {
                "nombre": estrella_nombre,
                "goles": estrella_goles
            }
        })
    except Exception as e:
        print(f"Error en stats-summary: {e}")
        return jsonify({"error": str(e)}), 500

@app.route('/api/equipos/<int:id>/generate_uid', methods=['POST'])
@csrf.exempt
def generate_equipo_uid(id):
    try:
        # Verificar permisos
        rol = (session.get('user_rol') or '').lower()
        if rol not in ['admin', 'ejecutivo', 'dueño_liga']:
            return jsonify({"error": "No tiene permisos para realizar esta acción"}), 403
            
        equipo = apply_liga_filter(Equipo.query, Equipo).filter_by(id=id).first_or_404()
        
        import random, string
        chars = string.ascii_uppercase + string.digits
        while True:
            new_uid = ''.join(random.choices(chars, k=15))
            # Verificar unicidad
            if not Equipo.query.filter_by(uid=new_uid).first():
                break
        
        equipo.uid = new_uid
        db.session.commit()
        
        return jsonify({"success": True, "uid": new_uid})
    except Exception as e:
        db.session.rollback()
        print(f"Error generando UID: {e}")
        return jsonify({"error": str(e)}), 500

# Utilidad para poblar UIDs faltantes
def ensure_team_uids():
    try:
        import random, string
        equipos_sin_uid = Equipo.query.filter(Equipo.uid == None).all()
        if equipos_sin_uid:
            chars = string.ascii_uppercase + string.digits
            for e in equipos_sin_uid:
                while True:
                    new_uid = ''.join(random.choices(chars, k=15))
                    # Verificar unicidad
                    if not Equipo.query.filter_by(uid=new_uid).first():
                        e.uid = new_uid
                        break
            db.session.commit()
            print(f"Sincronizados {len(equipos_sin_uid)} UIDs de equipos.")
    except Exception as ex:
        print(f"Error poblando UIDs: {ex}")

@app.route('/api/admin/dashboard-stats', methods=['GET'])
def get_dashboard_stats():
    try:
        from datetime import datetime, date, timedelta
        start_date_str = request.args.get('start_date')
        end_date_str = request.args.get('end_date')
        
        if start_date_str and end_date_str:
            start_date = datetime.strptime(start_date_str, '%Y-%m-%d').date()
            end_date = datetime.strptime(end_date_str, '%Y-%m-%d').date()
        else:
            start_date = date.today()
            end_date = start_date

        # 1. Partidos para el rango
        partidos_rango = Partido.query.filter(Partido.fecha.between(start_date, end_date)).count()

        # 2. Jugadores
        jugadores = Jugador.query.count()

        # 3. Entrenamientos activos
        entrenamientos = AlumnoEntrenamiento.query.filter(AlumnoEntrenamiento.activo == True).count()

        # 4. Alertas de pago (Operativas)
        alertas = Inscripcion.query.filter(Inscripcion.saldo_pendiente > 0).count()

        # 5. Métricas estadísticas
        equipos_count = Equipo.query.count()
        torneos_count = Torneo.query.count()
        arbitros_count = Arbitro.query.count()
        
        # 6. Vencimientos de Combos (Próximos 10 días)
        today = date.today()
        limit_date = today + timedelta(days=10)
        vencimientos_count = 0
        try:
            active_ligas = Liga.query.filter_by(activa=True).all()
            for l in active_ligas:
                v_str = l.vencimiento_actual
                if v_str:
                    v_date = datetime.strptime(v_str, '%Y-%m-%d').date()
                    # Si ya venció o vence en los próximos 10 días
                    if v_date <= limit_date:
                        vencimientos_count += 1
        except Exception as e_venc:
            print(f"Error calculando vencimientos dashboard: {e_venc}")

        return jsonify({
            "partidos_hoy": partidos_rango,
            "jugadores": jugadores,
            "entrenamientos_activos": entrenamientos,
            "alertas_pago": alertas,
            "equipos": equipos_count,
            "torneos": torneos_count,
            "arbitros": arbitros_count,
            "vencimientos_combos": vencimientos_count,
            "periodo": {
                "inicio": start_date.strftime('%Y-%m-%d'),
                "fin": end_date.strftime('%Y-%m-%d')
            }
        })
    except Exception as e:
        print(f"Error en dashboard-stats: {e}")
        return jsonify({
            "partidos_hoy": 0,
            "jugadores": 0,
            "entrenamientos_activos": 0,
            "alertas_pago": 0,
            "equipos": 0,
            "torneos": 0,
            "arbitros": 0,
            "ligas": 0,
            "error": str(e)
        }), 200

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        ensure_team_uids()
    app.run(debug=True, port=5003, use_reloader=True)
