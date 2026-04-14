import os, re

path = 'static/index.html'
with open(path, 'rb') as f:
    content = f.read().decode('utf-8')

# 1. Fix the syntax error (separating triggering AI from PDF export)
wrong = 'content.innerHTML =      window.exportDashboardToPDF = async function() {'
core_fix = 'content.innerHTML = "<p>Error al conectar con la IA.</p>";\n        }\n      }\n\n      window.exportDashboardToPDF = async function() {'

if wrong in content:
    content = content.replace(wrong, core_fix)
    print("Fixed syntax error.")
else:
    print("Could not find syntax error string exactly. Trying fallback.")
    # Generic fallback if spaces changed
    import re
    content = re.sub(r'content\.innerHTML\s+=\s+window\.exportDashboardToPDF\s+=\s+async\s+function\(\)\s+\{', core_fix, content)

# 2. Fix mangled UTF-8 characters specifically for the PDF
mangled_map = {
    'â ³': '⏳',
    'Â·': '|',
    'Ã¡': 'a',
    'Ã©': 'e',
    'Ã-': 'i',
    'Ã³': 'o',
    'Ãº': 'u',
    'Ã±': 'n',
    'â€”': '-',
    'PÃ¡gina': 'Pagina',
    'PÃ¡g.': 'Pag.',
    'AnÃ¡lisis': 'Analisis',
    'Ã³ptima': 'optima',
    'atenciÃ³n': 'atencion',
    'perÃ­odo': 'periodo',
    'dÃ­a': 'dia'
}

for k, v in mangled_map.items():
    content = content.replace(k, v)

# 3. Final cleanup of the duplicate button in AI panel
content = re.sub(r'(?s)<div style="display: flex; gap: 10px;">\s*<button class="btn-pdf".*?Descargar PDF.*?</button>\s*</div>', '<div style="display: flex; gap: 10px;"></div>', content)

with open(path, 'wb') as f:
    f.write(content.encode('utf-8'))

print("Completed cleanup.")
