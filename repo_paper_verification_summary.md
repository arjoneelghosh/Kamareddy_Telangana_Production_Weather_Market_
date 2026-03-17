# Repo-to-Paper Verification Summary

## Executive Summary

The repository supports a substantial, working AgriFore implementation, but not all paper claims are equally supported. The strongest repo-backed components are the DuckDB ETL stack, the Model 2 base market-price forecaster, the FastAPI backend, and the Next.js frontend. The Kamareddy weather-to-yield result is supported by a district-specific XGBoost artifact and metadata, but that result should be distinguished from broader experimental Model 1 scripts in `AgricultureProd/tools`. The RidgeCV adjustment layer and the LSTM autoencoder are implemented as offline artifacts and scripts, not as deployed backend inference modules.

The revised paper therefore softens deployment and integration language, clarifies the active SQL script count, corrects data-span wording, and separates deployed base-model functionality from offline experimental modules.

## Verified Claims

- `Weather-to-Yield XGBoost model exists and predicts yield_per_acre_proxy` ? VERIFIED.
  Evidence: `aaaFinalModels/model1/district_model_kamareddy.pkl`, `aaaFinalModels/model1/metadata_kamareddy.json`.
- `Model 1 achieves test R^2 around 0.77 on Kamareddy data` ? VERIFIED.
  Evidence: `aaaFinalModels/model1/metadata_kamareddy.json` (`test_metrics.r2 = 0.7701807237303334`).
- `Model 1 train/test row counts are 61 / 28` ? VERIFIED.
  Evidence: `aaaFinalModels/model1/metadata_kamareddy.json`.
- `Market Price XGBoost model exists and predicts monthly modal price` ? VERIFIED.
  Evidence: `AgriMarket/train_model2_base.py`, `AgriMarket/outputs/m2_base_model.pkl`, `AgriMarket/outputs/m2_base_metrics.csv`.
- `Model 2 achieves test R^2 around 0.8849` ? VERIFIED.
  Evidence: `AgriMarket/outputs/m2_base_metrics.csv` (`test_r2 = 0.8848663939994377`).
- `Model 2 train/test row counts are 28,571 / 4,264` ? VERIFIED.
  Evidence: `AgriMarket/outputs/m2_base_metrics.csv`.
- `Data covers 117 commodities and 169 AMC entries` ? VERIFIED for the market dataset/API listing.
  Evidence: `api_test_results.txt` (`GET /commodities` items = 117, `GET /markets` items = 169).
- `DuckDB ETL pipeline exists` ? VERIFIED.
  Evidence: `AgricultureProd/sql/*.sql`, `AgricultureProd/run_duckdb_pipeline.ps1`, `AgriMarket/run_model2_pipeline.ps1`.
- `Named DuckDB tables/views exist` ? VERIFIED.
  Evidence: `db_inspect.txt` lists `t_model1_dataset`, `v_model2_base_dataset`, `v_model2_adjust_dataset`, `t_market_monthly`, `t_weather_district_season`, etc.
- `LSTM Autoencoder for anomaly detection exists as implemented code` ? VERIFIED as offline code/artifacts.
  Evidence: `aaaFinalModels/model2/deeplearning_validator/market_lstm_autoencoder.h5`, `evaluate_lstm_autoencoder.py`, `lstm_config.json`, `inspection_output.txt`.
- `RidgeCV adjustment layer exists` ? VERIFIED.
  Evidence: `AgriMarket/train_model2_adjust.py`, `AgriMarket/outputs/m2_adjust_model.pkl`, `m2_adjust_metrics.csv`, `m2_adjust_metadata.json`.
- `FastAPI backend exists` ? VERIFIED.
  Evidence: `api/server.py`, `api/requirements.txt`.
- `Backend serves 12 endpoints` ? VERIFIED.
  Evidence: `api/server.py` plus `api_test_results.txt`; endpoint count includes `GET /health`.
- `/predict-price` uses a three-strategy fallback` ? VERIFIED.
  Evidence: `api/server.py` (`_predict_with_model`, precomputed 2024 CSV fallback, DuckDB historical average fallback).
- `Frontend is implemented in Next.js/React and uses backend endpoints` ? VERIFIED.
  Evidence: `frontend/package.json`, `frontend/app/*.tsx`, `frontend/services/api.ts`, `frontend/components/prediction/PredictionForm.tsx`.
- `Production-serving base-model artifacts come from aaaFinalModels` ? VERIFIED.
  Evidence: `api/server.py` loads `aaaFinalModels/model2/m2_base_model.pkl` and `aaaFinalModels/model2/m2_base_predictions_2024.csv`.

## Partially Verified Claims

- `System is an end-to-end full-stack application` ? PARTIALLY VERIFIED.
  The backend, frontend, ETL, and base-model inference are wired locally, but not every modeling component is deployed. Evidence: `api/server.py`, `frontend/services/api.ts`, local runners.
- `18 SQL transformation scripts` ? PARTIALLY VERIFIED.
  There are 18 SQL files under `AgricultureProd/sql`, but the active runnable chains use 17 stage scripts; `05_load_weather.sql` is superseded by `05_load_weather_v2.sql`.
- `Telangana district count matches repo usage` ? PARTIALLY VERIFIED.
  The paper's 30-district framing matches the market-facing API (`GET /districts` returns 30), but this is a repository/data-usage convention rather than a generic Telangana administrative claim.
- `RidgeCV adjustment is part of the Model 2 workflow` ? PARTIALLY VERIFIED.
  It is part of the offline training/prediction scripts (`train_model2_adjust.py`, `predict_model2.py`) but not backend-served inference.
- `LSTM anomaly detection is part of the system` ? PARTIALLY VERIFIED.
  It exists as offline validation code and artifacts, not as an API/frontend-integrated module.

## Unsupported or Overstated Claims

- `RidgeCV adjustment is deployed in backend inference` ? CONTRADICTED.
  Evidence: `api/server.py` loads only `aaaFinalModels/model2/m2_base_model.pkl`; no load of `m2_adjust_model.pkl`.
- `Adjustment layer is proven to improve prediction quality` ? NOT VERIFIED.
  Evidence: `AgriMarket/outputs/m2_adjust_metrics.csv` shows a completed RidgeCV run, but no repo artifact demonstrates improvement over the base model in deployed or controlled comparative evaluation.
- `LSTM anomaly detection is integrated into the served application` ? NOT VERIFIED.
  No endpoint or frontend component calls the validator.
- `The entire system is production-ready / fully deployed` ? NOT VERIFIED.
  Evidence: local app structure exists, but there is no deployment config, and backend inference is limited to the base model.
- `yield_signal is sourced from live Model 1 predictions` ? CONTRADICTED.
  Evidence: `AgricultureProd/sql/65_yield_feature_table.sql` builds `t_yield_seasonal` from `AgricultureProd/outputs/model1_dataset.csv`.
- `Five years of horticulture production data (2019-2023)` ? CONTRADICTED.
  Evidence: production inputs are four annual files: `2019-20`, `2020-21`, `2021-22`, `2022-23`.

## Internal Contradictions Found in the Paper

- The paper claimed `12 REST endpoints` but enumerated only 11 unless `GET /health` is included.
- The paper claimed `18 SQL transformation scripts` as an active ETL chain, while the runnable scripts are 17 active stages plus one retained legacy weather-loader file.
- The paper described the RidgeCV adjustment as part of the integrated prediction stack, while backend code serves only the base model.
- The paper described anomaly detection as part of the system workflow, while the repo shows it only as an offline validator.
- The paper described `yield_signal` as coming from Model 1 predictions, but SQL builds it from the seasonal yield dataset derived from `outputs/model1_dataset.csv`.
- The paper mixed a Kamareddy-specific Model 1 result with a broader Telangana-wide Model 2 deployment story without clearly separating district-specific and statewide scopes.

## Deployment Reality

- The deployable backend path is defined in `api/server.py`.
- The backend opens DuckDB read-only from `AgricultureProd/agri_validation.duckdb`.
- The backend loads only the base market model from `aaaFinalModels/model2/m2_base_model.pkl`.
- The backend fallback CSV is `aaaFinalModels/model2/m2_base_predictions_2024.csv`.
- The offline RidgeCV adjustment artifacts live in `AgriMarket/outputs` and are not loaded by the API.
- `AgriMarket/predict_model2.py` can optionally apply the adjuster offline if `m2_adjust_model.pkl` exists, but this is not the same as API deployment.
- The frontend is real and connected to backend endpoints through `frontend/services/api.ts`.
- The repo does not contain a full deployment stack such as Dockerfiles, orchestration, or production infra config.

## Recommended Paper Corrections

- Describe the SQL layer as `17 active stage scripts in the current runners, plus one superseded weather-loader SQL file retained in the repository`.
- Describe the Model 1 result as a `district-specific Kamareddy XGBoost artifact`, not as the only Model 1 implementation in the repo.
- Describe the RidgeCV layer as an `offline residual-correction experiment with saved artifacts`, not as deployed inference.
- Describe the LSTM autoencoder as an `offline anomaly validator` unless backend/frontend integration is added.
- Describe the backend as serving the `Model 2 base model with three fallbacks`, not a deployed two-stage adjustment pipeline.
- Replace `five years of horticulture production data (2019-2023)` with `four annual horticulture files (2019-20 through 2022-23)`.
- Keep the FastAPI/Next.js application claim, but frame it as a `working local full-stack implementation` rather than a fully integrated production deployment.
