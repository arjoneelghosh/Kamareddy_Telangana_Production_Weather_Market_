"""
Telegana_AgriForecaster - Model 1 diagnostics
District vs Global trend mapping + model selection recommendation

Inputs:
  - /mnt/data/model1_dataset.csv

Outputs (in out_dir):
  - global_test_by_district.csv
  - district_models_test_scores.csv
  - district_improvement_vs_global.csv
  - ablation_global_summary.csv
  - ablation_district_summary.csv
  - model_selection_recommendations.csv
  - plots:
      * plot_global_r2_by_district.png
      * plot_improvement_vs_global.png
      * plot_weather_delta_r2.png

Run:
  python district_vs_global_diagnostics.py --input_csv /mnt/data/model1_dataset.csv --out_dir /mnt/data/out

Notes:
  - Designed to avoid XGBoost early-stopping API differences by default.
  - You can enable early stopping with --use_early_stopping (optional).
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.compose import ColumnTransformer
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.preprocessing import OneHotEncoder, StandardScaler

import xgboost as xgb


# -----------------------------
# Utilities
# -----------------------------
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


def metrics_dict(y_true: np.ndarray, y_pred: np.ndarray) -> Dict[str, float]:
    rmse = float(np.sqrt(mean_squared_error(y_true, y_pred)))
    mae = float(mean_absolute_error(y_true, y_pred))
    r2 = float(r2_score(y_true, y_pred))
    return {"rmse": rmse, "mae": mae, "r2": r2}


def require_columns(df: pd.DataFrame, required: List[str]) -> None:
    missing = [c for c in required if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")


def safe_makedirs(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


# -----------------------------
# Modeling config
# -----------------------------
@dataclass
class ModelConfig:
    target: str
    numeric_features: List[str]
    categorical_features: List[str]
    train_years: List[str]
    test_year: str
    train_base_year: str
    val_year: str

    # Filters
    filter_dq_weather_missing: bool = True
    filter_dq_weather_incomplete: bool = True
    filter_yield_gt_0: bool = True


def build_preprocessor(cats: List[str], nums: List[str], scale_numeric: bool = False) -> ColumnTransformer:
    transformers = [("cat", OneHotEncoder(handle_unknown="ignore"), cats)]
    if nums:
        num_transformer = StandardScaler() if scale_numeric else "passthrough"
        transformers.append(("num", num_transformer, nums))
    return ColumnTransformer(transformers=transformers, remainder="drop", sparse_threshold=0.3)


def fit_xgb(
    X_train: np.ndarray,
    y_train: np.ndarray,
    X_val: np.ndarray | None,
    y_val: np.ndarray | None,
    params: Dict,
    use_early_stopping: bool,
    early_stopping_rounds: int,
    random_state: int = 42,
) -> xgb.XGBRegressor:
    """
    Fits XGBRegressor. By default, trains without early stopping to avoid wrapper incompatibilities.
    If use_early_stopping=True, uses callback-based early stopping (works with xgboost 3.x).
    """
    model = xgb.XGBRegressor(
        objective="reg:squarederror",
        tree_method=params.get("tree_method", "hist"),
        random_state=random_state,
        n_jobs=-1,
        **{k: v for k, v in params.items() if k != "tree_method"},
    )

    if use_early_stopping and (X_val is not None) and (y_val is not None):
        model.fit(
            X_train,
            y_train,
            eval_set=[(X_val, y_val)],
            verbose=False,
            callbacks=[xgb.callback.EarlyStopping(rounds=early_stopping_rounds, save_best=True)],
        )
    else:
        model.fit(X_train, y_train, verbose=False)

    return model


def split_by_year(df: pd.DataFrame, cfg: ModelConfig) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    train_base_df = df[df["year_label"] == cfg.train_base_year].copy()
    val_df = df[df["year_label"] == cfg.val_year].copy()
    train_df = df[df["year_label"].isin(cfg.train_years)].copy()
    test_df = df[df["year_label"] == cfg.test_year].copy()
    return train_base_df, val_df, train_df, test_df


# -----------------------------
# Diagnostics
# -----------------------------
def eval_by_district(y_true: np.ndarray, y_pred: np.ndarray, districts: np.ndarray, min_rows: int) -> pd.DataFrame:
    tmp = pd.DataFrame({"district": districts, "y_true": y_true, "y_pred": y_pred})
    rows = []
    for d, g in tmp.groupby("district"):
        if len(g) < min_rows:
            continue
        m = metrics_dict(g["y_true"].to_numpy(), g["y_pred"].to_numpy())
        rows.append((d, int(len(g)), m["r2"], m["rmse"], m["mae"]))
    out = pd.DataFrame(rows, columns=["district", "n_test", "r2", "rmse", "mae"]).sort_values(
        ["r2", "n_test"], ascending=[False, False]
    )
    return out


def make_barplot(df: pd.DataFrame, x: str, y: str, title: str, out_path: Path, top_k: int = 25) -> None:
    if df.empty:
        return
    plot_df = df.copy().head(top_k)
    plt.figure(figsize=(12, 6))
    plt.bar(plot_df[x].astype(str), plot_df[y].astype(float))
    plt.xticks(rotation=75, ha="right")
    plt.title(title)
    plt.tight_layout()
    plt.savefig(out_path, dpi=160)
    plt.close()


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input_csv", type=str, default="/mnt/data/model1_dataset.csv")
    parser.add_argument("--out_dir", type=str, default="/mnt/data/out")
    parser.add_argument("--tune_config", type=str, default=None)

    # Year split (matches your current pipeline)
    parser.add_argument("--train_years", type=str, default="2020-21,2021-22")
    parser.add_argument("--test_year", type=str, default="2022-23")
    parser.add_argument("--train_base_year", type=str, default="2020-21")
    parser.add_argument("--val_year", type=str, default="2021-22")

    # Filters
    parser.add_argument("--allow_incomplete_weather", action="store_true")
    parser.add_argument("--allow_missing_weather", action="store_true")

    # Scoring thresholds
    parser.add_argument("--min_test_rows_per_district", type=int, default=25)
    parser.add_argument("--min_train_rows_per_district_model", type=int, default=60)

    # Early stopping (optional)
    parser.add_argument("--use_early_stopping", action="store_true")
    parser.add_argument("--early_stopping_rounds", type=int, default=150)

    args = parser.parse_args()

    input_csv = Path(args.input_csv)
    out_dir = Path(args.out_dir)
    safe_makedirs(out_dir)

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

    cfg = ModelConfig(
        target="yield_per_acre_proxy",
        numeric_features=[
            "rain_total_mm",
            "rainy_days_total",
            "hum_min_avg",
            "hum_max_avg",
            "avg_mandals_reporting",
            "days_covered",
            "months_covered",
        ],
        categorical_features=["district", "crop_name", "season_norm"],
        train_years=[y.strip() for y in args.train_years.split(",") if y.strip()],
        test_year=args.test_year.strip(),
        train_base_year=args.train_base_year.strip(),
        val_year=args.val_year.strip(),
        filter_dq_weather_missing=(not args.allow_missing_weather),
        filter_dq_weather_incomplete=(not args.allow_incomplete_weather),
        filter_yield_gt_0=True,
    )

    # Baseline filtering
    mask = df[cfg.target].notna()
    if cfg.filter_yield_gt_0:
        mask = mask & (df[cfg.target] > 0)
    if cfg.filter_dq_weather_missing:
        mask = mask & (~df["dq_weather_missing"])
    if cfg.filter_dq_weather_incomplete:
        mask = mask & (~df["dq_weather_incomplete"])

    fdf = df[mask].copy()
    fdf = fdf.dropna(subset=cfg.numeric_features + cfg.categorical_features + [cfg.target])

    print(f"Rows loaded: {len(df)}")
    print(f"Rows after filters: {len(fdf)}")
    print("Filtered year_label counts:")
    print(fdf["year_label"].value_counts().sort_index().to_string())

    # Ensure years exist
    available_years = set(fdf["year_label"].astype(str).unique())
    needed_years = set(cfg.train_years + [cfg.test_year, cfg.train_base_year, cfg.val_year])
    missing_years = sorted(list(needed_years - available_years))
    if missing_years:
        raise SystemExit(f"Missing required year_label(s) after filtering: {missing_years}")

    # Split
    train_base_df, val_df, train_df, test_df = split_by_year(fdf, cfg)

    if train_base_df.empty or val_df.empty or train_df.empty or test_df.empty:
        raise SystemExit(
            f"Empty split: train_base={len(train_base_df)}, val={len(val_df)}, train={len(train_df)}, test={len(test_df)}"
        )

    # XGB params (overridable via --tune_config JSON file)
    xgb_params = {
        "max_depth": 8,
        "learning_rate": 0.05,
        "n_estimators": 400,     # moderate default; early stopping can reduce if enabled
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "min_child_weight": 2.0,
        "gamma": 0.0,
        "reg_lambda": 1.0,
        "reg_alpha": 0.0,
        "tree_method": "hist",
    }
    scale_numeric = False
    if args.tune_config:
        cfg_path = Path(args.tune_config)
        if not cfg_path.exists():
            raise SystemExit(f"tune_config file not found: {cfg_path}")
        tune_cfg = json.loads(cfg_path.read_text(encoding="utf-8-sig"))
        if "xgb_params" in tune_cfg and isinstance(tune_cfg["xgb_params"], dict):
            xgb_params.update(tune_cfg["xgb_params"])
        if "scale_numeric" in tune_cfg:
            scale_numeric = bool(tune_cfg["scale_numeric"])
        print("\nLoaded tuning config:")
        print(json.dumps({"xgb_params": xgb_params, "scale_numeric": scale_numeric}, indent=2))

    # -----------------------------
    # 1) GLOBAL MODEL (cat + weather)
    # -----------------------------
    pre_full = build_preprocessor(cfg.categorical_features, cfg.numeric_features, scale_numeric=scale_numeric)

    X_train_base = pre_full.fit_transform(train_base_df[cfg.categorical_features + cfg.numeric_features])
    y_train_base = train_base_df[cfg.target].to_numpy()

    X_val = pre_full.transform(val_df[cfg.categorical_features + cfg.numeric_features])
    y_val = val_df[cfg.target].to_numpy()

    X_train = pre_full.transform(train_df[cfg.categorical_features + cfg.numeric_features])
    y_train = train_df[cfg.target].to_numpy()

    X_test = pre_full.transform(test_df[cfg.categorical_features + cfg.numeric_features])
    y_test = test_df[cfg.target].to_numpy()

    global_model = fit_xgb(
        X_train=X_train_base,
        y_train=y_train_base,
        X_val=X_val,
        y_val=y_val,
        params=xgb_params,
        use_early_stopping=args.use_early_stopping,
        early_stopping_rounds=args.early_stopping_rounds,
    )

    global_train_pred = global_model.predict(X_train)
    global_test_pred = global_model.predict(X_test)

    global_train_metrics = metrics_dict(y_train, global_train_pred)
    global_test_metrics = metrics_dict(y_test, global_test_pred)

    print("\nGLOBAL (cat + weather):")
    print(f"Train: R2={global_train_metrics['r2']:.4f} RMSE={global_train_metrics['rmse']:.4f}")
    print(f"Test : R2={global_test_metrics['r2']:.4f} RMSE={global_test_metrics['rmse']:.4f}")

    # Per-district test metrics for global model
    global_by_dist = eval_by_district(
        y_true=y_test,
        y_pred=global_test_pred,
        districts=test_df["district"].to_numpy(),
        min_rows=args.min_test_rows_per_district,
    )
    global_by_dist_path = out_dir / "global_test_by_district.csv"
    global_by_dist.to_csv(global_by_dist_path, index=False)

    make_barplot(
        global_by_dist,
        x="district",
        y="r2",
        title=f"Global model Test R² by district ({cfg.test_year})",
        out_path=out_dir / "plot_global_r2_by_district.png",
        top_k=min(30, len(global_by_dist)),
    )

    # -----------------------------
    # 2) DISTRICT MODELS (per district)
    # -----------------------------
    district_rows = []
    districts = sorted(train_df["district"].unique().tolist())

    for d in districts:
        train_d = train_df[train_df["district"] == d]
        test_d = test_df[test_df["district"] == d]
        train_base_d = train_base_df[train_base_df["district"] == d]
        val_d = val_df[val_df["district"] == d]

        # Must have enough rows for training + scoring
        if len(train_d) < args.min_train_rows_per_district_model or len(test_d) < args.min_test_rows_per_district:
            continue

        # District model uses same features, but "district" column becomes constant.
        # We can drop district from categorical features for district-specific training to reduce useless one-hot.
        cats_d = ["crop_name", "season_norm"]
        nums_d = cfg.numeric_features
        pre_d = build_preprocessor(cats_d, nums_d, scale_numeric=scale_numeric)

        X_train_base_d = pre_d.fit_transform(train_base_d[cats_d + nums_d])
        y_train_base_d = train_base_d[cfg.target].to_numpy()

        # If val is too small for early stopping, fall back to no early stopping
        use_es = args.use_early_stopping and (len(val_d) >= 20) and (len(train_base_d) >= 20)

        if len(val_d) > 0:
            X_val_d = pre_d.transform(val_d[cats_d + nums_d])
            y_val_d = val_d[cfg.target].to_numpy()
        else:
            X_val_d, y_val_d = None, None
            use_es = False

        X_train_d = pre_d.transform(train_d[cats_d + nums_d])
        y_train_d = train_d[cfg.target].to_numpy()

        X_test_d = pre_d.transform(test_d[cats_d + nums_d])
        y_test_d = test_d[cfg.target].to_numpy()

        mdl_d = fit_xgb(
            X_train=X_train_base_d,
            y_train=y_train_base_d,
            X_val=X_val_d,
            y_val=y_val_d,
            params=xgb_params,
            use_early_stopping=use_es,
            early_stopping_rounds=args.early_stopping_rounds,
        )

        pred_test_d = mdl_d.predict(X_test_d)
        m_d = metrics_dict(y_test_d, pred_test_d)

        # Compare to global model performance on the same district subset
        idx = test_df["district"].to_numpy() == d
        global_pred_on_d = global_test_pred[idx]
        global_true_on_d = y_test[idx]
        global_m_on_d = metrics_dict(global_true_on_d, global_pred_on_d)

        district_rows.append(
            {
                "district": d,
                "train_rows": int(len(train_d)),
                "test_rows": int(len(test_d)),
                "district_model_r2": float(m_d["r2"]),
                "district_model_rmse": float(m_d["rmse"]),
                "global_on_d_r2": float(global_m_on_d["r2"]),
                "global_on_d_rmse": float(global_m_on_d["rmse"]),
                "improvement_r2": float(m_d["r2"] - global_m_on_d["r2"]),
                "improvement_rmse": float(global_m_on_d["rmse"] - m_d["rmse"]),
            }
        )

    district_models = pd.DataFrame(district_rows).sort_values(["improvement_r2", "district_model_r2"], ascending=False)

    district_models_path = out_dir / "district_models_test_scores.csv"
    district_models.to_csv(district_models_path, index=False)

    improvement_path = out_dir / "district_improvement_vs_global.csv"
    district_models[["district", "train_rows", "test_rows", "global_on_d_r2", "district_model_r2", "improvement_r2"]].to_csv(
        improvement_path, index=False
    )

    if not district_models.empty:
        make_barplot(
            district_models,
            x="district",
            y="improvement_r2",
            title=f"District model improvement over global (Test R², {cfg.test_year})",
            out_path=out_dir / "plot_improvement_vs_global.png",
            top_k=min(30, len(district_models)),
        )

    # -----------------------------
    # 3) ABLATION: cat-only vs cat+weather
    #    (Global + district deltas)
    # -----------------------------
    def run_global_ablation() -> Dict[str, Dict[str, float]]:
        # Cat-only
        pre_cat = build_preprocessor(cfg.categorical_features, [], scale_numeric=scale_numeric)
        Xtb = pre_cat.fit_transform(train_base_df[cfg.categorical_features])
        ytb = y_train_base
        Xv = pre_cat.transform(val_df[cfg.categorical_features])
        yv = y_val
        Xt = pre_cat.transform(train_df[cfg.categorical_features])
        yt = y_train
        Xte = pre_cat.transform(test_df[cfg.categorical_features])
        yte = y_test

        cat_params = dict(xgb_params)
        cat_params["n_estimators"] = 400

        cat_model = fit_xgb(
            X_train=Xtb,
            y_train=ytb,
            X_val=Xv,
            y_val=yv,
            params=cat_params,
            use_early_stopping=args.use_early_stopping,
            early_stopping_rounds=args.early_stopping_rounds,
        )
        cat_test_pred = cat_model.predict(Xte)
        cat_metrics = metrics_dict(yte, cat_test_pred)

        full_metrics = global_test_metrics
        delta_r2 = float(full_metrics["r2"] - cat_metrics["r2"])
        return {
            "cat_only": cat_metrics,
            "cat_plus_weather": full_metrics,
            "delta_r2_weather": {"r2": delta_r2},
        }

    ab_global = run_global_ablation()
    ablation_global_summary = pd.DataFrame(
        [
            {
                "model": "cat_only",
                "test_r2": ab_global["cat_only"]["r2"],
                "test_rmse": ab_global["cat_only"]["rmse"],
                "test_mae": ab_global["cat_only"]["mae"],
            },
            {
                "model": "cat_plus_weather",
                "test_r2": ab_global["cat_plus_weather"]["r2"],
                "test_rmse": ab_global["cat_plus_weather"]["rmse"],
                "test_mae": ab_global["cat_plus_weather"]["mae"],
            },
            {"model": "delta_weather", "test_r2": ab_global["delta_r2_weather"]["r2"], "test_rmse": np.nan, "test_mae": np.nan},
        ]
    )
    ablation_global_summary.to_csv(out_dir / "ablation_global_summary.csv", index=False)

    # District-level ablation delta: global model already computed (cat+weather).
    # Now compute global cat-only predictions per district and delta R².
    pre_cat_global = build_preprocessor(cfg.categorical_features, [], scale_numeric=scale_numeric)
    Xtb = pre_cat_global.fit_transform(train_base_df[cfg.categorical_features])
    ytb = y_train_base
    Xv = pre_cat_global.transform(val_df[cfg.categorical_features])
    yv = y_val
    Xte = pre_cat_global.transform(test_df[cfg.categorical_features])
    yte = y_test

    cat_model_global = fit_xgb(
        X_train=Xtb,
        y_train=ytb,
        X_val=Xv,
        y_val=yv,
        params=dict(xgb_params),
        use_early_stopping=args.use_early_stopping,
        early_stopping_rounds=args.early_stopping_rounds,
    )
    cat_test_pred_global = cat_model_global.predict(Xte)

    ablation_district_rows = []
    test_districts = test_df["district"].to_numpy()

    # cat-only by district
    cat_by_dist = eval_by_district(
        y_true=yte,
        y_pred=cat_test_pred_global,
        districts=test_districts,
        min_rows=args.min_test_rows_per_district,
    ).rename(columns={"r2": "r2_cat_only", "rmse": "rmse_cat_only", "mae": "mae_cat_only"})

    # cat+weather by district (from global model)
    full_by_dist = global_by_dist.rename(columns={"r2": "r2_cat_weather", "rmse": "rmse_cat_weather", "mae": "mae_cat_weather"})

    ab_dist = pd.merge(cat_by_dist, full_by_dist, on=["district", "n_test"], how="inner")
    ab_dist["delta_r2_weather"] = ab_dist["r2_cat_weather"] - ab_dist["r2_cat_only"]
    ab_dist = ab_dist.sort_values(["delta_r2_weather", "n_test"], ascending=[False, False])

    ab_dist.to_csv(out_dir / "ablation_district_summary.csv", index=False)

    if not ab_dist.empty:
        make_barplot(
            ab_dist,
            x="district",
            y="delta_r2_weather",
            title=f"Weather contribution ΔR² by district (global model, {cfg.test_year})",
            out_path=out_dir / "plot_weather_delta_r2.png",
            top_k=min(30, len(ab_dist)),
        )

    # -----------------------------
    # 4) Model selection recommendation (global vs district vs hybrid)
    # -----------------------------
    # Join district improvement + weather delta + global-on-district
    rec = district_models.merge(
        ab_dist[["district", "delta_r2_weather"]],
        on="district",
        how="left",
    )

    # Simple policy:
    # - If district model improves R² by >= +0.05 and district has decent data => choose district
    # - Else choose global
    # - Hybrid overall if at least K districts qualify
    rec["recommended_model"] = np.where(
        (rec["improvement_r2"] >= 0.05) & (rec["test_rows"] >= args.min_test_rows_per_district),
        "district_model",
        "global_model",
    )

    # district "weather matters" label
    rec["weather_signal"] = np.where(rec["delta_r2_weather"].fillna(0.0) >= 0.05, "strong", "weak_or_unclear")

    rec_out = rec[
        [
            "district",
            "train_rows",
            "test_rows",
            "global_on_d_r2",
            "district_model_r2",
            "improvement_r2",
            "delta_r2_weather",
            "weather_signal",
            "recommended_model",
        ]
    ].sort_values(["recommended_model", "improvement_r2"], ascending=[True, False])

    rec_out_path = out_dir / "model_selection_recommendations.csv"
    rec_out.to_csv(rec_out_path, index=False)

    # Global decision summary
    n_eligible = int((rec_out["recommended_model"] == "district_model").sum())
    total_scored = int(len(rec_out))
    decision = "hybrid" if n_eligible >= max(5, int(0.25 * max(1, total_scored))) else "global_with_optional_poc_district"

    summary = {
        "rows_loaded": int(len(df)),
        "rows_after_filters": int(len(fdf)),
        "global_test_metrics": global_test_metrics,
        "global_train_metrics": global_train_metrics,
        "district_models_scored": total_scored,
        "district_models_recommended": n_eligible,
        "overall_recommendation": decision,
        "policy": {
            "min_train_rows_per_district_model": args.min_train_rows_per_district_model,
            "min_test_rows_per_district": args.min_test_rows_per_district,
            "district_upgrade_threshold_improvement_r2": 0.05,
            "weather_signal_threshold_delta_r2": 0.05,
        },
        "paths": {
            "global_test_by_district": str(global_by_dist_path),
            "district_models_test_scores": str(district_models_path),
            "district_improvement_vs_global": str(improvement_path),
            "ablation_global_summary": str(out_dir / "ablation_global_summary.csv"),
            "ablation_district_summary": str(out_dir / "ablation_district_summary.csv"),
            "model_selection_recommendations": str(rec_out_path),
        },
    }

    (out_dir / "diagnostics_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print("\nSaved outputs to:", out_dir)
    print("Overall recommendation:", decision)
    print("District models recommended:", n_eligible, "out of", total_scored)
    print("Key files:")
    for k, v in summary["paths"].items():
        print(f"  - {k}: {v}")


if __name__ == "__main__":
    main()
