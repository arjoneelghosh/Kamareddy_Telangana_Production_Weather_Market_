DROP VIEW IF EXISTS v_prod_real;

CREATE VIEW v_prod_real AS
WITH enriched AS (
    SELECT
        TRIM(CAST(year AS VARCHAR)) AS year_label_raw,
        LOWER(TRIM(CAST(district AS VARCHAR))) AS district,
        LOWER(TRIM(CAST(mandal AS VARCHAR))) AS mandal,
        LOWER(TRIM(CAST(crop_name AS VARCHAR))) AS crop_name,
        LOWER(TRIM(CAST(area_production AS VARCHAR))) AS area_production_label,
        LOWER(TRIM(CAST(division AS VARCHAR))) AS division_norm,
        LOWER(TRIM(CAST(crop_type AS VARCHAR))) AS crop_type_norm,
        CASE
            WHEN season IS NULL OR trim(CAST(season AS VARCHAR)) = '' THEN NULL
            WHEN lower(trim(CAST(season AS VARCHAR))) LIKE '%kharif%' THEN 'kharif'
            WHEN lower(trim(CAST(season AS VARCHAR))) LIKE '%rabi%'   THEN 'rabi'
            ELSE NULL
        END AS season_norm,
        value,
        source_file
    FROM tg_raw
),
normalized AS (
    SELECT
        year_label_raw AS year_label,
        CASE
            WHEN regexp_full_match(year_label_raw, '^[0-9]{4}$') THEN CAST(year_label_raw AS INTEGER)
            WHEN regexp_full_match(year_label_raw, '^[0-9]{4}-[0-9]{2}$') THEN CAST(SUBSTR(year_label_raw, 1, 4) AS INTEGER)
            WHEN regexp_full_match(year_label_raw, '^[0-9]{4}-[0-9]{4}$') THEN CAST(SUBSTR(year_label_raw, 1, 4) AS INTEGER)
            ELSE NULL
        END AS year_start,
        CASE
            WHEN regexp_full_match(year_label_raw, '^[0-9]{4}$') THEN CAST(year_label_raw AS INTEGER)
            WHEN regexp_full_match(year_label_raw, '^[0-9]{4}-[0-9]{2}$') THEN
                CAST(SUBSTR(year_label_raw, 1, 4) AS INTEGER)
                + (
                    (CAST(SUBSTR(year_label_raw, 6, 2) AS INTEGER) - CAST(SUBSTR(year_label_raw, 3, 2) AS INTEGER) + 100) % 100
                )
            WHEN regexp_full_match(year_label_raw, '^[0-9]{4}-[0-9]{4}$') THEN CAST(SUBSTR(year_label_raw, 6, 4) AS INTEGER)
            ELSE NULL
        END AS year_end,
        district,
        mandal,
        crop_name,
        area_production_label,
        division_norm,
        crop_type_norm,
        season_norm,
        value,
        source_file
    FROM enriched
)
SELECT
    year_label,
    year_start,
    year_end,
    district,
    mandal,
    crop_name,
    season_norm,
    division_norm,
    crop_type_norm,
    source_file,
    value
FROM normalized
WHERE area_production_label = 'production'
  AND value IS NOT NULL
  AND value >= 0
  AND value < 1000000
  AND crop_name NOT LIKE 'grand total%'
  AND crop_name NOT LIKE 'total%'
  AND crop_name NOT LIKE 'sub total%'
  AND crop_name NOT LIKE 'others%'
  AND crop_name NOT LIKE 'other%'
  AND crop_name NOT LIKE '%etc%';

DROP VIEW IF EXISTS v_area_real;

CREATE VIEW v_area_real AS
WITH enriched AS (
    SELECT
        TRIM(CAST(year AS VARCHAR)) AS year_label_raw,
        LOWER(TRIM(CAST(district AS VARCHAR))) AS district,
        LOWER(TRIM(CAST(mandal AS VARCHAR))) AS mandal,
        LOWER(TRIM(CAST(crop_name AS VARCHAR))) AS crop_name,
        LOWER(TRIM(CAST(area_production AS VARCHAR))) AS area_production_label,
        LOWER(TRIM(CAST(division AS VARCHAR))) AS division_norm,
        LOWER(TRIM(CAST(crop_type AS VARCHAR))) AS crop_type_norm,
        CASE
            WHEN season IS NULL OR trim(CAST(season AS VARCHAR)) = '' THEN NULL
            WHEN lower(trim(CAST(season AS VARCHAR))) LIKE '%kharif%' THEN 'kharif'
            WHEN lower(trim(CAST(season AS VARCHAR))) LIKE '%rabi%'   THEN 'rabi'
            ELSE NULL
        END AS season_norm,
        value,
        source_file
    FROM tg_raw
),
normalized AS (
    SELECT
        year_label_raw AS year_label,
        CASE
            WHEN regexp_full_match(year_label_raw, '^[0-9]{4}$') THEN CAST(year_label_raw AS INTEGER)
            WHEN regexp_full_match(year_label_raw, '^[0-9]{4}-[0-9]{2}$') THEN CAST(SUBSTR(year_label_raw, 1, 4) AS INTEGER)
            WHEN regexp_full_match(year_label_raw, '^[0-9]{4}-[0-9]{4}$') THEN CAST(SUBSTR(year_label_raw, 1, 4) AS INTEGER)
            ELSE NULL
        END AS year_start,
        CASE
            WHEN regexp_full_match(year_label_raw, '^[0-9]{4}$') THEN CAST(year_label_raw AS INTEGER)
            WHEN regexp_full_match(year_label_raw, '^[0-9]{4}-[0-9]{2}$') THEN
                CAST(SUBSTR(year_label_raw, 1, 4) AS INTEGER)
                + (
                    (CAST(SUBSTR(year_label_raw, 6, 2) AS INTEGER) - CAST(SUBSTR(year_label_raw, 3, 2) AS INTEGER) + 100) % 100
                )
            WHEN regexp_full_match(year_label_raw, '^[0-9]{4}-[0-9]{4}$') THEN CAST(SUBSTR(year_label_raw, 6, 4) AS INTEGER)
            ELSE NULL
        END AS year_end,
        district,
        mandal,
        crop_name,
        area_production_label,
        division_norm,
        crop_type_norm,
        season_norm,
        value,
        source_file
    FROM enriched
)
SELECT
    year_label,
    year_start,
    year_end,
    district,
    mandal,
    crop_name,
    season_norm,
    division_norm,
    crop_type_norm,
    source_file,
    value
FROM normalized
WHERE area_production_label IN ('area', 'arearea')
  AND value IS NOT NULL
  AND value > 0
  AND crop_name NOT LIKE 'grand total%'
  AND crop_name NOT LIKE 'total%'
  AND crop_name NOT LIKE 'sub total%'
  AND crop_name NOT LIKE 'others%'
  AND crop_name NOT LIKE 'other%'
  AND crop_name NOT LIKE '%etc%';
