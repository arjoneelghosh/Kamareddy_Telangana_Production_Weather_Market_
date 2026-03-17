DROP VIEW IF EXISTS v_model2_adjust_dataset;

CREATE VIEW v_model2_adjust_dataset AS
SELECT
    b.month_start,
    b.district,
    b.amc,
    b.crop_name,
    b.season_norm,
    b.year_label,
    b.year_start,
    b.year_end,
    b.modal_price_mean,
    b.min_price_mean,
    b.max_price_mean,
    b.arrivals_sum,
    b.n_days,
    b.rain_sum_mm,
    b.rainy_days,
    b.hum_min_avg,
    b.hum_max_avg,
    b.avg_mandals_reporting,
    y.yield_per_acre_proxy AS yield_signal,
    y.dq_weather_incomplete
FROM v_model2_base_dataset AS b
LEFT JOIN t_yield_seasonal AS y
  ON b.year_label = y.year_label
 AND b.district = y.district
 AND b.season_norm = y.season_norm
 AND b.crop_key = y.crop_key;
