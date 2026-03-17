DROP VIEW IF EXISTS v_model2_base_dataset;

CREATE VIEW v_model2_base_dataset AS
SELECT
    m.month_start,
    m.district,
    m.amc,
    m.crop_name,
    regexp_replace(lower(trim(m.crop_name)), '\s+', ' ', 'g') AS crop_key,
    c.season_norm,
    c.year_label,
    c.year_start,
    c.year_end,
    m.modal_price_mean,
    m.min_price_mean,
    m.max_price_mean,
    m.arrivals_sum,
    m.n_days,
    w.rain_sum_mm,
    w.rainy_days,
    w.hum_min_avg,
    w.hum_max_avg,
    w.avg_mandals_reporting
FROM t_market_monthly AS m
LEFT JOIN v_month_to_season AS c
  ON m.month_start = c.month_start
LEFT JOIN t_weather_district_month AS w
  ON m.district = w.district
 AND YEAR(m.month_start) = w.yyyy
 AND MONTH(m.month_start) = w.mm;
