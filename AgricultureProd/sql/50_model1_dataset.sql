CREATE OR REPLACE TABLE t_model1_labels_district AS
SELECT
    p.year_label,
    p.year_start,
    p.year_end,
    COALESCE(a.to_key, p.district_key_raw) AS district_key,
    p.district,
    p.crop_name,
    p.season_final AS season_norm,
    SUM(p.production_value) AS total_production_value,
    SUM(p.area_acres) AS total_area_acres,
    SUM(p.production_value) / NULLIF(SUM(p.area_acres), 0) AS yield_per_acre_proxy,
    COUNT(*) AS mandal_rows_used,
    COUNT(DISTINCT p.mandal) AS mandals_used_distinct
FROM (
    SELECT
        year_label,
        year_start,
        year_end,
        district,
        crop_name,
        season_final,
        production_value,
        area_acres,
        mandal,
        regexp_replace(
            regexp_replace(
                regexp_replace(lower(district), 'urban', '', 'g'),
                'rural', '', 'g'
            ),
            '[^a-z0-9]+', '', 'g'
        ) AS district_key_raw
    FROM t_yield_outlier_flags
    WHERE dq_outlier_any = false
      AND season_final IN ('kharif', 'rabi')
      AND production_value > 0
      AND area_acres > 0
      AND production_value < 1000000
) AS p
LEFT JOIN t_district_alias AS a
  ON p.district_key_raw = a.from_key
GROUP BY
    p.year_label,
    p.year_start,
    p.year_end,
    district_key,
    p.district,
    p.crop_name,
    p.season_final;

CREATE OR REPLACE VIEW v_weather_season_canon AS
SELECT
    w.year_label,
    w.year_start,
    w.year_end,
    w.district,
    w.season_norm,
    w.rain_total_mm,
    w.rainy_days_total,
    w.hum_min_avg,
    w.hum_max_avg,
    w.avg_mandals_reporting,
    w.days_covered,
    w.months_covered,
    regexp_replace(
        regexp_replace(
            regexp_replace(lower(w.district), 'urban', '', 'g'),
            'rural', '', 'g'
        ),
        '[^a-z0-9]+', '', 'g'
    ) AS district_key_raw,
    COALESCE(a.to_key, regexp_replace(
        regexp_replace(
            regexp_replace(lower(w.district), 'urban', '', 'g'),
            'rural', '', 'g'
        ),
        '[^a-z0-9]+', '', 'g'
    )) AS district_key
FROM t_weather_district_season AS w
LEFT JOIN t_district_alias AS a
  ON regexp_replace(
        regexp_replace(
            regexp_replace(lower(w.district), 'urban', '', 'g'),
            'rural', '', 'g'
        ),
        '[^a-z0-9]+', '', 'g'
     ) = a.from_key;

CREATE OR REPLACE VIEW v_weather_season_canon_uniq AS
SELECT
  year_label,
  season_norm,
  district_key,
  MIN(district) AS district_rep,
  SUM(rain_total_mm * w) / NULLIF(SUM(w),0) AS rain_total_mm,
  SUM(rainy_days_total * w) / NULLIF(SUM(w),0) AS rainy_days_total,
  SUM(hum_min_avg * w) / NULLIF(SUM(w),0) AS hum_min_avg,
  SUM(hum_max_avg * w) / NULLIF(SUM(w),0) AS hum_max_avg,
  SUM(avg_mandals_reporting * w) / NULLIF(SUM(w),0) AS avg_mandals_reporting,
  MAX(days_covered) AS days_covered,
  MAX(months_covered) AS months_covered,
  COUNT(*) AS weather_rows_collapsed
FROM (
  SELECT
    *,
    CASE
      WHEN days_covered IS NULL OR days_covered = 0 THEN 1
      ELSE days_covered
    END AS w
  FROM v_weather_season_canon
) t
GROUP BY year_label, season_norm, district_key;

CREATE OR REPLACE TABLE t_model1_dataset AS
SELECT
  p.year_label, p.year_start, p.year_end,
  p.district, p.crop_name, p.season_norm,

  p.total_production_value,
  p.total_area_acres,
  p.yield_per_acre_proxy,
  p.mandal_rows_used,
  p.mandals_used_distinct,

  w.rain_total_mm,
  w.rainy_days_total,
  w.hum_min_avg,
  w.hum_max_avg,
  w.avg_mandals_reporting,
  w.days_covered,
  w.months_covered,

  CASE WHEN p.season_norm='kharif' THEN 4
       WHEN p.season_norm='rabi'   THEN 6
       ELSE NULL
  END AS expected_months,

  (w.year_label IS NULL) AS dq_weather_missing,
  CASE
    WHEN w.year_label IS NULL THEN TRUE
    WHEN p.season_norm='kharif' AND w.months_covered < 4 THEN TRUE
    WHEN p.season_norm='rabi'   AND w.months_covered < 6 THEN TRUE
    ELSE FALSE
  END AS dq_weather_incomplete

FROM t_model1_labels_district p
LEFT JOIN v_weather_season_canon_uniq w
  ON p.year_label   = w.year_label
 AND p.season_norm  = w.season_norm
 AND p.district_key = w.district_key;

COPY (SELECT * FROM t_model1_dataset)
TO 'outputs/model1_dataset.csv' (HEADER, DELIMITER ',');

CREATE OR REPLACE TABLE t_model1_join_coverage AS
WITH labels AS (
  SELECT year_label, season_norm, COUNT(*) AS rows_labels
  FROM t_model1_labels_district
  GROUP BY 1,2
),
joined AS (
  SELECT year_label, season_norm, COUNT(*) AS rows_joined
  FROM t_model1_dataset
  WHERE dq_weather_missing = FALSE
  GROUP BY 1,2
)
SELECT
  l.year_label,
  l.season_norm,
  l.rows_labels,
  COALESCE(j.rows_joined, 0) AS rows_joined,
  ROUND(100.0 * COALESCE(j.rows_joined, 0) / NULLIF(l.rows_labels, 0), 2) AS join_pct
FROM labels l
LEFT JOIN joined j
  ON l.year_label = j.year_label AND l.season_norm = j.season_norm
ORDER BY l.year_label, l.season_norm;

COPY (SELECT * FROM t_model1_join_coverage)
TO 'outputs/model1_join_coverage.csv' (HEADER, DELIMITER ',');

CREATE OR REPLACE TABLE t_model1_missing_districts AS
SELECT
  year_label,
  season_norm,
  district,
  SUM(mandal_rows_used) AS weight,
  COUNT(*) AS crop_rows_missing
FROM t_model1_dataset
WHERE dq_weather_missing = TRUE
GROUP BY 1,2,3
ORDER BY weight DESC, crop_rows_missing DESC
LIMIT 200;

COPY (SELECT * FROM t_model1_missing_districts)
TO 'outputs/model1_missing_districts.csv' (HEADER, DELIMITER ',');

COPY (
  SELECT year_label, season_norm, SUM(CASE WHEN weather_rows_collapsed>1 THEN 1 ELSE 0 END) AS keys_collapsed
  FROM v_weather_season_canon_uniq
  GROUP BY 1,2
  ORDER BY 1,2
) TO 'outputs/model1_weather_collisions.csv' (HEADER, DELIMITER ',');
