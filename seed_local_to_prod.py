from app import app
from models import db, Usuario, Cancha, Liga, Arbitro, Torneo, Equipo, Jugador
import datetime
import json
def inject_local_data():
    with app.app_context():
        print('--- Vaciando tablas previas (TRUNCATE) ---')
        if 'postgresql' in db.engine.url.drivername:
            tables = ', '.join([m.__tablename__ for m in [Liga, Usuario, Cancha, Arbitro, Torneo, Equipo, Jugador]])
            db.session.execute(db.text(f'TRUNCATE TABLE {tables} CASCADE'))
            db.session.commit()
        with db.session.no_autoflush:
            print('--- Insertando ligas ---')
            if not Liga.query.get(9):
                obj = Liga(id=9, nombre='Deportivo Cu', tipo_cliente='', subdominio=None, contacto='', activa=True, fecha_registro=datetime.datetime.strptime('2026-03-15 08:09:38', '%Y-%m-%d %H:%M:%S'), color='#c9e637', monto_mensual=150.0, extra_canchas=0, extra_torneos=0)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Liga.query.get(10):
                obj = Liga(id=10, nombre='Test Liga', tipo_cliente=None, subdominio=None, contacto=None, activa=True, fecha_registro=datetime.datetime.strptime('2026-03-17 19:26:39', '%Y-%m-%d %H:%M:%S'), color='#00ff88', monto_mensual=0.0, extra_canchas=0, extra_torneos=0)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Liga.query.get(11):
                obj = Liga(id=11, nombre='Test Liga', tipo_cliente=None, subdominio=None, contacto=None, activa=True, fecha_registro=datetime.datetime.strptime('2026-03-17 19:26:39', '%Y-%m-%d %H:%M:%S'), color='#00ff88', monto_mensual=0.0, extra_canchas=0, extra_torneos=0)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Liga.query.get(8):
                obj = Liga(id=8, nombre='Liga Cumbres', tipo_cliente='', subdominio=None, contacto='', activa=True, fecha_registro=datetime.datetime.strptime('2026-03-13 20:43:37', '%Y-%m-%d %H:%M:%S'), color='#7370a4', monto_mensual=350.0, extra_canchas=0, extra_torneos=0)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            db.session.commit()
            print('--- Insertando usuarios ---')
            if not Usuario.query.get(37):
                obj = Usuario(id=37, nombre='Árbitro Gral A - Deportivo Cu', email='arbitro_a_deportivocu@futadmin.com', password_hash='$2b$12$V.pbNE2qudQ2TDjXFzJOw.cERgnP33vbkbd.8DICfN0tqqkYKqc0m', rol='entrenador', liga_id=9, cancha_id=None, activo=True, fecha_creacion=datetime.datetime.strptime('2026-03-15 08:09:38', '%Y-%m-%d %H:%M:%S'), privacy_accepted=False, privacy_accepted_at=None)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Usuario.query.get(36):
                obj = Usuario(id=36, nombre='EUSTAQUIO DIAZ', email='Eustaquio@futadmin.com', password_hash='$2b$12$V.pbNE2qudQ2TDjXFzJOw.cERgnP33vbkbd.8DICfN0tqqkYKqc0m', rol='super_arbitro', liga_id=9, cancha_id=None, activo=True, fecha_creacion=datetime.datetime.strptime('2026-03-15 08:09:38', '%Y-%m-%d %H:%M:%S'), privacy_accepted=True, privacy_accepted_at=datetime.datetime.strptime('2026-03-17 05:02:20', '%Y-%m-%d %H:%M:%S'))
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Usuario.query.get(35):
                obj = Usuario(id=35, nombre='Equipo Gral - Liga Cumbres', email='equipo_ligacumbres@futadmin.com', password_hash='$2b$12$QHCITaxUOi.tijdr2kmi9urht5j0Sm5olZlsqfI3N7J5.lZ4UFIx6', rol='resultados', liga_id=8, cancha_id=None, activo=True, fecha_creacion=datetime.datetime.strptime('2026-03-13 20:43:38', '%Y-%m-%d %H:%M:%S'), privacy_accepted=True, privacy_accepted_at=datetime.datetime.strptime('2026-03-17 21:37:49', '%Y-%m-%d %H:%M:%S'))
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Usuario.query.get(33):
                obj = Usuario(id=33, nombre='Árbitro Gral A - Liga Cumbres', email='arbitro_a_ligacumbres@futadmin.com', password_hash='$2b$12$.56JWCmNNWy4SKpyE4hOvehSFfF6KoohlrONzyVahNWcswFdzl0Le', rol='arbitro', liga_id=8, cancha_id=None, activo=True, fecha_creacion=datetime.datetime.strptime('2026-03-13 20:43:38', '%Y-%m-%d %H:%M:%S'), privacy_accepted=True, privacy_accepted_at=datetime.datetime.strptime('2026-03-17 21:38:50', '%Y-%m-%d %H:%M:%S'))
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Usuario.query.get(32):
                obj = Usuario(id=32, nombre='Guillermo Diaz Flores', email='Gdiaz@futadmin.com', password_hash='$2b$12$.56JWCmNNWy4SKpyE4hOvehSFfF6KoohlrONzyVahNWcswFdzl0Le', rol='dueño_liga', liga_id=8, cancha_id=None, activo=True, fecha_creacion=datetime.datetime.strptime('2026-03-13 20:43:38', '%Y-%m-%d %H:%M:%S'), privacy_accepted=True, privacy_accepted_at=datetime.datetime.strptime('2026-03-17 21:56:43', '%Y-%m-%d %H:%M:%S'))
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Usuario.query.get(1):
                obj = Usuario(id=1, nombre='Administrador Sistema', email='admin@futadmin.com', password_hash='$2b$12$SJYe2Zjouavzmvs78kQlP./OyscR8Ce2Qgu2DG/YQOZA1hsu.qOYW', rol='admin', liga_id=None, cancha_id=None, activo=True, fecha_creacion=datetime.datetime.strptime('2026-03-10 20:22:22', '%Y-%m-%d %H:%M:%S'), privacy_accepted=True, privacy_accepted_at=datetime.datetime.strptime('2026-03-18 21:52:49', '%Y-%m-%d %H:%M:%S'))
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Usuario.query.get(40):
                obj = Usuario(id=40, nombre='Administrador Global', email='admin@adminfutbol.com', password_hash='$2b$12$4.dOn8wGL5NntJklkUY4POb.tojcv6tRK4qvdc5yjyw9TAAqOE/c6', rol='admin', liga_id=None, cancha_id=None, activo=True, fecha_creacion=datetime.datetime.strptime('2026-03-19 10:03:11', '%Y-%m-%d %H:%M:%S'), privacy_accepted=False, privacy_accepted_at=None)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Usuario.query.get(14):
                obj = Usuario(id=14, nombre='Omem Zaid ', email='a@a.com', password_hash='$2b$12$.9eZQRt5thlwxtLeASBlb.W9MflQRoXa3clDiqd2mmeViOzpmSV1a', rol='ejecutivo', liga_id=None, cancha_id=None, activo=True, fecha_creacion=datetime.datetime.strptime('2026-03-11 22:56:34', '%Y-%m-%d %H:%M:%S'), privacy_accepted=False, privacy_accepted_at=None)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Usuario.query.get(38):
                obj = Usuario(id=38, nombre='Árbitro Gral B - Deportivo Cu', email='arbitro_b_deportivocu@futadmin.com', password_hash='$2b$12$eSaFdtyBE3zfVsWaxWLEYOZyrLwy/leyTjP1zufNCBtfKBBbofE2O', rol='arbitro', liga_id=9, cancha_id=None, activo=True, fecha_creacion=datetime.datetime.strptime('2026-03-15 08:09:38', '%Y-%m-%d %H:%M:%S'), privacy_accepted=True, privacy_accepted_at=datetime.datetime.strptime('2026-03-15 22:49:29', '%Y-%m-%d %H:%M:%S'))
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Usuario.query.get(34):
                obj = Usuario(id=34, nombre='Árbitro Gral B - Liga Cumbres', email='arbitro_b_ligacumbres@futadmin.com', password_hash='$2b$12$.56JWCmNNWy4SKpyE4hOvehSFfF6KoohlrONzyVahNWcswFdzl0Le', rol='arbitro', liga_id=8, cancha_id=None, activo=True, fecha_creacion=datetime.datetime.strptime('2026-03-13 20:43:38', '%Y-%m-%d %H:%M:%S'), privacy_accepted=True, privacy_accepted_at=datetime.datetime.strptime('2026-03-15 23:15:42', '%Y-%m-%d %H:%M:%S'))
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Usuario.query.get(39):
                obj = Usuario(id=39, nombre='Lector Gral - Deportivo Cu', email='lector_deportivocu@futadmin.com', password_hash='$2b$12$yYuwNNp2OQirsn7r8IZNBOSRA.rekKTdF2cHavN9H8PTwnS10.IT2', rol='resultados', liga_id=9, cancha_id=None, activo=True, fecha_creacion=datetime.datetime.strptime('2026-03-15 08:09:38', '%Y-%m-%d %H:%M:%S'), privacy_accepted=True, privacy_accepted_at=datetime.datetime.strptime('2026-03-16 06:34:15', '%Y-%m-%d %H:%M:%S'))
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            db.session.commit()
            print('--- Insertando canchas ---')
            if not Cancha.query.get(14):
                obj = Cancha(id=14, liga_id=8, nombre='Deportivo Zuñiga', encargado='Maradona', email_encargado='', telefono_encargado='663*******', tipo='Gratuita', costo_renta=0.0, unidad_cobro='Partido', direccion='Las Cumbres TJ ', estado='Baja California', municipio='Tijuana', notas='', foto_url='/static/uploads/19266e87b0914d7ca0b5855363ff7f20.png', modalidad='Fútbol Rápido', fecha_afiliacion=datetime.datetime.strptime('2026-03-13 23:46:42', '%Y-%m-%d %H:%M:%S'), activo=True, dueno_id=None)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Cancha.query.get(15):
                obj = Cancha(id=15, liga_id=9, nombre='Colegio Ma.', encargado='Maria', email_encargado='', telefono_encargado='663*******', tipo='Propia', costo_renta=100.0, unidad_cobro='Partido', direccion='Flores Magón ', estado='Yucatán', municipio='Progreso', notas='📝 REGLAMENTO INTERNO - SEDE PRODUCTIVA\n\n1. EQUIPAMIENTO:\n- Uso obligatorio de calzado adecuado (tachones de goma o multitacos).\n- Prohibido el uso de tacos de aluminio.\n- Uso obligatorio de espinilleras durante los partidos.\n\n2. COMPORTAMIENTO:\n- Respeto total al cuerpo arbitral y personal de la sede.\n- Prohibido el consumo de bebidas alcohólicas y tabaco en las áreas de juego.\n- Cualquier riña o agresión resultará en expulsión inmediata de la sede.\n\n3. PAGOS Y RESERVAS:\n- Los pagos deben liquidarse antes del inicio del encuentro.\n- Tolerancia máxima de espera: 10 minutos.\n\n4. INSTALACIONES:\n- Mantener las áreas comunes limpias.\n- No se permite el ingreso de mascotas al terreno de juego.\n\n"El deporte es salud y sana convivencia."', foto_url='', modalidad='Fútbol 7', fecha_afiliacion=datetime.datetime.strptime('2026-03-15 08:18:28', '%Y-%m-%d %H:%M:%S'), activo=True, dueno_id=None)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            db.session.commit()
            print('--- Insertando arbitros ---')
            if not Arbitro.query.get(15):
                obj = Arbitro(id=15, liga_id=9, nombre='EUSTAQUIO DIAZ', email='Eustaquio@futadmin.com', telefono=None, nivel='Principal', foto_url=None, activo=True, telegram_id=None, password='admin123', cancha_id=15)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Arbitro.query.get(16):
                obj = Arbitro(id=16, liga_id=9, nombre='Árbitro Gral A - Deportivo Cu', email='arbitro_a_deportivocu@futadmin.com', telefono=None, nivel='Local', foto_url=None, activo=True, telegram_id=None, password='admin123', cancha_id=15)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Arbitro.query.get(17):
                obj = Arbitro(id=17, liga_id=9, nombre='Árbitro Gral B - Deportivo Cu', email='arbitro_b_deportivocu@futadmin.com', telefono=None, nivel='Local', foto_url=None, activo=True, telegram_id=None, password='admin123', cancha_id=15)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Arbitro.query.get(13):
                obj = Arbitro(id=13, liga_id=8, nombre='Árbitro Gral A - Liga Cumbres', email='arbitro_a_ligacumbres@futadmin.com', telefono='663*******', nivel='Principal', foto_url='/static/uploads/02b93ed2a2214072bf7215a30521bdf1.png', activo=True, telegram_id=None, password='admin123', cancha_id=14)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Arbitro.query.get(14):
                obj = Arbitro(id=14, liga_id=8, nombre='Árbitro Gral B - Liga Cumbres', email='arbitro_b_ligacumbres@futadmin.com', telefono=None, nivel='Local', foto_url=None, activo=True, telegram_id='5825342439', password='admin123', cancha_id=14)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            db.session.commit()
            print('--- Insertando torneos ---')
            if not Torneo.query.get(8):
                obj = Torneo(id=8, liga_id=8, nombre='Torneo Rapido 2026', tipo='Relámpago', costo_inscripcion=350.0, costo_arbitraje=0.0, fecha_inicio=datetime.datetime.strptime('2026-03-15 00:00:00', '%Y-%m-%d %H:%M:%S'), activo=True, archived=False, imagen_url='/static/uploads/5ef3c39adbc04e7cae0a95a73e75acad.png', reglamento='REGLAMENTO TORNEO RELÁMPAGO\n1. DURACIÓN: Partidos de 2 tiempos de 15 min.\n2. SISTEMA: Eliminación directa única; pierdes y sales.\n3. EMPATE: Definición inmediata por serie de 3 penaltis.\n4. PLANTILLA: Máximo 10 jugadores inscritos por equipo.\n5. REGLAS: Se aplican las bases de Fútbol 7 básicas.\n6. EXPULSIÓN: Tarjeta roja directa te deja fuera de todo el torneo.\n7. BALÓN: Deberá ser entregado al árbitro por el equipo local.\n8. TOLERANCIA: No existe; 2 min de retraso es default.\n9. CALZADO: Solo tenis (No tacos de fútbol campo).\n10. PREMIACIÓN: Se entrega al finalizar la gran final del día.', clausulas='CLÁUSULAS TORNEO RELÁMPAGO\n1. PAGO: Inscripción total pagada antes del primer sorteo.\n2. REEMBOLSO: No existen devoluciones por inasistencia.\n3. HORARIOS: Sujetos a cambios bruscos según avance del bracket.\n4. MÉDICO: El torneo cuenta con primeros auxilios básicos.\n5. ARBITRAJE: Paquete de pre-pago de $0 por fase.\n6. HIDRATACIÓN: Cada equipo es responsable de su consumo.\n7. PORRA: Se limitará el acceso a porras excesivamente grandes.\n8. PROTESTAS: Deben hacerse al finalizar el juego ante mesa directiva.\n9. PREMIOS: El trofeo y medallas son propiedad del campeón vigente.\n10. CIERRE: Al terminar el torneo, todos los equipos deben desalojar.', premios='BOLSA DE PREMIOS RELÁMPAGO\n1. CAMPEÓN: Reconocimiento y $3,000 en Bono.\n2. MVP: Balón Oficial.', num_tiempos=2, duracion_tiempo=15, descanso=5, arbitro_id=None, dias_juego='Do', horario_juego='08:00 a 22:00', cancha='Deportivo Zuñiga', formato='Eliminación Directa', jugadores_totales=15, jugadores_campo=7)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Torneo.query.get(15):
                obj = Torneo(id=15, liga_id=8, nombre='Torneo Estatal 202603', tipo='Relámpago', costo_inscripcion=500.0, costo_arbitraje=150.0, fecha_inicio=datetime.datetime.strptime('2026-03-21 00:00:00', '%Y-%m-%d %H:%M:%S'), activo=True, archived=False, imagen_url='/static/uploads/7a551e59197840b697883879802281b6.png', reglamento='REGLAMENTO TORNEO RELÁMPAGO\n1. DURACIÓN: Partidos de 2 tiempos de 30 min.\n2. SISTEMA: Eliminación directa única; pierdes y sales.\n3. EMPATE: Definición inmediata por serie de 3 penaltis.\n4. PLANTILLA: Máximo 10 jugadores inscritos por equipo.\n5. REGLAS: Se aplican las bases de Fútbol 7 básicas.\n6. EXPULSIÓN: Tarjeta roja directa te deja fuera de todo el torneo.\n7. BALÓN: Deberá ser entregado al árbitro por el equipo local.\n8. TOLERANCIA: No existe; 2 min de retraso es default.\n9. CALZADO: Solo tenis (No tacos de fútbol campo).\n10. PREMIACIÓN: Se entrega al finalizar la gran final del día.', clausulas='CLÁUSULAS TORNEO RELÁMPAGO\n1. PAGO: Inscripción total pagada antes del primer sorteo.\n2. REEMBOLSO: No existen devoluciones por inasistencia.\n3. HORARIOS: Sujetos a cambios bruscos según avance del bracket.\n4. MÉDICO: El torneo cuenta con primeros auxilios básicos.\n5. ARBITRAJE: Paquete de pre-pago de $150 por fase.\n6. HIDRATACIÓN: Cada equipo es responsable de su consumo.\n7. PORRA: Se limitará el acceso a porras excesivamente grandes.\n8. PROTESTAS: Deben hacerse al finalizar el juego ante mesa directiva.\n9. PREMIOS: El trofeo y medallas son propiedad del campeón vigente.\n10. CIERRE: Al terminar el torneo, todos los equipos deben desalojar.', premios='BOLSA DE PREMIOS RELÁMPAGO\n1. CAMPEÓN: Reconocimiento y $3,000 en Bono.\n2. MVP: Balón Oficial.', num_tiempos=2, duracion_tiempo=30, descanso=10, arbitro_id=None, dias_juego='Sa, Do', horario_juego='07:00 a 19:00', cancha='Deportivo Zuñiga', formato='Liga', jugadores_totales=15, jugadores_campo=11)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Torneo.query.get(12):
                obj = Torneo(id=12, liga_id=8, nombre='Torneo TJ Municipal 202603', tipo='Fútbol Rápido', costo_inscripcion=450.0, costo_arbitraje=150.0, fecha_inicio=datetime.datetime.strptime('2026-03-15 00:00:00', '%Y-%m-%d %H:%M:%S'), activo=True, archived=False, imagen_url='/static/uploads/ff22bfaedbb84d04a04af6a63a264589.png', reglamento='REGLAMENTO OFICIAL FÚTBOL RÁPIDO\n1. BARDAS: El contacto con la madera/pared es legal y válido.\n2. SAQUE DE BANDA: No existe, el balón rebota o sale por redes superiores.\n3. JUGADORES: 6 elementos en cancha con rotación constante.\n4. PERIODOS: 2 cuartos de 20 minutos cada uno.\n5. SUSPENSIÓN TÉCNICA: Sanción de 2 min tras conducta antideportiva.\n6. SHOOT-OUT: Mano o falta de último hombre otorga mano a mano.\n7. BALÓN: #4 específico de bote rápido.\n8. DESCANSO: 5 MINUTOS entre periodos.\n9. ARQUERO: No puede cruzar la media cancha con balón en mano.\n10. GOL: Válido desde cualquier sector de la cancha.', clausulas='CLÁUSULAS RÉGIMEN FÚTBOL RÁPIDO\n1. DAÑOS: Rotura de cristales o bardas corre por cuenta del equipo.\n2. FISCAL: El juez de mesa tiene autoridad sobre los delegados.\n3. PAGOS: Costo arbitral de $150 semanal obligatorio.\n4. REGLAS: Se sigue el código de la asociación nacional de la rama.\n5. TARJETAS: Tarjeta azul penaliza con tiempo muerto al jugador.\n6. EMPATE: Resolución por shoot-outs en etapas finales.\n7. UNIFORMES: Medias y números debidamente reglamentados.\n8. INTEGRIDAD: No se permiten tacos de aluminio o fierro.\n9. REGISTRO: Formatos de inscripción debidamente requisitados.\n10. VETO: Jugador sancionado no puede ingresar ni como espectador.', premios='BOLSA DE PREMIOS FÚTBOL RÁPIDO\n1. CAMPEÓN: $8,000 MXN.\n2. SUBCAMPEÓN: $3,000 MXN.\n3. 3ER LUGAR: Devolución de Inscripción.', num_tiempos=2, duracion_tiempo=20, descanso=5, arbitro_id=None, dias_juego='Do', horario_juego='07:00 a 19:00', cancha='Deportivo Zuñiga', formato='Liga', jugadores_totales=15, jugadores_campo=7)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Torneo.query.get(11):
                obj = Torneo(id=11, liga_id=8, nombre='Liga Socer 2026', tipo='Soccer', costo_inscripcion=450.0, costo_arbitraje=100.0, fecha_inicio=datetime.datetime.strptime('2026-03-15 00:00:00', '%Y-%m-%d %H:%M:%S'), activo=True, archived=False, imagen_url='/static/uploads/528940bad3a443ed8eb27bba656b49ea.png', reglamento='REGLAMENTO OFICIAL SOCCER (FUT 11)\n1. TIEMPOS: 2 periodos de 45 min oficiales con 10 min de descanso.\n2. REGLA 11: El fuera de lugar está vigente durante todo el juego.\n3. CAMBIOS: Máximo 5 cambios en 3 ventanas de tiempo.\n4. SAQUE DE META: Con el pie desde cualquier punto del área chica.\n5. BALÓN: Tamaño #5 con presión reglamentaria.\n6. TARJETAS: La acumulación de 3 amarillas causa 1 partido de suspensión.\n7. CAPITÁN: Único autorizado para dirigirse al cuerpo arbitral.\n8. ESPINILLERAS: Uso obligatorio; si no cuenta con ellas no juega.\n9. PORTERÍA: El portero está protegido dentro de su área chica.\n10. EMPATE: Se definirá según el formato de la competencia oficial.', clausulas='CLÁUSULAS LEGALES SOCCER\n1. SEGURIDAD: Los equipos asumen riesgos médicos inherentes.\n2. INSTALACIONES: Todo daño a la cancha será cubierto por el equipo.\n3. ALTAS: Jugadores nuevos solo permitidos hasta la mitad del torneo.\n4. MULTAS: Las tarjetas rojas directas generan multa de $100.\n5. PROTESTAS: Por escrito con evidencia y fianza de $300.\n6. REGLAMENTO: Los equipos aceptan los estatutos de la FIFA adaptados.\n7. ARBITRAJE: Se debe cubrir el pago arbtitral de $100 puntualmente.\n8. ASISTENCIA: 2 incomparecencias injustificadas causan baja.\n9. PREMIACIÓN: Sujeta a cumplimiento total de pagos económicos.\n10. JUNTA: Obligatoria la asistencia de delegados a reuniones.', premios='BOLSA DE PREMIOS SOCCER\n1. CAMPEÓN LIGA: Trofeo Grande y 10 Balones.\n2. CAMPEÓN DE COPA: Trofeo Mediano.\n3. GOLEADOR: Trofeo y Zapatos de Fútbol.', num_tiempos=2, duracion_tiempo=45, descanso=10, arbitro_id=None, dias_juego='Do', horario_juego='07:45 a 19:45', cancha='Deportivo Zuñiga', formato='Fase de Grupos', jugadores_totales=15, jugadores_campo=7)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Torneo.query.get(18):
                obj = Torneo(id=18, liga_id=8, nombre='Liga Nacional 2026', tipo='Soccer', costo_inscripcion=450.0, costo_arbitraje=150.0, fecha_inicio=datetime.datetime.strptime('2026-03-16 00:00:00', '%Y-%m-%d %H:%M:%S'), activo=True, archived=False, imagen_url='/static/uploads/1cd6041bf9794491aa81bee4c2d47519.png', reglamento='', clausulas='', premios='', num_tiempos=2, duracion_tiempo=30, descanso=10, arbitro_id=None, dias_juego='Do', horario_juego='07:00 a 19:00', cancha='Deportivo Zuñiga', formato='Fase de Grupos', jugadores_totales=15, jugadores_campo=11)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Torneo.query.get(19):
                obj = Torneo(id=19, liga_id=9, nombre='Test Torneo', tipo='', costo_inscripcion=0.0, costo_arbitraje=0.0, fecha_inicio=datetime.datetime.strptime('2026-03-17 00:00:00', '%Y-%m-%d %H:%M:%S'), activo=True, archived=False, imagen_url='', reglamento='', clausulas='', premios='', num_tiempos=2, duracion_tiempo=20, descanso=10, arbitro_id=None, dias_juego='', horario_juego='', cancha='Colegio Ma.', formato='Liga', jugadores_totales=15, jugadores_campo=7)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Torneo.query.get(20):
                obj = Torneo(id=20, liga_id=9, nombre='Test Torneo', tipo='', costo_inscripcion=0.0, costo_arbitraje=0.0, fecha_inicio=datetime.datetime.strptime('2026-03-17 00:00:00', '%Y-%m-%d %H:%M:%S'), activo=True, archived=False, imagen_url='', reglamento='', clausulas='', premios='', num_tiempos=2, duracion_tiempo=20, descanso=10, arbitro_id=None, dias_juego='', horario_juego='', cancha='Colegio Ma.', formato='Liga', jugadores_totales=15, jugadores_campo=7)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            db.session.commit()
            print('--- Insertando equipos ---')
            if not Equipo.query.get(92):
                obj = Equipo(id=92, liga_id=8, nombre='Arsenal 43', torneo_id=8, uid='LPNL07WDFZVGCQF', escudo_url='/static/uploads/a460e221bde54538b76afd2aa3c5759d.png', email='', colonia='Patio del Centro de Cómputo', colonia_geojson='{"type": "Polygon", "coordinates": [[[-116.9662795, 32.5313314], [-116.9661962, 32.5313179], [-116.9661926, 32.5313397], [-116.9659925, 32.5313144], [-116.9659991, 32.5312771], [-116.9660213, 32.5312657], [-116.9660441, 32.5311474], [-116.9655492, 32.5310826], [-116.9654608, 32.5315862], [-116.9660935, 32.5316725], [-116.9660984, 32.5316489], [-116.9662085, 32.5316657], [-116.9662795, 32.5313314]]]}', grupo='')
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(93):
                obj = Equipo(id=93, liga_id=8, nombre='Real Cumbres. ', torneo_id=8, uid='HK831GQAURBIV05', escudo_url='/static/uploads/f358285b49ae4ed2ba3a1d8a93f31c42.png', email=None, colonia='Centro Católico de Evangelización', colonia_geojson='{"type": "Polygon", "coordinates": [[[-117.0407687, 32.4351242], [-117.0393195, 32.4348158], [-117.0390136, 32.4355227], [-117.0389952, 32.4356024], [-117.0389911, 32.4356526], [-117.0389972, 32.4356994], [-117.0390013, 32.4357341], [-117.0390116, 32.4357704], [-117.0390362, 32.4358103], [-117.039067, 32.4358467], [-117.0391019, 32.4358727], [-117.039145, 32.4359056], [-117.039184, 32.4359246], [-117.0392271, 32.4359454], [-117.0392785, 32.4359792], [-117.0398598, 32.4362456], [-117.0402206, 32.4363924], [-117.0403766, 32.4363352], [-117.040469, 32.4361758], [-117.0405573, 32.4360061], [-117.0405368, 32.4359991], [-117.0405696, 32.4359437], [-117.040584, 32.435909], [-117.040623, 32.4357358], [-117.0407687, 32.4351242]]]}', grupo=None)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(98):
                obj = Equipo(id=98, liga_id=8, nombre='Tigres Dorados', torneo_id=8, uid='T22B452HZFX36Q2', escudo_url=None, email=None, colonia='Centro Comercial Pacifico', colonia_geojson='{"type": "Polygon", "coordinates": [[[-116.9954398, 32.4761046], [-116.9954187, 32.4760863], [-116.9953689, 32.4760413], [-116.9952783, 32.4759594], [-116.9947697, 32.4751614], [-116.9942791, 32.4744053], [-116.9942269, 32.4743079], [-116.9936472, 32.4733972], [-116.9935604, 32.4732609], [-116.9920168, 32.4766207], [-116.9920094, 32.4766905], [-116.9920208, 32.4768234], [-116.9920994, 32.4769967], [-116.9921481, 32.4770616], [-116.9922125, 32.4771239], [-116.9923507, 32.4772459], [-116.9925857, 32.4774293], [-116.9927313, 32.4774802], [-116.9929153, 32.4775455], [-116.9930762, 32.4775835], [-116.9932563, 32.4775897], [-116.9933617, 32.4775783], [-116.9933794, 32.4775735], [-116.9935177, 32.4775361], [-116.9939188, 32.4772367], [-116.9943674, 32.4769019], [-116.9945573, 32.4767602], [-116.9950579, 32.4763866], [-116.9953514, 32.4761678], [-116.9954398, 32.4761046]]]}', grupo='Grupo B')
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(100):
                obj = Equipo(id=100, liga_id=8, nombre='Xolos Bravos', torneo_id=8, uid='ISWGEMKRVE2EDC9', escudo_url=None, email=None, colonia='División del Norte', colonia_geojson='{"type": "Polygon", "coordinates": [[[-116.9295405, 32.4909716], [-116.9291749, 32.4905132], [-116.9290866, 32.4905634], [-116.9284795, 32.4909078], [-116.9285425, 32.4909869], [-116.9287657, 32.4912855], [-116.9288347, 32.4913721], [-116.929343, 32.4910837], [-116.9295405, 32.4909716]]]}', grupo='Grupo B')
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(164):
                obj = Equipo(id=164, liga_id=9, nombre='Test Team', torneo_id=19, uid='1LH3TE2UVANHLI7', escudo_url=None, email=None, colonia=None, colonia_geojson=None, grupo=None)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(165):
                obj = Equipo(id=165, liga_id=9, nombre='Test Team', torneo_id=20, uid='SECRET-UID-123', escudo_url=None, email=None, colonia=None, colonia_geojson=None, grupo=None)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(94):
                obj = Equipo(id=94, liga_id=8, nombre='Cimarrones FC', torneo_id=8, uid='SFJ1FX8N6XDIES4', escudo_url=None, email=None, colonia='Parque Colinas de la Presa', colonia_geojson='{"type": "Polygon", "coordinates": [[[-116.9324813, 32.441347], [-116.9320312, 32.4409985], [-116.9318861, 32.4410445], [-116.93174, 32.4410012], [-116.931661, 32.4408886], [-116.9316863, 32.4407596], [-116.93092, 32.4404308], [-116.9309936, 32.4414505], [-116.9313019, 32.4414514], [-116.9323319, 32.441389], [-116.9324813, 32.441347]]]}', grupo='Grupo A')
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(108):
                obj = Equipo(id=108, liga_id=8, nombre='Lobos del Desierto', torneo_id=8, uid='Y2RVO8T06AWQXYB', escudo_url=None, email=None, colonia='Zona Río', colonia_geojson='{"type": "Polygon", "coordinates": [[[-117.0401977, 32.5414914], [-117.0349569, 32.5388165], [-117.0348765, 32.5387782], [-117.0348082, 32.5387456], [-117.0345393, 32.5384725], [-117.0340932, 32.5377694], [-117.033987, 32.5374916], [-117.0338801, 32.5368155], [-117.0338043, 32.5357008], [-117.0321096, 32.5357724], [-117.0319712, 32.5345292], [-117.0314306, 32.5345886], [-117.0303955, 32.5330557], [-117.0302707, 32.5326309], [-117.0300797, 32.5321875], [-117.0298334, 32.5318259], [-117.0280258, 32.5296062], [-117.0265396, 32.5277276], [-117.0255403, 32.5265362], [-117.0246462, 32.5259559], [-117.0244448, 32.524664], [-117.0224931, 32.5236357], [-117.0214264, 32.5230697], [-117.0202029, 32.5224203], [-117.0181888, 32.5213705], [-117.0169562, 32.5208494], [-117.015708, 32.5203485], [-117.0158775, 32.5200262], [-117.0153289, 32.5197636], [-117.0154478, 32.5195462], [-117.013408, 32.5185889], [-117.0132499, 32.5184306], [-117.0124902, 32.5180629], [-117.0120042, 32.5186144], [-117.0094735, 32.5178938], [-117.0087894, 32.5176271], [-117.0084652, 32.517417], [-117.0080856, 32.5170602], [-117.0076862, 32.5168135], [-117.0073145, 32.5166901], [-117.0068953, 32.5166467], [-117.0065473, 32.5166534], [-117.006231, 32.5167168], [-117.0058988, 32.5168235], [-117.0055904, 32.5170135], [-117.0053531, 32.5172269], [-117.005191, 32.517417], [-117.0050003, 32.5179028], [-117.0022837, 32.5177798], [-117.0019574, 32.5177238], [-117.0016564, 32.5176155], [-117.001375, 32.5174682], [-117.0008007, 32.5172102], [-117.000581, 32.5170189], [-117.0003726, 32.5170869], [-117.0005479, 32.5189261], [-117.0007129, 32.5197644], [-117.0011297, 32.5198275], [-117.0017339, 32.5200478], [-117.0056253, 32.5238074], [-117.0072294, 32.5254096], [-117.0094828, 32.527054], [-117.0097859, 32.5272745], [-117.0107865, 32.5281897], [-117.0112411, 32.5287198], [-117.0115219, 32.5292699], [-117.0119035, 32.5300157], [-117.0117108, 32.5294136], [-117.0119516, 32.5292674], [-117.0129496, 32.5313765], [-117.0131273, 32.5317237], [-117.0136611, 32.5325738], [-117.0142345, 32.5333706], [-117.0145073, 32.5338206], [-117.0148068, 32.5345169], [-117.015905, 32.5357222], [-117.016116, 32.5359339], [-117.0164441, 32.536236], [-117.0178002, 32.537255], [-117.0187176, 32.5378449], [-117.0192868, 32.5369671], [-117.019775, 32.5371729], [-117.0218918, 32.5380632], [-117.0230436, 32.5385478], [-117.0234621, 32.5387171], [-117.0241452, 32.5389627], [-117.0243878, 32.5389749], [-117.0245972, 32.5390276], [-117.0250726, 32.5391801], [-117.0254343, 32.5393494], [-117.0254476, 32.539361], [-117.0256251, 32.539516], [-117.0257758, 32.5397192], [-117.0258662, 32.5399281], [-117.0258997, 32.5401511], [-117.0258428, 32.5403797], [-117.0257457, 32.5405829], [-117.0255223, 32.5407954], [-117.0253055, 32.5409206], [-117.0251354, 32.540978], [-117.0251556, 32.5410117], [-117.0251655, 32.5410283], [-117.0251719, 32.5410391], [-117.0253271, 32.5409803], [-117.0257733, 32.5407961], [-117.0258093, 32.5409198], [-117.0258254, 32.5409616], [-117.025877, 32.540987], [-117.0259064, 32.5409894], [-117.0262646, 32.5410402], [-117.0265693, 32.5411192], [-117.0266974, 32.5411679], [-117.0268255, 32.5412238], [-117.026844, 32.5412338], [-117.0268772, 32.5412512], [-117.0269593, 32.5413005], [-117.0270158, 32.5413261], [-117.0270696, 32.5413166], [-117.0270736, 32.5413126], [-117.0271035, 32.5412807], [-117.0271384, 32.5412972], [-117.0271863, 32.5413734], [-117.0271997, 32.5413926], [-117.0272246, 32.5414293], [-117.0272368, 32.5414472], [-117.0272414, 32.541454], [-117.0273556, 32.5416041], [-117.0273803, 32.5416369], [-117.0274863, 32.5417371], [-117.0277559, 32.5420079], [-117.0282285, 32.5425656], [-117.0283759, 32.542553], [-117.0284282, 32.5425486], [-117.0284802, 32.5425441], [-117.0285332, 32.5425396], [-117.0285826, 32.5425354], [-117.0286369, 32.5425307], [-117.0286942, 32.5425258], [-117.0287523, 32.5425209], [-117.028805, 32.5425163], [-117.0288678, 32.542511], [-117.0289265, 32.542506], [-117.0289811, 32.5425013], [-117.0290407, 32.5424962], [-117.0291025, 32.5424909], [-117.0291529, 32.5424866], [-117.0292109, 32.5424816], [-117.0292716, 32.5424765], [-117.0293303, 32.5424714], [-117.0293817, 32.542467], [-117.0294533, 32.5424609], [-117.0295083, 32.5424562], [-117.0295751, 32.5424505], [-117.0296381, 32.5424451], [-117.0296892, 32.5424408], [-117.0297526, 32.5424353], [-117.0298148, 32.54243], [-117.0298821, 32.5424243], [-117.0299457, 32.5424188], [-117.0300131, 32.5424131], [-117.0300714, 32.5424081], [-117.030149, 32.5424014], [-117.0302143, 32.5423959], [-117.0304086, 32.5423844], [-117.0304051, 32.5423317], [-117.0303991, 32.5422581], [-117.0303971, 32.5422221], [-117.030393, 32.5421458], [-117.0296093, 32.5413737], [-117.029553, 32.5412247], [-117.0299357, 32.5409373], [-117.0299462, 32.5409301], [-117.0299908, 32.5408993], [-117.0314985, 32.5402142], [-117.0343788, 32.5420086], [-117.0347533, 32.5419758], [-117.0401977, 32.5414914]]]}', grupo='Grupo D')
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(138):
                obj = Equipo(id=138, liga_id=8, nombre='Meteoros 100', torneo_id=12, uid='B7KDIVQALVPE79H', escudo_url=None, email='delegado_9_4@test.com', colonia='Zona Centro', colonia_geojson='{"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[[-117.046, 32.524], [-117.038, 32.524], [-117.038, 32.532], [-117.046, 32.532], [-117.046, 32.524]]]}}', grupo=None)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(130):
                obj = Equipo(id=130, liga_id=8, nombre='Valientes 41', torneo_id=11, uid='CVTSNK5WX1JZUIW', escudo_url=None, email='delegado_16@test.com', colonia='Libertad', colonia_geojson='{"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[[-117.01400000000001, 32.531], [-117.006, 32.531], [-117.006, 32.538999999999994], [-117.01400000000001, 32.538999999999994], [-117.01400000000001, 32.531]]]}}', grupo='Grupo B')
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(131):
                obj = Equipo(id=131, liga_id=8, nombre='Fuerza TJ 27', torneo_id=11, uid='HEV0RHUOCDBMKOB', escudo_url=None, email='delegado_17@test.com', colonia='Francisco Villa', colonia_geojson='{"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[[-117.069, 32.501000000000005], [-117.06099999999999, 32.501000000000005], [-117.06099999999999, 32.509], [-117.069, 32.509], [-117.069, 32.501000000000005]]]}}', grupo='Grupo B')
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(132):
                obj = Equipo(id=132, liga_id=8, nombre='Titanes 94', torneo_id=11, uid='1BNZBZHSFPTCAFB', escudo_url=None, email='delegado_18@test.com', colonia='Soler', colonia_geojson='{"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[[-117.07900000000001, 32.521], [-117.071, 32.521], [-117.071, 32.528999999999996], [-117.07900000000001, 32.528999999999996], [-117.07900000000001, 32.521]]]}}', grupo='Grupo B')
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(133):
                obj = Equipo(id=133, liga_id=8, nombre='Imperio 62', torneo_id=11, uid='LYJURLJU40MOL8L', escudo_url=None, email='delegado_19@test.com', colonia='Soler', colonia_geojson='{"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[[-117.07900000000001, 32.521], [-117.071, 32.521], [-117.071, 32.528999999999996], [-117.07900000000001, 32.528999999999996], [-117.07900000000001, 32.521]]]}}', grupo='Grupo C')
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(126):
                obj = Equipo(id=126, liga_id=8, nombre='Deportivo M 90', torneo_id=11, uid='AX5TDTQBRCWD41H', escudo_url=None, email='delegado_12@test.com', colonia='Libertad', colonia_geojson='{"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[[-117.01400000000001, 32.531], [-117.006, 32.531], [-117.006, 32.538999999999994], [-117.01400000000001, 32.538999999999994], [-117.01400000000001, 32.531]]]}}', grupo='Grupo C')
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(95):
                obj = Equipo(id=95, liga_id=8, nombre='Real Azteca', torneo_id=8, uid='GLBYOUWWC7YG645', escudo_url=None, email=None, colonia='Del. La Presa', colonia_geojson='{"type": "Polygon", "coordinates": [[[-116.8674733, 32.5042886], [-116.8670303, 32.5039583], [-116.866864, 32.5040261], [-116.8668479, 32.5041166], [-116.8667716, 32.5040895], [-116.866769, 32.5042867], [-116.8668321, 32.5042873], [-116.8668313, 32.5043434], [-116.8667595, 32.5043427], [-116.8667583, 32.5044307], [-116.866754, 32.5046971], [-116.8669376, 32.5046993], [-116.8669659, 32.5047726], [-116.8674733, 32.5042886]]]}', grupo='Grupo A')
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(102):
                obj = Equipo(id=102, liga_id=8, nombre='Halcones Reales', torneo_id=8, uid='CKLV5WK1NTB4CA1', escudo_url=None, email=None, colonia='Real del Mar', colonia_geojson='{"type": "Polygon", "coordinates": [[[-117.1036134, 32.4482453], [-117.1032326, 32.4478149], [-117.1028899, 32.4479704], [-117.102922, 32.4480175], [-117.1026765, 32.4481408], [-117.1026571, 32.4480192], [-117.1024715, 32.447799], [-117.1027629, 32.4476338], [-117.1024078, 32.4471725], [-117.1026056, 32.447013], [-117.1030503, 32.4461032], [-117.1030578, 32.4455902], [-117.1026882, 32.4448827], [-117.1020557, 32.4438541], [-117.1017547, 32.4432138], [-117.1003984, 32.4391789], [-117.0950985, 32.4410164], [-117.0930841, 32.4417149], [-117.089364, 32.4422163], [-117.0873292, 32.4428547], [-117.0863099, 32.4434076], [-117.0861411, 32.4435883], [-117.0857311, 32.4439687], [-117.0857105, 32.4442861], [-117.0859388, 32.4446101], [-117.0856153, 32.4454338], [-117.0854105, 32.4456586], [-117.0805065, 32.4470361], [-117.0800001, 32.4469481], [-117.0799182, 32.4468003], [-117.0797743, 32.4468711], [-117.0798172, 32.4470403], [-117.0796248, 32.4469849], [-117.0793875, 32.44711], [-117.0793127, 32.4469804], [-117.0791705, 32.447036], [-117.0792334, 32.4471782], [-117.0793369, 32.4475567], [-117.079803, 32.4484392], [-117.080441, 32.448223], [-117.0808326, 32.4490828], [-117.0802099, 32.4493055], [-117.0800945, 32.4490385], [-117.0791155, 32.4492693], [-117.079424, 32.4501407], [-117.080408, 32.4499869], [-117.0809153, 32.4503648], [-117.0815027, 32.4505595], [-117.0817717, 32.4504668], [-117.0820391, 32.4496632], [-117.0824219, 32.4498017], [-117.0830698, 32.4498537], [-117.0829277, 32.4505349], [-117.0835005, 32.4505403], [-117.0835487, 32.4499273], [-117.0838076, 32.449943], [-117.0840245, 32.4499108], [-117.0840036, 32.450531], [-117.0840948, 32.4506473], [-117.0843753, 32.4506769], [-117.0846598, 32.4505031], [-117.0845413, 32.4499873], [-117.0849935, 32.4498452], [-117.0867699, 32.4495683], [-117.0868043, 32.449278], [-117.0872018, 32.4491201], [-117.0876178, 32.4490351], [-117.0899629, 32.4489156], [-117.0915816, 32.4495913], [-117.0926754, 32.4497037], [-117.0935447, 32.4500897], [-117.0938101, 32.4500557], [-117.0956176, 32.4506961], [-117.0960162, 32.450596], [-117.0961701, 32.4507591], [-117.0964919, 32.4505888], [-117.0965669, 32.4505229], [-117.0969388, 32.4504881], [-117.0970566, 32.4505531], [-117.0971974, 32.4506148], [-117.0973218, 32.4506082], [-117.0974101, 32.4505655], [-117.0975092, 32.4504681], [-117.0975162, 32.4503867], [-117.0974857, 32.4503054], [-117.0978078, 32.4499456], [-117.0977226, 32.4496331], [-117.0978553, 32.4496188], [-117.0979734, 32.4495675], [-117.0981106, 32.4497411], [-117.0983322, 32.4495412], [-117.0981777, 32.4493959], [-117.0982776, 32.4492067], [-117.0983617, 32.4490784], [-117.0984394, 32.4490119], [-117.0985145, 32.4489735], [-117.0988027, 32.4493073], [-117.0994267, 32.448891], [-117.1002675, 32.4487282], [-117.1006153, 32.4487051], [-117.1010941, 32.4485829], [-117.1011677, 32.448538], [-117.1020983, 32.4486288], [-117.1024368, 32.4487037], [-117.1032204, 32.4484383], [-117.1036134, 32.4482453]]]}', grupo='Grupo C')
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(150):
                obj = Equipo(id=150, liga_id=8, nombre='Vikingos 180', torneo_id=12, uid='KW04PMNQ7MLEVPB', escudo_url=None, email='delegado_9_16@test.com', colonia='Libertad', colonia_geojson='{"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[[-117.01400000000001, 32.531], [-117.006, 32.531], [-117.006, 32.538999999999994], [-117.01400000000001, 32.538999999999994], [-117.01400000000001, 32.531]]]}}', grupo=None)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(151):
                obj = Equipo(id=151, liga_id=8, nombre='Espartanos 112', torneo_id=12, uid='13XWTWW0TQ1B0MX', escudo_url=None, email='delegado_9_17@test.com', colonia='Francisco Villa', colonia_geojson='{"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[[-117.069, 32.501000000000005], [-117.06099999999999, 32.501000000000005], [-117.06099999999999, 32.509], [-117.069, 32.509], [-117.069, 32.501000000000005]]]}}', grupo=None)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(96):
                obj = Equipo(id=96, liga_id=8, nombre='Águilas Negras', torneo_id=8, uid='XWRJNJRCNBTFGZB', escudo_url=None, email=None, colonia='Parque Sanchez Taboada II', colonia_geojson='{"type": "Polygon", "coordinates": [[[-116.9702612, 32.4640578], [-116.9701378, 32.4639877], [-116.9699125, 32.4640261], [-116.9695879, 32.4644606], [-116.969301, 32.464481], [-116.9688638, 32.4648861], [-116.9686411, 32.4647684], [-116.9682147, 32.4651712], [-116.9681878, 32.4652731], [-116.9685151, 32.4653387], [-116.9686304, 32.4654654], [-116.9686358, 32.465513], [-116.968419, 32.465908], [-116.9687856, 32.4660496], [-116.9690189, 32.4658294], [-116.9692867, 32.4656812], [-116.9699469, 32.4649128], [-116.9698991, 32.4648567], [-116.9698964, 32.4645987], [-116.9702612, 32.4640578]]]}', grupo='Grupo A')
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(97):
                obj = Equipo(id=97, liga_id=8, nombre='Leones del Norte', torneo_id=8, uid='W28SNYVNE0UNJCE', escudo_url=None, email=None, colonia='Parque Sanchez Taboada', colonia_geojson='{"type": "Polygon", "coordinates": [[[-116.9718271, 32.4688507], [-116.9713604, 32.4687557], [-116.9710868, 32.4699279], [-116.971497, 32.4700038], [-116.9715213, 32.4700274], [-116.9718271, 32.4688507]]]}', grupo='Grupo A')
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(99):
                obj = Equipo(id=99, liga_id=8, nombre='Guerreros del Sol', torneo_id=8, uid='65X1SARU7R1FNRL', escudo_url=None, email=None, colonia='Del. Otay Centenario', colonia_geojson='{"type": "Polygon", "coordinates": [[[-116.9435259, 32.5356975], [-116.9435027, 32.5356954], [-116.9435179, 32.535578], [-116.9432629, 32.5355545], [-116.9432467, 32.5356791], [-116.9432143, 32.5356761], [-116.9432005, 32.5357824], [-116.9432232, 32.5357845], [-116.94321, 32.5358863], [-116.9433136, 32.5358958], [-116.943317, 32.5358696], [-116.9433611, 32.5358736], [-116.9433587, 32.5358921], [-116.9434608, 32.5359015], [-116.943474, 32.5357999], [-116.9435121, 32.5358035], [-116.9435259, 32.5356975]]]}', grupo='Grupo B')
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(101):
                obj = Equipo(id=101, liga_id=8, nombre='Potros Salvajes', torneo_id=8, uid='IEH7V3L1JPWAP1I', escudo_url=None, email=None, colonia='Centro Comercial Jardines de Agua Caliente', colonia_geojson='{"type": "Polygon", "coordinates": [[[-116.9830481, 32.4885232], [-116.9829705, 32.4884578], [-116.9827729, 32.4886929], [-116.9828011, 32.4887257], [-116.9824164, 32.4891603], [-116.9824941, 32.4892287], [-116.9823917, 32.4893627], [-116.982307, 32.4892942], [-116.98212, 32.4894877], [-116.9823985, 32.4896463], [-116.9824164, 32.4894937], [-116.9826352, 32.4891752], [-116.9826352, 32.4890769], [-116.9828187, 32.4888834], [-116.9830481, 32.4885232]]]}', grupo='Grupo B')
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(103):
                obj = Equipo(id=103, liga_id=8, nombre='Cóndores FC', torneo_id=8, uid='GWX08EWR7F5CSY9', escudo_url=None, email=None, colonia='Tecate', colonia_geojson='{"type": "Polygon", "coordinates": [[[-116.6617402, 32.5699193], [-116.6615645, 32.568295], [-116.661412, 32.5683059], [-116.6609691, 32.5683453], [-116.6604962, 32.5683824], [-116.660128, 32.5647123], [-116.6558467, 32.5651366], [-116.6556469, 32.5651554], [-116.6551172, 32.5652059], [-116.6543546, 32.5609324], [-116.6556118, 32.5601031], [-116.6559718, 32.5598656], [-116.6559182, 32.5592588], [-116.6557507, 32.5579661], [-116.6544844, 32.5579874], [-116.6542479, 32.556814], [-116.6522032, 32.5570542], [-116.6522028, 32.5585381], [-116.6500364, 32.5588817], [-116.6502118, 32.5605217], [-116.6485945, 32.5617689], [-116.6448403, 32.5618982], [-116.6447951, 32.5618867], [-116.644703, 32.5614219], [-116.6445579, 32.5609028], [-116.6442988, 32.5597699], [-116.6439709, 32.558346], [-116.6432233, 32.558319], [-116.6423229, 32.5582398], [-116.6415826, 32.5582354], [-116.6407738, 32.5582083], [-116.6401181, 32.5582064], [-116.6401023, 32.5578207], [-116.6400873, 32.5575613], [-116.6400874, 32.5570562], [-116.640049, 32.5563209], [-116.6390573, 32.556424], [-116.6389884, 32.5551722], [-116.6372183, 32.5546619], [-116.6371043, 32.5540549], [-116.6369668, 32.5536441], [-116.6367225, 32.5533073], [-116.6365092, 32.5530473], [-116.6362647, 32.5527625], [-116.6360134, 32.5525182], [-116.6357691, 32.5521679], [-116.6356472, 32.5520368], [-116.6348534, 32.5512744], [-116.6317175, 32.5483109], [-116.6307104, 32.5472999], [-116.629749, 32.5473489], [-116.6284294, 32.5474217], [-116.6267355, 32.5475092], [-116.6254998, 32.5475709], [-116.6242027, 32.547655], [-116.6224863, 32.5477423], [-116.6191593, 32.5478879], [-116.6189152, 32.5483111], [-116.6178166, 32.548062], [-116.6178629, 32.5486034], [-116.6179543, 32.5493411], [-116.6180075, 32.5498284], [-116.6182823, 32.5504878], [-116.6185795, 32.5510457], [-116.6188086, 32.5513328], [-116.6190836, 32.5516291], [-116.6095008, 32.5516493], [-116.6107899, 32.560045], [-116.6148718, 32.5598614], [-116.6198537, 32.5596961], [-116.6209911, 32.5617], [-116.6179769, 32.5619096], [-116.6183888, 32.5641571], [-116.6155888, 32.5643921], [-116.6161383, 32.5670008], [-116.6169017, 32.5669152], [-116.6171837, 32.5691871], [-116.6159327, 32.5693095], [-116.615322, 32.5690393], [-116.6113243, 32.5693743], [-116.6114542, 32.5691943], [-116.6117289, 32.5686539], [-116.6108358, 32.5673228], [-116.6104085, 32.5666629], [-116.6101494, 32.5663644], [-116.6099054, 32.5661314], [-116.6094857, 32.5658843], [-116.6091501, 32.5655878], [-116.6089056, 32.564694], [-116.6087761, 32.5641794], [-116.608593, 32.5640232], [-116.6079979, 32.5632207], [-116.6070896, 32.5625075], [-116.6066166, 32.5621204], [-116.6061896, 32.5620153], [-116.6052203, 32.5618341], [-116.6051904, 32.5615363], [-116.6052743, 32.5590942], [-116.6037801, 32.5590526], [-116.6006126, 32.5589644], [-116.6004858, 32.5601306], [-116.5978204, 32.5603274], [-116.5976748, 32.5623492], [-116.5987889, 32.5623031], [-116.5988882, 32.5627297], [-116.59901, 32.5627413], [-116.6011925, 32.5627212], [-116.6019552, 32.5623357], [-116.603069, 32.5623302], [-116.6031149, 32.562044], [-116.6046561, 32.5620736], [-116.6045034, 32.5624092], [-116.6038069, 32.5635724], [-116.6037965, 32.5635921], [-116.6035805, 32.5639534], [-116.6069984, 32.5667696], [-116.6064798, 32.5670521], [-116.6062815, 32.567047], [-116.6057931, 32.566971], [-116.6049386, 32.5668759], [-116.6039924, 32.5667466], [-116.6036716, 32.566705], [-116.6033361, 32.566704], [-116.6028631, 32.5667701], [-116.6020239, 32.5668306], [-116.6015816, 32.5668676], [-116.6008182, 32.5669666], [-116.6004217, 32.5670443], [-116.5995899, 32.5672356], [-116.5990863, 32.5672949], [-116.5991096, 32.5683301], [-116.599163, 32.569494], [-116.5991631, 32.5705224], [-116.5992317, 32.5712736], [-116.5995823, 32.5711822], [-116.6000552, 32.5711454], [-116.6004831, 32.5710565], [-116.6012609, 32.5708921], [-116.6017187, 32.5708056], [-116.602085, 32.5707775], [-116.6024969, 32.5706908], [-116.6031531, 32.570614], [-116.6036416, 32.5705005], [-116.6038703, 32.5704471], [-116.604465, 32.5704016], [-116.6065711, 32.5703924], [-116.6069833, 32.5703937], [-116.6073567, 32.5704197], [-116.6076926, 32.570653], [-116.6080892, 32.5708617], [-116.6083334, 32.5711985], [-116.6085473, 32.5716367], [-116.6085244, 32.5718419], [-116.6085551, 32.5721284], [-116.6085548, 32.5723471], [-116.6082652, 32.5723462], [-116.6047173, 32.5719495], [-116.6026569, 32.5716972], [-116.6024281, 32.5720933], [-116.6019093, 32.5727119], [-116.6017722, 32.5728693], [-116.6012225, 32.5730863], [-116.6009784, 32.5731735], [-116.6005134, 32.5739862], [-116.6004521, 32.5741438], [-116.5995522, 32.5755573], [-116.5993386, 32.5755318], [-116.597797, 32.5749585], [-116.5971563, 32.5758856], [-116.5927162, 32.5739634], [-116.5916173, 32.5763707], [-116.5937386, 32.5771533], [-116.592848, 32.5792081], [-116.6201272, 32.5769588], [-116.6272647, 32.5763616], [-116.6388339, 32.5754081], [-116.6588523, 32.5737434], [-116.6615495, 32.5735184], [-116.6612211, 32.5709124], [-116.6610682, 32.5699693], [-116.6612973, 32.5699587], [-116.6615111, 32.5699344], [-116.6617402, 32.5699193]]]}', grupo='Grupo C')
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(104):
                obj = Equipo(id=104, liga_id=8, nombre='Los Toros', torneo_id=8, uid='1IG0EPQ1M4WZA9D', escudo_url=None, email=None, colonia='Centro Urbano 70-76', colonia_geojson='{"type": "Polygon", "coordinates": [[[-116.9900346, 32.5402569], [-116.9882355, 32.538167], [-116.987669, 32.5378052], [-116.9872002, 32.5376076], [-116.9867506, 32.5372408], [-116.9863583, 32.5371058], [-116.9863471, 32.5371035], [-116.9858151, 32.5369224], [-116.9855981, 32.5368754], [-116.9847076, 32.5365136], [-116.9844943, 32.5364331], [-116.9828367, 32.5358153], [-116.9821072, 32.5355403], [-116.9817287, 32.5354508], [-116.9812746, 32.5353522], [-116.9809162, 32.5352758], [-116.9805536, 32.5351858], [-116.9797125, 32.535041], [-116.9785141, 32.5360762], [-116.97954, 32.5364641], [-116.9899679, 32.5404072], [-116.9900346, 32.5402569]]]}', grupo='Grupo C')
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(105):
                obj = Equipo(id=105, liga_id=8, nombre='Chivas Verdes', torneo_id=8, uid='VBS4OPC68QD2UBA', escudo_url=None, email=None, colonia='Parque de Terrrazas de la Presa Seccion Vistas', colonia_geojson='{"type": "Polygon", "coordinates": [[[-116.917444, 32.4430252], [-116.9174364, 32.4428195], [-116.9171736, 32.4428422], [-116.9169, 32.4429667], [-116.916731, 32.4430866], [-116.9169027, 32.4431523], [-116.9172798, 32.4430449], [-116.917444, 32.4430252]]]}', grupo='Grupo C')
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(106):
                obj = Equipo(id=106, liga_id=8, nombre='Piratas del Río', torneo_id=8, uid='F45V2WOX1HW002O', escudo_url=None, email=None, colonia='Del. Centro', colonia_geojson='{"type": "Polygon", "coordinates": [[[-117.0365743, 32.5331086], [-117.0365686, 32.533047], [-117.0365579, 32.5329693], [-117.0365495, 32.5328916], [-117.0359467, 32.532941], [-117.0359843, 32.5333163], [-117.0361854, 32.5333334], [-117.0361787, 32.5331468], [-117.0365743, 32.5331086]]]}', grupo='Grupo D')
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(107):
                obj = Equipo(id=107, liga_id=8, nombre='Escorpiones CF', torneo_id=8, uid='83P01I9LPZD522M', escudo_url=None, email=None, colonia='Centro Urbano 70-76', colonia_geojson='{"type": "Polygon", "coordinates": [[[-116.9900346, 32.5402569], [-116.9882355, 32.538167], [-116.987669, 32.5378052], [-116.9872002, 32.5376076], [-116.9867506, 32.5372408], [-116.9863583, 32.5371058], [-116.9863471, 32.5371035], [-116.9858151, 32.5369224], [-116.9855981, 32.5368754], [-116.9847076, 32.5365136], [-116.9844943, 32.5364331], [-116.9828367, 32.5358153], [-116.9821072, 32.5355403], [-116.9817287, 32.5354508], [-116.9812746, 32.5353522], [-116.9809162, 32.5352758], [-116.9805536, 32.5351858], [-116.9797125, 32.535041], [-116.9785141, 32.5360762], [-116.97954, 32.5364641], [-116.9899679, 32.5404072], [-116.9900346, 32.5402569]]]}', grupo='Grupo D')
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(109):
                obj = Equipo(id=109, liga_id=8, nombre='Rayos Plateados', torneo_id=8, uid='C1UVOFVNEOEMG1R', escudo_url=None, email=None, colonia='El Florido', colonia_geojson='{"type": "Polygon", "coordinates": [[[-116.9215522, 32.4569436], [-116.921276, 32.4566946], [-116.9210346, 32.4566109], [-116.9208307, 32.4567829], [-116.9212438, 32.4571563], [-116.9215522, 32.4569436]]]}', grupo='Grupo D')
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(110):
                obj = Equipo(id=110, liga_id=8, nombre='Jaguares FC', torneo_id=8, uid='9CQEGI1W2PXVQCV', escudo_url=None, email=None, colonia='Centro Comercial Pacifico', colonia_geojson='{"type": "Polygon", "coordinates": [[[-116.9954398, 32.4761046], [-116.9954187, 32.4760863], [-116.9953689, 32.4760413], [-116.9952783, 32.4759594], [-116.9947697, 32.4751614], [-116.9942791, 32.4744053], [-116.9942269, 32.4743079], [-116.9936472, 32.4733972], [-116.9935604, 32.4732609], [-116.9920168, 32.4766207], [-116.9920094, 32.4766905], [-116.9920208, 32.4768234], [-116.9920994, 32.4769967], [-116.9921481, 32.4770616], [-116.9922125, 32.4771239], [-116.9923507, 32.4772459], [-116.9925857, 32.4774293], [-116.9927313, 32.4774802], [-116.9929153, 32.4775455], [-116.9930762, 32.4775835], [-116.9932563, 32.4775897], [-116.9933617, 32.4775783], [-116.9933794, 32.4775735], [-116.9935177, 32.4775361], [-116.9939188, 32.4772367], [-116.9943674, 32.4769019], [-116.9945573, 32.4767602], [-116.9950579, 32.4763866], [-116.9953514, 32.4761678], [-116.9954398, 32.4761046]]]}', grupo='Grupo E')
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(111):
                obj = Equipo(id=111, liga_id=8, nombre='Dragones del Valle', torneo_id=8, uid='CK58HURFXSTL7ON', escudo_url=None, email=None, colonia='San Antonio de los Buenos', colonia_geojson='{"type": "Polygon", "coordinates": [[[-117.0541833, 32.4846669], [-117.0541659, 32.4845695], [-117.0541354, 32.4844401], [-117.0540826, 32.4842711], [-117.0540092, 32.4841192], [-117.0538338, 32.4839227], [-117.0536936, 32.4838175], [-117.0535035, 32.4837235], [-117.0533395, 32.483677], [-117.0531801, 32.4836454], [-117.0507302, 32.4831062], [-117.0506608, 32.4831057], [-117.0506127, 32.4831327], [-117.0503346, 32.4837697], [-117.0502605, 32.4839506], [-117.0501031, 32.484512], [-117.0501164, 32.4845429], [-117.0501497, 32.4845626], [-117.0505422, 32.4846419], [-117.0531423, 32.4851132], [-117.0530176, 32.4856307], [-117.0536563, 32.4857603], [-117.0538491, 32.4857136], [-117.0539418, 32.4853336], [-117.0541037, 32.4853622], [-117.0541696, 32.4849904], [-117.0541764, 32.484831], [-117.0541833, 32.4846669]]]}', grupo='Grupo E')
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(112):
                obj = Equipo(id=112, liga_id=8, nombre='Búhos Dorados', torneo_id=8, uid='Q6LM15VGXG2WS00', escudo_url=None, email=None, colonia='Del. La Mesa', colonia_geojson='{"type": "Polygon", "coordinates": [[[-116.9903712, 32.4807616], [-116.9898687, 32.4803779], [-116.9897763, 32.4804738], [-116.9896069, 32.4805725], [-116.9892711, 32.4807675], [-116.9882913, 32.4812665], [-116.9878938, 32.4814848], [-116.9875641, 32.4817109], [-116.9872376, 32.4820098], [-116.9862239, 32.4833561], [-116.9851917, 32.484666], [-116.9843886, 32.4856603], [-116.9841767, 32.4859182], [-116.9839285, 32.4862098], [-116.9837213, 32.4864264], [-116.9834325, 32.4867296], [-116.9827081, 32.487494], [-116.9826376, 32.487569], [-116.9818026, 32.4884942], [-116.9812603, 32.4890582], [-116.9807766, 32.4894324], [-116.9802836, 32.4897131], [-116.9796397, 32.4899808], [-116.9781947, 32.4905421], [-116.9761766, 32.4912672], [-116.9760997, 32.4913105], [-116.9760543, 32.4913514], [-116.9760143, 32.4914042], [-116.9760069, 32.4914507], [-116.9760173, 32.4914927], [-116.9760332, 32.491531], [-116.9760668, 32.4915798], [-116.9761057, 32.4916176], [-116.9761488, 32.4916341], [-116.9762005, 32.491643], [-116.9762665, 32.4916415], [-116.9763508, 32.4916314], [-116.9764446, 32.4916154], [-116.9768852, 32.491501], [-116.9780591, 32.491132], [-116.9787, 32.4909137], [-116.9795257, 32.4906279], [-116.9802004, 32.4903342], [-116.9804654, 32.4902042], [-116.9809645, 32.4898638], [-116.9812018, 32.4896949], [-116.98163, 32.4892739], [-116.9822925, 32.4886008], [-116.9825883, 32.4882811], [-116.9833924, 32.4874365], [-116.9845077, 32.4863085], [-116.985238, 32.4856016], [-116.9857895, 32.4851182], [-116.9865967, 32.4843853], [-116.9875426, 32.4835017], [-116.9886055, 32.4825244], [-116.9894097, 32.4817291], [-116.9896901, 32.4814562], [-116.9903712, 32.4807616]]]}', grupo='Grupo E')
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(113):
                obj = Equipo(id=113, liga_id=8, nombre='Zorros Plateados', torneo_id=8, uid='UF2JQJHYQ0SCAVM', escudo_url=None, email=None, colonia='Parque Lomas de la Presa', colonia_geojson='{"type": "Polygon", "coordinates": [[[-116.9299855, 32.442073], [-116.9299506, 32.4418379], [-116.929787, 32.441847], [-116.9298051, 32.4420848], [-116.9299855, 32.442073]]]}', grupo='Grupo E')
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(114):
                obj = Equipo(id=114, liga_id=8, nombre='Aztecas 91', torneo_id=11, uid='MJY263C0F0Y70R2', escudo_url=None, email='delegado_0@test.com', colonia='Zona Centro', colonia_geojson='{"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[[-117.046, 32.524], [-117.038, 32.524], [-117.038, 32.532], [-117.046, 32.532], [-117.046, 32.524]]]}}', grupo='Grupo B')
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(134):
                obj = Equipo(id=134, liga_id=8, nombre='Rápidos 118', torneo_id=12, uid='0GZFJL46HCJZ6QY', escudo_url=None, email='delegado_9_0@test.com', colonia='Francisco Villa', colonia_geojson='{"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[[-117.069, 32.501000000000005], [-117.06099999999999, 32.501000000000005], [-117.06099999999999, 32.509], [-117.069, 32.509], [-117.069, 32.501000000000005]]]}}', grupo=None)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(135):
                obj = Equipo(id=135, liga_id=8, nombre='Fugaces 102', torneo_id=12, uid='NUU1MNF4BBTDM6I', escudo_url=None, email='delegado_9_1@test.com', colonia='Francisco Villa', colonia_geojson='{"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[[-117.069, 32.501000000000005], [-117.06099999999999, 32.501000000000005], [-117.06099999999999, 32.509], [-117.069, 32.509], [-117.069, 32.501000000000005]]]}}', grupo=None)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(136):
                obj = Equipo(id=136, liga_id=8, nombre='Estrellas 139', torneo_id=12, uid='H3FLT8JF39AIDDZ', escudo_url=None, email='delegado_9_2@test.com', colonia='Libertad', colonia_geojson='{"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[[-117.01400000000001, 32.531], [-117.006, 32.531], [-117.006, 32.538999999999994], [-117.01400000000001, 32.538999999999994], [-117.01400000000001, 32.531]]]}}', grupo=None)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(137):
                obj = Equipo(id=137, liga_id=8, nombre='Cometas 174', torneo_id=12, uid='TSNOR6NMUKMYJIF', escudo_url=None, email='delegado_9_3@test.com', colonia='La Cacho', colonia_geojson='{"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[[-117.039, 32.516000000000005], [-117.03099999999999, 32.516000000000005], [-117.03099999999999, 32.524], [-117.039, 32.524], [-117.039, 32.516000000000005]]]}}', grupo=None)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(139):
                obj = Equipo(id=139, liga_id=8, nombre='Halcones 123', torneo_id=12, uid='78F5G1YEA57SOGC', escudo_url=None, email='delegado_9_5@test.com', colonia='Otay Constituyentes', colonia_geojson='{"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[[-116.96900000000001, 32.531], [-116.961, 32.531], [-116.961, 32.538999999999994], [-116.96900000000001, 32.538999999999994], [-116.96900000000001, 32.531]]]}}', grupo=None)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(140):
                obj = Equipo(id=140, liga_id=8, nombre='Gavilanes 163', torneo_id=12, uid='UVI7B8CJ555WVY6', escudo_url=None, email='delegado_9_6@test.com', colonia='Libertad', colonia_geojson='{"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[[-117.01400000000001, 32.531], [-117.006, 32.531], [-117.006, 32.538999999999994], [-117.01400000000001, 32.538999999999994], [-117.01400000000001, 32.531]]]}}', grupo=None)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(141):
                obj = Equipo(id=141, liga_id=8, nombre='Búhos 149', torneo_id=12, uid='UOFDH279IS9BHOT', escudo_url=None, email='delegado_9_7@test.com', colonia='Rio Tijuana', colonia_geojson='{"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[[-117.02900000000001, 32.521], [-117.021, 32.521], [-117.021, 32.528999999999996], [-117.02900000000001, 32.528999999999996], [-117.02900000000001, 32.521]]]}}', grupo=None)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(142):
                obj = Equipo(id=142, liga_id=8, nombre='Linces 181', torneo_id=12, uid='Y7OXIJEWR93WMC9', escudo_url=None, email='delegado_9_8@test.com', colonia='Playas de Tijuana', colonia_geojson='{"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[[-117.119, 32.516000000000005], [-117.11099999999999, 32.516000000000005], [-117.11099999999999, 32.524], [-117.119, 32.524], [-117.119, 32.516000000000005]]]}}', grupo=None)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(143):
                obj = Equipo(id=143, liga_id=8, nombre='Panteras 152', torneo_id=12, uid='GB47X65DJ77Q4ZP', escudo_url=None, email='delegado_9_9@test.com', colonia='La Cacho', colonia_geojson='{"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[[-117.039, 32.516000000000005], [-117.03099999999999, 32.516000000000005], [-117.03099999999999, 32.524], [-117.039, 32.524], [-117.039, 32.516000000000005]]]}}', grupo=None)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(144):
                obj = Equipo(id=144, liga_id=8, nombre='Grizzlies 186', torneo_id=12, uid='U13KJ1SMDNMB7RG', escudo_url=None, email='delegado_9_10@test.com', colonia='Francisco Villa', colonia_geojson='{"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[[-117.069, 32.501000000000005], [-117.06099999999999, 32.501000000000005], [-117.06099999999999, 32.509], [-117.069, 32.509], [-117.069, 32.501000000000005]]]}}', grupo=None)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(145):
                obj = Equipo(id=145, liga_id=8, nombre='Coyotes 190', torneo_id=12, uid='CRL77E7G3MPSL1E', escudo_url=None, email='delegado_9_11@test.com', colonia='Francisco Villa', colonia_geojson='{"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[[-117.069, 32.501000000000005], [-117.06099999999999, 32.501000000000005], [-117.06099999999999, 32.509], [-117.069, 32.509], [-117.069, 32.501000000000005]]]}}', grupo=None)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(146):
                obj = Equipo(id=146, liga_id=8, nombre='Zorros 171', torneo_id=12, uid='FXKQAYP3N4VO83L', escudo_url=None, email='delegado_9_12@test.com', colonia='Camino Verde', colonia_geojson='{"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[[-116.989, 32.481], [-116.981, 32.481], [-116.981, 32.489], [-116.989, 32.489], [-116.989, 32.481]]]}}', grupo=None)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(147):
                obj = Equipo(id=147, liga_id=8, nombre='Toros 143', torneo_id=12, uid='N212S79FD1MNTZ9', escudo_url=None, email='delegado_9_13@test.com', colonia='Soler', colonia_geojson='{"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[[-117.07900000000001, 32.521], [-117.071, 32.521], [-117.071, 32.528999999999996], [-117.07900000000001, 32.528999999999996], [-117.07900000000001, 32.521]]]}}', grupo=None)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(148):
                obj = Equipo(id=148, liga_id=8, nombre='Búfalos 195', torneo_id=12, uid='JQQMDIPD38ILZ7I', escudo_url=None, email='delegado_9_14@test.com', colonia='Soler', colonia_geojson='{"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[[-117.07900000000001, 32.521], [-117.071, 32.521], [-117.071, 32.528999999999996], [-117.07900000000001, 32.528999999999996], [-117.07900000000001, 32.521]]]}}', grupo=None)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(149):
                obj = Equipo(id=149, liga_id=8, nombre='Corsarios 107', torneo_id=12, uid='9N7INJ1I1W0SKZ9', escudo_url=None, email='delegado_9_15@test.com', colonia='Rio Tijuana', colonia_geojson='{"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[[-117.02900000000001, 32.521], [-117.021, 32.521], [-117.021, 32.528999999999996], [-117.02900000000001, 32.528999999999996], [-117.02900000000001, 32.521]]]}}', grupo=None)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(152):
                obj = Equipo(id=152, liga_id=8, nombre='Gladiadores 173', torneo_id=12, uid='LWLZY4FPYBUWS21', escudo_url=None, email='delegado_9_18@test.com', colonia='Francisco Villa', colonia_geojson='{"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[[-117.069, 32.501000000000005], [-117.06099999999999, 32.501000000000005], [-117.06099999999999, 32.509], [-117.069, 32.509], [-117.069, 32.501000000000005]]]}}', grupo=None)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(153):
                obj = Equipo(id=153, liga_id=8, nombre='Legión 194', torneo_id=12, uid='KRAA6OZLS0BLOZ1', escudo_url=None, email='delegado_9_19@test.com', colonia='Libertad', colonia_geojson='{"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[[-117.01400000000001, 32.531], [-117.006, 32.531], [-117.006, 32.538999999999994], [-117.01400000000001, 32.538999999999994], [-117.01400000000001, 32.531]]]}}', grupo=None)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(154):
                obj = Equipo(id=154, liga_id=8, nombre='Unión 164', torneo_id=12, uid='7FX3VP2M5BDUUZ3', escudo_url=None, email='delegado_9_20@test.com', colonia='Francisco Villa', colonia_geojson='{"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[[-117.069, 32.501000000000005], [-117.06099999999999, 32.501000000000005], [-117.06099999999999, 32.509], [-117.069, 32.509], [-117.069, 32.501000000000005]]]}}', grupo=None)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(155):
                obj = Equipo(id=155, liga_id=8, nombre='Aliados 191', torneo_id=12, uid='TTX1E66KS52YC17', escudo_url=None, email='delegado_9_21@test.com', colonia='Camino Verde', colonia_geojson='{"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[[-116.989, 32.481], [-116.981, 32.481], [-116.981, 32.489], [-116.989, 32.489], [-116.989, 32.481]]]}}', grupo=None)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(156):
                obj = Equipo(id=156, liga_id=8, nombre='Fénix 106', torneo_id=12, uid='R6XAZEXTT4YJHBF', escudo_url=None, email='delegado_9_22@test.com', colonia='Francisco Villa', colonia_geojson='{"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[[-117.069, 32.501000000000005], [-117.06099999999999, 32.501000000000005], [-117.06099999999999, 32.509], [-117.069, 32.509], [-117.069, 32.501000000000005]]]}}', grupo=None)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(157):
                obj = Equipo(id=157, liga_id=8, nombre='Renacer 103', torneo_id=12, uid='0UTVT6Y46VNIQAA', escudo_url=None, email='delegado_9_23@test.com', colonia='Soler', colonia_geojson='{"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[[-117.07900000000001, 32.521], [-117.071, 32.521], [-117.071, 32.528999999999996], [-117.07900000000001, 32.528999999999996], [-117.07900000000001, 32.521]]]}}', grupo=None)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(158):
                obj = Equipo(id=158, liga_id=8, nombre='Triunfo 130', torneo_id=12, uid='B3128TTMZYPA8SW', escudo_url=None, email='delegado_9_24@test.com', colonia='Soler', colonia_geojson='{"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[[-117.07900000000001, 32.521], [-117.071, 32.521], [-117.071, 32.528999999999996], [-117.07900000000001, 32.528999999999996], [-117.07900000000001, 32.521]]]}}', grupo=None)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(115):
                obj = Equipo(id=115, liga_id=8, nombre='Guerreros 49', torneo_id=11, uid='S9KJOIE73Q4W2S3', escudo_url=None, email='delegado_1@test.com', colonia='Playas de Tijuana', colonia_geojson='{"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[[-117.119, 32.516000000000005], [-117.11099999999999, 32.516000000000005], [-117.11099999999999, 32.524], [-117.119, 32.524], [-117.119, 32.516000000000005]]]}}', grupo='Grupo A')
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(116):
                obj = Equipo(id=116, liga_id=8, nombre='Diablos 58', torneo_id=11, uid='VWBTB9C6JXC74YU', escudo_url=None, email='delegado_2@test.com', colonia='Francisco Villa', colonia_geojson='{"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[[-117.069, 32.501000000000005], [-117.06099999999999, 32.501000000000005], [-117.06099999999999, 32.509], [-117.069, 32.509], [-117.069, 32.501000000000005]]]}}', grupo='Grupo D')
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(117):
                obj = Equipo(id=117, liga_id=8, nombre='Águilas 53', torneo_id=11, uid='9TJ1VO9AOCS7OMS', escudo_url=None, email='delegado_3@test.com', colonia='Zona Centro', colonia_geojson='{"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[[-117.046, 32.524], [-117.038, 32.524], [-117.038, 32.532], [-117.046, 32.532], [-117.046, 32.524]]]}}', grupo='Grupo D')
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(118):
                obj = Equipo(id=118, liga_id=8, nombre='Leones 29', torneo_id=11, uid='DWPI125X864T1W8', escudo_url=None, email='delegado_4@test.com', colonia='Libertad', colonia_geojson='{"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[[-117.01400000000001, 32.531], [-117.006, 32.531], [-117.006, 32.538999999999994], [-117.01400000000001, 32.538999999999994], [-117.01400000000001, 32.531]]]}}', grupo='Grupo D')
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(119):
                obj = Equipo(id=119, liga_id=8, nombre='Tigres 83', torneo_id=11, uid='MUZD7B1AZ67G5BT', escudo_url=None, email='delegado_5@test.com', colonia='Zona Centro', colonia_geojson='{"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[[-117.046, 32.524], [-117.038, 32.524], [-117.038, 32.532], [-117.046, 32.532], [-117.046, 32.524]]]}}', grupo='Grupo C')
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(120):
                obj = Equipo(id=120, liga_id=8, nombre='Rayos 80', torneo_id=11, uid='GYVWJ85MSQAVVX5', escudo_url=None, email='delegado_6@test.com', colonia='La Cacho', colonia_geojson='{"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[[-117.039, 32.516000000000005], [-117.03099999999999, 32.516000000000005], [-117.03099999999999, 32.524], [-117.039, 32.524], [-117.039, 32.516000000000005]]]}}', grupo='Grupo C')
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(121):
                obj = Equipo(id=121, liga_id=8, nombre='Pumas 90', torneo_id=11, uid='L2J4HTKQV8LCFN1', escudo_url=None, email='delegado_7@test.com', colonia='Soler', colonia_geojson='{"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[[-117.07900000000001, 32.521], [-117.071, 32.521], [-117.071, 32.528999999999996], [-117.07900000000001, 32.528999999999996], [-117.07900000000001, 32.521]]]}}', grupo='Grupo A')
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(122):
                obj = Equipo(id=122, liga_id=8, nombre='Lobos 71', torneo_id=11, uid='CFS8LP12PB75K3A', escudo_url=None, email='delegado_8@test.com', colonia='Rio Tijuana', colonia_geojson='{"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[[-117.02900000000001, 32.521], [-117.021, 32.521], [-117.021, 32.528999999999996], [-117.02900000000001, 32.528999999999996], [-117.02900000000001, 32.521]]]}}', grupo='Grupo A')
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(123):
                obj = Equipo(id=123, liga_id=8, nombre='Dragones 51', torneo_id=11, uid='LH5V8BC2MGVX3H9', escudo_url=None, email='delegado_9@test.com', colonia='El Florido', colonia_geojson='{"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[[-116.894, 32.481], [-116.886, 32.481], [-116.886, 32.489], [-116.894, 32.489], [-116.894, 32.481]]]}}', grupo='Grupo A')
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(124):
                obj = Equipo(id=124, liga_id=8, nombre='Real Tijuana 7', torneo_id=11, uid='E8GZZS7SR6NF0F7', escudo_url=None, email='delegado_10@test.com', colonia='La Cacho', colonia_geojson='{"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[[-117.039, 32.516000000000005], [-117.03099999999999, 32.516000000000005], [-117.03099999999999, 32.524], [-117.039, 32.524], [-117.039, 32.516000000000005]]]}}', grupo='Grupo E')
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(125):
                obj = Equipo(id=125, liga_id=8, nombre='Atlético TJ 57', torneo_id=11, uid='R879XV1LSA6X4PK', escudo_url=None, email='delegado_11@test.com', colonia='El Florido', colonia_geojson='{"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[[-116.894, 32.481], [-116.886, 32.481], [-116.886, 32.489], [-116.894, 32.489], [-116.894, 32.481]]]}}', grupo='Grupo E')
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(127):
                obj = Equipo(id=127, liga_id=8, nombre='Sporting 78', torneo_id=11, uid='ZLG80VIGB5P878L', escudo_url=None, email='delegado_13@test.com', colonia='El Florido', colonia_geojson='{"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[[-116.894, 32.481], [-116.886, 32.481], [-116.886, 32.489], [-116.894, 32.489], [-116.894, 32.481]]]}}', grupo='Grupo E')
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(128):
                obj = Equipo(id=128, liga_id=8, nombre='Inter BC 91', torneo_id=11, uid='2VKZWH13BVFD2QK', escudo_url=None, email='delegado_14@test.com', colonia='Soler', colonia_geojson='{"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[[-117.07900000000001, 32.521], [-117.071, 32.521], [-117.071, 32.528999999999996], [-117.07900000000001, 32.528999999999996], [-117.07900000000001, 32.521]]]}}', grupo='Grupo D')
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Equipo.query.get(129):
                obj = Equipo(id=129, liga_id=8, nombre='Galácticos 92', torneo_id=11, uid='DNWOX57AE0KUUDR', escudo_url=None, email='delegado_15@test.com', colonia='Libertad', colonia_geojson='{"type": "Feature", "properties": {}, "geometry": {"type": "Polygon", "coordinates": [[[-117.01400000000001, 32.531], [-117.006, 32.531], [-117.006, 32.538999999999994], [-117.01400000000001, 32.538999999999994], [-117.01400000000001, 32.531]]]}}', grupo='Grupo E')
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            db.session.commit()
            print('--- Insertando jugadores ---')
            if not Jugador.query.get(645):
                obj = Jugador(id=645, liga_id=8, nombre='Messi', seudonimo=None, telefono='6632034042', posicion='Mediocampista', numero=10, fecha_nacimiento=datetime.datetime.strptime('2006-06-06', '%Y-%m-%d').date(), foto_url='/static/uploads/5b8fee3e92da41b18a368106e9713ac0.png', firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=92)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1082):
                obj = Jugador(id=1082, liga_id=8, nombre='Diño', seudonimo=None, telefono='6632034042', posicion='Delantero', numero=7, fecha_nacimiento=datetime.datetime.strptime('1998-02-10', '%Y-%m-%d').date(), foto_url='/static/uploads/5bed6996d32d4e67959053e5cc0579c3_dino.png', firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=92)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(646):
                obj = Jugador(id=646, liga_id=8, nombre='Néstor Orozco', seudonimo='EGXY890080V2RZFYVH', telefono='6102551386', posicion='Portero', numero=1, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=94)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(647):
                obj = Jugador(id=647, liga_id=8, nombre='Irving Reyes', seudonimo='SLOL5212668787J75W', telefono='6226234648', posicion='Lateral Izquierdo', numero=4, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=94)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(648):
                obj = Jugador(id=648, liga_id=8, nombre='Fulgencio Esquivel', seudonimo='SGUO905238DK11EQX7', telefono='6462576455', posicion='Delantero', numero=26, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=94)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(649):
                obj = Jugador(id=649, liga_id=8, nombre='Evaristo Esquivel', seudonimo='ZFLK750252J6F6Q3T4', telefono='6105520906', posicion='Mediocampista', numero=10, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=94)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(650):
                obj = Jugador(id=650, liga_id=8, nombre='Sebastián Leiva', seudonimo='SHOP277144DR0QZS0Q', telefono='6277377648', posicion='Mediocampista', numero=17, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=94)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(651):
                obj = Jugador(id=651, liga_id=8, nombre='Melitón Carrillo', seudonimo='HCTX376849PVI8NTBK', telefono='6717504925', posicion='Delantero', numero=14, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=94)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(652):
                obj = Jugador(id=652, liga_id=8, nombre='Omar Orozco', seudonimo='JPWI101226FNYPCVIB', telefono='6429066773', posicion='Defensa', numero=8, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=94)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(653):
                obj = Jugador(id=653, liga_id=8, nombre='Rigoberto Vargas', seudonimo='ETUR471889PDAHMPZG', telefono='6386345708', posicion='Defensa', numero=25, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=94)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(654):
                obj = Jugador(id=654, liga_id=8, nombre='Saúl Montoya', seudonimo='JURH918314EI54O25I', telefono='6964460514', posicion='Lateral Derecho', numero=27, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=94)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(655):
                obj = Jugador(id=655, liga_id=8, nombre='Sebastián Ríos', seudonimo='IGKJ1689581X3O5YLR', telefono='6177282658', posicion='Defensa', numero=13, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=94)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(656):
                obj = Jugador(id=656, liga_id=8, nombre='Santiago Bermúdez', seudonimo='MYMZ722322WJL72V9N', telefono='6395950939', posicion='Portero', numero=1, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=95)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(657):
                obj = Jugador(id=657, liga_id=8, nombre='Ricardo López', seudonimo='KOZP572994OANMYDOJ', telefono='6286548098', posicion='Defensa', numero=20, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=95)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(658):
                obj = Jugador(id=658, liga_id=8, nombre='Gervasio Núñez', seudonimo='IAHJ580149294Z9FXT', telefono='6187662722', posicion='Delantero', numero=6, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=95)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(659):
                obj = Jugador(id=659, liga_id=8, nombre='Primitivo Valdez', seudonimo='HJWO432323R4AEZ0I9', telefono='6396954670', posicion='Defensa', numero=15, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=95)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(660):
                obj = Jugador(id=660, liga_id=8, nombre='Ernesto Domínguez', seudonimo='QDHB408076QXWQZ0FH', telefono='6232288156', posicion='Delantero', numero=26, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=95)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(661):
                obj = Jugador(id=661, liga_id=8, nombre='Cornelio Montes', seudonimo='QMFJ138129U82P64BL', telefono='6616625384', posicion='Mediocampista', numero=11, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=95)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(662):
                obj = Jugador(id=662, liga_id=8, nombre='Lázaro Vargas', seudonimo='PAOY6645272A69432V', telefono='6514352179', posicion='Lateral Derecho', numero=5, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=95)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(663):
                obj = Jugador(id=663, liga_id=8, nombre='Emmanuel Carrillo', seudonimo='KUYE292305Y1N9NF7D', telefono='6178574884', posicion='Mediocampista', numero=23, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=95)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(664):
                obj = Jugador(id=664, liga_id=8, nombre='Erick Ibáñez', seudonimo='ZZDY652412ZCKNG73D', telefono='6782313881', posicion='Lateral Izquierdo', numero=19, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=95)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(665):
                obj = Jugador(id=665, liga_id=8, nombre='Pedro López', seudonimo='NXCE415401AASGSQ59', telefono='6557247789', posicion='Defensa', numero=28, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=95)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(666):
                obj = Jugador(id=666, liga_id=8, nombre='Gustavo Rangel', seudonimo='NHIG960008E5TOC8Q7', telefono='6564758844', posicion='Portero', numero=1, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=96)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(667):
                obj = Jugador(id=667, liga_id=8, nombre='Rodrigo Moreno', seudonimo='ORXN665127QB7SEWXY', telefono='6201298947', posicion='Delantero', numero=18, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=96)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(668):
                obj = Jugador(id=668, liga_id=8, nombre='Fulgencio Moreno', seudonimo='ICQK7491072BSTOFNL', telefono='6191974268', posicion='Defensa', numero=20, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=96)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(669):
                obj = Jugador(id=669, liga_id=8, nombre='Macedonio López', seudonimo='GQHV467529Z00RHITL', telefono='6803910886', posicion='Lateral Izquierdo', numero=16, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=96)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(670):
                obj = Jugador(id=670, liga_id=8, nombre='Fidel Acosta', seudonimo='DCNE078982OBAJQW7F', telefono='6976480003', posicion='Mediocampista', numero=7, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=96)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(671):
                obj = Jugador(id=671, liga_id=8, nombre='Querubín Peña', seudonimo='SBRC904469L3AHFSH4', telefono='6842500135', posicion='Delantero', numero=24, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=96)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(672):
                obj = Jugador(id=672, liga_id=8, nombre='Irving Delgado', seudonimo='XXVA625966UH88MN9M', telefono='6814671886', posicion='Lateral Derecho', numero=28, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=96)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(673):
                obj = Jugador(id=673, liga_id=8, nombre='Desiderio Flores', seudonimo='JNEX764886S177VMYG', telefono='6201287708', posicion='Mediocampista', numero=15, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=96)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(674):
                obj = Jugador(id=674, liga_id=8, nombre='Demetrio Esquivel', seudonimo='LHHA403917Z013CVY6', telefono='6415154186', posicion='Defensa', numero=12, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=96)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(675):
                obj = Jugador(id=675, liga_id=8, nombre='Lázaro Romero', seudonimo='FHQB705572PE1GC5SA', telefono='6709285262', posicion='Defensa', numero=9, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=96)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(676):
                obj = Jugador(id=676, liga_id=8, nombre='Néstor Ruiz', seudonimo='KUCL7116197GGQSHMP', telefono='6967546895', posicion='Portero', numero=1, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=97)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(677):
                obj = Jugador(id=677, liga_id=8, nombre='Aurelio Ortiz', seudonimo='VPLZ305371CTLILWSW', telefono='6613661108', posicion='Delantero', numero=14, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=97)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(678):
                obj = Jugador(id=678, liga_id=8, nombre='Gonzalo Jiménez', seudonimo='XIJX398475QWV1F2YJ', telefono='6131815634', posicion='Lateral Izquierdo', numero=3, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=97)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(679):
                obj = Jugador(id=679, liga_id=8, nombre='Ricardo Trejo', seudonimo='FOUC9423777U8Y63JY', telefono='6295917115', posicion='Mediocampista', numero=16, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=97)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(680):
                obj = Jugador(id=680, liga_id=8, nombre='Christopher Martínez', seudonimo='NQOC37538756RMU17K', telefono='6643850121', posicion='Mediocampista', numero=13, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=97)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(681):
                obj = Jugador(id=681, liga_id=8, nombre='Cornelio Fuentes', seudonimo='QVKU082196VFLI7OLV', telefono='6322358938', posicion='Lateral Derecho', numero=19, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=97)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(682):
                obj = Jugador(id=682, liga_id=8, nombre='Cristian Camacho', seudonimo='GRAT535026YGFV3CLL', telefono='6231158423', posicion='Defensa', numero=7, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=97)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(683):
                obj = Jugador(id=683, liga_id=8, nombre='Cornelio López', seudonimo='KCRQ6532321IWHSW25', telefono='6835626637', posicion='Delantero', numero=26, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=97)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(684):
                obj = Jugador(id=684, liga_id=8, nombre='Wenceslao Cruz', seudonimo='BBVO954375KREGH0TH', telefono='6236679128', posicion='Defensa', numero=28, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=97)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(685):
                obj = Jugador(id=685, liga_id=8, nombre='Rodrigo Ramírez', seudonimo='WIEE5964433URPGERC', telefono='6831819998', posicion='Defensa', numero=5, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=97)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(686):
                obj = Jugador(id=686, liga_id=8, nombre='Buenaventura Flores', seudonimo='VBDB516394N3D6IADQ', telefono='6295054018', posicion='Portero', numero=1, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=98)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(687):
                obj = Jugador(id=687, liga_id=8, nombre='Florián Argueta', seudonimo='CILW799015X60OV6F5', telefono='6528317729', posicion='Lateral Derecho', numero=6, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=98)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(688):
                obj = Jugador(id=688, liga_id=8, nombre='Celestino Delgado', seudonimo='QGPQ405633S0B0SIBN', telefono='6468167956', posicion='Defensa', numero=9, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=98)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(689):
                obj = Jugador(id=689, liga_id=8, nombre='Juan Rangel', seudonimo='BMLU992350005U7AE8', telefono='6616588201', posicion='Defensa', numero=23, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=98)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(690):
                obj = Jugador(id=690, liga_id=8, nombre='Irving Aguilar', seudonimo='NNKL707716PGPUNXAY', telefono='6894070527', posicion='Delantero', numero=5, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=98)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(691):
                obj = Jugador(id=691, liga_id=8, nombre='Nazario Briones', seudonimo='RQZJ765690E3MRY63Y', telefono='6744715179', posicion='Mediocampista', numero=24, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=98)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(692):
                obj = Jugador(id=692, liga_id=8, nombre='Maximiliano Medina', seudonimo='QUPX970585WVI94KY0', telefono='6448165711', posicion='Mediocampista', numero=14, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=98)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(693):
                obj = Jugador(id=693, liga_id=8, nombre='Exequiel Salazar', seudonimo='KFHT518106263HUS53', telefono='6749382382', posicion='Mediocampista', numero=12, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=98)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(694):
                obj = Jugador(id=694, liga_id=8, nombre='Severino Díaz', seudonimo='VONZ124315F9MDA01W', telefono='6243483147', posicion='Lateral Izquierdo', numero=25, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=98)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(695):
                obj = Jugador(id=695, liga_id=8, nombre='Marco Morales', seudonimo='OQYO327519KZ5Q4CCW', telefono='6926647455', posicion='Defensa', numero=20, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=98)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(696):
                obj = Jugador(id=696, liga_id=8, nombre='Próspero Cruz', seudonimo='DWIA276928RPHSFWUZ', telefono='6119644049', posicion='Portero', numero=1, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=99)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(697):
                obj = Jugador(id=697, liga_id=8, nombre='Aurelio Ibáñez', seudonimo='QTKX640324BQWOS4IN', telefono='6104677944', posicion='Delantero', numero=7, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=99)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(698):
                obj = Jugador(id=698, liga_id=8, nombre='Raúl Cruz', seudonimo='SXRQ932618TT4U5TAB', telefono='6985963812', posicion='Defensa', numero=19, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=99)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(699):
                obj = Jugador(id=699, liga_id=8, nombre='Nazario Torres', seudonimo='BMUS256101UEBIPLY7', telefono='6259693383', posicion='Defensa', numero=17, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=99)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(700):
                obj = Jugador(id=700, liga_id=8, nombre='Iván Flores', seudonimo='EFYN86914439EQCIR5', telefono='6118013553', posicion='Mediocampista', numero=14, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=99)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(701):
                obj = Jugador(id=701, liga_id=8, nombre='Rogelio Leiva', seudonimo='BGYI003935XJNN9A9J', telefono='6752107703', posicion='Defensa', numero=12, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=99)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(702):
                obj = Jugador(id=702, liga_id=8, nombre='Andrés Cárdenas', seudonimo='EQVV3437946SBA6K9K', telefono='6639876668', posicion='Lateral Izquierdo', numero=22, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=99)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(703):
                obj = Jugador(id=703, liga_id=8, nombre='Onésimo Navarro', seudonimo='PQMS442043P9OOZSUL', telefono='6585436109', posicion='Lateral Derecho', numero=15, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=99)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(704):
                obj = Jugador(id=704, liga_id=8, nombre='Hugo Rivera', seudonimo='CYHI0826170O8WKMI6', telefono='6971301605', posicion='Mediocampista', numero=30, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=99)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(705):
                obj = Jugador(id=705, liga_id=8, nombre='Nazario Morales', seudonimo='UJXX63469414S65GYK', telefono='6801109780', posicion='Mediocampista', numero=3, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=99)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(706):
                obj = Jugador(id=706, liga_id=8, nombre='Yamil Contreras', seudonimo='GJSZ426070O18XTSI8', telefono='6415060540', posicion='Portero', numero=1, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=100)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(707):
                obj = Jugador(id=707, liga_id=8, nombre='Yamil Montes', seudonimo='BKNA678427YTSI9926', telefono='6656871876', posicion='Defensa', numero=5, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=100)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(708):
                obj = Jugador(id=708, liga_id=8, nombre='Erick García', seudonimo='ASHE7063574BLIXAAZ', telefono='6885457049', posicion='Delantero', numero=26, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=100)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(709):
                obj = Jugador(id=709, liga_id=8, nombre='Marcos Romero', seudonimo='WRQQ1851925X1A7FTX', telefono='6233511824', posicion='Mediocampista', numero=22, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=100)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(710):
                obj = Jugador(id=710, liga_id=8, nombre='Rafael Orozco', seudonimo='XHGP795545DJOA45PD', telefono='6921414623', posicion='Lateral Derecho', numero=18, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=100)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(711):
                obj = Jugador(id=711, liga_id=8, nombre='Alfredo Vidal', seudonimo='BAXN05701811CP56NG', telefono='6249947814', posicion='Delantero', numero=14, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=100)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(712):
                obj = Jugador(id=712, liga_id=8, nombre='Lamberto Vega', seudonimo='BPYM215442FWAI7E2Y', telefono='6675870458', posicion='Mediocampista', numero=6, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=100)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(713):
                obj = Jugador(id=713, liga_id=8, nombre='Manuel Ibáñez', seudonimo='PXDC9595131EDYT8CJ', telefono='6894784946', posicion='Mediocampista', numero=19, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=100)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(714):
                obj = Jugador(id=714, liga_id=8, nombre='Kevin Camacho', seudonimo='NRPF210217FS59HNRX', telefono='6206163683', posicion='Lateral Izquierdo', numero=7, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=100)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(715):
                obj = Jugador(id=715, liga_id=8, nombre='Francisco Cruz', seudonimo='VOIV157182QMLMV5L6', telefono='6899644947', posicion='Defensa', numero=23, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=100)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(716):
                obj = Jugador(id=716, liga_id=8, nombre='Javier Ávila', seudonimo='AGJE427433B4ADPP4Q', telefono='6131562383', posicion='Portero', numero=1, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=101)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(717):
                obj = Jugador(id=717, liga_id=8, nombre='Juan Delgado', seudonimo='WGBF36730752BGYLZZ', telefono='6351747103', posicion='Defensa', numero=11, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=101)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(718):
                obj = Jugador(id=718, liga_id=8, nombre='Lucio Reyes', seudonimo='WRSS751226PPFV2VU6', telefono='6855100540', posicion='Defensa', numero=13, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=101)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(719):
                obj = Jugador(id=719, liga_id=8, nombre='Maximiliano Acosta', seudonimo='SMRG190165D41OQZB1', telefono='6257163200', posicion='Defensa', numero=9, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=101)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(720):
                obj = Jugador(id=720, liga_id=8, nombre='Lázaro Domínguez', seudonimo='IVCE374688LNKM5D9J', telefono='6412728436', posicion='Mediocampista', numero=21, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=101)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(721):
                obj = Jugador(id=721, liga_id=8, nombre='Jorge Ramos', seudonimo='HYRA076766Q5K9Z7VP', telefono='6533505619', posicion='Mediocampista', numero=27, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=101)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(722):
                obj = Jugador(id=722, liga_id=8, nombre='Lucio Sánchez', seudonimo='NCZJ0208456YCWOI8A', telefono='6286807591', posicion='Mediocampista', numero=20, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=101)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(723):
                obj = Jugador(id=723, liga_id=8, nombre='Arturo Reyes', seudonimo='FJLV2095671YX81CCC', telefono='6254694191', posicion='Lateral Derecho', numero=26, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=101)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(724):
                obj = Jugador(id=724, liga_id=8, nombre='Leonel López', seudonimo='AZAO6421034V265MGS', telefono='6901688354', posicion='Delantero', numero=10, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=101)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(725):
                obj = Jugador(id=725, liga_id=8, nombre='Agustín Rojas', seudonimo='BLRM530593GMSMXS92', telefono='6582146970', posicion='Lateral Izquierdo', numero=7, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=101)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(726):
                obj = Jugador(id=726, liga_id=8, nombre='Roberto Guerrero', seudonimo='AWCW272921RA8GWWIH', telefono='6307483805', posicion='Portero', numero=1, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=102)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(727):
                obj = Jugador(id=727, liga_id=8, nombre='Gilberto Medina', seudonimo='XLSD7518147L344FY2', telefono='6596302034', posicion='Delantero', numero=25, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=102)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(728):
                obj = Jugador(id=728, liga_id=8, nombre='Edwin Guerrero', seudonimo='TQUL919788TKDX4KMD', telefono='6995623182', posicion='Lateral Derecho', numero=12, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=102)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(729):
                obj = Jugador(id=729, liga_id=8, nombre='Longinos Briones', seudonimo='SNTB137766Q1TYQEMF', telefono='6741523277', posicion='Mediocampista', numero=19, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=102)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(730):
                obj = Jugador(id=730, liga_id=8, nombre='Miguel Mercado', seudonimo='XUDZ322822O2EYQ1FM', telefono='6321189515', posicion='Delantero', numero=11, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=102)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(731):
                obj = Jugador(id=731, liga_id=8, nombre='Alessandro Flores', seudonimo='NLIZ894343LBNVGUHT', telefono='6808366727', posicion='Mediocampista', numero=23, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=102)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(732):
                obj = Jugador(id=732, liga_id=8, nombre='Patrick Escalante', seudonimo='SIYD6217995SV6NI59', telefono='6812731322', posicion='Lateral Izquierdo', numero=7, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=102)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(733):
                obj = Jugador(id=733, liga_id=8, nombre='Rodrigo Carrillo', seudonimo='CCJB594996XV9GYL4D', telefono='6532632600', posicion='Mediocampista', numero=21, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=102)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(734):
                obj = Jugador(id=734, liga_id=8, nombre='Misael Contreras', seudonimo='ZOLU34088695RYQTDQ', telefono='6373824247', posicion='Defensa', numero=6, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=102)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(735):
                obj = Jugador(id=735, liga_id=8, nombre='Severino Díaz', seudonimo='FKMP993614HDZSS06K', telefono='6114757199', posicion='Defensa', numero=9, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=102)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(736):
                obj = Jugador(id=736, liga_id=8, nombre='Demetrio Ramírez', seudonimo='WPDH8121183OAIOZ3B', telefono='6436766676', posicion='Portero', numero=1, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=103)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(737):
                obj = Jugador(id=737, liga_id=8, nombre='Saturnino Acosta', seudonimo='XHIW694674TJ2329LJ', telefono='6806802611', posicion='Delantero', numero=4, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=103)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(738):
                obj = Jugador(id=738, liga_id=8, nombre='Fernando Ramos', seudonimo='EAGC3606788H329C8Q', telefono='6603984001', posicion='Lateral Izquierdo', numero=15, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=103)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(739):
                obj = Jugador(id=739, liga_id=8, nombre='Lucio Fuentes', seudonimo='CIXN3436061SX264FO', telefono='6516672763', posicion='Mediocampista', numero=11, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=103)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(740):
                obj = Jugador(id=740, liga_id=8, nombre='Nicanor Medina', seudonimo='ATFN132638Z87XD93K', telefono='6859637019', posicion='Defensa', numero=26, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=103)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(741):
                obj = Jugador(id=741, liga_id=8, nombre='Manuel Núñez', seudonimo='TWMO120715Z0YBUXNP', telefono='6958207325', posicion='Lateral Derecho', numero=9, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=103)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(742):
                obj = Jugador(id=742, liga_id=8, nombre='Jacinto Gutiérrez', seudonimo='UNVZ2618095ROGHM9Y', telefono='6178547839', posicion='Mediocampista', numero=5, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=103)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(743):
                obj = Jugador(id=743, liga_id=8, nombre='Constantino Torres', seudonimo='JEWK303789BLDU2G8L', telefono='6505252132', posicion='Delantero', numero=8, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=103)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(744):
                obj = Jugador(id=744, liga_id=8, nombre='Julio Leiva', seudonimo='OMWS92382005IWXIRV', telefono='6294392276', posicion='Defensa', numero=7, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=103)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(745):
                obj = Jugador(id=745, liga_id=8, nombre='Omar Luna', seudonimo='MACZ404007CSBSYT7F', telefono='6645455260', posicion='Mediocampista', numero=25, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=103)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(746):
                obj = Jugador(id=746, liga_id=8, nombre='Ricardo Reyes', seudonimo='SJYE625297IACCW03G', telefono='6258321146', posicion='Portero', numero=1, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=104)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(747):
                obj = Jugador(id=747, liga_id=8, nombre='Federico Cruz', seudonimo='HJPQ699517YZNSTFQX', telefono='6696554892', posicion='Mediocampista', numero=26, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=104)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(748):
                obj = Jugador(id=748, liga_id=8, nombre='Eduardo Salazar', seudonimo='ZXBU076954H5KJQ4WQ', telefono='6622264772', posicion='Lateral Izquierdo', numero=4, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=104)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(749):
                obj = Jugador(id=749, liga_id=8, nombre='Zacarías Montes', seudonimo='GSTW978670YIY08B52', telefono='6414129628', posicion='Defensa', numero=28, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=104)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(750):
                obj = Jugador(id=750, liga_id=8, nombre='Leonardo Rangel', seudonimo='ZQJD8550501SKKH7UL', telefono='6139196934', posicion='Delantero', numero=5, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=104)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(751):
                obj = Jugador(id=751, liga_id=8, nombre='Edwin Domínguez', seudonimo='LPXU238890YBLQD42U', telefono='6277792347', posicion='Mediocampista', numero=21, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=104)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(752):
                obj = Jugador(id=752, liga_id=8, nombre='Maximiliano Cervantes', seudonimo='MKQE010998GM9DES3L', telefono='6133154750', posicion='Defensa', numero=18, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=104)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(753):
                obj = Jugador(id=753, liga_id=8, nombre='Pantaleón Montoya', seudonimo='KHDP762932FHM58FVH', telefono='6998109665', posicion='Lateral Derecho', numero=25, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=104)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(754):
                obj = Jugador(id=754, liga_id=8, nombre='Rigoberto Valdez', seudonimo='HRYP15093222I3BVOS', telefono='6864903051', posicion='Defensa', numero=2, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=104)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(755):
                obj = Jugador(id=755, liga_id=8, nombre='Gustavo Díaz', seudonimo='KHBW4790056O38QKZY', telefono='6249479580', posicion='Mediocampista', numero=3, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=104)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(756):
                obj = Jugador(id=756, liga_id=8, nombre='Próspero Briones', seudonimo='BNWJ462575DCSPJBYZ', telefono='6115697319', posicion='Portero', numero=1, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=105)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(757):
                obj = Jugador(id=757, liga_id=8, nombre='Rigoberto Paredes', seudonimo='DUEC201428A73JC9VB', telefono='6302386265', posicion='Defensa', numero=25, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=105)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(758):
                obj = Jugador(id=758, liga_id=8, nombre='Guillermo Camacho', seudonimo='IIHW052483MT6AUHXM', telefono='6964843114', posicion='Lateral Izquierdo', numero=11, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=105)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(759):
                obj = Jugador(id=759, liga_id=8, nombre='Nazario Salazar', seudonimo='SHMY623098E45995H7', telefono='6926270931', posicion='Mediocampista', numero=2, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=105)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(760):
                obj = Jugador(id=760, liga_id=8, nombre='Maximiliano Mendoza', seudonimo='UMUT609253FJDXX8E2', telefono='6358094840', posicion='Delantero', numero=9, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=105)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(761):
                obj = Jugador(id=761, liga_id=8, nombre='Cristóbal González', seudonimo='HWBV70803209YNU1Z5', telefono='6933306959', posicion='Mediocampista', numero=27, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=105)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(762):
                obj = Jugador(id=762, liga_id=8, nombre='Ramiro Orozco', seudonimo='CMZB975731Z2Q87BPE', telefono='6826993322', posicion='Defensa', numero=19, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=105)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(763):
                obj = Jugador(id=763, liga_id=8, nombre='Bruno Sánchez', seudonimo='JEWC1767790J8CN8Y2', telefono='6696616248', posicion='Defensa', numero=6, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=105)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(764):
                obj = Jugador(id=764, liga_id=8, nombre='Gonzalo Fuentes', seudonimo='AZAS860573THUH7MTM', telefono='6782110754', posicion='Mediocampista', numero=23, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=105)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(765):
                obj = Jugador(id=765, liga_id=8, nombre='Sergio Carrillo', seudonimo='PEXV643683UY7VO4JP', telefono='6951410915', posicion='Delantero', numero=17, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=105)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(766):
                obj = Jugador(id=766, liga_id=8, nombre='Pantaleón Paredes', seudonimo='HLFG905306NPQFESLP', telefono='6352333343', posicion='Portero', numero=1, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=106)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(767):
                obj = Jugador(id=767, liga_id=8, nombre='Jorge Sánchez', seudonimo='GXPO597731MTBGWCEW', telefono='6445357981', posicion='Delantero', numero=10, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=106)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(768):
                obj = Jugador(id=768, liga_id=8, nombre='Samuel García', seudonimo='HMLI829049TX8O7XZA', telefono='6622497036', posicion='Mediocampista', numero=20, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=106)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(769):
                obj = Jugador(id=769, liga_id=8, nombre='Onésimo Argueta', seudonimo='ANYS2354064WUF5CKH', telefono='6114688349', posicion='Defensa', numero=11, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=106)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(770):
                obj = Jugador(id=770, liga_id=8, nombre='Manuel Núñez', seudonimo='NPGV334660ESCG9GGW', telefono='6659041395', posicion='Mediocampista', numero=30, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=106)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(771):
                obj = Jugador(id=771, liga_id=8, nombre='Cándido Acosta', seudonimo='TCQB253556OIM032FK', telefono='6402038151', posicion='Defensa', numero=22, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=106)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(772):
                obj = Jugador(id=772, liga_id=8, nombre='Néstor Díaz', seudonimo='JCIL162451PVRR0KJ8', telefono='6728131615', posicion='Lateral Izquierdo', numero=26, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=106)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(773):
                obj = Jugador(id=773, liga_id=8, nombre='Onofre Moreno', seudonimo='MOFF198870Q5YA6JVV', telefono='6494318081', posicion='Lateral Derecho', numero=4, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=106)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(774):
                obj = Jugador(id=774, liga_id=8, nombre='Rodrigo Ortiz', seudonimo='LVKT199696VL5NYMKL', telefono='6182763163', posicion='Mediocampista', numero=16, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=106)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(775):
                obj = Jugador(id=775, liga_id=8, nombre='Jacinto Hidalgo', seudonimo='FWXT2227302L4KAG0Q', telefono='6389416157', posicion='Defensa', numero=23, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=106)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(776):
                obj = Jugador(id=776, liga_id=8, nombre='Hector Flores', seudonimo='LJYT218100G4N0H13T', telefono='6771911726', posicion='Portero', numero=1, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=107)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(777):
                obj = Jugador(id=777, liga_id=8, nombre='Óscar Montes', seudonimo='ZSBX023979YQK7QLTR', telefono='6764294204', posicion='Defensa', numero=24, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=107)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(778):
                obj = Jugador(id=778, liga_id=8, nombre='Leonardo Morales', seudonimo='IJLM601141N806ZP3H', telefono='6984839533', posicion='Delantero', numero=3, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=107)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(779):
                obj = Jugador(id=779, liga_id=8, nombre='Ulises Guerrero', seudonimo='PNBI641035MZG9I7TK', telefono='6396890596', posicion='Mediocampista', numero=19, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=107)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(780):
                obj = Jugador(id=780, liga_id=8, nombre='Ernesto González', seudonimo='YOHW058687P0NB69AY', telefono='6338378209', posicion='Lateral Izquierdo', numero=20, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=107)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(781):
                obj = Jugador(id=781, liga_id=8, nombre='Lamberto Rivera', seudonimo='IKMP891375KJWEBCNB', telefono='6267240533', posicion='Defensa', numero=11, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=107)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(782):
                obj = Jugador(id=782, liga_id=8, nombre='Cándido Ortiz', seudonimo='MZLH088616HRM0JJNW', telefono='6829914536', posicion='Mediocampista', numero=17, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=107)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(783):
                obj = Jugador(id=783, liga_id=8, nombre='Macario Espinoza', seudonimo='SAIN534036OYD52WUZ', telefono='6236168908', posicion='Lateral Derecho', numero=13, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=107)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(784):
                obj = Jugador(id=784, liga_id=8, nombre='Melitón Navarro', seudonimo='UZJR599118HB5DD7V2', telefono='6893628142', posicion='Delantero', numero=25, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=107)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(785):
                obj = Jugador(id=785, liga_id=8, nombre='Irving Ramírez', seudonimo='KRUY587786KCUYBCP0', telefono='6245243444', posicion='Defensa', numero=15, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=107)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(786):
                obj = Jugador(id=786, liga_id=8, nombre='Pedro Herrera', seudonimo='VNCF2133099CER3341', telefono='6882466975', posicion='Portero', numero=1, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=108)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(787):
                obj = Jugador(id=787, liga_id=8, nombre='Claudio Hidalgo', seudonimo='OWIY944127OY2R2OOV', telefono='6444322663', posicion='Mediocampista', numero=19, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=108)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(788):
                obj = Jugador(id=788, liga_id=8, nombre='Cristóbal Ramos', seudonimo='LVSL340783C7SU4EJH', telefono='6369955463', posicion='Delantero', numero=22, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=108)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(789):
                obj = Jugador(id=789, liga_id=8, nombre='Simón Delgado', seudonimo='TIOL967315IME05LUK', telefono='6239518849', posicion='Defensa', numero=13, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=108)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(790):
                obj = Jugador(id=790, liga_id=8, nombre='Bryan Rivera', seudonimo='KZYH8690698VCCETNW', telefono='6273381013', posicion='Lateral Derecho', numero=26, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=108)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(791):
                obj = Jugador(id=791, liga_id=8, nombre='Florián Ávila', seudonimo='IMZK779431CFM3CTE7', telefono='6225435402', posicion='Delantero', numero=25, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=108)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(792):
                obj = Jugador(id=792, liga_id=8, nombre='Andrés Espinoza', seudonimo='AVHT5461081QMK60OZ', telefono='6548867552', posicion='Mediocampista', numero=29, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=108)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(793):
                obj = Jugador(id=793, liga_id=8, nombre='Querubín Medina', seudonimo='CFSV163027XUVBSZ7A', telefono='6732389258', posicion='Mediocampista', numero=12, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=108)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(794):
                obj = Jugador(id=794, liga_id=8, nombre='Sergio Alcántara', seudonimo='UQYC689715FJ2HG2AR', telefono='6397290081', posicion='Defensa', numero=20, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=108)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(795):
                obj = Jugador(id=795, liga_id=8, nombre='Gustavo Cárdenas', seudonimo='DUTH815601NJDWNGNA', telefono='6373469729', posicion='Lateral Izquierdo', numero=3, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=108)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(796):
                obj = Jugador(id=796, liga_id=8, nombre='Alexis Hernández', seudonimo='JEIS70377286DIEUUI', telefono='6954262745', posicion='Portero', numero=1, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=109)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(797):
                obj = Jugador(id=797, liga_id=8, nombre='Claudio Núñez', seudonimo='TYAP634066M2EYL8K1', telefono='6261415964', posicion='Defensa', numero=18, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=109)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(798):
                obj = Jugador(id=798, liga_id=8, nombre='Mauricio Romero', seudonimo='AEET6817882I3QATA7', telefono='6302388977', posicion='Lateral Derecho', numero=16, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=109)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(799):
                obj = Jugador(id=799, liga_id=8, nombre='Bryan Valdez', seudonimo='QSYY300067NDJQ84M2', telefono='6367675015', posicion='Defensa', numero=22, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=109)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(800):
                obj = Jugador(id=800, liga_id=8, nombre='Aurelio Hidalgo', seudonimo='EAPM6948739FZXCIB8', telefono='6187723707', posicion='Delantero', numero=25, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=109)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(801):
                obj = Jugador(id=801, liga_id=8, nombre='Erick Montes', seudonimo='YZTZ698230RTQIR13D', telefono='6762909069', posicion='Delantero', numero=17, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=109)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(802):
                obj = Jugador(id=802, liga_id=8, nombre='Rodrigo Guerrero', seudonimo='RDVM498169YKIX059R', telefono='6102123912', posicion='Mediocampista', numero=30, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=109)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(803):
                obj = Jugador(id=803, liga_id=8, nombre='Toribio Fuentes', seudonimo='WDFM6407276NHHCS7B', telefono='6886964550', posicion='Mediocampista', numero=6, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=109)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(804):
                obj = Jugador(id=804, liga_id=8, nombre='Cristóbal Escalante', seudonimo='USGI625615EDD3K76S', telefono='6378499194', posicion='Mediocampista', numero=29, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=109)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(805):
                obj = Jugador(id=805, liga_id=8, nombre='Ernesto Bermúdez', seudonimo='JVAT217223KJEI47XR', telefono='6236421115', posicion='Defensa', numero=28, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=109)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(806):
                obj = Jugador(id=806, liga_id=8, nombre='Telesforo Díaz', seudonimo='LJTO3826259C7ANUN4', telefono='6879036653', posicion='Portero', numero=1, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=110)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(807):
                obj = Jugador(id=807, liga_id=8, nombre='Jesús Guerrero', seudonimo='CQWY933978614TFJQJ', telefono='6225470025', posicion='Mediocampista', numero=15, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=110)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(808):
                obj = Jugador(id=808, liga_id=8, nombre='Alfredo Rangel', seudonimo='DEIJ514707W04TLL7J', telefono='6689908140', posicion='Lateral Derecho', numero=17, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=110)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(809):
                obj = Jugador(id=809, liga_id=8, nombre='Ezequiel Carrillo', seudonimo='ETMD9442655TJII0WF', telefono='6458870808', posicion='Delantero', numero=25, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=110)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(810):
                obj = Jugador(id=810, liga_id=8, nombre='Bruno Alcántara', seudonimo='HPOR310424L9E5D7G1', telefono='6728696340', posicion='Mediocampista', numero=14, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=110)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(811):
                obj = Jugador(id=811, liga_id=8, nombre='Fidel Montoya', seudonimo='EDVV802050LFXUQ9S7', telefono='6451240542', posicion='Defensa', numero=20, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=110)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(812):
                obj = Jugador(id=812, liga_id=8, nombre='Enrique De la Rosa', seudonimo='KCOF917493O2BRAZ81', telefono='6548290746', posicion='Delantero', numero=10, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=110)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(813):
                obj = Jugador(id=813, liga_id=8, nombre='Remigio Ávila', seudonimo='CYSF337549LHPLT3SA', telefono='6973126530', posicion='Defensa', numero=30, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=110)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(814):
                obj = Jugador(id=814, liga_id=8, nombre='Ramón González', seudonimo='RDSD758483TVQTLFLX', telefono='6221200918', posicion='Lateral Izquierdo', numero=7, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=110)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(815):
                obj = Jugador(id=815, liga_id=8, nombre='Guillermo Navarro', seudonimo='RQHO360488O2WJM5AC', telefono='6529260540', posicion='Mediocampista', numero=19, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=110)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(816):
                obj = Jugador(id=816, liga_id=8, nombre='Abraham Peña', seudonimo='HDJK257928CF85E915', telefono='6447257201', posicion='Portero', numero=1, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=111)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(817):
                obj = Jugador(id=817, liga_id=8, nombre='Fernando De la Rosa', seudonimo='JASE4557813PF9S402', telefono='6267063565', posicion='Defensa', numero=18, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=111)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(818):
                obj = Jugador(id=818, liga_id=8, nombre='Onésimo Castro', seudonimo='HZIK106649F4VH68SS', telefono='6877060811', posicion='Defensa', numero=26, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=111)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(819):
                obj = Jugador(id=819, liga_id=8, nombre='Daniel Paredes', seudonimo='LLZT168474HOWWP2NU', telefono='6332291851', posicion='Lateral Derecho', numero=17, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=111)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(820):
                obj = Jugador(id=820, liga_id=8, nombre='Gerardo Vidal', seudonimo='WRKJ7328134CG5GW6I', telefono='6344666783', posicion='Delantero', numero=7, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=111)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(821):
                obj = Jugador(id=821, liga_id=8, nombre='Zacarías López', seudonimo='XCOU333630JDE7EU6Z', telefono='6411381820', posicion='Lateral Izquierdo', numero=10, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=111)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(822):
                obj = Jugador(id=822, liga_id=8, nombre='Ramiro Ibáñez', seudonimo='HSBA249003ZJ89TIQA', telefono='6712421517', posicion='Mediocampista', numero=14, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=111)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(823):
                obj = Jugador(id=823, liga_id=8, nombre='Zacarías Argueta', seudonimo='NKTA277282IPVW6H98', telefono='6836631669', posicion='Delantero', numero=16, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=111)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(824):
                obj = Jugador(id=824, liga_id=8, nombre='Eduardo Argueta', seudonimo='NBKL617409Y2CB2YTZ', telefono='6473174257', posicion='Mediocampista', numero=23, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=111)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(825):
                obj = Jugador(id=825, liga_id=8, nombre='Alejandro Salazar', seudonimo='MHCU918915F9A7QN8M', telefono='6578555805', posicion='Defensa', numero=20, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=111)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(826):
                obj = Jugador(id=826, liga_id=8, nombre='Exequiel Aguilar', seudonimo='HDUB20831574HNGY7G', telefono='6626163249', posicion='Portero', numero=1, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=112)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(827):
                obj = Jugador(id=827, liga_id=8, nombre='Celestino Cruz', seudonimo='WCTX9205330FB95AE1', telefono='6612880534', posicion='Mediocampista', numero=24, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=112)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(828):
                obj = Jugador(id=828, liga_id=8, nombre='Celestino Ramírez', seudonimo='VIUG241008GHNMERB9', telefono='6508737219', posicion='Defensa', numero=30, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=112)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(829):
                obj = Jugador(id=829, liga_id=8, nombre='Federico Moreno', seudonimo='TYFD430281KYZ8T116', telefono='6932075395', posicion='Defensa', numero=9, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=112)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(830):
                obj = Jugador(id=830, liga_id=8, nombre='Claudio Cruz', seudonimo='WRYI8375415E64UYZE', telefono='6702609843', posicion='Mediocampista', numero=28, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=112)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(831):
                obj = Jugador(id=831, liga_id=8, nombre='Pacífico Argueta', seudonimo='MMLE584627WZDJLUAT', telefono='6755442165', posicion='Mediocampista', numero=19, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=112)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(832):
                obj = Jugador(id=832, liga_id=8, nombre='Diego Escalante', seudonimo='BLNM837019ZX0SNUZ4', telefono='6882446218', posicion='Lateral Izquierdo', numero=14, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=112)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(833):
                obj = Jugador(id=833, liga_id=8, nombre='Arturo Navarro', seudonimo='UYBY487237L7YV48XI', telefono='6521677033', posicion='Defensa', numero=21, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=112)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(834):
                obj = Jugador(id=834, liga_id=8, nombre='Fulgencio Orozco', seudonimo='NCVJ496342WU61WXVG', telefono='6839321512', posicion='Lateral Derecho', numero=15, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=112)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(835):
                obj = Jugador(id=835, liga_id=8, nombre='Abraham Espinoza', seudonimo='LFFS8273974WYGGEMV', telefono='6827719640', posicion='Delantero', numero=2, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=112)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(836):
                obj = Jugador(id=836, liga_id=8, nombre='Misael Romero', seudonimo='QJNR359001F114QVR9', telefono='6405689125', posicion='Portero', numero=1, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=113)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(837):
                obj = Jugador(id=837, liga_id=8, nombre='Alejandro García', seudonimo='KOMZ69219178CZU4E7', telefono='6845841335', posicion='Defensa', numero=6, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=113)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(838):
                obj = Jugador(id=838, liga_id=8, nombre='Próspero Herrera', seudonimo='OTSN308115N73KCL85', telefono='6559316524', posicion='Lateral Izquierdo', numero=17, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=113)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(839):
                obj = Jugador(id=839, liga_id=8, nombre='Mateo Orozco', seudonimo='QHBB482559JQEA6CHW', telefono='6327256519', posicion='Defensa', numero=16, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=113)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(840):
                obj = Jugador(id=840, liga_id=8, nombre='Plácido Vega', seudonimo='UQFP887187XON8K44W', telefono='6139480669', posicion='Delantero', numero=19, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=113)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(841):
                obj = Jugador(id=841, liga_id=8, nombre='Fernando Hidalgo', seudonimo='KMZU133947MXM2CT7D', telefono='6537488145', posicion='Defensa', numero=29, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=113)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(842):
                obj = Jugador(id=842, liga_id=8, nombre='Erick De la Rosa', seudonimo='IOTN665983A6CU8ZQR', telefono='6402830641', posicion='Mediocampista', numero=3, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=113)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(843):
                obj = Jugador(id=843, liga_id=8, nombre='Irving Cárdenas', seudonimo='EGVH274789PWJPQI9B', telefono='6224684354', posicion='Lateral Derecho', numero=12, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=113)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(844):
                obj = Jugador(id=844, liga_id=8, nombre='Rafael Alcántara', seudonimo='CXZV527613KQ3RVDZQ', telefono='6363114760', posicion='Mediocampista', numero=7, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=113)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(845):
                obj = Jugador(id=845, liga_id=8, nombre='Onofre Díaz', seudonimo='XKLP715996M8ZW6EAN', telefono='6923020242', posicion='Mediocampista', numero=28, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=113)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(846):
                obj = Jugador(id=846, liga_id=8, nombre='Carlos Mendez', seudonimo=None, telefono=None, posicion=None, numero=None, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=93)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(850):
                obj = Jugador(id=850, liga_id=8, nombre='Andres Lopez', seudonimo=None, telefono=None, posicion=None, numero=None, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=93)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(851):
                obj = Jugador(id=851, liga_id=8, nombre='Mario Ruiz', seudonimo=None, telefono=None, posicion=None, numero=None, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=93)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(852):
                obj = Jugador(id=852, liga_id=8, nombre='David Diaz', seudonimo=None, telefono=None, posicion=None, numero=None, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=93)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(853):
                obj = Jugador(id=853, liga_id=8, nombre='Jorge Hernandez', seudonimo=None, telefono=None, posicion=None, numero=None, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=93)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(854):
                obj = Jugador(id=854, liga_id=8, nombre='Ricardo Silva', seudonimo=None, telefono=None, posicion=None, numero=None, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=93)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(855):
                obj = Jugador(id=855, liga_id=8, nombre='Fernando Torres', seudonimo=None, telefono=None, posicion=None, numero=None, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=93)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(856):
                obj = Jugador(id=856, liga_id=8, nombre='Gabriel Soto', seudonimo=None, telefono=None, posicion=None, numero=None, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=93)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(857):
                obj = Jugador(id=857, liga_id=8, nombre='Jugador 0-0', seudonimo=None, telefono=None, posicion='Defensa', numero=18, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=114)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(860):
                obj = Jugador(id=860, liga_id=8, nombre='Jugador 0-3', seudonimo=None, telefono=None, posicion='Defensa', numero=49, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=114)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(861):
                obj = Jugador(id=861, liga_id=8, nombre='Jugador 0-4', seudonimo=None, telefono=None, posicion='Defensa', numero=58, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=114)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(862):
                obj = Jugador(id=862, liga_id=8, nombre='Jugador 1-0', seudonimo=None, telefono=None, posicion='Defensa', numero=72, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=115)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(865):
                obj = Jugador(id=865, liga_id=8, nombre='Jugador 1-3', seudonimo=None, telefono=None, posicion='Portero', numero=25, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=115)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(866):
                obj = Jugador(id=866, liga_id=8, nombre='Jugador 1-4', seudonimo=None, telefono=None, posicion='Portero', numero=32, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=115)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(868):
                obj = Jugador(id=868, liga_id=8, nombre='Jugador 2-1', seudonimo=None, telefono=None, posicion='Defensa', numero=17, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=116)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(869):
                obj = Jugador(id=869, liga_id=8, nombre='Jugador 2-2', seudonimo=None, telefono=None, posicion='Portero', numero=45, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=116)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(870):
                obj = Jugador(id=870, liga_id=8, nombre='Jugador 2-3', seudonimo=None, telefono=None, posicion='Delantero', numero=54, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=116)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(872):
                obj = Jugador(id=872, liga_id=8, nombre='Jugador 3-0', seudonimo=None, telefono=None, posicion='Delantero', numero=19, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=117)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(873):
                obj = Jugador(id=873, liga_id=8, nombre='Jugador 3-1', seudonimo=None, telefono=None, posicion='Delantero', numero=2, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=117)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(875):
                obj = Jugador(id=875, liga_id=8, nombre='Jugador 3-3', seudonimo=None, telefono=None, posicion='Defensa', numero=69, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=117)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(878):
                obj = Jugador(id=878, liga_id=8, nombre='Jugador 4-1', seudonimo=None, telefono=None, posicion='Portero', numero=64, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=118)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(879):
                obj = Jugador(id=879, liga_id=8, nombre='Jugador 4-2', seudonimo=None, telefono=None, posicion='Defensa', numero=33, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=118)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(881):
                obj = Jugador(id=881, liga_id=8, nombre='Jugador 4-4', seudonimo=None, telefono=None, posicion='Portero', numero=54, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=118)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(882):
                obj = Jugador(id=882, liga_id=8, nombre='Jugador 5-0', seudonimo=None, telefono=None, posicion='Delantero', numero=89, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=119)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(885):
                obj = Jugador(id=885, liga_id=8, nombre='Jugador 5-3', seudonimo=None, telefono=None, posicion='Medio', numero=72, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=119)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(886):
                obj = Jugador(id=886, liga_id=8, nombre='Jugador 5-4', seudonimo=None, telefono=None, posicion='Medio', numero=34, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=119)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(888):
                obj = Jugador(id=888, liga_id=8, nombre='Jugador 6-1', seudonimo=None, telefono=None, posicion='Medio', numero=50, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=120)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(889):
                obj = Jugador(id=889, liga_id=8, nombre='Jugador 6-2', seudonimo=None, telefono=None, posicion='Portero', numero=31, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=120)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(890):
                obj = Jugador(id=890, liga_id=8, nombre='Jugador 6-3', seudonimo=None, telefono=None, posicion='Defensa', numero=61, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=120)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(893):
                obj = Jugador(id=893, liga_id=8, nombre='Jugador 7-1', seudonimo=None, telefono=None, posicion='Medio', numero=21, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=121)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(894):
                obj = Jugador(id=894, liga_id=8, nombre='Jugador 7-2', seudonimo=None, telefono=None, posicion='Medio', numero=52, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=121)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(895):
                obj = Jugador(id=895, liga_id=8, nombre='Jugador 7-3', seudonimo=None, telefono=None, posicion='Defensa', numero=40, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=121)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(898):
                obj = Jugador(id=898, liga_id=8, nombre='Jugador 8-1', seudonimo=None, telefono=None, posicion='Defensa', numero=52, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=122)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(899):
                obj = Jugador(id=899, liga_id=8, nombre='Jugador 8-2', seudonimo=None, telefono=None, posicion='Portero', numero=5, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=122)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(901):
                obj = Jugador(id=901, liga_id=8, nombre='Jugador 8-4', seudonimo=None, telefono=None, posicion='Medio', numero=85, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=122)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(902):
                obj = Jugador(id=902, liga_id=8, nombre='Jugador 9-0', seudonimo=None, telefono=None, posicion='Defensa', numero=83, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=123)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(905):
                obj = Jugador(id=905, liga_id=8, nombre='Jugador 9-3', seudonimo=None, telefono=None, posicion='Medio', numero=94, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=123)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(906):
                obj = Jugador(id=906, liga_id=8, nombre='Jugador 9-4', seudonimo=None, telefono=None, posicion='Portero', numero=8, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=123)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(908):
                obj = Jugador(id=908, liga_id=8, nombre='Jugador 10-1', seudonimo=None, telefono=None, posicion='Delantero', numero=13, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=124)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(909):
                obj = Jugador(id=909, liga_id=8, nombre='Jugador 10-2', seudonimo=None, telefono=None, posicion='Medio', numero=66, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=124)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(911):
                obj = Jugador(id=911, liga_id=8, nombre='Jugador 10-4', seudonimo=None, telefono=None, posicion='Defensa', numero=71, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=124)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(912):
                obj = Jugador(id=912, liga_id=8, nombre='Jugador 11-0', seudonimo=None, telefono=None, posicion='Defensa', numero=34, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=125)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(913):
                obj = Jugador(id=913, liga_id=8, nombre='Jugador 11-1', seudonimo=None, telefono=None, posicion='Delantero', numero=89, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=125)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(914):
                obj = Jugador(id=914, liga_id=8, nombre='Jugador 11-2', seudonimo=None, telefono=None, posicion='Defensa', numero=56, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=125)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(919):
                obj = Jugador(id=919, liga_id=8, nombre='Jugador 12-2', seudonimo=None, telefono=None, posicion='Defensa', numero=17, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=126)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(920):
                obj = Jugador(id=920, liga_id=8, nombre='Jugador 12-3', seudonimo=None, telefono=None, posicion='Defensa', numero=72, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=126)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(921):
                obj = Jugador(id=921, liga_id=8, nombre='Jugador 12-4', seudonimo=None, telefono=None, posicion='Medio', numero=91, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=126)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(923):
                obj = Jugador(id=923, liga_id=8, nombre='Jugador 13-1', seudonimo=None, telefono=None, posicion='Delantero', numero=9, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=127)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(924):
                obj = Jugador(id=924, liga_id=8, nombre='Jugador 13-2', seudonimo=None, telefono=None, posicion='Delantero', numero=60, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=127)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(925):
                obj = Jugador(id=925, liga_id=8, nombre='Jugador 13-3', seudonimo=None, telefono=None, posicion='Delantero', numero=87, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=127)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(928):
                obj = Jugador(id=928, liga_id=8, nombre='Jugador 14-1', seudonimo=None, telefono=None, posicion='Medio', numero=71, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=128)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(929):
                obj = Jugador(id=929, liga_id=8, nombre='Jugador 14-2', seudonimo=None, telefono=None, posicion='Portero', numero=28, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=128)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(930):
                obj = Jugador(id=930, liga_id=8, nombre='Jugador 14-3', seudonimo=None, telefono=None, posicion='Medio', numero=81, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=128)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(934):
                obj = Jugador(id=934, liga_id=8, nombre='Jugador 15-2', seudonimo=None, telefono=None, posicion='Defensa', numero=49, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=129)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(935):
                obj = Jugador(id=935, liga_id=8, nombre='Jugador 15-3', seudonimo=None, telefono=None, posicion='Defensa', numero=82, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=129)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(936):
                obj = Jugador(id=936, liga_id=8, nombre='Jugador 15-4', seudonimo=None, telefono=None, posicion='Medio', numero=93, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=129)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(937):
                obj = Jugador(id=937, liga_id=8, nombre='Jugador 16-0', seudonimo=None, telefono=None, posicion='Defensa', numero=38, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=130)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(938):
                obj = Jugador(id=938, liga_id=8, nombre='Jugador 16-1', seudonimo=None, telefono=None, posicion='Delantero', numero=27, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=130)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(939):
                obj = Jugador(id=939, liga_id=8, nombre='Jugador 16-2', seudonimo=None, telefono=None, posicion='Delantero', numero=79, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=130)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(942):
                obj = Jugador(id=942, liga_id=8, nombre='Jugador 17-0', seudonimo=None, telefono=None, posicion='Medio', numero=34, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=131)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(847):
                obj = Jugador(id=847, liga_id=8, nombre='Luis Garcia', seudonimo=None, telefono=None, posicion=None, numero=None, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=93)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(944):
                obj = Jugador(id=944, liga_id=8, nombre='Jugador 17-2', seudonimo=None, telefono=None, posicion='Portero', numero=46, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=131)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(945):
                obj = Jugador(id=945, liga_id=8, nombre='Jugador 17-3', seudonimo=None, telefono=None, posicion='Delantero', numero=23, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=131)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(946):
                obj = Jugador(id=946, liga_id=8, nombre='Jugador 17-4', seudonimo=None, telefono=None, posicion='Defensa', numero=87, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=131)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(947):
                obj = Jugador(id=947, liga_id=8, nombre='Jugador 18-0', seudonimo=None, telefono=None, posicion='Delantero', numero=66, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=132)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(949):
                obj = Jugador(id=949, liga_id=8, nombre='Jugador 18-2', seudonimo=None, telefono=None, posicion='Delantero', numero=58, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=132)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(950):
                obj = Jugador(id=950, liga_id=8, nombre='Jugador 18-3', seudonimo=None, telefono=None, posicion='Delantero', numero=70, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=132)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(951):
                obj = Jugador(id=951, liga_id=8, nombre='Jugador 18-4', seudonimo=None, telefono=None, posicion='Portero', numero=52, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=132)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(952):
                obj = Jugador(id=952, liga_id=8, nombre='Jugador 19-0', seudonimo=None, telefono=None, posicion='Delantero', numero=83, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=133)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(953):
                obj = Jugador(id=953, liga_id=8, nombre='Jugador 19-1', seudonimo=None, telefono=None, posicion='Medio', numero=81, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=133)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(955):
                obj = Jugador(id=955, liga_id=8, nombre='Jugador 19-3', seudonimo=None, telefono=None, posicion='Delantero', numero=41, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=133)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(956):
                obj = Jugador(id=956, liga_id=8, nombre='Jugador 19-4', seudonimo=None, telefono=None, posicion='Delantero', numero=12, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=133)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(948):
                obj = Jugador(id=948, liga_id=8, nombre='Jugador 18-1', seudonimo=None, telefono=None, posicion='Portero', numero=5, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=True, equipo_id=132)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(954):
                obj = Jugador(id=954, liga_id=8, nombre='Jugador 19-2', seudonimo=None, telefono=None, posicion='Delantero', numero=18, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=True, equipo_id=133)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(957):
                obj = Jugador(id=957, liga_id=8, nombre='Jugador 9-0-0', seudonimo=None, telefono=None, posicion='Defensa', numero=68, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=134)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(958):
                obj = Jugador(id=958, liga_id=8, nombre='Jugador 9-0-1', seudonimo=None, telefono=None, posicion='Medio', numero=86, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=134)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(961):
                obj = Jugador(id=961, liga_id=8, nombre='Jugador 9-0-4', seudonimo=None, telefono=None, posicion='Defensa', numero=92, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=134)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(963):
                obj = Jugador(id=963, liga_id=8, nombre='Jugador 9-1-1', seudonimo=None, telefono=None, posicion='Delantero', numero=76, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=135)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(964):
                obj = Jugador(id=964, liga_id=8, nombre='Jugador 9-1-2', seudonimo=None, telefono=None, posicion='Medio', numero=35, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=135)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(965):
                obj = Jugador(id=965, liga_id=8, nombre='Jugador 9-1-3', seudonimo=None, telefono=None, posicion='Defensa', numero=46, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=135)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(967):
                obj = Jugador(id=967, liga_id=8, nombre='Jugador 9-2-0', seudonimo=None, telefono=None, posicion='Defensa', numero=70, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=136)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(969):
                obj = Jugador(id=969, liga_id=8, nombre='Jugador 9-2-2', seudonimo=None, telefono=None, posicion='Defensa', numero=49, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=136)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(971):
                obj = Jugador(id=971, liga_id=8, nombre='Jugador 9-2-4', seudonimo=None, telefono=None, posicion='Defensa', numero=44, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=136)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(972):
                obj = Jugador(id=972, liga_id=8, nombre='Jugador 9-3-0', seudonimo=None, telefono=None, posicion='Medio', numero=19, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=137)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(974):
                obj = Jugador(id=974, liga_id=8, nombre='Jugador 9-3-2', seudonimo=None, telefono=None, posicion='Delantero', numero=96, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=137)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(975):
                obj = Jugador(id=975, liga_id=8, nombre='Jugador 9-3-3', seudonimo=None, telefono=None, posicion='Delantero', numero=50, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=137)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(977):
                obj = Jugador(id=977, liga_id=8, nombre='Jugador 9-4-0', seudonimo=None, telefono=None, posicion='Delantero', numero=53, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=138)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(978):
                obj = Jugador(id=978, liga_id=8, nombre='Jugador 9-4-1', seudonimo=None, telefono=None, posicion='Medio', numero=58, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=138)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(979):
                obj = Jugador(id=979, liga_id=8, nombre='Jugador 9-4-2', seudonimo=None, telefono=None, posicion='Defensa', numero=62, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=138)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(981):
                obj = Jugador(id=981, liga_id=8, nombre='Jugador 9-4-4', seudonimo=None, telefono=None, posicion='Medio', numero=70, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=138)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(983):
                obj = Jugador(id=983, liga_id=8, nombre='Jugador 9-5-1', seudonimo=None, telefono=None, posicion='Delantero', numero=38, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=139)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(985):
                obj = Jugador(id=985, liga_id=8, nombre='Jugador 9-5-3', seudonimo=None, telefono=None, posicion='Defensa', numero=15, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=139)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(986):
                obj = Jugador(id=986, liga_id=8, nombre='Jugador 9-5-4', seudonimo=None, telefono=None, posicion='Medio', numero=17, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=139)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(987):
                obj = Jugador(id=987, liga_id=8, nombre='Jugador 9-6-0', seudonimo=None, telefono=None, posicion='Delantero', numero=77, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=140)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(988):
                obj = Jugador(id=988, liga_id=8, nombre='Jugador 9-6-1', seudonimo=None, telefono=None, posicion='Delantero', numero=48, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=140)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(990):
                obj = Jugador(id=990, liga_id=8, nombre='Jugador 9-6-3', seudonimo=None, telefono=None, posicion='Delantero', numero=63, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=140)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(992):
                obj = Jugador(id=992, liga_id=8, nombre='Jugador 9-7-0', seudonimo=None, telefono=None, posicion='Delantero', numero=78, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=141)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(994):
                obj = Jugador(id=994, liga_id=8, nombre='Jugador 9-7-2', seudonimo=None, telefono=None, posicion='Defensa', numero=92, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=141)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(996):
                obj = Jugador(id=996, liga_id=8, nombre='Jugador 9-7-4', seudonimo=None, telefono=None, posicion='Medio', numero=12, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=141)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(998):
                obj = Jugador(id=998, liga_id=8, nombre='Jugador 9-8-1', seudonimo=None, telefono=None, posicion='Medio', numero=29, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=142)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(999):
                obj = Jugador(id=999, liga_id=8, nombre='Jugador 9-8-2', seudonimo=None, telefono=None, posicion='Medio', numero=51, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=142)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1000):
                obj = Jugador(id=1000, liga_id=8, nombre='Jugador 9-8-3', seudonimo=None, telefono=None, posicion='Defensa', numero=37, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=142)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1002):
                obj = Jugador(id=1002, liga_id=8, nombre='Jugador 9-9-0', seudonimo=None, telefono=None, posicion='Medio', numero=64, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=143)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1003):
                obj = Jugador(id=1003, liga_id=8, nombre='Jugador 9-9-1', seudonimo=None, telefono=None, posicion='Medio', numero=16, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=143)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1006):
                obj = Jugador(id=1006, liga_id=8, nombre='Jugador 9-9-4', seudonimo=None, telefono=None, posicion='Medio', numero=33, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=143)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1007):
                obj = Jugador(id=1007, liga_id=8, nombre='Jugador 9-10-0', seudonimo=None, telefono=None, posicion='Defensa', numero=18, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=144)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1009):
                obj = Jugador(id=1009, liga_id=8, nombre='Jugador 9-10-2', seudonimo=None, telefono=None, posicion='Delantero', numero=10, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=144)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1011):
                obj = Jugador(id=1011, liga_id=8, nombre='Jugador 9-10-4', seudonimo=None, telefono=None, posicion='Portero', numero=16, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=144)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1013):
                obj = Jugador(id=1013, liga_id=8, nombre='Jugador 9-11-1', seudonimo=None, telefono=None, posicion='Defensa', numero=63, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=145)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1015):
                obj = Jugador(id=1015, liga_id=8, nombre='Jugador 9-11-3', seudonimo=None, telefono=None, posicion='Portero', numero=34, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=145)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(980):
                obj = Jugador(id=980, liga_id=8, nombre='Jugador 9-4-3', seudonimo=None, telefono=None, posicion='Portero', numero=90, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=138)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(959):
                obj = Jugador(id=959, liga_id=8, nombre='Jugador 9-0-2', seudonimo=None, telefono=None, posicion='Portero', numero=64, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=134)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(960):
                obj = Jugador(id=960, liga_id=8, nombre='Jugador 9-0-3', seudonimo=None, telefono=None, posicion='Defensa', numero=28, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=134)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(962):
                obj = Jugador(id=962, liga_id=8, nombre='Jugador 9-1-0', seudonimo=None, telefono=None, posicion='Portero', numero=70, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=135)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(966):
                obj = Jugador(id=966, liga_id=8, nombre='Jugador 9-1-4', seudonimo=None, telefono=None, posicion='Delantero', numero=34, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=135)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(968):
                obj = Jugador(id=968, liga_id=8, nombre='Jugador 9-2-1', seudonimo=None, telefono=None, posicion='Delantero', numero=88, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=136)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(970):
                obj = Jugador(id=970, liga_id=8, nombre='Jugador 9-2-3', seudonimo=None, telefono=None, posicion='Medio', numero=32, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=136)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(973):
                obj = Jugador(id=973, liga_id=8, nombre='Jugador 9-3-1', seudonimo=None, telefono=None, posicion='Portero', numero=69, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=137)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(976):
                obj = Jugador(id=976, liga_id=8, nombre='Jugador 9-3-4', seudonimo=None, telefono=None, posicion='Defensa', numero=95, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=137)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(982):
                obj = Jugador(id=982, liga_id=8, nombre='Jugador 9-5-0', seudonimo=None, telefono=None, posicion='Medio', numero=35, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=139)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(984):
                obj = Jugador(id=984, liga_id=8, nombre='Jugador 9-5-2', seudonimo=None, telefono=None, posicion='Delantero', numero=20, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=139)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(989):
                obj = Jugador(id=989, liga_id=8, nombre='Jugador 9-6-2', seudonimo=None, telefono=None, posicion='Medio', numero=85, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=140)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(991):
                obj = Jugador(id=991, liga_id=8, nombre='Jugador 9-6-4', seudonimo=None, telefono=None, posicion='Medio', numero=89, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=140)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(993):
                obj = Jugador(id=993, liga_id=8, nombre='Jugador 9-7-1', seudonimo=None, telefono=None, posicion='Portero', numero=85, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=141)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(995):
                obj = Jugador(id=995, liga_id=8, nombre='Jugador 9-7-3', seudonimo=None, telefono=None, posicion='Delantero', numero=43, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=141)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(997):
                obj = Jugador(id=997, liga_id=8, nombre='Jugador 9-8-0', seudonimo=None, telefono=None, posicion='Medio', numero=81, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=142)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1001):
                obj = Jugador(id=1001, liga_id=8, nombre='Jugador 9-8-4', seudonimo=None, telefono=None, posicion='Portero', numero=11, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=142)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1004):
                obj = Jugador(id=1004, liga_id=8, nombre='Jugador 9-9-2', seudonimo=None, telefono=None, posicion='Medio', numero=86, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=143)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1005):
                obj = Jugador(id=1005, liga_id=8, nombre='Jugador 9-9-3', seudonimo=None, telefono=None, posicion='Medio', numero=82, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=143)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1008):
                obj = Jugador(id=1008, liga_id=8, nombre='Jugador 9-10-1', seudonimo=None, telefono=None, posicion='Defensa', numero=19, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=144)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1010):
                obj = Jugador(id=1010, liga_id=8, nombre='Jugador 9-10-3', seudonimo=None, telefono=None, posicion='Portero', numero=98, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=144)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1012):
                obj = Jugador(id=1012, liga_id=8, nombre='Jugador 9-11-0', seudonimo=None, telefono=None, posicion='Portero', numero=16, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=145)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1014):
                obj = Jugador(id=1014, liga_id=8, nombre='Jugador 9-11-2', seudonimo=None, telefono=None, posicion='Defensa', numero=48, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=145)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1016):
                obj = Jugador(id=1016, liga_id=8, nombre='Jugador 9-11-4', seudonimo=None, telefono=None, posicion='Portero', numero=40, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=145)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1018):
                obj = Jugador(id=1018, liga_id=8, nombre='Jugador 9-12-1', seudonimo=None, telefono=None, posicion='Delantero', numero=59, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=146)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1019):
                obj = Jugador(id=1019, liga_id=8, nombre='Jugador 9-12-2', seudonimo=None, telefono=None, posicion='Medio', numero=59, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=146)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1020):
                obj = Jugador(id=1020, liga_id=8, nombre='Jugador 9-12-3', seudonimo=None, telefono=None, posicion='Portero', numero=8, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=146)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1021):
                obj = Jugador(id=1021, liga_id=8, nombre='Jugador 9-12-4', seudonimo=None, telefono=None, posicion='Defensa', numero=47, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=146)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1022):
                obj = Jugador(id=1022, liga_id=8, nombre='Jugador 9-13-0', seudonimo=None, telefono=None, posicion='Delantero', numero=39, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=147)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1023):
                obj = Jugador(id=1023, liga_id=8, nombre='Jugador 9-13-1', seudonimo=None, telefono=None, posicion='Delantero', numero=49, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=147)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1026):
                obj = Jugador(id=1026, liga_id=8, nombre='Jugador 9-13-4', seudonimo=None, telefono=None, posicion='Portero', numero=70, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=147)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1027):
                obj = Jugador(id=1027, liga_id=8, nombre='Jugador 9-14-0', seudonimo=None, telefono=None, posicion='Medio', numero=47, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=148)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1029):
                obj = Jugador(id=1029, liga_id=8, nombre='Jugador 9-14-2', seudonimo=None, telefono=None, posicion='Delantero', numero=33, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=148)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1031):
                obj = Jugador(id=1031, liga_id=8, nombre='Jugador 9-14-4', seudonimo=None, telefono=None, posicion='Defensa', numero=6, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=148)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1032):
                obj = Jugador(id=1032, liga_id=8, nombre='Jugador 9-15-0', seudonimo=None, telefono=None, posicion='Defensa', numero=66, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=149)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1033):
                obj = Jugador(id=1033, liga_id=8, nombre='Jugador 9-15-1', seudonimo=None, telefono=None, posicion='Defensa', numero=9, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=149)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1034):
                obj = Jugador(id=1034, liga_id=8, nombre='Jugador 9-15-2', seudonimo=None, telefono=None, posicion='Defensa', numero=62, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=149)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1036):
                obj = Jugador(id=1036, liga_id=8, nombre='Jugador 9-15-4', seudonimo=None, telefono=None, posicion='Portero', numero=44, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=149)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1037):
                obj = Jugador(id=1037, liga_id=8, nombre='Jugador 9-16-0', seudonimo=None, telefono=None, posicion='Medio', numero=22, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=150)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1040):
                obj = Jugador(id=1040, liga_id=8, nombre='Jugador 9-16-3', seudonimo=None, telefono=None, posicion='Delantero', numero=63, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=150)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1041):
                obj = Jugador(id=1041, liga_id=8, nombre='Jugador 9-16-4', seudonimo=None, telefono=None, posicion='Defensa', numero=63, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=150)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1042):
                obj = Jugador(id=1042, liga_id=8, nombre='Jugador 9-17-0', seudonimo=None, telefono=None, posicion='Medio', numero=73, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=151)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1043):
                obj = Jugador(id=1043, liga_id=8, nombre='Jugador 9-17-1', seudonimo=None, telefono=None, posicion='Medio', numero=19, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=151)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1045):
                obj = Jugador(id=1045, liga_id=8, nombre='Jugador 9-17-3', seudonimo=None, telefono=None, posicion='Defensa', numero=15, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=151)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1047):
                obj = Jugador(id=1047, liga_id=8, nombre='Jugador 9-18-0', seudonimo=None, telefono=None, posicion='Defensa', numero=27, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=152)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1048):
                obj = Jugador(id=1048, liga_id=8, nombre='Jugador 9-18-1', seudonimo=None, telefono=None, posicion='Medio', numero=60, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=152)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1051):
                obj = Jugador(id=1051, liga_id=8, nombre='Jugador 9-18-4', seudonimo=None, telefono=None, posicion='Medio', numero=68, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=152)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1053):
                obj = Jugador(id=1053, liga_id=8, nombre='Jugador 9-19-1', seudonimo=None, telefono=None, posicion='Delantero', numero=4, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=153)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1054):
                obj = Jugador(id=1054, liga_id=8, nombre='Jugador 9-19-2', seudonimo=None, telefono=None, posicion='Delantero', numero=41, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=153)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1056):
                obj = Jugador(id=1056, liga_id=8, nombre='Jugador 9-19-4', seudonimo=None, telefono=None, posicion='Medio', numero=89, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=153)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1058):
                obj = Jugador(id=1058, liga_id=8, nombre='Jugador 9-20-1', seudonimo=None, telefono=None, posicion='Defensa', numero=6, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=154)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1060):
                obj = Jugador(id=1060, liga_id=8, nombre='Jugador 9-20-3', seudonimo=None, telefono=None, posicion='Portero', numero=11, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=154)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1061):
                obj = Jugador(id=1061, liga_id=8, nombre='Jugador 9-20-4', seudonimo=None, telefono=None, posicion='Medio', numero=42, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=154)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1062):
                obj = Jugador(id=1062, liga_id=8, nombre='Jugador 9-21-0', seudonimo=None, telefono=None, posicion='Medio', numero=28, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=155)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1065):
                obj = Jugador(id=1065, liga_id=8, nombre='Jugador 9-21-3', seudonimo=None, telefono=None, posicion='Portero', numero=71, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=155)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1066):
                obj = Jugador(id=1066, liga_id=8, nombre='Jugador 9-21-4', seudonimo=None, telefono=None, posicion='Delantero', numero=15, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=155)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1069):
                obj = Jugador(id=1069, liga_id=8, nombre='Jugador 9-22-2', seudonimo=None, telefono=None, posicion='Medio', numero=81, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=156)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1070):
                obj = Jugador(id=1070, liga_id=8, nombre='Jugador 9-22-3', seudonimo=None, telefono=None, posicion='Medio', numero=63, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=156)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1071):
                obj = Jugador(id=1071, liga_id=8, nombre='Jugador 9-22-4', seudonimo=None, telefono=None, posicion='Defensa', numero=9, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=156)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1072):
                obj = Jugador(id=1072, liga_id=8, nombre='Jugador 9-23-0', seudonimo=None, telefono=None, posicion='Medio', numero=32, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=157)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1073):
                obj = Jugador(id=1073, liga_id=8, nombre='Jugador 9-23-1', seudonimo=None, telefono=None, posicion='Medio', numero=11, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=157)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1074):
                obj = Jugador(id=1074, liga_id=8, nombre='Jugador 9-23-2', seudonimo=None, telefono=None, posicion='Defensa', numero=77, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=157)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1075):
                obj = Jugador(id=1075, liga_id=8, nombre='Jugador 9-23-3', seudonimo=None, telefono=None, posicion='Delantero', numero=53, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=157)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1077):
                obj = Jugador(id=1077, liga_id=8, nombre='Jugador 9-24-0', seudonimo=None, telefono=None, posicion='Delantero', numero=49, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=158)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1079):
                obj = Jugador(id=1079, liga_id=8, nombre='Jugador 9-24-2', seudonimo=None, telefono=None, posicion='Portero', numero=75, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=158)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1080):
                obj = Jugador(id=1080, liga_id=8, nombre='Jugador 9-24-3', seudonimo=None, telefono=None, posicion='Medio', numero=21, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=False, equipo_id=158)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(849):
                obj = Jugador(id=849, liga_id=8, nombre='Roberto Flores', seudonimo=None, telefono='', posicion='Delantero', numero=None, fecha_nacimiento=None, foto_url='', firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=138)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(848):
                obj = Jugador(id=848, liga_id=8, nombre='Juan Perez', seudonimo=None, telefono=None, posicion=None, numero=None, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=93)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(940):
                obj = Jugador(id=940, liga_id=8, nombre='Jugador 16-3', seudonimo=None, telefono=None, posicion='Medio', numero=45, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=130)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(941):
                obj = Jugador(id=941, liga_id=8, nombre='Jugador 16-4', seudonimo=None, telefono=None, posicion='Medio', numero=10, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=130)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(943):
                obj = Jugador(id=943, liga_id=8, nombre='Jugador 17-1', seudonimo=None, telefono=None, posicion='Portero', numero=55, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=True, equipo_id=131)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(858):
                obj = Jugador(id=858, liga_id=8, nombre='Jugador 0-1', seudonimo=None, telefono=None, posicion='Portero', numero=49, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=114)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(859):
                obj = Jugador(id=859, liga_id=8, nombre='Jugador 0-2', seudonimo=None, telefono=None, posicion='Portero', numero=83, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=114)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1017):
                obj = Jugador(id=1017, liga_id=8, nombre='Jugador 9-12-0', seudonimo=None, telefono=None, posicion='Portero', numero=87, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=True, equipo_id=146)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1024):
                obj = Jugador(id=1024, liga_id=8, nombre='Jugador 9-13-2', seudonimo=None, telefono=None, posicion='Portero', numero=17, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=147)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1025):
                obj = Jugador(id=1025, liga_id=8, nombre='Jugador 9-13-3', seudonimo=None, telefono=None, posicion='Delantero', numero=49, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=147)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1028):
                obj = Jugador(id=1028, liga_id=8, nombre='Jugador 9-14-1', seudonimo=None, telefono=None, posicion='Portero', numero=65, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=148)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1030):
                obj = Jugador(id=1030, liga_id=8, nombre='Jugador 9-14-3', seudonimo=None, telefono=None, posicion='Delantero', numero=29, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=148)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1035):
                obj = Jugador(id=1035, liga_id=8, nombre='Jugador 9-15-3', seudonimo=None, telefono=None, posicion='Portero', numero=57, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=True, equipo_id=149)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1038):
                obj = Jugador(id=1038, liga_id=8, nombre='Jugador 9-16-1', seudonimo=None, telefono=None, posicion='Portero', numero=17, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=150)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1039):
                obj = Jugador(id=1039, liga_id=8, nombre='Jugador 9-16-2', seudonimo=None, telefono=None, posicion='Delantero', numero=85, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=150)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1044):
                obj = Jugador(id=1044, liga_id=8, nombre='Jugador 9-17-2', seudonimo=None, telefono=None, posicion='Portero', numero=17, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=151)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1046):
                obj = Jugador(id=1046, liga_id=8, nombre='Jugador 9-17-4', seudonimo=None, telefono=None, posicion='Defensa', numero=98, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=151)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1049):
                obj = Jugador(id=1049, liga_id=8, nombre='Jugador 9-18-2', seudonimo=None, telefono=None, posicion='Portero', numero=14, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=152)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1050):
                obj = Jugador(id=1050, liga_id=8, nombre='Jugador 9-18-3', seudonimo=None, telefono=None, posicion='Medio', numero=39, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=152)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1052):
                obj = Jugador(id=1052, liga_id=8, nombre='Jugador 9-19-0', seudonimo=None, telefono=None, posicion='Medio', numero=5, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=153)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1055):
                obj = Jugador(id=1055, liga_id=8, nombre='Jugador 9-19-3', seudonimo=None, telefono=None, posicion='Defensa', numero=72, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=153)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1057):
                obj = Jugador(id=1057, liga_id=8, nombre='Jugador 9-20-0', seudonimo=None, telefono=None, posicion='Portero', numero=11, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=154)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1059):
                obj = Jugador(id=1059, liga_id=8, nombre='Jugador 9-20-2', seudonimo=None, telefono=None, posicion='Medio', numero=17, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=154)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1063):
                obj = Jugador(id=1063, liga_id=8, nombre='Jugador 9-21-1', seudonimo=None, telefono=None, posicion='Portero', numero=80, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=155)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1064):
                obj = Jugador(id=1064, liga_id=8, nombre='Jugador 9-21-2', seudonimo=None, telefono=None, posicion='Defensa', numero=65, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=155)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1067):
                obj = Jugador(id=1067, liga_id=8, nombre='Jugador 9-22-0', seudonimo=None, telefono=None, posicion='Medio', numero=57, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=156)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1068):
                obj = Jugador(id=1068, liga_id=8, nombre='Jugador 9-22-1', seudonimo=None, telefono=None, posicion='Medio', numero=38, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=156)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1076):
                obj = Jugador(id=1076, liga_id=8, nombre='Jugador 9-23-4', seudonimo=None, telefono=None, posicion='Portero', numero=90, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=True, equipo_id=157)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1078):
                obj = Jugador(id=1078, liga_id=8, nombre='Jugador 9-24-1', seudonimo=None, telefono=None, posicion='Portero', numero=20, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=158)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(1081):
                obj = Jugador(id=1081, liga_id=8, nombre='Jugador 9-24-4', seudonimo=None, telefono=None, posicion='Defensa', numero=60, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=158)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(863):
                obj = Jugador(id=863, liga_id=8, nombre='Jugador 1-1', seudonimo=None, telefono=None, posicion='Delantero', numero=31, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=115)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(864):
                obj = Jugador(id=864, liga_id=8, nombre='Jugador 1-2', seudonimo=None, telefono=None, posicion='Portero', numero=49, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=115)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(867):
                obj = Jugador(id=867, liga_id=8, nombre='Jugador 2-0', seudonimo=None, telefono=None, posicion='Portero', numero=70, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=116)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(871):
                obj = Jugador(id=871, liga_id=8, nombre='Jugador 2-4', seudonimo=None, telefono=None, posicion='Delantero', numero=26, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=116)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(874):
                obj = Jugador(id=874, liga_id=8, nombre='Jugador 3-2', seudonimo=None, telefono=None, posicion='Defensa', numero=50, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=117)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(876):
                obj = Jugador(id=876, liga_id=8, nombre='Jugador 3-4', seudonimo=None, telefono=None, posicion='Portero', numero=24, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=117)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(877):
                obj = Jugador(id=877, liga_id=8, nombre='Jugador 4-0', seudonimo=None, telefono=None, posicion='Portero', numero=32, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=118)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(880):
                obj = Jugador(id=880, liga_id=8, nombre='Jugador 4-3', seudonimo=None, telefono=None, posicion='Portero', numero=17, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=118)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(883):
                obj = Jugador(id=883, liga_id=8, nombre='Jugador 5-1', seudonimo=None, telefono=None, posicion='Portero', numero=92, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=119)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(884):
                obj = Jugador(id=884, liga_id=8, nombre='Jugador 5-2', seudonimo=None, telefono=None, posicion='Delantero', numero=76, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=119)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(887):
                obj = Jugador(id=887, liga_id=8, nombre='Jugador 6-0', seudonimo=None, telefono=None, posicion='Portero', numero=13, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=120)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(891):
                obj = Jugador(id=891, liga_id=8, nombre='Jugador 6-4', seudonimo=None, telefono=None, posicion='Medio', numero=99, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=120)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(892):
                obj = Jugador(id=892, liga_id=8, nombre='Jugador 7-0', seudonimo=None, telefono=None, posicion='Portero', numero=49, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=121)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(896):
                obj = Jugador(id=896, liga_id=8, nombre='Jugador 7-4', seudonimo=None, telefono=None, posicion='Defensa', numero=72, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=121)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(897):
                obj = Jugador(id=897, liga_id=8, nombre='Jugador 8-0', seudonimo=None, telefono=None, posicion='Portero', numero=98, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=122)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(900):
                obj = Jugador(id=900, liga_id=8, nombre='Jugador 8-3', seudonimo=None, telefono=None, posicion='Medio', numero=94, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=122)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(903):
                obj = Jugador(id=903, liga_id=8, nombre='Jugador 9-1', seudonimo=None, telefono=None, posicion='Medio', numero=80, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=123)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(904):
                obj = Jugador(id=904, liga_id=8, nombre='Jugador 9-2', seudonimo=None, telefono=None, posicion='Portero', numero=62, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=123)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(907):
                obj = Jugador(id=907, liga_id=8, nombre='Jugador 10-0', seudonimo=None, telefono=None, posicion='Medio', numero=91, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=124)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(910):
                obj = Jugador(id=910, liga_id=8, nombre='Jugador 10-3', seudonimo=None, telefono=None, posicion='Portero', numero=87, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=124)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(915):
                obj = Jugador(id=915, liga_id=8, nombre='Jugador 11-3', seudonimo=None, telefono=None, posicion='Defensa', numero=32, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=125)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(916):
                obj = Jugador(id=916, liga_id=8, nombre='Jugador 11-4', seudonimo=None, telefono=None, posicion='Portero', numero=73, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=125)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(917):
                obj = Jugador(id=917, liga_id=8, nombre='Jugador 12-0', seudonimo=None, telefono=None, posicion='Medio', numero=37, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=126)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(918):
                obj = Jugador(id=918, liga_id=8, nombre='Jugador 12-1', seudonimo=None, telefono=None, posicion='Portero', numero=66, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=126)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(922):
                obj = Jugador(id=922, liga_id=8, nombre='Jugador 13-0', seudonimo=None, telefono=None, posicion='Portero', numero=75, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=127)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(926):
                obj = Jugador(id=926, liga_id=8, nombre='Jugador 13-4', seudonimo=None, telefono=None, posicion='Delantero', numero=40, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=127)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(927):
                obj = Jugador(id=927, liga_id=8, nombre='Jugador 14-0', seudonimo=None, telefono=None, posicion='Portero', numero=54, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=128)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(931):
                obj = Jugador(id=931, liga_id=8, nombre='Jugador 14-4', seudonimo=None, telefono=None, posicion='Defensa', numero=31, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=128)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(932):
                obj = Jugador(id=932, liga_id=8, nombre='Jugador 15-0', seudonimo=None, telefono=None, posicion='Defensa', numero=45, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=False, es_capitan=True, equipo_id=129)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            if not Jugador.query.get(933):
                obj = Jugador(id=933, liga_id=8, nombre='Jugador 15-1', seudonimo=None, telefono=None, posicion='Portero', numero=65, fecha_nacimiento=None, foto_url=None, firma_tutor_url=None, es_portero=True, es_capitan=False, equipo_id=129)
                if hasattr(obj, 'configuracion') and isinstance(obj.configuracion, str): obj.configuracion = json.loads(obj.configuracion)
                db.session.add(obj)
            db.session.commit()
        print('--- Ajustando secuencias de PostgreSQL ---')
        if 'postgresql' in db.engine.url.drivername:
            for table_name in [m.__tablename__ for m in [Usuario, Liga, Cancha, Arbitro, Torneo, Equipo, Jugador]]:
                try:
                    db.session.execute(db.text(f"SELECT setval('{table_name}_id_seq', coalesce((SELECT max(id) FROM {table_name}), 1), (SELECT max(id) FROM {table_name}) IS NOT NULL);"))
                except Exception as e:
                    db.session.rollback()
                    print(f'No se pudo ajustar secuencia {table_name}_id_seq: {e}')
        db.session.commit()
if __name__ == '__main__':
    inject_local_data()