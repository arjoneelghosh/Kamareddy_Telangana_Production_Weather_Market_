DROP VIEW IF EXISTS v_month_to_season;

CREATE VIEW v_month_to_season AS
WITH base AS (
    SELECT DISTINCT month_start
    FROM t_market_monthly
),
tagged AS (
    SELECT
        month_start,
        CASE
            WHEN MONTH(month_start) BETWEEN 6 AND 9 THEN 'kharif'
            WHEN MONTH(month_start) BETWEEN 10 AND 12 THEN 'rabi'
            WHEN MONTH(month_start) BETWEEN 1 AND 3 THEN 'rabi'
            ELSE NULL
        END AS season_norm,
        CASE
            WHEN MONTH(month_start) BETWEEN 6 AND 9 THEN YEAR(month_start)
            WHEN MONTH(month_start) BETWEEN 10 AND 12 THEN YEAR(month_start)
            WHEN MONTH(month_start) BETWEEN 1 AND 3 THEN YEAR(month_start) - 1
            ELSE NULL
        END AS year_start
    FROM base
)
SELECT
    month_start,
    season_norm,
    year_start,
    year_start + 1 AS year_end,
    CASE
        WHEN year_start IS NULL THEN NULL
        ELSE CAST(year_start AS VARCHAR) || '-' || lpad(CAST(((year_start + 1) % 100) AS VARCHAR), 2, '0')
    END AS year_label
FROM tagged;
