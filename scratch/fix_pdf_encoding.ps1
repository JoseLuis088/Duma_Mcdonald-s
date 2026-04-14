$file = "static\index.html"
[System.Text.Encoding]::RegisterProvider([System.Text.CodePagesEncodingProvider]::Instance)
$bytes   = [System.IO.File]::ReadAllBytes((Resolve-Path $file).Path)
$content = [System.Text.Encoding]::UTF8.GetString($bytes)

# ──────────────────────────────────────────────────────────────
# 1) Remove the duplicate "Descargar PDF" button from AI panel
# ──────────────────────────────────────────────────────────────
# Pattern between <div style="display: flex; gap: 10px;"> ... </div> in AI header
$btnPattern = '(?s)(<div style="display: flex; gap: 10px;">)\s*<button class="btn-pdf" onclick="exportDashboardToPDF\(\)">\s*<span[^>]*>.*?</span>\s*Descargar PDF\s*</button>\s*(</div>)'
$content = [System.Text.RegularExpressions.Regex]::Replace($content, $btnPattern, '$1$2')

Write-Host "Step 1 done (btn removal)"

# ──────────────────────────────────────────────────────────────
# 2) Fix encoding: replace accented/special chars in static
#    JS string literals inside exportDashboardToPDF.
#    We target the known bad strings and replace them with
#    their ASCII equivalents so jsPDF renders them cleanly.
# ──────────────────────────────────────────────────────────────

# Title strings
$content = $content -replace 'Reporte Operativo\s+[—\u2014]\s+Duma AI', 'Reporte Operativo - Duma AI'
$content = $content -replace 'Evoluci[óoÃ³]n temporal de las fases del motor', 'Evolucion temporal de las fases del motor'
$content = $content -replace 'Disponibilidad Diaria \(%\)', 'Disponibilidad Diaria (%)'
$content = $content -replace 'Porcentaje de uptime por d[íiÃ­]a en el per[íiÃ­]odo seleccionado', 'Porcentaje de uptime por dia en el periodo seleccionado'
$content = $content -replace 'An[áaÃ¡]lisis y Recomendaciones\s+[—\u2014]\s+DUMA IA', 'Analisis y Recomendaciones - DUMA IA'
$content = $content -replace "Duma AI  [·\u00B7\u22C5]  Reporte Confidencial  [·\u00B7\u22C5]", 'Duma AI  |  Reporte Confidencial  |'
$content = $content -replace "P[áaÃ¡]gina", 'Pagina'
$content = $content -replace "P[áaÃ¡]g\. '", "Pag. '"

Write-Host "Step 2 done (encoding fix)"

# ──────────────────────────────────────────────────────────────
# 3) Remove any em-dash or unusual dash characters in JS strings
# ──────────────────────────────────────────────────────────────
# Replace em-dash (U+2014) and en-dash (U+2013) in the JS section
$emDash  = [char]0x2014
$enDash  = [char]0x2013
$content = $content -replace "$emDash", ' - '
$content = $content -replace "$enDash", ' - '

Write-Host "Step 3 done (dash fix)"

# Save
[System.IO.File]::WriteAllBytes((Resolve-Path $file).Path, [System.Text.Encoding]::UTF8.GetBytes($content))
Write-Host "SUCCESS: File saved."
