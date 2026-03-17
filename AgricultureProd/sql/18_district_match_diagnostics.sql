CREATE TABLE IF NOT EXISTS t_district_alias(
    from_key VARCHAR,
    to_key VARCHAR,
    from_name VARCHAR,
    to_name VARCHAR,
    note VARCHAR
);

INSERT INTO t_district_alias
SELECT 'asifabad','kumurambheem','asifabad','kumuram bheem','rename'
WHERE NOT EXISTS (SELECT 1 FROM t_district_alias WHERE from_key='asifabad');

INSERT INTO t_district_alias
SELECT 'gadwal','jogulambagadwal','gadwal','jogulamba gadwal','rename'
WHERE NOT EXISTS (SELECT 1 FROM t_district_alias WHERE from_key='gadwal');

INSERT INTO t_district_alias
SELECT 'jagital','jagtial','jagital','jagtial','rename'
WHERE NOT EXISTS (SELECT 1 FROM t_district_alias WHERE from_key='jagital');

INSERT INTO t_district_alias
SELECT 'jangoan','jangaon','jangoan','jangaon','rename'
WHERE NOT EXISTS (SELECT 1 FROM t_district_alias WHERE from_key='jangoan');

INSERT INTO t_district_alias
SELECT 'jayashanker','jayashankar','jayashanker','jayashankar','rename'
WHERE NOT EXISTS (SELECT 1 FROM t_district_alias WHERE from_key='jayashanker');

INSERT INTO t_district_alias
SELECT 'kothagudem','bhadradrikothagudem','kothagudem','bhadradri kothagudem','rename'
WHERE NOT EXISTS (SELECT 1 FROM t_district_alias WHERE from_key='kothagudem');

INSERT INTO t_district_alias
SELECT 'medchal','medchalmalkajgiri','medchal','medchal malkajgiri','rename'
WHERE NOT EXISTS (SELECT 1 FROM t_district_alias WHERE from_key='medchal');

INSERT INTO t_district_alias
SELECT 'sircilla','rajannasircilla','sircilla','rajanna sircilla','rename'
WHERE NOT EXISTS (SELECT 1 FROM t_district_alias WHERE from_key='sircilla');

INSERT INTO t_district_alias
SELECT 'yadadri','yadadribhuvanagiri','yadadri','yadadri bhuvanagiri','rename'
WHERE NOT EXISTS (SELECT 1 FROM t_district_alias WHERE from_key='yadadri');

INSERT INTO t_district_alias
SELECT 'yadadribhongir','yadadribhuvanagiri','yadadri bhongir','yadadri bhuvanagiri','rename'
WHERE NOT EXISTS (SELECT 1 FROM t_district_alias WHERE from_key='yadadribhongir');

INSERT INTO t_district_alias
SELECT 'wanaparathy','wanaparthy','wanaparathy','wanaparthy','rename'
WHERE NOT EXISTS (SELECT 1 FROM t_district_alias WHERE from_key='wanaparathy');

INSERT INTO t_district_alias
SELECT 'mahabubad','mahabubabad','mahabubad','mahabubabad','rename'
WHERE NOT EXISTS (SELECT 1 FROM t_district_alias WHERE from_key='mahabubad');

INSERT INTO t_district_alias
SELECT 'rajannasiricilla','rajannasircilla','rajannasiricilla','rajanna sircilla','rename'
WHERE NOT EXISTS (SELECT 1 FROM t_district_alias WHERE from_key='rajannasiricilla');

UPDATE t_district_alias
SET to_key='jayashankarbhupalpally', to_name='jayashankar-bhupalpally', note='map short district name to full weather district key'
WHERE from_key IN ('jayashanker','jayashankar');

INSERT INTO t_district_alias (from_key,to_key,from_name,to_name,note)
SELECT 'jayashanker','jayashankarbhupalpally','jayashanker','jayashankar-bhupalpally','map short district name to full weather district key'
WHERE NOT EXISTS (SELECT 1 FROM t_district_alias WHERE from_key='jayashanker');

INSERT INTO t_district_alias (from_key,to_key,from_name,to_name,note)
SELECT 'jayashankar','jayashankarbhupalpally','jayashankar','jayashankar-bhupalpally','map short district name to full weather district key'
WHERE NOT EXISTS (SELECT 1 FROM t_district_alias WHERE from_key='jayashankar');

UPDATE t_district_alias
SET to_key='warangal', to_name='warangal', note='proxy mapping for hanumakonda -> warangal for weather join'
WHERE from_key='hanumakonda';

INSERT INTO t_district_alias (from_key,to_key,from_name,to_name,note)
SELECT 'hanumakonda','warangal','hanumakonda','warangal','proxy mapping for hanumakonda -> warangal for weather join'
WHERE NOT EXISTS (SELECT 1 FROM t_district_alias WHERE from_key='hanumakonda');

DROP VIEW IF EXISTS v_prod_district_keys;

CREATE VIEW v_prod_district_keys AS
WITH prod_raw AS (
    SELECT
        year_label,
        season_final AS season_norm,
        district,
        regexp_replace(
            regexp_replace(
                regexp_replace(lower(district), 'urban', '', 'g'),
                'rural', '', 'g'
            ),
            '[^a-z0-9]+', '', 'g'
        ) AS district_key_raw,
        COUNT(*) AS row_count
    FROM t_yield_outlier_flags
    WHERE dq_outlier_any = false
      AND season_final IN ('kharif', 'rabi')
    GROUP BY year_label, season_final, district, district_key_raw
)
SELECT
    p.year_label,
    p.season_norm,
    p.district,
    p.district_key_raw,
    COALESCE(a.to_key, p.district_key_raw) AS district_key_canon,
    p.row_count
FROM prod_raw AS p
LEFT JOIN t_district_alias AS a
  ON p.district_key_raw = a.from_key;

DROP VIEW IF EXISTS v_weather_district_keys;

CREATE VIEW v_weather_district_keys AS
WITH weather_raw AS (
    SELECT
        year_label,
        season_norm,
        district,
        regexp_replace(
            regexp_replace(
                regexp_replace(lower(district), 'urban', '', 'g'),
                'rural', '', 'g'
            ),
            '[^a-z0-9]+', '', 'g'
        ) AS district_key_raw,
        COUNT(*) AS row_count
    FROM t_weather_district_season
    GROUP BY year_label, season_norm, district, district_key_raw
)
SELECT
    w.year_label,
    w.season_norm,
    w.district,
    w.district_key_raw,
    COALESCE(a.to_key, w.district_key_raw) AS district_key_canon,
    w.row_count
FROM weather_raw AS w
LEFT JOIN t_district_alias AS a
  ON w.district_key_raw = a.from_key;

CREATE OR REPLACE TABLE t_prod_missing_weather AS
SELECT
    p.year_label,
    p.season_norm,
    p.district AS prod_district,
    p.district_key_raw AS prod_district_key_raw,
    p.district_key_canon AS prod_district_key_canon,
    p.row_count AS prod_row_count,
    NULL::VARCHAR AS weather_district,
    NULL::VARCHAR AS weather_district_key_raw,
    NULL::VARCHAR AS weather_district_key_canon,
    NULL::BIGINT AS weather_row_count
FROM v_prod_district_keys AS p
WHERE NOT EXISTS (
    SELECT 1
    FROM v_weather_district_keys AS w
    WHERE w.year_label = p.year_label
      AND w.season_norm = p.season_norm
      AND w.district_key_canon = p.district_key_canon
);

COPY (
    SELECT *
    FROM t_prod_missing_weather
    ORDER BY year_label, season_norm, prod_district
) TO 'outputs/districts_in_prod_missing_in_weather.csv' (HEADER, DELIMITER ',');

CREATE OR REPLACE TABLE t_weather_missing_prod AS
SELECT
    w.year_label,
    w.season_norm,
    NULL::VARCHAR AS prod_district,
    NULL::VARCHAR AS prod_district_key_raw,
    NULL::VARCHAR AS prod_district_key_canon,
    NULL::BIGINT AS prod_row_count,
    w.district AS weather_district,
    w.district_key_raw AS weather_district_key_raw,
    w.district_key_canon AS weather_district_key_canon,
    w.row_count AS weather_row_count
FROM v_weather_district_keys AS w
WHERE NOT EXISTS (
    SELECT 1
    FROM v_prod_district_keys AS p
    WHERE p.year_label = w.year_label
      AND p.season_norm = w.season_norm
      AND p.district_key_canon = w.district_key_canon
);

COPY (
    SELECT *
    FROM t_weather_missing_prod
    ORDER BY year_label, season_norm, weather_district
) TO 'outputs/districts_in_weather_missing_in_prod.csv' (HEADER, DELIMITER ',');
