from app import app, db
from models import Torneo, Liga, Usuario

with app.app_context():
    print("--- INVESTIGACIÓN DE TORNEO Y USUARIO ---")
    
    # 1. Buscar el torneo
    nombre_torneo = "Torneo Estatal 202603"
    torneo = Torneo.query.filter(Torneo.nombre.ilike(f"%{nombre_torneo}%")).first()
    
    if torneo:
        print(f"TORNEO ENCONTRADO:")
        print(f"  ID: {torneo.id}")
        print(f"  Nombre: {torneo.nombre}")
        print(f"  Sede (cancha): {torneo.cancha}")
        print(f"  Liga ID: {torneo.liga_id}")
        if torneo.liga_id:
            liga = Liga.query.get(torneo.liga_id)
            print(f"  Liga Nombre: {liga.nombre if liga else 'No encontrada'}")
    else:
        print(f"ERROR: Torneo '{nombre_torneo}' no encontrado.")

    # 2. Buscar al usuario operativo 
    # El usuario mencionado es "Guillermo Diaz Flores"
    usuario = Usuario.query.filter(Usuario.nombre.ilike("%Guillermo%")).first()
    if usuario:
        print(f"\nUSUARIO ENCONTRADO:")
        print(f"  ID: {usuario.id}")
        print(f"  Nombre: {usuario.nombre}")
        print(f"  Rol: {usuario.rol}")
        print(f"  Liga ID: {usuario.liga_id}")
        print(f"  Cancha ID: {usuario.cancha_id}")
        if usuario.liga_id:
            liga_u = Liga.query.get(usuario.liga_id)
            print(f"  Liga Usuario: {liga_u.nombre if liga_u else 'No encontrada'}")
    else:
        print("\nERROR: Usuario 'Guillermo' no encontrado.")

    # 3. Listar otros torneos en la misma sede para comparar
    if torneo:
        print(f"\nOTROS TORNEOS EN SEDE '{torneo.cancha}':")
        otros = Torneo.query.filter(Torneo.cancha.ilike(f"%{torneo.cancha}%")).all()
        for t in otros:
            print(f"  - [{t.id}] {t.nombre} | Liga ID: {t.liga_id}")

    print("\n--- FIN DE INVESTIGACIÓN ---")
