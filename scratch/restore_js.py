path = 'static/index.html'
with open(path, 'rb') as f:
    content = f.read().decode('utf-8')

import re

# Block to find: from the end of renderPressureChart to the start of exportDashboardToPDF
# I'll look for the end of Plotly.newPlot for pressurePlot

pattern = re.compile(r'textfont: \{ size: 9, color: tc \}\n\s+\}\], \{ responsive: true, displayModeBar: false \}\);\n\s+\}\n\s+.*?\n\s+window\.exportDashboardToPDF', re.DOTALL)

new_block = """textfont: { size: 9, color: tc }
        }], { responsive: true, displayModeBar: false });
      }

      function renderAvailabilityChart(dailyData) {
        const isDark = document.documentElement.getAttribute('data-theme') === 'dark';
        const tc = isDark ? '#e2e8f0' : '#1e293b';
        const gc = isDark ? 'rgba(255,255,255,0.05)' : 'rgba(0,0,0,0.07)';
        Plotly.newPlot('availPlot', [{
          x: dailyData.map(function(d){ return d.date; }),
          y: dailyData.map(function(d){ return d.value; }),
          type: 'bar',
          marker: { color: dailyData.map(function(v){ return v.value >= 90 ? '#4ade80' : v.value >= 70 ? '#facc15' : '#f87171'; }) }
        }], {
          paper_bgcolor: 'transparent', plot_bgcolor: 'transparent',
          margin: {t:10, r:10, b:50, l:45},
          font: { family: 'Inter, sans-serif', color: tc },
          xaxis: { gridcolor: gc, tickfont: { size: 9, color: tc } },
          yaxis: { range: [0,105], title: { text: '% Uptime', font: {size:10} }, tickfont: { size: 9, color: tc } }
        }, { responsive: true, displayModeBar: false });
      }

      window.toggleFullscreenChart = function(cardId, plotId, defaultHeight) {
        const card = el(cardId);
        const plot = el(plotId);
        if (!card || !plot) return;
        const isFS = card.classList.toggle('fs-overlay');
        plot.style.height = isFS ? 'calc(100vh - 120px)' : (defaultHeight || '400px');
        document.body.style.overflow = isFS ? 'hidden' : 'auto';
        Plotly.Plots.resize(plot);
      };

      // ---------------------------------------------------------
      // 6. AI & PDF
      // ---------------------------------------------------------
      async function triggerAIAnalysis(data, ciudad, sucursal, from, to) {
        const container = el('aiAnalysisContainer');
        const content   = el('aiContent');
        if (!container || !content) return;
        container.style.display = 'block';
        content.innerHTML = '<div class="ai-loading"><div class="ai-pulse"></div><div style="font-weight:700;color:var(--brand);">DUMA analizando equipos críticos...</div></div>';
        try {
          const kpis = data.kpis || {};
          const deviceLabel = (typeof currentDeviceType !== 'undefined' ? currentDeviceType : 'Maquina de nieve');
          const summary = 'Equipo: ' + deviceLabel + '. Sucursal: ' + sucursal + ' (' + ciudad + '). Periodo: ' + from + ' a ' + to +
                          '. Uptime: ' + (kpis.availability||'N/A') + '. Carga maxima: ' + (kpis.avg_load||'N/A') + '. Desbalance: ' + (kpis.imbalance||'N/A') + (kpis.avg_pressure ? '. Presion promedio: ' + kpis.avg_pressure + ' (umbral critico: menos de 20 PSI es alerta)' : '') + '.';
          const res = await fetch('/api/sense/ai-analysis', {
            method: 'POST',
            headers: {'Content-Type':'application/json'},
            body: JSON.stringify({summary: summary})
          });
          const json = await res.json();
          content.innerHTML = mdToHtml(json.report || 'No se pudo generar el análisis.');
        } catch(e) {
          content.innerHTML = "<p>Error al conectar con la IA.</p>";
        }
      }

      window.exportDashboardToPDF"""

if pattern.search(content):
    content = pattern.sub(new_block, content)
    print("Restore successful via Pattern")
else:
    print("Pattern not found, trying fallback...")
    # Fallback to lines 2309 to 2346 roughly
    lines = content.split('\n')
    # Try to find the gaps
    start_idx = -1
    end_idx = -1
    for i, line in enumerate(lines):
        if 'textfont: { size: 9, color: tc }' in line: start_idx = i
        if 'window.exportDashboardToPDF' in line: end_idx = i
    if start_idx != -1 and end_idx != -1:
        print(f"Replacing lines {start_idx+1} to {end_idx}")
        # Build the block carefully
        prefix = lines[:start_idx]
        suffix = lines[end_idx:]
        # Note: the new_block already contains the start/end lines
        # I'll just adjust the new_block to fit exactly
        mid = new_block.split('\n')
        content = '\n'.join(prefix + mid + suffix)
        print("Restore successful via Line Indices")

with open(path, 'wb') as f:
    f.write(content.encode('utf-8'))
print("Done.")
