from flask import Blueprint, request, jsonify, session
from models import db, Cancha, apply_liga_filter, Usuario, Arbitro, bcrypt, check_canchas_limit, check_users_limit

canchas_bp = Blueprint('canchas', __name__)

@canchas_bp.route('/api/canchas', methods=['GET'])
def get_canchas():
    from utils import paginate_query
    query = Cancha.query
    query = apply_liga_filter(query, Cancha)
    
    # Filtro por usuario dueño
    if session.get('user_rol') == 'dueno_cancha':
        user_id = session.get('user_id')
        if user_id:
            query = query.filter_by(dueno_id=user_id)
            
    # Soporte para paginación
    return paginate_query(query)

@canchas_bp.route('/api/canchas', methods=['POST'])
def add_cancha():
    data = request.get_json()
    if not data or not data.get('nombre'):
        return jsonify({"error": "Nombre es requerido"}), 400
        
    # Verificar límites del plan
    liga_id = session.get('liga_id')
    user_rol = session.get('user_rol')
    
    can_create, msg = check_canchas_limit(liga_id, user_rol)
    if not can_create:
        return jsonify({"error": msg}), 403
    
    new_cancha = Cancha(
        nombre=data['nombre'],
        encargado=data.get('encargado'),
        email_encargado=data.get('email_encargado'),
        telefono_encargado=data.get('telefono_encargado'),
        tipo=data.get('tipo', 'Gratuita'),
        costo_renta=float(data.get('costo_renta', 0)),
        unidad_cobro=data.get('unidad_cobro', 'Partido'),
        direccion=data.get('direccion'),
        estado=data.get('estado'),
        municipio=data.get('municipio'),
        notas=data.get('notas'),
        foto_url=data.get('foto_url'),
        modalidad=data.get('modalidad', 'Fútbol 7'),
        liga_id=data.get('liga_id') or session.get('liga_id')
    )
    db.session.add(new_cancha)
    db.session.flush() # Para obtener el ID de la nueva cancha
    
    # Hook: Crear o enlazar cuenta de DUEÑO DE CANCHA
    owner_email = data.get('owner_email_custom') or data.get('email_encargado')
    owner_pass = data.get('owner_pass_custom') or 'fut123'
    if data.get('crear_cuenta_owner') and owner_email:
        existing = Usuario.query.filter_by(email=owner_email).first()
        if not existing:
            hashed_pw = bcrypt.generate_password_hash(owner_pass).decode('utf-8')
            new_user = Usuario(
                nombre=data.get('encargado') or data['nombre'],
                email=owner_email,
                password_hash=hashed_pw,
                rol='dueno_cancha',
                liga_id=new_cancha.liga_id,
                cancha_id=new_cancha.id,
                activo=True
            )
            db.session.add(new_user)
            db.session.flush()
            new_cancha.dueno_id = new_user.id
        else:
            new_cancha.dueno_id = existing.id
            if existing.rol != 'dueno_cancha':
                existing.rol = 'dueno_cancha'

    # Hook: Crear cuentas de ÁRBITROS VINCULADOS (1 o 2)
    for i in [1, 2]:
        arb_email = data.get(f'arb_email_{i}')
        arb_nombre = data.get(f'arb_nombre_{i}')
        arb_pass = data.get(f'arb_pass_{i}') or 'fut123'
        if data.get(f'crear_arb_{i}') and arb_email and arb_nombre:
            # 1. Crear el Árbitro en la tabla 'arbitros' si no existe o actualizar link
            arb_record = Arbitro.query.filter_by(email=arb_email).first()
            if not arb_record:
                arb_record = Arbitro(
                    nombre=arb_nombre,
                    email=arb_email,
                    cancha_id=new_cancha.id,
                    liga_id=new_cancha.liga_id,
                    activo=True
                )
                db.session.add(arb_record)
            else:
                arb_record.cancha_id = new_cancha.id
            
            # 2. Crear el Usuario de acceso
            user_record = Usuario.query.filter_by(email=arb_email).first()
            if not user_record:
                hashed_pw = bcrypt.generate_password_hash(arb_pass).decode('utf-8')
                new_arb_user = Usuario(
                    nombre=arb_nombre,
                    email=arb_email,
                    password_hash=hashed_pw,
                    rol='arbitro',
                    liga_id=new_cancha.liga_id,
                    cancha_id=new_cancha.id,
                    activo=True
                )
                db.session.add(new_arb_user)
                
    # Hook: Crear cuentas de ENTRENADORES VINCULADOS (1 o 2)
    for i in [1, 2]:
        entr_email = data.get(f'entr_email_{i}')
        entr_nombre = data.get(f'entr_nombre_{i}')
        entr_pass = data.get(f'entr_pass_{i}') or 'fut123'
        if data.get(f'crear_entr_{i}') and entr_email and entr_nombre:
            user_record = Usuario.query.filter_by(email=entr_email).first()
            if not user_record:
                hashed_pw = bcrypt.generate_password_hash(entr_pass).decode('utf-8')
                new_entr_user = Usuario(
                    nombre=entr_nombre,
                    email=entr_email,
                    password_hash=hashed_pw,
                    rol='entrenador',
                    liga_id=new_cancha.liga_id,
                    cancha_id=new_cancha.id,
                    activo=True
                )
                db.session.add(new_entr_user)
            else:
                user_record.cancha_id = new_cancha.id
                if user_record.rol in ['equipo', None]:
                    user_record.rol = 'entrenador'

    db.session.commit()
    return jsonify(new_cancha.to_dict()), 201

@canchas_bp.route('/api/canchas/<int:id>', methods=['PUT'])
def update_cancha(id):
    cancha = Cancha.query.get_or_404(id)
    data = request.get_json()
    
    cancha.nombre = data.get('nombre', cancha.nombre)
    cancha.encargado = data.get('encargado', cancha.encargado)
    cancha.email_encargado = data.get('email_encargado', cancha.email_encargado)
    cancha.telefono_encargado = data.get('telefono_encargado', cancha.telefono_encargado)
    cancha.tipo = data.get('tipo', cancha.tipo)
    cancha.costo_renta = float(data.get('costo_renta', cancha.costo_renta))
    cancha.unidad_cobro = data.get('unidad_cobro', cancha.unidad_cobro)
    cancha.direccion = data.get('direccion', cancha.direccion)
    cancha.estado = data.get('estado', cancha.estado)
    cancha.municipio = data.get('municipio', cancha.municipio)
    cancha.notas = data.get('notas', cancha.notas)
    cancha.foto_url = data.get('foto_url', cancha.foto_url)
    cancha.modalidad = data.get('modalidad', cancha.modalidad)
    cancha.activo = data.get('activo', cancha.activo)
    
    # Hook: Crear o enlazar cuenta de DUEÑO DE CANCHA
    owner_email = data.get('owner_email_custom') or data.get('email_encargado')
    owner_pass = data.get('owner_pass_custom') or 'fut123'
    if data.get('crear_cuenta_owner') and owner_email:
        existing = Usuario.query.filter_by(email=owner_email).first()
        if not existing:
            hashed_pw = bcrypt.generate_password_hash(owner_pass).decode('utf-8')
            new_user = Usuario(
                nombre=data.get('encargado') or cancha.nombre,
                email=owner_email,
                password_hash=hashed_pw,
                rol='dueno_cancha',
                liga_id=cancha.liga_id,
                cancha_id=cancha.id,
                activo=True
            )
            db.session.add(new_user)
            db.session.flush()
            cancha.dueno_id = new_user.id
        else:
            cancha.dueno_id = existing.id
            if existing.rol != 'dueno_cancha':
                existing.rol = 'dueno_cancha'

    # Hook: Crear cuentas de ÁRBITROS VINCULADOS
    for i in [1, 2]:
        arb_email = data.get(f'arb_email_{i}')
        arb_nombre = data.get(f'arb_nombre_{i}')
        arb_pass = data.get(f'arb_pass_{i}') or 'fut123'
        if data.get(f'crear_arb_{i}') and arb_email and arb_nombre:
            arb_record = Arbitro.query.filter_by(email=arb_email).first()
            if not arb_record:
                arb_record = Arbitro(
                    nombre=arb_nombre,
                    email=arb_email,
                    cancha_id=cancha.id,
                    liga_id=cancha.liga_id,
                    activo=True
                )
                db.session.add(arb_record)
            else:
                arb_record.cancha_id = cancha.id
            
            user_record = Usuario.query.filter_by(email=arb_email).first()
            if not user_record:
                hashed_pw = bcrypt.generate_password_hash(arb_pass).decode('utf-8')
                new_arb_user = Usuario(
                    nombre=arb_nombre,
                    email=arb_email,
                    password_hash=hashed_pw,
                    rol='arbitro',
                    liga_id=cancha.liga_id,
                    cancha_id=cancha.id,
                    activo=True
                )
                db.session.add(new_arb_user)
                
    # Hook: Crear cuentas de ENTRENADORES VINCULADOS
    for i in [1, 2]:
        entr_email = data.get(f'entr_email_{i}')
        entr_nombre = data.get(f'entr_nombre_{i}')
        entr_pass = data.get(f'entr_pass_{i}') or 'fut123'
        if data.get(f'crear_entr_{i}') and entr_email and entr_nombre:
            user_record = Usuario.query.filter_by(email=entr_email).first()
            if not user_record:
                hashed_pw = bcrypt.generate_password_hash(entr_pass).decode('utf-8')
                new_entr_user = Usuario(
                    nombre=entr_nombre,
                    email=entr_email,
                    password_hash=hashed_pw,
                    rol='entrenador',
                    liga_id=cancha.liga_id,
                    cancha_id=cancha.id,
                    activo=True
                )
                db.session.add(new_entr_user)
            else:
                user_record.cancha_id = cancha.id
                if user_record.rol in ['equipo', None]:
                    user_record.rol = 'entrenador'
    
    db.session.commit()
    return jsonify(cancha.to_dict())

@canchas_bp.route('/api/canchas/<int:id>', methods=['DELETE'])
def delete_cancha(id):
    cancha = Cancha.query.get_or_404(id)
    db.session.delete(cancha)
    db.session.commit()
    return jsonify({"message": "Cancha eliminada"})

# ==========================================
# ENDPOINTS PARA CANCHAS INDIVIDUALES (CAMPOS)
# ==========================================

from models import CanchaDetalle

@canchas_bp.route('/api/canchas/<int:sede_id>/campos', methods=['GET'])
def get_campos(sede_id):
    """Obtiene todas las canchas individuales de un predio/sede"""
    campos = CanchaDetalle.query.filter_by(sede_id=sede_id).all()
    # Si la solicitud no tiene filtros extras, regresamos la lista.
    return jsonify([c.to_dict() for c in campos])

@canchas_bp.route('/api/canchas/<int:sede_id>/campos', methods=['POST'])
def add_campo(sede_id):
    """Agrega una nueva cancha a un predio"""
    sede = Cancha.query.get_or_404(sede_id)
    data = request.get_json()
    
    # === VERIFICACIÓN DE LÍMITES POR PLAN (OPCIÓN A) ===
    # El usuario dijo: equipo y super_arbitro -> max 1 cancha. dueño de liga -> varias
    user_rol = session.get('user_rol', '').lower()
    
    current_count = CanchaDetalle.query.filter_by(sede_id=sede_id).count()
    if user_rol in ['equipo', 'super_arbitro'] and current_count >= 1:
        return jsonify({"error": "Tu plan amateur solo permite 1 cancha por sede. Haz upgrade a Dueño de Liga para tener canchas múltiples."}), 403
    
    nuevo_campo = CanchaDetalle(
        sede_id=sede.id,
        liga_id=sede.liga_id,
        nombre=data.get('nombre', f'Cancha {current_count + 1}'),
        modalidad=data.get('modalidad', 'Fútbol 7'),
        superficie=data.get('superficie', 'Césped natural'),
        techada=bool(data.get('techada', False)),
        capacidad=int(data.get('capacidad', 0)),
        activa=bool(data.get('activa', True)),
        notas=data.get('notas', '')
    )
    
    db.session.add(nuevo_campo)
    db.session.commit()
    return jsonify(nuevo_campo.to_dict()), 201

@canchas_bp.route('/api/campos/<int:campo_id>', methods=['PUT'])
def update_campo(campo_id):
    campo = CanchaDetalle.query.get_or_404(campo_id)
    data = request.get_json()
    
    if 'nombre' in data: campo.nombre = data['nombre']
    if 'modalidad' in data: campo.modalidad = data['modalidad']
    if 'superficie' in data: campo.superficie = data['superficie']
    if 'techada' in data: campo.techada = bool(data['techada'])
    if 'capacidad' in data: campo.capacidad = int(data['capacidad'])
    if 'activa' in data: campo.activa = bool(data['activa'])
    if 'notas' in data: campo.notas = data['notas']
    
    db.session.commit()
    return jsonify(campo.to_dict())

@canchas_bp.route('/api/campos/<int:campo_id>', methods=['DELETE'])
def delete_campo(campo_id):
    campo = CanchaDetalle.query.get_or_404(campo_id)
    db.session.delete(campo)
    db.session.commit()
    return jsonify({"message": "Cancha individual (campo) eliminada con éxito"})
