-- DuckDB: 統一成月資料並以月份合併（排除未完整的當月 2026-10）
CREATE OR REPLACE TABLE ffr AS
SELECT date_trunc('month', CAST(observation_date AS DATE))::DATE AS month, FEDFUNDS AS ffr
FROM read_csv_auto('data/raw/FEDFUNDS.csv');
CREATE OR REPLACE TABLE cpi AS
SELECT date_trunc('month', CAST(observation_date AS DATE))::DATE AS month, CPIAUCSL AS cpi
FROM read_csv_auto('data/raw/CPIAUCSL.csv');
-- 匯率為日資料（缺值為空字串/'.'），取每月平均
CREATE OR REPLACE TABLE fx AS
SELECT date_trunc('month', CAST(observation_date AS DATE))::DATE AS month, avg(TRY_CAST(DEXTAUS AS DOUBLE)) AS usdtwd
FROM read_csv_auto('data/raw/DEXTAUS.csv', all_varchar=true)
WHERE TRY_CAST(DEXTAUS AS DOUBLE) IS NOT NULL
GROUP BY 1;
CREATE OR REPLACE TABLE taiex AS
SELECT date_trunc('month', CAST("Date" AS DATE))::DATE AS month, "Close" AS taiex_close
FROM read_csv_auto('data/raw/TWII_monthly.csv');
CREATE OR REPLACE TABLE monthly AS
SELECT t.month, t.taiex_close, f.usdtwd, r.ffr, c.cpi
FROM taiex t JOIN fx f USING (month) JOIN ffr r USING (month) LEFT JOIN cpi c USING (month)
WHERE t.month < DATE '2026-10-01'
ORDER BY t.month;
COPY monthly TO 'data/processed/monthly_merged.csv' (HEADER);
