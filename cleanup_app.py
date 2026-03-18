import os

file_path = r'c:\futadmin\app.py'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
skip = False
for i, line in enumerate(lines):
    line_no = i + 1
    
    # El desastre empieza en 2305 y termina en 2537 (aproximado)
    # Queremos mantener hasta el return de handle_combo_pagos (2303 aprox)
    # Y retomar en @app.route('/telegram_app') (2538 aprox)
    # También queremos quitar el @app.route('/api/webhook_check') (2545-2550 aprox)
    
    if line_no == 2305:
        skip = True
        print(f"Iniciando skip en línea {line_no}")
    
    if line_no == 2538:
        skip = False
        print(f"Terminando skip en línea {line_no}")
    
    if line_no == 2542:
        skip = True
        print(f"Iniciando skip (webhook) en línea {line_no}")
    
    if line_no == 2551:
        skip = False
        print(f"Terminando skip (webhook) en línea {line_no}")
        
    if not skip:
        new_lines.append(line)

with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("App.py limpiado con éxito.")
