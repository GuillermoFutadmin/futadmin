import os
from flask import Blueprint, jsonify, request, session, redirect, url_for, render_template

from models import db, Usuario, Liga, Cancha, Configuracion, bcrypt
from datetime import datetime
import uuid
import re
from logic.receipts import generate_receipt_pdf, send_receipt_email

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
    import traceback
    from datetime import datetime
    try:
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
            raw_subdominio = data.get('subdominio', liga.subdominio)
            liga.subdominio = raw_subdominio.strip() if raw_subdominio and raw_subdominio.strip() != "" else None
            
            # Actualizar credenciales si se proporcionan
            owner_email = data.get('owner_email')
            owner_pass = data.get('owner_pass')

            if owner_email or owner_pass:
                # Identificar el usuario titular
                from models import Usuario, Arbitro
                titular = Usuario.query.filter_by(liga_id=liga.id).filter(Usuario.rol.in_(['dueño_liga', 'super_arbitro', 'equipo'])).first()
                
                if titular:
                    if owner_email:
                        titular.email = owner_email
                    
                    if owner_pass:
                        hashed_pw = bcrypt.generate_password_hash(owner_pass).decode('utf-8')
                        # Sincronizar contraseña para TODOS los usuarios de la liga (Combo)
                        for u in liga.usuarios:
                            u.password_hash = hashed_pw
                        
                        # Sincronizar también con la tabla de Árbitros (password en plano según modelo actual)
                        arbitros_asociados = Arbitro.query.filter_by(liga_id=liga.id).all()
                        for arb in arbitros_asociados:
                            arb.password = owner_pass
            
            # Commit y respuesta única al final
            db.session.commit()
            return jsonify(liga.to_dict())
            
    except Exception as e:
        db.session.rollback()
        error_msg = f"Error en handle_liga_single (ID {liga_id}): {str(e)}"
        print(f"{error_msg}\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500
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
        
        # 0. Validar si el correo del titular ya existe (Causa común de 400)
        owner_email = data.get('owner_email')
        if not owner_email:
            return jsonify({'error': 'El correo del titular es obligatorio'}), 400
            
        if Usuario.query.filter_by(email=owner_email).first():
            return jsonify({'error': f'El correo {owner_email} ya está registrado en el sistema'}), 400

        # 1. Crear la Liga (Combo)
        raw_sub = data.get('subdominio')
        clean_sub = raw_sub.strip() if raw_sub and raw_sub.strip() != "" else None
        
        # Validar unicidad de subdominio manualmente para dar error claro
        if clean_sub and Liga.query.filter_by(subdominio=clean_sub).first():
            return jsonify({'error': f'El subdominio {clean_sub} ya está en uso'}), 400

        nueva_liga = Liga(
            nombre=data.get('nombre'),
            subdominio=clean_sub,
            color=data.get('color', '#00ff88'),
            tipo_cliente=data.get('tipo_cliente', ''),
            contacto=data.get('contacto', ''),
            monto_mensual=monto_pactado,
            activa=True
        )
        db.session.add(nueva_liga)
        db.session.flush() # Para obtener el ID
        
        # 3. Crear el Usuario Responsable y Subcuentas
        owner_pass = data.get('owner_pass')
        if owner_email and owner_pass:
            hashed_pw = bcrypt.generate_password_hash(owner_pass).decode('utf-8')
            new_user = Usuario(
                nombre=data.get('owner_nombre', data.get('nombre')),
                email=owner_email,
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

        # --- ENVIAR NOTIFICACIÓN POR CORREO (Async) ---
        try:
            from logic.receipts import trigger_receipt_email_async
            from datetime import timedelta
            
            # Obtener datos completos de la liga para el Estado de Cuenta
            liga_info = nueva_liga.to_dict()
            
            # Preparar datos seguros para el hilo (objetos planos)
            ticket_data = {
                "is_futadmin": True,
                "id_cliente": nueva_liga.id,
                "folio": f"COMB-{nueva_liga.id}-{datetime.now().strftime('%y%m%d')}",
                "fecha": (datetime.utcnow() - timedelta(hours=6)).strftime('%d/%m/%Y %H:%M'),
                "fecha_registro": liga_info.get('fecha_registro'),
                "liga_nombre": nueva_liga.nombre,
                "monto_abonado": float(monto_pactado),
                "monto_mensual": float(nueva_liga.monto_mensual or 0),
                "monto_total_mensual": float(nueva_liga.monto_total_mensual or 0),
                "tipo": f"Suscripción - Plan {rol_owner.replace('_', ' ').title()}",
                "paquete": rol_owner,
                "metodo": "Transferencia",
                "mes_pagado": mes_actual,
                "equipo": "Plan Inicial (1 Sede, 5 Ligas)", 
                "torneo": "Activación FutAdmin PRO",
                "contacto": nueva_liga.contacto,
                "vencimiento": liga_info.get('vencimiento'),
                "stats": liga_info.get('stats', {}),
                "detalles": liga_info.get('detalles', {}),
                "expansiones": liga_info.get('expansiones', []),
                "pagos_historial": [nuevo_pago.to_dict()] # El pago que acabamos de crear
            }
            
            nombre_u = data.get('owner_nombre', 'Administrador')
            
            # 1. Enviar al correo del Dueño
            trigger_receipt_email_async(ticket_data, data['owner_email'], nombre_u)
            
            # 2. Enviar copia al correo de Contacto (si es distinto)
            if nueva_liga.contacto and nueva_liga.contacto != data['owner_email']:
                trigger_receipt_email_async(ticket_data, nueva_liga.contacto, nombre_u)
                
        except Exception as e:
            print(f"Error en hook asíncrono de correo (combo): {e}")

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



@users_bp.route('/api/user/self/change_password', methods=['POST'])
def self_change_password():
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "No has iniciado sesión"}), 401
    
    data = request.json
    new_password = data.get('new_password')
    if not new_password or len(new_password) < 6:
        return jsonify({"success": False, "error": "La contraseña debe tener al menos 6 caracteres"}), 400
    
    user = Usuario.query.get(session['user_id'])
    if not user:
        return jsonify({"success": False, "error": "Usuario no encontrado"}), 404
    
    # Bloqueo de seguridad para cuentas genéricas/públicas
    if user.rol in ['resultados', 'espectador', 'visor']:
        return jsonify({
            "success": False, 
            "error": "Esta es una cuenta pública de acceso general. Por seguridad, el cambio de contraseña está restringido."
        }), 403
        
    user.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
    db.session.commit()
    return jsonify({"success": True, "message": "Contraseña actualizada correctamente"})

@users_bp.route('/api/user/combo/collaborators', methods=['GET'])
def get_combo_collaborators():
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "No has iniciado sesión"}), 401
    
    user = Usuario.query.get(session['user_id'])
    if not user or user.rol not in ['dueño_liga', 'super_arbitro', 'equipo']:
        return jsonify({"success": False, "error": "No tienes permisos para ver colaboradores"}), 403
    
    # Obtener otros usuarios de la misma liga
    collaborators = Usuario.query.filter(Usuario.liga_id == user.liga_id, Usuario.id != user.id).all()
    return jsonify([u.to_dict() for u in collaborators])

@users_bp.route('/api/user/collaborator/<int:colab_id>/password', methods=['PUT'])
def update_collaborator_password(colab_id):
    if 'user_id' not in session:
        return jsonify({"success": False, "error": "No has iniciado sesión"}), 401
    
    data = request.json
    new_password = data.get('password')
    if not new_password or len(new_password) < 6:
        return jsonify({"success": False, "error": "La contraseña debe tener al menos 6 caracteres"}), 400
    
    current_user = Usuario.query.get(session['user_id'])
    colab = Usuario.query.get(colab_id)
    
    if not colab or colab.liga_id != current_user.liga_id:
        return jsonify({"success": False, "error": "Colaborador no encontrado o no pertenece a tu liga"}), 404
    
    # Validar permisos
    if current_user.rol not in ['dueño_liga', 'super_arbitro', 'equipo']:
        return jsonify({"success": False, "error": "No tienes permisos para administrar esta cuenta"}), 403
        
    colab.password_hash = bcrypt.generate_password_hash(new_password).decode('utf-8')
    
    # Si el colaborador es árbitro, sincronizar también su tabla
    from models import Arbitro
    sync_arb = Arbitro.query.filter_by(email=colab.email).first()
    if sync_arb:
        sync_arb.password = new_password
        
    db.session.commit()
    return jsonify({"success": True, "message": f"Contraseña de {colab.nombre} actualizada correctamente"})


# ─────────────────────────────────────────────────────────────────────────────
#  AUTO-REGISTRO PÚBLICO (Freemium — sin cobro)
# ─────────────────────────────────────────────────────────────────────────────

@users_bp.route('/registro')
def registro_view():
    """Página pública de registro para nuevos administradores de liga."""
    return render_template('registro.html')


def generate_unique_subdomain(name):
    """Genera un slug único para el subdominio de la liga."""
    import re, unicodedata
    if not name: return None
    # Quitar acentos y caracteres especiales
    slug = unicodedata.normalize('NFKD', name).encode('ascii', 'ignore').decode('ascii')
    slug = re.sub(r'[^a-z0-9]+', '-', slug.lower()).strip('-')
    
    if not slug: slug = "liga"
    
    base_slug = slug[:40]
    final_slug = base_slug
    counter = 1
    # Búsqueda de disponibilidad
    while Liga.query.filter_by(subdominio=final_slug).first():
        suffix = f"-{counter}"
        final_slug = base_slug[:(40-len(suffix))] + suffix
        counter += 1
    return final_slug


@users_bp.route('/api/registro', methods=['POST'])
def registro_publico():
    """
    Registro público gratuito refinado.
    Crea una Liga + 4 cuentas de acceso.
    Realiza AUTO-LOGIN automático tras el éxito.
    """
    data = request.json or {}

    # Honeypot check (campo oculto que no debería estar lleno)
    if data.get('website_url'):
        return jsonify({'success': False, 'error': 'Bot detected'}), 400

    # ── Validaciones ──────────────────────────────────────────────────────────
    nombre_liga   = (data.get('nombre_liga') or '').strip()
    nombre_admin  = (data.get('nombre_admin') or '').strip()
    email         = (data.get('email') or '').strip().lower()
    password      = data.get('password') or ''
    telefono      = (data.get('telefono') or '').strip()
    municipio     = (data.get('municipio') or '').strip()
    estado        = (data.get('estado') or '').strip()

    if not all([nombre_liga, nombre_admin, email, password]):
        return jsonify({'success': False, 'error': 'Campos básicos obligatorios omitidos'}), 400
    
    if len(password) < 8:
        return jsonify({'success': False, 'error': 'La contraseña debe tener al menos 8 caracteres'}), 400

    if Usuario.query.filter_by(email=email).first():
        return jsonify({'success': False, 'error': f'El correo {email} ya está registrado'}), 400

    try:
        # ── 1. Generar Subdominio y Color ─────────────────────────────────────
        subdominio = generate_unique_subdomain(nombre_liga)
        
        import random
        vibrant_colors = [
            '#00ff88', '#00d1ff', '#ff007a', '#7a00ff', '#ff8800', 
            '#ffcc00', '#00ffcc', '#ff00ff', '#88ff00', '#0088ff',
            '#ff4444', '#44ff44', '#4444ff', '#ffff44', '#ff44ff'
        ]
        color_random = random.choice(vibrant_colors)

        # ── 2. Crear Liga ─────────────────────────────────────────────────────
        nueva_liga = Liga(
            nombre=nombre_liga,
            subdominio=subdominio,
            color=color_random,
            tipo_cliente='dueño_liga',
            contacto=telefono if telefono else email,
            municipio=municipio,
            estado=estado,
            monto_mensual=0.0,
            activa=True
        )
        # Guardar ubicación en notas o campos extras si no existen campos dedicados
        # (Asumiendo que Liga puede manejar esto o se agrega a contacto)
        if municipio or estado:
            ubicacion = f"{municipio}, {estado}".strip(", ")
            nueva_liga.contacto = f"{nueva_liga.contacto} | {ubicacion}"

        db.session.add(nueva_liga)
        db.session.flush()

        # ── 3. Contraseña y Propietario ───────────────────────────────────────
        hashed_pw = bcrypt.generate_password_hash(password).decode('utf-8')
        owner = Usuario(
            nombre=nombre_admin,
            email=email,
            password_hash=hashed_pw,
            rol='dueño_liga',
            liga_id=nueva_liga.id,
            activo=True
        )
        db.session.add(owner)

        # ── 4. Generar Subcuentas ─────────────────────────────────────────────
        liga_clean = re.sub(r'[^a-zA-Z0-9]', '', nombre_liga).lower()[:20]
        domain = 'futadmin.com'
        subcuentas_cfg = [
            (f'arbitro_a_{liga_clean}', f'Árbitro A — {nombre_liga}', 'arbitro',    'Local'),
            (f'arbitro_b_{liga_clean}', f'Árbitro B — {nombre_liga}', 'arbitro',    'Local'),
            (f'lector_{liga_clean}',    f'Lector — {nombre_liga}',    'resultados', None),
        ]

        for prefijo, sub_nombre, sub_rol, sub_nivel in subcuentas_cfg:
            sub_email = f'{prefijo}@{domain}'
            if Usuario.query.filter_by(email=sub_email).first():
                sub_email = f'{prefijo}_{uuid.uuid4().hex[:4]}@{domain}'

            sub_user = Usuario(
                nombre=sub_nombre,
                email=sub_email,
                password_hash=hashed_pw,
                rol=sub_rol,
                liga_id=nueva_liga.id,
                activo=True
            )
            db.session.add(sub_user)
            if sub_rol == 'arbitro':
                from models import Arbitro
                sub_arb = Arbitro(
                    nombre=sub_nombre, email=sub_email, password=password,
                    liga_id=nueva_liga.id, activo=True, nivel=sub_nivel or 'Local'
                )
                db.session.add(sub_arb)

        db.session.commit()

        # ── 5. AUTO-LOGIN ─────────────────────────────────────────────────────
        session.clear() # Limpiar cualquier sesión previa
        session['user_id']   = owner.id
        session['user_name'] = owner.nombre
        session['user_rol']  = owner.rol
        session['liga_id']   = nueva_liga.id
        session.permanent    = True

        return jsonify({
            'success': True,
            'redirect_url': '/',
            'msg': f'¡Bienvenido {nombre_admin}! Tu liga "{nombre_liga}" ha sido creada.'
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': f'Ocurrió un error al crear la liga: {str(e)}'}), 500

