from flask import Blueprint, jsonify, request, session
from models import db, Arbitro, Usuario, Cancha, Torneo, Partido, Inscripcion, Pago, EventoPartido, AsistenciaPartido, apply_liga_filter
from datetime import datetime, date
import secrets

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

@arbitros_bp.route('/api/telegram/verify_referee', methods=['POST'])
def telegram_verify_referee():
    data = request.json
    telegram_id = str(data.get('telegram_id'))
    password = data.get('password')
    if not telegram_id or not password:
        return jsonify({"error": "telegram_id and password required"}), 400
    
    # Intentar primero por telegram_id y contraseña exactos
    arbitro = Arbitro.query.filter_by(telegram_id=telegram_id, password=password, activo=True).first()
    
    if not arbitro:
        # Si no coincide la pareja, buscar por contraseña en general para vincular el ID
        arbitro = Arbitro.query.filter_by(password=password, activo=True).first()
        if arbitro:
            # Desvincular el ID de quien lo tuviera antes (para permitir cambios rápidos en pruebas)
            from sqlalchemy import and_
            otros = Arbitro.query.filter(Arbitro.telegram_id == telegram_id, Arbitro.id != arbitro.id).all()
            for o in otros:
                o.telegram_id = None
                
            arbitro.telegram_id = telegram_id
            db.session.commit()
        else:
            return jsonify({"authenticated": False, "error": "Credenciales incorrectas o ID no vinculado."}), 401
        
    return jsonify({
        "authenticated": True,
        "referee": {
            "id": arbitro.id,
            "nombre": arbitro.nombre,
            "nivel": arbitro.nivel
        }
    })

@arbitros_bp.route('/api/telegram/tournaments', methods=['GET'])
def telegram_get_tournaments():
    tournaments = Torneo.query.filter_by(activo=True).all()
    return jsonify([{"id": t.id, "nombre": t.nombre} for t in tournaments])

@arbitros_bp.route('/api/telegram/matches', methods=['GET'])
def telegram_get_matches():
    telegram_id = request.args.get('telegram_id')
    torneo_id = request.args.get('torneo_id', type=int)
    if not telegram_id or not torneo_id:
        return jsonify({"error": "telegram_id and torneo_id required"}), 400
        
    arbitro = Arbitro.query.filter_by(telegram_id=telegram_id).first()
    if not arbitro:
        return jsonify({"error": "Referee not found"}), 404
        
    partidos = Partido.query.filter_by(torneo_id=torneo_id)\
        .order_by(Partido.fecha.asc(), Partido.hora.asc()).all()
    
    return jsonify([p.to_dict() for p in partidos])

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
        nuevo_evento = EventoPartido(
            partido_id=id,
            equipo_id=data.get('equipo_id'),
            jugador_id=data.get('jugador_id'),
            minuto=data.get('minuto'),
            tipo=data.get('tipo'),
            periodo=data.get('periodo', 1),
            nota=data.get('nota'), # Card note
            liga_id=partido.liga_id
        )
        db.session.add(nuevo_evento)
        
        telegram_id = data.get('telegram_id')
        
        if data.get('tipo') == 'Inicio':
            partido.estado = 'Live'
            partido.fecha = datetime.now().date()
            partido.hora = datetime.now().strftime('%H:%M')
            
            if telegram_id:
                arbitro = Arbitro.query.filter_by(telegram_id=str(telegram_id)).first()
                if arbitro:
                    partido.arbitro_id = arbitro.id
        
        elif data.get('tipo') == 'Medio Tiempo':
            partido.estado = 'HalfTime'
        elif data.get('tipo') == 'Reanudación':
            partido.estado = 'Live'
        elif data.get('tipo') == 'Fin':
            partido.estado = 'Played'
            gl = partido.goles_local or 0
            gv = partido.goles_visitante or 0
            if gl > gv: partido.ganador_id = partido.equipo_local_id
            elif gv > gl: partido.ganador_id = partido.equipo_visitante_id
            
            db.session.commit()
            
            # Nota: auto_avanzar_ronda y check_and_start_liguilla_auto 
            # deben estar accesibles, tal vez importándolas o moviéndolas a un helper.
            # Por ahora las llamaremos asumiendo que están disponibles o manejaremos el error.
            try:
                from app import auto_avanzar_ronda, check_and_start_liguilla_auto
                auto_avanzar_ronda(partido.torneo_id)
                check_and_start_liguilla_auto(partido.torneo_id)
            except ImportError:
                pass
            
        if data.get('tipo') == 'Gol':
            if data.get('equipo_id') == partido.equipo_local_id:
                partido.goles_local = (partido.goles_local or 0) + 1
            elif data.get('equipo_id') == partido.equipo_visitante_id:
                partido.goles_visitante = (partido.goles_visitante or 0) + 1
                
        db.session.commit()
        return jsonify({"success": True, "evento": nuevo_evento.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

@arbitros_bp.route('/api/telegram/match/<int:id>/payment', methods=['POST'])
def telegram_match_payment(id):
    data = request.json
    equipo_id = data.get('equipo_id')
    monto = data.get('monto')
    metodo = data.get('metodo', 'Efectivo')
    
    if not equipo_id or not monto:
        return jsonify({"error": "equipo_id and monto required"}), 400
        
    partido = Partido.query.get_or_404(id)
    torneo = Torneo.query.get(partido.torneo_id)
    
    inscripcion = Inscripcion.query.filter_by(torneo_id=partido.torneo_id, equipo_id=equipo_id).first()
    if not inscripcion:
        inscripcion = Inscripcion(
            torneo_id=partido.torneo_id,
            equipo_id=equipo_id,
            monto_pactado_inscripcion=float(torneo.costo_inscripcion or 0)
        )
        db.session.add(inscripcion)
        db.session.flush()

    try:
        nuevo_pago = Pago(
            inscripcion_id=inscripcion.id,
            monto=float(monto),
            tipo='Arbitraje',
            metodo=metodo,
            partido_id=id,
            comentario=f'Cobro de arbitraje vía Telegram App'
        )
        db.session.add(nuevo_pago)
        db.session.commit()
        return jsonify({"success": True, "pago_id": nuevo_pago.id})
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
