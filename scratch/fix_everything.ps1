$path = "static\index.html"
$content = [System.IO.File]::ReadAllText($path, [System.Text.Encoding]::UTF8)

# 1. Fix the syntax error in triggerAIAnalysis / exportDashboardToPDF
$wrongLink = 'content\.innerHTML\s+=\s+window\.exportDashboardToPDF\s+=\s+async\s+function\(\)\s+\{'
$correctLink = 'content.innerHTML = "<p>Error al conectar con la IA.</p>"; } `r`n`r`n      window.exportDashboardToPDF = async function() {'
$content = [System.Text.RegularExpressions.Regex]::Replace($content, $wrongLink, $correctLink)

# 2. Fix mangled UTF-8 characters in the entire file
# We'll replace the most common ones found in the earlier view_file output
$replacements = @{
    'â ³' = '⏳'
    'Â·' = '·'
    'Ã¡' = 'á'
    'Ã©' = 'é'
    'Ã­' = 'í'
    'Ã³' = 'ó'
    'Ãº' = 'ú'
    'Ã±' = 'ñ'
    'Ã?' = 'Á'
    'Ã‰' = 'É'
    'Ã?' = 'Í'
    'Ã“' = 'Ó'
    'Ãš' = 'Ú'
    'Ã‘' = 'Ñ'
    'â€”' = '-'
    'PÃ¡gina' = 'Pagina'
    'PÃ¡g.' = 'Pag.'
    'AnÃ¡lisis' = 'Analisis'
    'atenciÃ³n' = 'atencion'
    'Ã³ptima' = 'optima'
    'perÃ­odo' = 'periodo'
    'dÃ­a' = 'dia'
    'IntervenciÃ³n' = 'Intervencion'
}

foreach ($key in $replacements.Keys) {
    $content = $content.Replace($key, $replacements[$key])
}

# 3. Specifically fix the PDF function strings to be ASCII safe since jsPDF fonts might not support accents
$content = $content.Replace('Reporte Operativo - Duma AI', 'Reporte Operativo - Duma AI')
$content = $content.Replace('Monitoreo de Corriente (Amperes)', 'Monitoreo de Corriente (Amperes)')
$content = $content.Replace('Evolucion temporal de las fases del motor', 'Evolucion temporal de las fases del motor')
$content = $content.Replace('Disponibilidad Diaria (%)', 'Disponibilidad Diaria (%)')
$content = $content.Replace('Porcentaje de uptime por dia en el periodo seleccionado', 'Porcentaje de uptime por dia en el periodo seleccionado')
$content = $content.Replace('Analisis y Recomendaciones - DUMA IA', 'Analisis y Recomendaciones - DUMA IA')

# 4. Remove duplicate button just in case (though it seemed gone)
$btnRegex = '(?s)<div style="display: flex; gap: 10px;">\s*<button class="btn-pdf".*?Descargar PDF.*?</button>\s*</div>'
$content = [System.Text.RegularExpressions.Regex]::Replace($content, $btnRegex, '<div style="display: flex; gap: 10px;"></div>')

[System.IO.File]::WriteAllText($path, $content, [System.Text.Encoding]::UTF8)
Write-Host "Fixed everything."
