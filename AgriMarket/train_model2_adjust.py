from __future__ import annotations

import json
import subprocess
from io import StringIO
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.linear_model import RidgeCV


def load_from_duckdb(db_path: Path, duckdb_cli: Path, query: str) -> pd.DataFrame:
    try:
        import duckdb  # type: ignore

        con = duckdb.connect(str(db_path))
        df = con.execute(query).fetchdf()
        con.close()
        return df
    except Exception:
        result = subprocess.run(
            [str(duckdb_cli), str(db_path), "-csv", query],
            check=True,
            capture_output=True,
            text=True,
        )
        return pd.read_csv(StringIO(result.stdout))


def metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict:
    return {
        "rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "r2": float(r2_score(y_true, y_pred)),
    }


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    agri_prod_dir = base_dir.parent / "AgricultureProd"
    outputs_dir = base_dir / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)

    db_path = agri_prod_dir / "agri_validation.duckdb"
    duckdb_cli = agri_prod_dir / "tools" / "duckdb" / "duckdb.exe"

    oof_path = outputs_dir / "m2_base_oof.csv"
    if not oof_path.exists():
        raise FileNotFoundError(f"Missing OOF file: {oof_path}. Run train_model2_base.py first.")
    oof = pd.read_csv(oof_path, parse_dates=["month_start"])

    adjust_df = load_from_duckdb(
        db_path,
        duckdb_cli,
        "SELECT * FROM v_model2_adjust_dataset WHERE season_norm IN ('kharif','rabi')",
    )
    adjust_df["month_start"] = pd.to_datetime(adjust_df["month_start"])

    merged = oof.merge(
        adjust_df,
        on=["month_start", "district", "amc", "crop_name"],
        how="left",
        suffixes=("", "_adj"),
    )
    merged["residual"] = merged["actual_price"] - merged["base_pred"]

    fit_df = merged[merged["yield_signal"].notna()].copy()
    if fit_df.empty:
        pd.DataFrame(
            [{"status": "no_rows_with_yield_signal"}]
        ).to_csv(outputs_dir / "m2_adjust_metrics.csv", index=False)
        joblib.dump({"status": "no_fit"}, outputs_dir / "m2_adjust_model.pkl")
        return

    if "month_start" not in fit_df.columns and "obs_date" in fit_df.columns:
        fit_df["month_start"] = pd.to_datetime(fit_df["obs_date"])
    fit_df = fit_df.dropna(subset=["residual", "month_start", "actual_price", "base_pred"])
    fit_df["month_of_year"] = fit_df["month_start"].dt.month

    missing_features = []

    numeric_features = []
    for c in ["base_pred", "yield_signal"]:
        if c in fit_df.columns:
            numeric_features.append(c)
        else:
            missing_features.append(c)

    if "arrivals_sum" in fit_df.columns:
        numeric_features.append("arrivals_sum")
    else:
        missing_features.append("arrivals_sum")

    if "rain_mm_total" in fit_df.columns:
        numeric_features.append("rain_mm_total")
    elif "rain_sum_mm" in fit_df.columns:
        numeric_features.append("rain_sum_mm")
    else:
        missing_features.extend(["rain_mm_total", "rain_sum_mm"])

    for c in ["rainy_days", "hum_min_avg", "hum_max_avg", "month_of_year"]:
        if c in fit_df.columns:
            numeric_features.append(c)
        else:
            missing_features.append(c)

    categorical_features = []
    if "season_norm" in fit_df.columns:
        categorical_features.append("season_norm")
    else:
        missing_features.append("season_norm")

    feature_cols = numeric_features + categorical_features
    if not feature_cols or "base_pred" not in numeric_features or "yield_signal" not in numeric_features:
        raise SystemExit(
            f"Insufficient features for Ridge adjuster. features={feature_cols}, missing={missing_features}"
        )

    print(f"Rows with yield_signal: {len(fit_df)}")
    print(f"Date range: {fit_df['month_start'].min().date()} to {fit_df['month_start'].max().date()}")
    print(f"Residual mean/std: {fit_df['residual'].mean():.4f} / {fit_df['residual'].std():.4f}")
    print(f"corr(residual, yield_signal): {fit_df['residual'].corr(fit_df['yield_signal']):.4f}")
    print(f"corr(residual, base_pred): {fit_df['residual'].corr(fit_df['base_pred']):.4f}")
    print(f"Unique crops: {fit_df['crop_name'].nunique(dropna=True)}")
    print(f"Unique districts: {fit_df['district'].nunique(dropna=True)}")
    if missing_features:
        print("Missing/ignored features:", sorted(set(missing_features)))

    train_df = fit_df[fit_df["month_start"] <= pd.Timestamp("2021-12-01")].copy()
    test_df = fit_df[fit_df["month_start"] >= pd.Timestamp("2022-01-01")].copy()
    split_rule = "train<=2021-12-01, test>=2022-01-01"
    if train_df.empty or test_df.empty:
        split_idx = int(len(fit_df) * 0.8)
        fit_df = fit_df.sort_values("month_start")
        train_df = fit_df.iloc[:split_idx].copy()
        test_df = fit_df.iloc[split_idx:].copy()
        split_rule = "fallback_time_order_80_20"

    pre = ColumnTransformer(
        transformers=[
            (
                "cat",
                Pipeline(
                    [("imp", SimpleImputer(strategy="most_frequent")), ("ohe", OneHotEncoder(handle_unknown="ignore"))]
                ),
                categorical_features,
            ),
            (
                "num",
                Pipeline([("imp", SimpleImputer(strategy="median")), ("scale", StandardScaler())]),
                numeric_features,
            ),
        ]
    )
    model = RidgeCV(alphas=[0.1, 1.0, 10.0, 100.0, 1000.0])
    pipe = Pipeline([("pre", pre), ("model", model)])

    pipe.fit(train_df[feature_cols], train_df["residual"].to_numpy())
    train_resid_pred = pipe.predict(train_df[feature_cols])
    test_resid_pred = pipe.predict(test_df[feature_cols])

    resid_train_metrics = metrics(train_df["residual"].to_numpy(), train_resid_pred)
    resid_test_metrics = metrics(test_df["residual"].to_numpy(), test_resid_pred)

    train_final_pred = train_df["base_pred"].to_numpy() + train_resid_pred
    test_final_pred = test_df["base_pred"].to_numpy() + test_resid_pred

    final_train_metrics = metrics(train_df["actual_price"].to_numpy(), train_final_pred)
    final_test_metrics = metrics(test_df["actual_price"].to_numpy(), test_final_pred)
    alpha_chosen = float(pipe.named_steps["model"].alpha_)

    print(f"Adjust rows train={len(train_df)} test={len(test_df)}")
    print(f"Chosen alpha: {alpha_chosen}")
    print(
        "Residual Train: "
        f"R2={resid_train_metrics['r2']:.4f} RMSE={resid_train_metrics['rmse']:.4f} MAE={resid_train_metrics['mae']:.4f}"
    )
    print(
        "Residual Test : "
        f"R2={resid_test_metrics['r2']:.4f} RMSE={resid_test_metrics['rmse']:.4f} MAE={resid_test_metrics['mae']:.4f}"
    )
    print(
        "Final Train: "
        f"R2={final_train_metrics['r2']:.4f} RMSE={final_train_metrics['rmse']:.4f} MAE={final_train_metrics['mae']:.4f}"
    )
    print(
        "Final Test : "
        f"R2={final_test_metrics['r2']:.4f} RMSE={final_test_metrics['rmse']:.4f} MAE={final_test_metrics['mae']:.4f}"
    )

    pd.DataFrame(
        [
            {
                "model": "ridgecv",
                "alpha": alpha_chosen,
                "train_rows": len(train_df),
                "test_rows": len(test_df),
                "resid_train_r2": resid_train_metrics["r2"],
                "resid_train_rmse": resid_train_metrics["rmse"],
                "resid_train_mae": resid_train_metrics["mae"],
                "resid_test_r2": resid_test_metrics["r2"],
                "resid_test_rmse": resid_test_metrics["rmse"],
                "resid_test_mae": resid_test_metrics["mae"],
                "final_train_r2": final_train_metrics["r2"],
                "final_train_rmse": final_train_metrics["rmse"],
                "final_train_mae": final_train_metrics["mae"],
                "final_test_r2": final_test_metrics["r2"],
                "final_test_rmse": final_test_metrics["rmse"],
                "final_test_mae": final_test_metrics["mae"],
            }
        ]
    ).to_csv(outputs_dir / "m2_adjust_metrics.csv", index=False)

    joblib.dump({"pipeline": pipe, "features": feature_cols}, outputs_dir / "m2_adjust_model.pkl")
    (outputs_dir / "m2_adjust_metadata.json").write_text(
        json.dumps(
            {
                "model": "ridgecv",
                "alpha": alpha_chosen,
                "features_used": feature_cols,
                "missing_features": sorted(set(missing_features)),
                "split_rule": split_rule,
                "train_rows": len(train_df),
                "test_rows": len(test_df),
            },
            indent=2,
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
