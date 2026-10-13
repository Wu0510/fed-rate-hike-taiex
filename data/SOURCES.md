# 資料來源（下載日：2026-10-13）

## 分析實際使用（data/raw/）
| 檔案 | 來源 | 原始頻率／期間 | 授權 |
|---|---|---|---|
| FEDFUNDS.csv | FRED https://fred.stlouisfed.org/graph/fredgraph.csv?id=FEDFUNDS（聯邦基金有效利率） | 月，1954-07 ~ 2026-09 | 美國政府公開資料（Fed）；依 FRED 使用條款需註明出處 |
| DEXTAUS.csv | FRED https://fred.stlouisfed.org/graph/fredgraph.csv?id=DEXTAUS（新台幣/美元，Fed H.10） | 日，1983-10-03 ~ 2026-10-02 | 同上 |
| CPIAUCSL.csv | FRED https://fred.stlouisfed.org/graph/fredgraph.csv?id=CPIAUCSL（美國 CPI，BLS） | 月，1947-01 ~ 2026-08 | 美國政府公開資料（BLS） |
| TWII_monthly.csv | Yahoo Finance ^TWII，透過 yfinance 下載（月 K，未調整） | 月，1997-07 ~ 2026-10（2026-10 未完整，分析排除） | Yahoo 使用條款，僅供個人/研究用途，不可再散布 |

合併後分析期間：1997-08 ~ 2026-09（350 個月報酬）。

## Kaggle 參考資料（data/raw/kaggle/，下載成功但未用於主分析）
- federalreserve/taiwan--u.s.-foreign-exchange-rate：DEXTAUS 日資料 1983-10-03 ~ 2019-12-13，只到 2019，所以改用 FRED 的最新版本。
- chunghaoleeyginger/taiwan-capitalization-weighted-stock-index：TWII 日資料 2000-01-04 ~ 2021-08-27，只到 2021，所以改用 yfinance。
- jesusgaud/inflation-forecasting-dataset：2000-01 ~ 2024-12，但數值跟 FRED 官方對不上（例如 2000-01 聯邦基金利率寫 3.47，官方是 5.45；失業率寫 7.22，官方是 4.0），看起來是模擬資料，所以不採用。
授權以各 Kaggle 頁面標示為準（未逐一確認）。
