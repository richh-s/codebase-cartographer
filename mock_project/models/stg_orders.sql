
WITH raw_data AS (
    SELECT * FROM {{ source('internal_raw', 'orders') }}
)
SELECT * FROM raw_data
