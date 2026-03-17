import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def parse_bool_series(series: pd.Series) -> pd.Series:
    if pd.api.types.is_bool_dtype(series):
        return series.fillna(False)
    mapped = (
        series.astype(str)
        .str.strip()
        .str.lower()
        .map({"true": True, "false": False, "1": True, "0": False, "yes": True, "no": False})
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


def main() -> None:
    repo_root = Path(__file__).resolve().parents[1]
    input_csv = repo_root / "outputs" / "model1_dataset.csv"
    out_dir = repo_root / "outputs"
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

    df["dq_weather_missing"] = parse_bool_series(df["dq_weather_missing"])
    df["dq_weather_incomplete"] = parse_bool_series(df["dq_weather_incomplete"])

    # Baseline training filter: complete weather rows and positive target.
    filtered = df[
        (~df["dq_weather_missing"])
        & (~df["dq_weather_incomplete"])
        & (df["yield_per_acre_proxy"].notna())
        & (df["yield_per_acre_proxy"] > 0)
    ].copy()

    print(f"Rows loaded: {len(df)}")
    print(f"Rows after baseline filters: {len(filtered)}")
    print("Available year_label counts (filtered):")
    print(filtered["year_label"].value_counts(dropna=False).sort_index().to_string())

    train_years = {"2020-21", "2021-22"}
    test_year = "2022-23"
    available_years = set(filtered["year_label"].dropna().astype(str).unique())
    required_years = set(train_years) | {test_year}
    if not required_years.issubset(available_years):
        missing_years = sorted(required_years - available_years)
        raise SystemExit(
            "Required year_label values missing for split: "
            f"{missing_years}. Check input data coverage."
        )

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

    require_columns(filtered, feature_columns + [target_col, "year_label"])
    filtered = filtered.dropna(subset=feature_columns + [target_col])

    train_df = filtered[filtered["year_label"].isin(train_years)].copy()
    test_df = filtered[filtered["year_label"] == test_year].copy()

    if train_df.empty or test_df.empty:
        raise SystemExit(
            f"Split produced empty set(s): train_rows={len(train_df)}, test_rows={len(test_df)}. "
            "Check year_label availability after filters."
        )

    X_train = train_df[feature_columns]
    y_train = train_df[target_col].to_numpy()
    X_test = test_df[feature_columns]
    y_test = test_df[target_col].to_numpy()

    preprocess = ColumnTransformer(
        transformers=[
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
            ("num", StandardScaler(), numeric_features),
        ]
    )

    model = RandomForestRegressor(
        n_estimators=400,
        max_depth=None,
        min_samples_leaf=2,
        n_jobs=-1,
        random_state=42,
    )

    pipeline = Pipeline(
        steps=[
            ("preprocess", preprocess),
            ("model", model),
        ]
    )

    try:
        pipeline.fit(X_train, y_train)
    except PermissionError:
        print("Parallel training with n_jobs=-1 failed due to environment permissions; retrying with n_jobs=1.")
        pipeline.set_params(model__n_jobs=1)
        pipeline.fit(X_train, y_train)

    train_pred = pipeline.predict(X_train)
    test_pred = pipeline.predict(X_test)

    train_metrics = metrics_dict(y_train, train_pred)
    test_metrics = metrics_dict(y_test, test_pred)

    print(f"Train rows: {len(train_df)}, Test rows: {len(test_df)}")
    print(
        "Train metrics: "
        f"RMSE={train_metrics['rmse']:.4f}, MAE={train_metrics['mae']:.4f}, R2={train_metrics['r2']:.4f}"
    )
    print(
        "Test metrics: "
        f"RMSE={test_metrics['rmse']:.4f}, MAE={test_metrics['mae']:.4f}, R2={test_metrics['r2']:.4f}"
    )

    feature_names = pipeline.named_steps["preprocess"].get_feature_names_out()
    importances = pipeline.named_steps["model"].feature_importances_
    imp_df = pd.DataFrame(
        {"feature": feature_names, "importance": importances}
    ).sort_values("importance", ascending=False)
    imp_df["rank"] = np.arange(1, len(imp_df) + 1)
    imp_df = imp_df[["rank", "feature", "importance"]]

    print("Top 25 feature importances:")
    print(imp_df.head(25).to_string(index=False))

    imp_path = out_dir / "model1_feature_importance.csv"
    imp_df.to_csv(imp_path, index=False)

    model_path = out_dir / "model1_rf.joblib"
    joblib.dump(pipeline, model_path)

    metadata = {
        "training_rows": int(len(train_df)),
        "test_rows": int(len(test_df)),
        "feature_columns_used": feature_columns,
        "target": target_col,
        "filter_rules": [
            "dq_weather_missing == False",
            "dq_weather_incomplete == False",
            "yield_per_acre_proxy not null",
            "yield_per_acre_proxy > 0",
            "train years: 2020-21, 2021-22",
            "test year: 2022-23",
        ],
        "train_metrics": train_metrics,
        "test_metrics": test_metrics,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }
    meta_path = out_dir / "model1_metadata.json"
    meta_path.write_text(json.dumps(metadata, indent=2), encoding="utf-8")

    print(f"Wrote model: {model_path}")
    print(f"Wrote feature importances: {imp_path}")
    print(f"Wrote metadata: {meta_path}")


if __name__ == "__main__":
    main()
