
# Fix orphan duplicate HTML + add pressure threshold line to chart
path = 'static/index.html'
with open(path, 'rb') as f:
    content = f.read().decode('utf-8')

# 1. Remove orphan duplicate KPI HTML (lines 1945-1950 area)
orphan = '''          \r\n              <div class="kpi-card glass">\r\n                <div class="kpi-label">CARGA MÁXIMA</div>\r\n                <div class="kpi-value" id="kpi-load">--</div>\r\n                <div class="kpi-sub">Pico de seguridad por fase</div>\r\n              </div>\r\n            </div>\r\n'''
content = content.replace(orphan, '\n')
print("Step 1 done - orphan removed:", orphan in content)

# 2. Add horizontal threshold line at 20 PSI in renderPressureChart
old_pressure_chart_end = '''        }, { responsive: true, displayModeBar: false });
      }

      function renderAvailabilityChart'''

new_pressure_chart_end = '''        }, { responsive: true, displayModeBar: false });
      }

      function renderAvailabilityChart'''

# The pressure chart function - add shapes for threshold line
old_pressure = '''        Plotly.newPlot('pressurePlot', [{
          x: pData.labels, y: pData.values, type: 'bar',
          marker: { color: colors }
        }], {
          paper_bgcolor: 'transparent', plot_bgcolor: 'transparent',
          margin: {t:10, r:10, b:40, l:40},
          font: { family: 'Inter, sans-serif', color: tc },
          xaxis: { gridcolor: gc, tickfont: { size: 9, color: tc } },
          yaxis: { title: { text: 'PSI', font: {size:10} }, gridcolor: gc, tickfont: { size: 9, color: tc } }
        }, { responsive: true, displayModeBar: false });'''

new_pressure = '''        var yMax = Math.max(30, Math.max(...pData.values) * 1.1);
        Plotly.newPlot('pressurePlot', [{
          x: pData.labels, y: pData.values, type: 'bar',
          name: 'Presion PSI',
          marker: { color: colors },
          text: pData.values.map(v => v.toFixed(1) + ' PSI'),
          textposition: 'outside',
          textfont: { size: 9, color: tc }
        }], {
          paper_bgcolor: 'transparent', plot_bgcolor: 'transparent',
          margin: {t:20, r:10, b:40, l:45},
          font: { family: 'Inter, sans-serif', color: tc },
          xaxis: { gridcolor: gc, tickfont: { size: 9, color: tc } },
          yaxis: { range: [0, yMax], title: { text: 'PSI', font: {size:10} }, gridcolor: gc, tickfont: { size: 9, color: tc } },
          shapes: [{
            type: 'line', x0: 0, x1: 1, xref: 'paper',
            y0: 20, y1: 20, yref: 'y',
            line: { color: '#f87171', width: 2, dash: 'dash' }
          }],
          annotations: [{
            x: 1, xref: 'paper', y: 20, yref: 'y',
            text: 'Min 20 PSI', showarrow: false,
            font: { size: 9, color: '#f87171' },
            xanchor: 'right', yanchor: 'bottom'
          }]
        }, { responsive: true, displayModeBar: false });'''

content = content.replace(old_pressure, new_pressure)
print("Step 2 done - threshold line added")

with open(path, 'wb') as f:
    f.write(content.encode('utf-8'))
print("Saved.")
