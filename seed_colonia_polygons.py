
import requests
import json
import time
from app import app, db
from models import Equipo

# Lista expandida para asegurar varianza
COLONIES = [
    "Centro, Tijuana",
    "Playas de Tijuana",
    "Zona Rio, Tijuana",
    "Colonia Libertad, Tijuana",
    "Otay Constituyentes, Tijuana",
    "Santa Fe, Tijuana",
    "El Florido, Tijuana",
    "Loma Bonita, Tijuana",
    "Camino Verde, Tijuana",
    "Villa Fontana, Tijuana",
    "Colonia Cacho, Tijuana",
    "La Mesa, Tijuana",
    "El Lago, Tijuana",
    "Cerro Colorado, Tijuana",
    "Mariano Matamoros, Tijuana",
    "La Presa, Tijuana",
    "San Antonio de los Buenos, Tijuana",
    "Sanchez Taboada, Tijuana",
    "Delegacion Centenario, Tijuana",
    "Granjas Familiares, Tijuana",
    "Hacienda Santa Maria, Tijuana",
    "Las Delicias, Tijuana",
    "Pueblo Nuevo, Tijuana",
    "Valle de las Palmas, Tijuana",
    "Real del Mar, Tijuana",
    "Rosarito", # Cerca
    "Tecate"    # Cerca
]

def fetch_geojson(query):
    print(f"Fetching GeoJSON for: {query}...")
    url = "https://nominatim.openstreetmap.org/search"
    params = {
        "q": query + ", Baja California, Mexico",
        "format": "json",
        "polygon_geojson": 1,
        "limit": 10, 
        "addressdetails": 1
    }
    headers = {
        "User-Agent": "FutAdmin-Seeder/1.2"
    }
    try:
        res = requests.get(url, params=params, headers=headers)
        if res.status_code == 200:
            data = res.json()
            results = []
            for item in data:
                if "geojson" in item and item["geojson"]["type"] in ["Polygon", "MultiPolygon"]:
                    addr = item.get("address", {})
                    name = addr.get("suburb") or addr.get("neighbourhood") or item.get("name") or query.split(',')[0]
                    results.append((name, json.dumps(item['geojson'])))
            return results
    except Exception as e:
        print(f"Error fetching {query}: {e}")
    return []

def seed():
    with app.app_context():
        equipos = Equipo.query.all()
        print(f"Procesando {len(equipos)} equipos.")
        
        # Build a LARGE pool
        full_pool = []
        for c in COLONIES:
            results = fetch_geojson(c)
            for res in results:
                # Evitar duplicados exactos de geojson
                if not any(res[1] == item[1] for item in full_pool):
                    full_pool.append(res)
            time.sleep(1) # Respect Nominatim
            if len(full_pool) >= len(equipos):
                break
        
        if not full_pool:
            print("No se pudieron obtener polígonos.")
            return

        print(f"Pool de {len(full_pool)} polígonos únicos listo.")
        
        # Asignar secuencialmente o aleatorio pero tratando de cubrir todos
        for i, eq in enumerate(equipos):
            # Usar modulo para ciclar si el pool es más pequeño que equipos
            col_name, col_geo = full_pool[i % len(full_pool)]
            eq.colonia = col_name
            eq.colonia_geojson = col_geo
            print(f"Asignado unique {col_name} a {eq.nombre}")
        
        db.session.commit()
        print(f"Equipos actualizados con éxito con {min(len(full_pool), len(equipos))} perímetros distintos.")

if __name__ == "__main__":
    seed()
