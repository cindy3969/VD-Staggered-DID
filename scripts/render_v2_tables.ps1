param([string]$InputDoc, [string]$OutputPdf)
$ErrorActionPreference = 'Stop'
$wordRender = New-Object -ComObject Word.Application
$wordRender.Visible = $false
$wordRender.DisplayAlerts = 0
try {
    $renderDocument = $wordRender.Documents.Open($InputDoc, $false, $true)
    $renderDocument.ExportAsFixedFormat($OutputPdf, 17)
    $renderDocument.Close($false)
} finally {
    $wordRender.Quit()
}
