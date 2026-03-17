from io import StringIO
from pathlib import Path
import subprocess

import pandas as pd


def main() -> None:
    base = Path(__file__).resolve().parent
    db_path = base / "agri_validation.duckdb"
    duckdb_cli = base / "tools" / "duckdb" / "duckdb.exe"
    model1_csv = base / "outputs" / "model1_dataset.csv"

    years = ["2020-21", "2021-22", "2022-23"]

    query = """
        SELECT
            year_label,
            rain_total_mm,
            rainy_days_total,
            days_covered,
            months_covered
        FROM t_weather_district_season
        WHERE lower(district) = 'kamareddy'
          AND season_norm = 'rabi'
          AND year_label IN ('2020-21', '2021-22', '2022-23')
        ORDER BY year_label
    """

    try:
        import duckdb  # type: ignore

        con = duckdb.connect(str(db_path))
        rebuilt = con.execute(query).fetchdf()
        con.close()
    except ModuleNotFoundError:
        if not duckdb_cli.exists():
            raise FileNotFoundError(
                "duckdb Python module is missing and bundled DuckDB CLI was not found at "
                f"{duckdb_cli}"
            )
        result = subprocess.run(
            [str(duckdb_cli), str(db_path), "-csv", query],
            check=True,
            capture_output=True,
            text=True,
        )
        rebuilt = pd.read_csv(StringIO(result.stdout))

    print("=== Rebuilt seasonal table: kamareddy + rabi ===")
    print(rebuilt.to_string(index=False))

    if not model1_csv.exists():
        raise FileNotFoundError(f"Missing model1 dataset CSV: {model1_csv}")

    model1 = pd.read_csv(model1_csv)
    for col in ["district", "season_norm", "year_label"]:
        if col not in model1.columns:
            raise ValueError(f"Missing required column in model1 CSV: {col}")

    old_grouped = (
        model1[
            (model1["district"].astype(str).str.lower() == "kamareddy")
            & (model1["season_norm"].astype(str).str.lower() == "rabi")
            & (model1["year_label"].astype(str).isin(years))
        ]
        .groupby("year_label", as_index=False)
        .agg(
            old_rain_total_mm=("rain_total_mm", "mean"),
            old_rainy_days_total=("rainy_days_total", "mean"),
            old_days_covered=("days_covered", "mean"),
            old_months_covered=("months_covered", "mean"),
        )
        .sort_values("year_label")
    )

    print("\n=== outputs/model1_dataset.csv grouped: kamareddy + rabi ===")
    print(old_grouped.to_string(index=False))

    compare = rebuilt.merge(old_grouped, on="year_label", how="outer")
    compare["delta_rain_total_mm"] = compare["rain_total_mm"] - compare["old_rain_total_mm"]
    compare["delta_rainy_days_total"] = compare["rainy_days_total"] - compare["old_rainy_days_total"]
    compare["delta_days_covered"] = compare["days_covered"] - compare["old_days_covered"]
    compare["delta_months_covered"] = compare["months_covered"] - compare["old_months_covered"]

    print("\n=== Comparison (rebuilt - model1_csv_grouped) ===")
    print(compare.sort_values("year_label").to_string(index=False))


if __name__ == "__main__":
    main()
