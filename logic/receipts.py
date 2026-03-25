import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib import colors
import base64
import requests

RESEND_API_URL = "https://api.resend.com/emails"

def generate_receipt_pdf(data, filename):
    """
    Genera un PDF profesional basado en los datos del ticket.
    'data' debe contener campos como folio, fecha, equipo, torneo, sede, monto_abonado, etc.
    """
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter

    # Ajustes iniciales
    margin = 1 * inch
    c.setFont("Helvetica-Bold", 16)
    
    # Determine if it's a FutAdmin receipt or a League receipt
    is_futadmin = data.get('is_futadmin', False)
    
    # Header
    if is_futadmin:
        c.drawString(margin, height - margin, "COMPROBANTE DE PAGO - FUTADMIN")
    else:
        league_name = data.get('liga_nombre', 'RECIBO DE LIGA')
        c.drawString(margin, height - margin, f"RECIBO OFICIAL - {league_name.upper()}")

    c.setFont("Helvetica", 10)
    c.drawString(margin, height - margin - 20, f"Folio: {data.get('folio', 'N/A')}")
    c.drawString(margin, height - margin - 35, f"Fecha: {data.get('fecha', datetime.now().strftime('%d/%m/%Y %H:%M'))}")

    # Horizontal Line
    c.setStrokeColor(colors.black)
    c.line(margin, height - margin - 45, width - margin, height - margin - 45)

    # Content
    y_pos = height - margin - 70
    c.setFont("Helvetica-Bold", 12)
    
    if is_futadmin:
        c.drawString(margin, y_pos, "Detalles de Suscripción")
    else:
        c.drawString(margin, y_pos, "Detalles del Pago")

    c.setFont("Helvetica", 11)
    y_pos -= 20
    
    lines = []
    if is_futadmin:
        lines.append(f"Liga: {data.get('liga_nombre', 'N/A')}")
        lines.append(f"Concepto: {data.get('tipo', 'Suscripción Mensual')}")
        lines.append(f"Mes Pagado: {data.get('mes_pagado', 'N/A')}")
    else:
        lines.append(f"Equipo: {data.get('equipo', 'N/A')}")
        lines.append(f"Torneo: {data.get('torneo', 'N/A')}")
        lines.append(f"Sede: {data.get('sede', 'Por definir')}")
        lines.append(f"Concepto: {data.get('tipo', 'Abono')}")
        
        if data.get('partido'):
            p = data['partido']
            lines.append(f"Partido: {p.get('rivales', 'N/A')} (J{p.get('jornada', '?')})")

    for line in lines:
        c.drawString(margin + 20, y_pos, f"• {line}")
        y_pos -= 15

    # Financial Details
    y_pos -= 10
    c.setStrokeColor(colors.grey)
    c.line(margin, y_pos, width - margin, y_pos)
    y_pos -= 20
    
    c.setFont("Helvetica-Bold", 12)
    c.drawString(margin, y_pos, "Resumen Financiero")
    c.setFont("Helvetica", 11)
    y_pos -= 20
    
    monto_pactado = data.get('monto_pactado', 0)
    total_pagado = data.get('total_pagado', 0)
    abonado = data.get('monto_abonado', 0)
    saldo = data.get('saldo_pendiente', 0)
    
    c.drawString(margin + 20, y_pos, f"Monto de la Operación: ${abonado:,.2f} ({data.get('metodo', 'Efectivo')})")
    y_pos -= 15
    
    if not is_futadmin:
        c.drawString(margin + 20, y_pos, f"Monto Pactado Total: ${monto_pactado:,.2f}")
        y_pos -= 15
        c.drawString(margin + 20, y_pos, f"Acumulado Pagado: ${total_pagado:,.2f}")
        y_pos -= 15
        c.setFont("Helvetica-Bold", 11)
        c.drawString(margin + 20, y_pos, f"Saldo Pendiente: ${saldo:,.2f}")
        c.setFont("Helvetica", 11)
        y_pos -= 30

    # Legal / Notes
    if not is_futadmin:
        c.setFont("Helvetica-Bold", 10)
        c.drawString(margin, y_pos, "NOTAS Y REGLAMENTO:")
        c.setFont("Helvetica", 8)
        y_pos -= 12
        
        text = data.get('clausulas', '') or data.get('reglamento', '')
        # Simple text wrapping
        max_chars = 90
        for part in text.split('\n'):
            while len(part) > max_chars:
                c.drawString(margin + 10, y_pos, part[:max_chars])
                part = part[max_chars:]
                y_pos -= 10
            c.drawString(margin + 10, y_pos, part)
            y_pos -= 10
            if y_pos < margin: break

    # Footer
    c.setFont("Helvetica-Oblique", 8)
    c.drawCentredString(width/2, margin/2, "Este es un comprobante digital generado automáticamente por FutAdmin.")
    c.drawCentredString(width/2, margin/2 - 10, "FutAdmin - Control de Ingresos y Gestión Deportiva")

    c.save()
    return filename

def _log_mail(message):
    try:
        # Usar ruta absoluta basada en el script actual para evitar confusiones de CWD
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        log_path = os.path.join(base_dir, "mail_debug.log")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(log_path, "a", encoding="utf-8") as f:
            f.write(f"[{timestamp}] {message}\n")
    except Exception as e:
        print(f"CRITICAL: Failed to write to mail_debug.log: {e}")

def send_receipt_email(to_email, subject, body, attachment_path=None):
    """
    Envía un correo electrónico con un archivo adjunto.
    Si existe RESEND_API_KEY se usa la API de Resend (puerto 443), si no se usa SMTP como fallback.
    """
    resend_api_key = os.getenv('RESEND_API_KEY')
    smtp_user = os.getenv('SMTP_USER')
    sender_email = os.getenv('MAIL_DEFAULT_SENDER', smtp_user or 'no-reply@futadmin.com.mx')

    if resend_api_key:
        return _send_via_resend(resend_api_key, sender_email, to_email, subject, body, attachment_path)
    else:
        return _send_via_smtp(to_email, subject, body, attachment_path, sender_email)

def _send_via_resend(api_key, sender_email, to_email, subject, body, attachment_path):
    _log_mail("DEBUG: Intentando conexión a Resend API...")
    try:
        payload = {
            "from": f"FutAdmin <{sender_email}>",
            "to": [to_email],
            "subject": subject,
            "html": body.replace('\n', '<br>')
        }
        
        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, "rb") as f:
                encoded_file = base64.b64encode(f.read()).decode('utf-8')
            payload["attachments"] = [
                {
                    "filename": os.path.basename(attachment_path),
                    "content": encoded_file
                }
            ]
            
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(RESEND_API_URL, json=payload, headers=headers, timeout=15)
        
        if response.status_code in (200, 201):
            _log_mail(f"SUCCESS: Correo enviado correctamente vía Resend API a {to_email}")
            return True
        else:
            _log_mail(f"ERROR Resend API [{response.status_code}]: {response.text}")
            return False
            
    except Exception as e:
        import traceback
        _log_mail(f"ERROR GENERAL enviando correo por Resend API a {to_email}: {str(e)}\n{traceback.format_exc()}")
        return False

def _send_via_smtp(to_email, subject, body, attachment_path, sender_email):
    # Fallback SMTP tradicional
    smtp_host = os.getenv('SMTP_HOST')
    smtp_port = os.getenv('SMTP_PORT', 465)
    smtp_user = os.getenv('SMTP_USER')
    smtp_pass = os.getenv('SMTP_PASS')

    if not all([smtp_host, smtp_user, smtp_pass]):
        _log_mail(f"ERROR: Configuración SMTP incompleta y sin API Key. Saltando envío a {to_email}")
        return False

    try:
        msg = MIMEMultipart()
        msg['From'] = f"FutAdmin Notifications <{sender_email}>"
        msg['To'] = to_email
        msg['Subject'] = subject

        msg.attach(MIMEText(body, 'plain'))

        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, "rb") as f:
                attach = MIMEApplication(f.read(), _subtype="pdf")
                attach.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment_path))
                msg.attach(attach)

        port = int(smtp_port)
        _log_mail(f"DEBUG: Intentando conexión a {smtp_host}:{port}...")
        
        if port == 465:
            server = smtplib.SMTP_SSL(smtp_host, port, timeout=30)
        else:
            server = smtplib.SMTP(smtp_host, port, timeout=30)
            server.starttls()
            
        _log_mail(f"DEBUG: Conectado. Intentando login como {smtp_user}...")
        server.login(smtp_user, smtp_pass)
        
        _log_mail(f"DEBUG: Login exitoso. Enviando mensaje a {to_email}...")
        server.send_message(msg)
        server.quit()
        
        _log_mail(f"SUCCESS: Correo enviado correctamente a {to_email} (vía SMTP)")
        return True
    except smtplib.SMTPException as se:
        _log_mail(f"ERROR SMTP enviando correo a {to_email}: {str(se)}")
        return False
    except Exception as e:
        import traceback
        _log_mail(f"ERROR GENERAL enviando correo a {to_email} vía SMTP: {str(e)}\n{traceback.format_exc()}")
        return False

