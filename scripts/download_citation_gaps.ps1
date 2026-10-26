$ErrorActionPreference = 'Stop'
$dir = 'C:\Users\user\Documents\VD\outputs\patentsview_2024_full_cohort\source'
$url = 'https://zenodo.org/records/15058362/files/g_us_patent_citation.tsv.zip?download=1'
$items = @(
    @{ Name='gap1'; Range='788400517-1078252297' },
    @{ Name='gap2'; Range='1351713546-1617378446' },
    @{ Name='gap3'; Range='1929018511-2156504595' }
)
$jobs = @()
foreach ($item in $items) {
    $path = Join-Path $dir ("g_us_patent_citation.$($item.Name)")
    $jobs += Start-Process -FilePath 'curl.exe' -ArgumentList @(
        '-L','--fail','--retry','30','--retry-all-errors','--retry-delay','10',
        '-r',$item.Range,'-o',$path,$url
    ) -WindowStyle Hidden -PassThru
}
$jobs | Wait-Process
Write-Output 'gap downloads finished'
