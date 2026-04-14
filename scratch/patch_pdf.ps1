
$file = "static\index.html"
$content = Get-Content $file -Raw -Encoding UTF8

$startMarker = "      window.exportDashboardToPDF = async function() {"
$endMarker = "      };"

$startIdx = $content.IndexOf($startMarker)
$searchFrom = $startIdx + $startMarker.Length
$endIdx = $content.IndexOf($endMarker, $searchFrom)
$fullEnd = $endIdx + $endMarker.Length

$newFunc = @'
      window.exportDashboardToPDF = async function() {
        const btn = document.querySelector('.btn-pdf');
        if (!btn) return;
        const orig = btn.innerHTML;
        btn.innerHTML = '⏳ Generando...'; btn.disabled = true;
        try {
          const ciudad   = el('filterCiudad')   ? el('filterCiudad').value   : '';
          const sucursal = el('filterSucursal') ? el('filterSucursal').value : 'Reporte';
          const jsPDFCls = (window.jspdf && window.jspdf.jsPDF) ? window.jspdf.jsPDF : window.jsPDF;
          if (!jsPDFCls) throw new Error('jsPDF no está disponible');

          const PAGE_W = 8.5, PAGE_H = 11, M = 0.55;
          const BRAND  = [0, 128, 102];
          const DARK   = [20, 30, 40];
          const GRAY   = [90, 100, 110];
          const LIGHT  = [240, 244, 248];

          const doc = new jsPDFCls({ orientation: 'p', unit: 'in', format: 'letter' });
          const now  = new Date();
          const dateStr = now.toLocaleDateString('es-MX', {year:'numeric',month:'long',day:'numeric'});

          function addFooter(pageLabel) {
            var H = PAGE_H - 0.38;
            doc.setDrawColor(0,128,102).setLineWidth(0.01).line(M, H - 0.05, PAGE_W - M, H - 0.05);
            doc.setFont('helvetica','normal').setFontSize(8).setTextColor(90,100,110);
            doc.text('Duma AI  ·  Reporte Confidencial  ·  ' + dateStr, M, H + 0.06);
            doc.text(pageLabel, PAGE_W - M, H + 0.06, {align:'right'});
          }

          // PAGINA 1 — Corriente
          doc.setFillColor(0,128,102).rect(0, 0, PAGE_W, 0.9, 'F');
          doc.setFont('helvetica','bold').setFontSize(20).setTextColor(255,255,255)
             .text('Reporte Operativo  —  Duma AI', M, 0.58);
          doc.setFont('helvetica','normal').setFontSize(10).setTextColor(200,235,228)
             .text('Sucursal: ' + sucursal + (ciudad ? '   |   ' + ciudad : ''), M, 0.78);

          var y = 1.02;
          doc.setFont('helvetica','bold').setFontSize(12).setTextColor(20,30,40)
             .text('Monitoreo de Corriente (Amperes)', M, y);
          doc.setFont('helvetica','normal').setFontSize(9).setTextColor(90,100,110)
             .text('Evolución temporal de las fases del motor', M, y + 0.18);
          y += 0.38;

          if (el('sensePlot')) {
            await Plotly.relayout('sensePlot', {
              'font.color':'#1e293b','xaxis.tickfont.color':'#1e293b',
              'yaxis.tickfont.color':'#1e293b','xaxis.gridcolor':'rgba(0,0,0,0.08)',
              'yaxis.gridcolor':'rgba(0,0,0,0.08)'
            });
            var img1 = await Plotly.toImage('sensePlot', {format:'png', width:1400, height:650, scale:2});
            doc.addImage(img1, 'PNG', M, y, 7.4, 3.55);
          }
          addFooter('Página 1');

          // PAGINA 2 — Disponibilidad
          if (el('availPlot')) {
            doc.addPage();
            doc.setFillColor(0,128,102).rect(0, 0, PAGE_W, 0.46, 'F');
            doc.setFont('helvetica','bold').setFontSize(13).setTextColor(255,255,255)
               .text('Reporte Operativo  —  Duma AI', M, 0.3);

            y = 0.7;
            doc.setFont('helvetica','bold').setFontSize(12).setTextColor(20,30,40)
               .text('Disponibilidad Diaria (%)', M, y);
            doc.setFont('helvetica','normal').setFontSize(9).setTextColor(90,100,110)
               .text('Porcentaje de uptime por día en el período seleccionado', M, y + 0.18);
            y += 0.42;

            await Plotly.relayout('availPlot', {
              'font.color':'#1e293b','xaxis.tickfont.color':'#1e293b',
              'yaxis.tickfont.color':'#1e293b','xaxis.gridcolor':'rgba(0,0,0,0.08)',
              'yaxis.gridcolor':'rgba(0,0,0,0.08)'
            });
            var img2 = await Plotly.toImage('availPlot', {format:'png', width:1400, height:600, scale:2});
            doc.addImage(img2, 'PNG', M, y, 7.4, 3.4);
            y += 3.55;

            doc.setFontSize(8).setTextColor(90,100,110);
            var legend = [
              {r:74,g:222,b:128, label:'>= 90%  Disponibilidad óptima'},
              {r:250,g:204,b:21, label:'70-89%  Atención recomendada'},
              {r:248,g:113,b:113, label:'< 70%  Intervención urgente'}
            ];
            var lx = M;
            legend.forEach(function(l) {
              doc.setFillColor(l.r,l.g,l.b).roundedRect(lx, y, 0.12, 0.12, 0.02, 0.02, 'F');
              doc.text(l.label, lx + 0.17, y + 0.1);
              lx += 2.48;
            });
            addFooter('Página 2');
          }

          // PAGINA(S) 3+ — Análisis IA
          var aiText = el('aiContent') ? el('aiContent').innerText.trim() : '';
          if (aiText) {
            doc.addPage();
            doc.setFillColor(0,128,102).rect(0, 0, PAGE_W, 0.46, 'F');
            doc.setFont('helvetica','bold').setFontSize(13).setTextColor(255,255,255)
               .text('Reporte Operativo  —  Duma AI', M, 0.3);

            y = 0.7;
            // Caja titular IA
            doc.setFillColor(0,128,102).roundedRect(M, y, 7.4, 0.38, 0.06, 0.06, 'F');
            doc.setFont('helvetica','bold').setFontSize(13).setTextColor(255,255,255)
               .text('Análisis y Recomendaciones — DUMA IA', M + 0.18, y + 0.255);
            y += 0.56;

            var rawLines = aiText.split('\n');
            var CONTENT_W = 7.2, LINE_H = 0.165;

            function checkPageBreak(neededH) {
              if (y + neededH > PAGE_H - 0.65) {
                addFooter('Pág. ' + doc.internal.getNumberOfPages());
                doc.addPage();
                doc.setFillColor(0,128,102).rect(0, 0, PAGE_W, 0.46, 'F');
                doc.setFont('helvetica','bold').setFontSize(13).setTextColor(255,255,255)
                   .text('Reporte Operativo  —  Duma AI', M, 0.3);
                y = 0.7;
              }
            }

            rawLines.forEach(function(rawLine) {
              var line = rawLine.trim();
              if (!line) { y += LINE_H * 0.55; return; }

              var isHeader = /^\d+[\.\)]\s/.test(line) || /^#{1,3}\s/.test(line);
              var isBullet = /^[•\-\*]\s/.test(line);

              if (isHeader) {
                checkPageBreak(0.52);
                var cleanH = line.replace(/^#{1,3}\s/, '');
                doc.setFillColor(240,244,248).roundedRect(M, y - 0.01, CONTENT_W, 0.32, 0.04, 0.04, 'F');
                doc.setDrawColor(0,128,102).setLineWidth(0.025).line(M + 0.01, y - 0.01, M + 0.01, y + 0.31);
                doc.setFont('helvetica','bold').setFontSize(10.5).setTextColor(0,128,102)
                   .text(cleanH, M + 0.14, y + 0.21);
                y += 0.42;
              } else if (isBullet) {
                var cleanB = line.replace(/^[•\-\*]\s*/, '');
                var wrapped = doc.setFont('helvetica','normal').setFontSize(9.5).splitTextToSize(cleanB, CONTENT_W - 0.28);
                checkPageBreak(wrapped.length * LINE_H + 0.06);
                doc.setFillColor(0,128,102).circle(M + 0.07, y + 0.065, 0.038, 'F');
                doc.setTextColor(20,30,40).text(wrapped, M + 0.2, y + 0.1);
                y += wrapped.length * LINE_H + 0.05;
              } else {
                var wrapped = doc.setFont('helvetica','normal').setFontSize(9.5).setTextColor(20,30,40).splitTextToSize(line, CONTENT_W);
                checkPageBreak(wrapped.length * LINE_H + 0.04);
                doc.text(wrapped, M, y + 0.1);
                y += wrapped.length * LINE_H + 0.04;
              }
            });
            addFooter('Pág. ' + doc.internal.getNumberOfPages());
          }

          updatePlotlyTheme(document.documentElement.getAttribute('data-theme'));
          doc.save('Reporte_Duma_' + sucursal + '.pdf');

        } catch(e) {
          alert('Error generando PDF: ' + e.message);
          console.error(e);
        } finally {
          btn.innerHTML = orig; btn.disabled = false;
        }
      };
'@

$before = $content.Substring(0, $startIdx)
$after  = $content.Substring($fullEnd)
$newContent = $before + $newFunc + $after

[System.IO.File]::WriteAllText((Resolve-Path $file).Path, $newContent, [System.Text.Encoding]::UTF8)
Write-Host "SUCCESS: exportDashboardToPDF rewritten."
