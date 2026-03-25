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
FUTADMIN_LOGO_URL = "https://futadmin.com.mx/static/img/logos/futadmin_circle.png"
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
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f4f6f8;padding:15px 0;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:12px;overflow:hidden;box-shadow:0 4px 20px rgba(0,0,0,0.08);">
        <!-- HEADER -->
        <tr>
          <td style="background-color:#1a1a2e;background:linear-gradient(135deg,#1a1a2e 0%,#16213e 60%,#0f3460 100%);padding:15px 40px;text-align:center;">
            <img src="{FUTADMIN_LOGO_URL}" alt="FutAdmin" width="60" height="60" style="border-radius:50%;border:2px solid #00d4aa;margin-bottom:6px;display:block;margin-left:auto;margin-right:auto;">
            <span style="color:#ffffff;font-size:18px;font-weight:700;letter-spacing:1px;display:block;margin-top:2px;">FutAdmin</span>
            <span style="color:#ffffff;font-size:11px;letter-spacing:2px;text-transform:uppercase;display:block;margin-top:2px;opacity:0.9;">Recibo Oficial de Pago</span>
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
          <td style="padding:15px 40px 10px;">
            <p style="margin:0;font-size:15px;color:#333;">Hola <strong>{nombre}</strong>,</p>
            <p style="margin:5px 0 0;font-size:14px;color:#666;line-height:1.4;">
              Adjuntamos el recibo oficial de tu pago en <strong>{liga_nombre}</strong>. 
            </p>
          </td>
        </tr>
        <!-- PAYMENT DETAILS -->
        <tr>
          <td style="padding:10px 40px;">
            <p style="margin:0 0 8px;font-size:14px;font-weight:700;color:#1a1a2e;border-left:4px solid #00d4aa;padding-left:10px;">Detalles del Pago</p>
            <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e8e8e8;border-radius:8px;overflow:hidden;font-size:13px;">
              <tr>
                <td style="padding:6px 12px;color:#555;border-bottom:1px solid #f0f0f0;background:#fafafa;width:45%;">🏆 Liga</td>
                <td style="padding:6px 12px;font-weight:600;border-bottom:1px solid #f0f0f0;background:#fafafa;">{liga_nombre}</td>
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
          <td style="padding:0 40px 15px;">
            <p style="margin:0 0 8px;font-size:14px;font-weight:700;color:#1a1a2e;border-left:4px solid #0f3460;padding-left:10px;">Resumen Financiero</p>
            <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e8e8e8;border-radius:8px;overflow:hidden;font-size:13px;">
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
    Genera un PDF profesional con diseño FutAdmin: header oscuro, logo, tablas y firma.
    """
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable, Image as RLImage
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
    from reportlab.lib.units import inch, mm
    from reportlab.lib import colors as rl_colors

    # --- Colores de marca ---
    DARK_BG   = rl_colors.HexColor('#1a1a2e')
    TEAL      = rl_colors.HexColor('#00d4aa')
    MID_BLUE  = rl_colors.HexColor('#0f3460')
    LIGHT_GREY= rl_colors.HexColor('#f4f6f8')
    DARK_TEXT = rl_colors.HexColor('#1a1a2e')
    RED_COLOR = rl_colors.HexColor('#e74c3c')
    GREEN_COLOR = rl_colors.HexColor('#27ae60')

    doc = SimpleDocTemplate(filename, pagesize=letter,
                            leftMargin=0.6*inch, rightMargin=0.6*inch,
                            topMargin=0.4*inch, bottomMargin=0.5*inch)
    story = []
    styles = getSampleStyleSheet()

    is_futadmin = data.get('is_futadmin', False)
    liga_nombre = data.get('liga_nombre', 'Liga FutAdmin')
    folio       = data.get('folio', 'N/A')
    fecha       = data.get('fecha', datetime.now().strftime('%d/%m/%Y %H:%M'))

    # --- LOGO ---
    logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             'static', 'img', 'logos', 'futadmin_circle.png')
    logo_elem = None
    if os.path.exists(logo_path):
        logo_elem = RLImage(logo_path, width=70, height=70)

    # --- HEADER TABLE (logo + título) ---
    title_style = ParagraphStyle('HeaderTitle', fontName='Helvetica-Bold',
                                 fontSize=18, textColor=rl_colors.white,
                                 alignment=TA_LEFT, leading=22)
    sub_style = ParagraphStyle('HeaderSub', fontName='Helvetica',
                               fontSize=10, textColor=TEAL,
                               alignment=TA_LEFT, leading=14)
    title_text = Paragraph("FutAdmin", title_style)
    sub_text   = Paragraph("RECIBO OFICIAL DE PAGO", sub_style)

    if logo_elem:
        header_data = [[logo_elem, [title_text, sub_text]]]
        header_table = Table(header_data, colWidths=[80, None])
    else:
        header_data = [[[title_text, sub_text]]]
        header_table = Table(header_data, colWidths=[None])

    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), DARK_BG),
        ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING',(0,0), (-1,-1), 14),
        ('RIGHTPADDING',(0,0),(-1,-1), 14),
        ('TOPPADDING', (0,0), (-1,-1), 12),
        ('BOTTOMPADDING',(0,0),(-1,-1), 12),
        ('ROWBACKGROUNDS',(0,0),(-1,-1),[DARK_BG]),
    ]))
    story.append(header_table)

    # --- FOLIO BANNER ---
    folio_style = ParagraphStyle('Folio', fontName='Helvetica-Bold',
                                 fontSize=10, textColor=DARK_TEXT, alignment=TA_CENTER)
    folio_table = Table([[Paragraph(f"Folio: {folio}   |   {fecha}", folio_style)]],
                        colWidths=[None])
    folio_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), TEAL),
        ('TOPPADDING', (0,0),(-1,-1), 8),
        ('BOTTOMPADDING', (0,0),(-1,-1), 8),
    ]))
    story.append(folio_table)
    story.append(Spacer(1, 8))

    # --- SALUDO ---
    equipo_nombre = data.get('equipo', '')
    greeting_style = ParagraphStyle('Greeting', fontName='Helvetica', fontSize=11,
                                    textColor=DARK_TEXT, alignment=TA_LEFT, leading=16)
    story.append(Paragraph(
        f"Este documento acredita el pago realizado por el equipo <b>{equipo_nombre}</b> "
        f"en la liga <b>{liga_nombre}</b>. Consérvelo como comprobante oficial.",
        greeting_style))
    story.append(Spacer(1, 8))

    # --- SECCIÓN: Detalles del Pago ---
    sec_style = ParagraphStyle('SecTitle', fontName='Helvetica-Bold', fontSize=12,
                               textColor=rl_colors.white, alignment=TA_LEFT)
    sec_banner = Table([[Paragraph("  Detalles del Pago", sec_style)]], colWidths=[None])
    sec_banner.setStyle(TableStyle([
        ('BACKGROUND', (0,0),(-1,-1), MID_BLUE),
        ('TOPPADDING',(0,0),(-1,-1),6), ('BOTTOMPADDING',(0,0),(-1,-1),6),
    ]))
    story.append(sec_banner)
    story.append(Spacer(1, 4))

    label_s = ParagraphStyle('Label', fontName='Helvetica-Bold', fontSize=10, textColor=DARK_TEXT)
    value_s = ParagraphStyle('Value', fontName='Helvetica', fontSize=10, textColor=rl_colors.HexColor('#333333'))

    detail_rows = []
    if is_futadmin:
        detail_rows = [
            [Paragraph("Liga:", label_s), Paragraph(liga_nombre, value_s)],
            [Paragraph("Concepto:", label_s), Paragraph(data.get('tipo','Suscripción'), value_s)],
            [Paragraph("Mes Pagado:", label_s), Paragraph(str(data.get('mes_pagado','N/A')), value_s)],
        ]
    else:
        detail_rows = [
            [Paragraph("Liga / Administrador:", label_s), Paragraph(liga_nombre, value_s)],
            [Paragraph("Equipo:", label_s), Paragraph(data.get('equipo','N/A'), value_s)],
            [Paragraph("Torneo:", label_s), Paragraph(data.get('torneo','N/A'), value_s)],
            [Paragraph("Sede:", label_s), Paragraph(data.get('sede','Por definir'), value_s)],
            [Paragraph("Concepto:", label_s), Paragraph(data.get('tipo','Abono'), value_s)],
            [Paragraph("Método de Pago:", label_s), Paragraph(data.get('metodo','Efectivo'), value_s)],
        ]
        if data.get('partido'):
            p = data['partido']
            detail_rows.append([
                Paragraph("Partido:", label_s),
                Paragraph(f"{p.get('rivales','N/A')}  (Jornada {p.get('jornada','?')})", value_s)
            ])

    detail_table = Table(detail_rows, colWidths=[160, None])
    detail_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), LIGHT_GREY),
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [rl_colors.white, LIGHT_GREY]),
        ('GRID', (0,0), (-1,-1), 0.3, rl_colors.HexColor('#dddddd')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(detail_table)
    story.append(Spacer(1, 12))

    # --- SECCIÓN: Resumen Financiero ---
    sec_banner2 = Table([[Paragraph("  Resumen Financiero", sec_style)]], colWidths=[None])
    sec_banner2.setStyle(TableStyle([
        ('BACKGROUND', (0,0),(-1,-1), MID_BLUE),
        ('TOPPADDING',(0,0),(-1,-1),6), ('BOTTOMPADDING',(0,0),(-1,-1),6),
    ]))
    story.append(sec_banner2)
    story.append(Spacer(1, 4))

    abonado      = float(data.get('monto_abonado', 0))
    monto_pactado= float(data.get('monto_pactado', 0))
    total_pagado = float(data.get('total_pagado', 0))
    saldo        = float(data.get('saldo_pendiente', 0))
    saldo_color  = RED_COLOR if saldo > 0 else GREEN_COLOR

    saldo_style = ParagraphStyle('SaldoVal', fontName='Helvetica-Bold', fontSize=10, textColor=saldo_color)
    green_style = ParagraphStyle('GreenVal', fontName='Helvetica-Bold', fontSize=10, textColor=GREEN_COLOR)

    fin_rows = [
        [Paragraph("💵  Monto Abonado (esta operación):", label_s), Paragraph(f"${abonado:,.2f}  ({data.get('metodo','Efectivo')})", green_style)],
    ]
    if not is_futadmin:
        fin_rows += [
            [Paragraph("📋  Monto Pactado Total:", label_s), Paragraph(f"${monto_pactado:,.2f}", value_s)],
            [Paragraph("✅  Total Acumulado Pagado:", label_s), Paragraph(f"${total_pagado:,.2f}", value_s)],
            [Paragraph("🔴  Saldo Pendiente:", label_s), Paragraph(f"${saldo:,.2f}", saldo_style)],
        ]

    fin_table = Table(fin_rows, colWidths=[240, None])
    fin_table.setStyle(TableStyle([
        ('ROWBACKGROUNDS', (0,0), (-1,-1), [rl_colors.white, LIGHT_GREY]),
        ('GRID', (0,0), (-1,-1), 0.3, rl_colors.HexColor('#dddddd')),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('LEFTPADDING', (0,0), (-1,-1), 8),
        ('RIGHTPADDING', (0,0), (-1,-1), 8),
    ]))
    story.append(fin_table)
    story.append(Spacer(1, 12))

    # --- SECCIÓN: Reglamento / Notas ---
    if not is_futadmin:
        text = data.get('clausulas', '') or data.get('reglamento', '')
        if text and text.strip():
            sec_banner3 = Table([[Paragraph("  Reglamento y Notas", sec_style)]], colWidths=[None])
            sec_banner3.setStyle(TableStyle([
                ('BACKGROUND', (0,0),(-1,-1), rl_colors.HexColor('#555555')),
                ('TOPPADDING',(0,0),(-1,-1),6), ('BOTTOMPADDING',(0,0),(-1,-1),6),
            ]))
            story.append(sec_banner3)
            story.append(Spacer(1, 4))
            reg_style = ParagraphStyle('Reg', fontName='Helvetica', fontSize=8,
                                       textColor=rl_colors.HexColor('#444444'), leading=11)
            story.append(Paragraph(text.replace('\n', '<br/>'), reg_style))
            story.append(Spacer(1, 10))

    # --- FOOTER / FIRMA ---
    story.append(HRFlowable(width="100%", thickness=1, color=rl_colors.HexColor('#cccccc')))
    story.append(Spacer(1, 6))
    footer_style = ParagraphStyle('Footer', fontName='Helvetica-Oblique', fontSize=8,
                                  textColor=rl_colors.HexColor('#888888'), alignment=TA_CENTER)
    story.append(Paragraph(
        "Este es un comprobante digital generado automáticamente por <b>FutAdmin • futadmin.com.mx</b>.<br/>"
        "Plataforma de Gestión Deportiva — @futadmin.tj",
        footer_style))

    doc.build(story)
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

