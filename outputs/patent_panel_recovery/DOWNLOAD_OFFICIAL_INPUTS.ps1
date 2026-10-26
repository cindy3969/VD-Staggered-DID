param(
    [switch]$IncludeForwardCitations
)

$ErrorActionPreference = 'Stop'
$sourceDir = 'C:\Users\user\Documents\VD\outputs\patentsview_2024_full_cohort\source'
New-Item -ItemType Directory -Force -Path $sourceDir | Out-Null
$base = 'https://zenodo.org/records/15783125/files'

# Quantity and application-linkage inputs. curl -C - resumes interrupted files.
$files = @(
    'g_application.tsv.zip',
    'g_patent.tsv.zip',
    'g_assignee_disambiguated.tsv.zip',
    'g_assignee_not_disambiguated.tsv.zip',
    'pg_published_application.tsv.zip',
    'pg_assignee_disambiguated.tsv.zip',
    'pg_assignee_not_disambiguated.tsv.zip',
    'pg_granted_pgpubs_crosswalk.tsv.zip'
)

if ($IncludeForwardCitations) {
    $files += 'g_us_patent_citation.tsv.zip'
    $files += 'g_cpc_current.tsv.zip'
}

foreach ($name in $files) {
    $out = Join-Path $sourceDir $name
    Write-Host "Downloading or resuming $name"
    & curl.exe -L -C - --retry 20 --retry-all-errors --retry-delay 15 `
        -o $out "$base/$name?download=1"
    if ($LASTEXITCODE -ne 0) {
        throw "Download failed for $name with exit code $LASTEXITCODE"
    }
}

Write-Host 'Official PatentsView inputs are ready.'
