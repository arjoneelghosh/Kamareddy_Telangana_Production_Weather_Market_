DROP TABLE IF EXISTS t_crop_year_coverage;

CREATE TABLE t_crop_year_coverage AS
SELECT
    year_label,
    crop_name,
    COUNT(DISTINCT district) AS district_count,
    COUNT(DISTINCT mandal) AS mandal_count,
    SUM(value) AS production_sum
FROM v_prod_real
GROUP BY year_label, crop_name;

DROP TABLE IF EXISTS t_crop_stability;

CREATE TABLE t_crop_stability AS
WITH per_year AS (
    SELECT
        crop_name,
        year_label,
        COUNT(DISTINCT district) AS districts_in_year,
        COUNT(DISTINCT mandal) AS mandals_in_year
    FROM v_prod_real
    GROUP BY crop_name, year_label
),
aggregated AS (
    SELECT
        crop_name,
        COUNT(*) AS years_present,
        MIN(districts_in_year) AS min_districts_any_year,
        MIN(mandals_in_year) AS min_mandals_any_year
    FROM per_year
    GROUP BY crop_name
)
SELECT
    crop_name,
    min_districts_any_year,
    min_mandals_any_year
FROM aggregated
WHERE years_present = 4;

DROP TABLE IF EXISTS t_yield_join_check;

CREATE TABLE t_yield_join_check AS
WITH p_base AS (
    SELECT
        ROW_NUMBER() OVER () AS prod_row_id,
        *
    FROM v_prod_real
),
season_matches AS (
    SELECT
        p.prod_row_id,
        p.year_label,
        p.year_start AS p_year_start,
        p.year_end AS p_year_end,
        a.year_start AS a_year_start,
        a.year_end AS a_year_end,
        p.district,
        p.mandal,
        p.crop_name,
        p.season_norm AS p_season_norm,
        a.season_norm AS a_season_norm,
        p.value AS production_value,
        a.value AS area_acres,
        p.source_file AS prod_source_file,
        a.source_file AS area_source_file,
        ROW_NUMBER() OVER (
            PARTITION BY p.prod_row_id
            ORDER BY
                CASE
                    WHEN p.season_norm = a.season_norm THEN 0
                    WHEN p.season_norm IS NULL OR a.season_norm IS NULL THEN 1
                    ELSE 2
                END,
                a.source_file,
                a.division_norm,
                a.crop_type_norm
        ) AS rn
    FROM p_base AS p
    JOIN v_area_real AS a
      ON p.year_label = a.year_label
     AND p.district   = a.district
     AND p.mandal     = a.mandal
     AND p.crop_name  = a.crop_name
     AND (
          p.season_norm = a.season_norm
          OR p.season_norm IS NULL
          OR a.season_norm IS NULL
     )
),
fallback_matches AS (
    SELECT
        p.prod_row_id,
        p.year_label,
        p.year_start AS p_year_start,
        p.year_end AS p_year_end,
        a.year_start AS a_year_start,
        a.year_end AS a_year_end,
        p.district,
        p.mandal,
        p.crop_name,
        p.season_norm AS p_season_norm,
        a.season_norm AS a_season_norm,
        p.value AS production_value,
        a.value AS area_acres,
        p.source_file AS prod_source_file,
        a.source_file AS area_source_file,
        ROW_NUMBER() OVER (
            PARTITION BY p.prod_row_id
            ORDER BY a.source_file, a.division_norm, a.crop_type_norm
        ) AS rn
    FROM p_base AS p
    JOIN v_area_real AS a
      ON p.year_label = a.year_label
     AND p.district   = a.district
     AND p.mandal     = a.mandal
     AND p.crop_name  = a.crop_name
    WHERE NOT EXISTS (
        SELECT 1
        FROM season_matches AS sm
        WHERE sm.prod_row_id = p.prod_row_id
    )
),
chosen AS (
    SELECT * FROM season_matches WHERE rn = 1
    UNION ALL
    SELECT * FROM fallback_matches WHERE rn = 1
)
SELECT
    year_label,
    COALESCE(p_year_start, a_year_start) AS year_start,
    COALESCE(p_year_end, a_year_end) AS year_end,
    district,
    mandal,
    crop_name,
    COALESCE(p_season_norm, a_season_norm) AS season_final,
    production_value,
    area_acres,
    production_value / NULLIF(area_acres, 0) AS prod_per_acre,
    prod_source_file,
    area_source_file
FROM chosen;

COPY (
    SELECT
        year_label,
        crop_name,
        district_count,
        mandal_count,
        production_sum
    FROM t_crop_year_coverage
    ORDER BY year_label, crop_name
) TO 'outputs/crop_year_coverage.csv' (HEADER, DELIMITER ',');

COPY (
    SELECT
        crop_name,
        min_districts_any_year,
        min_mandals_any_year
    FROM t_crop_stability
    ORDER BY crop_name
) TO 'outputs/crop_stability.csv' (HEADER, DELIMITER ',');

COPY (
    SELECT
        year_label,
        quantile_cont(prod_per_acre, 0.5) AS median_prod_per_acre,
        quantile_cont(prod_per_acre, 0.9) AS p90_prod_per_acre,
        MAX(prod_per_acre) AS max_prod_per_acre
    FROM t_yield_join_check
    WHERE prod_per_acre IS NOT NULL
    GROUP BY year_label
    ORDER BY year_label
) TO 'outputs/yield_sanity_by_year.csv' (HEADER, DELIMITER ',');
