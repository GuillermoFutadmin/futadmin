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
import threading

RESEND_API_URL = "https://api.resend.com/emails"
FUTADMIN_LOGO_URL = "https://futadmin.com.mx/static/img/logos/futadmin_circle.png"
FUTADMIN_INSTAGRAM = "https://www.instagram.com/futadmin.tj/"
FUTADMIN_WEBSITE = "https://futadmin.com.mx"


def build_receipt_email_html(nombre, liga_nombre, equipo, torneo, tipo, monto_abonado,
                              monto_pactado=0, total_pagado=0, saldo_pendiente=0,
                              metodo="Efectivo", folio="N/A", fecha=None, partido=None, is_futadmin=False,
                              tournament_details=None):
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

    # --- Seccion de Detalles del Torneo (Nueva) ---
    tournament_html = ""
    if tournament_details and not is_futadmin:
        t = tournament_details
        tournament_html = f"""
        <!-- TOURNAMENT DETAILS SECTION -->
        <tr>
          <td style="padding:15px 40px 10px;">
            <p style="margin:0 0 8px;font-size:14px;font-weight:700;color:#1a1a2e;border-left:4px solid #f1c40f;padding-left:10px;">Información del Torneo / Reglamento</p>
            <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid #e8e8e8;border-radius:8px;overflow:hidden;font-size:12px;background:#fffef0;">
              <tr>
                <td style="padding:6px 12px;color:#555;border-bottom:1px solid #f0f0f0;width:40%;">📅 Inicio de Torneo</td>
                <td style="padding:6px 12px;font-weight:600;border-bottom:1px solid #f0f0f0;color:#d35400;">{t.get('fecha_inicio', 'Pendiente')}</td>
              </tr>
              <tr>
                <td style="padding:6px 12px;color:#555;border-bottom:1px solid #f0f0f0;">🕒 Horarios / Días</td>
                <td style="padding:6px 12px;font-weight:600;border-bottom:1px solid #f0f0f0;">{t.get('horarios', 'S/H')}</td>
              </tr>
              <tr>
                <td style="padding:6px 12px;color:#555;border-bottom:1px solid #f0f0f0;">🏆 Premios</td>
                <td style="padding:6px 12px;font-weight:600;border-bottom:1px solid #f0f0f0;color:#c0392b;">{t.get('premios', 'Ver reglamento')}</td>
              </tr>
              <tr>
                <td style="padding:6px 12px;color:#555;border-bottom:1px solid #f0f0f0;">🏢 Organiza</td>
                <td style="padding:6px 12px;font-weight:600;border-bottom:1px solid #f0f0f0;">{t.get('organiza', 'FutAdmin')}</td>
              </tr>
              <tr>
                <td style="padding:6px 12px;color:#555;">📞 Contacto</td>
                <td style="padding:6px 12px;font-weight:600;">{t.get('contacto', 'No disponible')}</td>
              </tr>
            </table>
            <div style="margin-top:10px;padding:12px;background:#f9f9f9;border:1px solid #eee;border-radius:8px;font-size:11px;color:#666;line-height:1.5;max-height:150px;overflow-y:auto;">
                <strong>REGLAS Y CLÁUSULAS:</strong><br>
                { (t.get('reglamento','') + ' ' + t.get('clausulas','')).strip() or 'Consultar con el organizador.' }
            </div>
          </td>
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
                Este documento acredita el pago realizado por el equipo <strong>{equipo}</strong> en el torneo <strong>{torneo}</strong> de la liga <strong>{liga_nombre}</strong>. Consérvalo como comprobante oficial.
            </p>
          </td>
        </tr>

        {tournament_html}

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
                <td style="padding:8px 12px;color:#555;border-bottom:1px solid #f0f0f0;">{ '📊 Capacidad' if is_futadmin else '👕 Equipo' }</td>
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
              📎 <strong>PDF adjunto:</strong> El recibo oficial en PDF está adjunto con el reglamento completo del torneo.
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

    is_futadmin = data.get('is_futadmin', False)
    
    # Si es futadmin (Combo), usamos el generador de Estado de Cuenta detallado
    if is_futadmin:
        return generate_statement_pdf(data, filename)

    doc = SimpleDocTemplate(filename, pagesize=letter,
                            leftMargin=0.6*inch, rightMargin=0.6*inch,
                            topMargin=0.4*inch, bottomMargin=0.5*inch)
    story = []
    styles = getSampleStyleSheet()

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
    torneo_nombre = data.get('torneo', '')
    liga_m = data.get('liga_nombre', 'FutAdmin')
    
    greeting_style = ParagraphStyle('Greeting', fontName='Helvetica', fontSize=10,
                                    textColor=DARK_TEXT, alignment=TA_LEFT, leading=14)
    
    greeting_text = f"Este documento acredita el pago realizado por el equipo <b>{equipo_nombre}</b> en el torneo <b>{torneo_nombre}</b> de la liga <b>{liga_m}</b>. Consérvelo como comprobante oficial."
        
    story.append(Paragraph(greeting_text, greeting_style))
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

    detail_rows = [
        [Paragraph("Liga / Administrador:", label_s), Paragraph(liga_nombre, value_s)],
        [Paragraph("Equipo:", label_s), Paragraph(data.get('equipo','N/A'), value_s)],
        [Paragraph("Torneo:", label_s), Paragraph(data.get('torneo','N/A'), value_s)],
        [Paragraph("Inicio Torneo:", label_s), Paragraph(data.get('fecha_inicio_torneo','Pendiente'), value_s)],
        [Paragraph("Horarios / Días:", label_s), Paragraph(data.get('horarios','N/A'), value_s)],
        [Paragraph("Sede:", label_s), Paragraph(data.get('sede','Por definir'), value_s)],
        [Paragraph("Tipo / Formato:", label_s), Paragraph(f"{data.get('tipo_torneo','Liga')} / {data.get('formato','Torneo')}", value_s)],
        [Paragraph("Organiza / Contacto:", label_s), Paragraph(f"{data.get('organiza','FutAdmin')} - {data.get('contacto','')}", value_s)],
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
    text = data.get('clausulas', '') or data.get('reglamento', '')
    if text and text.strip():
        sec_banner3 = Table([[Paragraph("  Reglamento, Premios y Notas", sec_style)]], colWidths=[None])
        sec_banner3.setStyle(TableStyle([
            ('BACKGROUND', (0,0),(-1,-1), rl_colors.HexColor('#555555')),
            ('TOPPADDING',(0,0),(-1,-1),6), ('BOTTOMPADDING',(0,0),(-1,-1),6),
        ]))
        story.append(sec_banner3)
        story.append(Spacer(1, 4))
        
        reg_style = ParagraphStyle('Reg', fontName='Helvetica', fontSize=8,
                                   textColor=rl_colors.HexColor('#444444'), leading=11)

        premios = data.get('premios', '')
        if premios:
            story.append(Paragraph(f"<b>PREMIOS:</b> {premios}", reg_style))
            story.append(Spacer(1, 6))

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

def generate_statement_pdf(data, filename):
    """
    Genera un PDF 'Estado de Cuenta' detallado (Imagen 2) con historial, métricas y términos legales.
    """
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, HRFlowable, Image as RLImage, PageBreak
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
                            leftMargin=0.5*inch, rightMargin=0.5*inch,
                            topMargin=0.4*inch, bottomMargin=0.4*inch)
    story = []
    styles = getSampleStyleSheet()
    
    liga_name = data.get('liga_nombre', 'Organización')
    fecha     = data.get('fecha', datetime.now().strftime('%d/%m/%Y'))
    id_cliente = data.get('id_cliente', 'N/A')

    # --- ESTILOS ---
    h1 = ParagraphStyle('H1', fontName='Helvetica-Bold', fontSize=14, textColor=DARK_TEXT, spaceAfter=2)
    label_s = ParagraphStyle('LabelS', fontName='Helvetica-Bold', fontSize=10, textColor=DARK_TEXT)
    value_s = ParagraphStyle('ValueS', fontName='Helvetica', fontSize=10, textColor=rl_colors.HexColor('#444444'))
    small_label = ParagraphStyle('SmallL', fontName='Helvetica-Bold', fontSize=8, textColor=rl_colors.white)
    small_val = ParagraphStyle('SmallV', fontName='Helvetica', fontSize=8, textColor=DARK_TEXT)

    # --- HEADER ---
    logo_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             'static', 'img', 'logos', 'futadmin_circle.png')
    logo_elem = RLImage(logo_path, width=60, height=60) if os.path.exists(logo_path) else Paragraph("", styles['Normal'])

    header_content = [
        logo_elem,
        [
            Paragraph("FutAdmin PRO", ParagraphStyle('PT', fontName='Helvetica-Bold', fontSize=24, textColor=rl_colors.white)),
            Paragraph("ESTADO DE CUENTA Y RESUMEN OPERATIVO", ParagraphStyle('PS', fontName='Helvetica', fontSize=10, textColor=TEAL)),
            Paragraph(f"ORGANIZACIÓN: {liga_name.upper()}", ParagraphStyle('PO', fontName='Helvetica', fontSize=10, textColor=rl_colors.white))
        ],
        [
            Paragraph(f"Generado: {fecha}", ParagraphStyle('PG', fontName='Helvetica', fontSize=10, textColor=rl_colors.white, alignment=TA_RIGHT)),
            Paragraph(f"ID Cliente: {id_cliente}", ParagraphStyle('PI', fontName='Helvetica', fontSize=10, textColor=rl_colors.white, alignment=TA_RIGHT))
        ]
    ]
    header_table = Table([header_content], colWidths=[70, 320, 110])
    header_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), DARK_BG),
        ('VALIGN',     (0,0), (-1,-1), 'MIDDLE'),
        ('LEFTPADDING',(0,0), (-1,-1), 15), ('TOPPADDING', (0,0), (-1,-1), 12), ('BOTTOMPADDING',(0,0),(-1,-1), 12)
    ]))
    story.append(header_table)
    story.append(Spacer(1, 15))

    # --- SECCION 1: RESUMEN DE MEMBRESÍA ---
    story.append(Paragraph("RESUMEN DE MEMBRESÍA", h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=TEAL, spaceAfter=10))
    
    stats = data.get('stats', {})
    membership_data = [
        [Paragraph("Organización:", label_s), Paragraph(liga_name, value_s), Paragraph("Plan Actual:", label_s), Paragraph(data.get('paquete', 'N/A').upper(), value_s)],
        [Paragraph("Meses Pagados:", label_s), Paragraph(f"{stats.get('total_meses_pagados', 0)} Mes(es)", value_s), Paragraph("Costo Mensual:", label_s), Paragraph(f"${data.get('monto_total_mensual', 0):,.2f} MXN", value_s)],
        [Paragraph("Próximo Pago:", label_s), Paragraph(data.get('vencimiento', 'Vigente'), value_s), Paragraph("Monto a Pagar:", label_s), Paragraph(f"${data.get('monto_total_mensual', 0):,.2f} MXN", value_s)],
    ]
    mem_table = Table(membership_data, colWidths=[110, 140, 110, 140])
    mem_table.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP'), ('BOTTOMPADDING',(0,0),(-1,-1),6)]))
    story.append(mem_table)
    story.append(Spacer(1, 10))

    # --- SECCION 2: INFRAESTRUCTURA Y CAPACIDAD ---
    story.append(Paragraph("INFRAESTRUCTURA Y CAPACIDAD", h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=TEAL, spaceAfter=10))
    
    cap_sedes = 1 + (data.get('extra_canchas', 0))
    cap_ligas = 5 + (data.get('extra_torneos', 0))
    sedes_list = data.get('detalles', {}).get('canchas', []) or ["Ninguna registrada"]
    ligas_list = data.get('detalles', {}).get('torneos', []) or ["Ninguna registrada"]

    sedes_p = [Paragraph(f"<b>Sedes ({len(sedes_list)} de {cap_sedes} Permitidas):</b>", label_s)] + [Paragraph(f"• {s}", value_s) for s in sedes_list]
    ligas_p = [Paragraph(f"<b>Torneos ({len(ligas_list)} de {cap_ligas} Permitidos):</b>", label_s)] + [Paragraph(f"• {l}", value_s) for l in ligas_list]

    infra_table = Table([[sedes_p, ligas_p]], colWidths=[250, 250])
    infra_table.setStyle(TableStyle([('VALIGN',(0,0),(-1,-1),'TOP')]))
    story.append(infra_table)
    story.append(Spacer(1, 15))

    # --- SECCION 3: IMPACTO OPERATIVO ---
    impacto_data = [[Paragraph(f"<b>Impacto Operativo:</b> &nbsp;&nbsp; {stats.get('equipos', 0)} Equipos Inscritos &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp; {stats.get('jugadores', 0)} Jugadores Registrados", value_s)]]
    impacto_table = Table(impacto_data, colWidths=[500])
    impacto_table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1), LIGHT_GREY), ('ALIGN',(0,0),(-1,-1),'CENTER'), ('PADDING',(0,0),(-1,-1),10)]))
    story.append(impacto_table)
    story.append(Spacer(1, 20))

    # --- SECCION 4: HISTÓRICO DE INCREMENTOS ---
    story.append(Paragraph("HISTÓRICO DE INCREMENTOS DE COMBOS", h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=TEAL, spaceAfter=8))
    
    exp_header = [Paragraph("FECHA", small_label), Paragraph("TIPO DE CAMBIO", small_label), Paragraph("CANT.", small_label), Paragraph("MONTO ADIC.", small_label), Paragraph("ESTATUS", small_label)]
    exp_rows = [exp_header]
    
    # Fila Inicial
    exp_rows.append([Paragraph(data.get('fecha_registro', ''), small_val), Paragraph("Combo Base (Inscripción)", small_val), Paragraph("1 Sede / 5 Ligas", small_val), Paragraph(f"${data.get('monto_mensual', 0):,.2f}", small_val), Paragraph("<b>ACTIVO</b>", ParagraphStyle('A', fontSize=8, textColor=GREEN_COLOR))])
    
    for e in data.get('expansiones', []):
        desc = "Sede Extra" if e.get('tipo', '') == 'extra_canchas' else "Torneo Extra"
        cant = f"+{e.get('cantidad', 0)}" if e.get('cantidad',0) > 0 else str(e.get('cantidad', 0))
        monto = f"${e.get('monto_adicional', 0):,.2f}" if e.get('monto_adicional',0) > 0 else ("--" if e.get('cantidad',0) < 0 else "Combo")
        status = "ACTIVO" if e.get('cantidad',0) > 0 else "BAJA"
        s_color = GREEN_COLOR if status == "ACTIVO" else RED_COLOR
        exp_rows.append([Paragraph(e.get('fecha','').split(' ')[0], small_val), Paragraph(desc, small_val), Paragraph(cant, small_val), Paragraph(monto, small_val), Paragraph(f"<b>{status}</b>", ParagraphStyle('S', fontSize=8, textColor=s_color))])

    exp_table = Table(exp_rows, colWidths=[70, 160, 90, 100, 80])
    exp_table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0), rl_colors.HexColor('#505050')), ('GRID',(0,0),(-1,-1),0.5, rl_colors.grey), ('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
    story.append(exp_table)
    story.append(Spacer(1, 20))

    # --- SECCION 5: HISTORIAL DE APORTACIONES ---
    story.append(Paragraph("HISTORIAL DE APORTACIONES MENSUALES", h1))
    story.append(HRFlowable(width="100%", thickness=1.5, color=TEAL, spaceAfter=8))
    
    pay_header = [Paragraph("FECHA PAGO", small_label), Paragraph("MES CUBIERTO / CONCEPTO", small_label), Paragraph("MÉTODO", small_label), Paragraph("MONTO PAGADO", small_label)]
    pay_rows = [pay_header]
    
    for p in data.get('pagos_historial', []):
        pay_rows.append([Paragraph(p.get('fecha',''), small_val), Paragraph(p.get('mes_pagado',''), small_val), Paragraph(p.get('metodo',''), small_val), Paragraph(f"<b>${p.get('monto',0):,.2f}</b>", small_val)])
    
    if len(pay_rows) == 1:
        pay_rows.append([Paragraph("No se han registrado pagos históricos.", small_val), "", "", ""])

    pay_table = Table(pay_rows, colWidths=[100, 200, 100, 100])
    pay_table.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0), rl_colors.HexColor('#323232')), ('GRID',(0,0),(-1,-1),0.5, rl_colors.grey), ('VALIGN',(0,0),(-1,-1),'MIDDLE')]))
    story.append(pay_table)
    story.append(PageBreak())

    # --- SECCION 6: TÉRMINOS LEGALES (PAGINA 2) ---
    story.append(Paragraph("TÉRMINOS, CONDICIONES Y RESPONSABILIDADES LEGALES:", ParagraphStyle('LegalT', fontName='Helvetica-Bold', fontSize=12, textColor=rl_colors.HexColor('#666666'))))
    story.append(HRFlowable(width="100%", thickness=1, color=rl_colors.HexColor('#666666'), spaceAfter=10))
    
    legal_style = ParagraphStyle('Legal', fontName='Helvetica', fontSize=8.5, textColor=rl_colors.HexColor('#555555'), leading=11, alignment=TA_LEFT, spaceAfter=8)
    legal_bold  = ParagraphStyle('LegalB', fontName='Helvetica-Bold', fontSize=8.5, textColor=rl_colors.HexColor('#444444'), leading=11, spaceAfter=2)

    full_legal_1 = "Conforme a lo dispuesto en el Código de Comercio y la Ley Federal de Protección al Consumidor, FutAdmin se constituye exclusivamente como un proveedor de Software como Servicio (SaaS). Su función primordial es proveer herramientas tecnológicas avanzadas para el control de ingresos, gestión de roles y automatización de estadísticas deportivas. La plataforma NO interviene, organiza, ni supervisa la logística física de los torneos, partidos, traslados o la integridad física de los participantes en campo. El Administrador de la Liga reconoce que es el único responsable de la ejecución técnica y operativa de sus eventos deportivos. FutAdmin no se hace responsable por daños directos o indirectos derivados de cancelaciones, lesiones físicas o disputas legales entre terceros asociados a la organización. La relación jurídica entre FutAdmin y la Organización se limita estrictamente a la licencia temporal de uso del software. Cualquier falla técnica será atendida bajo los niveles de servicio estipulados, pero no generará bajo ninguna circunstancia derecho a indemnizaciones por lucro cesante o pérdida de oportunidades de negocio. El uso de la plataforma por parte del Administrador implica la aceptación total de que FutAdmin es un facilitador administrativo y no un garante de la seguridad o el éxito comercial de la liga. El Administrador debe asegurar proactivamente que todo su personal y usuarios finales sigan estrictamente las normativas locales vigentes de protección civil y reglamentos deportivos municipales."
    full_legal_2 = "El tratamiento de la información personal dentro del sistema se rige por la Ley Federal de Protección de Datos Personales en Posesión de los Particulares (LFPDPPP), específicamente cumpliendo con sus artículos 8, 12, 16 y 17. En esta relación contractual, la Organización (Liga) actúa como el 'Responsable' absoluto del tratamiento de los datos de sus jugadores, equipos y personal, mientras que FutAdmin actúa únicamente como el 'Encargado' del almacenamiento técnico. Es obligación irrenunciable y exclusiva de la Organización contar con su propio Aviso de Privacidad vigente y obtener el consentimiento informado y expreso de sus usuarios para la captura de nombres, teléfonos, correos y datos biométricos. FutAdmin implementa medidas de seguridad técnicas y administrativas de alta calidad para proteger la base de datos contra accesos no autorizados, conforme a los estándares marcados por el Reglamento de la LFPDPPP. Los derechos ARCO (Acceso, Rectificación, Cancelación y Oposición) deben ser garantizados y gestionados primordialmente por el Administrador de la Liga ante sus inscritos. FutAdmin no comercializa, transfiere ni utiliza los datos de los jugadores para fines publicitarios o distintos a la operación técnica necesaria del sistema. En caso de una vulneración de seguridad imputable a la negligencia del Administrador (como el intercambio de contraseñas o descuido en los accesos), FutAdmin queda exento de toda responsabilidad legal, civil o pecunaria por el mal uso de dicha información."
    full_legal_3 = "En estricto cumplimiento con la Ley General de los Derechos de Niñas, Niños y Adolescentes (LGDNNA), particularmente lo ordenado en los artículos 76, 77 y 78, se prohíbe terminantemente la difusión, publicación o manejo de imágenes y datos personales de menores de edad que permitan su plena identificación sin el consentimiento parental expreso, por escrito y verificable. El Administrador de la Liga es el único responsable legal ante las autoridades de verificar que cada fotografía de menor de edad subida al sistema cuente con la autorización firmada por los padres o tutores legales, autorizando específicamente el uso en listas de asistencia, credenciales digitales o perfiles de liguilla públicos. El principio del 'Interés Superior de la Niñez' debe prevalecer sobre cualquier necesidad administrativa o deportiva de la liga. FutAdmin provee las herramientas técnicas para permitir al administrador restringir la visibilidad de estos datos, pero la decisión final de publicar perfiles públicos de menores recae exclusivamente en la voluntad y gestión de la Organización. Cualquier violación a este derecho fundamental a la intimidad, o la exposición de menores a situaciones de riesgo por un manejo inadecuado de la plataforma, será responsabilidad penal y administrativa directa del Administrador de la Liga, deslindando a FutAdmin de cualquier proceso judicial o sanción derivada del incumplimiento de las normativas de la LGDNNA de Protección a la Niñez."
    full_legal_4 = "El software FutAdmin, así como su código fuente, interfaces gráficas, algoritmos y logotipos asociados están protegidos por la Ley Federal del Derecho de Autor (artículos 101 y subsiguientes) y la Ley Federal de Protección a la Propiedad Industrial. Se otorga a la Organización una licencia de uso personal, intransferible y temporal mientras el pago se mantenga al corriente. Queda estrictamente prohibida la ingeniería inversa, copia no autorizada o distribución de cualquier módulo del software sin la autorización expresa y por escrito de FutAdmin. Respecto a los costos de operación, conforme al Código Civil Federal y el Código de Comercio, los montos se determinan por la capacidad técnica activa contratada (Sedes y Ligas extras habilitadas). La falta de pago oportuno generará la suspensión automática del acceso al sistema tras concluir el periodo de gracia establecido. Las cancelaciones de paquetes o reducciones de plan deben solicitarse con al menos 5 días hábiles de anticipación para ser procesadas antes del siguiente cierre. Los periodos de tiempo ya pagados o activaciones de capacidad técnica realizadas ('Combos') NO son reembolsables, ya que el servicio tecnológico se considera devengado al momento de habilitar el recurso en el servidor. La Organización acepta que los costos pueden ser actualizados periódicamente conforme a la inflación o mejoras estructurales críticas, notificando siempre con antelación a través del panel administrativo oficial."

    story.append(Paragraph("1. NATURALEZA DEL SERVICIO Y LIMITACIÓN DE RESPONSABILIDAD (CÓDIGO DE COMERCIO Y LFPC):", legal_bold))
    story.append(Paragraph(full_legal_1, legal_style))
    story.append(Paragraph("2. PROTECCIÓN DE DATOS PERSONALES Y DERECHOS ARCO (LFPDPPP):", legal_bold))
    story.append(Paragraph(full_legal_2, legal_style))
    story.append(Paragraph("3. TUTELA DE DERECHOS DE MENORES Y DERECHO A LA INTIMIDAD (LGDNNA):", legal_bold))
    story.append(Paragraph(full_legal_3, legal_style))
    story.append(Paragraph("4. PROPIEDAD INTELECTUAL Y CONDICIONES DE COBRO (LFDA):", legal_bold))
    story.append(Paragraph(full_legal_4, legal_style))

    story.append(Spacer(1, 20))
    story.append(Paragraph("DOCUMENTO OFICIAL - WWW.FUTADMIN.COM.MX", ParagraphStyle('F', fontSize=8, textColor=GREEN_COLOR, alignment=TA_CENTER, fontName='Helvetica-Bold')))

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
            "html": body
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

        msg.attach(MIMEText(body, 'html'))

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


def trigger_receipt_email_async(ticket_data, recipient_email, recipient_name="Administrador"):
    """Helper para generar PDF y enviar correo de recibo en un hilo separado (no bloqueante)."""
    def internal_worker(data, email, name):
        _log_mail(f"THREAD START: Preparando envío para {email} (Folio: {data.get('folio')})")
        try:
            import os, tempfile
            from datetime import timedelta, datetime
            
            # 1. Asegurar fecha local si no viene (Tijuana -7)
            # Generar fecha local para el recibo (Offset de 6 horas para México)
            if not data.get('fecha'):
                from datetime import datetime, timedelta
                data['fecha'] = (datetime.utcnow() - timedelta(hours=6)).strftime('%d/%m/%Y %H:%M')

            # 2. Directorio temporal
            temp_dir = tempfile.gettempdir()
            filename = f"recibo_{data.get('folio', 'pago')}.pdf"
            pdf_path = os.path.join(temp_dir, filename)

            # 3. Generar PDF
            generate_receipt_pdf(data, pdf_path)
            
            # 4. Asunto según contexto
            is_futadmin = data.get('is_futadmin', False)
            liga_n = data.get('liga_nombre', 'FutAdmin')
            if is_futadmin:
                subject = f"Comprobante de Pago - FutAdmin - {liga_n}"
            else:
                subject = f"Recibo de Pago - {liga_n} - {data.get('equipo', 'Equipo')}"

            # 5. Cuerpo HTML
            body = build_receipt_email_html(
                nombre=name,
                liga_nombre=liga_n,
                equipo=data.get('equipo', ''),
                torneo=data.get('torneo', ''),
                tipo=data.get('tipo', 'Abono'),
                monto_abonado=float(data.get('monto_abonado', 0)),
                monto_pactado=float(data.get('monto_pactado', 0)),
                total_pagado=float(data.get('total_pagado', 0)),
                saldo_pendiente=float(data.get('saldo_pendiente', 0)),
                metodo=data.get('metodo', 'Efectivo'),
                folio=data.get('folio', 'N/A'),
                fecha=data.get('fecha'),
                partido=data.get('partido'),
                is_futadmin=is_futadmin,
                tournament_details=data # Pasar todo el dict para extraer detalles extra
            )

            # 6. Enviar vía Resend (o fallback SMTP interno)
            send_receipt_email(email, subject, body, pdf_path)
            
            # 7. Limpieza
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
        except Exception as e:
            msg = f"Error asíncrono en envío de recibo (logic_async): {e}"
            print(msg)
            # Log to file for production visibility
            try:
                log_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "mail_debug.log")
                with open(log_path, "a", encoding="utf-8") as f:
                    from datetime import datetime
                    f.write(f"[{datetime.now()}] THREAD ERROR: {msg}\n")
            except:
                pass

    threading.Thread(target=internal_worker, args=(ticket_data, recipient_email, recipient_name), daemon=True).start()
