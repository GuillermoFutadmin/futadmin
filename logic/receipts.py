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
FUTADMIN_LOGO_URL = "https://res.cloudinary.com/dzqgrgfnf/image/upload/v1742861131/logos_futadmin/futadmin_logo_circular.png"
FUTADMIN_INSTAGRAM = "https://www.instagram.com/futadmin.tj/"
FUTADMIN_WEBSITE = "https://futadmin.com.mx"


def build_receipt_email_html(nombre, liga_nombre, equipo, torneo, tipo, monto_abonado,
                              monto_pactado=0, total_pagado=0, saldo_pendiente=0,
                              metodo="Efectivo", folio="N/A", fecha=None, partido=None, is_futadmin=False):
    """Genera un cuerpo HTML profesional para el correo de recibo de pago con firma FutAdmin."""
    fecha_str = fecha or datetime.now().strftime('%d/%m/%Y %H:%M')
    saldo_color = "#e74c3c" if saldo_pendiente > 0 else "#27ae60"

    partido_row = ""
    if partido:
        partido_row = f"""
              <tr>
                <td style="padding:8px 12px;color:#555;border-bottom:1px solid #f0f0f0;">⚽ Partido</td>
                <td style="padding:8px 12px;font-weight:600;border-bottom:1px solid #f0f0f0;">{partido.get('rivales','N/A')} (J{partido.get('jornada','?')})</td>
              </tr>"""

    financial_rows = f"""
              <tr>
                <td style="padding:8px 12px;color:#555;border-bottom:1px solid #f0f0f0;">💵 Monto Abonado</td>
                <td style="padding:8px 12px;font-weight:700;color:#27ae60;border-bottom:1px solid #f0f0f0;">${monto_abonado:,.2f} ({metodo})</td>
              </tr>"""
    if not is_futadmin:
        financial_rows += f"""
              <tr>
                <td style="padding:8px 12px;color:#555;border-bottom:1px solid #f0f0f0;background:#fafafa;">📋 Monto Pactado</td>
                <td style="padding:8px 12px;font-weight:600;border-bottom:1px solid #f0f0f0;background:#fafafa;">${monto_pactado:,.2f}</td>
              </tr>
              <tr>
                <td style="padding:8px 12px;color:#555;border-bottom:1px solid #f0f0f0;">✅ Total Pagado</td>
                <td style="padding:8px 12px;font-weight:600;border-bottom:1px solid #f0f0f0;">${total_pagado:,.2f}</td>
              </tr>
              <tr>
                <td style="padding:8px 12px;color:#555;">🔴 Saldo Pendiente</td>
                <td style="padding:8px 12px;font-weight:700;color:{saldo_color};">${saldo_pendiente:,.2f}</td>
              </tr>"""

    return f"""<!DOCTYPE html>
<html lang="es">
<head><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"></head>
<body style="margin:0;padding:0;background:#f4f6f8;font-family:'Segoe UI',Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f6f8;padding:30px 0;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.08);">
        <!-- HEADER -->
        <tr>
          <td style="background:linear-gradient(135deg,#1a1a2e 0%,#16213e 60%,#0f3460 100%);padding:32px 40px;text-align:center;">
            <img src="{FUTADMIN_LOGO_URL}" alt="FutAdmin" width="80" height="80" style="border-radius:50%;border:3px solid #00d4aa;margin-bottom:12px;display:block;margin-left:auto;margin-right:auto;"><br>
            <span style="color:#ffffff;font-size:22px;font-weight:700;letter-spacing:1px;">FutAdmin</span><br>
            <span style="color:#00d4aa;font-size:13px;letter-spacing:2px;text-transform:uppercase;">Recibo Oficial de Pago</span>
          </td>
        </tr>
        <!-- FOLIO BANNER -->
        <tr>
          <td style="background:#00d4aa;padding:10px 40px;text-align:center;">
            <span style="color:#1a1a2e;font-size:13px;font-weight:700;">Folio: {folio} &nbsp;|&nbsp; {fecha_str}</span>
          </td>
        </tr>
        <!-- GREETING -->
        <tr>
          <td style="padding:30px 40px 10px;">
            <p style="margin:0;font-size:16px;color:#333;">Hola <strong>{nombre}</strong>,</p>
            <p style="margin:12px 0 0;font-size:14px;color:#666;line-height:1.6;">
              Adjuntamos el recibo oficial correspondiente a tu pago en <strong>{liga_nombre}</strong>. 
              Guarda este correo como comprobante de tu transacción.
            </p>
          </td>
        </tr>
        <!-- PAYMENT DETAILS -->
        <tr>
          <td style="padding:20px 40px;">
            <p style="margin:0 0 12px;font-size:15px;font-weight:700;color:#1a1a2e;border-left:4px solid #00d4aa;padding-left:10px;">Detalles del Pago</p>
            <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e8e8e8;border-radius:8px;overflow:hidden;font-size:14px;">
              <tr>
                <td style="padding:8px 12px;color:#555;border-bottom:1px solid #f0f0f0;background:#fafafa;width:45%;">🏆 Liga</td>
                <td style="padding:8px 12px;font-weight:600;border-bottom:1px solid #f0f0f0;background:#fafafa;">{liga_nombre}</td>
              </tr>
              <tr>
                <td style="padding:8px 12px;color:#555;border-bottom:1px solid #f0f0f0;">👕 Equipo</td>
                <td style="padding:8px 12px;font-weight:600;border-bottom:1px solid #f0f0f0;">{equipo}</td>
              </tr>
              <tr>
                <td style="padding:8px 12px;color:#555;border-bottom:1px solid #f0f0f0;background:#fafafa;">🗂️ Torneo</td>
                <td style="padding:8px 12px;font-weight:600;border-bottom:1px solid #f0f0f0;background:#fafafa;">{torneo}</td>
              </tr>
              <tr>
                <td style="padding:8px 12px;color:#555;border-bottom:1px solid #f0f0f0;">📌 Concepto</td>
                <td style="padding:8px 12px;font-weight:600;border-bottom:1px solid #f0f0f0;">{tipo}</td>
              </tr>
              {partido_row}
            </table>
          </td>
        </tr>
        <!-- FINANCIAL SUMMARY -->
        <tr>
          <td style="padding:0 40px 20px;">
            <p style="margin:0 0 12px;font-size:15px;font-weight:700;color:#1a1a2e;border-left:4px solid #0f3460;padding-left:10px;">Resumen Financiero</p>
            <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e8e8e8;border-radius:8px;overflow:hidden;font-size:14px;">
              {financial_rows}
            </table>
          </td>
        </tr>
        <!-- PDF NOTE -->
        <tr>
          <td style="padding:0 40px 24px;">
            <div style="background:#fff8e1;border:1px solid #ffe082;border-radius:8px;padding:14px 18px;font-size:13px;color:#795548;">
              📎 <strong>PDF adjunto:</strong> El recibo oficial en PDF está adjunto. Descárgalo como comprobante físico.
            </div>
          </td>
        </tr>
        <!-- FOOTER / FIRMA -->
        <tr>
          <td style="background:#1a1a2e;padding:28px 40px;text-align:center;">
            <img src="{FUTADMIN_LOGO_URL}" alt="FutAdmin" width="52" height="52" style="border-radius:50%;border:2px solid #00d4aa;display:block;margin:0 auto 10px auto;">
            <p style="margin:0;color:#00d4aa;font-size:16px;font-weight:700;">FutAdmin</p>
            <p style="margin:4px 0 0;color:#aaa;font-size:12px;">Plataforma de Gestión Deportiva</p>
            <p style="margin:10px 0 0;">
              <a href="{FUTADMIN_WEBSITE}" style="color:#00d4aa;font-size:12px;text-decoration:none;">🌐 futadmin.com.mx</a>
              &nbsp;&nbsp;|&nbsp;&nbsp;
              <a href="{FUTADMIN_INSTAGRAM}" style="color:#e1306c;font-size:12px;text-decoration:none;">📸 @futadmin.tj</a>
            </p>
            <hr style="border:none;border-top:1px solid #333;margin:16px 0;">
            <p style="margin:0;color:#555;font-size:11px;">Este es un comprobante digital generado automáticamente. No responder a este correo.</p>
          </td>
        </tr>
      </table>
    </td></tr>
  </table>
</body>
</html>"""

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

