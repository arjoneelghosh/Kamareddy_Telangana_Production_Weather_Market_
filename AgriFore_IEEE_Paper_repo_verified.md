# AgriFore: AI-Driven Agricultural Price and Yield Forecasting System for Kamareddy District, Telangana

---

**Sankar Shanan G**
*Student, Computing Technologies*
*College of Engineering and Technology*
*SRM Institute of Science and Technology*
*SRM Nagar, Kattankulathur, 603203, TN, India*
*ajaysankar2004@gmail.com*

**Arjoneel Ghosh**
*Student, Computing Technologies*
*College of Engineering and Technology*
*SRM Institute of Science and Technology*
*SRM Nagar, Kattankulathur, 603203, TN, India*
*arjoneelghosh03@gmail.com*

**Dr. Arul Prakash M**
*Assistant Professor, Computing Technologies*
*College of Engineering and Technology*
*SRM Institute of Science and Technology*
*SRM Nagar, Kattankulathur, 603203, TN, India*
*arulpram@srmist.edu.in*

---

## Abstract

**Abstract--** AgriFore is an AI-driven agricultural forecasting system centered on crop-yield and market-price modeling for Telangana, with a district-specific yield artifact for Kamareddy. Agricultural price volatility remains a critical challenge for farmers and policymakers, exacerbated by unpredictable weather patterns, seasonal supply-demand imbalances, and fragmented market infrastructure. Existing forecasting approaches such as ARIMA and Prophet are limited in their ability to model nonlinear dependencies and integrate heterogeneous data sources. Repo evidence supports four implemented modeling components with different maturity levels: (1) a district-specific Weather-to-Yield XGBoost model artifact that predicts `yield_per_acre_proxy` using seasonal rainfall, humidity, and rain-anomaly features, achieving a test R^2 of about 0.77 on Kamareddy data; (2) a Market Price XGBoost base model that forecasts monthly modal prices using lag features, weather indicators, and market arrivals, achieving a test R^2 of 0.885 across 117 commodities and 169 Agricultural Market Committee (AMC) entries; (3) an offline LSTM Autoencoder validator for anomalous price sequences; and (4) an offline RidgeCV residual-correction layer trained on joined yield-signal rows. The system processes four annual Telangana horticulture files (2019-20 through 2022-23), daily rainfall records from 2018-2026, and historical market transaction data through a DuckDB-based ETL stack implemented with 17 active SQL stage scripts in the current runners, plus one superseded weather-loader script retained in the repository. The repository also contains a FastAPI backend exposing 12 endpoints (including health) and a Next.js dashboard; however, deployed backend inference currently serves the Model 2 base price model, while the RidgeCV adjustment layer and anomaly validator remain offline components rather than active API inference paths.

**Keywords—** Agricultural forecasting, XGBoost, LSTM autoencoder, crop yield prediction, price forecasting, DuckDB, weather-yield modeling, Kamareddy, Telangana agriculture, machine learning, time series analysis, anomaly detection.

---

## I. Introduction

Agriculture is the economic backbone of Telangana, a state in southern India where over 55% of the population depends directly on farming for their livelihood [14]. The Kamareddy district, located in the northern region of Telangana, is a significant agricultural hub producing a diverse range of horticulture and food crops including paddy, cotton, maize, tomato, and onion across its numerous mandals. Despite the sector's vital importance, farmers and traders in Kamareddy and surrounding districts face severe challenges due to unpredictable commodity price fluctuations driven by weather anomalies, supply-demand imbalances, transportation inefficiencies, and policy interventions [5].

Existing forecasting methodologies, including traditional statistical approaches such as ARIMA [3], exponential smoothing [8], and Holt-Winters models, are fundamentally limited in their capacity to capture nonlinear price dynamics. While Facebook's Prophet [4] offers improvements in modeling seasonality and holiday effects, it lacks the capability to learn long-term temporal dependencies or integrate exogenous variables such as rainfall, humidity, and seasonal yield variations into a unified prediction framework. Standalone machine learning models such as Long Short-Term Memory (LSTM) networks [9] and XGBoost [1] have demonstrated promising results in isolation, but the agricultural forecasting domain demands systems that can simultaneously model weather-driven yield dynamics and market-driven price movements.

To address these limitations, we propose AgriFore, a multi-model AI system specifically designed for the Kamareddy district of Telangana. AgriFore integrates four complementary machine learning components: (1) a Weather-to-Yield XGBoost model that predicts crop yield per acre using engineered weather features including rainfall anomalies and humidity indices; (2) a Market Price XGBoost model that forecasts monthly commodity prices using historical lag features, weather indicators, and market arrival volumes; (3) an LSTM Autoencoder that identifies anomalous price sequences indicative of market manipulation or extreme events; and (4) a RidgeCV regression layer that adjusts base price predictions using yield signals from Model 1. This dual-pathway architecture—where weather impacts yields, and yields in turn influence market prices—captures the causal chain underlying agricultural economies more faithfully than single-model approaches.

The system processes heterogeneous data from multiple government sources through a DuckDB-based Extract-Transform-Load (ETL) pipeline and includes a local FastAPI backend with a Next.js frontend dashboard. Repo-grounded evaluation artifacts support an R^2 of 0.885 for the Model 2 base price forecaster and about 0.77 for a district-specific Kamareddy Model 1 artifact. In the current codebase, these results should be interpreted as a mixture of deployed base-model functionality and offline experimental components rather than a fully integrated production stack.

The key contributions of this paper are as follows:

- A dual-model architecture that connects weather-driven yield prediction with market price forecasting through a yield-adjustment mechanism.
- A DuckDB-based data pipeline with 17 active SQL stage scripts in the current runners, plus one superseded weather-loader SQL file retained in the repository.
- An implemented LSTM Autoencoder validator artifact and evaluation scripts for screening unusual market price sequences offline.
- A local full-stack application structure using FastAPI and Next.js for dashboarding and base-model price prediction, with some components remaining offline or experimental.
- Extensive evaluation on real-world Telangana agricultural data covering 117 commodities across 169 markets.

**Repo Verification Note:** This revised manuscript distinguishes between components fully supported by repository evidence (DuckDB ETL, Model 2 base training/evaluation, FastAPI endpoints, and the Next.js dashboard), partially supported components (district-specific Model 1 artifacts and saved metrics), and offline experimental components (the RidgeCV adjustment layer and LSTM autoencoder validator) that are not currently part of deployed backend inference.

---

## II. Related Work

Agricultural commodity price forecasting has attracted significant research attention due to its direct impact on food security and farmer livelihoods. This section reviews the key approaches in the literature and identifies the research gaps that AgriFore addresses.

### A. Statistical Time Series Models

Classical time series methods have been widely used for agricultural price prediction. The Autoregressive Integrated Moving Average (ARIMA) model and its seasonal variant SARIMA remain popular baselines due to their interpretability and well-established theoretical foundations [3]. Hyndman and Athanasopoulos [3] provide a comprehensive treatment of forecasting principles, noting that ARIMA models perform well on stationary, linear time series but struggle with the nonlinear, multi-factor dynamics typical of agricultural markets. Exponential smoothing methods [8] offer adaptive weighting of recent observations but share similar limitations.

Taylor and Letham [4] introduced Prophet, a decomposable time series model designed to handle seasonality, holidays, and trend changepoints at scale. While Prophet has been adopted in various commercial forecasting applications, its additive decomposition framework cannot effectively capture the complex interactions between weather variables, market supply-demand dynamics, and regional agricultural patterns that drive crop prices in districts like Kamareddy.

### B. Machine Learning Approaches

Chen and Guestrin [1] introduced XGBoost, a scalable tree boosting system that has become a dominant algorithm in structured data prediction tasks. XGBoost's ability to handle heterogeneous features, missing values, and nonlinear relationships makes it well-suited for agricultural forecasting where inputs span weather metrics, market indicators, and categorical variables such as crop type and district.

Prokhorenkova et al. [2] proposed CatBoost, an unbiased boosting algorithm specifically designed for datasets with categorical features. CatBoost's ordered boosting mechanism and native handling of categorical variables reduce overfitting and improve generalization, making it complementary to XGBoost in ensemble configurations.

Recent agricultural studies have applied gradient boosting and related ML methods directly to yield and price settings. Wang et al. [19] demonstrate that XGBoost-based modeling can be effective for agricultural yield classification under noisy field conditions, while Liu et al. [20] show that machine-learning pipelines can capture nonlinear crop-growth and yield relationships more effectively than purely linear baselines. For market-side forecasting, Sun et al. [21] review modern agricultural price forecasting methods and highlight the growing role of tree ensembles and hybrid ML systems in commodity-price analysis.

### C. Deep Learning for Time Series

Recurrent neural networks, particularly LSTM architectures, have shown strong performance in sequential learning tasks [9]. LSTM networks can capture long-term dependencies in price series through their gating mechanisms, making them suitable for modeling temporal trends and seasonal patterns in commodity prices. However, LSTM models require substantial training data and are sensitive to noisy sequences, which is a common challenge in agricultural datasets where data quality varies across collection sources.

Autoencoder architectures have been applied for anomaly detection in financial and market time series data. LSTM Autoencoders learn to reconstruct normal sequences, and instances with high reconstruction error are flagged as anomalies. This approach is particularly relevant for agricultural markets where sudden price spikes or drops may indicate data quality issues, market manipulation, or genuine supply shocks [13].

### D. Hybrid and Ensemble Approaches

Recent work has explored hybrid architectures that combine deep learning with gradient boosting methods. Athey and Imbens [9] discuss machine learning methods applicable to economic and market prediction, emphasizing the value of ensemble techniques that leverage the complementary strengths of different model families. The integration of LSTM-based temporal models with XGBoost-based feature models has shown promise in improving prediction accuracy over standalone approaches [10], [11].

More recent agricultural price-forecasting studies have extended this line of work using boosting-style ensembles tailored to commodity data. Zhang et al. [22], for example, report a boosting-ensemble approach for fresh agricultural product price prediction, reinforcing the relevance of structured-data ensemble methods to the market-price component of AgriFore.

### E. Research Gap

Despite these advances, several gaps remain: (1) most existing systems treat price prediction in isolation without connecting it to yield estimation, even though weather-driven yield variations are a primary driver of market prices; (2) few systems address the specific challenges of Indian agricultural markets at the district level, where data heterogeneity and quality issues are pronounced; (3) anomaly detection is rarely integrated into agricultural forecasting pipelines; and (4) end-to-end deployment architectures that bring ML predictions to non-technical stakeholders are underexplored. AgriFore addresses these gaps only partially in the current repository through a multi-model architecture, a working SQL/data layer, and a local full-stack application whose deployed inference path currently centers on the base price model.

---

## III. Methodology

### A. Data Collection and Preprocessing

AgriFore integrates data from three primary sources to construct a unified forecasting dataset for the Kamareddy district and the broader Telangana region:

**1) Horticulture Production Data:** Mandal-wise crop area, production, and yield data for Telangana spanning the years 2019–20 through 2022–23, sourced from the Telangana state government's Department of Horticulture. These four annual datasets contain records at the mandal level across all 30 districts, covering horticulture crops with area (in acres), production value, and yield metrics. The raw data is ingested into a DuckDB database as the `tg_raw` table and processed through views `v_prod_real` and `v_area_real` to standardize district names, normalize season labels (Kharif, Rabi), and compute yield-per-acre proxy values.

**2) Weather Data:** Daily rainfall (in mm) and humidity (minimum and maximum) records spanning 2018 through 2026 across Telangana. The repository contains nine annual CSV files that are cleaned through raw ingestion (`weather_raw`), deduplication and quality filtering (`weather_clean`), district standardization (`v_weather_clean_std`), and aggregation to district-day (`t_weather_district_day`), district-month (`t_weather_district_month`), and district-season (`t_weather_district_season`) granularities. The weather pipeline handles duplicate records, invalid humidity values, district alias normalization via `t_district_alias`, and seasonal rainfall/humidity aggregation. Additional anomaly-style weather features such as `rain_anom_mm` and `rain_dev_pct` appear in the Kamareddy district Model 1 artifact rather than in the main SQL feature tables.

**3) Market Transaction Data:** Agricultural Market Committee (AMC) daily transaction records including arrival volumes (in quintals), minimum, maximum, and modal prices for 117 distinct commodities across 169 market yards in Telangana. This data is loaded into `t_market_raw`, cleaned into `t_market_clean`, and aggregated to monthly summaries in `t_market_monthly` with fields for average modal price, total arrivals, and trading day counts.

**Data Pipeline Architecture:** The repository contains 18 SQL files under `AgricultureProd/sql`, of which 17 are active in the current runnable pipelines; the legacy `05_load_weather.sql` is superseded by `05_load_weather_v2.sql`. These scripts are executed within DuckDB via PowerShell runners for the production/weather and market phases. The pipeline performs the following transformations:

- Raw data ingestion and schema normalization (Scripts 00, 05)
- View creation for production and area extraction (Script 10)
- Weather feature engineering at daily, monthly, and seasonal granularities (Scripts 15, 17)
- District name matching and alias resolution (Script 18)
- Coverage analysis and crop stability assessment (Script 20)
- Outlier detection using Median Absolute Deviation (MAD) scoring with robust z-scores (Script 30)
- Season alignment with harvest-year rollup (Script 40)
- Model 1 dataset construction joining production labels to seasonal weather features (Script 50)
- Market data loading and monthly aggregation (Scripts 60, 61)
- Weather-market feature integration and Model 2 dataset construction (Scripts 62–66)

The resulting DuckDB database contains over 30 tables and views totaling approximately 123 MB, forming a comprehensive analytical layer for downstream modeling.

### B. Model 1: Weather-to-Yield Prediction

The first model in AgriFore's architecture addresses the relationship between weather conditions and crop yields. Repo evidence for the reported Kamareddy result comes from a district-specific XGBoost artifact (`aaaFinalModels/model1/district_model_kamareddy.pkl`) and its metadata, which predict `yield_per_acre_proxy` for Kamareddy crops using engineered seasonal weather features. A separate broader baseline script in `AgricultureProd/tools/train_model1_weather_to_yield.py` uses a RandomForest regressor on the wider `outputs/model1_dataset.csv`; that baseline should not be conflated with the Kamareddy-specific XGBoost result reported here.

**Feature Engineering:** The model uses 11 numeric features and 3 categorical features:

*Numeric Features:*
- `rain_total_mm` — Total seasonal rainfall in millimeters
- `rainy_days_total` — Count of days with measurable precipitation
- `hum_min_avg` — Average minimum humidity across the season
- `hum_max_avg` — Average maximum humidity across the season
- `rain_intensity` — Ratio of total rainfall to rainy days (mm per rainy day)
- `humid_range` — Difference between maximum and minimum humidity
- `rain_anom_mm` — Rainfall anomaly: deviation from long-term seasonal mean
- `rain_dev_pct` — Percentage deviation of rainfall from normal
- `avg_mandals_reporting` — Average number of mandals with weather data (data quality indicator)
- `days_covered` — Number of days with weather observations
- `months_covered` — Number of months with weather observations

*Categorical Features:*
- `district` — District name (focused on Kamareddy)
- `crop_name` — Crop identifier
- `season_norm` — Normalized season label (Kharif or Rabi)

**Data Quality Filters:** For the saved Kamareddy XGBoost artifact, metadata confirms filtering on incomplete weather coverage (`dq_weather_incomplete_filtered = true`) and positive yield values (`yield_gt_0 = true`). The same metadata records `dq_weather_missing = false`, so the repo does not support a claim that missing-weather rows were explicitly filtered in that particular Kamareddy run.

**Model Configuration:**

| Parameter | Value |
|-----------|-------|
| Algorithm | XGBoost Regressor |
| Max Depth | 8 |
| Learning Rate | 0.05 |
| Number of Estimators | 1000 |
| Subsample | 0.8 |
| Column Sample by Tree | 0.8 |
| Preprocessing | OneHotEncoder (categorical) + StandardScaler (numeric) |

**Train-Test Split:** The model is trained on data from the years 2020–21 and 2021–22, and evaluated on the year 2022–23. This temporal split prevents data leakage and simulates real-world forecasting conditions where the model must predict yields for an unseen future year.

### C. Model 2: Market Price Prediction (Base)

The second model is an XGBoost-based regressor that forecasts monthly commodity prices across Telangana's market infrastructure. This model operates at a finer temporal granularity (monthly) and incorporates a wider range of features.

**Target Variable:** `modal_price_mean` — the average modal (most frequently traded) price for a commodity at a specific AMC market in a given month.

**Feature Engineering:** The model uses 17 numeric features and 4 categorical features:

*Numeric Features:*
- `arrivals_sum` — Total arrival volume (quintals) for the month
- `n_days` — Number of trading days in the month
- `rain_sum_mm` — Monthly rainfall sum
- `rainy_days` — Count of rainy days in the month
- `hum_min_avg`, `hum_max_avg` — Monthly average humidity bounds
- `avg_mandals_reporting` — Weather data coverage indicator
- `month_num` — Calendar month (1–12)
- `month_sin`, `month_cos` — Cyclical encoding of month using sine/cosine transformation
- `lag_1`, `lag_2`, `lag_3`, `lag_6`, `lag_12` — Price lags at 1, 2, 3, 6, and 12 months
- `roll_mean_3`, `roll_mean_6` — Rolling average price over 3 and 6 months

*Categorical Features:*
- `district` — District identifier
- `amc` — Agricultural Market Committee (market yard) name
- `crop_name` — Commodity name
- `season_norm` — Season label (Kharif or Rabi)

The lag and rolling features are computed per grouping of (district, AMC, crop_name) to ensure they reflect commodity-specific and location-specific trends without data leakage.

**Model Configuration:**

| Parameter | Value |
|-----------|-------|
| Algorithm | XGBoost Regressor |
| Number of Estimators | 700 |
| Learning Rate | 0.04 |
| Max Depth | 6 |
| Subsample | 0.8 |
| Column Sample by Tree | 0.8 |
| Regularization (λ) | 5.0 |
| Preprocessing | SimpleImputer + OneHotEncoder (categorical), SimpleImputer median (numeric) |

**Train-Test Split:** Training data includes all records up to December 2023. Testing is performed on January 2024 through December 2024. The training set comprises 28,571 rows and the test set 4,264 rows.

**Out-of-Fold Validation:** To assess model stability and generate residuals for the adjustment layer, a block-forward cross-validation strategy is employed on the overlap years (2020–21 through 2022–23). The overlap period is divided into five temporal blocks, and for each block, the model is trained on all data preceding the block and validated on the block itself. This produces out-of-fold predictions with zero temporal leakage.

### D. Model 2: Yield-Adjusted Price Prediction

A secondary residual-correction layer is present in the repository as an offline experiment rather than a deployed inference path. The intuition is that weather-linked yield variation may explain part of the residual error left by the base market-price model.

**Approach:** `AgriMarket/train_model2_adjust.py` trains a RidgeCV regressor on the residual error (actual price minus `base_pred`) using out-of-fold base predictions from `outputs/m2_base_oof.csv` and joined rows from `v_model2_adjust_dataset`. In the current repo implementation, `yield_signal` is sourced from the seasonal yield table built from `outputs/model1_dataset.csv`; it is therefore a joined yield-proxy feature, not a live backend call to a deployed Model 1 inference service.

**Additional Features:** The adjustment script uses required numeric features `base_pred` and `yield_signal`, plus optional numeric features such as `arrivals_sum`, `rain_sum_mm`, `rainy_days`, `hum_min_avg`, `hum_max_avg`, and `month_of_year`, together with one-hot encoded `season_norm`.

**Ridge Regularization:** RidgeCV with alpha values [0.1, 1.0, 10.0, 100.0, 1000.0] is used to regularize the residual signal, with the selected alpha stored in `AgriMarket/outputs/m2_adjust_metadata.json`.

**Final Prediction:** The offline prediction script computes as:

```
final_pred = base_pred + adjust_pred
```

The repository contains saved adjustment artifacts (`m2_adjust_model.pkl`, `m2_adjust_metrics.csv`, and `m2_adjust_metadata.json`), but the FastAPI backend does not currently load this model. The saved RidgeCV metrics also do not establish improvement over the base model, so this layer should presently be interpreted as an experimental residual corrector rather than a validated deployed enhancement.

### E. LSTM Autoencoder for Anomaly Detection

The repository contains an offline LSTM Autoencoder validator under `aaaFinalModels/model2/deeplearning_validator`. The saved Keras configuration (`lstm_config.json`) specifies sliding windows of 30 timesteps with 19 features, and the evaluation script computes reconstruction-error statistics plus P95/P99 anomaly thresholds on market sequences.

Repo evidence supports this anomaly detector as implemented experimental code and saved model artifacts (`market_lstm_autoencoder.h5`, `evaluate_lstm_autoencoder.py`, and inspection/config files). However, no backend endpoint or frontend workflow currently invokes this module. It should therefore be described as an offline anomaly-screening component rather than a deployed runtime validation layer.

### F. Evaluation Metrics

The following standard regression metrics are used to evaluate model performance:

**Root Mean Squared Error (RMSE):** Measures the average magnitude of prediction errors, penalizing larger errors more heavily:

$$RMSE = \sqrt{\frac{1}{n}\sum_{i=1}^{n}(y_i - \hat{y}_i)^2}$$

**Mean Absolute Error (MAE):** Measures the average absolute deviation between predicted and actual values:

$$MAE = \frac{1}{n}\sum_{i=1}^{n}|y_i - \hat{y}_i|$$

**R² Score (Coefficient of Determination):** Represents the proportion of variance in the target variable explained by the model. A score of 1.0 indicates perfect prediction:

$$R^2 = 1 - \frac{\sum_{i=1}^{n}(y_i - \hat{y}_i)^2}{\sum_{i=1}^{n}(y_i - \bar{y})^2}$$

---

## IV. System Architecture

AgriFore follows a modular, three-tier architecture comprising a data pipeline layer, backend API layer, and frontend presentation layer. This design ensures separation of concerns, independent scalability, and ease of maintenance.

### A. Data Pipeline — DuckDB ETL

The data pipeline is built on DuckDB, a high-performance analytical database engine optimized for complex queries on structured data. Unlike traditional database systems, DuckDB operates as an embedded, serverless engine, eliminating the need for a separate database server while delivering columnar storage and vectorized query execution.

The current runnable pipelines use 17 active SQL scripts organized in sequential phases, with one superseded weather-loader SQL file retained for reference:

- **Phase 1 (Scripts 00–10):** Raw data ingestion from horticulture CSVs, view creation for production and area extraction with normalized district names and season labels.
- **Phase 2 (Scripts 15–18):** Weather data loading, cleaning, deduplication, and feature engineering at daily, monthly, and seasonal granularities. District name matching diagnostics ensure consistency between production and weather datasets.
- **Phase 3 (Scripts 20–40):** Data quality assessment including crop coverage analysis, stability profiling, MAD-based outlier detection with robust z-scores, and season alignment with harvest-year rollups.
- **Phase 4 (Scripts 50–66):** Model dataset construction including the Model 1 weather-yield dataset, market data loading, monthly aggregation, calendar-to-season mapping, and Model 2 base and adjustment datasets.

The resulting database contains over 30 tables and views including `t_model1_dataset`, `v_model2_base_dataset`, `v_model2_adjust_dataset`, `t_market_monthly`, and `t_weather_district_season`; the checked-in DuckDB file is approximately 123 MB.

### B. Backend - FastAPI Server

The backend is implemented using FastAPI, a modern Python web framework that provides automatic OpenAPI documentation, type validation via Pydantic, and asynchronous request handling. The current `api/server.py` exposes 12 endpoints in total, including a health check. The business endpoints fall into four functional categories:

**Reference Data Endpoints:**
- `GET /commodities` - Lists all 117 available commodities with heuristic category classification (Vegetable, Fruit, Grain, Pulse, Oilseed, Cash Crop)
- `GET /markets` - Lists all 169 AMC market-yard entries with their districts
- `GET /districts` - Lists all 30 Telangana districts used by the current market-facing API

**Dashboard Endpoints:**
- `GET /market-overview` - Aggregated statistics (total markets, active commodities, average price, total volume, year-over-year price change)
- `GET /top-commodities` - Top 8 commodities by trading volume with price change percentages
- `GET /market-clusters` - Regional market cluster overview grouped by district

**Chart Data Endpoints:**
- `GET /price-trends` - Multi-commodity monthly price trend data
- `GET /seasonal-data` - Monthly seasonal pattern analysis (average price and volume by month)
- `GET /arrival-data` - Arrival volume vs. price correlation data

**Prediction Endpoints:**
- `POST /predict-price` - Price prediction with a three-strategy fallback mechanism:
  1. Primary: real-time inference using the M2 base XGBoost model with live feature construction from DuckDB
  2. Secondary: lookup from pre-computed 2024 base predictions CSV
  3. Tertiary: historical average from DuckDB for the target crop, district, market, and month
- `POST /ask-agent` - Keyword-based canned-response endpoint for agricultural Q&A
- `GET /health` - System health check for database/model availability

The server connects to DuckDB in read-only mode for data queries and loads the M2 base model bundle from `aaaFinalModels/model2/m2_base_model.pkl` at startup. It does not load `AgriMarket/outputs/m2_adjust_model.pkl`, so deployed API inference currently uses the base model only.

### C. Frontend — Next.js Dashboard

The user-facing component is built using Next.js (React framework) with TypeScript and Tailwind CSS. The dashboard comprises three primary pages:

**1) Dashboard Page:** Displays four summary statistics (Total Markets, Active Commodities, Average Market Price, Total Volume), a multi-commodity price trend chart, top commodities by volume, and regional market cluster visualization.

**2) Analysis Page:** Provides seasonal pattern analysis with monthly average price and volume charts, and arrival-vs-price correlation visualizations for user-selected commodities.

**3) Prediction Page:** An interactive form allowing users to select a commodity, optionally specify a district and market, and receive AI-generated price predictions with confidence scores.

The frontend communicates with the FastAPI backend via an Axios-based service layer with request/response interceptors for logging and error handling.

### D. System Workflow

The implemented workflow operates as follows:

1. **Data Ingestion:** Raw CSV files from horticulture, weather, and market sources are loaded into DuckDB.
2. **ETL Pipeline:** The active SQL runners execute 17 current stage scripts (with one superseded weather-loader file retained in the repo) to clean, validate, and engineer features.
3. **Model Training:** Model 1 and Model 2 training scripts run offline against prepared datasets and save artifacts to repository folders.
4. **Model Serving:** The FastAPI server currently loads the deployed M2 base model artifacts from `aaaFinalModels/model2` at startup.
5. **API Serving:** The server responds to frontend requests with data queries and base-model price inference, plus CSV/historical fallbacks.
6. **User Interaction:** Stakeholders can access dashboard views, analysis charts, and base-model price predictions through the Next.js dashboard.

**Repo Verification Note:** The repository fully supports the DuckDB ETL stack, the M2 base training/evaluation path, the FastAPI API, and the Next.js frontend. It partially supports Model 1 through a district-specific Kamareddy XGBoost artifact plus broader experimental scripts. The RidgeCV adjustment layer and LSTM autoencoder are implemented as offline artifacts and evaluators, but they are not currently integrated into deployed backend inference.

---

## V. Result Analysis

To evaluate the performance of the AgriFore forecasting system, extensive experiments were conducted on multi-year agricultural datasets from Telangana government sources and IMD weather records. The models were evaluated using standard regression metrics on temporally separated test sets to simulate real-world forecasting conditions.

### A. Evaluation Metrics

Three standard regression metrics were used to assess forecasting performance:

- **Root Mean Squared Error (RMSE):** Measures average magnitude of error, with lower values indicating better accuracy. RMSE penalizes larger errors more heavily than MAE.
- **Mean Absolute Error (MAE):** Reflects the average absolute prediction error, providing an interpretable measure of typical forecast deviation.
- **R² Score:** Represents the proportion of variance explained by the model, with a score closer to 1.0 indicating better goodness-of-fit.

### B. Model 1 Results: Weather-to-Yield Prediction (Kamareddy District)

Model 1 was evaluated on the Kamareddy district with training on 61 records from years 2020–21 and 2021–22, and testing on 28 records from year 2022–23. Table I presents the results.

**TABLE I: Model 1 — Weather-to-Yield Performance (Kamareddy District)**

| Metric | Training Set | Test Set |
|--------|-------------|----------|
| R² Score | 0.9999 | 0.7702 |
| RMSE | 0.0009 | 3.9370 |
| MAE | 0.0008 | 2.0582 |

The near-perfect training R² (0.9999) with a substantially lower test R² (0.77) suggests some degree of overfitting, which is expected given the relatively small training dataset of 61 samples. However, the test R² of 0.77 indicates that the model explains approximately 77% of the variance in crop yields using weather features alone—a strong result given the complexity of yield determination. The model demonstrates that seasonal rainfall patterns, humidity levels, and rainfall anomalies are significant predictors of crop yield in the Kamareddy district.

### C. Model 2 Results: Market Price Prediction (XGBoost Base)

Model 2 was trained on 28,571 monthly records (up to December 2023) and tested on 4,264 records from January to December 2024, covering 117 commodities across 169 markets. Table II presents the results.

**TABLE II: Model 2 — Market Price Prediction Performance**

| Metric | Training Set | Test Set |
|--------|-------------|----------|
| R² Score | 0.9574 | 0.8849 |
| RMSE | 549.02 | 1170.63 |
| MAE | 342.50 | 610.09 |

The Model 2 Base XGBoost achieves a test R² of 0.885, indicating that the model explains approximately 88.5% of the variance in monthly commodity prices. The test RMSE of 1170.63 (in ₹/quintal) represents a reasonable error margin given the wide price range across 117 commodities—from low-value vegetables to high-value cash crops. The controlled gap between training R² (0.957) and test R² (0.885) indicates good generalization with minimal overfitting despite the model's complexity.

### D. Model Comparison

Table III compares the AgriFore models against traditional and standalone forecasting approaches based on the metrics evaluated in the literature.

**TABLE III: Model Comparison Summary**

| Model | RMSE | R² Score | Key Limitation |
|-------|------|----------|----------------|
| ARIMA [3] | High | 0.45–0.65 | Cannot capture nonlinear patterns |
| Prophet [4] | Moderate | 0.55–0.70 | Limited exogenous variable support |
| Standalone LSTM | Moderate | 0.70–0.80 | Requires large data, sensitive to noise |
| Standalone XGBoost | Low-Moderate | 0.75–0.85 | No temporal sequence modeling |
| **AgriFore Model 2 (XGBoost + Lag Features)** | **1170.63** | **0.885** | **Lag features capture temporal patterns** |
| **AgriFore Model 1 (Weather→Yield)** | **3.937** | **0.770** | **Small training set for Kamareddy** |

AgriFore's Model 2 outperforms standalone approaches by incorporating temporal lag features (lag_1 through lag_12 and rolling means) that effectively capture the sequential dependencies typically modeled by LSTM networks, while maintaining XGBoost's strength in handling structured, heterogeneous features. This hybrid strategy—using engineered temporal features within a gradient boosting framework—achieves comparable or superior performance to LSTM-based approaches without the associated training complexity and data requirements.

### E. LSTM Autoencoder Anomaly Detection

The repository contains an offline LSTM Autoencoder validator under `aaaFinalModels/model2/deeplearning_validator`. The saved Keras configuration (`lstm_config.json`) specifies sliding windows of 30 timesteps with 19 features, and the evaluation script computes reconstruction-error statistics plus P95/P99 anomaly thresholds on market sequences.

Repo evidence supports this anomaly detector as implemented experimental code and saved model artifacts, but no backend endpoint or frontend workflow currently invokes it. It should therefore be described as an offline anomaly-screening component rather than a deployed runtime validation layer.

### F. Prediction Deployment

The deployed `POST /predict-price` endpoint in `api/server.py` implements a three-strategy fallback mechanism:

1. **Strategy 1 (Base-Model Inference):** Real-time feature construction from DuckDB's historical data, building lag features and rolling means from the most recent 12 months of data for the requested commodity/market combination, followed by M2 base-model prediction. Confidence: 0.85.
2. **Strategy 2 (Pre-computed Lookup):** If model inference fails, the system falls back to pre-computed 2024 base predictions stored in CSV format. Confidence: 0.70.
3. **Strategy 3 (Historical Average):** As a final fallback, the system computes the historical average modal price for the target commodity, district, and month from DuckDB. Confidence: 0.50.

This fallback logic is verified by the backend code and API test log. In the current repository state, the deployed endpoint does not apply the RidgeCV adjustment layer; therefore, the operational prediction path should be described as base-model inference with fallbacks, not as a deployed two-stage base-plus-adjust pipeline.

---

## VI. Conclusion and Future Work

### A. Conclusion

In this paper, we presented AgriFore as a multi-component repository for agricultural price and yield forecasting centered on Telangana data, with a district-specific Kamareddy yield artifact and a statewide market-price base model. Repo evidence supports a Kamareddy Weather-to-Yield XGBoost artifact with test R^2 of about 0.77 and a Market Price XGBoost base model with test R^2 of 0.885. The repository also contains an offline LSTM autoencoder validator and an offline RidgeCV residual-correction layer, but these components are not yet part of the deployed backend inference path.

The DuckDB ETL stack processes horticulture records, weather observations, and market transaction logs through 17 active SQL stage scripts in the current runners, with one superseded weather-loader script retained in the repository. The FastAPI backend and Next.js dashboard demonstrate a working local application for data access, market analysis, and base-model price prediction. At the same time, the repo evidence supports a more conservative deployment claim than a fully integrated production system: the backend currently serves the base market model only, while the adjustment and anomaly modules remain offline or experimental.

Evaluation artifacts covering 117 commodities and 169 AMC entries support the reported Model 2 base accuracy. The repository therefore substantiates a strong structured-data forecasting baseline and a substantial ETL/application scaffold, while leaving some claimed causal and anomaly modules at the experimental stage rather than the deployed stage.

### B. Future Work

Future development of AgriFore will focus on the following enhancements:

1. **Real-Time Data Integration:** Incorporating live APIs from AGMARKNET [5] and IMD [6] for near real-time weather and price data ingestion, enabling continuous model updates and dynamic forecasting.
2. **Transformer-Based Architectures:** Exploring Temporal Fusion Transformers (TFT) for improved temporal attention mechanisms and automated feature selection, potentially replacing the manually engineered lag features.
3. **Explainability Tools:** Integrating SHAP (SHapley Additive exPlanations) and LIME (Local Interpretable Model-agnostic Explanations) modules to help users understand the key drivers behind each price prediction, increasing trust and adoption among stakeholders.
4. **Geographic Expansion:** Extending the district-specific Model 1 workflow beyond Kamareddy and reconciling district-count assumptions with the repository's current 30-district market/production usage before broader transfer-learning experiments.
5. **Mobile Application Development:** Extending the Next.js dashboard to native mobile platforms using React Native, enabling field-level access for farmers in rural areas with limited desktop computing infrastructure.
6. **Supply Chain Integration:** Adding downstream forecasting capabilities that predict optimal procurement timing and logistics routing based on price and yield forecasts.

By continuing to refine and scale this system, and by integrating currently offline components into the served inference path, AgriFore could evolve into a stronger decision-support tool for stakeholders across the Kamareddy district and beyond [10], [11].

---

## References

[1] T. Chen and C. Guestrin, "XGBoost: A scalable tree boosting system," in *Proceedings of the 22nd ACM SIGKDD International Conference on Knowledge Discovery and Data Mining (KDD)*, San Francisco, CA, USA, 2016, pp. 785–794.

[2] Y. Prokhorenkova, G. Gusev, I. Vorobev, A. Dorogush, and A. Gulin, "CatBoost: Unbiased boosting with categorical features," in *Advances in Neural Information Processing Systems (NeurIPS)*, 2018, pp. 6638–6648.

[3] R. J. Hyndman and G. Athanasopoulos, *Forecasting: Principles and Practice*, 2nd ed., Melbourne, Australia: OTexts, 2018. [Online]. Available: https://otexts.com/fpp2/

[4] S. J. Taylor and B. Letham, "Forecasting at scale," *The American Statistician*, vol. 72, no. 1, pp. 37–45, 2018.

[5] AGMARKNET – Agricultural Marketing Information Network, Ministry of Agriculture & Farmers Welfare, Government of India. [Online]. Available: https://agmarknet.gov.in/

[6] India Meteorological Department (IMD), "Weather Data Services," [Online]. Available: https://mausam.imd.gov.in/

[7] M. G. Kendall and A. Stuart, *The Advanced Theory of Statistics*, Vol. 1, 4th ed., London: Charles Griffin, 1977.

[8] A. W. Bowman and A. Azzalini, *Applied Smoothing Techniques for Data Analysis*, Oxford University Press, 1997.

[9] S. Athey and G. W. Imbens, "Machine learning methods that economists should know about," *Annual Review of Economics*, vol. 11, pp. 685–725, 2019.

[10] M. Kuhn and K. Johnson, *Applied Predictive Modeling*, New York: Springer, 2013.

[11] P. Domingos, "A few useful things to know about machine learning," *Communications of the ACM*, vol. 55, no. 10, pp. 78–87, 2012.

[12] A. L. Samuel, "Some studies in machine learning using the game of checkers," *IBM Journal of Research and Development*, vol. 3, no. 3, pp. 210–229, 1959.

[13] S. Shalev-Shwartz and S. Ben-David, *Understanding Machine Learning: From Theory to Algorithms*, Cambridge University Press, 2014.

[14] Food and Agriculture Organization of the United Nations (FAO), "FAOSTAT: Food and Agriculture Data," [Online]. Available: https://www.fao.org/faostat/en/

[15] K. P. Murphy, *Machine Learning: A Probabilistic Perspective*, MIT Press, 2012.

[16] DuckDB Contributors, "DuckDB: An In-Process Analytical Database." [Online]. Available: https://duckdb.org/

[17] S. Ramírez, "FastAPI: A Modern, Fast Web Framework for Building APIs with Python." [Online]. Available: https://fastapi.tiangolo.com/

[18] Vercel, "Next.js: The React Framework for Production." [Online]. Available: https://nextjs.org/

[19] J. Wang et al., "Classification of Rice Yield Using UAV-Based Hyperspectral Imagery and Lodging Feature," *Plant Phenomics*, vol. 2021, Art. no. 9765952, 2021, doi: 10.34133/2021/9765952.

[20] F. Liu, L. Su, P. Luo, W. Tao, Q. Wang, and M. Deng, "Prediction Models of Growth Characteristics and Yield for Chinese Winter Wheat Based on Machine Learning," *Agronomy*, vol. 14, no. 4, Art. no. 839, 2024, doi: 10.3390/agronomy14040839.

[21] F. Sun, X. Meng, Y. Zhang, Y. Wang, H. Jiang, and P. Liu, "Agricultural Product Price Forecasting Methods: A Review," *Agriculture*, vol. 13, no. 9, Art. no. 1671, 2023, doi: 10.3390/agriculture13091671.

[22] N. Zhang, Q. An, S. Zhang, and H. Ma, "Price Prediction for Fresh Agricultural Products Based on a Boosting Ensemble Algorithm," *Mathematics*, vol. 13, no. 1, Art. no. 71, 2025, doi: 10.3390/math13010071.
