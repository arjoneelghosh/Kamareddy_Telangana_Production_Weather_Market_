# AgriFore — Runtime Run Report

> **Date:** 2026-03-17  
> **Operator:** Antigravity (automated)  
> **Repository:** `C:\Users\footb\Desktop\AgriFore`

---

## Executive Summary

**The project runs end-to-end.** The backend API starts cleanly, loads the trained M2 XGBoost model, connects to the DuckDB database, and serves real price predictions via `POST /predict-price`. Four out of five sample forecasts returned valid predictions directly from the trained model (confidence 0.85). No code changes were required.

---

## A. Runtime Discovery

### Backend Entrypoint
- **File:** `api/server.py`
- **Module:** `api.server:app`
- **Framework:** FastAPI
- **Run command:** `python -m uvicorn api.server:app --host 127.0.0.1 --port 8000`
- **Docs:** `http://localhost:8000/docs` (Swagger)

### Required Dependencies
- **File:** `api/requirements.txt`
- **Packages:** fastapi, uvicorn[standard], pandas, numpy, duckdb, joblib, xgboost, scikit-learn
- **Status:** All already installed. No `pip install` was needed.

### Trained Models
| Model | Path | Size | Purpose |
|---|---|---|---|
| M2 Base XGBoost | `aaaFinalModels/model2/m2_base_model.pkl` | 2.6 MB | Crop price prediction (multi-crop, multi-market) |
| M1 Kamareddy | `aaaFinalModels/model1/district_model_kamareddy.pkl` | 1.5 MB | Weather→Yield for Kamareddy district |
| M2 Predictions CSV | `aaaFinalModels/model2/m2_base_predictions_2024.csv` | 283 KB | Pre-computed 2024 fallback predictions |

### Database
- **Path:** `AgricultureProd/agri_validation.duckdb`
- **Tables used:** `t_market_monthly`, `v_model2_base_dataset`
- **Status:** Exists, readable, connected at startup

### Forecast Endpoint
- **URL:** `POST /predict-price`
- **Parameters:** `commodity` (required), `market` (optional), `district` (optional), `month` (optional), `year` (optional)
- **Strategy cascade:**
  1. M2 XGBoost with real-time feature engineering from DuckDB (confidence 0.85)
  2. Lookup from `m2_base_predictions_2024.csv` (confidence 0.70)
  3. Historical average from DuckDB (confidence 0.50)

---

## B. System Start & Test Results

### Server Startup
```
python -m uvicorn api.server:app --host 127.0.0.1 --port 8000
```
- **Result:** ✅ Server started on http://127.0.0.1:8000
- **Warnings:** sklearn version mismatch (1.2.2 pickled, 1.6.1 installed) — non-fatal
- **Model loaded:** Yes — "Loaded M2 base model (N features)"
- **Predictions CSV loaded:** Yes — "Loaded 2024 predictions (N rows)"

### Health Check
```
GET http://127.0.0.1:8000/health → 200 OK
{
  "status": "ok",
  "database": "connected",
  "model_m2_base": "loaded",
  "predictions_2024": "loaded"
}
```

### Other Endpoints Tested
| Endpoint | Status | Notes |
|---|---|---|
| `GET /health` | ✅ 200 | All systems green |
| `GET /commodities` | ✅ 200 | 117 commodities |
| `GET /markets` | ✅ 200 | 169 AMC markets |
| `GET /districts` | ✅ 200 | 30 Telangana districts |
| `GET /market-overview` | ✅ 200 | Dashboard stats |
| `GET /top-commodities` | ✅ 200 | Top 8 by volume |
| `GET /market-clusters` | ✅ 200 | 6 major clusters |
| `GET /price-trends` | ✅ 200 | Historical trend data |
| `GET /seasonal-data` | ✅ 200 | 12 months of seasonal pattern |
| `GET /arrival-data` | ✅ 200 | Arrival vs price |
| `POST /predict-price` | ✅ 200 | Real XGBoost predictions |
| `POST /ask-agent` | ✅ 200 | Stub Q&A |

---

## C. Forecast Execution

### What was run
Five `POST /predict-price` calls with different crop/market/month combinations.

### Results Summary
| Crop | Location | Month/Year | Predicted Price | Confidence | Model Used |
|---|---|---|---|---|---|
| Tomato | Hyderabad district | Jun 2025 | ₹2,467/qtl | 0.85 | M2 XGBoost ✅ |
| Cotton | Statewide | Oct 2025 | ₹7,347/qtl | 0.85 | M2 XGBoost ✅ |
| Paddy | Warangal market | Dec 2025 | ₹1,637/qtl | 0.85 | M2 XGBoost ✅ |
| Onions | Siddipet district | Mar 2026 | — | — | 404 (data gap) ❌ |
| Maize | Karimnagar district | Aug 2025 | ₹2,292/qtl | 0.85 | M2 XGBoost ✅ |

### What worked
- Server starts cleanly with all assets loaded
- The M2 XGBoost model loads and produces predictions (Strategy 1)
- Feature engineering from DuckDB works — lag features, rolling means, cyclical encoding
- 4 out of 5 forecasts returned real model predictions (confidence 0.85)

### What failed
- **Onions in Siddipet:** 404 — data coverage gap. The `v_model2_base_dataset` view doesn't have enough onion records for Siddipet. All three strategies exhausted. This is a data issue, not a code bug.

### What was fixed
- **Nothing.** No code or path fixes were needed. The system ran as-is from the repository.

### Model/Artifact/Path used
- **Model:** `C:\Users\footb\Desktop\AgriFore\aaaFinalModels\model2\m2_base_model.pkl`
- **Database:** `C:\Users\footb\Desktop\AgriFore\AgricultureProd\agri_validation.duckdb`
- **View used for features:** `v_model2_base_dataset` (DuckDB view)
- **Fallback CSV:** `C:\Users\footb\Desktop\AgriFore\aaaFinalModels\model2\m2_base_predictions_2024.csv`

### Result source
**Live backend API** — not a direct script or simulation. The predictions went through the full FastAPI endpoint → DuckDB feature engineering → XGBoost model inference → JSON response pipeline.

---

## D. Final Answers

### Can the project actually run right now?
**Yes.** The backend starts, loads all models and data, and serves all endpoints correctly.

### Can it produce a real forecast right now?
**Yes.** The `POST /predict-price` endpoint produces real XGBoost model predictions for most crop/market combinations. 4 out of 5 test cases succeeded with the primary model strategy.

### What exact command should I run locally to reproduce a successful sample forecast?

**Step 1: Start the server** (from the repo root `C:\Users\footb\Desktop\AgriFore`):
```bash
python -m uvicorn api.server:app --host 127.0.0.1 --port 8000
```

**Step 2: Hit the predict endpoint** (in another terminal):
```bash
curl -X POST http://127.0.0.1:8000/predict-price -H "Content-Type: application/json" -d "{\"commodity\": \"tomato\", \"district\": \"Hyderabad\", \"month\": 6, \"year\": 2025}"
```

Or with Python:
```python
import requests
r = requests.post("http://127.0.0.1:8000/predict-price", json={
    "commodity": "tomato",
    "district": "Hyderabad",
    "month": 6,
    "year": 2025
})
print(r.json())
```

### Blockers (minor)
1. **sklearn version warning** — the model was pickled with sklearn 1.2.2 but the installed version is 1.6.1. Non-fatal but prints warnings. Fix: `pip install scikit-learn==1.2.2` or re-export the model.
2. **Some crop/district combos return 404** — data coverage gap in the training view, not a code issue.

---

## Files Created

| File | Description |
|---|---|
| `runtime_run_report.md` | This file — full runtime execution report |
| `sample_forecast_output.md` | Detailed forecast inputs, raw outputs, and interpretations |
| `runtime_commands_log.txt` | All commands executed |
| `runtime_errors_log.txt` | All errors and warnings encountered |
| `forecast_raw_outputs.json` | Machine-readable JSON of all API responses |
