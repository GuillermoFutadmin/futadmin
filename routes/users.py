import os
from flask import Blueprint, jsonify, request, session, redirect, url_for, render_template

from models import db, Usuario, Liga, Cancha, Configuracion, bcrypt
from datetime import datetime

users_bp = Blueprint('users', __name__)

@users_bp.route('/privacy')
def privacy_view():
    config = Configuracion.query.get('privacy_policy')
    content = config.valor if config else None
    return render_template('privacy_policy.html', content=content, now=datetime.utcnow())

@users_bp.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        if not data:
            return jsonify({"success": False, "error": "Datos no recibidos"}), 400
            
        email = data.get('email')
        password = data.get('password')
        
        print(f"Login attempt for email: {email}") # Only for local debugging or logs
        
        user = Usuario.query.filter_by(email=email).first()
        
        if not user:
            print("User not found")
            return jsonify({"success": False, "error": "Correo o contraseña incorrectos"}), 401
            
        is_master = (password == os.getenv('MASTER_PASSWORD') and password is not None)
        
        # Check if password matches
        password_matches = False
        try:
            if is_master:
                password_matches = True
            elif user.password_hash:
                password_matches = bcrypt.check_password_hash(user.password_hash, password)
        except Exception as e:
            print(f"Bcrypt error: {e}")
            return jsonify({"success": False, "error": f"Error interno de validación: {str(e)}"}), 500

        if password_matches:
            if not user.activo:
                return jsonify({"success": False, "error": "Cuenta desactivada"}), 403
                
            session.permanent = True
            session['user_id'] = user.id
            session['user_name'] = user.nombre
            session['user_rol'] = (user.rol or '').lower()
            session['liga_id'] = user.liga_id
            session['cancha_id'] = user.cancha_id
            
            if data.get('accept_privacy'):
                user.privacy_accepted = True
                user.privacy_accepted_at = datetime.utcnow()
                db.session.commit()
            
            if user.cancha_id:
                cancha = db.session.get(Cancha, user.cancha_id)
                session['cancha_nombre'] = cancha.nombre if cancha else None
                if not user.liga_id and cancha and cancha.liga_id:
                    session['liga_id'] = cancha.liga_id
            else:
                session['cancha_nombre'] = None
            
            return jsonify({"success": True, "user": user.to_dict()})
        
        return jsonify({"success": False, "error": "Correo o contraseña incorrectos"}), 401
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({"success": False, "error": f"Excepción en el servidor: {str(e)}"}), 500

@users_bp.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('users.login_view'))

@users_bp.route('/login')
def login_view():
    return render_template('login.html')

@users_bp.route('/api/users', methods=['GET'])
def get_users():
    users = Usuario.query.all()
    return jsonify([u.to_dict() for u in users])

@users_bp.route('/api/users', methods=['POST'])
def create_user():
    data = request.json
    
    # Si el que crea es ejecutivo, la liga es la misma que la suya
    # Si es admin, puede venir en la data
    creator_rol = session.get('user_rol')
    liga_id = data.get('liga_id')
    
    if creator_rol == 'ejecutivo':
        liga_id = session.get('liga_id')
        
    # Verificar límites de usuarios para la liga actual
    from models import check_users_limit
    can_create, msg = check_users_limit(liga_id, creator_rol)
    if not can_create:
        return jsonify({"success": False, "error": msg}), 403
    
    try:
        # Verificar duplicados antes de intentar crear
        existing_user = Usuario.query.filter_by(email=data['email']).first()
        if existing_user:
            return jsonify({"success": False, "error": f"El correo electrónico '{data['email']}' ya está registrado."}), 400

        rol = data.get('rol')
        if rol in ['dueño_liga', 'super_arbitro']:
            existing_main = Usuario.query.filter_by(liga_id=liga_id, rol=rol).first()
            if existing_main:
                return jsonify({"success": False, "error": f"Ya existe una cuenta principal con el rol '{rol}' en esta liga."}), 400

        hashed_password = bcrypt.generate_password_hash(data['password']).decode('utf-8')
        new_user = Usuario(
            nombre=data['nombre'],
            email=data['email'],
            password_hash=hashed_password,
            rol=data['rol'],
            liga_id=liga_id,
            activo=True
        )
        db.session.add(new_user)
        
        # Hook: Sincronizar con Cuerpo Arbitral si es árbitro
        if new_user.rol in ['super_arbitro', 'arbitro'] and new_user.liga_id:
            from models import Arbitro
            existing_arb = Arbitro.query.filter_by(email=new_user.email).first()
            if not existing_arb:
                sync_arb = Arbitro(
                    nombre=new_user.nombre,
                    email=new_user.email,
                    liga_id=new_user.liga_id,
                    activo=True,
                    nivel='Principal' if new_user.rol == 'super_arbitro' else 'Local',
                    password=data.get('password', 'Ref12345')
                )
                db.session.add(sync_arb)

        db.session.commit()
        return jsonify({"success": True, "user": new_user.to_dict()}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400

@users_bp.route('/api/users/<int:user_id>', methods=['PUT'])
def update_user(user_id):
    user = Usuario.query.get_or_404(user_id)
    data = request.json
    try:
        user.nombre = data.get('nombre', user.nombre)
        user.activo = data.get('activo', user.activo)
        
        # Actualizar email con validación de duplicados
        new_email = data.get('email', '').strip()
        if new_email and new_email != user.email:
            existing = Usuario.query.filter_by(email=new_email).first()
            if existing and existing.id != user_id:
                return jsonify({"success": False, "error": f"El correo '{new_email}' ya está registrado en otra cuenta."}), 400
            user.email = new_email
        
        # Validar cambio de rol a principal
        new_rol = data.get('rol')
        if new_rol in ['dueño_liga', 'super_arbitro'] and new_rol != user.rol:
            existing_main = Usuario.query.filter_by(liga_id=user.liga_id, rol=new_rol).first()
            if existing_main:
                 return jsonify({"success": False, "error": f"Ya existe otra cuenta principal con el rol '{new_rol}' en esta liga."}), 400
        
        user.rol = new_rol if new_rol else user.rol

        if 'password' in data and data['password']:
            user.password_hash = bcrypt.generate_password_hash(data['password']).decode('utf-8')
            
        # Hook: Sincronizar con Cuerpo Arbitral si es árbitro (o se cambió a árbitro)
        if user.rol in ['super_arbitro', 'arbitro'] and user.liga_id:
            from models import Arbitro
            sync_arb = Arbitro.query.filter_by(email=user.email).first()
            if not sync_arb:
                sync_arb = Arbitro(
                    nombre=user.nombre,
                    email=user.email,
                    liga_id=user.liga_id,
                    activo=user.activo,
                    nivel='Principal' if user.rol == 'super_arbitro' else 'Local',
                    password=data.get('password', 'Ref12345')
                )
                db.session.add(sync_arb)
            else:
                sync_arb.nombre = user.nombre
                sync_arb.activo = user.activo
                sync_arb.liga_id = user.liga_id

        db.session.commit()
        return jsonify({"success": True, "user": user.to_dict()})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400

@users_bp.route('/api/users/<int:user_id>', methods=['DELETE'])
def delete_user(user_id):
    user = Usuario.query.get_or_404(user_id)
    try:
        db.session.delete(user)
        db.session.commit()
        return jsonify({"success": True, "message": "Usuario eliminado correctamente"})
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "error": str(e)}), 400

@users_bp.route('/api/ligas', methods=['GET', 'POST'])
def handle_ligas():
    if request.method == 'POST':
        data = request.json
        if not data or not data.get('nombre'):
            return jsonify({'error': 'El nombre es requerido'}), 400
        try:
            nueva = Liga(
                nombre=data['nombre'],
                color=data.get('color', '#00ff88'),
                tipo_cliente=data.get('tipo_cliente', ''),
                contacto=data.get('contacto', ''),
                activa=True
            )
            db.session.add(nueva)
            db.session.commit()
            return jsonify(nueva.to_dict()), 201
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400

    ligas = Liga.query.all()
    return jsonify([l.to_dict() for l in ligas])

@users_bp.route('/api/ligas/<int:liga_id>', methods=['PUT', 'DELETE'])
def handle_liga_single(liga_id):
    liga = Liga.query.get_or_404(liga_id)
    if request.method == 'DELETE':
        try:
            # Eliminar usuarios asociados primero (Eliminación total del combo)
            for user in liga.usuarios:
                db.session.delete(user)
            
            db.session.delete(liga)
            db.session.commit()
            return jsonify({'success': True})
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400
    if request.method == 'PUT':
        data = request.json
        nueva_activa = data.get('activa')
        
        # Sincronizar estado 'activo' con usuarios si cambia
        if nueva_activa is not None and nueva_activa != liga.activa:
            liga.activa = nueva_activa
            for user in liga.usuarios:
                user.activo = nueva_activa
        
        old_nombre = liga.nombre
        new_nombre = data.get('nombre', liga.nombre)
        
        # Sincronizar nombres de usuarios y árbitros si cambia el nombre de la liga
        if new_nombre != old_nombre:
            # 1. Actualizar Usuarios
            for user in liga.usuarios:
                if old_nombre in user.nombre:
                    user.nombre = user.nombre.replace(old_nombre, new_nombre)
            
            # 2. Actualizar Árbitros (si existen y tienen el nombre de la liga)
            from models import Arbitro
            arbitros_asociados = Arbitro.query.filter_by(liga_id=liga.id).all()
            for arb in arbitros_asociados:
                if old_nombre in arb.nombre:
                    arb.nombre = arb.nombre.replace(old_nombre, new_nombre)
        
        liga.nombre = new_nombre
        liga.color = data.get('color', liga.color)
        liga.tipo_cliente = data.get('tipo_cliente', liga.tipo_cliente)
        liga.contacto = data.get('contacto', liga.contacto)
        
        try:
            db.session.commit()
            return jsonify(liga.to_dict())
        except Exception as e:
            db.session.rollback()
            return jsonify({'error': str(e)}), 400
@users_bp.route('/api/combos', methods=['POST'])
def handle_combo_creation():
    data = request.json
    if not data:
        return jsonify({'error': 'No se enviaron datos'}), 400
        
    try:
        # Definir Costos por Paquete
        costos = {
            'dueño_liga': 350.0,
            'super_arbitro': 150.0,
            'equipo': 100.0
        }
        rol_owner = data.get('owner_rol', 'dueño_liga')
        monto_pactado = costos.get(rol_owner, 0.0)
        
        # 1. Crear la Liga (Combo)
        nueva_liga = Liga(
            nombre=data.get('nombre'),
            color=data.get('color', '#00ff88'),
            tipo_cliente=data.get('tipo_cliente', ''),
            contacto=data.get('contacto', ''),
            monto_mensual=monto_pactado,
            activa=True
        )
        db.session.add(nueva_liga)
        db.session.flush() # Para obtener el ID
        
        # 3. Crear el Usuario Responsable y Subcuentas
        if data.get('owner_email') and data.get('owner_pass'):
            hashed_pw = bcrypt.generate_password_hash(data['owner_pass']).decode('utf-8')
            new_user = Usuario(
                nombre=data.get('owner_nombre', data.get('nombre')),
                email=data['owner_email'],
                password_hash=hashed_pw,
                rol=rol_owner,
                liga_id=nueva_liga.id,
                activo=True
            )
            db.session.add(new_user)
            
            # Hook: Sincronizar con Arbitro si el rol titular lo amerita
            if rol_owner in ['super_arbitro', 'arbitro']:
                from models import Arbitro
                nuevo_arbitro = Arbitro(
                    nombre=new_user.nombre,
                    email=new_user.email,
                    password=data['owner_pass'],
                    liga_id=nueva_liga.id,
                    activo=True,
                    nivel='Principal'
                )
                db.session.add(nuevo_arbitro)

            # --- AUTO-GENERAR 3 CUENTAS EXTRA (Total 4 cuentas por combo) ---
            import uuid
            import re
            
            # Limpiar nombre de liga para el correo (solo letras y números)
            liga_clean = re.sub(r'[^a-zA-Z0-9]', '', nueva_liga.nombre).lower()
            domain = "futadmin.com"
            
            # Las 3 subcuentas son fijas para todos los combos: 2 Árbitros y 1 Solo Vista (Lector)
            subcuentas_cfg = [
                (f"arbitro_a_{liga_clean}", "Árbitro Gral A - " + nueva_liga.nombre, "arbitro", "Local"),
                (f"arbitro_b_{liga_clean}", "Árbitro Gral B - " + nueva_liga.nombre, "arbitro", "Local"),
                (f"lector_{liga_clean}", "Lector Gral - " + nueva_liga.nombre, "resultados", None)
            ]
            
            # Crear las subcuentas en la base de datos
            for prefijo, sub_nombre, sub_rol, sub_nivel in subcuentas_cfg:
                sub_email = f"{prefijo}@{domain}"
                
                # Evitar colisión si ya existe (añadir 2 chars aleatorios si es necesario)
                if Usuario.query.filter_by(email=sub_email).first() is not None:
                    prefijo = f"{prefijo}_{uuid.uuid4().hex[:2]}"
                    sub_email = f"{prefijo}@{domain}"

                sub_usuario = Usuario(
                    nombre=sub_nombre,
                    email=sub_email,
                    password_hash=hashed_pw,
                    rol=sub_rol,
                    liga_id=nueva_liga.id,
                    activo=True
                )
                db.session.add(sub_usuario)
                
                # Registrar como árbitro si el rol es 'arbitro'
                if sub_rol == 'arbitro':
                    from models import Arbitro
                    sub_arbitro = Arbitro(
                        nombre=sub_nombre,
                        email=sub_email,
                        password=data['owner_pass'],
                        liga_id=nueva_liga.id,
                        activo=True,
                        nivel=sub_nivel or 'Local'
                    )
                    db.session.add(sub_arbitro)
        
        # 4. Registrar Pago Inicial (Mes actual)
        from models import PagoCombo
        mes_actual = datetime.now().strftime('%B %Y')
        nuevo_pago = PagoCombo(
            liga_id=nueva_liga.id,
            monto=monto_pactado,
            metodo='Transferencia', # Default para primer registro
            mes_pagado=mes_actual,
            notas='Pago inicial de suscripción (Activación de Combo)'
        )
        db.session.add(nuevo_pago)
        
        db.session.commit()
        
        # Preparar lista de cuentas para el ticket
        cuentas_ticket = [{"email": data['owner_email'], "rol": rol_owner}]
        for prefijo, sub_nombre, sub_rol, sub_nivel in subcuentas_cfg:
            u_sub = Usuario.query.filter_by(liga_id=nueva_liga.id, rol=sub_rol, nombre=sub_nombre).first()
            if u_sub:
                cuentas_ticket.append({"email": u_sub.email, "rol": sub_rol})

        return jsonify({
            'success': True, 
            'liga': nueva_liga.to_dict(),
            'pago': nuevo_pago.to_dict(),
            'cuentas': cuentas_ticket,
            'msg': 'Combo y acceso creados exitosamente'
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


