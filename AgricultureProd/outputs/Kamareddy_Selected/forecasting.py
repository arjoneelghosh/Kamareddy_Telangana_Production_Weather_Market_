import json
from pathlib import Path

import numpy as np
import pandas as pd
import joblib

# ----------------------------
# Paths (your folder structure)
# ----------------------------
BASE_DIR = Path(r"C:\Users\footb\Desktop\AgriFore\AgricultureProd\outputs\Kamareddy_Selected")
DATA_PATH = BASE_DIR / "model1_dataset.csv"
META_PATH = BASE_DIR / "metadata_kamareddy.json"

def find_model_pkl():
    # Your folder listing doesn't show the .pkl inside Kamareddy_Selected,
    # so check common locations + fallback to recursive search.
    candidates = [
        BASE_DIR / "district_model_kamareddy.pkl",
        BASE_DIR.parent / "district_model_kamareddy.pkl",
    ]
    for c in candidates:
        if c.exists():
            return c

    for c in BASE_DIR.parent.rglob("*.pkl"):
        if "kamareddy" in c.name.lower():
            return c

    return None

MODEL_PATH = find_model_pkl()
if MODEL_PATH is None:
    raise FileNotFoundError(
        "Could not find district_model_kamareddy.pkl.\n"
        f"Checked:\n  - {BASE_DIR}\n  - {BASE_DIR.parent}\n"
        "And searched recursively under outputs for any *.pkl containing 'kamareddy'.\n"
        "Place the model file in Kamareddy_Selected or outputs, then rerun."
    )

# ----------------------------
# Load metadata and enforce versions
# ----------------------------
meta = json.loads(META_PATH.read_text(encoding="utf-8"))
expected = meta.get("env_versions", {})

def _ver(modname):
    mod = __import__(modname)
    return getattr(mod, "__version__", "unknown")

runtime = {
    "python": None,
    "numpy": _ver("numpy"),
    "pandas": _ver("pandas"),
    "sklearn": _ver("sklearn"),
    "xgboost": _ver("xgboost"),
    "joblib": _ver("joblib"),
}

# Hard fail if sklearn major/minor doesn't match training
# (prevents ColumnTransformer internal-attr crashes)
exp_sklearn = expected.get("sklearn")
if exp_sklearn and runtime["sklearn"] != exp_sklearn:
    raise RuntimeError(
        f"Version mismatch: model was trained with sklearn={exp_sklearn}, "
        f"but you are running sklearn={runtime['sklearn']}.\n"
        "Create/activate a venv and install the training versions:\n"
        "  numpy==1.26.4 pandas==2.3.3 scikit-learn==1.4.1.post1 joblib==1.4.2 xgboost==3.2.0"
    )

# ----------------------------
# Load artifacts
# ----------------------------
df = pd.read_csv(DATA_PATH)
pipe = joblib.load(MODEL_PATH)

# ----------------------------
# Scenario configuration
# ----------------------------
district = "kamareddy"
season = "rabi"  # Feb–Mar context maps to Rabi in your season-level model

# Filters used in training (from metadata)
subset = df.copy()
subset["district"] = subset["district"].astype(str).str.lower()

hist = subset[
    (subset["district"] == district)
    & (subset["season_norm"] == season)
    & (subset["dq_weather_missing"] == False)
    & (subset["dq_weather_incomplete"] == False)
    & (subset["yield_per_acre_proxy"] > 0)
].copy()

if hist.empty:
    raise ValueError(
        f"No historical rows found for district='{district}', season='{season}' after filters. "
        "Check district/season values in model1_dataset.csv."
    )

# Choose 3 crops automatically (most frequent)
top_crops = hist["crop_name"].value_counts().head(3).index.tolist()

# Historical means for scenario baselines
rain_mean = float(hist["rain_total_mm"].mean())
rain_days_mean = float(hist["rainy_days_total"].mean())
hum_min_mean = float(hist["hum_min_avg"].mean())
hum_max_mean = float(hist["hum_max_avg"].mean())
avg_mandals_mean = float(hist["avg_mandals_reporting"].mean())
days_covered_mean = float(hist["days_covered"].mean())
months_covered_mean = float(hist["months_covered"].mean())

def build_rows(mult: float, scenario_label: str):
    rain = rain_mean * mult
    rainy_days = max(rain_days_mean * mult, 1.0)

    rows = []
    for crop in top_crops:
        rows.append({
            # categorical
            "district": district,
            "crop_name": crop,
            "season_norm": season,

            # numeric (base)
            "rain_total_mm": rain,
            "rainy_days_total": rainy_days,
            "hum_min_avg": hum_min_mean,
            "hum_max_avg": hum_max_mean,
            "avg_mandals_reporting": avg_mandals_mean,
            "days_covered": days_covered_mean,
            "months_covered": months_covered_mean,

            # numeric (derived expected by training)
            "rain_intensity": rain / rainy_days,
            "humid_range": hum_max_mean - hum_min_mean,
            "rain_anom_mm": rain - rain_mean,
            "rain_dev_pct": ((rain - rain_mean) / rain_mean) * 100.0 if rain_mean != 0 else 0.0,

            "scenario": scenario_label,
            "rain_mult": mult,
        })
    return rows 

rows = []
rows += build_rows(1.0, "Normal (historical mean)")
rows += build_rows(0.8, "Dry (-20% rainfall)")
rows += build_rows(1.2, "Wet (+20% rainfall)")

scen_df = pd.DataFrame(rows)

# Use feature lists from metadata to build X in the expected shape
num_feats = meta["features"]["numeric"]
cat_feats = meta["features"]["categorical"]
X = scen_df[cat_feats + num_feats].copy()

# Predict
scen_df["pred_yield_per_acre_proxy"] = pipe.predict(X)

# Delta vs normal by crop
normal_map = scen_df[scen_df["scenario"].str.startswith("Normal")].set_index("crop_name")["pred_yield_per_acre_proxy"].to_dict()
scen_df["delta_vs_normal"] = scen_df.apply(lambda r: r["pred_yield_per_acre_proxy"] - normal_map.get(r["crop_name"], np.nan), axis=1)
scen_df["pct_change_vs_normal"] = scen_df.apply(
    lambda r: (r["delta_vs_normal"] / normal_map[r["crop_name"]] * 100.0)
    if r["crop_name"] in normal_map and normal_map[r["crop_name"]] != 0 else np.nan,
    axis=1
)

# Print
display_cols = [
    "scenario", "crop_name",
    "rain_total_mm", "rainy_days_total",
    "pred_yield_per_acre_proxy",
    "delta_vs_normal", "pct_change_vs_normal"
]
print("\nKamareddy | Rabi | Scenario Predictions (2026 context)\n")
print(
    scen_df[display_cols]
    .sort_values(["crop_name", "scenario"])
    .assign(
        rain_total_mm=lambda d: d["rain_total_mm"].round(2),
        rainy_days_total=lambda d: d["rainy_days_total"].round(2),
        pred_yield_per_acre_proxy=lambda d: d["pred_yield_per_acre_proxy"].round(3),
        delta_vs_normal=lambda d: d["delta_vs_normal"].round(3),
        pct_change_vs_normal=lambda d: d["pct_change_vs_normal"].round(2),
    )
    .to_string(index=False)
)

# Save for later comparison
out_csv = BASE_DIR / "scenario_predictions_kamareddy_rabi_2026.csv"
scen_df.to_csv(out_csv, index=False)
print(f"\nSaved: {out_csv}")
print(f"Model used: {MODEL_PATH}")