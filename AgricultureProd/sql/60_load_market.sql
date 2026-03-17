DROP TABLE IF EXISTS t_market_raw;

CREATE TABLE t_market_raw AS
SELECT
    TRY_CAST(DDate AS DATE) AS obs_date,
    LOWER(TRIM(CAST(District AS VARCHAR))) AS district,
    LOWER(TRIM(CAST(AmcName AS VARCHAR))) AS amc,
    LOWER(TRIM(CAST(CommName AS VARCHAR))) AS crop_name,
    TRY_CAST(Arrivals AS DOUBLE) AS arrivals,
    TRY_CAST(Model AS DOUBLE) AS modal_price,
    TRY_CAST(Minimum AS DOUBLE) AS min_price,
    TRY_CAST(Maximum AS DOUBLE) AS max_price,
    'C:/Users/footb/Desktop/AgriFore/AgriMarket/final_agriculture_cleaned.csv' AS source_file
FROM read_csv_auto(
    'C:/Users/footb/Desktop/AgriFore/AgriMarket/final_agriculture_cleaned.csv',
    header = true
);

DROP TABLE IF EXISTS t_market_clean;

CREATE TABLE t_market_clean AS
WITH sanitized AS (
    SELECT
        obs_date,
        district,
        amc,
        crop_name,
        CASE
            WHEN arrivals IS NULL OR arrivals <= 0 OR arrivals > 50000000 THEN NULL
            ELSE arrivals
        END AS arrivals,
        CASE
            WHEN min_price IS NULL OR min_price <= 0 OR min_price > 200000 THEN NULL
            ELSE min_price
        END AS min_price,
        CASE
            WHEN max_price IS NULL OR max_price <= 0 OR max_price > 200000 THEN NULL
            ELSE max_price
        END AS max_price,
        CASE
            WHEN modal_price IS NULL OR modal_price <= 0 OR modal_price > 200000 THEN NULL
            ELSE modal_price
        END AS modal_price,
        source_file
    FROM t_market_raw
)
SELECT
    obs_date,
    district,
    amc,
    crop_name,
    arrivals,
    min_price,
    max_price,
    modal_price,
    source_file
FROM sanitized
WHERE obs_date IS NOT NULL
  AND district IS NOT NULL AND district <> ''
  AND amc IS NOT NULL AND amc <> ''
  AND crop_name IS NOT NULL AND crop_name <> ''
  AND NOT (min_price IS NOT NULL AND max_price IS NOT NULL AND min_price > max_price)
  AND (
      min_price IS NULL
      OR max_price IS NULL
      OR (modal_price BETWEEN min_price AND max_price)
  )
  AND modal_price IS NOT NULL;
