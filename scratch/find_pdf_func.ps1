
$file = "static\index.html"
$content = Get-Content $file -Raw -Encoding UTF8

# Find start/end markers
$startMarker = "      window.exportDashboardToPDF = async function() {"
$endMarker = "      };"

$startIdx = $content.IndexOf($startMarker)
# Find the matching closing brace after startIdx
$searchFrom = $startIdx + $startMarker.Length
$endIdx = $content.IndexOf($endMarker, $searchFrom)

if ($startIdx -lt 0 -or $endIdx -lt 0) {
    Write-Host "ERROR: Could not find markers. Start=$startIdx, End=$endIdx"
    exit 1
}

Write-Host "Found exportDashboardToPDF at char $startIdx to $($endIdx + $endMarker.Length)"
Write-Host "Snippet: $($content.Substring($startIdx, 60))..."
