"""
Simula TODA la jornada 1 del torneo activo:
- Crea pares de partidos (round-robin jornada 1)
- Genera resultado realista (0-5 goles por equipo)
- Genera EventoPartido: Gol, Asistencia, Tarjeta Amarilla, Tarjeta Roja, Autogol, Penalti
- Registra asistencias de jugadores
- Marca los partidos como Played
"""
import os, sys, random
from datetime import date, timedelta

sys.stdout.reconfigure(encoding='utf-8')

from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from models import db, Torneo, Equipo, Jugador, Partido, EventoPartido, AsistenciaPartido

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Pesos de tipos de evento (frecuencia relativa por partido)
TIPOS_EVENTO = {
    'Gol':             {'prob': 1.0},  # controlado externamente
    'Tarjeta Amarilla': {'prob': 0.55},
    'Tarjeta Roja':    {'prob': 0.08},
    'Autogol':         {'prob': 0.04},
    'Penalti Fallado': {'prob': 0.05},
}

def minuto_aleatorio(periodo=None):
    if periodo == 1:
        return random.randint(1, 45)
    elif periodo == 2:
        return random.randint(46, 90)
    return random.randint(1, 90)

def simular_partido(partido, equipo_local, equipo_visitante, jugadores_local, jugadores_visitante):
    """Simula un partido completo y crea eventos."""
    # Resultado
    goles_local     = random.choices([0,1,2,3,4,5], weights=[10,25,28,18,12,7])[0]
    goles_visitante = random.choices([0,1,2,3,4,5], weights=[12,26,27,18,11,6])[0]

    partido.goles_local     = goles_local
    partido.goles_visitante = goles_visitante
    partido.estado          = 'Played'

    # Ganador
    if goles_local > goles_visitante:
        partido.ganador_id = equipo_local.id
    elif goles_visitante > goles_local:
        partido.ganador_id = equipo_visitante.id
    else:
        partido.ganador_id = None  # empate

    eventos = []
    minutos_usados = set()

    def minuto_unico():
        for _ in range(50):
            m = random.randint(1, 92)
            if m not in minutos_usados:
                minutos_usados.add(m)
                return m
        return random.randint(1, 92)

    def campo(eq_id, jugadores):
        return [j for j in jugadores if not j.es_portero]

    def portero(jugadores):
        return next((j for j in jugadores if j.es_portero), jugadores[0] if jugadores else None)

    no_porteros_local     = [j for j in jugadores_local if not j.es_portero] or jugadores_local
    no_porteros_visitante = [j for j in jugadores_visitante if not j.es_portero] or jugadores_visitante

    # --- GOLES LOCAL ---
    if no_porteros_local:
        for g in range(goles_local):
            goleador = random.choice(no_porteros_local)
            asistente = random.choice([j for j in no_porteros_local if j.id != goleador.id] or no_porteros_local)
            min_gol = minuto_unico()
            periodo = 1 if min_gol <= 45 else 2

            eventos.append(EventoPartido(
                partido_id=partido.id, equipo_id=equipo_local.id,
                jugador_id=goleador.id, minuto=min_gol,
                tipo='Gol', periodo=periodo, liga_id=partido.liga_id,
                nota=f"⚽ Gol de {goleador.nombre} (#{goleador.numero})"
            ))
            # Asistencia (70% de probabilidad)
            if random.random() < 0.70:
                eventos.append(EventoPartido(
                    partido_id=partido.id, equipo_id=equipo_local.id,
                    jugador_id=asistente.id, minuto=max(1, min_gol - 1),
                    tipo='Asistencia', periodo=periodo, liga_id=partido.liga_id,
                    nota=f"🎯 Asistencia de {asistente.nombre}"
                ))
    else:
        partido.goles_local = 0
        goles_local = 0

    # --- GOLES VISITANTE ---
    if no_porteros_visitante:
        for g in range(goles_visitante):
            goleador = random.choice(no_porteros_visitante)
            asistente = random.choice([j for j in no_porteros_visitante if j.id != goleador.id] or no_porteros_visitante)
            min_gol = minuto_unico()
            periodo = 1 if min_gol <= 45 else 2

            eventos.append(EventoPartido(
                partido_id=partido.id, equipo_id=equipo_visitante.id,
                jugador_id=goleador.id, minuto=min_gol,
                tipo='Gol', periodo=periodo, liga_id=partido.liga_id,
                nota=f"⚽ Gol de {goleador.nombre} (#{goleador.numero})"
            ))
            if random.random() < 0.70:
                eventos.append(EventoPartido(
                    partido_id=partido.id, equipo_id=equipo_visitante.id,
                    jugador_id=asistente.id, minuto=max(1, min_gol - 1),
                    tipo='Asistencia', periodo=periodo, liga_id=partido.liga_id,
                    nota=f"🎯 Asistencia de {asistente.nombre}"
                ))
    else:
        partido.goles_visitante = 0
        goles_visitante = 0

    # --- TARJETAS AMARILLAS (2-5 por partido) ---
    n_amarillas = random.randint(2, 5)
    todos = jugadores_local + jugadores_visitante
    random.shuffle(todos)
    amarillados = set()
    for jug in todos[:n_amarillas]:
        if jug.id in amarillados:
            continue
        eq_id = equipo_local.id if jug in jugadores_local else equipo_visitante.id
        m = minuto_unico()
        eventos.append(EventoPartido(
            partido_id=partido.id, equipo_id=eq_id,
            jugador_id=jug.id, minuto=m,
            tipo='Amarilla', periodo=1 if m <= 45 else 2,
            liga_id=partido.liga_id,
            nota=f"🟡 {jug.nombre} amonestado"
        ))
        amarillados.add(jug.id)

    # --- TARJETA ROJA (10% de probabilidad) ---
    if random.random() < 0.10:
        todos2 = (jugadores_local + jugadores_visitante).copy()
        random.shuffle(todos2)
        expulsado = todos2[0]
        eq_id = equipo_local.id if expulsado in jugadores_local else equipo_visitante.id
        m = minuto_unico()
        eventos.append(EventoPartido(
            partido_id=partido.id, equipo_id=eq_id,
            jugador_id=expulsado.id, minuto=m,
            tipo='Roja', periodo=1 if m <= 45 else 2,
            liga_id=partido.liga_id,
            nota=f"🔴 {expulsado.nombre} expulsado del campo"
        ))

    # --- AUTOGOL (5% probabilidad) ---
    if random.random() < 0.05:
        jug = random.choice(jugadores_local + jugadores_visitante)
        eq_id = equipo_local.id if jug in jugadores_local else equipo_visitante.id
        # El autogol beneficia al equipo contrario
        eq_beneficiado = equipo_visitante.id if eq_id == equipo_local.id else equipo_local.id
        m = minuto_unico()
        eventos.append(EventoPartido(
            partido_id=partido.id, equipo_id=eq_beneficiado,
            jugador_id=jug.id, minuto=m,
            tipo='Autogol', periodo=1 if m <= 45 else 2,
            liga_id=partido.liga_id,
            nota=f"🙈 Autogol de {jug.nombre}"
        ))

    # --- ASISTENCIAS AL PARTIDO (presencia de jugadores) ---
    asistencias = []
    for jug in jugadores_local:
        presente = random.random() < 0.92  # 92% de asistencia
        asistencias.append(AsistenciaPartido(
            partido_id=partido.id, jugador_id=jug.id,
            equipo_id=equipo_local.id, presente=presente,
            liga_id=partido.liga_id
        ))
    for jug in jugadores_visitante:
        presente = random.random() < 0.90
        asistencias.append(AsistenciaPartido(
            partido_id=partido.id, jugador_id=jug.id,
            equipo_id=equipo_visitante.id, presente=presente,
            liga_id=partido.liga_id
        ))

    return eventos, asistencias, goles_local, goles_visitante


with app.app_context():
    # Encontrar torneo activo
    torneo = Torneo.query.filter_by(activo=True).order_by(Torneo.id.desc()).first()
    if not torneo:
        torneo = Torneo.query.order_by(Torneo.id.desc()).first()

    print(f"⚽ Torneo: [{torneo.id}] {torneo.nombre}")

    # Jornada a simular
    JORNADA = 1

    # Verificar partidos existentes en jornada 1
    existentes_list = Partido.query.filter_by(torneo_id=torneo.id, jornada=JORNADA).all()
    if existentes_list:
        print(f"⚠️  Limpiando {len(existentes_list)} partidos previos de la jornada {JORNADA}...")
        pids = [p.id for p in existentes_list]
        EventoPartido.query.filter(EventoPartido.partido_id.in_(pids)).delete(synchronize_session=False)
        AsistenciaPartido.query.filter(AsistenciaPartido.partido_id.in_(pids)).delete(synchronize_session=False)
        Partido.query.filter_by(torneo_id=torneo.id, jornada=JORNADA).delete()
        db.session.commit()
        print("   ✅ Limpieza completada.")

    # Obtener equipos
    equipos = Equipo.query.filter_by(torneo_id=torneo.id).all()
    random.shuffle(equipos)
    print(f"   Equipos en torneo: {len(equipos)}")

    if len(equipos) < 2:
        print("❌ Se necesitan al menos 2 equipos.")
        sys.exit(1)

    # Round robin: si número impar, el último descansa
    if len(equipos) % 2 != 0:
        equipos.append(None)  # bye

    mitad = len(equipos) // 2
    pares = []
    lista = equipos[:]
    for i in range(mitad):
        local = lista[i]
        visitante = lista[-(i+1)]
        if local is not None and visitante is not None:
            pares.append((local, visitante))

    fecha_juego = date.today()
    cancha_nombre = torneo.cancha or "Deportivo Principal"
    
    # Intentar sacar la hora del horario_juego o usar default
    hora_base = "09:00"
    if torneo.horario_juego and ":" in torneo.horario_juego:
        try:
            # Si dice "08:00 a 22:00", tomar la primera parte
            hora_base = torneo.horario_juego.split(' ')[0]
            if ':' not in hora_base: hora_base = "09:00"
        except:
            pass

    total_partidos = 0
    total_goles = 0
    total_eventos = 0

    for idx, (eq_local, eq_vis) in enumerate(pares):
        hora = f"{(10 + idx // 3):02d}:{('00' if idx % 3 == 0 else '30' if idx % 3 == 1 else '00')}"

        # Crear partido
        partido = Partido(
            torneo_id=torneo.id,
            liga_id=torneo.liga_id,
            jornada=JORNADA,
            equipo_local_id=eq_local.id,
            equipo_visitante_id=eq_vis.id,
            fecha=fecha_juego,
            hora=hora,
            cancha=cancha_nombre,
            estado='Played',
            fase='Regular'
        )
        db.session.add(partido)
        db.session.flush()

        # Jugadores de cada equipo
        jugs_local = Jugador.query.filter_by(equipo_id=eq_local.id).all()
        jugs_vis   = Jugador.query.filter_by(equipo_id=eq_vis.id).all()

        eventos, asistencias, gl, gv = simular_partido(partido, eq_local, eq_vis, jugs_local, jugs_vis)

        for ev in eventos:
            db.session.add(ev)
        for asist in asistencias:
            db.session.add(asist)

        total_goles   += gl + gv
        total_eventos += len(eventos)
        total_partidos += 1

        print(f"   [{idx+1:02d}] {eq_local.nombre:22s} {gl} - {gv} {eq_vis.nombre:22s}  "
              f"({len(eventos)} eventos)")

    db.session.commit()

    print(f"\n🏆 Jornada {JORNADA} simulada:")
    print(f"   Partidos jugados : {total_partidos}")
    print(f"   Goles totales    : {total_goles}")
    print(f"   Eventos (goles, tarjetas, asistencias, etc.): {total_eventos}")
    print(f"\nAbre el calendario o el dashboard para ver los resultados!")
