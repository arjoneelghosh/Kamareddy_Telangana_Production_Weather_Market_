from __future__ import annotations

import json
import subprocess
from io import StringIO
from pathlib import Path
from typing import Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.base import clone
from sklearn.impute import SimpleImputer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder


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


def make_ohe(sparse: bool) -> OneHotEncoder:
    try:
        return OneHotEncoder(handle_unknown="ignore", sparse_output=sparse)
    except TypeError:
        return OneHotEncoder(handle_unknown="ignore", sparse=sparse)


def add_time_features(df: pd.DataFrame) -> pd.DataFrame:
    out = df.sort_values(["district", "amc", "crop_name", "month_start"]).copy()
    grp = out.groupby(["district", "amc", "crop_name"], dropna=False)

    for lag in [1, 2, 3, 6, 12]:
        out[f"lag_{lag}"] = grp["modal_price_mean"].shift(lag)

    lag1 = grp["modal_price_mean"].shift(1)
    out["roll_mean_3"] = lag1.groupby([out["district"], out["amc"], out["crop_name"]]).transform(
        lambda s: s.rolling(3, min_periods=2).mean()
    )
    out["roll_mean_6"] = lag1.groupby([out["district"], out["amc"], out["crop_name"]]).transform(
        lambda s: s.rolling(6, min_periods=3).mean()
    )

    out["month_num"] = out["month_start"].dt.month
    out["month_sin"] = np.sin(2 * np.pi * out["month_num"] / 12)
    out["month_cos"] = np.cos(2 * np.pi * out["month_num"] / 12)
    return out


def get_model() -> Tuple[object, str]:
    try:
        from xgboost import XGBRegressor  # type: ignore

        return (
            XGBRegressor(
                objective="reg:squarederror",
                n_estimators=700,
                learning_rate=0.04,
                max_depth=6,
                subsample=0.8,
                colsample_bytree=0.8,
                reg_lambda=5.0,
                random_state=42,
                n_jobs=-1,
            ),
            "xgboost",
        )
    except Exception:
        try:
            from lightgbm import LGBMRegressor  # type: ignore

            return (
                LGBMRegressor(
                    n_estimators=800,
                    learning_rate=0.04,
                    max_depth=-1,
                    num_leaves=63,
                    subsample=0.8,
                    colsample_bytree=0.8,
                    random_state=42,
                ),
                "lightgbm",
            )
        except Exception:
            return (
                HistGradientBoostingRegressor(
                    max_depth=8,
                    learning_rate=0.05,
                    max_iter=500,
                    min_samples_leaf=20,
                    random_state=42,
                ),
                "hist_gradient_boosting",
            )


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

    query = """
        SELECT *
        FROM v_model2_base_dataset
        WHERE season_norm IN ('kharif','rabi')
    """
    df = load_from_duckdb(db_path, duckdb_cli, query)
    if df.empty:
        raise SystemExit("v_model2_base_dataset is empty. Run SQL 60..66 first.")

    df["month_start"] = pd.to_datetime(df["month_start"])
    df = add_time_features(df)

    numeric_features = [
        "arrivals_sum",
        "n_days",
        "rain_sum_mm",
        "rainy_days",
        "hum_min_avg",
        "hum_max_avg",
        "avg_mandals_reporting",
        "month_num",
        "month_sin",
        "month_cos",
        "lag_1",
        "lag_2",
        "lag_3",
        "lag_6",
        "lag_12",
        "roll_mean_3",
        "roll_mean_6",
    ]
    categorical_features = ["district", "amc", "crop_name", "season_norm"]
    target = "modal_price_mean"
    all_features = numeric_features + categorical_features

    df[target] = pd.to_numeric(df[target], errors="coerce")
    model_df = df.dropna(subset=[target] + ["month_start"]).copy()
    model_df = model_df[np.isfinite(model_df[target])].copy()
    for c in all_features:
        if c not in model_df.columns:
            model_df[c] = np.nan
    model_df = model_df.dropna(subset=["lag_1", "lag_2", "roll_mean_3"])

    train_mask = model_df["month_start"] <= pd.Timestamp("2023-12-01")
    test_mask = (model_df["month_start"] >= pd.Timestamp("2024-01-01")) & (
        model_df["month_start"] <= pd.Timestamp("2024-12-01")
    )
    train_df = model_df[train_mask].copy()
    test_df = model_df[test_mask].copy()
    if train_df.empty or test_df.empty:
        raise SystemExit(f"Invalid split. train_rows={len(train_df)}, test_rows={len(test_df)}")

    pre = ColumnTransformer(
        transformers=[
            ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("ohe", make_ohe(True))]), categorical_features),
            ("num", Pipeline([("imputer", SimpleImputer(strategy="median"))]), numeric_features),
        ]
    )
    estimator, model_name = get_model()
    pipe = Pipeline([("pre", pre), ("model", estimator)])

    X_train = train_df[all_features]
    y_train = train_df[target].to_numpy()
    X_test = test_df[all_features]
    y_test = test_df[target].to_numpy()
    fallback_estimator = HistGradientBoostingRegressor(
        max_depth=8,
        learning_rate=0.05,
        max_iter=500,
        min_samples_leaf=20,
        random_state=42,
    )
    pre_for_oof = pre
    try:
        pipe.fit(X_train, y_train)
    except Exception as exc:
        print(f"Primary model '{model_name}' failed: {exc}")
        print("Falling back to hist_gradient_boosting.")
        model_name = "hist_gradient_boosting_fallback"
        pre_dense = ColumnTransformer(
            transformers=[
                ("cat", Pipeline([("imputer", SimpleImputer(strategy="most_frequent")), ("ohe", make_ohe(False))]), categorical_features),
                ("num", Pipeline([("imputer", SimpleImputer(strategy="median"))]), numeric_features),
            ]
        )
        pipe = Pipeline([("pre", pre_dense), ("model", fallback_estimator)])
        pipe.fit(X_train, y_train)
        pre_for_oof = pre_dense

    train_pred = pipe.predict(X_train)
    test_pred = pipe.predict(X_test)
    m_train = metrics(y_train, train_pred)
    m_test = metrics(y_test, test_pred)

    print(f"Rows total={len(model_df)} train={len(train_df)} test={len(test_df)}")
    print(f"Model={model_name}")
    print(f"Train: R2={m_train['r2']:.4f} RMSE={m_train['rmse']:.4f} MAE={m_train['mae']:.4f}")
    print(f"Test : R2={m_test['r2']:.4f} RMSE={m_test['rmse']:.4f} MAE={m_test['mae']:.4f}")

    pred_out = test_df[["month_start", "district", "amc", "crop_name", target]].copy()
    pred_out = pred_out.rename(columns={target: "actual_price"})
    pred_out["pred_price"] = test_pred
    pred_out["pred_price"] = pred_out["pred_price"].clip(lower=0.0)
    pred_out.to_csv(outputs_dir / "m2_base_predictions_2024.csv", index=False)

    pd.DataFrame(
        [
            {
                "model": model_name,
                "train_rows": len(train_df),
                "test_rows": len(test_df),
                "train_r2": m_train["r2"],
                "train_rmse": m_train["rmse"],
                "train_mae": m_train["mae"],
                "test_r2": m_test["r2"],
                "test_rmse": m_test["rmse"],
                "test_mae": m_test["mae"],
            }
        ]
    ).to_csv(outputs_dir / "m2_base_metrics.csv", index=False)

    # OOF for overlap years, no leakage (block forward by month).
    overlap = model_df[model_df["year_label"].isin(["2020-21", "2021-22", "2022-23"])].copy()
    oof_rows = []
    months = np.array(sorted(overlap["month_start"].dropna().unique()))
    month_blocks = [b for b in np.array_split(months, 5) if len(b) > 0]
    for block in month_blocks:
        block_start = pd.Timestamp(block.min())
        train_fold = overlap[overlap["month_start"] < block_start]
        val_fold = overlap[overlap["month_start"].isin(block)]
        if len(train_fold) < 100 or val_fold.empty:
            continue
        fold_pipe = Pipeline([("pre", clone(pre_for_oof)), ("model", clone(pipe.named_steps["model"]))])
        fold_pipe.fit(train_fold[all_features], train_fold[target].to_numpy())
        val_pred = fold_pipe.predict(val_fold[all_features])
        out = val_fold[["month_start", "district", "amc", "crop_name", target]].copy()
        out = out.rename(columns={target: "actual_price"})
        out["base_pred"] = val_pred
        out["base_pred"] = out["base_pred"].clip(lower=0.0)
        oof_rows.append(out)

    oof_df = pd.concat(oof_rows, ignore_index=True) if oof_rows else pd.DataFrame(
        columns=["month_start", "district", "amc", "crop_name", "actual_price", "base_pred"]
    )
    oof_df.to_csv(outputs_dir / "m2_base_oof.csv", index=False)

    joblib.dump({"pipeline": pipe, "features": all_features, "model_name": model_name}, outputs_dir / "m2_base_model.pkl")
    (outputs_dir / "m2_base_training_metadata.json").write_text(
        json.dumps(
            {
                "db_path": str(db_path),
                "train_cutoff": "2023-12-01",
                "test_range": ["2024-01-01", "2024-12-01"],
                "features": all_features,
                "model_name": model_name,
            },
            indent=2,
        ),
        encoding="utf-8",
    )


if __name__ == "__main__":
    main()
