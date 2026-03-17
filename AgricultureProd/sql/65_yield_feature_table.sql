DROP TABLE IF EXISTS t_yield_seasonal;

CREATE TABLE t_yield_seasonal AS
WITH base AS (
    SELECT
        year_label,
        LOWER(TRIM(CAST(district AS VARCHAR))) AS district,
        LOWER(TRIM(CAST(crop_name AS VARCHAR))) AS crop_name,
        LOWER(TRIM(CAST(season_norm AS VARCHAR))) AS season_norm,
        TRY_CAST(yield_per_acre_proxy AS DOUBLE) AS yield_per_acre_proxy,
        CAST(dq_weather_incomplete AS VARCHAR) AS dq_weather_incomplete_raw
    FROM read_csv_auto(
        'C:/Users/footb/Desktop/AgriFore/AgricultureProd/outputs/model1_dataset.csv',
        header = true
    )
),
normalized AS (
    SELECT
        year_label,
        district,
        crop_name,
        season_norm,
        yield_per_acre_proxy,
        dq_weather_incomplete_raw,
        regexp_replace(
            replace(
                replace(
                    regexp_replace(
                        trim(split_part(regexp_replace(lower(trim(crop_name)), '\s*\(.*$', ''), '/', 1)),
                        '\s+',
                        ' ',
                        'g'
                    ),
                    'greenchilli',
                    'green chilli'
                ),
                'red chillies',
                'red chilli'
            ),
            '\s+',
            ' ',
            'g'
        ) AS crop_key
    FROM base
)
SELECT
    year_label,
    district,
    crop_name,
    crop_key,
    season_norm,
    AVG(yield_per_acre_proxy) AS yield_per_acre_proxy,
    BOOL_OR(
        CASE
            WHEN LOWER(TRIM(dq_weather_incomplete_raw)) IN ('true', '1', 't', 'yes', 'y') THEN TRUE
            ELSE FALSE
        END
    ) AS dq_weather_incomplete
FROM normalized
WHERE year_label IS NOT NULL
  AND district IS NOT NULL
  AND crop_name IS NOT NULL
  AND season_norm IS NOT NULL
  AND crop_key IS NOT NULL
  AND crop_key <> ''
  AND yield_per_acre_proxy IS NOT NULL
GROUP BY 1, 2, 3, 4, 5;
