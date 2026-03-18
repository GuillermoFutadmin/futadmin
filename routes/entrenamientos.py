from flask import Blueprint, request, jsonify, session
from models import db, GrupoEntrenamiento, AlumnoEntrenamiento, Pago, Arbitro, Cancha, apply_liga_filter, Usuario
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()
from datetime import datetime

entrenamientos_bp = Blueprint('entrenamientos', __name__)

@entrenamientos_bp.route('/grupos', methods=['GET', 'POST'])
def handle_grupos_entrenamiento():
    if request.method == 'POST':
        data = request.json
        
        fecha_ini = None
        if data.get('fecha_inicio'):
            try: fecha_ini = datetime.strptime(data['fecha_inicio'], '%Y-%m-%d').date()
            except: pass
            
        fecha_fn = None
        if data.get('fecha_fin'):
            try: fecha_fn = datetime.strptime(data['fecha_fin'], '%Y-%m-%d').date()
            except: pass

        nuevo = GrupoEntrenamiento(
            nombre=data.get('nombre'),
            profesor_id=data.get('profesor_id') or None,
            dias=data.get('dias'),
            horario=data.get('horario'),
            costo_mensual=float(data.get('costo_mensual') or 0.0),
            tipo=data.get('tipo'),
            categoria=data.get('categoria'),
            fecha_inicio=fecha_ini,
            fecha_fin=fecha_fn,
            cancha=data.get('cancha'),
            capacidad=int(data.get('capacidad') or 0),
            costo_inscripcion=float(data.get('costo_inscripcion') or 0.0),
            foto_url=data.get('foto_url'),
            liga_id=session.get('liga_id')
        )
        db.session.add(nuevo)
        
        # Hook: Si el profesor tiene email, asegurar usuario de entrenador
        if nuevo.profesor_id:
            prof = Arbitro.query.get(nuevo.profesor_id)
            if prof and prof.email:
                existing = Usuario.query.filter_by(email=prof.email).first()
                if not existing:
                    hashed_pw = bcrypt.generate_password_hash(prof.password or 'coach123').decode('utf-8')
                    new_user = Usuario(
                        nombre=prof.nombre,
                        email=prof.email,
                        password_hash=hashed_pw,
                        rol='entrenador',
                        liga_id=nuevo.liga_id,
                        activo=True
                    )
                    db.session.add(new_user)

        db.session.commit()
        return jsonify(nuevo.to_dict()), 201
        
    # GET
    query = GrupoEntrenamiento.query
    query = apply_liga_filter(query, GrupoEntrenamiento)
    grupos = query.order_by(GrupoEntrenamiento.id.desc()).all()
    return jsonify([g.to_dict() for g in grupos])

@entrenamientos_bp.route('/grupos/<int:id>', methods=['PUT', 'DELETE'])
def handle_grupo_id(id):
    grupo = GrupoEntrenamiento.query.get_or_404(id)
    if request.method == 'DELETE':
        db.session.delete(grupo)
        db.session.commit()
        return jsonify({"success": True})
        
    if request.method == 'PUT':
        data = request.json
        if 'nombre' in data: grupo.nombre = data['nombre']
        if 'profesor_id' in data: grupo.profesor_id = data['profesor_id'] or None
        if 'dias' in data: grupo.dias = data['dias']
        if 'horario' in data: grupo.horario = data['horario']
        if 'costo_mensual' in data: grupo.costo_mensual = float(data['costo_mensual'])
        if 'tipo' in data: grupo.tipo = data['tipo']
        if 'categoria' in data: grupo.categoria = data['categoria']
        if 'fecha_inicio' in data and data['fecha_inicio']:
            try: grupo.fecha_inicio = datetime.strptime(data['fecha_inicio'], '%Y-%m-%d').date()
            except: pass
        if 'fecha_fin' in data and data['fecha_fin']:
            try: grupo.fecha_fin = datetime.strptime(data['fecha_fin'], '%Y-%m-%d').date()
            except: pass
        if 'cancha' in data: grupo.cancha = data['cancha']
        if 'capacidad' in data: grupo.capacidad = int(data['capacidad'] or 0)
        if 'costo_inscripcion' in data: grupo.costo_inscripcion = float(data['costo_inscripcion'])
        if 'foto_url' in data: grupo.foto_url = data['foto_url']
        if 'activo' in data: grupo.activo = data['activo']
        
        db.session.commit()
        return jsonify(grupo.to_dict())

@entrenamientos_bp.route('/alumnos', methods=['GET', 'POST'])
def handle_alumnos_entrenamiento():
    if request.method == 'POST':
        data = request.json
        grupo_id = data.get('grupo_id')
        if not grupo_id:
            return jsonify({"error": "Se requiere grupo_id"}), 400
            
        fecha_nac = None
        if data.get('fecha_nacimiento'):
            try:
                fecha_nac = datetime.strptime(data['fecha_nacimiento'], '%Y-%m-%d').date()
            except ValueError:
                pass
                
        abono = float(data.get('pago_inicial', 0))
        metodo = data.get('metodo_pago', 'Efectivo')
        grupo = GrupoEntrenamiento.query.get(grupo_id)
        
        nuevo = AlumnoEntrenamiento(
            nombre=data.get('nombre'),
            grupo_id=grupo_id,
            fecha_nacimiento=fecha_nac,
            telefono_contacto=data.get('telefono_contacto'),
            nombre_tutor=data.get('nombre_tutor'),
            foto_url=data.get('foto_url'),
            liga_id=session.get('liga_id')
        )
        db.session.add(nuevo)
        db.session.flush()

        # Si hay abono inicial, registrar el pago con el periodo actual para que aparezca en el resumen
        if abono > 0:
            ahora = datetime.now()
            # Formato de periodo: "Mes Año" (ej. "Marzo 2026")
            meses = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
            periodo_actual = f"{meses[ahora.month]} {ahora.year}"
            
            nuevo_pago = Pago(
                alumno_id=nuevo.id,
                monto=abono,
                tipo='Inscripcion_Academia',
                metodo=metodo,
                comentario=f"{periodo_actual} | Inscripción inicial"
            )
            db.session.add(nuevo_pago)
            db.session.flush()

        db.session.commit()

        reglas_cancha = ""
        cancha_asignada = None
        if grupo and grupo.cancha:
            cancha_asignada = Cancha.query.filter_by(nombre=grupo.cancha).first()
            if cancha_asignada and cancha_asignada.notas:
                reglas_cancha = f"\n\nREGLAS DE LA SEDE ({grupo.cancha}):\n{cancha_asignada.notas}"

        ticket_data = {
            "alumno": nuevo.nombre,
            "grupo": grupo.nombre if grupo else "Sin grupo",
            "categoria": grupo.categoria if grupo else "",
            "profesor": grupo.profesor.nombre if grupo and grupo.profesor else "Sin asignar",
            "sede": grupo.cancha if (grupo and grupo.cancha) else "Por definir",
            "monto_pagado": abono,
            "metodo": metodo,
            "fecha": (nuevo.fecha_inscripcion or datetime.now()).strftime('%d/%m/%Y %H:%M'),
            "horario": grupo.horario if grupo else "",
            "dias": grupo.dias if grupo else "",
            "clausulas": reglas_cancha
        }

        return jsonify({
            "alumno": nuevo.to_dict(),
            "ticket": ticket_data
        }), 201
        
    # GET
    grupo_id = request.args.get('grupo_id')
    query = AlumnoEntrenamiento.query
    query = apply_liga_filter(query, AlumnoEntrenamiento)
    if grupo_id:
        query = query.filter_by(grupo_id=grupo_id)
    alumnos = query.order_by(AlumnoEntrenamiento.nombre).all()
    return jsonify([a.to_dict() for a in alumnos])

@entrenamientos_bp.route('/alumnos/<int:id>', methods=['PUT', 'DELETE'])
def handle_alumno_id(id):
    alumno = AlumnoEntrenamiento.query.get_or_404(id)
    if request.method == 'DELETE':
        db.session.delete(alumno)
        db.session.commit()
        return jsonify({"success": True})
        
    if request.method == 'PUT':
        try:
            data = request.json
            if 'nombre' in data: alumno.nombre = data['nombre']
            if 'fecha_nacimiento' in data and data['fecha_nacimiento']:
                try:
                    alumno.fecha_nacimiento = datetime.strptime(data['fecha_nacimiento'], '%Y-%m-%d').date()
                except ValueError:
                    pass
            if 'telefono_contacto' in data: alumno.telefono_contacto = data['telefono_contacto']
            if 'nombre_tutor' in data: alumno.nombre_tutor = data['nombre_tutor']
            if 'foto_url' in data: alumno.foto_url = data['foto_url']
            if 'activo' in data: alumno.activo = data['activo']
            
            # Permitir registrar pago incluso en edición
            abono = float(data.get('pago_inicial', 0))
            ticket_data = None
            if abono > 0:
                ahora = datetime.now()
                meses = ["", "Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"]
                periodo_actual = f"{meses[ahora.month]} {ahora.year}"
                
                nuevo_pago = Pago(
                    alumno_id=alumno.id,
                    monto=abono,
                    tipo='Inscripcion_Academia',
                    metodo=data.get('metodo_pago', 'Efectivo'),
                    comentario=f"{periodo_actual} | Abono en edición"
                )
                db.session.add(nuevo_pago)
                db.session.flush()
                
                grupo = alumno.grupo
                if grupo and grupo.cancha:
                    cancha_asignada = Cancha.query.filter_by(nombre=grupo.cancha).first()
                    if cancha_asignada and cancha_asignada.notas:
                        reglas_cancha = f"\n\nREGLAS DE LA SEDE ({grupo.cancha}):\n{cancha_asignada.notas}"

                ticket_data = {
                    "alumno": alumno.nombre,
                    "grupo": grupo.nombre if grupo else "Sin grupo",
                    "categoria": grupo.categoria if grupo else "",
                    "profesor": grupo.profesor.nombre if grupo and grupo.profesor else "Sin asignar",
                    "sede": grupo.cancha if (grupo and grupo.cancha) else "Por definir",
                    "monto_pagado": abono,
                    "metodo": nuevo_pago.metodo,
                    "fecha": ahora.strftime('%d/%m/%Y %H:%M'),
                    "horario": grupo.horario if grupo else "",
                    "dias": grupo.dias if grupo else "",
                    "clausulas": reglas_cancha
                }
            
            db.session.commit()
            res = alumno.to_dict()
            if ticket_data:
                return jsonify({"alumno": res, "ticket": ticket_data})
            return jsonify(res)
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

@entrenamientos_bp.route('/pagos', methods=['GET', 'POST'])
def handle_pagos_academia():
    if request.method == 'POST':
        data = request.json
        print(f"DEBUG: Intento de registro de pago: {data}")
        alumno_id = data.get('alumno_id')
        if not alumno_id:
            return jsonify({"error": "Se requiere alumno_id"}), 400

        try:
            nuevo = Pago(
                inscripcion_id=None,
                alumno_id=alumno_id,
                monto=float(data.get('monto', 0)),
                tipo='Mensualidad_Academia',
                metodo=data.get('metodo', 'Efectivo'),
                comentario=data.get('comentario', ''),
                liga_id=session.get('liga_id')
            )
            if data.get('periodo'):
                nuevo.comentario = data['periodo'] + ((' | ' + data.get('comentario', '')) if data.get('comentario') else '')

            db.session.add(nuevo)
            db.session.commit()
            
            # Refresh para asegurar que nuevo.fecha esté poblado
            db.session.refresh(nuevo)
            
            alumno = AlumnoEntrenamiento.query.get(alumno_id)
            grupo = alumno.grupo if alumno else None
            
            # Preparar datos del ticket
            ticket_data = {
                "alumno": alumno.nombre if alumno else "—",
                "grupo": grupo.nombre if grupo else "Sin grupo",
                "categoria": grupo.categoria if grupo else "",
                "profesor": grupo.profesor.nombre if grupo and grupo.profesor else "Sin asignar",
                "monto_pagado": float(nuevo.monto),
                "metodo": nuevo.metodo,
                "fecha": nuevo.fecha.strftime('%d/%m/%Y %H:%M') if nuevo.fecha else datetime.utcnow().strftime('%d/%m/%Y %H:%M'),
                "horario": grupo.horario if grupo else "",
                "dias": grupo.dias if grupo else ""
            }
            
            print(f"DEBUG: Pago registrado exitosamente ID: {nuevo.id}")
            return jsonify({
                "status": "success",
                "id": nuevo.id,
                "ticket": ticket_data
            }), 201
        except Exception as e:
            db.session.rollback()
            import traceback
            error_details = traceback.format_exc()
            print(f"ERROR CRÍTICO en registro de pago academia:\n{error_details}")
            from flask import current_app
            return jsonify({
                "error": str(e),
                "details": error_details if current_app.debug else "Consulte los logs del servidor"
            }), 500

    grupo_id = request.args.get('grupo_id', type=int)
    alumno_id_filter = request.args.get('alumno_id', type=int)
    periodo = request.args.get('periodo')

    query = Pago.query.filter_by(tipo='Mensualidad_Academia')
    query = apply_liga_filter(query, Pago)

    if alumno_id_filter:
        query = query.filter_by(alumno_id=alumno_id_filter)
    elif grupo_id:
        alumnos_ids = [a.id for a in AlumnoEntrenamiento.query.filter_by(grupo_id=grupo_id).all()]
        if not alumnos_ids:
            return jsonify([])
        query = query.filter(Pago.alumno_id.in_(alumnos_ids))

    if periodo:
        query = query.filter(Pago.comentario.like(f'{periodo}%'))

    pagos = query.order_by(Pago.fecha.desc()).all()
    result = []
    for p in pagos:
        alumno = AlumnoEntrenamiento.query.get(p.alumno_id) if p.alumno_id else None
        result.append({
            "id": p.id,
            "alumno_id": p.alumno_id,
            "alumno_nombre": alumno.nombre if alumno else "—",
            "grupo_id": alumno.grupo_id if alumno else None,
            "monto": p.monto,
            "metodo": p.metodo,
            "comentario": p.comentario or "",
            "fecha": p.fecha.strftime('%Y-%m-%d %H:%M') if p.fecha else ""
        })
    return jsonify(result)

@entrenamientos_bp.route('/pagos/resumen', methods=['GET'])
def resumen_pagos_academia():
    try:
        grupo_id = request.args.get('grupo_id', type=int)
        periodo = request.args.get('periodo', '')

        if not grupo_id or not periodo:
            return jsonify({"error": "grupo_id y periodo son requeridos"}), 400

        alumnos = AlumnoEntrenamiento.query.filter_by(grupo_id=grupo_id, activo=True).all()
        alumnos_ids = [a.id for a in alumnos]

        if not alumnos_ids:
            return jsonify({
                "grupo_nombre": GrupoEntrenamiento.query.get(grupo_id).nombre if GrupoEntrenamiento.query.get(grupo_id) else "",
                "costo_mensual": 0,
                "periodo": periodo,
                "total_alumnos": 0,
                "total_pagados": 0,
                "alumnos": []
            })

        pagos_periodo = Pago.query.filter(
            Pago.tipo.in_(['Mensualidad_Academia', 'Inscripcion_Academia', 'Abono_Academia']),
            Pago.alumno_id.in_(alumnos_ids),
            Pago.comentario.like(f'{periodo}%')
        ).all()

        grupo = GrupoEntrenamiento.query.get(grupo_id)
        costo_mensual = float(grupo.costo_mensual or 0) if grupo else 0

        result = []
        total_pagados_completo = 0
        
        for a in alumnos:
            mis_pagos = [p for p in pagos_periodo if p.alumno_id == a.id]
            total_pagado_alumno = sum(p.monto for p in mis_pagos)
            es_pagado_completo = total_pagado_alumno >= costo_mensual if costo_mensual > 0 else len(mis_pagos) > 0
            
            if es_pagado_completo:
                total_pagados_completo += 1

            result.append({
                "alumno_id": a.id,
                "alumno_nombre": a.nombre,
                "telefono": a.telefono_contacto or "",
                "tutor": a.nombre_tutor or "",
                "pagado": es_pagado_completo,
                "monto_pagado": total_pagado_alumno,
                "metodo": mis_pagos[-1].metodo if mis_pagos else "—",
                "fecha_pago": mis_pagos[-1].fecha.strftime('%Y-%m-%d') if mis_pagos and mis_pagos[-1].fecha else "—",
                "pagos": [{
                    "id": p.id,
                    "monto": float(p.monto),
                    "metodo": p.metodo,
                    "fecha": p.fecha.strftime('%d/%m/%Y %H:%M') if p.fecha else "—",
                    "comentario": p.comentario,
                    "ticket_data": { # Estructura lista para showTicket
                        "alumno": a.nombre,
                        "grupo": grupo.nombre if grupo else "—",
                        "categoria": grupo.categoria if grupo else "—",
                        "profesor": grupo.profesor.nombre if grupo and grupo.profesor else "—",
                        "monto_pagado": float(p.monto),
                        "metodo": p.metodo,
                        "fecha": p.fecha.strftime('%d/%m/%Y %H:%M') if p.fecha else "—",
                        "horario": grupo.horario if grupo else "—",
                        "dias": grupo.dias if grupo else "—"
                    }
                } for p in mis_pagos]
            })

        return jsonify({
            "grupo_nombre": grupo.nombre if grupo else "",
            "costo_mensual": costo_mensual,
            "periodo": periodo,
            "total_alumnos": len(alumnos),
            "total_pagados": total_pagados_completo,
            "alumnos": result
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500
