# AgriFore Repository — Full Inventory Report

**Generated:** 2026-03-17  
**Repository:** `arjoneelghosh/Kamareddy_Telangana_Production_Weather_Market_`  
**Total Files:** 119 (excluding `.git`)  
**Total Directories:** 28 (excluding `.git`)  
**Total Size:** ~198 MB  

---

## Table of Contents

1. [Root-Level Files](#1-root-level-files)
2. [AgriMarket — Market Price Model Module](#2-agrimarket--market-price-model-module)
3. [AgricultureProd — Production & ETL Pipeline Module](#3-agricultureprod--production--etl-pipeline-module)
4. [aaaFinalModels — Canonical Model Artifacts](#4-aaafinalmodels--canonical-model-artifacts)
5. [api — FastAPI Backend](#5-api--fastapi-backend)
6. [frontend — Next.js Web Application](#6-frontend--nextjs-web-application)
7. [Summary Statistics](#7-summary-statistics)
8. [System Architecture Overview](#8-system-architecture-overview)

---

## 1. Root-Level Files

| # | File | Size | Type | Description |
|---|------|------|------|-------------|
| 1 | `.gitattributes` | ~1 KB | Config | Git LFS tracking rules for large binary files (`.pkl`, `.joblib`, `.duckdb`, `.exe`, `.zip`, `.docx`, `.pdf`) |
| 2 | `.gitignore` | ~1 KB | Config | Excludes build caches (`node_modules/`, `.next/`, `__pycache__/`, `.venv/`, `*.pyc`) and secrets |
| 3 | `AgriFore_IEEE_Paper.md` | 40 KB | 📄 Paper | Full IEEE-style research paper draft in Markdown describing the AgriFore system, methodology, results, and references |
| 4 | `AgriFore_IEEE_Paper_repo_verified.md` | 44 KB | 📄 Paper | Repo-verified version of the same IEEE paper — cross-referenced against actual code, data, and model output to ensure claims match implementation |
| 5 | `arjosankarfinalieee.docx` | 680 KB | 📄 Paper | IEEE paper in Microsoft Word format (submission-ready) |
| 6 | `arjosankarfinalieee.pdf` | 472 KB | 📄 Paper | IEEE paper in PDF format (submission-ready) |
| 7 | `api_test_results.txt` | 8 KB | 📝 Log | Log of API endpoint test results from a live backend session — includes responses for `/health`, `/predict`, `/market/overview`, `/commodities`, etc. |
| 8 | `db_inspect.txt` | 20 KB | 📝 Log | DuckDB schema inspection dump — lists all tables, views, columns, and row counts in `agri_validation.duckdb` |
| 9 | `db_tables.txt` | 0 KB | 📝 Log | Empty file (likely a failed or partial capture of DB table listing) |
| 10 | `forecast_raw_outputs.json` | ~1 KB | 📊 Analysis | Raw JSON responses from 7 API calls (health check + 6 commodity price predictions across Telangana districts) |
| 11 | `march2026_forecast.json` | 4 KB | 📊 Analysis | JSON output from the `run_march2026.py` demo script — price predictions for Tomato, Cotton, Maize, Red Gram, Bengal Gram, Chillies for March 2026 |
| 12 | `march2026_prediction_vs_reality.md` | 8 KB | 📊 Analysis | Markdown report comparing March 2026 model predictions against actual market price data; includes commodity-by-commodity accuracy review |
| 13 | `repo_audit.md` | 12 KB | 📝 Docs | Audit of the repo identifying: (1) useless/unused items to delete, (2) insight/documentation files not required for running the system; also identifies what IS required for system operation |
| 14 | `repo_paper_change_log.md` | 8 KB | 📝 Docs | Changelog documenting iterations and revisions made to align the IEEE paper with the actual repository implementation |
| 15 | `repo_paper_verification_summary.md` | 12 KB | 📝 Docs | Summary of how each paper claim (model R², dataset size, feature count, pipeline steps) was verified against actual repo outputs |
| 16 | `run_march2026.py` | 4 KB | 🔧 Script | Standalone Python script that calls the live FastAPI backend to generate and display March 2026 price forecasts for selected commodities and districts |
| 17 | `runtime_commands_log.txt` | 4 KB | 📝 Log | Log of shell commands executed during a backend runtime test session |
| 18 | `runtime_errors_log.txt` | 4 KB | 📝 Log | Error and warning messages captured during a backend runtime session |
| 19 | `runtime_run_report.md` | 8 KB | 📝 Docs | Structured report from a past backend runtime test — covers server startup, endpoint responses, and error diagnosis |
| 20 | `sample_forecast_output.md` | 8 KB | 📊 Analysis | Formatted sample output showing the full prediction result structure for multiple commodities |

---

## 2. AgriMarket — Market Price Model Module

This module contains the Model 2 (market price XGBoost) training, adjustment, and prediction scripts, plus all output artifacts.

### 2a. Scripts

| # | File | Size | Type | Description |
|---|------|------|------|-------------|
| 1 | `AgriMarket/train_model2_base.py` | 12 KB | 🐍 Python | Trains the base XGBoost market price model (`m2_base_model.pkl`). Reads from DuckDB (`model2_base_dataset` view), engineers lag/rolling features, performs train/test split (cut-off: 2023-12-01), fits XGBoost pipeline, and saves model + metadata + metrics |
| 2 | `AgriMarket/train_model2_adjust.py` | 12 KB | 🐍 Python | Trains the RidgeCV yield-adjustment layer (Model 2 adjust). Takes base model residuals and combines with yield-signal features to build a correction layer; saves `m2_adjust_metadata.json` and `m2_adjust_metrics.csv` |
| 3 | `AgriMarket/predict_model2.py` | 8 KB | 🐍 Python | Inference script for Model 2. Loads `m2_base_model.pkl`, queries DuckDB for features, and outputs price predictions for a given commodity/district/month/year combination |
| 4 | `AgriMarket/run_model2_pipeline.ps1` | 4 KB | PowerShell | Orchestration script that runs `train_model2_base.py` → `train_model2_adjust.py` in sequence; used to retrain the full Model 2 pipeline from scratch |

### 2b. Outputs

| # | File | Size | Type | Description |
|---|------|------|------|-------------|
| 5 | `AgriMarket/outputs/m2_base_model.pkl` | 2.5 MB | 🤖 Model | Serialized XGBoost pipeline for base market price prediction (117 commodities × 169 AMC markets; test R² = 0.885) |
| 6 | `AgriMarket/outputs/m2_base_training_metadata.json` | ~1 KB | 📋 Metadata | Training configuration and environment metadata for the base Model 2 (feature list, train cutoff, test range, model name) |
| 7 | `AgriMarket/outputs/m2_base_metrics.csv` | ~1 KB | 📊 Metrics | Model 2 base performance metrics: train R²=0.957, test R²=0.885, test RMSE=1171 (₹/quintal), test MAE=610; 28,571 train rows, 4,264 test rows |
| 8 | `AgriMarket/outputs/m2_adjust_metadata.json` | ~1 KB | 📋 Metadata | Configuration metadata for the RidgeCV yield-adjustment layer |
| 9 | `AgriMarket/outputs/m2_adjust_metrics.csv` | ~1 KB | 📊 Metrics | Performance metrics for the yield-adjusted Model 2 predictions |
| 10 | `AgriMarket/outputs/correlationmatrix.png` | 432 KB | 🖼️ Image | Correlation heatmap of Model 2 feature set (lag features, weather variables, arrivals, month) |
| 11 | `AgriMarket/outputs/direct comparison.png` | 176 KB | 🖼️ Image | Side-by-side comparison chart of base vs. adjusted Model 2 price predictions |
| 12 | `AgriMarket/outputs/Screenshot 2026-03-03 011925.png` | 376 KB | 🖼️ Image | Screenshot of terminal/IDE output captured during model training (not referenced by code) |
| 13 | `AgriMarket/outputs/terminal_screenshot.png` | 728 KB | 🖼️ Image | Screenshot of terminal output from a training run (not referenced by code) |

---

## 3. AgricultureProd — Production & ETL Pipeline Module

This module contains the DuckDB-based ETL pipeline, SQL transformation scripts, Model 1 training tools, and all intermediate outputs. It also houses the main database.

### 3a. Pipeline Orchestration

| # | File | Size | Type | Description |
|---|------|------|------|-------------|
| 1 | `AgricultureProd/run_duckdb_pipeline.ps1` | 4 KB | PowerShell | Master pipeline runner — executes all 18 SQL scripts in order through DuckDB, then exports CSV outputs to `outputs/`; also trains Model 1 by calling `tools/train_model1_xgboost.py` |
| 2 | `AgricultureProd/README_PIPELINE.md` | 3 KB | 📝 Docs | Documentation for the DuckDB pipeline — usage instructions, output file descriptions, and quick sanity SQL queries |

### 3b. Database

| # | File | Size | Type | Description |
|---|------|------|------|-------------|
| 3 | `AgricultureProd/agri_validation.duckdb` | 118 MB | 🗄️ Database | Main DuckDB analytical database containing all raw, cleaned, and feature-engineered tables for production data, weather data, and market data; queried by the FastAPI backend at runtime |

### 3c. SQL Scripts (ETL Pipeline — 18 scripts)

| # | File | Size | Stage | Description |
|---|------|------|-------|-------------|
| 4 | `AgricultureProd/sql/00_load_telangana.sql` | 4 KB | Ingest | Loads 4 horticulture production CSVs (`horticulture-*.csv`) into `tg_raw` table |
| 5 | `AgricultureProd/sql/05_load_weather.sql` | 8 KB | Ingest | Loads 9 IMD rainfall CSV files (2018–2026) into `weather_raw`, applies deduplication into `weather_clean` |
| 6 | `AgricultureProd/sql/05_load_weather_v2.sql` | 8 KB | Ingest | Version 2 of weather loading — improved district name normalization and fuzzy-match handling |
| 7 | `AgricultureProd/sql/10_views_telangana.sql` | 4 KB | Transform | Creates views `v_prod_real` (production) and `v_area_real` (area) with standardized column names and filters |
| 8 | `AgricultureProd/sql/15_weather_features.sql` | 4 KB | Feature Engineering | Builds `t_weather_district_day` — district-level daily aggregates of rainfall and humidity |
| 9 | `AgricultureProd/sql/17_weather_seasonal.sql` | 4 KB | Feature Engineering | Builds `t_weather_district_season` — seasonal (kharif/rabi/summer) weather aggregates by district and production year |
| 10 | `AgricultureProd/sql/18_district_match_diagnostics.sql` | 8 KB | Diagnostics | Analyzes district name matching between production and weather data; identifies unmatched districts |
| 11 | `AgricultureProd/sql/20_coverage_and_stability.sql` | 8 KB | Diagnostics | Computes crop/year/district coverage statistics and crop stability metrics (crops seen across all years) |
| 12 | `AgricultureProd/sql/30_outlier_detection.sql` | 4 KB | QA | MAD-based outlier detection for yield-per-acre values; produces `yield_outliers_by_year.csv` and `yield_outliers_top50.csv` |
| 13 | `AgricultureProd/sql/40_season_alignment.sql` | 4 KB | Transform | Maps crop production records to harvest years and season buckets; creates `t_harvest_year_rollup` |
| 14 | `AgricultureProd/sql/50_model1_dataset.sql` | 8 KB | Model Prep | Joins production labels to seasonal weather features to produce the final Model 1 training dataset (`model1_dataset.csv`) |
| 15 | `AgricultureProd/sql/60_load_market.sql` | 4 KB | Ingest | Loads `final_agriculture_cleaned.csv` market transactions into `market_raw` table |
| 16 | `AgricultureProd/sql/61_market_monthly.sql` | 4 KB | Aggregate | Aggregates daily market transactions to monthly price/arrival summaries |
| 17 | `AgricultureProd/sql/62_weather_monthly_features.sql` | 4 KB | Feature Engineering | Builds `t_weather_district_month` — monthly weather summaries for use in Model 2 features |
| 18 | `AgricultureProd/sql/63_calendar_month_to_season.sql` | 4 KB | Lookup | Creates a calendar-month-to-season mapping table (kharif/rabi/summer by month number) |
| 19 | `AgricultureProd/sql/64_model2_base_dataset.sql` | 4 KB | Model Prep | Joins monthly market data with weather features and lag/rolling price features to create Model 2 base dataset |
| 20 | `AgricultureProd/sql/65_yield_feature_table.sql` | 4 KB | Model Prep | Creates a yield signal feature table for use by the RidgeCV adjustment layer |
| 21 | `AgricultureProd/sql/66_model2_adjust_dataset.sql` | 4 KB | Model Prep | Joins base model residuals with yield features to produce the Model 2 adjustment training dataset |

### 3d. Model Training Tools

| # | File | Size | Type | Description |
|---|------|------|------|-------------|
| 22 | `AgricultureProd/tools/train_model1_weather_to_yield.py` | 8 KB | 🐍 Python | Original Model 1 training script using a Random Forest approach; reads `model1_dataset.csv`, trains RF, saves `model1_rf.joblib` |
| 23 | `AgricultureProd/tools/train_model1_xgboost.py` | 28 KB | 🐍 Python | Primary Model 1 training script using XGBoost; reads from DuckDB, trains district-level XGBoost models, saves `.pkl` and `metadata_kamareddy.json`; this is the canonical trainer used in the pipeline |
| 24 | `AgricultureProd/tools/train_model1_xgboost_50%.py` | 16 KB | 🐍 Python | Variant of the XGBoost Model 1 trainer using only 50% of training data (used for sensitivity/ablation experiments) |
| 25 | `AgricultureProd/tools/duckdb/duckdb.exe` | 33 MB | ⚙️ Binary | DuckDB CLI executable (Windows x86_64) — used by PowerShell scripts to run SQL files against the database |
| 26 | `AgricultureProd/tools/duckdb.zip` | 12 MB | 📦 Archive | Zipped DuckDB CLI binary — redundant since `duckdb.exe` is already extracted; safe to delete |

### 3e. One-Off Exploration / Validation Scripts

| # | File | Size | Type | Description |
|---|------|------|------|-------------|
| 27 | `AgricultureProd/duckdb_validate.py` | 4 KB | 🐍 Python | Initial DB setup helper script; creates the DuckDB database and loads raw data manually (predates the SQL pipeline; no longer used) |
| 28 | `AgricultureProd/duckdb_phase1_conditionB.py` | 4 KB | 🐍 Python | Ad-hoc Phase 1 exploration script that checks year/crop/district counts; produces two CSVs now absent from current repo state |
| 29 | `AgricultureProd/validate_weather_rebuild.py` | 4 KB | 🐍 Python | One-off script to validate weather data rebuilding; not part of the main pipeline |

### 3f. Pipeline Outputs

| # | File | Size | Type | Description |
|---|------|------|------|-------------|
| 30 | `AgricultureProd/outputs/model1_rf.joblib` | 24 MB | 🤖 Model | Serialized Random Forest model for crop yield prediction (older variant; the XGBoost version in `aaaFinalModels/model1/` is canonical) |
| 31 | `AgricultureProd/outputs/model1_metadata.json` | ~1 KB | 📋 Metadata | Metadata for the Random Forest Model 1 variant |
| 32 | `AgricultureProd/outputs/xgb_tune_config.json` | ~1 KB | 📋 Config | XGBoost hyperparameter tuning configuration used during Model 1 experiments |
| 33 | `AgricultureProd/outputs/codex_tuning_summary.txt` | ~1 KB | 📝 Log | Summary text of the XGBoost hyperparameter tuning process |
| 34 | `AgricultureProd/outputs/Screenshot 2026-03-03 011925.png` | 376 KB | 🖼️ Image | Screenshot of terminal during pipeline run (not referenced by code) |
| 35 | `AgricultureProd/outputs/Kamareddy_Selected/district_model_kamareddy.pkl` | 1.5 MB | 🤖 Model | District-specific XGBoost yield prediction model for Kamareddy (duplicate of `aaaFinalModels/model1/district_model_kamareddy.pkl`) |
| 36 | `AgricultureProd/outputs/Kamareddy_Selected/metadata_kamareddy.json` | ~1 KB | 📋 Metadata | Metadata for the above Kamareddy model (duplicate of `aaaFinalModels/model1/metadata_kamareddy.json`) |
| 37 | `AgricultureProd/outputs/Kamareddy_Selected/forecasting.py` | 8 KB | 🐍 Python | Standalone forecasting script that was developed inside the outputs folder during experimentation |
| 38 | `AgricultureProd/outputs/Kamareddy_Selected/Screenshot 2026-03-03 011925.png` | 376 KB | 🖼️ Image | Duplicate screenshot (not referenced by code) |

---

## 4. aaaFinalModels — Canonical Model Artifacts

This directory holds the **production-ready, canonical** model files used by the FastAPI backend at runtime.

### 4a. Model 1 — Weather-to-Yield XGBoost (Kamareddy District)

| # | File | Size | Type | Description |
|---|------|------|------|-------------|
| 1 | `aaaFinalModels/model1/district_model_kamareddy.pkl` | 1.5 MB | 🤖 Model | Serialized XGBoost pipeline for crop yield prediction in Kamareddy district. Features: 11 numeric weather inputs (rainfall total, rainy days, humidity min/max, intensity, anomaly, deviation, mandal reporting, days/months covered) + 3 categorical (district, crop, season). **Test R² = 0.77** |
| 2 | `aaaFinalModels/model1/metadata_kamareddy.json` | ~2 KB | 📋 Metadata | Full training metadata: 61 train rows, 28 test rows, train years 2020–22, test year 2022–23, XGBoost params (max_depth=8, lr=0.05, n_estimators=1000), train R²≈1.0, test R²=0.77, RMSE=3.94, MAE=2.06 |

### 4b. Model 2 — Market Price XGBoost (Canonical Copy)

| # | File | Size | Type | Description |
|---|------|------|------|-------------|
| 3 | `aaaFinalModels/model2/m2_base_model.pkl` | 2.6 MB | 🤖 Model | Canonical serialized XGBoost pipeline for market price prediction across all 117 commodities and 169 AMC markets in Telangana. Features include lag prices (1/2/3/6/12 months), rolling means, monthly encodings (sin/cos), market arrivals, weather variables, and categoricals. **Test R² = 0.885** |
| 4 | `aaaFinalModels/model2/m2_base_training_metadata.json` | ~1 KB | 📋 Metadata | Training metadata for Model 2: features list, train cutoff (2023-12-01), test range (2024-01–2024-12), model name |
| 5 | `aaaFinalModels/model2/m2_base_metrics.csv` | ~1 KB | 📊 Metrics | Model 2 metrics: train R²=0.957, test R²=0.885, test RMSE=1171 ₹/quintal, test MAE=610; 28,571 train rows, 4,264 test rows |

### 4c. Model 2 — Deep Learning Validator

| # | File | Size | Type | Description |
|---|------|------|------|-------------|
| 6 | `aaaFinalModels/model2/deeplearning_validator/evaluate_lstm_autoencoder.py` | 12 KB | 🐍 Python | Script that trains and evaluates an LSTM Autoencoder for anomalous market price sequence detection; loads sequences from DuckDB, trains the autoencoder, and reports reconstruction error distribution |
| 7 | `aaaFinalModels/model2/deeplearning_validator/evaluate_validated_model.py` | 12 KB | 🐍 Python | Script that cross-validates the base Model 2 XGBoost predictions using the LSTM anomaly scores as an overlay; produces combined accuracy/anomaly report |
| 8 | `aaaFinalModels/model2/deeplearning_validator/lstm_config.json` | 12 KB | 📋 Config | LSTM Autoencoder configuration: architecture (input/hidden/latent dims, sequence length, threshold), training hyperparameters, and environment versions |
| 9 | `aaaFinalModels/model2/deeplearning_validator/inspection_output.txt` | 4 KB | 📝 Log | Text output from a validator inspection run — includes reconstruction errors, detected anomalies, and threshold statistics |
| 10 | `aaaFinalModels/model2/deeplearning_validator/xgb_info.txt` | 4 KB | 📝 Log | XGBoost model introspection output: feature importance rankings, number of trees, booster parameters |

---

## 5. api — FastAPI Backend

The Python FastAPI server that serves all REST endpoints consumed by the frontend.

| # | File | Size | Type | Description |
|---|------|------|------|-------------|
| 1 | `api/__init__.py` | ~1 KB | 🐍 Python | Package initializer for the `api` module |
| 2 | `api/server.py` | 28 KB | 🐍 Python | Main FastAPI application. Connects to `agri_validation.duckdb`, loads `m2_base_model.pkl`, and exposes 12 REST endpoints (see below) |
| 3 | `api/requirements.txt` | ~0.2 KB | 📋 Config | Python dependencies: `fastapi>=0.100`, `uvicorn[standard]`, `pandas`, `numpy`, `duckdb`, `joblib`, `xgboost`, `scikit-learn` |

### API Endpoints (from `api/server.py`)

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check — verifies DB connection and model loading |
| GET | `/commodities` | Lists all 117 available commodities |
| GET | `/districts` | Lists all Telangana districts in the dataset |
| GET | `/markets` | Lists all 169 AMC markets |
| GET | `/market/overview` | Summary stats: total markets, active commodities, avg price, total volume, price change |
| GET | `/market/trends` | Recent price trend data for the top commodities |
| GET | `/market/clusters` | Market cluster analysis results |
| GET | `/market/seasonal` | Seasonal price pattern data by commodity |
| GET | `/price-history/{commodity}` | Historical price time series for a specific commodity |
| POST | `/predict` | Main prediction endpoint — takes `{commodity, district?, market?, month, year}`, returns `{predicted_price, confidence}` |
| GET | `/yield/forecast` | Model 1 yield forecast for a given crop/season/district |
| GET | `/anomalies` | Recent price anomalies detected by the LSTM Autoencoder |

---

## 6. frontend — Next.js Web Application

A Next.js 15 / React 18 / TypeScript dashboard that provides the user interface for market intelligence and price prediction.

### 6a. Configuration Files

| # | File | Size | Type | Description |
|---|------|------|------|-------------|
| 1 | `frontend/package.json` | ~1 KB | 📋 Config | Node.js project definition — name: `ai-agricultural-market-frontend`, version 0.1.0; scripts: `dev`, `build`, `start`, `lint` |
| 2 | `frontend/package-lock.json` | 232 KB | 📋 Config | Exact dependency lock file for reproducible installs |
| 3 | `frontend/next.config.js` | ~1 KB | 📋 Config | Next.js configuration (API proxy settings, environment variables) |
| 4 | `frontend/tsconfig.json` | ~1 KB | 📋 Config | TypeScript compiler configuration |
| 5 | `frontend/tailwind.config.ts` | ~1 KB | 📋 Config | Tailwind CSS configuration (content paths, theme, plugins) |
| 6 | `frontend/postcss.config.mjs` | ~0.2 KB | 📋 Config | PostCSS configuration for Tailwind CSS processing |
| 7 | `frontend/.eslintrc.json` | ~0.2 KB | 📋 Config | ESLint configuration extending `next/core-web-vitals` |
| 8 | `frontend/.gitignore` | ~1 KB | Config | Frontend-specific gitignore (node_modules, .next, build artifacts) |
| 9 | `frontend/.env.local.example` | ~0.2 KB | Config | Example environment file with `NEXT_PUBLIC_API_URL` placeholder |
| 10 | `frontend/README.md` | 8 KB | 📝 Docs | Frontend-specific README covering setup, development, and deployment instructions |

**Key Dependencies:**  
- `next@15.5.12`, `react@18`, `react-dom@18` — framework  
- `recharts@2.12.0` — charting library for price trend/arrival charts  
- `axios@1.6.7` — HTTP client for API calls  
- `lucide-react@0.344.0` — icon library  
- `date-fns@3.3.1` — date formatting utilities  
- `tailwindcss@3.3.0` — utility-first CSS  

### 6b. App Pages

| # | File | Size | Description |
|---|------|------|-------------|
| 11 | `frontend/app/layout.tsx` | ~1 KB | Root layout component — wraps all pages in the `Layout` component, sets metadata (title, description) |
| 12 | `frontend/app/globals.css` | ~1 KB | Global CSS file with Tailwind directives and custom base styles |
| 13 | `frontend/app/page.tsx` | 8 KB | **Dashboard / Home page** — displays `StatCard` summary tiles (markets, commodities, avg price, volume), `TopCommodities`, `PriceTrendChart`, and `MarketClusters` |
| 14 | `frontend/app/analysis/page.tsx` | ~1 KB | **Analysis page** — shows `SeasonalPatternChart` and `ArrivalVsPriceChart` |
| 15 | `frontend/app/prediction/page.tsx` | ~1 KB | **Prediction page** — hosts the `PredictionForm` and `PredictionResult` components for interactive price forecasting |

### 6c. Layout Components

| # | File | Size | Description |
|---|------|------|-------------|
| 16 | `frontend/components/layout/Layout.tsx` | ~1 KB | Outer layout shell — renders `Header` + `Sidebar` + main content area |
| 17 | `frontend/components/layout/Header.tsx` | ~1 KB | Top navigation bar with application title and logo |
| 18 | `frontend/components/layout/Sidebar.tsx` | ~1 KB | Left navigation sidebar with links to Dashboard, Analysis, and Prediction pages |

### 6d. Chart Components

| # | File | Size | Description |
|---|------|------|-------------|
| 19 | `frontend/components/charts/PriceTrendChart.tsx` | ~1 KB | Recharts `LineChart` showing commodity price over time (fetches from `/market/trends`) |
| 20 | `frontend/components/charts/TrendChart.tsx` | ~1 KB | Generic trend chart used for rendering historical price series from `/price-history/{commodity}` |
| 21 | `frontend/components/charts/SeasonalPatternChart.tsx` | ~1 KB | `BarChart` showing average price by month/season for a selected commodity (fetches from `/market/seasonal`) |
| 22 | `frontend/components/charts/ArrivalVsPriceChart.tsx` | ~1 KB | Dual-axis chart comparing market arrival volumes vs. price over time |

### 6e. Dashboard Components

| # | File | Size | Description |
|---|------|------|-------------|
| 23 | `frontend/components/dashboard/StatCard.tsx` | ~1 KB | Summary stat tile — displays a label, value, icon, and optional change indicator |
| 24 | `frontend/components/dashboard/TopCommodities.tsx` | ~1 KB | Table/list of the top 10 commodities by market volume (fetches from `/commodities`) |
| 25 | `frontend/components/dashboard/MarketClusters.tsx` | ~1 KB | Visual display of market cluster analysis (fetches from `/market/clusters`) |

### 6f. Prediction Components

| # | File | Size | Description |
|---|------|------|-------------|
| 26 | `frontend/components/prediction/PredictionForm.tsx` | 8 KB | Interactive form for price prediction — dropdowns for commodity, district, market; date pickers for month/year; submits to `/predict` |
| 27 | `frontend/components/prediction/PredictionResult.tsx` | ~1 KB | Displays the prediction result — commodity name, predicted price (₹/quintal), confidence score |

### 6g. UI Components

| # | File | Size | Description |
|---|------|------|-------------|
| 28 | `frontend/components/ui/Button.tsx` | ~1 KB | Reusable button with variant styles (primary, secondary, outline) |
| 29 | `frontend/components/ui/Card.tsx` | ~1 KB | Reusable card container with shadow and border |
| 30 | `frontend/components/ui/Input.tsx` | ~1 KB | Styled text input component |
| 31 | `frontend/components/ui/Select.tsx` | ~1 KB | Styled dropdown/select component |
| 32 | `frontend/components/ui/LoadingSpinner.tsx` | ~1 KB | Animated SVG loading indicator |

### 6h. Services, Types, and Utilities

| # | File | Size | Description |
|---|------|------|-------------|
| 33 | `frontend/services/api.ts` | 8 KB | Axios-based API client — defines typed functions for all backend endpoints (`fetchCommodities`, `fetchMarketOverview`, `predict`, `fetchPriceHistory`, etc.) |
| 34 | `frontend/types/index.ts` | ~1 KB | TypeScript type definitions for all domain objects: `Commodity`, `PredictionRequest`, `PredictionResult`, `MarketOverview`, `PriceTrendPoint`, etc. |
| 35 | `frontend/utils/formatters.ts` | ~1 KB | Utility functions for formatting currency (₹), numbers, percentages, and dates for display |

---

## 7. Summary Statistics

### Files by Category

| Category | Count | Total Size |
|----------|-------|-----------|
| 🐍 Python scripts | 15 | ~140 KB |
| 📄 TypeScript/TSX source | 25 | ~100 KB |
| 🗄️ SQL scripts | 18 | ~100 KB |
| 🤖 ML model binaries (`.pkl`, `.joblib`) | 5 | ~30 MB |
| 🗄️ DuckDB database | 1 | ~118 MB |
| ⚙️ Binary / archive | 2 | ~45 MB |
| 📋 JSON config/metadata | 14 | ~30 KB |
| 📝 Markdown documentation | 10 | ~140 KB |
| 📝 Text logs | 9 | ~50 KB |
| 🖼️ PNG images | 6 | ~2.5 MB |
| 📄 Paper (DOCX/PDF) | 2 | ~1.2 MB |
| 📦 Node package lock | 1 | ~232 KB |
| ⚙️ Config files | 11 | ~20 KB |
| **Total** | **119** | **~198 MB** |

### Files by Directory

| Directory | Files | Purpose |
|-----------|-------|---------|
| `/` (root) | 20 | Papers, logs, demo scripts, documentation |
| `AgriMarket/` | 4 | Model 2 training scripts |
| `AgriMarket/outputs/` | 9 | Model 2 artifacts and charts |
| `AgricultureProd/` | 3 | ETL pipeline orchestration + DB |
| `AgricultureProd/sql/` | 18 | ETL SQL transformation scripts |
| `AgricultureProd/tools/` | 4 | Model 1 training scripts + DuckDB CLI |
| `AgricultureProd/tools/duckdb/` | 1 | DuckDB executable |
| `AgricultureProd/outputs/` | 5 | Pipeline outputs |
| `AgricultureProd/outputs/Kamareddy_Selected/` | 4 | Duplicate Model 1 artifacts |
| `aaaFinalModels/model1/` | 2 | **Canonical** Model 1 artifacts |
| `aaaFinalModels/model2/` | 3 | **Canonical** Model 2 artifacts |
| `aaaFinalModels/model2/deeplearning_validator/` | 5 | LSTM validator scripts + artifacts |
| `api/` | 3 | FastAPI backend server |
| `frontend/` | 10 | Next.js config + README |
| `frontend/app/` | 3 | Next.js page components |
| `frontend/app/analysis/` | 1 | Analysis page |
| `frontend/app/prediction/` | 1 | Prediction page |
| `frontend/components/charts/` | 4 | Chart components |
| `frontend/components/dashboard/` | 3 | Dashboard components |
| `frontend/components/layout/` | 3 | Layout components |
| `frontend/components/prediction/` | 2 | Prediction components |
| `frontend/components/ui/` | 5 | UI primitives |
| `frontend/services/` | 1 | API client service |
| `frontend/types/` | 1 | TypeScript types |
| `frontend/utils/` | 1 | Formatter utilities |

---

## 8. System Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────┐
│                     AgriFore System Architecture                    │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  DATA SOURCES                                                       │
│  ├── IMD Rainfall CSVs (2018–2026)         ─┐                      │
│  ├── Telangana Horticulture CSVs (4 files)  ├─► DuckDB ETL         │
│  └── Market Transactions CSV (117 crops)   ─┘   (18 SQL scripts)  │
│                                                     │               │
│                                                     ▼               │
│                                         agri_validation.duckdb      │
│                                         (118 MB analytical DB)      │
│                                                     │               │
│  TRAINING PIPELINE                                  │               │
│  ├── train_model1_xgboost.py  ─────────────────────►│              │
│  │   └── Kamareddy XGBoost Yield Model              │              │
│  │       (R² = 0.77 on test year 2022-23)           │              │
│  │                                                  │              │
│  ├── train_model2_base.py  ────────────────────────►│              │
│  │   └── Market Price XGBoost                       │              │
│  │       (R² = 0.885, 117 crops × 169 markets)      │              │
│  │                                                  │              │
│  ├── train_model2_adjust.py (RidgeCV layer)          │              │
│  └── evaluate_lstm_autoencoder.py                    │              │
│      └── LSTM Autoencoder Anomaly Detector           │              │
│                                                     │               │
│  RUNTIME                                            │               │
│  ┌─────────────────────────────┐                    │               │
│  │  api/server.py (FastAPI)    │◄───────────────────┘               │
│  │  12 REST endpoints          │                                    │
│  │  Loads: duckdb, m2_base.pkl │                                    │
│  └────────────┬────────────────┘                                    │
│               │ HTTP (JSON)                                         │
│  ┌────────────▼────────────────┐                                    │
│  │  frontend/ (Next.js 15)     │                                    │
│  │  Dashboard, Analysis,       │                                    │
│  │  Prediction UI              │                                    │
│  └─────────────────────────────┘                                    │
└─────────────────────────────────────────────────────────────────────┘
```

### Key Model Performance Summary

| Model | Algorithm | Training Data | Key Metric |
|-------|-----------|--------------|------------|
| Model 1 — Yield | XGBoost | 61 train rows (Kamareddy, 2020–22) | Test R² = **0.77** |
| Model 2 — Price | XGBoost | 28,571 train rows (all districts, 2019–2023) | Test R² = **0.885** |
| Model 2 Adjust | RidgeCV | Residuals + yield features | Correction layer over Model 2 |
| Anomaly Detector | LSTM Autoencoder | Market price sequences | Reconstruction error threshold |

---

*This report was generated by scanning all 119 files across 28 directories in the repository root. For cleanup recommendations (unused files, duplicates), see `repo_audit.md`. For paper-to-implementation verification, see `repo_paper_verification_summary.md`.*
