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
    Utiliza variables de entorno para la configuración SMTP.
    """
    smtp_host = os.getenv('SMTP_HOST')
    smtp_port = os.getenv('SMTP_PORT', 587)
    smtp_user = os.getenv('SMTP_USER')
    smtp_pass = os.getenv('SMTP_PASS')
    sender_email = os.getenv('MAIL_DEFAULT_SENDER', smtp_user)

    if not all([smtp_host, smtp_user, smtp_pass]):
        _log_mail(f"ERROR: Configuración SMTP incompleta. Saltando envío a {to_email}")
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

        # Connect and send
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
        
        _log_mail(f"SUCCESS: Correo enviado correctamente a {to_email}")
        return True
    except smtplib.SMTPException as se:
        _log_mail(f"ERROR SMTP enviando correo a {to_email}: {str(se)}")
        return False
    except Exception as e:
        import traceback
        error_msg = f"ERROR GENERAL enviando correo a {to_email}: {str(e)}\n{traceback.format_exc()}"
        _log_mail(error_msg)
        return False
