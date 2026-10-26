$ErrorActionPreference = 'Stop'
$dir = 'C:\Users\user\Documents\VD\outputs\patentsview_2024_full_cohort\source'
$url = 'https://zenodo.org/records/15783125/files/g_us_patent_citation.tsv.zip?download=1'
$ranges = @(
    '0-539126148',
    '539126149-1078252297',
    '1078252298-1617378446',
    '1617378447-2156504595'
)
$jobs = @()
for ($i = 0; $i -lt $ranges.Count; $i++) {
    $out = Join-Path $dir ("g_us_patent_citation.part{0}" -f $i)
    $jobs += Start-Process -FilePath 'curl.exe' -ArgumentList @('-L','--fail','--retry','20','--retry-all-errors','--retry-delay','15','-r',$ranges[$i],'-o',$out,$url) -WindowStyle Hidden -PassThru
}
$jobs | Wait-Process
foreach ($job in $jobs) {
    if ($job.ExitCode -ne 0) { throw "citation part download failed: $($job.Id) code $($job.ExitCode)" }
}
Write-Output 'citation parts downloaded'
