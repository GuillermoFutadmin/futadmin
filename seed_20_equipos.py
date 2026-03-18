"""
Seed: 20 equipos con 10 jugadores cada uno en el torneo más reciente activo.
- Capitán (1 por equipo)
- Portero (1 por equipo)
- Número de dorsal único por equipo
- Posición, edad, CURP única (generada), teléfono
"""
import os, random, sys, string
sys.stdout.reconfigure(encoding='utf-8')
from dotenv import load_dotenv
load_dotenv()

from flask import Flask
from models import db, Torneo, Equipo, Jugador, Inscripcion, Liga

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('SQLALCHEMY_DATABASE_URI', 'sqlite:///futadmin.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# ── DATOS DE EJEMPLO ──────────────────────────────────────────────────────────

NOMBRES = [
    "Carlos","Miguel","Alejandro","Daniel","José","Luis","Andrés","Francisco","Ricardo","Juan",
    "Sergio","Roberto","Eduardo","Fernando","Pablo","Victor","Javier","Arturo","Gilberto","Hector",
    "Marco","Rodrigo","Raúl","Omar","Iván","Mario","Jorge","Guillermo","Pedro","Antonio",
    "Ernesto","Alfredo","Gustavo","Alberto","Mauricio","Leonardo","Jesús","Diego","Óscar","Armando",
    "Rafael","Erick","Jonathan","Adrián","Gerardo","Emmanuel","Kevin","Cristian","Saúl","Manuel",
    "César","Hugo","Tomás","Ignacio","Boris","Fidel","Ramiro","Rogelio","Ezequiel","Néstor",
    "Samuel","Esteban","Claudio","Benjamín","Aurelio","Rolando","Agustín","Misael","Zacarías","Salomón",
    "Nicolás","Fabio","Ulises","Gonzalo","Ramón","Leonel","Aurelio","Isidro","Hipólito","Epifanio",
    "Simón","Jerónimo","Maximiliano","Teófilo","Rigoberto","Cándido","Zenón","Macario","Onésimo","Lucio",
    "Timoteo","Nicanor","Próspero","Melanio","Herculano","Fulgencio","Severino","Celestino","Honorio","Hipólito",
    "Rodrigo","Santiago","Emilio","Renato","Gabriel","Sebastián","Mateo","Ángel","Alexis","Bruno",
    "Felipe","Patrick","Irving","Edwin","Bryan","Christopher","Dario","Dante","Silvio","Julio",
    "Enrique","Constantino","Marcos","Lázaro","Braulio","Saturnino","Valentín","Bonifacio","Crisanto","Evaristo",
    "Emiliano","Toribio","Plácido","Baldomero","Longinos","Victoriano","Melitón","Ambrosio","Pantaleón","Anastasio",
    "Natalio","Venancio","Primitivo","Florencio","Pacífico","Buenaventura","Demetrio","Exequiel","Florián","Hermenegildo",
    "Irving","Alan","Fausto","Federico","Giovanni","Alessandro","Aurelio","Cristóbal","Gervasio","Heriberto",
    "Jacinto","Lamberto","Macedonio","Nazario","Onofre","Plinio","Querubín","Remigio","Simeón","Telesforo",
    "Ulpiano","Vivaldo","Wenceslao","Xóchitl","Yamil","Zacarías","Abraham","Benito","Cornelio","Desiderio",
]

APELLIDOS = [
    "García","Martínez","López","González","Hernández","Pérez","Sánchez","Ramírez","Torres","Flores",
    "Reyes","Morales","Jiménez","Ortiz","Cruz","Gutiérrez","Romero","Díaz","Mendoza","Vega",
    "Castillo","Rojas","Herrera","Medina","Ramos","Ávila","Luna","Fuentes","Moreno","Rivera",
    "Guerrero","Chávez","Vargas","Domínguez","Salazar","Castro","Aguilar","Orozco","Delgado","Acosta",
    "Espinoza","Ruiz","Contreras","Rubio","Valdez","Núñez","Rangel","Trejo","Bermúdez","Cárdenas",
    "Leiva","Paredes","Ibáñez","Navarro","Escalante","Briones","Carrillo","Peña","De la Rosa","Montoya",
    "Esquivel","Mercado","Vidal","Cervantes","Ríos","Camacho","Argueta","Montes","Alcántara","Hidalgo",
]

POSICIONES = [
    "Delantero","Delantero","Mediocampista","Mediocampista","Mediocampista",
    "Defensa","Defensa","Defensa","Lateral Derecho","Lateral Izquierdo",
]

NOMBRES_EQUIPOS = [
    "Cimarrones FC","Real Azteca","Águilas Negras","Leones del Norte","Tigres Dorados",
    "Guerreros del Sol","Xolos Bravos","Potros Salvajes","Halcones Reales","Cóndores FC",
    "Los Toros","Chivas Verdes","Piratas del Río","Escorpiones CF","Lobos del Desierto",
    "Rayos Plateados","Jaguares FC","Dragones del Valle","Búhos Dorados","Zorros Plateados",
]

CURPS_USADOS = set()

def gen_curp():
    while True:
        letters = ''.join(random.choices(string.ascii_uppercase, k=4))
        nums    = ''.join(random.choices(string.digits, k=6))
        ext     = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
        curp = f"{letters}{nums}{ext}"
        if curp not in CURPS_USADOS:
            CURPS_USADOS.add(curp)
            return curp

def gen_telefono():
    return f"6{random.randint(10,99)}{random.randint(1000000,9999999)}"

def nombre_completo():
    return f"{random.choice(NOMBRES)} {random.choice(APELLIDOS)}"

# ── MAIN ──────────────────────────────────────────────────────────────────────

with app.app_context():
    # Buscar el torneo más reciente activo
    torneo = Torneo.query.filter_by(activo=True).order_by(Torneo.id.desc()).first()
    if not torneo:
        torneo = Torneo.query.order_by(Torneo.id.desc()).first()

    if not torneo:
        print("❌ No se encontró ningún torneo. Crea uno primero.")
        sys.exit(1)

    print(f"📋 Torneo seleccionado: [{torneo.id}] {torneo.nombre} (Liga ID: {torneo.liga_id})")

    equipos_existentes = Equipo.query.filter_by(torneo_id=torneo.id).count()
    print(f"   Equipos actuales: {equipos_existentes}")

    equipos_creados = 0
    jugadores_creados = 0

    for i, nombre_equipo in enumerate(NOMBRES_EQUIPOS):
        # Verificar si ya existe
        if Equipo.query.filter_by(nombre=nombre_equipo, torneo_id=torneo.id).first():
            print(f"   ⚠️  Equipo '{nombre_equipo}' ya existe, saltando...")
            continue

        equipo = Equipo(
            nombre=nombre_equipo,
            torneo_id=torneo.id,
            liga_id=torneo.liga_id,
            grupo=f"Grupo {'ABCDE'[i // 4]}"
        )
        db.session.add(equipo)
        db.session.flush()

        # Crear inscripción automática si no existe
        ins_exist = Inscripcion.query.filter_by(torneo_id=torneo.id, equipo_id=equipo.id).first()
        if not ins_exist:
            ins = Inscripcion(
                torneo_id=torneo.id,
                equipo_id=equipo.id,
                monto_pactado_inscripcion=float(torneo.costo_inscripcion or 0),
                liga_id=torneo.liga_id
            )
            db.session.add(ins)

        # Crear 10 jugadores
        dorsales_usados = set()
        posiciones_shuffled = POSICIONES.copy()
        random.shuffle(posiciones_shuffled)

        for j in range(10):
            # Dorsal único 1-99
            dorsal = None
            if j == 0:
                dorsal = 1  # portero siempre #1
            else:
                while dorsal is None or dorsal in dorsales_usados:
                    dorsal = random.randint(2, 30)
            dorsales_usados.add(dorsal)

            es_portero  = (j == 0)
            es_capitan  = (j == 1)  # capitán = segundo jugador
            posicion    = "Portero" if es_portero else posiciones_shuffled[j % len(posiciones_shuffled)]
            edad        = random.randint(17, 38)
            nombre_jug  = nombre_completo()
            curp        = gen_curp()
            telefono    = gen_telefono()

            jugador = Jugador(
                nombre=nombre_jug,
                curp=curp,
                telefono=telefono,
                posicion=posicion,
                numero=dorsal,
                edad=edad,
                es_portero=es_portero,
                es_capitan=es_capitan,
                equipo_id=equipo.id,
                liga_id=torneo.liga_id
            )
            db.session.add(jugador)
            jugadores_creados += 1

        equipos_creados += 1
        print(f"   ✅ [{equipo.id}] {nombre_equipo} – 10 jugadores (portero + capitán + 8 de campo)")

    db.session.commit()
    print(f"\n🎉 Seed completado:")
    print(f"   Equipos creados : {equipos_creados}")
    print(f"   Jugadores total : {jugadores_creados}")
    total_equipos = Equipo.query.filter_by(torneo_id=torneo.id).count()
    total_jug     = db.session.query(db.func.count(Jugador.id)).join(Equipo).filter(Equipo.torneo_id == torneo.id).scalar()
    print(f"   Total en torneo : {total_equipos} equipos, {total_jug} jugadores")
