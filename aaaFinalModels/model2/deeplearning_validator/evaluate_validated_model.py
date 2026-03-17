"""
Evaluate the Validated Price Model against the market dataset.

Compares this model against the existing M2 base XGBoost model
using the same test split (2024 data) for an apples-to-apples comparison.

Outputs:
  - Model structure inspection
  - R², RMSE, MAE metrics on 2024 test data
  - Per-district and per-crop accuracy breakdown
  - Comparison table vs M2 base XGBoost
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

BASE_DIR = Path(__file__).resolve().parent
FINAL_MODELS_DIR = BASE_DIR.parent  # aaaFinalModels/model2/


def metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    mask = np.isfinite(y_true) & np.isfinite(y_pred)
    y_true, y_pred = y_true[mask], y_pred[mask]
    if len(y_true) == 0:
        return {"r2": float("nan"), "rmse": float("nan"), "mae": float("nan"), "n": 0}
    return {
        "r2": float(r2_score(y_true, y_pred)),
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "n": len(y_true),
    }


def load_validated_model():
    """Load and inspect the validated price model."""
    model_path = BASE_DIR / "validated_price_model.pkl"
    if not model_path.exists():
        sys.exit(f"Model not found: {model_path}")

    bundle = joblib.load(model_path)
    return bundle


def load_data() -> pd.DataFrame:
    """Load the clean market dataset."""
    csv_path = BASE_DIR / "clean_market_dataset.csv"
    if not csv_path.exists():
        sys.exit(f"Dataset not found: {csv_path}")

    df = pd.read_csv(csv_path)
    df["ddate"] = pd.to_datetime(df["ddate"], errors="coerce")
    for col in ["arrivals", "minimum", "maximum", "model"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df = df.dropna(subset=["ddate", "model"])
    df = df[df["model"] > 0].copy()
    return df


def load_m2_base_predictions() -> pd.DataFrame | None:
    """Load the M2 base XGBoost predictions for comparison."""
    pred_path = FINAL_MODELS_DIR / "m2_base_predictions_2024.csv"
    if not pred_path.exists():
        return None
    return pd.read_csv(pred_path, parse_dates=["month_start"])


def aggregate_monthly(df: pd.DataFrame) -> pd.DataFrame:
    """Aggregate daily market data to monthly for fair comparison."""
    df["month_start"] = df["ddate"].dt.to_period("M").dt.to_timestamp()
    monthly = (
        df.groupby(["month_start", "district", "amcname", "commname"])
        .agg(
            modal_price_mean=("model", "mean"),
            arrivals_sum=("arrivals", "sum"),
            n_days=("model", "count"),
            min_price=("minimum", "mean"),
            max_price=("maximum", "mean"),
        )
        .reset_index()
    )
    return monthly


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    """Add lag + rolling features for model input."""
    out = df.sort_values(["district", "amcname", "commname", "month_start"]).copy()
    grp = out.groupby(["district", "amcname", "commname"], dropna=False)

    for lag in [1, 2, 3, 6, 12]:
        out[f"lag_{lag}"] = grp["modal_price_mean"].shift(lag)

    lag1 = grp["modal_price_mean"].shift(1)
    out["roll_mean_3"] = lag1.groupby(
        [out["district"], out["amcname"], out["commname"]]
    ).transform(lambda s: s.rolling(3, min_periods=2).mean())
    out["roll_mean_6"] = lag1.groupby(
        [out["district"], out["amcname"], out["commname"]]
    ).transform(lambda s: s.rolling(6, min_periods=3).mean())

    out["month_num"] = out["month_start"].dt.month
    out["month_sin"] = np.sin(2 * np.pi * out["month_num"] / 12)
    out["month_cos"] = np.cos(2 * np.pi * out["month_num"] / 12)
    return out


def inspect_model(bundle) -> dict:
    """Inspect what's inside the model bundle."""
    info = {"type": str(type(bundle))}

    if isinstance(bundle, dict):
        info["keys"] = list(bundle.keys())
        for k, v in bundle.items():
            info[f"key_{k}_type"] = str(type(v))
            if hasattr(v, "n_features_in_"):
                info[f"key_{k}_n_features"] = v.n_features_in_
            if hasattr(v, "feature_names_in_"):
                info[f"key_{k}_feature_names"] = list(v.feature_names_in_)
            if hasattr(v, "named_steps"):
                info[f"key_{k}_steps"] = list(v.named_steps.keys())
    elif hasattr(bundle, "predict"):
        info["is_estimator"] = True
        if hasattr(bundle, "n_features_in_"):
            info["n_features"] = bundle.n_features_in_
        if hasattr(bundle, "feature_names_in_"):
            info["feature_names"] = list(bundle.feature_names_in_)
        if hasattr(bundle, "named_steps"):
            info["steps"] = list(bundle.named_steps.keys())
    else:
        info["note"] = "Unknown structure"

    return info


def try_predict(bundle, df: pd.DataFrame) -> np.ndarray | None:
    """Attempt to generate predictions from the model bundle."""

    # Case 1: dict with pipeline key
    if isinstance(bundle, dict) and "pipeline" in bundle:
        pipeline = bundle["pipeline"]
        features = bundle.get("features", None)
        if features:
            missing = [f for f in features if f not in df.columns]
            if missing:
                print(f"  [WARN] Missing features for prediction: {missing}")
                for f in missing:
                    df[f] = np.nan
            return pipeline.predict(df[features])
        else:
            return None

    # Case 2: bare estimator
    if hasattr(bundle, "predict"):
        # Try with all numeric columns
        num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        try:
            return bundle.predict(df[num_cols])
        except Exception as e:
            print(f"  [WARN] Direct predict failed: {e}")
            return None

    return None


def main() -> None:
    print("=" * 60)
    print("Validated Price Model Evaluation")
    print("=" * 60)

    # Load model
    bundle = load_validated_model()
    model_info = inspect_model(bundle)

    print("\n--- Model Structure ---")
    for k, v in model_info.items():
        if isinstance(v, list) and len(v) > 10:
            print(f"  {k}: [{', '.join(str(x) for x in v[:5])}, ... ({len(v)} total)]")
        else:
            print(f"  {k}: {v}")

    # Load data
    df = load_data()
    print(f"\nDataset: {len(df):,} daily records")
    print(f"Date range: {df['ddate'].min().date()} to {df['ddate'].max().date()}")

    # Aggregate to monthly
    monthly = aggregate_monthly(df)
    monthly = add_time_features(monthly)

    # Rename columns to match standard naming
    monthly = monthly.rename(columns={"amcname": "amc", "commname": "crop_name"})

    # Split: train ≤ 2023-12, test = 2024
    train_mask = monthly["month_start"] <= pd.Timestamp("2023-12-01")
    test_mask = (monthly["month_start"] >= pd.Timestamp("2024-01-01")) & (
        monthly["month_start"] <= pd.Timestamp("2024-12-01")
    )

    # Drop rows without lag features
    monthly = monthly.dropna(subset=["lag_1", "lag_2", "roll_mean_3"])
    train_df = monthly[train_mask].copy()
    test_df = monthly[test_mask].copy()

    print(f"\nTrain rows: {len(train_df):,}")
    print(f"Test rows:  {len(test_df):,}")

    if test_df.empty:
        print("[ERROR] No test data for 2024. Cannot evaluate.")
        return

    # Try to predict
    print("\n--- Attempting Predictions ---")
    test_preds = try_predict(bundle, test_df)

    if test_preds is not None and len(test_preds) == len(test_df):
        test_preds = np.clip(test_preds, 0, None)  # Clip negatives
        actual = test_df["modal_price_mean"].values

        overall = metrics(actual, test_preds)

        print("\n" + "=" * 60)
        print("VALIDATED PRICE MODEL — TEST METRICS (2024)")
        print("=" * 60)
        print(f"  N rows: {overall['n']}")
        print(f"  R²:     {overall['r2']:.4f}")
        print(f"  RMSE:   {overall['rmse']:.4f}")
        print(f"  MAE:    {overall['mae']:.4f}")

        # Per-district breakdown
        print("\n--- Per-District Test Metrics (top 10 by row count) ---")
        test_df["pred_price"] = test_preds
        dist_metrics = []
        for dist, grp in test_df.groupby("district"):
            m = metrics(grp["modal_price_mean"].values, grp["pred_price"].values)
            m["district"] = dist
            dist_metrics.append(m)
        dist_df = pd.DataFrame(dist_metrics).sort_values("n", ascending=False)
        print(dist_df.head(10).to_string(index=False))

        # Per-crop breakdown
        print("\n--- Per-Crop Test Metrics (top 10 by row count) ---")
        crop_metrics = []
        for crop, grp in test_df.groupby("crop_name"):
            m = metrics(grp["modal_price_mean"].values, grp["pred_price"].values)
            m["crop"] = crop
            crop_metrics.append(m)
        crop_df = pd.DataFrame(crop_metrics).sort_values("n", ascending=False)
        print(crop_df.head(10).to_string(index=False))

        # Comparison with M2 Base
        m2_preds = load_m2_base_predictions()
        if m2_preds is not None:
            print("\n" + "=" * 60)
            print("COMPARISON: Validated Model vs M2 Base XGBoost")
            print("=" * 60)

            # M2 base metrics from file
            m2_metrics_path = FINAL_MODELS_DIR / "m2_base_metrics.csv"
            if m2_metrics_path.exists():
                m2_met = pd.read_csv(m2_metrics_path)
                row = m2_met.iloc[0]
                print(f"\n  M2 Base XGBoost (from saved metrics):")
                print(f"    Test R²:  {row['test_r2']:.4f}")
                print(f"    Test RMSE: {row['test_rmse']:.4f}")
                print(f"    Test MAE:  {row['test_mae']:.4f}")

            print(f"\n  Validated Price Model:")
            print(f"    Test R²:   {overall['r2']:.4f}")
            print(f"    Test RMSE: {overall['rmse']:.4f}")
            print(f"    Test MAE:  {overall['mae']:.4f}")

            if overall["r2"] > 0.885:
                print("\n  ✅ Validated model OUTPERFORMS M2 Base XGBoost")
            elif overall["r2"] > 0.80:
                print("\n  ⚠️ Validated model is COMPETITIVE with M2 Base XGBoost")
            else:
                print("\n  ❌ Validated model UNDERPERFORMS M2 Base XGBoost")

        # Save predictions
        out_path = BASE_DIR / "validated_model_predictions_2024.csv"
        test_df[["month_start", "district", "amc", "crop_name", "modal_price_mean", "pred_price"]].to_csv(
            out_path, index=False
        )
        print(f"\n✅ Predictions saved to: {out_path}")

    else:
        print("\n[INFO] Could not generate predictions with standard approach.")
        print("       The model may require a specific input format.")
        print("       Dumping model structure for manual inspection:\n")
        print(json.dumps(model_info, indent=2, default=str))

        # If it's a dict, try to show more details
        if isinstance(bundle, dict):
            for k, v in bundle.items():
                print(f"\n  Key '{k}':")
                print(f"    Type: {type(v)}")
                if hasattr(v, "get_params"):
                    params = v.get_params()
                    for pk, pv in list(params.items())[:10]:
                        print(f"    {pk}: {pv}")

    print("\n" + "=" * 60)


if __name__ == "__main__":
    main()
