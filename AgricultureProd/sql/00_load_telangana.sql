DROP TABLE IF EXISTS tg_raw;

CREATE TABLE tg_raw AS
SELECT
    * EXCLUDE (filename),
    filename AS source_file
FROM read_csv_auto(
    'horticulture-Mandal_wise_Crop_Area_Production_and_Yield_data _*.csv',
    filename = true,
    union_by_name = true
);

SELECT 'total_row_count' AS metric, COUNT(*) AS row_count
FROM tg_raw;

SELECT source_file, COUNT(*) AS row_count
FROM tg_raw
GROUP BY source_file
ORDER BY source_file;

SELECT DISTINCT CAST(year AS VARCHAR) AS year_label
FROM tg_raw
ORDER BY year_label;

DESCRIBE tg_raw;
