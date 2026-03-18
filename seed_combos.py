import os
import uuid
import random
from app import app
from models import db, Liga, Torneo, Equipo, Jugador, Cancha

def seed_data():
    with app.app_context():
        # Encontrar las 3 ligas más recientes
        recent_ligas = Liga.query.order_by(Liga.id.desc()).limit(3).all()
        
        if not recent_ligas:
            print("No se encontraron ligas para inyectar datos.")
            return

        print(f"Detectadas {len(recent_ligas)} ligas recientes.")
        
        nombres_equipos = [
            "Real Madrid CF", "FC Barcelona", "Manchester City", "Liverpool FC", 
            "Bayern Munich", "PSG", "Inter Milan", "AC Milan", "Juventus", "Arsenal",
            "Atlético Madrid", "Borussia Dortmund", "Chelsea FC", "Napoli", "Benfica",
            "Ajax", "Porto", "Tottenham", "Roma", "Lazio", "Leverkusen", "Aston Villa",
            "Sevilla FC", "Real Betis", "Villarreal", "Real Sociedad", "Athletic Club"
        ]

        posiciones = ["Portero", "Defensa", "Mediocampista", "Delantero"]
        nombres_personas = ["Juan", "Pedro", "Luis", "Carlos", "Roberto", "Miguel", "Angel", "Diego", "Fernando", "Javier"]
        apellidos = ["García", "Rodríguez", "Martínez", "Hernández", "López", "González", "Pérez", "Sánchez", "Ramírez", "Cruz"]

        for liga in recent_ligas:
            print(f"Procesando Liga: {liga.nombre} (ID: {liga.id})")
            
            # 1. Crear Sede (Cancha)
            cancha = Cancha.query.filter_by(liga_id=liga.id).first()
            if not cancha:
                cancha = Cancha(
                    nombre=f"Unidad Deportiva {liga.nombre}",
                    liga_id=liga.id,
                    direccion="Av. Principal #123, Col. Centro",
                    municipio="Ciudad de México",
                    estado="CDMX",
                    tipo="Propia",
                    modalidad="Fútbol 7"
                )
                db.session.add(cancha)
                db.session.flush()
                print(f"  - Creada Sede: {cancha.nombre}")
            else:
                print(f"  - Usando Sede existente: {cancha.nombre}")

            # 2. Crear Torneo si no tiene ninguno activo
            torneo = Torneo.query.filter_by(liga_id=liga.id, archived=False).first()
            if not torneo:
                torneo = Torneo(
                    nombre=f"Torneo Apertura - {liga.nombre}",
                    liga_id=liga.id,
                    tipo="Liga",
                    activo=True,
                    cancha=cancha.nombre
                )
                db.session.add(torneo)
                db.session.flush()
                print(f"  - Creado Torneo: {torneo.nombre}")
            else:
                print(f"  - Usando Torneo existente: {torneo.nombre}")

            # 3. Inyectar entre 15 y 25 equipos
            num_equipos = random.randint(15, 25)
            # Evitar nombres duplicados en la misma liga
            pool_nombres = random.sample(nombres_equipos, min(num_equipos, len(nombres_equipos)))
            
            for i in range(num_equipos):
                nombre_eq = pool_nombres[i] if i < len(pool_nombres) else f"Equipo {i+1} - {liga.nombre}"
                
                # Verificar si ya existe el equipo por nombre en ese torneo
                if Equipo.query.filter_by(nombre=nombre_eq, torneo_id=torneo.id).first():
                    continue

                equipo = Equipo(
                    nombre=nombre_eq,
                    torneo_id=torneo.id,
                    liga_id=liga.id,
                    uid=f"EQ-{uuid.uuid4().hex[:8].upper()}",
                    email=f"delegado_{uuid.uuid4().hex[:4]}@mail.com"
                )
                db.session.add(equipo)
                db.session.flush()

                # 4. Inyectar 10-15 jugadores por equipo
                num_jugadores = random.randint(10, 15)
                for j in range(num_jugadores):
                    nom = random.choice(nombres_personas)
                    ape = random.choice(apellidos)
                    pos = random.choice(posiciones)
                    
                    jugador = Jugador(
                        nombre=f"{nom} {ape}",
                        posicion=pos,
                        numero=random.randint(1, 99),
                        edad=random.randint(18, 45),
                        equipo_id=equipo.id,
                        liga_id=liga.id,
                        es_capitan=(j == 0), # El primero es capitán
                        es_portero=(pos == "Portero")
                    )
                    db.session.add(jugador)
                
                if i % 5 == 0:
                    print(f"    - Inyectados {i} equipos...")

        db.session.commit()
        print("¡Inyección de datos completada exitosamente!")

if __name__ == "__main__":
    seed_data()
