DROP TABLE IF EXISTS t_season_coverage;

CREATE TABLE t_season_coverage AS
SELECT
    year_label,
    season_final,
    COUNT(*) AS row_count,
    COUNT(DISTINCT crop_name) AS distinct_crop_count,
    SUM(CASE WHEN season_final IS NULL THEN 1 ELSE 0 END) AS missing_season_rows
FROM t_yield_join_check
GROUP BY year_label, season_final;

COPY (
    SELECT
        year_label,
        season_final,
        row_count,
        distinct_crop_count,
        missing_season_rows
    FROM t_season_coverage
    ORDER BY year_label, season_final
) TO 'outputs/season_coverage.csv' (HEADER, DELIMITER ',');

DROP TABLE IF EXISTS t_harvest_year_rollup;

CREATE TABLE t_harvest_year_rollup AS
SELECT
    CASE
        WHEN season_final IN ('rabi', 'summer') THEN year_end
        WHEN season_final = 'kharif' THEN year_start
        ELSE year_end
    END AS harvest_year,
    season_final,
    crop_name,
    SUM(production_value) AS total_production_value,
    SUM(area_acres) AS total_area_acres,
    SUM(production_value) / NULLIF(SUM(area_acres), 0) AS yield_per_acre_proxy
FROM t_yield_join_check
WHERE production_value IS NOT NULL
  AND area_acres IS NOT NULL
  AND production_value > 0
  AND area_acres > 0
  AND production_value < 1000000
GROUP BY
    CASE
        WHEN season_final IN ('rabi', 'summer') THEN year_end
        WHEN season_final = 'kharif' THEN year_start
        ELSE year_end
    END,
    season_final,
    crop_name;

COPY (
    SELECT
        harvest_year,
        season_final,
        crop_name,
        total_production_value,
        total_area_acres,
        yield_per_acre_proxy
    FROM t_harvest_year_rollup
    ORDER BY harvest_year, season_final, crop_name
) TO 'outputs/harvest_year_rollup.csv' (HEADER, DELIMITER ',');
