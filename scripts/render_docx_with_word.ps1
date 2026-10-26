$ErrorActionPreference = 'Stop'
$docx = 'C:\Users\user\Documents\VD\outputs\table2_forward_citations_application_level\Table_2_forward_citations_replication.docx'
$pdf = 'C:\Users\user\Documents\VD\.artifact_work\table2_render\Table_2_forward_citations_replication.pdf'
New-Item -ItemType Directory -Force -Path (Split-Path -Parent $pdf) | Out-Null
$word = New-Object -ComObject Word.Application
$word.Visible = $false
try {
    $doc = $word.Documents.Open($docx, $false, $true)
    $doc.ExportAsFixedFormat($pdf, 17)
    $doc.Close($false)
} finally {
    $word.Quit()
}
Write-Output $pdf
