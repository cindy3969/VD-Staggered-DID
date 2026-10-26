$ErrorActionPreference = 'Stop'
$dir = 'C:\Users\user\Documents\VD\outputs\patentsview_2024_full_cohort\source\citation_segments'
$url = 'https://zenodo.org/records/15783125/files/g_us_patent_citation.tsv.zip?download=1'
$total = [int64]2156504596
$segment = [int64](64MB)
New-Item -ItemType Directory -Force -Path $dir | Out-Null

$specs = @()
for ($start = [int64]0; $start -lt $total; $start += $segment) {
    $end = [Math]::Min($total - 1, $start + $segment - 1)
    $index = [int]($start / $segment)
    $path = Join-Path $dir ('seg{0:D3}' -f $index)
    $specs += [pscustomobject]@{ Start=$start; End=$end; Path=$path; Size=($end-$start+1) }
}

for ($round = 1; $round -le 10; $round++) {
    $pending = @($specs | Where-Object { -not (Test-Path $_.Path) -or (Get-Item $_.Path).Length -ne $_.Size })
    if ($pending.Count -eq 0) { break }
    Write-Output "round $round pending $($pending.Count)"
    for ($offset = 0; $offset -lt $pending.Count; $offset += 8) {
        $batch = @($pending | Select-Object -Skip $offset -First 8)
        $jobs = @()
        foreach ($item in $batch) {
            $jobs += Start-Process -FilePath 'curl.exe' -ArgumentList @(
                '-L','--fail','--silent','--show-error','--connect-timeout','30','--max-time','240',
                '-r',("{0}-{1}" -f $item.Start,$item.End),'-o',$item.Path,$url
            ) -WindowStyle Hidden -PassThru
        }
        $jobs | Wait-Process
    }
}

$bad = @($specs | Where-Object { -not (Test-Path $_.Path) -or (Get-Item $_.Path).Length -ne $_.Size })
if ($bad.Count) { throw "incomplete citation segments: $($bad.Count)" }
Write-Output 'citation segments downloaded'
