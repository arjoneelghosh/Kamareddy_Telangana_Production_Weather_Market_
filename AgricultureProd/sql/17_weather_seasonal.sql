DROP TABLE IF EXISTS t_weather_district_season;

CREATE TABLE t_weather_district_season AS
WITH tagged AS (
    SELECT
        district,
        obs_date,
        rain_mm_med,
        hum_min_avg,
        hum_max_avg,
        mandals_reporting,
        CASE
            WHEN MONTH(obs_date) BETWEEN 6 AND 9 THEN 'kharif'
            WHEN MONTH(obs_date) BETWEEN 10 AND 12 THEN 'rabi'
            WHEN MONTH(obs_date) BETWEEN 1 AND 3 THEN 'rabi'
            ELSE NULL
        END AS season_norm,
        CASE
            WHEN MONTH(obs_date) BETWEEN 6 AND 9 THEN YEAR(obs_date)
            WHEN MONTH(obs_date) BETWEEN 10 AND 12 THEN YEAR(obs_date)
            WHEN MONTH(obs_date) BETWEEN 1 AND 3 THEN YEAR(obs_date) - 1
            ELSE NULL
        END AS year_start
    FROM t_weather_district_day
),
seasonal_base AS (
    SELECT
        year_start,
        year_start + 1 AS year_end,
        CAST(year_start AS VARCHAR) || '-' || lpad(CAST(((year_start + 1) % 100) AS VARCHAR), 2, '0') AS year_label,
        district,
        season_norm,
        obs_date,
        rain_mm_med,
        hum_min_avg,
        hum_max_avg,
        mandals_reporting
    FROM tagged
    WHERE season_norm IS NOT NULL
      AND year_start IS NOT NULL
      AND MONTH(obs_date) NOT IN (4, 5)
)
SELECT
    year_label,
    year_start,
    year_end,
    district,
    season_norm,
    SUM(rain_mm_med) AS rain_total_mm,
    SUM(CASE WHEN rain_mm_med >= 2 THEN 1 ELSE 0 END) AS rainy_days_total,
    AVG(hum_min_avg) AS hum_min_avg,
    AVG(hum_max_avg) AS hum_max_avg,
    AVG(mandals_reporting) AS avg_mandals_reporting,
    COUNT(*) AS days_covered,
    COUNT(DISTINCT MONTH(obs_date)) AS months_covered
FROM seasonal_base
GROUP BY year_label, year_start, year_end, district, season_norm;

COPY (
    SELECT
        year_label,
        year_start,
        year_end,
        district,
        season_norm,
        rain_total_mm,
        rainy_days_total,
        hum_min_avg,
        hum_max_avg,
        avg_mandals_reporting,
        days_covered,
        months_covered
    FROM t_weather_district_season
    ORDER BY year_start, season_norm, district
) TO 'outputs/weather_district_seasonal.csv' (HEADER, DELIMITER ',');

COPY (
    SELECT
        year_label,
        season_norm,
        COUNT(*) AS districts_covered,
        MIN(days_covered) AS min_days,
        quantile_cont(days_covered, 0.5) AS p50_days,
        MAX(days_covered) AS max_days
    FROM t_weather_district_season
    GROUP BY year_label, season_norm
    ORDER BY year_label, season_norm
) TO 'outputs/weather_seasonal_coverage.csv' (HEADER, DELIMITER ',');

COPY (
    SELECT
        year_label,
        season_norm,
        district,
        rain_total_mm,
        rainy_days_total,
        days_covered,
        months_covered
    FROM t_weather_district_season
    ORDER BY rain_total_mm DESC
    LIMIT 10
) TO 'outputs/top10_wettest_district_seasons.csv' (HEADER, DELIMITER ',');
