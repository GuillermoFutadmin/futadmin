from app import app, db
from models import Equipo

with app.app_context():
    e = Equipo.query.first()
    if not e:
        print("No hay equipos para probar")
    else:
        id = e.id
        print(f"Probando con Equipo ID: {id}, UID Real: {e.uid}")
        
        roles = ['admin', 'ejecutivo', 'dueño_liga', 'resultados', 'arbitro', 'solo vista', '', None]
        
        from flask import session
        with app.test_request_context():
            for r in roles:
                with app.test_client() as client:
                    with client.session_transaction() as sess:
                        sess['user_id'] = 1
                        sess['user_rol'] = r
                    
                    response = client.get(f'/api/equipos/{id}/stats-summary')
                    data = response.get_json()
                    uid_returned = data.get('uid')
                    print(f"Role: {r} (stats-summary) -> UID returned: {uid_returned}")
                    
                    response_list = client.get(f'/api/equipos')
                    list_data = response_list.get_json()
                    e_in_list = next((eq for eq in list_data if eq['id'] == id), None)
                    uid_in_list = e_in_list.get('uid') if e_in_list else "Not found"
                    print(f"Role: {r} (/api/equipos) -> UID in list: {uid_in_list}")
