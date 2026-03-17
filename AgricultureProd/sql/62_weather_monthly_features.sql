DROP TABLE IF EXISTS t_weather_district_month;

CREATE TABLE t_weather_district_month AS
SELECT
    year,
    district,
    YEAR(obs_date) AS yyyy,
    MONTH(obs_date) AS mm,
    SUM(rain_mm_med) AS rain_sum_mm,
    COUNT(*) FILTER (WHERE rain_mm_med >= 2) AS rainy_days,
    AVG(hum_min_avg) AS hum_min_avg,
    AVG(hum_max_avg) AS hum_max_avg,
    AVG(mandals_reporting) AS avg_mandals_reporting
FROM t_weather_district_day
GROUP BY year, district, YEAR(obs_date), MONTH(obs_date);
