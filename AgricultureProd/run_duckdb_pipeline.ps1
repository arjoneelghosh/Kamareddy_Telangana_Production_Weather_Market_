$ErrorActionPreference = "Stop"

$repoRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $repoRoot

$outputsDir = Join-Path $repoRoot "outputs"
if (-not (Test-Path -Path $outputsDir -PathType Container)) {
    New-Item -ItemType Directory -Path $outputsDir | Out-Null
}
Remove-Item -Path (Join-Path $outputsDir "*.csv") -ErrorAction SilentlyContinue

$duckdbPath = Join-Path $repoRoot "tools\duckdb\duckdb.exe"
$dbPath = Join-Path $repoRoot "agri_validation.duckdb"

if (-not (Test-Path -Path $duckdbPath -PathType Leaf)) {
    throw "DuckDB CLI not found at: $duckdbPath"
}

if (-not (Test-Path -Path $dbPath -PathType Leaf)) {
    throw "Database file not found at: $dbPath"
}

function Invoke-DuckDbRead {
    param(
        [Parameter(Mandatory = $true)]
        [string]$SqlScript
    )

    Write-Host "Running .read $SqlScript"
    & $duckdbPath $dbPath ".read $SqlScript"
    if ($LASTEXITCODE -ne 0) {
        throw "DuckDB failed while running script: $SqlScript"
    }
}

Invoke-DuckDbRead "sql/00_load_telangana.sql"
Invoke-DuckDbRead "sql/10_views_telangana.sql"
Invoke-DuckDbRead "sql/20_coverage_and_stability.sql"
Invoke-DuckDbRead "sql/30_outlier_detection.sql"
Invoke-DuckDbRead "sql/40_season_alignment.sql"
Invoke-DuckDbRead "sql/05_load_weather_v2.sql"
Invoke-DuckDbRead "sql/15_weather_features.sql"
Invoke-DuckDbRead "sql/17_weather_seasonal.sql"
Invoke-DuckDbRead "sql/18_district_match_diagnostics.sql"
Invoke-DuckDbRead "sql/50_model1_dataset.sql"

Write-Host ""
Write-Host "DuckDB Telangana pipeline completed successfully."
Write-Host "Output CSVs written to: $outputsDir"
