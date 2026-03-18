"""
Telangana AgriForecaster — FastAPI Backend Server

Serves all endpoints expected by the Next.js frontend.
Connects to DuckDB for data queries and M2 XGBoost for price prediction.

Run:  uvicorn api.server:app --reload --port 8000
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Optional

import duckdb
import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
ROOT = Path(__file__).resolve().parent.parent
DB_PATH = ROOT / "AgricultureProd" / "agri_validation.duckdb"
MODELS_DIR = ROOT / "aaaFinalModels"
PREDICTIONS_CSV = MODELS_DIR / "model2" / "m2_base_predictions_2024.csv"

# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s  %(levelname)s  %(message)s")
log = logging.getLogger("agri-api")

# ---------------------------------------------------------------------------
# FastAPI app
# ---------------------------------------------------------------------------
app = FastAPI(
    title="Telangana AgriForecaster API",
    description="Backend for the AI Agricultural Market Intelligence Dashboard",
    version="0.1.0",
)

# CORS — allow all origins for public app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
def get_db() -> duckdb.DuckDBPyConnection:
    """Return a read-only DuckDB connection."""
    return duckdb.connect(str(DB_PATH), read_only=True)


# Month name helper
MONTH_NAMES = [
    "Jan", "Feb", "Mar", "Apr", "May", "Jun",
    "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",
]


# ---------------------------------------------------------------------------
# Model loading (at startup)
# ---------------------------------------------------------------------------
m2_pipeline = None
m2_features: list[str] = []

try:
    m2_bundle = joblib.load(MODELS_DIR / "model2" / "m2_base_model.pkl")
    m2_pipeline = m2_bundle["pipeline"]
    m2_features = m2_bundle["features"]
    log.info("Loaded M2 base model  (%d features)", len(m2_features))
except Exception as e:
    log.warning("Could not load M2 base model: %s", e)

# Pre-load 2024 predictions for fast fallback
_pred_2024: pd.DataFrame | None = None
try:
    _pred_2024 = pd.read_csv(PREDICTIONS_CSV, parse_dates=["month_start"])
    log.info("Loaded 2024 predictions  (%d rows)", len(_pred_2024))
except Exception as e:
    log.warning("2024 predictions CSV not found: %s", e)


# =====================================================================
#  REFERENCE DATA ENDPOINTS
# =====================================================================

@app.get("/commodities", tags=["Reference Data"])
def get_commodities():
    """List all available commodities."""
    con = get_db()
    try:
        df = con.sql("""
            SELECT DISTINCT crop_name
            FROM t_market_monthly
            WHERE crop_name IS NOT NULL
            ORDER BY crop_name
        """).df()
    finally:
        con.close()

    results = []
    for _, row in df.iterrows():
        name = str(row["crop_name"])
        # Heuristic category classification
        vegetables = {
            "tomato", "onions", "potato", "brinjal", "cabbage", "cauliflower",
            "carrot", "green chillies", "ladys finger", "bitter gourd",
            "bottle gourd", "capsicum", "cucumber", "drumstick", "pumpkin",
            "ribbed gourd", "snake gourd", "cluster beans", "french beans",
            "field beans", "beet root", "radish", "sweet potato", "yam",
            "lobha", "kheera", "donda", "chowchow", "green onion",
            "green peas", "colacasio(arvi)",
        }
        fruits = {
            "banana", "mango", "orange", "grapes", "papaya", "guava",
            "pomegrenates", "sapota", "mosambi", "apple", "pine apple",
            "water melon", "musk melon", "custard apple", "ber",
            "amla", "lemon", "green mangos", "nashpati(pear)",
        }
        grains = {
            "paddy", "maize", "jowar", "wheat", "ragi", "bazra",
        }
        pulses = {
            "red gram", "green gram", "bengal gram", "black gram",
            "cowpea", "horse gram",
        }
        oilseeds = {
            "groundnut pods", "soyabean", "gingelly", "castor",
            "sunflower", "safflower", "mustard",
        }
        cash_crops = {"cotton", "tumeric", "chillies(dry)", "coriander", "tamarind"}

        lower = name.lower()
        if lower in vegetables:
            cat = "Vegetable"
        elif lower in fruits:
            cat = "Fruit"
        elif lower in grains:
            cat = "Grain"
        elif lower in pulses:
            cat = "Pulse"
        elif lower in oilseeds:
            cat = "Oilseed"
        elif lower in cash_crops:
            cat = "Cash Crop"
        else:
            cat = "Other"

        results.append({
            "id": name.lower().replace(" ", "_"),
            "name": name.title(),
            "category": cat,
        })
    return results


@app.get("/markets", tags=["Reference Data"])
def get_markets():
    """List all AMC markets."""
    con = get_db()
    try:
        df = con.sql("""
            SELECT DISTINCT amc, district
            FROM t_market_monthly
            WHERE amc IS NOT NULL
            ORDER BY amc
        """).df()
    finally:
        con.close()

    return [
        {
            "id": row["amc"].lower().replace(" ", "_"),
            "name": row["amc"].title(),
            "district": row["district"].title(),
        }
        for _, row in df.iterrows()
    ]


@app.get("/districts", tags=["Reference Data"])
def get_districts():
    """List all districts."""
    con = get_db()
    try:
        df = con.sql("""
            SELECT DISTINCT district
            FROM t_market_monthly
            WHERE district IS NOT NULL
            ORDER BY district
        """).df()
    finally:
        con.close()

    return [
        {
            "id": row["district"].lower().replace(" ", "_"),
            "name": row["district"].title(),
            "state": "Telangana",
        }
        for _, row in df.iterrows()
    ]


# =====================================================================
#  DASHBOARD ENDPOINTS
# =====================================================================

@app.get("/market-overview", tags=["Dashboard"])
def market_overview():
    """Dashboard summary statistics."""
    con = get_db()
    try:
        stats = con.sql("""
            SELECT
                COUNT(DISTINCT amc)        AS total_markets,
                COUNT(DISTINCT crop_name)  AS active_commodities,
                AVG(modal_price_mean)      AS avg_price,
                SUM(arrivals_sum)          AS total_volume
            FROM t_market_monthly
        """).df().iloc[0]

        # Price change: latest available year vs previous year
        change_df = con.sql("""
            WITH years AS (
                SELECT DISTINCT EXTRACT(YEAR FROM month_start) AS yr
                FROM t_market_monthly
                ORDER BY yr DESC
                LIMIT 2
            ),
            latest AS (
                SELECT AVG(modal_price_mean) AS p
                FROM t_market_monthly
                WHERE EXTRACT(YEAR FROM month_start) = (SELECT MAX(yr) FROM years)
            ),
            prior AS (
                SELECT AVG(modal_price_mean) AS p
                FROM t_market_monthly
                WHERE EXTRACT(YEAR FROM month_start) = (SELECT MIN(yr) FROM years)
            )
            SELECT 100.0 * (l.p - p.p) / NULLIF(p.p, 0) AS pct
            FROM latest l, prior p
        """).df()
        price_change = float(change_df.iloc[0]["pct"]) if not change_df.empty else 0.0
    finally:
        con.close()

    return {
        "totalMarkets": int(stats["total_markets"]),
        "activeCommodities": int(stats["active_commodities"]),
        "avgPrice": round(float(stats["avg_price"]), 0),
        "totalVolume": round(float(stats["total_volume"]), 0),
        "priceChange": round(price_change, 1),
    }


@app.get("/top-commodities", tags=["Dashboard"])
def top_commodities():
    """Top commodities by trading volume."""
    con = get_db()
    try:
        df = con.sql("""
            WITH latest_year AS (
                SELECT MAX(EXTRACT(YEAR FROM month_start)) AS yr FROM t_market_monthly
            ),
            current AS (
                SELECT crop_name,
                       AVG(modal_price_mean) AS price,
                       SUM(arrivals_sum)     AS volume
                FROM t_market_monthly
                WHERE EXTRACT(YEAR FROM month_start) = (SELECT yr FROM latest_year)
                GROUP BY crop_name
            ),
            previous AS (
                SELECT crop_name,
                       AVG(modal_price_mean) AS price
                FROM t_market_monthly
                WHERE EXTRACT(YEAR FROM month_start) = (SELECT yr - 1 FROM latest_year)
                GROUP BY crop_name
            )
            SELECT c.crop_name,
                   c.price,
                   c.volume,
                   COALESCE(100.0 * (c.price - p.price) / NULLIF(p.price, 0), 0) AS change_pct
            FROM current c
            LEFT JOIN previous p ON c.crop_name = p.crop_name
            ORDER BY c.volume DESC
            LIMIT 8
        """).df()
    finally:
        con.close()

    return [
        {
            "name": row["crop_name"].title(),
            "price": round(float(row["price"])),
            "change": round(float(row["change_pct"]), 1),
            "volume": round(float(row["volume"])),
        }
        for _, row in df.iterrows()
    ]


@app.get("/market-clusters", tags=["Dashboard"])
def market_clusters():
    """Regional market cluster overview."""
    con = get_db()
    try:
        df = con.sql("""
            SELECT district,
                   COUNT(DISTINCT amc) AS markets,
                   AVG(modal_price_mean) AS avg_price
            FROM t_market_monthly
            GROUP BY district
            ORDER BY markets DESC
            LIMIT 6
        """).df()
    finally:
        con.close()

    return [
        {
            "name": row["district"].title(),
            "markets": int(row["markets"]),
            "avgPrice": round(float(row["avg_price"])),
            "region": row["district"].title() + ", Telangana",
        }
        for _, row in df.iterrows()
    ]


# =====================================================================
#  CHART DATA ENDPOINTS
# =====================================================================

@app.get("/price-trends", tags=["Charts"])
def price_trends(commodity: Optional[str] = Query(default=None)):
    """
    Multi-commodity monthly price trends.
    If commodity is specified, return only that one.
    Otherwise returns top 3 (Tomato, Paddy, Cotton).
    """
    if commodity:
        crops = [commodity.lower()]
    else:
        crops = ["tomato", "paddy", "cotton"]

    con = get_db()
    try:
        dfs = []
        for crop in crops:
            df = con.sql(f"""
                SELECT month_start AS date,
                       AVG(modal_price_mean) AS price
                FROM t_market_monthly
                WHERE LOWER(crop_name) = '{crop}'
                GROUP BY month_start
                ORDER BY month_start
            """).df()
            if not df.empty:
                title = crop.title()
                df = df.rename(columns={"price": title})
                dfs.append(df)
    finally:
        con.close()

    if not dfs:
        return []

    # Merge all frames on date
    merged = dfs[0]
    for df in dfs[1:]:
        merged = merged.merge(df, on="date", how="outer")
    merged = merged.sort_values("date")
    merged["date"] = merged["date"].astype(str)

    # Build records manually, skipping NaN values for JSON compatibility
    records = []
    for _, row in merged.iterrows():
        record = {}
        for col in merged.columns:
            val = row[col]
            if isinstance(val, float) and (np.isnan(val) or np.isinf(val)):
                continue  # skip NaN — Recharts handles missing keys gracefully
            record[col] = val
        records.append(record)

    return records


@app.get("/seasonal-data", tags=["Charts"])
def seasonal_data(commodity: Optional[str] = Query(default="tomato")):
    """Monthly seasonal pattern for a commodity."""
    con = get_db()
    try:
        df = con.sql(f"""
            SELECT EXTRACT(MONTH FROM month_start) AS month_num,
                   AVG(modal_price_mean) AS avg_price,
                   SUM(arrivals_sum) AS volume
            FROM t_market_monthly
            WHERE LOWER(crop_name) = LOWER('{commodity}')
            GROUP BY month_num
            ORDER BY month_num
        """).df()
    finally:
        con.close()

    if df.empty:
        return []

    return [
        {
            "month": MONTH_NAMES[int(row["month_num"]) - 1],
            "avgPrice": round(float(row["avg_price"])),
            "volume": round(float(row["volume"])),
        }
        for _, row in df.iterrows()
    ]


@app.get("/arrival-data", tags=["Charts"])
def arrival_data(commodity: Optional[str] = Query(default="tomato")):
    """Monthly arrival volume vs price for a commodity."""
    con = get_db()
    try:
        df = con.sql(f"""
            SELECT EXTRACT(MONTH FROM month_start) AS month_num,
                   SUM(arrivals_sum) AS arrival,
                   AVG(modal_price_mean) AS price
            FROM t_market_monthly
            WHERE LOWER(crop_name) = LOWER('{commodity}')
            GROUP BY month_num
            ORDER BY month_num
        """).df()
    finally:
        con.close()

    if df.empty:
        return []

    return [
        {
            "month": MONTH_NAMES[int(row["month_num"]) - 1],
            "arrival": round(float(row["arrival"])),
            "price": round(float(row["price"])),
        }
        for _, row in df.iterrows()
    ]


# =====================================================================
#  PREDICTION ENDPOINT
# =====================================================================

class PredictPriceRequest(BaseModel):
    commodity: str
    market: Optional[str] = None
    district: Optional[str] = None
    month: Optional[int] = None
    year: Optional[int] = None


@app.post("/predict-price", tags=["Prediction"])
def predict_price(req: PredictPriceRequest):
    """
    Predict crop price using the M2 Base XGBoost model.

    Falls back to historical average from 2024 predictions CSV
    if the model cannot produce a prediction.
    """
    target_month = req.month or pd.Timestamp.now().month
    target_year = req.year or pd.Timestamp.now().year
    crop = req.commodity.lower()

    # ------------------------------------------------------------------
    # Strategy 1: Use the M2 Base XGBoost model with real feature data
    # ------------------------------------------------------------------
    if m2_pipeline is not None:
        try:
            prediction = _predict_with_model(
                crop=crop,
                district=req.district,
                market=req.market,
                month=target_month,
                year=target_year,
            )
            if prediction is not None:
                return {
                    "commodity": req.commodity.title(),
                    "predicted_price": round(float(prediction)),
                    "market": req.market.title() if req.market else None,
                    "district": req.district.title() if req.district else None,
                    "confidence": 0.85,
                }
        except Exception as e:
            log.warning("Model prediction failed, falling back: %s", e)

    # ------------------------------------------------------------------
    # Strategy 2: Lookup from pre-computed 2024 predictions
    # ------------------------------------------------------------------
    if _pred_2024 is not None:
        try:
            mask = _pred_2024["crop_name"].str.lower() == crop
            if req.district:
                mask &= _pred_2024["district"].str.lower() == req.district.lower()
            if req.market:
                amc_col = "amc" if "amc" in _pred_2024.columns else "market"
                if amc_col in _pred_2024.columns:
                    mask &= _pred_2024[amc_col].str.lower() == req.market.lower()

            subset = _pred_2024[mask]
            if not subset.empty:
                # Use the prediction column (or actual as fallback)
                pred_col = "base_pred" if "base_pred" in subset.columns else "modal_price_mean"
                avg_pred = subset[pred_col].mean()
                if np.isfinite(avg_pred) and avg_pred < 1e10:
                    return {
                        "commodity": req.commodity.title(),
                        "predicted_price": round(float(avg_pred)),
                        "market": req.market.title() if req.market else None,
                        "district": req.district.title() if req.district else None,
                        "confidence": 0.7,
                    }
        except Exception as e:
            log.warning("2024 predictions lookup failed: %s", e)

    # ------------------------------------------------------------------
    # Strategy 3: Historical average from DuckDB
    # ------------------------------------------------------------------
    con = get_db()
    try:
        filter_clause = f"LOWER(crop_name) = '{crop}'"
        if req.district:
            filter_clause += f" AND LOWER(district) = '{req.district.lower()}'"
        if req.market:
            filter_clause += f" AND LOWER(amc) = '{req.market.lower()}'"

        df = con.sql(f"""
            SELECT AVG(modal_price_mean) AS avg_price,
                   COUNT(*) AS n
            FROM t_market_monthly
            WHERE {filter_clause}
              AND EXTRACT(MONTH FROM month_start) = {target_month}
        """).df()
    finally:
        con.close()

    if not df.empty and df.iloc[0]["n"] > 0:
        avg_price = float(df.iloc[0]["avg_price"])
        return {
            "commodity": req.commodity.title(),
            "predicted_price": round(avg_price),
            "market": req.market.title() if req.market else None,
            "district": req.district.title() if req.district else None,
            "confidence": 0.5,
        }

    raise HTTPException(
        status_code=404,
        detail=f"No data available for commodity '{req.commodity}'"
    )


def _predict_with_model(
    crop: str,
    district: str | None,
    market: str | None,
    month: int,
    year: int,
) -> float | None:
    """
    Build a feature vector from DuckDB history and run M2 Base XGBoost.
    Returns predicted price or None if not enough data.
    """
    con = get_db()
    try:
        # Build filter
        where = f"LOWER(crop_name) = '{crop}'"
        if district:
            where += f" AND LOWER(district) = '{district.lower()}'"
        if market:
            where += f" AND LOWER(amc) = '{market.lower()}'"

        # Get the latest 12 months of data for lag features
        hist = con.sql(f"""
            SELECT *
            FROM v_model2_base_dataset
            WHERE {where}
            ORDER BY month_start DESC
            LIMIT 12
        """).df()
    finally:
        con.close()

    if hist.empty or len(hist) < 2:
        return None

    # Build the feature row from latest record
    latest = hist.iloc[0].to_dict()

    # Time features
    latest["month_num"] = month
    latest["month_sin"] = np.sin(2 * np.pi * month / 12)
    latest["month_cos"] = np.cos(2 * np.pi * month / 12)

    # Lag features (lag_1 = most recent, lag_2 = 2nd most recent, etc.)
    lag_map = {1: 0, 2: 1, 3: 2, 6: 5, 12: 11}
    for lag, idx in lag_map.items():
        if idx < len(hist):
            latest[f"lag_{lag}"] = hist.iloc[idx]["modal_price_mean"]
        else:
            latest[f"lag_{lag}"] = hist.iloc[-1]["modal_price_mean"]

    # Rolling features from lag_1 history
    prices = hist["modal_price_mean"].values
    latest["roll_mean_3"] = float(np.mean(prices[:min(3, len(prices))]))
    latest["roll_mean_6"] = float(np.mean(prices[:min(6, len(prices))]))

    # Build DataFrame with all required features
    feat_df = pd.DataFrame([latest])
    for f in m2_features:
        if f not in feat_df.columns:
            feat_df[f] = np.nan

    # Predict
    pred = m2_pipeline.predict(feat_df[m2_features])[0]

    # Sanity check
    if not np.isfinite(pred) or pred < 0 or pred > 1e8:
        return None

    return pred


# =====================================================================
#  ASK-AGENT ENDPOINT (stub)
# =====================================================================

class AskAgentRequest(BaseModel):
    query: str


@app.post("/ask-agent", tags=["Agent"])
def ask_agent(req: AskAgentRequest):
    """
    AI Q&A about agricultural markets.
    Currently a stub — returns a helpful canned response.
    """
    q = req.query.lower()

    # Basic keyword matching for demo
    if "price" in q and any(crop in q for crop in ["tomato", "onion", "potato", "paddy", "cotton"]):
        return {
            "answer": (
                "Based on our analysis of Telangana market data, crop prices are "
                "influenced by seasonal supply patterns, weather conditions, and "
                "arrival volumes. Use the Price Prediction page for specific forecasts."
            ),
            "sources": ["t_market_monthly", "m2_base_model"],
        }
    elif "weather" in q or "rain" in q:
        return {
            "answer": (
                "Weather data (daily rainfall and humidity) is integrated into our "
                "models. Rainfall anomalies are key drivers of yield variation. "
                "The data covers 2018–2025 across all Telangana districts."
            ),
            "sources": ["t_weather_district_day", "t_weather_district_season"],
        }
    elif "yield" in q or "production" in q:
        return {
            "answer": (
                "Model 1 (Weather→Yield) currently covers Kamareddy district with "
                "R²=0.77. It uses seasonal rainfall, humidity, and rain anomaly "
                "features to predict horticulture crop yields."
            ),
            "sources": ["t_model1_dataset", "district_model_kamareddy.pkl"],
        }
    else:
        return {
            "answer": (
                "I can help with questions about crop prices, weather impact on "
                "yields, seasonal patterns, and market trends in Telangana. "
                "Try asking about a specific crop or topic!"
            ),
            "sources": [],
        }


# =====================================================================
#  HEALTH CHECK
# =====================================================================

@app.get("/health", tags=["System"])
def health_check():
    """Health check endpoint."""
    db_ok = DB_PATH.exists()
    model_ok = m2_pipeline is not None

    return {
        "status": "ok" if (db_ok and model_ok) else "degraded",
        "database": "connected" if db_ok else "missing",
        "model_m2_base": "loaded" if model_ok else "not loaded",
        "predictions_2024": "loaded" if _pred_2024 is not None else "not loaded",
    }


# =====================================================================
#  Startup / shutdown events
# =====================================================================

@app.on_event("startup")
async def startup():
    log.info("=" * 50)
    log.info("AgriForecaster API starting on http://localhost:8000")
    log.info("  Database: %s  (exists=%s)", DB_PATH.name, DB_PATH.exists())
    log.info("  M2 Base model: %s", "loaded" if m2_pipeline else "NOT loaded")
    log.info("  Swagger docs: http://localhost:8000/docs")
    log.info("=" * 50)
