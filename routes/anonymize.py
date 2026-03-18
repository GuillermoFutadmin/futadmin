from flask import Blueprint, jsonify, request, session
from models import db, Usuario, Arbitro, Jugador, Partido, EventoPartido, AsistenciaPartido
from datetime import datetime

anonymize_bp = Blueprint('anonymize', __name__)

@anonymize_bp.route('/api/users/<int:user_id>/anonymize', methods=['POST'])
def anonymize_user_data(user_id):
    # Solo administradores pueden ejecutar esta acción por ahora
    if session.get('user_rol') not in ['admin', 'ejecutivo', 'dueño_liga']:
        return jsonify({"error": "No tiene permisos para ejecutar anonimización"}), 403
    
    user = Usuario.query.get_or_404(user_id)
    email_original = user.email
    
    try:
        # 1. Anonimizar el Usuario
        user.nombre = f"Usuario Anonimizado #{user.id}"
        user.email = f"anon_{user.id}@futadmin.com"
        user.password_hash = "ANONYMIZED"
        user.activo = False
        
        # 2. Buscar y anonimizar en Cuerpo Arbitral si existe
        arbitro = Arbitro.query.filter_by(email=email_original).first()
        if arbitro:
            arbitro.nombre = user.nombre
            arbitro.email = user.email
            arbitro.telefono = "0000000000"
            arbitro.telegram_id = None
            arbitro.password = "ANONYMIZED"
            arbitro.foto_url = None
            arbitro.activo = False
            
        # 3. Buscar y anonimizar en Jugadores si existe
        jugador = Jugador.query.filter_by(correo=email_original).first()
        if jugador:
            jugador.nombre = user.nombre
            jugador.correo = user.email
            jugador.telefono = "0000000000"
            jugador.foto_url = None
            
        db.session.commit()
        return jsonify({
            "success": True, 
            "message": "Datos anonimizados correctamente. Se preservaron los registros históricos."
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# Endpoint extra para anonimizar Jugadores que NO tienen cuenta de usuario (vía correo o ID directo)
@anonymize_bp.route('/api/jugadores/<int:jugador_id>/anonymize', methods=['POST'])
def anonymize_player_data(jugador_id):
    if session.get('user_rol') not in ['admin', 'ejecutivo', 'dueño_liga']:
        return jsonify({"error": "Permisos insuficientes"}), 403
        
    jugador = Jugador.query.get_or_404(jugador_id)
    
    try:
        jugador.nombre = f"Jugador Anonimizado #{jugador.id}"
        jugador.correo = f"anon_player_{jugador.id}@futadmin.com"
        jugador.telefono = "0000000000"
        jugador.foto_url = None
        
        db.session.commit()
        return jsonify({"success": True})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
