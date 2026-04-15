import os

path = 'templates/index.html'
if os.path.exists(path):
    with open(path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Redefinir bloque style/root
    # Nos basamos en que la línea 29 es <style>
    new_lines = lines[:29]
    new_lines.append('    <style>\n')
    new_lines.append('        :root {\n')
    new_lines.append('            --primary: {{ branding.color }};\n')
    new_lines.append('            --primary-glow: {{ branding.color }}4D; /* 30% alpha */\n')
    new_lines.append('        }\n')
    # Saltamos hasta que empiece .premium-tooltip (que sabemos que está después)
    # Buscamos el índice de .premium-tooltip
    target_idx = 43
    for i, line in enumerate(lines):
        if '.premium-tooltip {' in line:
            target_idx = i
            break
    
    new_lines.extend(lines[target_idx:])

    with open(path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("SUCCESS: index.html cleaned up.")
else:
    print("ERROR: file not found.")
