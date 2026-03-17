# AgriFore Repository Audit

## Overview

After a thorough scan of every directory and file in the repo, here are the two lists you asked for.

---

## List 1: Useless / Unused Items

These are files and folders that are **not referenced by any running component** (frontend, backend, models) and serve no purpose in the current project state.

| # | Path | Type | Why It's Useless |
|---|------|------|-----------------|
| 1 | `IEEE/` | Empty dir | Completely empty — no files inside |
| 2 | `aaaFinalModels/model3/` | Empty dir | Placeholder with zero content |
| 3 | `api/__pycache__/` | Cache dir | Auto-generated Python bytecode; safe to delete |
| 4 | `AgricultureProd/outputs/Kamareddy_Selected/.venv/` | venv dir | A leftover virtual environment inside an outputs subfolder |
| 5 | `AgricultureProd/outputs/xgb_try_1/` | Experiment dir | Old XGBoost tuning run — not used by any code |
| 6 | `AgricultureProd/outputs/xgb_try_2/` | Experiment dir | Old XGBoost tuning run — not used by any code |
| 7 | `AgricultureProd/outputs/xgb_try_3/` | Experiment dir | Old XGBoost tuning run — not used by any code |
| 8 | `AgricultureProd/outputs/xgb_try_4/` | Experiment dir | Old XGBoost tuning run — not used by any code |
| 9 | `AgricultureProd/outputs/xgb_try_5/` | Experiment dir | Old XGBoost tuning run — not used by any code |
| 10 | `AgricultureProd/outputs/xgb_try_6/` | Experiment dir | Old XGBoost tuning run — not used by any code |
| 11 | `AgricultureProd/outputs/xgb_try_7/` | Experiment dir | Old XGBoost tuning run — not used by any code |
| 12 | `AgricultureProd/outputs/xgb_try_8/` | Experiment dir | Old XGBoost tuning run — not used by any code |
| 13 | `AgricultureProd/outputs/xgb_try_baseline/` | Experiment dir | Old XGBoost baseline run — not used by any code |
| 14 | `AgricultureProd/outputs/xgb_try_debug/` | Experiment dir | Old XGBoost debug run — not used by any code |
| 15 | `AgricultureProd/outputs_xgb_50%/` | Experiment dir | Duplicate set of model1 outputs from XGBoost 50% training variant; no code references this folder |
| 16 | `AgricultureProd/output_production_validation/` | Intermediate output | Contains duplicate diagnostic CSVs already present in `outputs/` |
| 17 | `AgricultureProd/output_rainfall_prod_/` | Intermediate output | Another duplicate set of the same diagnostic CSVs |
| 18 | `AgricultureProd/outputs/Screenshot 2026-03-03 011925.png` | Screenshot | Random screenshot sitting in outputs (382 KB) |
| 19 | `AgricultureProd/outputs/Kamareddy_Selected/Screenshot 2026-03-03 011925.png` | Screenshot | Same screenshot duplicated inside Kamareddy folder |
| 20 | `AgriMarket/outputs/Screenshot 2026-03-03 011925.png` | Screenshot | Same screenshot duplicated again in market outputs |
| 21 | `AgriMarket/outputs/terminal_screenshot.png` | Screenshot | Terminal screenshot — no code references it |
| 22 | `AgricultureProd/phase1_year_crop_district_counts.csv` | Stale CSV | Output from `duckdb_phase1_conditionB.py` — a one-off exploration, not used anywhere |
| 23 | `AgricultureProd/phase1_year_total_districts.csv` | Stale CSV | Same — one-off output, zero references |
| 24 | `AgricultureProd/duckdb_phase1_conditionB.py` | One-off script | Ad-hoc exploration script; not part of any pipeline |
| 25 | `AgricultureProd/duckdb_validate.py` | One-off script | Initial DB creation helper; the pipeline uses `run_duckdb_pipeline.ps1` + SQL scripts instead |
| 26 | `AgricultureProd/validate_weather_rebuild.py` | One-off script | One-off weather validation script; no pipeline or code calls it |
| 27 | `AgricultureProd/tools/duckdb.zip` | Archive | Zipped DuckDB binary (11 MB); the extracted `duckdb.exe` already exists at `tools/duckdb/duckdb.exe` |
| 28 | `AgricultureProd/outputs/xgb_tune_config.json` | Config file | Tuning config for old XGBoost experiments; no current script reads it |
| 29 | `frontend/.git/` | Nested git | The frontend has its own `.git` — likely leftover from cloning a template |
| 30 | `frontend/.next/` | Build cache | Next.js build output; regenerated on `npm run dev` |
| 31 | `frontend/tsconfig.tsbuildinfo` | Build cache | TypeScript incremental build file (152 KB) |
| 32 | `db_tables.txt` | Empty/stale file | Listed at 0 bytes — empty file |

> [!TIP]
> **Quick cleanup command** (PowerShell):
> ```powershell
> # Remove empty dirs
> Remove-Item -Recurse -Force "IEEE", "aaaFinalModels\model3"
> # Remove experiment dirs
> Remove-Item -Recurse -Force "AgricultureProd\outputs\xgb_try_*"
> # Remove duplicate output dirs
> Remove-Item -Recurse -Force "AgricultureProd\output_production_validation", "AgricultureProd\output_rainfall_prod_", "AgricultureProd\outputs_xgb_50%"
> # Remove pycache and build caches
> Remove-Item -Recurse -Force "api\__pycache__", "frontend\.next", "frontend\tsconfig.tsbuildinfo"
> # Remove stale screenshots
> Get-ChildItem -Recurse -Filter "Screenshot*" | Remove-Item
> # Remove stale zip
> Remove-Item "AgricultureProd\tools\duckdb.zip"
> ```

---

## List 2: Insight / Documentation Files (Not Needed for Running)

These files provide **analysis, documentation, logs, or research outputs** that are valuable for understanding the project but are **NOT required** by the frontend, backend, or model training/inference pipelines.

| # | Path | Size | Category | What It Contains |
|---|------|------|----------|-----------------|
| 1 | `AgriFore_IEEE_Paper.md` | 40 KB | 📄 Paper | Full IEEE paper draft in markdown |
| 2 | `AgriFore_IEEE_Paper_repo_verified.md` | 45 KB | 📄 Paper | Repo-verified version of the same paper |
| 3 | `arjosankarfinalieee.docx` | 695 KB | 📄 Paper | IEEE paper in Word format |
| 4 | `arjosankarfinalieee.pdf` | 481 KB | 📄 Paper | IEEE paper in PDF format |
| 5 | `march2026_prediction_vs_reality.md` | 8 KB | 📊 Analysis | Prediction vs actual comparison for March 2026 |
| 6 | `march2026_forecast.json` | 2 KB | 📊 Analysis | Raw JSON output from March 2026 forecast script |
| 7 | `forecast_raw_outputs.json` | 1 KB | 📊 Analysis | Earlier forecast raw outputs |
| 8 | `sample_forecast_output.md` | 5 KB | 📊 Analysis | Formatted sample forecast results |
| 9 | `repo_paper_change_log.md` | 7 KB | 📝 Docs | Changelog of paper vs repo alignment |
| 10 | `repo_paper_verification_summary.md` | 9 KB | 📝 Docs | Summary of how the repo matches the paper claims |
| 11 | `runtime_run_report.md` | 7 KB | 📝 Logs | Report from a past runtime test session |
| 12 | `runtime_commands_log.txt` | 4 KB | 📝 Logs | Log of commands run during backend testing |
| 13 | `runtime_errors_log.txt` | 2 KB | 📝 Logs | Error log from a past runtime session |
| 14 | `api_test_results.txt` | 5 KB | 📝 Logs | Log of API endpoint test results |
| 15 | `db_inspect.txt` | 17 KB | 📝 Logs | DuckDB schema inspection dump |
| 16 | `db_tables.txt` | 0 KB | 📝 Logs | Empty — likely a failed/stale version of db_inspect |
| 17 | `run_march2026.py` | 2 KB | 🔧 Script | One-off forecast script that calls the API — useful for demo but not part of the app |
| 18 | `AgricultureProd/README_PIPELINE.md` | 3 KB | 📝 Docs | Pipeline documentation for the DuckDB data pipeline |
| 19 | `AgriMarket/outputs/correlationmatrix.png` | 441 KB | 📊 Analysis | Correlation matrix visualization |
| 20 | `AgriMarket/outputs/direct comparison.png` | 179 KB | 📊 Analysis | Model comparison chart |
| 21 | `AgriMarket/outputs/m2_forecast.csv` | <1 KB | 📊 Analysis | Small forecast output CSV |
| 22 | `AgriMarket/outputs/m2_march_Forecastings.csv` | 225 KB | 📊 Analysis | March forecasting outputs |
| 23 | `aaaFinalModels/model2/deeplearning_validator/` | ~55 MB total | 📊 Analysis | Deep learning model validation artifacts (LSTM autoencoder + evaluation scripts) — not used by the running system |
| 24 | `AgricultureProd/outputs/Kamareddy_Selected/` | ~2 MB | 📊 Analysis | Kamareddy-specific model 1 forecasting demo with its own venv and prediction script |

> [!NOTE]
> **Impact summary**: 
> - Deleting **List 1** items would free up roughly **~60+ MB** of disk space (mostly from the `.venv`, XGBoost experiments, `duckdb.zip`, and duplicate outputs).
> - **List 2** items are documentation/analysis artifacts. They're safe to archive separately but shouldn't be deleted if you want to preserve research context.

---

## What IS Required for the System to Run

For reference, here's what the running system actually depends on:

### Backend (`api/server.py`)
- `AgricultureProd/agri_validation.duckdb` — the main database
- `aaaFinalModels/model2/m2_base_model.pkl` — the M2 XGBoost pipeline
- `aaaFinalModels/model2/m2_base_predictions_2024.csv` — fallback predictions
- `api/__init__.py` + `api/server.py` + `api/requirements.txt`

### Frontend (`frontend/`)
- All files under `frontend/app/`, `frontend/components/`, `frontend/services/`, `frontend/types/`, `frontend/utils/`
- Config files: `package.json`, `next.config.js`, `tailwind.config.ts`, `tsconfig.json`, `postcss.config.mjs`, `.eslintrc.json`
- `frontend/node_modules/` (installed dependencies)

### Model Training (re-training only, not for running)
- `AgricultureProd/sql/` — all 18 SQL scripts
- `AgricultureProd/run_duckdb_pipeline.ps1`
- `AgricultureProd/tools/train_model1_weather_to_yield.py`
- `AgricultureProd/tools/duckdb/duckdb.exe`
- `AgriMarket/train_model2_base.py`, `train_model2_adjust.py`, `predict_model2.py`
- `AgriMarket/run_model2_pipeline.ps1`
- `aaaFinalModels/model1/` — Model 1 artifacts (Kamareddy district)

### Raw Data (required for pipeline rebuild)
- `Weather/` — 9 rainfall CSV files (2018–2026)
- `AgricultureProd/horticulture-*.csv` — 4 horticulture production CSVs
- `AgriMarket/final_agriculture_cleaned.csv` — market arrivals/prices data
- `Soil/agri_gini_output.csv` — soil data (though not actively used by models yet)
