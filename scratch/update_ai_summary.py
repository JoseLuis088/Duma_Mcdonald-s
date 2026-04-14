path = 'static/index.html'
with open(path, 'rb') as f:
    content = f.read().decode('utf-8')

# Update the AI summary to include device type and pressure context
old = (". Uptime: ' + (kpis.availability||'N/A') + '. Carga: ' + "
       "(kpis.avg_load||'N/A') + '. Desbalance: ' + (kpis.imbalance||'N/A') + "
       "(kpis.avg_pressure ? '. Presion: ' + kpis.avg_pressure : '') + '.'")

new = (". Uptime: ' + (kpis.availability||'N/A') + '. Carga maxima: ' + "
       "(kpis.avg_load||'N/A') + '. Desbalance: ' + (kpis.imbalance||'N/A') + "
       "(kpis.avg_pressure ? '. Presion promedio: ' + kpis.avg_pressure + "
       "' (umbral critico: menos de 20 PSI es alerta)' : '') + '.'")

if old in content:
    content = content.replace(old, new)
    print("AI summary updated OK")
else:
    print("Pattern not found, trying line-by-line search...")
    lines = content.split('\n')
    for i, line in enumerate(lines):
        if "Uptime" in line and "Carga" in line and "Desbalance" in line and "Presion" in line:
            print(f"Found at line {i+1}: {repr(line[:120])}")
            lines[i] = line.replace(
                "'. Carga: '",
                "'. Carga maxima: '"
            ).replace(
                "'. Presion: ' + kpis.avg_pressure",
                "'. Presion promedio: ' + kpis.avg_pressure + ' (umbral critico: menos de 20 PSI es alerta)'"
            )
            print(f"Fixed to: {repr(lines[i][:120])}")
    content = '\n'.join(lines)

# Also add device label to summary
old2 = "const summary = 'Sucursal: '"
new2 = ("const deviceLabel = (typeof currentDeviceType !== 'undefined' ? currentDeviceType : 'Maquina de nieve');\n"
        "          const summary = 'Equipo: ' + deviceLabel + '. Sucursal: '")

if old2 in content:
    content = content.replace(old2, new2)
    print("Device label added OK")
else:
    print("Could not find const summary line")

with open(path, 'wb') as f:
    f.write(content.encode('utf-8'))
print("Done.")
