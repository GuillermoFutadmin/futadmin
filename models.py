from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from datetime import datetime
from flask import session
from sqlalchemy import or_, and_, distinct
from sqlalchemy.ext.hybrid import hybrid_property

db = SQLAlchemy()
bcrypt = Bcrypt()



class Liga(db.Model):

    __tablename__ = 'ligas'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo_cliente = db.Column(db.String(50)) # 'Dueño de Cancha', 'Árbitro/AC', 'Equipo'
    subdominio = db.Column(db.String(50), unique=True, nullable=True)
    contacto = db.Column(db.String(100))
    activa = db.Column(db.Boolean, default=True)
    fecha_registro = db.Column(db.DateTime, default=datetime.utcnow)
    color = db.Column(db.String(20), default='#00ff88')
    monto_mensual = db.Column(db.Float, default=0.0)
    extra_canchas = db.Column(db.Integer, default=0)
    extra_torneos = db.Column(db.Integer, default=0)

    @property
    def monto_total_mensual(self):
        # Según lo solicitado por el Ing: 290 por sede extra, 85 por liga extra
        pago_extras = (self.extra_canchas or 0) * 290 + (self.extra_torneos or 0) * 85
        return (self.monto_mensual or 0.0) + pago_extras

    def to_dict(self):
        # Estadísticas de registros desde el inicio
        users_count = Usuario.query.filter_by(liga_id=self.id).count()
        canchas_count = Cancha.query.filter_by(liga_id=self.id).count()
        torneos_count = Torneo.query.filter_by(liga_id=self.id).count()
        # Verificar si tiene pagos y obtener el último
        last_payment = PagoCombo.query.filter_by(liga_id=self.id).order_by(PagoCombo.fecha.desc()).first()
        has_payments = last_payment is not None
        
        # Totales para el resumen
        from sqlalchemy import func
        total_acumulado_meses = db.session.query(func.sum(PagoCombo.cantidad_meses)).filter_by(liga_id=self.id).scalar() or 0
        
        # Detalles de entidades
        canchas = Cancha.query.filter_by(liga_id=self.id).all()
        torneos = Torneo.query.filter_by(liga_id=self.id).all()
        teams_count = Equipo.query.filter_by(liga_id=self.id).count()
        players_count = Jugador.query.filter_by(liga_id=self.id).count()
        
        # Determinar paquete basado en el dueño
        owner = Usuario.query.filter_by(liga_id=self.id).filter(Usuario.rol.in_(['dueño_liga', 'super_arbitro', 'equipo'])).first()
        paquete = owner.rol if owner else self.tipo_cliente
        
        # Historial de expansiones
        expansiones = LigaExpansion.query.filter_by(liga_id=self.id).order_by(LigaExpansion.fecha.desc()).all()
        
        return {
            "id": self.id,
            "nombre": self.nombre,
            "tipo_cliente": self.tipo_cliente,
            "subdominio": self.subdominio,
            "contacto": self.contacto,
            "activa": self.activa,
            "color": self.color,
            "monto_mensual": self.monto_mensual,
            "extra_canchas": self.extra_canchas,
            "extra_torneos": self.extra_torneos,
            "monto_total_mensual": self.monto_total_mensual,
            "fecha_registro": self.fecha_registro.strftime('%Y-%m-%d') if self.fecha_registro else None,
            "paquete": paquete,
            "has_payments": has_payments,
            "stats": {
                "usuarios": users_count,
                "canchas": canchas_count,
                "torneos": torneos_count,
                "equipos": teams_count,
                "jugadores": players_count,
                "total_meses_pagados": int(total_acumulado_meses)
            },
            "detalles": {
                "canchas": [c.nombre for c in canchas],
                "torneos": [t.nombre for t in torneos]
            },
            "ultimo_pago": {
                "mes": last_payment.mes_pagado if last_payment else "Sin Pagos",
                "monto": last_payment.monto if last_payment else 0,
                "fecha": last_payment.fecha.strftime('%Y-%m-%d') if last_payment else None
            } if has_payments else None,
            "vencimiento": self.vencimiento_actual,
            "expansiones": [e.to_dict() for e in expansiones]
        }

    @property
    def vencimiento_actual(self):
        # El corte es el día de inscripción
        # Vencimiento = fecha_registro + Sum(meses_pagados)
        from sqlalchemy import func
        total_meses = db.session.query(func.sum(PagoCombo.cantidad_meses)).filter_by(liga_id=self.id).scalar() or 0
        
        if not self.fecha_registro:
            return None
            
        # Lógica nativa para añadir meses sin dateutil
        start_date = self.fecha_registro
        month = start_date.month - 1 + int(total_meses)
        year = start_date.year + month // 12
        month = month % 12 + 1
        # Asegurar día válido (ej: si es 31 y el mes tiene 30)
        import calendar
        last_day = calendar.monthrange(year, month)[1]
        day = min(start_date.day, last_day)
        
        vence = datetime(year, month, day)
        return vence.strftime('%Y-%m-%d')

class Usuario(db.Model):
    __tablename__ = 'usuarios'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128))
    rol = db.Column(db.String(30), nullable=False) # 'admin', 'ejecutivo', 'dueño_liga', 'super_arbitro', 'arbitro', 'entrenador', 'equipo'
    liga_id = db.Column(db.Integer, db.ForeignKey('ligas.id'), nullable=True)
    cancha_id = db.Column(db.Integer, db.ForeignKey('canchas.id'), nullable=True)
    activo = db.Column(db.Boolean, default=True)
    telegram_id = db.Column(db.String(50), unique=True, nullable=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    privacy_accepted = db.Column(db.Boolean, default=False)
    privacy_accepted_at = db.Column(db.DateTime, nullable=True)
    
    liga = db.relationship('Liga', backref='usuarios', lazy=True)
    cancha = db.relationship('Cancha', backref='usuarios_list', lazy=True, foreign_keys=[cancha_id])

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "email": self.email,
            "rol": self.rol,
            "liga_id": self.liga_id,
            "cancha_id": self.cancha_id,
            "activo": self.activo,
            "privacy_accepted": self.privacy_accepted,
            "privacy_accepted_at": self.privacy_accepted_at.strftime('%Y-%m-%d %H:%M') if self.privacy_accepted_at else None,
            "color": self.liga.color if self.liga else (self.cancha.liga.color if self.cancha and self.cancha.liga else "#00ff88")
        }

class Torneo(db.Model):
    __tablename__ = 'torneos'
    id = db.Column(db.Integer, primary_key=True)
    liga_id = db.Column(db.Integer, db.ForeignKey('ligas.id'), nullable=True, index=True)
    nombre = db.Column(db.String(100), nullable=False)
    tipo = db.Column(db.String(50))
    costo_inscripcion = db.Column(db.Float, default=0.0)
    costo_arbitraje = db.Column(db.Float, default=0.0)
    fecha_inicio = db.Column(db.DateTime, default=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)
    archived = db.Column(db.Boolean, default=False)
    imagen_url = db.Column(db.String(255))
    reglamento = db.Column(db.Text)
    clausulas = db.Column(db.Text)
    premios = db.Column(db.Text)
    num_tiempos = db.Column(db.Integer, default=2)
    duracion_tiempo = db.Column(db.Integer, default=20)
    descanso = db.Column(db.Integer, default=10)
    arbitro_id = db.Column(db.Integer, db.ForeignKey('arbitros.id'), nullable=True)
    dias_juego = db.Column(db.String(255))
    horario_juego = db.Column(db.String(100))
    cancha = db.Column(db.String(100))
    formato = db.Column(db.String(50), default="Liga")
    jugadores_totales = db.Column(db.Integer, default=15)
    jugadores_campo = db.Column(db.Integer, default=7)
    
    liga = db.relationship('Liga', backref='torneos_list', lazy=True)
    
    def to_dict(self):
        # Optimización: Reducir round-trips a la BD
        equipo_count = 0
        jugador_count = 0
        tiene_usuario = False
        cancha_municipio = "Tijuana"

        try:
            # Los conteos son necesarios para las tarjetas de liga en el dashboard
            equipo_count = db.session.query(db.func.count(Equipo.id)).filter(Equipo.torneo_id == self.id).scalar() or 0
            
            # Jugadores vía join con equipos del torneo
            jugador_count = db.session.query(db.func.count(Jugador.id))\
                .join(Equipo, Jugador.equipo_id == Equipo.id)\
                .filter(Equipo.torneo_id == self.id).scalar() or 0
            
            # Verificar usuario asociado (solo si hay árbitro)
            if self.arbitro_id and self.responsable:
                email = self.responsable.email
                if email:
                    # Usamos una consulta existencial simple
                    tiene_usuario = db.session.query(Usuario.id).filter(Usuario.email == email).first() is not None
            
            # El municipio de la cancha suele ser estático o ya conocido
            # Para evitar N+1 en canchas por cada torneo, si self.cancha existe, podríamos cachearlo 
            # o simplemente usar un valor por defecto si no es crítico en tiempo real.
        except Exception as e:
            print(f"Error in Torneo.to_dict for ID {self.id}: {e}")

        return {
            "id": self.id,
            "nombre": self.nombre,
            "tipo": self.tipo,
            "costo_inscripcion": float(self.costo_inscripcion or 0),
            "costo_arbitraje": float(self.costo_arbitraje or 0),
            "fecha_inicio": self.fecha_inicio.strftime('%Y-%m-%d') if self.fecha_inicio else None,
            "activo": self.activo,
            "archived": self.archived,
            "imagen_url": self.imagen_url,
            "reglamento": self.reglamento or "",
            "clausulas": self.clausulas or "",
            "premios": self.premios or "",
            "color": self.liga.color if self.liga else "#00ff88",
            "num_tiempos": self.num_tiempos or 2,
            "duracion_tiempo": self.duracion_tiempo or 20,
            "descanso": self.descanso or 10,
            "arbitro_id": self.arbitro_id,
            "dias_juego": self.dias_juego or "",
            "horario_juego": self.horario_juego or "",
            "cancha": self.cancha or "",
            "cancha_municipio": cancha_municipio,
            "formato": self.formato or "Liga",
            "liga_nombre": self.liga.nombre if self.liga else "—",
            "equipos_count": equipo_count,
            "jugadores_count": jugador_count,
            "jugadores_totales": self.jugadores_totales,
            "jugadores_campo": self.jugadores_campo,
            "tiene_usuario": tiene_usuario,
            "stats": {
                "equipos": equipo_count,
                "jugadores": jugador_count
            }
        }

class Equipo(db.Model):
    __tablename__ = 'equipos'
    id = db.Column(db.Integer, primary_key=True)
    liga_id = db.Column(db.Integer, db.ForeignKey('ligas.id'), nullable=True, index=True)
    nombre = db.Column(db.String(100), nullable=False)
    torneo_id = db.Column(db.Integer, db.ForeignKey('torneos.id'), nullable=False)
    uid = db.Column(db.String(20), unique=True, index=True) # ID Único Identitario (12-15 chars)
    escudo_url = db.Column(db.String(255))
    email = db.Column(db.String(100)) # Email del delegado
    colonia = db.Column(db.String(100)) # Ubicación más precisa
    colonia_geojson = db.Column(db.Text) # GeoJSON perimetral
    grupo = db.Column(db.String(50))
    # Estadísticas para arranques de torneos ya iniciados
    puntos_legacy = db.Column(db.Integer, default=0)
    goles_f_legacy = db.Column(db.Integer, default=0)
    goles_c_legacy = db.Column(db.Integer, default=0)
    amarillas_legacy = db.Column(db.Integer, default=0)
    rojas_legacy = db.Column(db.Integer, default=0)
    saldo_arbitraje_legacy = db.Column(db.Float, default=0.0)
    
    jugadores = db.relationship('Jugador', backref='equipo', lazy=True, cascade="all, delete-orphan")
    liga = db.relationship('Liga', backref='equipos_list', lazy=True)
    torneo = db.relationship('Torneo', backref='equipos_rel', lazy=True)
    
    @property
    def color(self):
        """Hereda el color de la liga asociada o del torneo"""
        if self.liga and self.liga.color:
            return self.liga.color
        if self.torneo and self.torneo.liga and self.torneo.liga.color:
            return self.torneo.liga.color
        return "#00ff88" # Verde por defecto

    def to_dict(self, user_rol=None):
        # Optimización: Omitimos el count() pesado aquí para evitar N+1
        jugador_count = 0 
        
        # Clonar datos base
        data = {
            "id": self.id,
            "nombre": self.nombre,
            "torneo_id": self.torneo_id,
            "escudo_url": self.escudo_url,
            "email": self.email or "",
            "colonia": self.colonia or "",
            "colonia_geojson": self.colonia_geojson or "",
            "grupo": self.grupo or "",
            "color": self.color,
            "liga_id": self.liga_id,
            "liga_nombre": self.liga.nombre if self.liga else "—",
            "saldo_arbitraje_legacy": float(self.saldo_arbitraje_legacy or 0.0),
            "tiene_usuario": Usuario.query.filter_by(email=self.email).first() is not None if self.email else False,
            "jugadores_count": jugador_count,
            "stats": {
                "jugadores": jugador_count
            }
        }
        
        # Solo incluir UID si el rol es administrativo (admin, ejecutivo, dueño_liga)
        # Se permite None por compatibilidad (si no se especifica rol, se asume que no tiene acceso por defecto si es consulta general)
        rol = (user_rol or '').lower()
        if rol in ['admin', 'ejecutivo', 'dueño_liga']:
            data["uid"] = self.uid or f"EQ-{self.id:06d}"
            
        return data

class Jugador(db.Model):
    __tablename__ = 'jugadores'
    id = db.Column(db.Integer, primary_key=True)
    liga_id = db.Column(db.Integer, db.ForeignKey('ligas.id'), nullable=True, index=True)
    nombre = db.Column(db.String(100), nullable=False)
    seudonimo = db.Column(db.String(100)) # Reemplaza CURP
    telefono = db.Column(db.String(15))
    posicion = db.Column(db.String(50))
    numero = db.Column(db.Integer)
    fecha_nacimiento = db.Column(db.Date, nullable=True)
    foto_url = db.Column(db.String(255))
    firma_tutor_url = db.Column(db.String(255), nullable=True)  # Firma digital del tutor (solo menores)
    es_portero = db.Column(db.Boolean, default=False)
    es_capitan = db.Column(db.Boolean, default=False)
    equipo_id = db.Column(db.Integer, db.ForeignKey('equipos.id'), nullable=False)
    # Estadísticas para arranques de torneos ya iniciados
    goles_legacy = db.Column(db.Integer, default=0)
    amarillas_legacy = db.Column(db.Integer, default=0)
    rojas_legacy = db.Column(db.Integer, default=0)
    
    liga = db.relationship('Liga', backref='jugadores_list', lazy=True)

    @property
    def color(self):
        """Hereda el color del equipo (que a su vez hereda de la liga)"""
        return self.equipo.color if self.equipo else "#00ff88"

    def to_dict(self):
        # Optimización: El lookup por nombre es muy lento en listas grandes
        tiene_usuario = False 
        return {
            "id": self.id,
            "nombre": self.nombre,
            "seudonimo": self.seudonimo or "",
            "telefono": self.telefono or "",
            "posicion": self.posicion or "",
            "numero": self.numero,
            "fecha_nacimiento": self.fecha_nacimiento.strftime('%Y-%m-%d') if self.fecha_nacimiento else "",
            "foto_url": self.foto_url or "",
            "firma_tutor_url": self.firma_tutor_url or "",
            "es_portero": self.es_portero,
            "es_capitan": self.es_capitan,
            "equipo_id": self.equipo_id,
            "equipo_nombre": self.equipo.nombre if self.equipo else "—",
            "liga_id": self.liga_id,
            "liga_nombre": self.liga.nombre if self.liga else "—",
            "color": self.color,
            "tiene_usuario": tiene_usuario
        }

class Inscripcion(db.Model):
    __tablename__ = 'inscripciones'
    id = db.Column(db.Integer, primary_key=True)
    torneo_id = db.Column(db.Integer, db.ForeignKey('torneos.id'), nullable=False)
    equipo_id = db.Column(db.Integer, db.ForeignKey('equipos.id'), nullable=False)
    monto_pactado_inscripcion = db.Column(db.Float, default=0.0)
    liga_id = db.Column(db.Integer, db.ForeignKey('ligas.id'), nullable=True, index=True)
    
    @hybrid_property
    def saldo_pendiente(self):
        # Calcular el saldo basado en el monto pactado menos lo pagado
        total_pagado = sum(p.monto for p in self.pagos)
        return self.monto_pactado_inscripcion - total_pagado

    @saldo_pendiente.expression
    def saldo_pendiente(cls):
        # Versión para SQL (para que .filter() funcione)
        from sqlalchemy import func
        from models import Pago
        # Subquery para sumar pagos de esta inscripción
        pagos_subquery = db.session.query(
            func.coalesce(func.sum(Pago.monto), 0)
        ).filter(Pago.inscripcion_id == cls.id).correlate(cls).as_scalar()
        
        return cls.monto_pactado_inscripcion - pagos_subquery

    def to_dict(self):
        return {
            "id": self.id,
            "torneo_id": self.torneo_id,
            "equipo_id": self.equipo_id,
            "monto_pactado_inscripcion": float(self.monto_pactado_inscripcion or 0),
            "saldo_pendiente": float(self.saldo_pendiente),
            "liga_id": self.liga_id
        }
    
    torneo = db.relationship('Torneo', backref='inscripciones_rel', lazy=True)
    equipo = db.relationship('Equipo', backref=db.backref('inscripciones_rel', cascade="all, delete-orphan"), lazy=True)
    pagos = db.relationship('Pago', backref='inscripcion', lazy=True, cascade="all, delete-orphan")

class Pago(db.Model):
    __tablename__ = 'pagos'
    id = db.Column(db.Integer, primary_key=True)
    inscripcion_id = db.Column(db.Integer, db.ForeignKey('inscripciones.id'), nullable=True)
    monto = db.Column(db.Float, nullable=False)
    tipo = db.Column(db.String(50), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    metodo = db.Column(db.String(50))
    comentario = db.Column(db.String(255))
    partido_id = db.Column(db.Integer, db.ForeignKey('partidos.id'), nullable=True)
    torneo_id = db.Column(db.Integer, db.ForeignKey('torneos.id'), nullable=True, index=True)
    alumno_id = db.Column(db.Integer, db.ForeignKey('alumnos_entrenamiento.id'), nullable=True)
    liga_id = db.Column(db.Integer, db.ForeignKey('ligas.id'), nullable=True, index=True)

class GrupoEntrenamiento(db.Model):
    __tablename__ = 'grupos_entrenamiento'
    id = db.Column(db.Integer, primary_key=True)
    liga_id = db.Column(db.Integer, db.ForeignKey('ligas.id'), nullable=True, index=True)
    nombre = db.Column(db.String(100), nullable=False)
    profesor_id = db.Column(db.Integer, db.ForeignKey('arbitros.id', ondelete='SET NULL'), nullable=True)
    dias = db.Column(db.String(100))
    horario = db.Column(db.String(100))
    costo_mensual = db.Column(db.Float, default=0.0)
    tipo = db.Column(db.String(50))
    categoria = db.Column(db.String(50))
    fecha_inicio = db.Column(db.Date, nullable=True)
    fecha_fin = db.Column(db.Date, nullable=True)
    cancha = db.Column(db.String(100))
    capacidad = db.Column(db.Integer)
    costo_inscripcion = db.Column(db.Float, default=0.0)
    foto_url = db.Column(db.String(255), nullable=True)
    activo = db.Column(db.Boolean, default=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    profesor = db.relationship('Arbitro', backref='grupos', lazy=True)
    alumnos = db.relationship('AlumnoEntrenamiento', backref='grupo', lazy=True, cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "profesor_id": self.profesor_id,
            "profesor_nombre": self.profesor.nombre if self.profesor else "Sin asignar",
            "dias": self.dias or "",
            "horario": self.horario or "",
            "costo_mensual": float(self.costo_mensual or 0),
            "tipo": self.tipo or "",
            "categoria": self.categoria or "",
            "fecha_inicio": self.fecha_inicio.strftime('%Y-%m-%d') if self.fecha_inicio else "",
            "fecha_fin": self.fecha_fin.strftime('%Y-%m-%d') if self.fecha_fin else "",
            "cancha": self.cancha or "",
            "capacidad": self.capacidad or 0,
            "costo_inscripcion": float(self.costo_inscripcion or 0),
            "foto_url": self.foto_url or "",
            "activo": self.activo,
            "alumnos_count": AlumnoEntrenamiento.query.filter_by(grupo_id=self.id).count()
        }

class AlumnoEntrenamiento(db.Model):
    __tablename__ = 'alumnos_entrenamiento'
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False)
    grupo_id = db.Column(db.Integer, db.ForeignKey('grupos_entrenamiento.id'), nullable=False)
    fecha_nacimiento = db.Column(db.Date, nullable=True)
    telefono_contacto = db.Column(db.String(20), nullable=True)
    nombre_tutor = db.Column(db.String(100), nullable=True)
    activo = db.Column(db.Boolean, default=True)
    fecha_inscripcion = db.Column(db.DateTime, default=datetime.utcnow)
    foto_url = db.Column(db.String(255), nullable=True)
    liga_id = db.Column(db.Integer, db.ForeignKey('ligas.id'), nullable=True, index=True)
    
    pagos_mensualidad = db.relationship('Pago', backref='alumno', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "grupo_id": self.grupo_id,
            "fecha_nacimiento": self.fecha_nacimiento.strftime('%Y-%m-%d') if self.fecha_nacimiento else "",
            "telefono_contacto": self.telefono_contacto or "",
            "nombre_tutor": self.nombre_tutor or "",
            "activo": self.activo,
            "fecha_inscripcion": self.fecha_inscripcion.strftime('%Y-%m-%d') if self.fecha_inscripcion else "",
            "foto_url": self.foto_url or "",
            "liga_id": self.liga_id
        }

class Partido(db.Model):
    __tablename__ = 'partidos'
    id = db.Column(db.Integer, primary_key=True)
    liga_id = db.Column(db.Integer, db.ForeignKey('ligas.id'), nullable=True, index=True)
    torneo_id = db.Column(db.Integer, db.ForeignKey('torneos.id'), nullable=False)
    jornada = db.Column(db.Integer, nullable=False, default=1)
    equipo_local_id = db.Column(db.Integer, db.ForeignKey('equipos.id'), nullable=False)
    equipo_visitante_id = db.Column(db.Integer, db.ForeignKey('equipos.id'), nullable=False)
    arbitro_id = db.Column(db.Integer, db.ForeignKey('arbitros.id'), nullable=True)
    fecha = db.Column(db.Date, nullable=True)
    hora = db.Column(db.String(10), nullable=True)
    cancha = db.Column(db.String(100), nullable=True)
    goles_local = db.Column(db.Integer, nullable=True)
    goles_visitante = db.Column(db.Integer, nullable=True)
    estado = db.Column(db.String(20), default='Scheduled')
    fase = db.Column(db.String(50), default='Regular')
    penales_local = db.Column(db.Integer, nullable=True)
    penales_visitante = db.Column(db.Integer, nullable=True)
    ganador_id = db.Column(db.Integer, db.ForeignKey('equipos.id'), nullable=True)
    timer_started_at = db.Column(db.BigInteger, nullable=True)  # Unix ms when timer started
    tiempo_corrido_segundos = db.Column(db.Integer, default=0)  # Acumulado al hacer pausa/medio tiempo
    periodo_actual = db.Column(db.Integer, default=1)  # 1 = primer tiempo, 2 = segundo tiempo
    
    torneo = db.relationship('Torneo', backref='partidos', lazy=True)
    equipo_local = db.relationship('Equipo', foreign_keys=[equipo_local_id], lazy=True)
    equipo_visitante = db.relationship('Equipo', foreign_keys=[equipo_visitante_id], lazy=True)
    arbitro = db.relationship('Arbitro', backref=db.backref('partidos_rel', lazy=True), lazy=True)

    def to_dict(self):
        t = self.torneo
        return {
            "id": self.id,
            "liga_id": self.liga_id,
            "torneo_id": self.torneo_id,
            "torneo_name": t.nombre if t else "",
            "jornada": self.jornada,
            "equipo_local_id": self.equipo_local_id,
            "equipo_visitante_id": self.equipo_visitante_id,
            "equipo_local": self.equipo_local.nombre if self.equipo_local else "—",
            "equipo_visitante": self.equipo_visitante.nombre if self.equipo_visitante else "—",
            "equipo_local_escudo": self.equipo_local.escudo_url if self.equipo_local else "",
            "equipo_visitante_escudo": self.equipo_visitante.escudo_url if self.equipo_visitante else "",
            "arbitro_id": self.arbitro_id,
            "arbitro": self.arbitro.nombre if self.arbitro else "",
            "arbitro_nombre": self.arbitro.nombre if self.arbitro else "POR ASIGNAR",
            "fecha": self.fecha.strftime('%Y-%m-%d') if self.fecha else "",
            "hora": self.hora or "",
            "cancha": self.cancha or "",
            "goles_local": self.goles_local if self.goles_local is not None else 0,
            "goles_visitante": self.goles_visitante if self.goles_visitante is not None else 0,
            "estado": self.estado or "Scheduled",
            "fase": self.fase or "Regular",
            "penales_local": self.penales_local,
            "penales_visitante": self.penales_visitante,
            "ganador_id": self.ganador_id,
            # Torneo timing settings
            "duracion_tiempo": t.duracion_tiempo if t else 20,
            "descanso": t.descanso if t else 10,
            "num_tiempos": t.num_tiempos if t else 2,
            "costo_arbitraje": t.costo_arbitraje if t else 0,
            # Server-side timer
            "timer_started_at": self.timer_started_at,
            "tiempo_corrido_segundos": self.tiempo_corrido_segundos or 0,
            "periodo_actual": self.periodo_actual or 1,
        }


class Arbitro(db.Model):
    __tablename__ = 'arbitros'
    id = db.Column(db.Integer, primary_key=True)
    liga_id = db.Column(db.Integer, db.ForeignKey('ligas.id'), nullable=True, index=True)
    nombre = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100))
    telefono = db.Column(db.String(15))
    nivel = db.Column(db.String(50))
    foto_url = db.Column(db.String(255))
    activo = db.Column(db.Boolean, default=True)
    telegram_id = db.Column(db.String(50), unique=True, nullable=True)
    password = db.Column(db.String(100), nullable=True)
    cancha_id = db.Column(db.Integer, db.ForeignKey('canchas.id'), nullable=True)

    liga = db.relationship('Liga', backref='arbitros_list', lazy=True)
    cancha_rel = db.relationship('Cancha', backref='arbitros_rel', lazy=True)

    def to_dict(self):
        tiene_usuario = Usuario.query.filter_by(email=self.email).first() is not None if self.email else False
        return {
            "id": self.id,
            "nombre": self.nombre,
            "email": self.email or "",
            "telefono": self.telefono or "",
            "nivel": self.nivel or "",
            "foto_url": self.foto_url or "",
            "activo": self.activo,
            "telegram_id": self.telegram_id,
            "password": self.password or "",
            "liga_id": self.liga_id,
            "liga_nombre": self.liga.nombre if self.liga else "Independiente",
            "liga_color": self.liga.color if self.liga else "#00ff88",
            "tiene_usuario": tiene_usuario
        }

class EventoPartido(db.Model):
    __tablename__ = 'eventos_partido'
    id = db.Column(db.Integer, primary_key=True)
    liga_id = db.Column(db.Integer, db.ForeignKey('ligas.id'), nullable=True, index=True)
    partido_id = db.Column(db.Integer, db.ForeignKey('partidos.id'), nullable=False)
    equipo_id = db.Column(db.Integer, db.ForeignKey('equipos.id'), nullable=True)
    jugador_id = db.Column(db.Integer, db.ForeignKey('jugadores.id'), nullable=True)
    minuto = db.Column(db.Integer)
    tipo = db.Column(db.String(50))
    periodo = db.Column(db.Integer, default=1)
    nota = db.Column(db.Text, nullable=True)
    fecha_creacion = db.Column(db.DateTime, default=datetime.utcnow)
    
    partido = db.relationship('Partido', backref=db.backref('eventos_rel', lazy=True), lazy=True)
    equipo = db.relationship('Equipo', lazy=True)
    jugador = db.relationship('Jugador', lazy=True)

    def to_dict(self):
        return {
            "id": self.id,
            "partido_id": self.partido_id,
            "equipo_id": self.equipo_id,
            "jugador_id": self.jugador_id,
            "minuto": self.minuto,
            "tipo": self.tipo,
            "periodo": self.periodo,
            "nota": self.nota or ""
        }

class AsistenciaPartido(db.Model):
    __tablename__ = 'asistencias_partido'
    id = db.Column(db.Integer, primary_key=True)
    liga_id = db.Column(db.Integer, db.ForeignKey('ligas.id'), nullable=True, index=True)
    partido_id = db.Column(db.Integer, db.ForeignKey('partidos.id'), nullable=False)
    jugador_id = db.Column(db.Integer, db.ForeignKey('jugadores.id'), nullable=False)
    equipo_id = db.Column(db.Integer, db.ForeignKey('equipos.id'), nullable=False)
    presente = db.Column(db.Boolean, default=False)

class Cancha(db.Model):
    __tablename__ = 'canchas'
    id = db.Column(db.Integer, primary_key=True)
    liga_id = db.Column(db.Integer, db.ForeignKey('ligas.id'), nullable=True, index=True)
    nombre = db.Column(db.String(100), nullable=False)
    encargado = db.Column(db.String(100))
    email_encargado = db.Column(db.String(100))
    telefono_encargado = db.Column(db.String(20))
    tipo = db.Column(db.String(50), default='Gratuita') # 'Rentada', 'Propia', 'Gratuita'
    costo_renta = db.Column(db.Float, default=0.0)
    unidad_cobro = db.Column(db.String(50), default='Partido') # 'Partido', 'Hora', 'Día'
    direccion = db.Column(db.String(255))
    estado = db.Column(db.String(100))
    municipio = db.Column(db.String(100))
    notas = db.Column(db.Text)
    foto_url = db.Column(db.String(255))
    modalidad = db.Column(db.String(50), default='Fútbol 7')
    fecha_afiliacion = db.Column(db.DateTime, default=datetime.utcnow)
    activo = db.Column(db.Boolean, default=True)
    dueno_id = db.Column(db.Integer, db.ForeignKey('usuarios.id'), nullable=True)

    liga = db.relationship('Liga', backref='canchas_list', lazy=True)

    def to_dict(self):
        try:
            # Estadísticas extendidas
            nombre_clean = self.nombre.strip() if self.nombre else ""
            
            # Torneos: Vinculación robusta por nombre e ID de liga
            torneos = Torneo.query.filter(
                Torneo.cancha.ilike(nombre_clean), 
                Torneo.activo == True,
                Torneo.liga_id == self.liga_id
            ).all()
            torneos_nombres = [t.nombre for t in torneos]
            
            grupos = GrupoEntrenamiento.query.filter(
                GrupoEntrenamiento.cancha.ilike(nombre_clean),
                GrupoEntrenamiento.liga_id == self.liga_id
            ).all()
            grupos_nombres = [g.nombre for g in grupos]
            
            tiene_usuario = Usuario.query.filter_by(email=self.email_encargado).first() is not None if self.email_encargado else False
            
            torneos_ids = [t.id for t in torneos]
            
            # Partidos: De los torneos asociados Y de la liga actual
            partidos_query = Partido.query.filter(
                Partido.liga_id == self.liga_id,
                or_(
                    Partido.torneo_id.in_(torneos_ids) if torneos_ids else False,
                    Partido.cancha.ilike(nombre_clean)
                )
            )
            partidos_count = partidos_query.count()
            
            # Jugadores: Total de jugadores en los equipos de los torneos de esta sede (filtrado por liga)
            jugadores_count = 0
            if torneos_ids:
                jugadores_count = db.session.query(db.func.count(distinct(Jugador.id))).\
                    join(Equipo).\
                    filter(Equipo.torneo_id.in_(torneos_ids), Equipo.liga_id == self.liga_id).scalar() or 0
            
            # Ligas asociadas (en el contexto de combo es 1, pero se mantiene lógica para super-arbitro si aplica)
            ligas_count = 1 if self.liga_id else 0

            # Equipos únicos de esta liga en esta sede
            equipos_count = 0
            if torneos_ids:
                equipos_count = Equipo.query.filter(Equipo.torneo_id.in_(torneos_ids), Equipo.liga_id == self.liga_id).count()

            # Árbitros asociados estrictamente a esta LIGA y Sede
            # Un árbitro de la Liga A no debe contarse en la Liga B aunque se llame igual la sede.
            arbitros_ids = set([a.id for a in self.arbitros_rel if a.liga_id == self.liga_id])
            
            # Inyectar árbitros vinculados a los torneos de esta liga
            torneos_arb_ids = [t.arbitro_id for t in torneos if t.arbitro_id and t.liga_id == self.liga_id]
            arbitros_ids.update(torneos_arb_ids)
            
            # Árbitros de los partidos de esta liga
            partidos_arb_ids = [p.arbitro_id for p in partidos_query.all() if p.arbitro_id and p.liga_id == self.liga_id]
            arbitros_ids.update(partidos_arb_ids)
            
            arbitros_asociados = []
            if arbitros_ids:
                arbitros_asociados = [a.nombre for a in Arbitro.query.filter(Arbitro.id.in_(list(arbitros_ids)), Arbitro.liga_id == self.liga_id).all()]
            
            # Obtener todos los usuarios asociados a esta sede (SOLO SI PERTENECEN A ESTA LIGA)
            usuarios_query = Usuario.query.filter(
                Usuario.liga_id == self.liga_id,
                or_(
                    Usuario.cancha_id == self.id,
                    Usuario.cancha_id == None
                )
            ).filter(~Usuario.rol.in_(['admin', 'ejecutivo'])).all()
            
        except Exception as e:
            print(f"Error in Cancha.to_dict: {e}")
            torneos_nombres = []
            grupos_nombres = []
            tiene_usuario = False
            partidos_count = 0
            jugadores_count = 0
            ligas_count = 0
            equipos_count = 0
            arbitros_asociados = []
            usuarios_query = []

        return {
            "id": self.id,
            "nombre": self.nombre,
            "encargado": self.encargado or "",
            "email_encargado": self.email_encargado or "",
            "telefono_encargado": self.telefono_encargado or "",
            "tipo": self.tipo or "Gratuita",
            "costo_renta": float(self.costo_renta or 0),
            "unidad_cobro": self.unidad_cobro or "Partido",
            "direccion": self.direccion or "",
            "estado": self.estado or "",
            "municipio": self.municipio or "",
            "notas": self.notas or "",
            "foto_url": self.foto_url or "",
            "modalidad": self.modalidad or "Fútbol 7",
            "fecha_afiliacion": self.fecha_afiliacion.strftime('%Y-%m-%d') if self.fecha_afiliacion else "",
            "activo": self.activo,
            "torneos_asociados": torneos_nombres,
            "grupos_asociados": grupos_nombres,
            "tiene_usuario": tiene_usuario,
            "color": self.liga.color if self.liga else "#00ff88",
            "liga_id": self.liga_id,
            "partidos_count": partidos_count,
            "jugadores_count": jugadores_count,
            "ligas_count": ligas_count,
            "equipos_count": equipos_count,
            "arbitros": arbitros_asociados,
            "usuarios": [u.to_dict() for u in usuarios_query] if 'usuarios_query' in locals() else []
        }

class PagoCancha(db.Model):
    __tablename__ = 'pagos_canchas'
    id = db.Column(db.Integer, primary_key=True)
    liga_id = db.Column(db.Integer, db.ForeignKey('ligas.id'), nullable=True, index=True)
    cancha_id = db.Column(db.Integer, db.ForeignKey('canchas.id'), nullable=False)
    monto = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    comprobante_url = db.Column(db.String(255))
    notas = db.Column(db.Text)
    
    cancha = db.relationship('Cancha', backref=db.backref('pagos_recibidos', cascade="all, delete-orphan", lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "cancha_id": self.cancha_id,
            "cancha_nombre": self.cancha.nombre if self.cancha else "",
            "monto": float(self.monto or 0),
            "fecha": self.fecha.strftime('%Y-%m-%d %H:%M') if self.fecha else None,
            "comprobante_url": self.comprobante_url or "",
            "notas": self.notas or ""
        }

class PagoCombo(db.Model):
    __tablename__ = 'pagos_combos'
    id = db.Column(db.Integer, primary_key=True)
    liga_id = db.Column(db.Integer, db.ForeignKey('ligas.id'), nullable=False, index=True)
    monto = db.Column(db.Float, nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    metodo = db.Column(db.String(50)) # 'Transferencia', 'Efectivo', 'Tarjeta'
    comprobante_url = db.Column(db.String(255))
    notas = db.Column(db.Text)
    mes_pagado = db.Column(db.String(100)) # Ej: 'Marzo 2024'
    cantidad_meses = db.Column(db.Integer, default=1)
    
    liga = db.relationship('Liga', backref=db.backref('pagos_suscripcion', cascade="all, delete-orphan", lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "liga_id": self.liga_id,
            "liga_nombre": self.liga.nombre if self.liga else "Desconocida",
            "monto": float(self.monto or 0),
            "fecha": self.fecha.strftime('%Y-%m-%d'),
            "metodo": self.metodo or "No especificado",
            "comprobante_url": self.comprobante_url or "",
            "notas": self.notas or "",
            "mes_pagado": self.mes_pagado or "",
            "cantidad_meses": self.cantidad_meses or 1
        }

class LigaExpansion(db.Model):
    __tablename__ = 'ligas_expansiones'
    id = db.Column(db.Integer, primary_key=True)
    liga_id = db.Column(db.Integer, db.ForeignKey('ligas.id'), nullable=False, index=True)
    tipo = db.Column(db.String(50)) # 'extra_canchas' o 'extra_torneos'
    cantidad = db.Column(db.Integer)
    monto_adicional = db.Column(db.Float)
    fecha = db.Column(db.DateTime, default=datetime.utcnow)
    
    liga = db.relationship('Liga', backref=db.backref('expansiones_rel', cascade="all, delete-orphan", lazy=True))

    def to_dict(self):
        return {
            "id": self.id,
            "tipo": self.tipo,
            "cantidad": self.cantidad,
            "monto_adicional": self.monto_adicional,
            "fecha": self.fecha.strftime('%Y-%m-%d %H:%M')
        }

class Configuracion(db.Model):
    __tablename__ = 'configuracion'
    clave = db.Column(db.String(50), primary_key=True)
    valor = db.Column(db.Text)
    ultima_actualizacion = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "clave": self.clave,
            "valor": self.valor,
            "ultima_actualizacion": self.ultima_actualizacion.strftime('%Y-%m-%d %H:%M') if self.ultima_actualizacion else None
        }

# --- Funciones Auxiliares (definidas al final para asegurar carga de modelos) ---

def get_liga_id():
    """Retorna el liga_id de la sesión o None si es admin/global."""
    rol = str(session.get('user_rol') or '').lower()
    if rol in ['admin', 'ejecutivo']:
        return None
    val = session.get('liga_id')
    try:
        return int(val) if val is not None else None
    except (ValueError, TypeError):
        return None

def apply_liga_filter(query, model, ignore_archived=False):
    """Aplica el filtro de liga_id o cancha_id si corresponde con blindaje por liga."""
    l_id = get_liga_id()
    c_id = session.get('cancha_id')
    c_nombre = session.get('cancha_nombre')
    rol = str(session.get('user_rol') or '').lower()
    
    # 1. EL FILTRO DE LIGA ES MANDATORIO PARA SEGURIDAD (Excepto Admins)
    if l_id and rol not in ['admin', 'ejecutivo']:
        query = query.filter(model.liga_id == l_id)
    
    # 1.5 FILTRO DE ARCHIVADO (Solo para Torneos)
    if model.__tablename__ == 'torneos' and not ignore_archived:
        # Por defecto no mostramos los archivados en la app normal (incluyendo los que tienen NULL por la migración reciente)
        query = query.filter(or_(model.archived == False, model.archived == None))
    
    # 2. FILTRO DE SEDE ES RESTRICTIVO (Para perfiles locales)
    # Si el usuario es 'arbitro', 'entrenador' o no es nivel liga, debe estar limitado a su sede.
    if c_id and rol not in ['admin', 'ejecutivo', 'dueño_liga', 'super_arbitro']:
        if model.__tablename__ == 'canchas':
            query = query.filter(model.id == c_id)
        elif model.__tablename__ == 'torneos':
            query = query.filter(model.cancha == c_nombre)
        elif model.__tablename__ == 'equipos':
            query = query.filter(model.torneo_id.in_(
                db.session.query(Torneo.id).filter(Torneo.cancha == c_nombre, Torneo.liga_id == l_id)
            ))
        elif model.__tablename__ == 'jugadores':
            query = query.filter(model.equipo_id.in_(
                db.session.query(Equipo.id).join(Torneo).filter(Torneo.cancha == c_nombre, Torneo.liga_id == l_id)
            ))
        elif model.__tablename__ == 'alumnos_entrenamiento':
            query = query.filter(model.grupo_id.in_(
                db.session.query(GrupoEntrenamiento.id).filter(GrupoEntrenamiento.cancha == c_nombre, GrupoEntrenamiento.liga_id == l_id)
            ))
        elif model.__tablename__ == 'inscripciones':
            query = query.filter(model.torneo_id.in_(
                db.session.query(Torneo.id).filter(Torneo.cancha == c_nombre, Torneo.liga_id == l_id)
            ))
        elif model.__tablename__ == 'partidos':
            query = query.filter(or_(
                model.torneo_id.in_(db.session.query(Torneo.id).filter(Torneo.cancha == c_nombre, Torneo.liga_id == l_id)),
                and_(model.cancha == c_nombre, model.liga_id == (l_id or model.liga_id))
            ))
        elif model.__tablename__ == 'grupos_entrenamiento':
            query = query.filter(model.cancha == c_nombre)
        elif model.__tablename__ == 'arbitros':
            query = query.filter(model.cancha_id == c_id)
            
    return query

def get_role_limits(rol):
    """Retorna los límites permitidos para cada rol según el plan de suscripción."""
    rol = str(rol or '').strip().lower().replace('ñ', 'n')
    limits = {
        'admin': {'users': 99999, 'canchas': 99999, 'torneos': 99999},
        'ejecutivo': {'users': 99999, 'canchas': 99999, 'torneos': 99999},
        'dueno_liga': {'users': 4, 'canchas': 1, 'torneos': 5},
        'dueño_liga': {'users': 4, 'canchas': 1, 'torneos': 5},
        'super_arbitro': {'users': 4, 'canchas': 1, 'torneos': 2},
        'equipo': {'users': 4, 'canchas': 1, 'torneos': 1},
        'arbitro': {'users': 0, 'canchas': 0, 'torneos': 0},
        'entrenador': {'users': 0, 'canchas': 0, 'torneos': 0},
        'resultados': {'users': 0, 'canchas': 0, 'torneos': 0},
        'dueno_cancha': {'users': 0, 'canchas': 0, 'torneos': 0}
    }
    return limits.get(rol, {'users': 0, 'canchas': 0, 'torneos': 0})

def check_canchas_limit(liga_id, rol):
    """Verifica si el rol puede crear más canchas."""
    limits = get_role_limits(rol)
    if 'canchas' not in limits: return True
    
    # Sumar canchas extra permitidas para esta liga
    extra = 0
    if liga_id:
        liga = Liga.query.get(liga_id)
        if liga: extra = liga.extra_canchas or 0

    max_val = limits['canchas'] + extra
    current_count = Cancha.query.filter_by(liga_id=liga_id).count()
    if current_count >= max_val:
        return False, f"Límite alcanzado: Tu plan permite {max_val} sede(s). (Base: {limits['canchas']} + Extra: {extra})"
    return True, ""

def check_torneos_limit(liga_id, rol):
    """Verifica si el rol puede crear más torneos."""
    limits = get_role_limits(rol)
    
    # Sumar torneos extra permitidos para esta liga
    extra = 0
    if liga_id:
        liga = Liga.query.get(liga_id)
        if liga: extra = liga.extra_torneos or 0

    if 'torneos' in limits:
        max_torneos = limits['torneos'] + extra
    elif 'torneos_per_cancha' in limits:
        num_canchas = Cancha.query.filter_by(liga_id=liga_id).count()
        max_torneos = (num_canchas * limits['torneos_per_cancha']) + extra
        if max_torneos == 0: max_torneos = limits['torneos_per_cancha'] + extra
    else:
        return True, ""

    current_count = Torneo.query.filter_by(liga_id=liga_id, archived=False).count()
    if current_count >= max_torneos:
        return False, f"Límite alcanzado: Tu plan permite {max_torneos} torneo(s). (Base: {max_torneos - extra} + Extra: {extra})"
    return True, ""

def check_users_limit(liga_id, rol):
    """Verifica si el rol puede crear más usuarios vinculados a su liga."""
    limits = get_role_limits(rol)
    if 'users' not in limits: return True
    
    current_count = Usuario.query.filter_by(liga_id=liga_id).count()
    if current_count >= limits['users']:
        return False, f"Límite alcanzado: Tu plan permite hasta {limits['users']} usuarios vinculados."
    return True, ""
