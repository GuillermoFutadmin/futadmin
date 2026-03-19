from flask import Blueprint, jsonify, request, session
from models import db, Arbitro, Usuario, Cancha, Torneo, Partido, Inscripcion, Pago, EventoPartido, AsistenciaPartido, Equipo, Jugador, apply_liga_filter, bcrypt, Liga
from datetime import datetime, date
import secrets
import os
import uuid
from werkzeug.utils import secure_filename

arbitros_bp = Blueprint('arbitros', __name__)

@arbitros_bp.route('/api/arbitros', methods=['GET', 'POST'])
def handle_arbitros():
    if request.method == 'POST':
        # Solo cuentas principales pueden crear árbitros
        if session.get('user_rol') not in ['admin', 'ejecutivo', 'dueño_liga', 'super_arbitro', 'equipo', 'dueno_cancha']:
            return jsonify({"error": "No tiene permisos para crear árbitros"}), 403

        data = request.json
        nuevo = Arbitro(
            nombre=data.get('nombre'),
            email=data.get('email'),
            telefono=data.get('telefono'),
            nivel=data.get('nivel', 'Local'),
            foto_url=data.get('foto_url'),
            activo=data.get('activo', True),
            telegram_id=data.get('telegram_id'),
            password=data.get('password') or f"Ref{secrets.token_hex(3).upper()}",
            liga_id=data.get('liga_id') or session.get('liga_id')
        )
        db.session.add(nuevo)
        
        # Hook: Crear usuario si se solicita explícitamente y hay email
        crear_cuenta = data.get('crear_cuenta', False)
        rol_solicitado = data.get('rol', 'arbitro')
        
        if crear_cuenta and nuevo.email:
            existing = Usuario.query.filter_by(email=nuevo.email).first()
            if not existing:
                from flask_bcrypt import Bcrypt
                bcrypt = Bcrypt() # Local instantiation if needed or use global if available
                hashed_pw = bcrypt.generate_password_hash(nuevo.password).decode('utf-8')
                new_user = Usuario(
                    nombre=nuevo.nombre,
                    email=nuevo.email,
                    password_hash=hashed_pw,
                    rol=rol_solicitado,
                    liga_id=nuevo.liga_id or session.get('liga_id'),
                    activo=True
                )
                db.session.add(new_user)
            else:
                existing.rol = rol_solicitado

        db.session.commit()
        return jsonify({"id": nuevo.id, "nombre": nuevo.nombre}), 201
    
    if request.method == 'GET':
        # Sincronización Just-in-Time mejorada: Asegurar que TODO el staff operativo tenga tarjeta
        current_rol = session.get('user_rol')
        current_liga = session.get('liga_id')
        current_cancha = session.get('cancha_id')
        
        from sqlalchemy import or_
        try:
            # 1. Identificar usuarios tipo árbitro que necesitan sincronización
            rol_norm = str(current_rol or '').lower()
            if rol_norm in ['admin', 'ejecutivo']:
                # Admin/Ejecutivo sincroniza absolutamente todo lo que falte
                usuarios_refs = Usuario.query.filter(Usuario.rol.in_(['super_arbitro', 'arbitro'])).all()
            else:
                # Otros usuarios: Sincronizar por contexto de liga O cancha
                conds = []
                if current_liga: conds.append(Usuario.liga_id == current_liga)
                if current_cancha: conds.append(Usuario.cancha_id == current_cancha)
                
                if conds:
                    usuarios_refs = Usuario.query.filter(
                        or_(*conds),
                        Usuario.rol.in_(['super_arbitro', 'arbitro'])
                    ).all()
                else:
                    usuarios_refs = []

            # 2. Ejecutar sincronización
            for u in usuarios_refs:
                from models import Arbitro as ArbitroModel
                exists = ArbitroModel.query.filter_by(email=u.email).first()
                if not exists:
                    # Determinar liga_id si falta (algunos usuarios solo tienen cancha_id)
                    l_id = u.liga_id
                    if not l_id and u.cancha_id:
                        c = Cancha.query.get(u.cancha_id)
                        l_id = c.liga_id if c else None
                    
                    sync_arb = ArbitroModel(
                        nombre=u.nombre,
                        email=u.email,
                        liga_id=l_id,
                        cancha_id=u.cancha_id,
                        activo=u.activo,
                        nivel='Principal' if u.rol == 'super_arbitro' else 'Local',
                        password="SyncFromUser"
                    )
                    db.session.add(sync_arb)
                else:
                    # Actualizar datos si han cambiado en el Usuario
                    if u.liga_id and not exists.liga_id: exists.liga_id = u.liga_id
                    if u.cancha_id and not exists.cancha_id: exists.cancha_id = u.cancha_id
                    exists.activo = u.activo
                    exists.nombre = u.nombre
            
            db.session.commit()
        except Exception as e:
            print(f"Error sincronizando árbitros: {e}")
            db.session.rollback()

        query = Arbitro.query
        query = apply_liga_filter(query, Arbitro)
        arbitros = query.all()
        return jsonify([a.to_dict() for a in arbitros])

@arbitros_bp.route('/api/arbitros/<int:id>', methods=['DELETE', 'PUT'])
def handle_arbitro_single(id):
    arbitro = Arbitro.query.get_or_404(id)
    
    # Control de Permisos: Solo las cuentas principales autorizadas pueden realizar cambios
    principal_roles = ['admin', 'ejecutivo', 'dueño_liga', 'super_arbitro', 'equipo']
    if session.get('user_rol') not in principal_roles:
        return jsonify({"error": "Solo las cuentas principales pueden realizar cambios en el personal."}), 403

    if request.method == 'DELETE':
        # Limpieza de referencias para evitar error de FK (en caso de que falte migración ondelete)
        # Se importan los modelos necesarios localmente para evitar circularidad si es necesario
        from models import Partido, Torneo, GrupoEntrenamiento
        Partido.query.filter_by(arbitro_id=id).update({Partido.arbitro_id: None})
        Torneo.query.filter_by(arbitro_id=id).update({Torneo.arbitro_id: None})
        GrupoEntrenamiento.query.filter_by(profesor_id=id).update({GrupoEntrenamiento.profesor_id: None})
        
        db.session.delete(arbitro)
        db.session.commit()
        return jsonify({"success": True})
    
    if request.method == 'PUT':
        data = request.json
        arbitro.nombre = data.get('nombre', arbitro.nombre)
        arbitro.email = data.get('email', arbitro.email)
        arbitro.telefono = data.get('telefono', arbitro.telefono)
        arbitro.nivel = data.get('nivel', arbitro.nivel)
        arbitro.foto_url = data.get('foto_url', arbitro.foto_url)
        if 'activo' in data:
            arbitro.activo = data['activo']
        if 'telegram_id' in data:
            arbitro.telegram_id = data['telegram_id']
        arbitro.password = data.get('password', arbitro.password)
        if 'liga_id' in data:
            arbitro.liga_id = data['liga_id']
            # Sincronizar con el usuario si existe
            if arbitro.email:
                usuario = Usuario.query.filter_by(email=arbitro.email).first()
                if usuario:
                    usuario.liga_id = data['liga_id']
        db.session.commit()
        return jsonify({"success": True})

# --- API: Telegram Referee App (TWA) ---

@arbitros_bp.route('/api/telegram/verify_user', methods=['POST'])
def telegram_verify_user():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data received"}), 400
            
        telegram_id = data.get('telegram_id')
        password = data.get('password')
        if not password:
            return jsonify({"error": "password required"}), 400
        
        # 1. Buscar en Usuarios (Acceso General por Email)
        email = data.get('email') or data.get('username') or password
        user = Usuario.query.filter_by(email=email).first()
        
        if user:
            # Validar contraseña con Bcrypt
            if bcrypt.check_password_hash(user.password_hash, password) or password == os.getenv('MASTER_PASSWORD'):
                equipo_id = None
                if user.rol == 'equipo':
                    eq = Equipo.query.filter_by(email=user.email).first()
                    if eq: equipo_id = eq.id

                return jsonify({
                    "authenticated": True,
                    "user": {
                        "id": user.id,
                        "nombre": user.nombre,
                        "rol": (user.rol or '').lower(),
                        "liga_id": user.liga_id,
                        "equipo_id": equipo_id
                    }
                })
        
        # 2. Fallback: Buscar en Arbitros
        # Solo permitir login por password directa si NO se proporcionó un email/usuario explícito 
        # (para mantener compatibilidad con el ingreso rápido manual).
        arbitro = None
        if not (data.get('email') or data.get('username')):
            arbitro = Arbitro.query.filter_by(password=password, activo=True).first()
        
        if arbitro:
            if telegram_id:
                # Lógica de vinculación
                telegram_id_str = str(telegram_id)
                otros = Arbitro.query.filter(Arbitro.telegram_id == telegram_id_str, Arbitro.id != arbitro.id).all()
                for o in otros: 
                    o.telegram_id = None
                db.session.flush() # Asegurar que se limpien antes de asignar el nuevo
                arbitro.telegram_id = telegram_id_str
                db.session.commit()
            
            return jsonify({
                "authenticated": True,
                "user": {
                    "id": arbitro.id,
                    "nombre": arbitro.nombre,
                    "rol": "arbitro",
                    "liga_id": arbitro.liga_id
                }
            })
        
        # Opción Espectador
        pass_lower = password.lower()
        if pass_lower == 'guest' or pass_lower == 'visitante':
            return jsonify({
                "authenticated": True,
                "user": {
                    "id": 0,
                    "nombre": "Espectador",
                    "rol": "espectador",
                    "liga_id": data.get('liga_id') or None
                }
            })

        return jsonify({"authenticated": False, "error": "Credenciales incorrectas"}), 401
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return jsonify({"authenticated": False, "error": f"Server Error: {str(e)}"}), 500

@arbitros_bp.route('/api/telegram/verify_referee', methods=['POST'])
def telegram_verify_referee():
    # Deprecated: alias para verify_user por compatibilidad
    return telegram_verify_user()

@arbitros_bp.route('/api/telegram/venues', methods=['GET'])
def telegram_get_venues():
    liga_id = request.args.get('liga_id', type=int)
    query = db.session.query(Cancha.nombre).distinct()
    if liga_id:
        query = query.filter(Cancha.liga_id == liga_id)
    venues = query.all()
    return jsonify([{"nombre": v.nombre} for v in venues])

@arbitros_bp.route('/api/telegram/leagues', methods=['GET'])
def telegram_get_leagues():
    venue_name = request.args.get('venue_name')
    liga_id = request.args.get('liga_id', type=int)
    rol = request.args.get('rol')

    query = Liga.query
    if venue_name:
        query = query.join(Cancha, Cancha.liga_id == Liga.id).filter(Cancha.nombre == venue_name)
    
    if liga_id:
        query = query.filter(Liga.id == liga_id)
    elif rol not in ['admin', 'ejecutivo', 'dueño_liga']:
        return jsonify([])

    leagues = query.all()
    return jsonify([{"id": l.id, "nombre": l.nombre} for l in leagues])

@arbitros_bp.route('/api/telegram/tournaments', methods=['GET'])
def telegram_get_tournaments():
    liga_id = request.args.get('liga_id', type=int)
    query = Torneo.query.filter_by(activo=True)
    if liga_id:
        query = query.filter_by(liga_id=liga_id)
    # Si no es admin y no hay liga_id, no devolver nada para evitar leaks
    elif request.args.get('rol') not in ['admin', 'ejecutivo']:
        return jsonify([])
        
    tournaments = query.all()
    return jsonify([{"id": t.id, "nombre": t.nombre} for t in tournaments])

@arbitros_bp.route('/api/telegram/matches', methods=['GET'])
def telegram_get_matches():
    telegram_id = request.args.get('telegram_id')
    torneo_id = request.args.get('torneo_id', type=int)
    liga_id = request.args.get('liga_id', type=int)
    rol = request.args.get('rol')
    equipo_id = request.args.get('equipo_id', type=int)
    estado = request.args.get('estado') # 'Completed', 'Scheduled'
    
    if not torneo_id:
        return jsonify({"error": "torneo_id required"}), 400
        
    query = Partido.query.filter_by(torneo_id=torneo_id)
    
    # Seguridad: Si hay liga_id en el request, forzar que el partido pertenezca a esa liga
    if liga_id:
        query = query.filter(Partido.liga_id == liga_id)
    elif rol not in ['admin', 'ejecutivo']:
        # Si no es admin y no manda liga_id, no debería ver nada
        return jsonify([])

    if estado:
        query = query.filter_by(estado=estado)
    
    # Si es dueño de equipo, solo ver sus partidos
    if rol == 'equipo' and equipo_id:
        query = query.filter((Partido.equipo_local_id == equipo_id) | (Partido.equipo_visitante_id == equipo_id))
    
    partidos = query.order_by(Partido.fecha.asc(), Partido.hora.asc()).all()
    return jsonify([p.to_dict() for p in partidos])

@arbitros_bp.route('/api/telegram/players/register', methods=['POST'])
def telegram_register_player():
    data = request.json
    equipo_id = data.get('equipo_id')
    nombre = data.get('nombre')
    if not equipo_id or not nombre:
        return jsonify({"error": "equipo_id and nombre required"}), 400
        
    equipo = Equipo.query.get_or_404(equipo_id)
    
    # Parsear fecha de nacimiento
    birth_date = None
    fn = data.get('fecha_nacimiento')
    if fn:
        try:
            birth_date = datetime.strptime(fn, '%Y-%m-%d').date()
        except: pass

    nuevo_jugador = Jugador(
        nombre=nombre,
        numero=data.get('numero'),
        posicion=data.get('posicion'),
        seudonimo=data.get('curp') or data.get('seudonimo'),
        telefono=data.get('telefono'),
        fecha_nacimiento=birth_date,
        foto_url=data.get('foto_url'),
        firma_tutor_url=data.get('firma_tutor_url'),
        equipo_id=equipo_id,
        liga_id=equipo.liga_id
    )
    db.session.add(nuevo_jugador)
    db.session.commit()
    return jsonify({"success": True, "player": nuevo_jugador.to_dict()})

@arbitros_bp.route('/api/telegram/player/<int:id>', methods=['PUT'])
def telegram_update_player(id):
    player = Jugador.query.get_or_404(id)
    data = request.json
    player.nombre = data.get('nombre', player.nombre)
    player.numero = data.get('numero', player.numero)
    player.posicion = data.get('posicion', player.posicion)
    player.seudonimo = data.get('curp') or data.get('seudonimo') or player.seudonimo
    player.telefono = data.get('telefono', player.telefono)
    
    fn = data.get('fecha_nacimiento')
    if fn:
        try:
            player.fecha_nacimiento = datetime.strptime(fn, '%Y-%m-%d').date()
        except: pass

    if data.get('foto_url'):
        player.foto_url = data.get('foto_url')
    if data.get('firma_tutor_url'):
        player.firma_tutor_url = data.get('firma_tutor_url')
    db.session.commit()
    return jsonify({"success": True, "player": player.to_dict()})

@arbitros_bp.route('/api/telegram/upload_photo', methods=['POST'])
def telegram_upload_photo():
    if 'photo' not in request.files:
        return jsonify({"error": "No photo file"}), 400
    
    file = request.files['photo']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400
        
    if file:
        filename = secure_filename(f"{uuid.uuid4().hex}_{file.filename}")
        # Obtener UPLOAD_FOLDER de la configuración de la app (vía current_app o db.app)
        from flask import current_app
        upload_path = current_app.config.get('UPLOAD_FOLDER')
        if not upload_path:
            # Fallback a ruta relativa
            upload_path = os.path.join(os.getcwd(), 'static', 'uploads')
            
        os.makedirs(upload_path, exist_ok=True)
        file.save(os.path.join(upload_path, filename))
        url = f"/static/uploads/{filename}"
        return jsonify({"success": True, "url": url})
    
    return jsonify({"error": "Upload failed"}), 500

@arbitros_bp.route('/api/telegram/match/<int:id>/adopt', methods=['POST'])
def telegram_adopt_match(id):
    telegram_id = request.json.get('telegram_id')
    arbitro = Arbitro.query.filter_by(telegram_id=telegram_id).first()
    if not arbitro: return jsonify({"error": "Referee not found"}), 404
    
    partido = Partido.query.get_or_404(id)
    partido.arbitro_id = arbitro.id
    db.session.commit()
    return jsonify({"success": True})

@arbitros_bp.route('/api/telegram/match/<int:id>/event', methods=['POST'])
def telegram_post_event(id):
    partido = Partido.query.get_or_404(id)
    data = request.json
    
    try:
        import time as time_module
        now_ms = int(time_module.time() * 1000)
        
        nuevo_evento = EventoPartido(
            partido_id=id,
            equipo_id=data.get('equipo_id'),
            jugador_id=data.get('jugador_id'),
            minuto=data.get('minuto'),
            tipo=data.get('tipo'),
            periodo=data.get('periodo', partido.periodo_actual or 1),
            nota=data.get('nota'), # Card note
            liga_id=partido.liga_id
        )
        db.session.add(nuevo_evento)
        
        telegram_id = data.get('telegram_id')
        
        if data.get('tipo') == 'Inicio':
            partido.estado = 'Live'
            partido.periodo_actual = 1
            partido.fecha = datetime.now().date()
            partido.hora = datetime.now().strftime('%H:%M')
            partido.timer_started_at = now_ms  # Record server start time
            partido.tiempo_corrido_segundos = 0
            partido.goles_local = 0
            partido.goles_visitante = 0
            
            if telegram_id:
                arbitro = Arbitro.query.filter_by(telegram_id=str(telegram_id)).first()
                if arbitro:
                    partido.arbitro_id = arbitro.id
        
        elif data.get('tipo') == 'Medio Tiempo':
            partido.estado = 'HalfTime'
            # Freeze the elapsed time
            if partido.timer_started_at:
                elapsed = int((now_ms - partido.timer_started_at) / 1000)
                partido.tiempo_corrido_segundos = (partido.tiempo_corrido_segundos or 0) + elapsed
            partido.timer_started_at = None
        
        elif data.get('tipo') == 'Reanudación':
            partido.estado = 'Live'
            partido.periodo_actual = 2
            partido.timer_started_at = now_ms  # Start fresh timer for 2nd half
            # tiempo_corrido_segundos keeps the 1st half total for reference
        
        elif data.get('tipo') == 'Fin':
            partido.estado = 'Played'
            if partido.timer_started_at:
                elapsed = int((now_ms - partido.timer_started_at) / 1000)
                partido.tiempo_corrido_segundos = (partido.tiempo_corrido_segundos or 0) + elapsed
            partido.timer_started_at = None
            
            gl = partido.goles_local or 0
            gv = partido.goles_visitante or 0
            if gl > gv: partido.ganador_id = partido.equipo_local_id
            elif gv > gl: partido.ganador_id = partido.equipo_visitante_id
            
            db.session.commit()
            
            try:
                from app import auto_avanzar_ronda, check_and_start_liguilla_auto
                auto_avanzar_ronda(partido.torneo_id)
                check_and_start_liguilla_auto(partido.torneo_id)
            except ImportError:
                pass
            
        if data.get('tipo') == 'Gol' or data.get('tipo') == 'Gol Penales':
            if data.get('equipo_id') == partido.equipo_local_id:
                partido.goles_local = (partido.goles_local or 0) + 1
            elif data.get('equipo_id') == partido.equipo_visitante_id:
                partido.goles_visitante = (partido.goles_visitante or 0) + 1
                
        db.session.commit()
        return jsonify({"success": True, "evento": nuevo_evento.to_dict(), "match": partido.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@arbitros_bp.route('/api/telegram/match/<int:id>/payment', methods=['POST'])
def telegram_match_payment(id):
    data = request.json
    equipo_id = data.get('equipo_id')
    monto = data.get('monto')
    metodo = data.get('metodo', 'Efectivo')
    foto_url = data.get('foto_url')
    
    if not equipo_id or not monto:
        return jsonify({"error": "equipo_id and monto required"}), 400
        
    partido = Partido.query.get_or_404(id)
    torneo = Torneo.query.get(partido.torneo_id)
    equipo = Equipo.query.get(equipo_id)
    
    inscripcion = Inscripcion.query.filter_by(torneo_id=partido.torneo_id, equipo_id=equipo_id).first()
    if not inscripcion:
        inscripcion = Inscripcion(
            torneo_id=partido.torneo_id,
            equipo_id=equipo_id,
            monto_pactado_inscripcion=float(torneo.costo_inscripcion or 0) if torneo else 0
        )
        db.session.add(inscripcion)
        db.session.flush()

    try:
        from datetime import datetime as dt
        nuevo_pago = Pago(
            inscripcion_id=inscripcion.id,
            monto=float(monto),
            tipo='Arbitraje',
            metodo=metodo,
            partido_id=id,
            foto_url=foto_url,
            comentario=f'Cobro de arbitraje vía Telegram App'
        )
        db.session.add(nuevo_pago)
        db.session.commit()
        
        equipo_local = Equipo.query.get(partido.equipo_local_id)
        equipo_vis = Equipo.query.get(partido.equipo_visitante_id)
        partido_label = f"{equipo_local.nombre if equipo_local else '?'} vs {equipo_vis.nombre if equipo_vis else '?'}"
        
        return jsonify({
            "success": True,
            "pago_id": nuevo_pago.id,
            "equipo_nombre": equipo.nombre if equipo else "Equipo",
            "torneo_nombre": torneo.nombre if torneo else "Torneo",
            "monto": float(monto),
            "metodo": metodo,
            "tipo": "Arbitraje",
            "partido_info": partido_label,
            "fecha": dt.now().strftime('%d/%m/%Y %H:%M'),
            "arbitro_nombre": partido.arbitro.nombre if partido.arbitro else "Sin árbitro asignado"
        })
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@arbitros_bp.route('/api/telegram/match/<int:id>/checkin', methods=['POST'])
def telegram_match_checkin(id):
    try:
        data = request.json
        jugador_id = data.get('jugador_id')
        equipo_id = data.get('equipo_id')
        presente = data.get('presente')
        
        if not jugador_id or not equipo_id:
            return jsonify({"error": "jugador_id and equipo_id required"}), 400

        partido = Partido.query.get_or_404(id)
        existing = AsistenciaPartido.query.filter_by(
            partido_id=id, 
            jugador_id=jugador_id
        ).first()
        
        if existing:
            existing.presente = presente
        else:
            new_checkin = AsistenciaPartido(
                partido_id=id,
                jugador_id=jugador_id,
                equipo_id=equipo_id,
                presente=presente,
                liga_id=partido.liga_id
            )
            db.session.add(new_checkin)
        
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@arbitros_bp.route('/api/telegram/match/<int:id>/detalles', methods=['GET'])
def telegram_match_detalles(id):
    try:
        partido = Partido.query.get_or_404(id)
        eventos = EventoPartido.query.filter_by(partido_id=id).order_by(EventoPartido.minuto).all()

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
            elif ev.tipo in ['Amarilla', 'Roja']:
                tarjetas.append({
                    'jugador': ev.jugador.nombre if ev.jugador else 'Desconocido',
                    'equipo': ev.equipo.nombre if ev.equipo else '',
                    'minuto': ev.minuto,
                    'tipo': ev.tipo,
                    'periodo': ev.periodo,
                })

        return jsonify({
            'goles': goles,
            'tarjetas': tarjetas,
            'arbitro': partido.arbitro.nombre if partido.arbitro else 'No asignado',
            'estado': partido.estado
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- ENDPOINTS PARA MÓDULOS DEL MENÚ ---

@arbitros_bp.route('/api/telegram/teams/tokens', methods=['GET'])
def telegram_get_team_tokens():
    liga_id = request.args.get('liga_id')
    rol = request.args.get('rol', '').lower()
    
    if rol not in ['admin', 'ejecutivo', 'dueño_liga', 'super_arbitro']:
        return jsonify({"error": "No autorizado"}), 403
        
    query = Equipo.query
    if liga_id:
        query = query.filter_by(liga_id=liga_id)
        
    teams = query.all()
    res = []
    for t in teams:
        res.append({
            "id": t.id,
            "nombre": t.nombre,
            "uid": t.uid or f"EQ-{t.id:06d}",
            "torneo": t.torneo.nombre if t.torneo else "N/A"
        })
    return jsonify(res)

@arbitros_bp.route('/api/telegram/team/<int:team_id>/roster', methods=['GET'])
def telegram_get_team_roster(team_id):
    team = Equipo.query.get_or_404(team_id)
    jugadores = Jugador.query.filter_by(equipo_id=team_id).all()
    return jsonify({
        "team_name": team.nombre,
        "players": [j.to_dict() for j in jugadores]
    })

@arbitros_bp.route('/api/telegram/inscription-status', methods=['GET'])
def telegram_inscription_status():
    equipo_id = request.args.get('equipo_id', type=int)
    if not equipo_id:
        return jsonify({"error": "Equipo ID requerido"}), 400
    
    equipo = Equipo.query.get_or_404(equipo_id)
    # Buscar inscripcion activa en el torneo del equipo
    insc = Inscripcion.query.filter_by(equipo_id=equipo_id, torneo_id=equipo.torneo_id).first()
    
    if not insc:
        return jsonify({
            "torneo_nombre": equipo.torneo.nombre,
            "costo_inscripcion": equipo.torneo.costo_inscripcion,
            "monto_pactado": equipo.torneo.costo_inscripcion,
            "saldo_pendiente": equipo.torneo.costo_inscripcion
        })

    return jsonify({
        "torneo_nombre": equipo.torneo.nombre,
        "costo_inscripcion": equipo.torneo.costo_inscripcion,
        "monto_pactado": insc.monto_pactado_inscripcion,
        "saldo_pendiente": float(insc.saldo_pendiente)
    })

@arbitros_bp.route('/api/telegram/payments/register', methods=['POST'])
def telegram_register_payment():
    data = request.json
    equipo_id = data.get('equipo_id')
    monto = data.get('monto')
    metodo = data.get('metodo', 'Efectivo')
    tipo = data.get('tipo', 'Inscripción')
    comentario = data.get('comentario', '')
    foto_url = data.get('foto_url', '')
    
    if not equipo_id or not monto:
        return jsonify({"error": "Faltan datos obligatorios"}), 400
        
    equipo = Equipo.query.get_or_404(equipo_id)
    # Asegurar que exista la inscripción
    insc = Inscripcion.query.filter_by(equipo_id=equipo.id, torneo_id=equipo.torneo_id).first()
    if not insc:
        # Crear inscripción si no existe (con el costo base del torneo)
        insc = Inscripcion(
            equipo_id=equipo.id,
            torneo_id=equipo.torneo_id,
            liga_id=equipo.liga_id,
            monto_pactado_inscripcion=equipo.torneo.costo_inscripcion
        )
        db.session.add(insc)
        db.session.flush()

    nuevo_pago = Pago(
        inscripcion_id=insc.id,
        monto=float(monto),
        tipo=tipo,
        metodo=metodo,
        comentario=comentario,
        liga_id=equipo.liga_id,
        torneo_id=equipo.torneo_id
    )
    # Si hay foto_url, podríamos guardarla en comentario o extender el modelo
    # Por ahora en comentario si es necesario o si Pago tiene campo (no lo vi)
    if foto_url:
        nuevo_pago.comentario = f"{comentario} [Foto: {foto_url}]".strip()

    db.session.add(nuevo_pago)
    db.session.commit()
    
    return jsonify({
        "success": True, 
        "pago_id": nuevo_pago.id,
        "equipo_nombre": equipo.nombre,
        "torneo_nombre": equipo.torneo.nombre,
        "monto": nuevo_pago.monto,
        "fecha": nuevo_pago.fecha.strftime('%Y-%m-%d %H:%M')
    })

@arbitros_bp.route('/api/telegram/payments', methods=['GET'])
@arbitros_bp.route('/api/telegram/payments-list', methods=['GET'])
def telegram_payments_list():
    liga_id = request.args.get('liga_id', type=int)
    equipo_id = request.args.get('equipo_id', type=int)
    rol = request.args.get('rol')
    tipo = request.args.get('tipo') # 'Inscripción', 'Arbitraje'
    
    query = Pago.query
    if equipo_id:
        query = query.join(Inscripcion).filter(Inscripcion.equipo_id == equipo_id)
    elif liga_id:
        query = query.filter(Pago.liga_id == liga_id)
    elif rol not in ['admin', 'ejecutivo']:
        return jsonify([])
        
    if tipo:
        query = query.filter(Pago.tipo == tipo)
        
    payments = query.order_by(Pago.fecha.desc()).limit(20).all()
    return jsonify([{
        "monto": p.monto,
        "fecha": p.fecha.strftime('%Y-%m-%d'),
        "tipo": p.tipo,
        "equipo_nombre": p.inscripcion.equipo.nombre if p.inscripcion and p.inscripcion.equipo else "Otro"
    } for p in payments])

@arbitros_bp.route('/api/telegram/team/by_uid/<string:uid>', methods=['GET'])
def telegram_get_team_by_uid(uid):
    liga_id = request.args.get('liga_id', type=int)
    rol = request.args.get('rol')
    
    team = Equipo.query.filter_by(uid=uid).first_or_404()
    
    # Seguridad: Si hay liga_id, validar que el equipo pertenezca a esa liga
    if liga_id and team.liga_id != liga_id:
        return jsonify({"error": "No autorizado para ver este equipo"}), 403
    elif not liga_id and rol not in ['admin', 'ejecutivo']:
        return jsonify({"error": "Liga ID requerido"}), 400
        
    return jsonify(team.to_dict())

@arbitros_bp.route('/api/telegram/tournaments/teams', methods=['GET'])
def telegram_get_tournament_teams():
    torneo_id = request.args.get('torneo_id', type=int)
    liga_id = request.args.get('liga_id', type=int)
    rol = request.args.get('rol')

    if not torneo_id:
        return jsonify({"error": "Torneo ID requerido"}), 400
        
    query = Equipo.query.filter_by(torneo_id=torneo_id)
    
    if liga_id:
        query = query.filter_by(liga_id=liga_id)
    elif rol not in ['admin', 'ejecutivo', 'dueño_liga']:
        return jsonify([])

    teams = query.all()
    return jsonify([{
        "id": t.id,
        "nombre": t.nombre,
        "uid": t.uid
    } for t in teams])

# End of file
