DROP TABLE IF EXISTS t_market_monthly;

CREATE TABLE t_market_monthly AS
SELECT
    CAST(date_trunc('month', obs_date) AS DATE) AS month_start,
    district,
    amc,
    crop_name,
    AVG(modal_price) AS modal_price_mean,
    AVG(min_price) AS min_price_mean,
    AVG(max_price) AS max_price_mean,
    SUM(arrivals) AS arrivals_sum,
    COUNT(*) AS n_days
FROM t_market_clean
GROUP BY 1, 2, 3, 4;
