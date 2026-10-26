param([string]$InputDocx,[string]$OutputPdf)
$ErrorActionPreference='Stop'
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $OutputPdf) | Out-Null
$tableWord=New-Object -ComObject Word.Application
$tableWord.Visible=$false
$tableWord.DisplayAlerts=0
try {
    $tableDoc=$tableWord.Documents.Open($InputDocx,$false,$true)
    $tableDoc.ExportAsFixedFormat($OutputPdf,17)
    $tableDoc.Close($false)
} finally {
    $tableWord.Quit()
}
Write-Output $OutputPdf
