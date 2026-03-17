$ErrorActionPreference = "Stop"

$marketRoot = Split-Path -Parent $MyInvocation.MyCommand.Path
$agriProdRoot = Join-Path (Split-Path -Parent $marketRoot) "AgricultureProd"
$outputsDir = Join-Path $marketRoot "outputs"
if (-not (Test-Path -Path $outputsDir -PathType Container)) {
    New-Item -ItemType Directory -Path $outputsDir | Out-Null
}

$duckdbPath = Join-Path $agriProdRoot "tools\\duckdb\\duckdb.exe"
$dbPath = Join-Path $agriProdRoot "agri_validation.duckdb"
if (-not (Test-Path -Path $duckdbPath -PathType Leaf)) {
    throw "DuckDB CLI not found at: $duckdbPath"
}
if (-not (Test-Path -Path $dbPath -PathType Leaf)) {
    throw "DuckDB DB not found at: $dbPath"
}

function Invoke-Sql {
    param([string]$SqlFile)
    $fullSql = Join-Path $agriProdRoot $SqlFile
    if (-not (Test-Path -Path $fullSql -PathType Leaf)) {
        throw "SQL script not found: $fullSql"
    }
    $duckdbSqlPath = $fullSql -replace "\\", "/"
    Write-Host "Running .read $duckdbSqlPath"
    & $duckdbPath $dbPath ".read $duckdbSqlPath"
    if ($LASTEXITCODE -ne 0) {
        throw "DuckDB failed on $SqlFile"
    }
}

Invoke-Sql "sql/60_load_market.sql"
Invoke-Sql "sql/61_market_monthly.sql"
Invoke-Sql "sql/62_weather_monthly_features.sql"
Invoke-Sql "sql/63_calendar_month_to_season.sql"
Invoke-Sql "sql/64_model2_base_dataset.sql"
Invoke-Sql "sql/65_yield_feature_table.sql"
Invoke-Sql "sql/66_model2_adjust_dataset.sql"

Push-Location $marketRoot
try {
    Write-Host "Training Model 2 base..."
    python .\\train_model2_base.py
    if ($LASTEXITCODE -ne 0) { throw "train_model2_base.py failed" }
    Write-Host "Training Model 2 adjust..."
    python .\\train_model2_adjust.py
    if ($LASTEXITCODE -ne 0) { throw "train_model2_adjust.py failed" }
}
finally {
    Pop-Location
}

$required = @(
    "m2_base_metrics.csv",
    "m2_base_predictions_2024.csv",
    "m2_base_model.pkl",
    "m2_base_oof.csv",
    "m2_adjust_metrics.csv",
    "m2_adjust_model.pkl"
)
foreach ($f in $required) {
    $p = Join-Path $outputsDir $f
    if (-not (Test-Path -Path $p -PathType Leaf)) {
        throw "Missing expected artifact: $p"
    }
}

Write-Host ""
Write-Host "Model 2 pipeline completed."
Write-Host "Artifacts written to: $outputsDir"
