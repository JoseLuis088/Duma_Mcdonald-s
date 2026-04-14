path = 'static/index.html'
with open(path, 'rb') as f:
    content = f.read().decode('utf-8')

import re

# 1. Fix renderPressureChart (Restore layout, shapes, and annotations)
# Using a more robust string match instead of complex regex first
old_p = 'textfont: { size: 9, color: tc }\n        }], { responsive: true, displayModeBar: false });'
new_p = """textfont: { size: 9, color: tc }
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
        }, { responsive: true, displayModeBar: false });"""

if old_p in content:
    content = content.replace(old_p, new_p)
    print("Fixed Pressure Chart")
else:
    # Try with raw string in case of line ending diffs
    old_p_raw = 'textfont: { size: 9, color: tc }\r\n        }], { responsive: true, displayModeBar: false });'
    if old_p_raw in content:
        content = content.replace(old_p_raw, new_p)
        print("Fixed Pressure Chart (Raw)")
    else:
        print("Could not find pressure chart pattern")

# 2. Cleanup fetchSenseData (Remove redundant listeners)
# They were at lines 2248-2250 roughly
listeners = """            el('btnToggleFS') && el('btnToggleFS').addEventListener('click', () => toggleFullscreenChart('mainChartCard', 'sensePlot', '400px'));
            el('btnToggleAvail') && el('btnToggleAvail').addEventListener('click', () => toggleFullscreenChart('availChartCard', 'availPlot', '250px'));
            el('btnTogglePressure') && el('btnTogglePressure').addEventListener('click', () => toggleFullscreenChart('pressureChartCard', 'pressurePlot', '250px'));"""

if listeners in content:
    content = content.replace(listeners, "")
    print("Cleaned up fetchSenseData listeners")
else:
    # Try with CRLF
    listeners_crlf = listeners.replace('\n', '\r\n')
    if listeners_crlf in content:
        content = content.replace(listeners_crlf, "")
        print("Cleaned up fetchSenseData listeners (CRLF)")
    else:
        print("Could not find listeners pattern")

# 3. Add listeners to window.onload correctly
onload_mark = "el('btnClear') && el('btnClear').addEventListener('click', function(){"
listeners_to_add = """// Pantalla Completa Listeners
        el('btnToggleFS') && el('btnToggleFS').addEventListener('click', () => toggleFullscreenChart('mainChartCard', 'sensePlot', '400px'));
        el('btnToggleAvail') && el('btnToggleAvail').addEventListener('click', () => toggleFullscreenChart('availChartCard', 'availPlot', '250px'));
        el('btnTogglePressure') && el('btnTogglePressure').addEventListener('click', () => toggleFullscreenChart('pressureChartCard', 'pressurePlot', '250px'));

        el('btnClear') && el('btnClear').addEventListener('click', function(){"""

if onload_mark in content:
    content = content.replace(onload_mark, listeners_to_add)
    print("Added listeners to onload")

# 4. Remove double exportDashboardToPDF
content = content.replace("window.exportDashboardToPDF\n      window.exportDashboardToPDF = async function()", "window.exportDashboardToPDF = async function()")
content = content.replace("window.exportDashboardToPDF\r\n      window.exportDashboardToPDF = async function()", "window.exportDashboardToPDF = async function()")

with open(path, 'wb') as f:
    f.write(content.encode('utf-8'))
print("Done.")
