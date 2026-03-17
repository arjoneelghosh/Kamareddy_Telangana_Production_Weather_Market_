# Telangana DuckDB Pipeline

Run the full pipeline with:

```powershell
powershell -ExecutionPolicy Bypass -File .\run_duckdb_pipeline.ps1
```

This will:
- load all Telangana horticulture CSVs into `tg_raw`
- build `v_prod_real`, `v_area_real`, and analysis tables
- load and clean weather data into `weather_raw`, `weather_clean`, `v_weather_clean_std`
- build weather feature tables `t_weather_district_day`, `t_weather_district_month`, and `t_weather_district_season`
- export CSV outputs into `outputs/`

Outputs:
- `crop_year_coverage.csv`: per year/crop production coverage by district and mandal counts.
- `crop_stability.csv`: crops seen in all four years with minimum geographic footprint.
- `yield_sanity_by_year.csv`: median/p90/max production-per-acre sanity profile by year.
- `yield_outliers_by_year.csv`: yearly outlier incidence summary after robust MAD-based scoring.
- `yield_outliers_top50.csv`: highest production-per-acre rows with outlier flags and provenance.
- `season_coverage.csv`: season completeness profile by year and season bucket.
- `harvest_year_rollup.csv`: season-adjusted harvest-year production/area rollup with yield proxy.
- `weather_duplicates_by_year.csv`: yearly raw-vs-dedup weather row counts and duplicate removal.
- `weather_key_multiplicity.csv`: multiplicity distribution for dedup keys in weather cleaning.
- `weather_coverage_by_year.csv`: district/mandal coverage and observation-day completeness by year.
- `weather_district_seasonal.csv`: district-level kharif/rabi seasonal rainfall and humidity features by production-style year label.
- `weather_seasonal_coverage.csv`: district coverage and days-covered summary by seasonal year label.
- `model1_dataset.csv`: final Model 1 training dataset (production labels left-joined to seasonal district weather features).
- `model1_join_coverage.csv`: year/season join coverage from labels to weather.
- `model1_missing_districts.csv`: top missing-weather districts in Model 1 labels by weighted crop rows.

Quick sanity:

```sql
SELECT season_norm, COUNT(*) FROM v_prod_real GROUP BY season_norm ORDER BY COUNT(*) DESC;
```

```sql
SELECT * FROM read_csv_auto('outputs/yield_outliers_by_year.csv', header=true);
```

```sql
SELECT harvest_year, season_final, COUNT(*) FROM t_harvest_year_rollup GROUP BY 1,2 ORDER BY 1,2;
```

```sql
SELECT year, COUNT(*) FROM weather_clean GROUP BY year ORDER BY year;
```

```sql
SELECT year, district, SUM(rain_sum_mm) AS yearly_rain
FROM t_weather_district_month
GROUP BY 1,2
ORDER BY 1,3 DESC
LIMIT 10;
```

```sql
SELECT year_label, season_norm, COUNT(*)
FROM t_weather_district_season
GROUP BY 1,2
ORDER BY 1,2;
```

```sql
SELECT year_label, season_norm, COUNT(*)
FROM t_model1_dataset
GROUP BY 1,2
ORDER BY 1,2;
```

```sql
SELECT dq_weather_missing, COUNT(*)
FROM t_model1_dataset
GROUP BY 1
ORDER BY 1;
```

Train Model 1 baseline:

```bash
python tools/train_model1_weather_to_yield.py
```

Generated artifacts:
- `outputs/model1_rf.joblib`
- `outputs/model1_feature_importance.csv`
- `outputs/model1_metadata.json`
