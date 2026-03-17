# AgriFore — Sample Forecast Output

> **Date:** 2026-03-17  
> **Method:** Live backend API (`POST /predict-price`)  
> **Model used:** M2 Base XGBoost (from `aaaFinalModels/model2/m2_base_model.pkl`)  
> **Execution type:** Fully working — real model, real database, real API

---

## Forecast 1 — Tomato in Hyderabad (June 2025)

| Field | Value |
|---|---|
| **Endpoint** | `POST http://127.0.0.1:8000/predict-price` |
| **Input payload** | `{"commodity": "tomato", "district": "Hyderabad", "month": 6, "year": 2025}` |
| **HTTP Status** | `200 OK` |
| **Prediction strategy** | Strategy 1 — M2 Base XGBoost model with real feature data |

### Raw output
```json
{
  "commodity": "Tomato",
  "predicted_price": 2467,
  "market": null,
  "district": "Hyderabad",
  "confidence": 0.85
}
```

### Interpretation
The M2 XGBoost model predicts **₹2,467 per quintal** for tomato in Hyderabad district during June 2025. Confidence of **0.85** indicates the prediction came from the real trained model (Strategy 1), not a fallback. June is typically a summer month with moderate tomato supply, so a price above the annual average (~₹1,100) is plausible due to off-season supply constraints.

---

## Forecast 2 — Cotton Statewide (October 2025)

| Field | Value |
|---|---|
| **Endpoint** | `POST http://127.0.0.1:8000/predict-price` |
| **Input payload** | `{"commodity": "cotton", "month": 10, "year": 2025}` |
| **HTTP Status** | `200 OK` |
| **Prediction strategy** | Strategy 1 — M2 Base XGBoost model |

### Raw output
```json
{
  "commodity": "Cotton",
  "predicted_price": 7347,
  "market": null,
  "district": null,
  "confidence": 0.85
}
```

### Interpretation
Cotton is predicted at **₹7,347 per quintal** statewide for October 2025. This is the harvest/arrival season for cotton in Telangana. The price aligns with the range typical for Kharif cotton arrivals. Confidence 0.85 = real XGBoost model prediction.

---

## Forecast 3 — Paddy in Warangal Market (December 2025)

| Field | Value |
|---|---|
| **Endpoint** | `POST http://127.0.0.1:8000/predict-price` |
| **Input payload** | `{"commodity": "paddy", "market": "Warangal", "month": 12, "year": 2025}` |
| **HTTP Status** | `200 OK` |
| **Prediction strategy** | Strategy 1 — M2 Base XGBoost model |

### Raw output
```json
{
  "commodity": "Paddy",
  "predicted_price": 1637,
  "market": "Warangal",
  "district": null,
  "confidence": 0.85
}
```

### Interpretation
Paddy in Warangal market is forecast at **₹1,637 per quintal** for December 2025. Warangal is a major rice-producing region, and December falls in the Kharif procurement window. The price is consistent with MSP trends for paddy in Telangana (~₹2,000–2,200 recent MSP, but market modal prices tend to be lower). Real model prediction.

---

## Forecast 4 — Onions in Siddipet (March 2026) ❌

| Field | Value |
|---|---|
| **Endpoint** | `POST http://127.0.0.1:8000/predict-price` |
| **Input payload** | `{"commodity": "onions", "district": "Siddipet", "month": 3, "year": 2026}` |
| **HTTP Status** | `404 Not Found` |
| **Prediction strategy** | All strategies failed (data gap) |

### Raw output
```json
{
  "detail": "No data available for commodity 'onions'"
}
```

### Interpretation
The onions/Siddipet combination doesn't have enough records in the model's training view (`v_model2_base_dataset`) for any of the three prediction strategies. This is a **data coverage gap**, not a code error. Onions may be traded in Siddipet district but under a different crop name variant or with insufficient historical records for the model view.

---

## Forecast 5 — Maize in Karimnagar (August 2025)

| Field | Value |
|---|---|
| **Endpoint** | `POST http://127.0.0.1:8000/predict-price` |
| **Input payload** | `{"commodity": "maize", "district": "Karimnagar", "month": 8, "year": 2025}` |
| **HTTP Status** | `200 OK` |
| **Prediction strategy** | Strategy 1 — M2 Base XGBoost model |

### Raw output
```json
{
  "commodity": "Maize",
  "predicted_price": 2292,
  "market": null,
  "district": "Karimnagar",
  "confidence": 0.85
}
```

### Interpretation
Maize in Karimnagar is predicted at **₹2,292 per quintal** for August 2025. August is monsoon season, typically when early Kharif maize starts arriving. The price aligns with recent maize market averages (~₹2,259 based on top-commodities endpoint). Real model prediction with 0.85 confidence.

---

## Summary

| Crop | Location | Month/Year | Predicted Price (₹/quintal) | Confidence | Strategy | Status |
|---|---|---|---|---|---|---|
| Tomato | Hyderabad | Jun 2025 | 2,467 | 0.85 | XGBoost model | ✅ |
| Cotton | Statewide | Oct 2025 | 7,347 | 0.85 | XGBoost model | ✅ |
| Paddy | Warangal | Dec 2025 | 1,637 | 0.85 | XGBoost model | ✅ |
| Onions | Siddipet | Mar 2026 | — | — | All failed | ❌ |
| Maize | Karimnagar | Aug 2025 | 2,292 | 0.85 | XGBoost model | ✅ |

**Model used:** `aaaFinalModels/model2/m2_base_model.pkl` (M2 Base XGBoost, ~2.6 MB)  
**Database used:** `AgricultureProd/agri_validation.duckdb`  
**Fallback triggered:** No — all successful predictions came from the real trained model (Strategy 1)  
**This was NOT a simulation.** These are real predictions from the live backend API using the real trained model.
