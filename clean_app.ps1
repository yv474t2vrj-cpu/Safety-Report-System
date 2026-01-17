$file = "app.py"
$content = Get-Content $file -Raw

# Replace common problematic characters
$replacements = @{
    'â€¢' = '•'
    'âœ“' = '[OK]'
    'âš€' = ''
    'ðŸš€' = ''
    'ðŸ"‹' = ''
    'ðŸ"' = ''
    'ðŸŒ' = ''
}

foreach ($key in $replacements.Keys) {
    $content = $content -replace $key, $replacements[$key]
}

# Ensure UTF-8 encoding
$content | Set-Content $file -Encoding UTF8

Write-Host "File cleaned and saved with UTF-8 encoding" -ForegroundColor Green