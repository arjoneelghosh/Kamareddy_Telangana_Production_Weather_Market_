DROP TABLE IF EXISTS t_yield_outlier_flags;

CREATE TABLE t_yield_outlier_flags AS
WITH base AS (
    SELECT
        year_label,
        crop_name,
        district,
        mandal,
        season_final,
        COALESCE(season_final, '_no_season') AS season_group,
        year_start,
        year_end,
        production_value,
        area_acres,
        prod_per_acre,
        prod_source_file,
        area_source_file,
        LN(1 + prod_per_acre) AS log_yield
    FROM t_yield_join_check
    WHERE prod_per_acre IS NOT NULL
      AND area_acres > 0
      AND production_value > 0
      AND production_value < 1000000
),
group_stats AS (
    SELECT
        year_label,
        crop_name,
        season_group,
        quantile_cont(log_yield, 0.5) AS median_log_yield,
        quantile_cont(area_acres, 0.01) AS area_p01,
        quantile_cont(prod_per_acre, 0.99) AS yield_p99
    FROM base
    GROUP BY year_label, crop_name, season_group
),
with_ad AS (
    SELECT
        b.*,
        gs.median_log_yield,
        gs.area_p01,
        gs.yield_p99,
        ABS(b.log_yield - gs.median_log_yield) AS ad
    FROM base AS b
    JOIN group_stats AS gs
      ON b.year_label = gs.year_label
     AND b.crop_name = gs.crop_name
     AND b.season_group = gs.season_group
),
mad_stats AS (
    SELECT
        year_label,
        crop_name,
        season_group,
        quantile_cont(ad, 0.5) AS mad_log_yield
    FROM with_ad
    GROUP BY year_label, crop_name, season_group
)
SELECT
    wa.year_label,
    wa.crop_name,
    wa.district,
    wa.mandal,
    wa.season_final,
    wa.year_start,
    wa.year_end,
    wa.production_value,
    wa.area_acres,
    wa.prod_per_acre,
    wa.log_yield,
    wa.prod_source_file,
    wa.area_source_file,
    wa.median_log_yield,
    ms.mad_log_yield,
    wa.area_p01,
    wa.yield_p99,
    0.6745 * (wa.log_yield - wa.median_log_yield) / NULLIF(ms.mad_log_yield, 0) AS robust_z,
    wa.area_acres <= wa.area_p01 AS dq_tiny_area,
    CASE
        WHEN COALESCE(ms.mad_log_yield, 0) = 0 THEN wa.prod_per_acre > wa.yield_p99
        ELSE ABS(0.6745 * (wa.log_yield - wa.median_log_yield) / NULLIF(ms.mad_log_yield, 0)) > 6
    END AS dq_outlier_yield,
    (
        wa.area_acres <= wa.area_p01
        OR CASE
            WHEN COALESCE(ms.mad_log_yield, 0) = 0 THEN wa.prod_per_acre > wa.yield_p99
            ELSE ABS(0.6745 * (wa.log_yield - wa.median_log_yield) / NULLIF(ms.mad_log_yield, 0)) > 6
        END
    ) AS dq_outlier_any
FROM with_ad AS wa
JOIN mad_stats AS ms
  ON wa.year_label = ms.year_label
 AND wa.crop_name = ms.crop_name
 AND wa.season_group = ms.season_group;

COPY (
    SELECT
        year_label,
        COUNT(*) AS rows_total,
        SUM(CASE WHEN dq_outlier_any THEN 1 ELSE 0 END) AS outlier_rows,
        100.0 * SUM(CASE WHEN dq_outlier_any THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0) AS outlier_pct,
        MAX(prod_per_acre) AS max_yield,
        MAX(CASE WHEN NOT dq_outlier_any THEN prod_per_acre ELSE NULL END) AS max_yield_non_outlier
    FROM t_yield_outlier_flags
    GROUP BY year_label
    ORDER BY year_label
) TO 'outputs/yield_outliers_by_year.csv' (HEADER, DELIMITER ',');

COPY (
    SELECT
        year_label,
        crop_name,
        district,
        mandal,
        season_final,
        area_acres,
        production_value,
        prod_per_acre,
        prod_source_file,
        area_source_file,
        dq_tiny_area,
        dq_outlier_yield,
        dq_outlier_any,
        robust_z
    FROM t_yield_outlier_flags
    ORDER BY prod_per_acre DESC, year_label, crop_name, district, mandal
    LIMIT 50
) TO 'outputs/yield_outliers_top50.csv' (HEADER, DELIMITER ',');
