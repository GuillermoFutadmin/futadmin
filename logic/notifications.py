import requests
import os

def send_telegram_message(chat_id, text):
    """
    Función base para enviar un mensaje de texto vía Telegram Bot API.
    """
    token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not token:
        # Fallback to app config if available
        try:
            from app import app
            token = app.config.get('TELEGRAM_BOT_TOKEN')
        except:
            return False

    if not chat_id or not token:
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    
    try:
        res = requests.post(url, json=payload, timeout=5)
        return res.status_code == 200
    except Exception as e:
        print(f"Error enviando Telegram: {e}")
        return False

def notify_match_event(match_id, event_type, data=None):
    """
    Identifica a los interesados (dueños de liga) y envía la alerta del evento.
    """
    from models import Partido, Usuario
    p = Partido.query.get(match_id)
    if not p: return

    # 1. Construir el mensaje según el tipo
    emoji = "⚽"
    if event_type == 'Gol': emoji = "⚽ *¡GOOOL!*"
    elif event_type == 'Amarilla': emoji = "🟨 *TARJETA AMARILLA*"
    elif event_type == 'Roja': emoji = "🟥 *TARJETA ROJA*"
    elif event_type == 'Inicio': emoji = "🏁 *INICIO DEL PARTIDO*"
    elif event_type == 'Fin': emoji = "🔚 *FIN DEL PARTIDO*"
    elif event_type == 'Medio Tiempo': emoji = "🕒 *MEDIO TIEMPO*"

    team_name = data.get('team_name', '') if data else ''
    player_name = data.get('player_name', '') if data else ''
    minute = data.get('minute', '') if data else ''
    
    score = f"({p.goles_local or 0} - {p.goles_visitante or 0})"
    
    msg = f"{emoji}\n\n"
    msg += f"🏟️ *Partido:* {p.equipo_local.nombre} vs {p.equipo_visitante.nombre}\n"
    msg += f"📊 *Marcador:* {score}\n"
    
    if event_type in ['Gol', 'Amarilla', 'Roja']:
        msg += f"👤 *Actor:* {player_name} ({team_name})\n"
        if minute: msg += f"⏱️ *Minuto:* {minute}'\n"
    
    liga_nombre = 'FutAdmin'
    if p.torneo and p.torneo.liga:
        liga_nombre = p.torneo.liga.nombre
    elif p.liga_id:
        from models import Liga
        l = Liga.query.get(p.liga_id)
        if l: liga_nombre = l.nombre

    msg += f"\n🏆 *Liga:* {liga_nombre}\n"
    msg += f"📅 *Fecha:* {p.fecha}"

    # 2. Buscar destinatarios: Dueños de la liga y Super Árbitros vinculados a esta liga
    destinatarios = Usuario.query.filter(
        Usuario.liga_id == p.liga_id,
        Usuario.rol.in_(['dueño_liga', 'super_arbitro']),
        Usuario.telegram_id.isnot(None)
    ).all()

    # Evitar duplicados si hay varios destinatarios con el mismo telegram_id
    chat_ids = set([str(d.telegram_id) for d in destinatarios])
    
    for chat_id in chat_ids:
        send_telegram_message(chat_id, msg)

    return True
