import duckdb
from pathlib import Path

BASE = Path(__file__).resolve().parent
DB_PATH = BASE / "agri_validation.duckdb"

# Output CSVs so you can open in Excel quickly
OUT_YEAR_CROP_DISTRICTS = BASE / "phase1_year_crop_district_counts.csv"
OUT_YEAR_DISTINCT_DISTRICTS = BASE / "phase1_year_total_districts.csv"

con = duckdb.connect(str(DB_PATH))

# 1) Build a clean "production only (metric tonnes)" view.
#    We do NOT aggregate mandals here; we just standardize strings and filter units.
con.execute("""
CREATE OR REPLACE VIEW v_prod_metric AS
SELECT
    TRIM(CAST(year AS VARCHAR)) AS year_label,
    LOWER(TRIM(CAST(district AS VARCHAR))) AS district,
    LOWER(TRIM(CAST(crop_name AS VARCHAR))) AS crop_name,
    CAST(value AS DOUBLE) AS production_mt
FROM tg_raw
WHERE LOWER(TRIM(CAST(area_production AS VARCHAR))) = 'production in metric tonnes'
  AND value IS NOT NULL;
""")

# 2) Year-wise total unique districts present (useful to pick a threshold)
con.execute("""
CREATE OR REPLACE TABLE t_year_total_districts AS
SELECT
    year_label,
    COUNT(DISTINCT district) AS total_districts_in_year
FROM v_prod_metric
GROUP BY 1
ORDER BY 1;
""")

# 3) For EACH YEAR: for EACH CROP: count number of districts where it appears
con.execute("""
CREATE OR REPLACE TABLE t_year_crop_district_counts AS
SELECT
    year_label,
    crop_name,
    COUNT(DISTINCT district) AS district_count,
    SUM(production_mt) AS production_mt_sum,
    COUNT(*) AS row_count
FROM v_prod_metric
GROUP BY 1,2
ORDER BY year_label, district_count DESC, production_mt_sum DESC;
""")

# 4) Print a readable snapshot to the terminal (top crops per year)
years = [r[0] for r in con.execute("SELECT DISTINCT year_label FROM t_year_crop_district_counts ORDER BY year_label").fetchall()]

print("\n=== Year-wise: Top crops by district coverage (metric tonnes only) ===")
for y in years:
    print(f"\n--- {y} ---")
    rows = con.execute("""
        SELECT crop_name, district_count, production_mt_sum
        FROM t_year_crop_district_counts
        WHERE year_label = ?
        ORDER BY district_count DESC, production_mt_sum DESC
        LIMIT 25;
    """, [y]).fetchall()
    for crop_name, district_count, prod_sum in rows:
        print(f"{crop_name:40s}  districts={district_count:3d}  prod_mt_sum={prod_sum:,.2f}")

# 5) Export CSVs for your manual threshold decision
con.execute(f"""
COPY t_year_crop_district_counts
TO '{OUT_YEAR_CROP_DISTRICTS.as_posix()}'
(HEADER, DELIMITER ',');
""")

con.execute(f"""
COPY t_year_total_districts
TO '{OUT_YEAR_DISTINCT_DISTRICTS.as_posix()}'
(HEADER, DELIMITER ',');
""")

print("\nWrote:")
print(" -", OUT_YEAR_CROP_DISTRICTS)
print(" -", OUT_YEAR_DISTINCT_DISTRICTS)

con.close()
