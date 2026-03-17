from __future__ import annotations

import argparse
import subprocess
from io import StringIO
from pathlib import Path

import joblib
import numpy as np
import pandas as pd


def load_from_duckdb(db_path: Path, duckdb_cli: Path, query: str) -> pd.DataFrame:
    try:
        import duckdb  # type: ignore

        con = duckdb.connect(str(db_path))
        df = con.execute(query).fetchdf()
        con.close()
        return df
    except ModuleNotFoundError:
        result = subprocess.run(
            [str(duckdb_cli), str(db_path), "-csv", query],
            check=True,
            capture_output=True,
            text=True,
        )
        return pd.read_csv(StringIO(result.stdout))


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


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--month_from", required=True, help="YYYY-MM-01")
    parser.add_argument("--month_to", required=True, help="YYYY-MM-01")
    parser.add_argument("--district", default=None)
    parser.add_argument("--amc", default=None)
    parser.add_argument("--crop_name", default=None)
    args = parser.parse_args()

    base_dir = Path(__file__).resolve().parent
    agri_prod_dir = base_dir.parent / "AgricultureProd"
    outputs_dir = base_dir / "outputs"
    outputs_dir.mkdir(parents=True, exist_ok=True)

    db_path = agri_prod_dir / "agri_validation.duckdb"
    duckdb_cli = agri_prod_dir / "tools" / "duckdb" / "duckdb.exe"

    df = load_from_duckdb(db_path, duckdb_cli, "SELECT * FROM v_model2_adjust_dataset")
    if df.empty:
        raise SystemExit("v_model2_adjust_dataset is empty. Run SQL stages first.")
    df["month_start"] = pd.to_datetime(df["month_start"])
    df = add_time_features(df)

    month_from = pd.Timestamp(args.month_from)
    month_to = pd.Timestamp(args.month_to)
    mask = (df["month_start"] >= month_from) & (df["month_start"] <= month_to)
    if args.district:
        mask &= df["district"].str.lower() == args.district.lower()
    if args.amc:
        mask &= df["amc"].str.lower() == args.amc.lower()
    if args.crop_name:
        mask &= df["crop_name"].str.lower() == args.crop_name.lower()
    pred_df = df[mask].copy()
    if pred_df.empty:
        raise SystemExit("No rows matched filters/month range.")

    base_bundle = joblib.load(outputs_dir / "m2_base_model.pkl")
    base_model = base_bundle["pipeline"]
    base_features = base_bundle["features"]
    for c in base_features:
        if c not in pred_df.columns:
            pred_df[c] = np.nan
    pred_df["base_pred"] = base_model.predict(pred_df[base_features])
    pred_df["base_pred"] = pred_df["base_pred"].clip(lower=0.0)

    pred_df["adjust_pred"] = np.nan
    adjust_path = outputs_dir / "m2_adjust_model.pkl"
    if adjust_path.exists():
        adjust_bundle = joblib.load(adjust_path)
        if isinstance(adjust_bundle, dict) and "pipeline" in adjust_bundle:
            adj_model = adjust_bundle["pipeline"]
            adj_features = adjust_bundle["features"]
            for c in adj_features:
                if c not in pred_df.columns:
                    pred_df[c] = np.nan
            has_yield = pred_df["yield_signal"].notna()
            if has_yield.any():
                pred_df.loc[has_yield, "adjust_pred"] = adj_model.predict(pred_df.loc[has_yield, adj_features])

    pred_df["final_pred"] = pred_df["base_pred"] + pred_df["adjust_pred"].fillna(0.0)
    pred_df["final_pred"] = pred_df["final_pred"].clip(lower=0.0)
    out_cols = [
        "month_start",
        "district",
        "amc",
        "crop_name",
        "season_norm",
        "modal_price_mean",
        "yield_signal",
        "base_pred",
        "adjust_pred",
        "final_pred",
    ]
    pred_df[out_cols].sort_values(["month_start", "district", "amc", "crop_name"]).to_csv(
        outputs_dir / "m2_forecast.csv", index=False
    )
    print(f"Wrote forecast: {outputs_dir / 'm2_forecast.csv'} rows={len(pred_df)}")


if __name__ == "__main__":
    main()
