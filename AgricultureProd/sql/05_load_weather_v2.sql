DROP TABLE IF EXISTS weather_stage;

CREATE TABLE weather_stage (
    year INTEGER,
    district VARCHAR,
    mandal VARCHAR,
    obs_date DATE,
    rain_mm DOUBLE,
    hum_min DOUBLE,
    hum_max DOUBLE,
    source_file VARCHAR
);

INSERT INTO weather_stage
SELECT
    2018 AS year,
    LOWER(TRIM(CAST(district AS VARCHAR))) AS district,
    LOWER(TRIM(CAST(mandal AS VARCHAR))) AS mandal,
    TRY_CAST(Date AS DATE) AS obs_date,
    TRY_CAST(Rainfall_mm AS DOUBLE) AS rain_mm,
    TRY_CAST(humidity_min AS DOUBLE) AS hum_min,
    TRY_CAST(humidity_max AS DOUBLE) AS hum_max,
    'Weather/final_daily_rainfall_2018.csv' AS source_file
FROM read_csv_auto('Weather/final_daily_rainfall_2018.csv', header = true);

INSERT INTO weather_stage
SELECT
    2019 AS year,
    LOWER(TRIM(CAST(District AS VARCHAR))) AS district,
    LOWER(TRIM(CAST(Mandal AS VARCHAR))) AS mandal,
    TRY_CAST(Date AS DATE) AS obs_date,
    TRY_CAST(Rainfall AS DOUBLE) AS rain_mm,
    TRY_CAST(Humidity_Min AS DOUBLE) AS hum_min,
    TRY_CAST(Humidity_Max AS DOUBLE) AS hum_max,
    'Weather/final_daily_rainfall_2019.csv' AS source_file
FROM read_csv_auto('Weather/final_daily_rainfall_2019.csv', header = true);

INSERT INTO weather_stage
SELECT
    2020 AS year,
    LOWER(TRIM(CAST(District AS VARCHAR))) AS district,
    LOWER(TRIM(CAST(Mandal AS VARCHAR))) AS mandal,
    TRY_CAST(Date AS DATE) AS obs_date,
    TRY_CAST("Rainfall (mm)" AS DOUBLE) AS rain_mm,
    TRY_CAST("Min Humidity (%)" AS DOUBLE) AS hum_min,
    TRY_CAST("Max Humidity (%)" AS DOUBLE) AS hum_max,
    'Weather/final_daily_rainfall_2020.csv' AS source_file
FROM read_csv_auto('Weather/final_daily_rainfall_2020.csv', header = true);

INSERT INTO weather_stage
SELECT
    2021 AS year,
    LOWER(TRIM(CAST(District AS VARCHAR))) AS district,
    LOWER(TRIM(CAST(Mandal AS VARCHAR))) AS mandal,
    TRY_CAST(Date AS DATE) AS obs_date,
    TRY_CAST("Rain (mm)" AS DOUBLE) AS rain_mm,
    TRY_CAST("Min Humidity (%)" AS DOUBLE) AS hum_min,
    TRY_CAST("Max Humidity (%)" AS DOUBLE) AS hum_max,
    'Weather/final_daily_rainfall_2021.csv' AS source_file
FROM read_csv_auto('Weather/final_daily_rainfall_2021.csv', header = true);

INSERT INTO weather_stage
SELECT
    2022 AS year,
    LOWER(TRIM(CAST(District AS VARCHAR))) AS district,
    LOWER(TRIM(CAST(Mandal AS VARCHAR))) AS mandal,
    TRY_CAST(Date AS DATE) AS obs_date,
    TRY_CAST("Rain (mm)" AS DOUBLE) AS rain_mm,
    TRY_CAST("Min Humidity (%)" AS DOUBLE) AS hum_min,
    TRY_CAST("Max Humidity (%)" AS DOUBLE) AS hum_max,
    'Weather/final_daily_rainfall_2022.csv' AS source_file
FROM read_csv_auto('Weather/final_daily_rainfall_2022.csv', header = true);

INSERT INTO weather_stage
SELECT
    2023 AS year,
    LOWER(TRIM(CAST(District AS VARCHAR))) AS district,
    LOWER(TRIM(CAST(Mandal AS VARCHAR))) AS mandal,
    TRY_CAST(Date AS DATE) AS obs_date,
    TRY_CAST("Rain (mm)" AS DOUBLE) AS rain_mm,
    TRY_CAST("Min Humidity (%)" AS DOUBLE) AS hum_min,
    TRY_CAST("Max Humidity (%)" AS DOUBLE) AS hum_max,
    'Weather/final_daily_rainfall_2023.csv' AS source_file
FROM read_csv_auto('Weather/final_daily_rainfall_2023.csv', header = true);

INSERT INTO weather_stage
SELECT
    2024 AS year,
    LOWER(TRIM(CAST(District AS VARCHAR))) AS district,
    LOWER(TRIM(CAST(Mandal AS VARCHAR))) AS mandal,
    TRY_CAST(Date AS DATE) AS obs_date,
    TRY_CAST("Rain (mm)" AS DOUBLE) AS rain_mm,
    TRY_CAST("Min Humidity (%)" AS DOUBLE) AS hum_min,
    TRY_CAST("Max Humidity (%)" AS DOUBLE) AS hum_max,
    'Weather/final_daily_rainfall_2024.csv' AS source_file
FROM read_csv_auto('Weather/final_daily_rainfall_2024.csv', header = true);

INSERT INTO weather_stage
SELECT
    2025 AS year,
    LOWER(TRIM(CAST(District AS VARCHAR))) AS district,
    LOWER(TRIM(CAST(Mandal AS VARCHAR))) AS mandal,
    TRY_CAST(Date AS DATE) AS obs_date,
    TRY_CAST("Rain (mm)" AS DOUBLE) AS rain_mm,
    TRY_CAST("Min Humidity (%)" AS DOUBLE) AS hum_min,
    TRY_CAST("Max Humidity (%)" AS DOUBLE) AS hum_max,
    'Weather/final_daily_rainfall_2025.csv' AS source_file
FROM read_csv_auto('Weather/final_daily_rainfall_2025.csv', header = true);

INSERT INTO weather_stage
SELECT
    2026 AS year,
    LOWER(TRIM(CAST(District AS VARCHAR))) AS district,
    LOWER(TRIM(CAST(Mandal AS VARCHAR))) AS mandal,
    TRY_CAST(Date AS DATE) AS obs_date,
    TRY_CAST("Rain (mm)" AS DOUBLE) AS rain_mm,
    TRY_CAST("Min Humidity (%)" AS DOUBLE) AS hum_min,
    TRY_CAST("Max Humidity (%)" AS DOUBLE) AS hum_max,
    'Weather/final_daily_rainfall_2026.csv' AS source_file
FROM read_csv_auto('Weather/final_daily_rainfall_2026.csv', header = true);

DROP TABLE IF EXISTS weather_raw;

CREATE TABLE weather_raw AS
SELECT
    year,
    district,
    mandal,
    obs_date,
    rain_mm,
    CASE
        WHEN hum_min < 0 OR hum_min > 100 THEN NULL
        ELSE hum_min
    END AS hum_min,
    CASE
        WHEN hum_max < 0 OR hum_max > 100 THEN NULL
        ELSE hum_max
    END AS hum_max,
    source_file
FROM weather_stage
WHERE district IS NOT NULL
  AND district <> ''
  AND mandal IS NOT NULL
  AND mandal <> ''
  AND NOT regexp_full_match(mandal, '^[0-9]+$')
  AND obs_date IS NOT NULL;

DROP TABLE IF EXISTS weather_clean;

CREATE TABLE weather_clean AS
SELECT
    year,
    district,
    mandal,
    obs_date,
    MAX(rain_mm) AS rain_mm,
    MIN(hum_min) AS hum_min,
    MAX(hum_max) AS hum_max,
    COUNT(*) AS rows_per_key,
    ANY_VALUE(source_file) AS source_file
FROM weather_raw
GROUP BY year, district, mandal, obs_date;

DROP VIEW IF EXISTS v_weather_clean_std;

CREATE VIEW v_weather_clean_std AS
SELECT
    year,
    CASE
        WHEN district = 'hanumakkonda' THEN 'hanumakonda'
        ELSE district
    END AS district,
    mandal,
    obs_date,
    rain_mm,
    hum_min,
    hum_max,
    rows_per_key,
    source_file
FROM weather_clean;

COPY (
    WITH raw_counts AS (
        SELECT
            year,
            COUNT(*) AS total_rows_raw
        FROM weather_raw
        GROUP BY year
    ),
    clean_counts AS (
        SELECT
            year,
            COUNT(*) AS total_unique_keys_clean
        FROM weather_clean
        GROUP BY year
    )
    SELECT
        r.year,
        r.total_rows_raw,
        c.total_unique_keys_clean,
        r.total_rows_raw - c.total_unique_keys_clean AS duplicate_rows_removed
    FROM raw_counts AS r
    JOIN clean_counts AS c
      ON r.year = c.year
    ORDER BY r.year
) TO 'outputs/weather_duplicates_by_year.csv' (HEADER, DELIMITER ',');

COPY (
    SELECT
        rows_per_key,
        COUNT(*) AS count_keys
    FROM weather_clean
    GROUP BY rows_per_key
    ORDER BY rows_per_key
) TO 'outputs/weather_key_multiplicity.csv' (HEADER, DELIMITER ',');

COPY (
    WITH mandal_days AS (
        SELECT
            year,
            district,
            mandal,
            COUNT(DISTINCT obs_date) AS obs_days
        FROM v_weather_clean_std
        GROUP BY year, district, mandal
    ),
    base AS (
        SELECT
            year,
            COUNT(DISTINCT district) AS distinct_districts,
            COUNT(DISTINCT mandal) AS distinct_mandals
        FROM v_weather_clean_std
        GROUP BY year
    )
    SELECT
        b.year,
        b.distinct_districts,
        b.distinct_mandals,
        MIN(m.obs_days) AS min_obs_days_per_mandal,
        quantile_cont(m.obs_days, 0.5) AS p50_obs_days_per_mandal,
        MAX(m.obs_days) AS max_obs_days_per_mandal
    FROM base AS b
    JOIN mandal_days AS m
      ON b.year = m.year
    GROUP BY b.year, b.distinct_districts, b.distinct_mandals
    ORDER BY b.year
) TO 'outputs/weather_coverage_by_year.csv' (HEADER, DELIMITER ',');
