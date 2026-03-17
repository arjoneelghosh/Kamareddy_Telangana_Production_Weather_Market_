import argparse
import json
import platform
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
import xgboost as xgb
from sklearn.compose import ColumnTransformer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import OneHotEncoder


def parse_bool_series(series: pd.Series) -> pd.Series:
    """Normalize boolean-like columns stored as bool/0-1/strings. Missing => False."""
    if pd.api.types.is_bool_dtype(series):
        return series.fillna(False)

    mapped = (
        series.astype(str)
        .str.strip()
        .str.lower()
        .map(
            {
                "true": True,
                "false": False,
                "1": True,
                "0": False,
                "yes": True,
                "no": False,
                "t": True,
                "f": False,
                "y": True,
                "n": False,
            }
        )
    )
    return mapped.fillna(False)


def require_columns(df: pd.DataFrame, required: list[str]) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def metrics_dict(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    mae = float(mean_absolute_error(y_true, y_pred))
    r2 = float(r2_score(y_true, y_pred))
    return {"rmse": rmse, "mae": mae, "r2": r2}


def to_dense_if_needed(X):
    """XGBoost accepts scipy sparse. Keep as-is unless it's a weird type."""
    return X


def main() -> None:
    parser = argparse.ArgumentParser(description="Train Model 1 with XGBoost: Weather -> Yield (yield_per_acre_proxy).")
    repo_root = Path(__file__).resolve().parents[1]
    parser.add_argument(
        "--input_csv",
        type=str,
        default=str(repo_root / "outputs" / "model1_dataset.csv"),
        help="Path to outputs/model1_dataset.csv",
    )
    parser.add_argument(
        "--out_dir",
        type=str,
        default=str(repo_root / "outputs"),
        help="Output directory for artifacts",
    )

    # Time split
    parser.add_argument("--train_years", type=str, default="2020-21,2021-22")
    parser.add_argument("--test_year", type=str, default="2022-23")
    parser.add_argument("--train_base_year", type=str, default="2020-21")
    parser.add_argument("--val_year", type=str, default="2021-22")

    # Filters
    parser.add_argument(
        "--allow_incomplete_weather",
        action="store_true",
        help="If set, do NOT filter dq_weather_incomplete rows (not recommended for baseline).",
    )

    # XGB params
    parser.add_argument("--max_depth", type=int, default=8)
    parser.add_argument("--learning_rate", type=float, default=0.05)
    parser.add_argument("--n_estimators", type=int, default=4000)
    parser.add_argument("--subsample", type=float, default=0.8)
    parser.add_argument("--colsample_bytree", type=float, default=0.8)
    parser.add_argument("--min_child_weight", type=float, default=2.0)
    parser.add_argument("--reg_lambda", type=float, default=1.0)
    parser.add_argument("--reg_alpha", type=float, default=0.0)
    parser.add_argument("--early_stopping_rounds", type=int, default=150)

    args = parser.parse_args()

    input_csv = Path(args.input_csv)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    if not input_csv.exists():
        raise FileNotFoundError(f"Input dataset not found: {input_csv}")

    df = pd.read_csv(input_csv)

    required_cols = [
        "year_label",
        "district",
        "crop_name",
        "season_norm",
        "yield_per_acre_proxy",
        "rain_total_mm",
        "rainy_days_total",
        "hum_min_avg",
        "hum_max_avg",
        "avg_mandals_reporting",
        "days_covered",
        "months_covered",
        "dq_weather_missing",
        "dq_weather_incomplete",
    ]
    require_columns(df, required_cols)

    # Normalize dq flags
    df["dq_weather_missing"] = parse_bool_series(df["dq_weather_missing"])
    df["dq_weather_incomplete"] = parse_bool_series(df["dq_weather_incomplete"])

    # Baseline filters
    mask = (~df["dq_weather_missing"]) & (df["yield_per_acre_proxy"].notna()) & (df["yield_per_acre_proxy"] > 0)
    if not args.allow_incomplete_weather:
        mask = mask & (~df["dq_weather_incomplete"])
    filtered = df[mask].copy()

    print(f"Rows loaded: {len(df)}")
    print(f"Rows after baseline filters: {len(filtered)}")
    print("Available year_label counts (filtered):")
    print(filtered["year_label"].value_counts(dropna=False).sort_index().to_string())

    train_years = {y.strip() for y in args.train_years.split(",") if y.strip()}
    test_year = args.test_year.strip()
    train_base_year = args.train_base_year.strip()
    val_year = args.val_year.strip()

    required_years = set(train_years) | {test_year, train_base_year, val_year}
    available_years = set(filtered["year_label"].dropna().astype(str).unique())
    if not required_years.issubset(available_years):
        missing = sorted(required_years - available_years)
        raise SystemExit(f"Required year_label values missing after filters: {missing}")

    # Features
    numeric_features = [
        "rain_total_mm",
        "rainy_days_total",
        "hum_min_avg",
        "hum_max_avg",
        "avg_mandals_reporting",
        "days_covered",
        "months_covered",
    ]
    categorical_features = ["district", "crop_name", "season_norm"]
    feature_columns = numeric_features + categorical_features
    target_col = "yield_per_acre_proxy"

    require_columns(filtered, feature_columns + [target_col])

    # Drop rows with missing features/target
    filtered = filtered.dropna(subset=feature_columns + [target_col])

    # Splits
    train_base_df = filtered[filtered["year_label"] == train_base_year].copy()
    val_df = filtered[filtered["year_label"] == val_year].copy()
    train_df = filtered[filtered["year_label"].isin(train_years)].copy()
    test_df = filtered[filtered["year_label"] == test_year].copy()

    if train_base_df.empty or val_df.empty or train_df.empty or test_df.empty:
        raise SystemExit(
            f"Split produced empty set(s): train_base={len(train_base_df)}, val={len(val_df)}, "
            f"train={len(train_df)}, test={len(test_df)}"
        )

    # Preprocess: OneHot categorical, passthrough numeric
    preprocess = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
            ("num", "passthrough", numeric_features),
        ],
        remainder="drop",
        sparse_threshold=0.3,
    )

    X_train_base = preprocess.fit_transform(train_base_df[feature_columns])
    y_train_base = train_base_df[target_col].to_numpy()

    X_val = preprocess.transform(val_df[feature_columns])
    y_val = val_df[target_col].to_numpy()

    X_train = preprocess.transform(train_df[feature_columns])
    y_train = train_df[target_col].to_numpy()

    X_test = preprocess.transform(test_df[feature_columns])
    y_test = test_df[target_col].to_numpy()

    X_train_base = to_dense_if_needed(X_train_base)
    X_val = to_dense_if_needed(X_val)
    X_train = to_dense_if_needed(X_train)
    X_test = to_dense_if_needed(X_test)

    # Train with early stopping (XGBoost 3.x: callbacks go in constructor)
    model = xgb.XGBRegressor(
        objective="reg:squarederror",
        n_estimators=args.n_estimators,
        learning_rate=args.learning_rate,
        max_depth=args.max_depth,
        subsample=args.subsample,
        colsample_bytree=args.colsample_bytree,
        min_child_weight=args.min_child_weight,
        reg_lambda=args.reg_lambda,
        reg_alpha=args.reg_alpha,
        tree_method="hist",
        random_state=42,
        n_jobs=-1,
        early_stopping_rounds=args.early_stopping_rounds,
        callbacks=[xgb.callback.EarlyStopping(rounds=args.early_stopping_rounds, save_best=True)],
    )

    print(f"Training XGBoost with early stopping (train={train_base_year}, val={val_year})...")
    model.fit(
        X_train_base,
        y_train_base,
        eval_set=[(X_val, y_val)],
        verbose=False,
    )

    best_iteration = getattr(model, "best_iteration", None)
    best_score = getattr(model, "best_score", None)
    print(f"Best iteration: {best_iteration}, best val score: {best_score}")

    # Refit on full training years using best_iteration as cap (if available)
    final_n_estimators = (int(best_iteration) + 1) if best_iteration is not None else args.n_estimators

    final_model = xgb.XGBRegressor(
        objective="reg:squarederror",
        n_estimators=final_n_estimators,
        learning_rate=args.learning_rate,
        max_depth=args.max_depth,
        subsample=args.subsample,
        colsample_bytree=args.colsample_bytree,
        min_child_weight=args.min_child_weight,
        reg_lambda=args.reg_lambda,
        reg_alpha=args.reg_alpha,
        tree_method="hist",
        random_state=42,
        n_jobs=-1,
    )

    print(f"Refitting on full train years {sorted(list(train_years))} with n_estimators={final_n_estimators}...")
    final_model.fit(X_train, y_train, verbose=False)

    # Evaluate
    train_pred = final_model.predict(X_train)
    test_pred = final_model.predict(X_test)

    train_metrics = metrics_dict(y_train, train_pred)
    test_metrics = metrics_dict(y_test, test_pred)

    print(f"Train rows: {len(train_df)}, Test rows: {len(test_df)}")
    print(f"Train metrics: RMSE={train_metrics['rmse']:.4f}, MAE={train_metrics['mae']:.4f}, R2={train_metrics['r2']:.4f}")
    print(f"Test  metrics: RMSE={test_metrics['rmse']:.4f}, MAE={test_metrics['mae']:.4f}, R2={test_metrics['r2']:.4f}")

    # Feature importance (gain)
    try:
        feature_names = preprocess.get_feature_names_out()
    except Exception:
        feature_names = np.array([f"f_{i}" for i in range(getattr(final_model, "n_features_in_", 0) or 0)])

    booster = final_model.get_booster()
    gain = booster.get_score(importance_type="gain")  # dict: f0 -> gain
    rows = []
    for k, v in gain.items():
        if k.startswith("f"):
            idx = int(k[1:])
            name = feature_names[idx] if idx < len(feature_names) else k
        else:
            name = k
        rows.append((name, float(v)))

    imp_df = pd.DataFrame(rows, columns=["feature", "gain"]).sort_values("gain", ascending=False)
    imp_df.insert(0, "rank", np.arange(1, len(imp_df) + 1))
    imp_path = out_dir / "model1_xgb_feature_importance.csv"
    imp_df.to_csv(imp_path, index=False)

    print("Top 25 XGBoost gain importances:")
    if not imp_df.empty:
        print(imp_df.head(25).to_string(index=False))
    else:
        print("(No importance available; check model training)")

    # Save artifacts
    preproc_path = out_dir / "model1_xgb_preprocess.joblib"
    joblib.dump(preprocess, preproc_path)

    model_path = out_dir / "model1_xgb_model.json"
    final_model.save_model(str(model_path))

    metadata = {
        "training_rows": int(len(train_df)),
        "test_rows": int(len(test_df)),
        "train_years": sorted(list(train_years)),
        "test_year": test_year,
        "train_base_year": train_base_year,
        "val_year": val_year,
        "target": target_col,
        "filters": {
            "dq_weather_missing": False,
            "dq_weather_incomplete_filtered": (not args.allow_incomplete_weather),
            "yield_gt_0": True,
        },
        "features": {"numeric": numeric_features, "categorical": categorical_features},
        "xgb_params": {
            "max_depth": args.max_depth,
            "learning_rate": args.learning_rate,
            "n_estimators_requested": args.n_estimators,
            "n_estimators_final": final_n_estimators,
            "subsample": args.subsample,
            "colsample_bytree": args.colsample_bytree,
            "min_child_weight": args.min_child_weight,
            "reg_lambda": args.reg_lambda,
            "reg_alpha": args.reg_alpha,
            "early_stopping_rounds": args.early_stopping_rounds,
            "best_iteration": best_iteration,
            "best_val_score": best_score,
        },
        "train_metrics": train_metrics,
        "test_metrics": test_metrics,
        "env_versions": {
            "python": platform.python_version(),
            "platform": platform.platform(),
            "numpy": np.__version__,
            "pandas": pd.__version__,
            "sklearn": sklearn.__version__,
            "xgboost": xgb.__version__,
            "joblib": joblib.__version__,
        },
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }

    meta_path = out_dir / "model1_xgb_metadata.json"
    meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print(f"Wrote preprocessor: {preproc_path}")
    print(f"Wrote XGBoost model: {model_path}")
    print(f"Wrote feature importances: {imp_path}")
    print(f"Wrote metadata: {meta_path}")


if __name__ == "__main__":
    main()