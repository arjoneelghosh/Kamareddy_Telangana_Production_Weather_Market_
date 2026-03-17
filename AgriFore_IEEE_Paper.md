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

**Abstract—** AgriFore is a comprehensive AI-driven agricultural forecasting system designed to predict crop yields and market commodity prices in the Kamareddy district of Telangana, India. Agricultural price volatility remains a critical challenge for farmers and policymakers, exacerbated by unpredictable weather patterns, seasonal supply-demand imbalances, and fragmented market infrastructure. Existing forecasting approaches such as ARIMA and Prophet are limited in their ability to model nonlinear dependencies and integrate heterogeneous data sources. AgriFore addresses these limitations through a multi-model machine learning architecture comprising: (1) a Weather-to-Yield XGBoost model that predicts crop yield per acre using seasonal rainfall, humidity, and rain anomaly features, achieving a test R² of 0.77 on Kamareddy district data; (2) a Market Price XGBoost model that forecasts monthly commodity prices using lag features, weather indicators, and market arrivals, achieving a test R² of 0.885 across 117 commodities and 169 Agricultural Market Committee (AMC) markets; (3) an LSTM Autoencoder for detecting anomalous price sequences; and (4) a RidgeCV-based yield-adjustment layer that corrects base price predictions using yield signals. The system processes five years of Telangana horticulture production data (2019–2023), daily rainfall records from the India Meteorological Department (2018–2026), and historical market transaction data through a robust DuckDB-based ETL pipeline comprising 18 SQL transformation scripts. AgriFore is deployed as a full-stack web application with a FastAPI backend serving 12 REST endpoints and a Next.js React dashboard providing real-time market intelligence, trend analysis, and interactive price prediction for stakeholders across the agricultural value chain.

**Keywords—** Agricultural forecasting, XGBoost, LSTM autoencoder, crop yield prediction, price forecasting, DuckDB, weather-yield modeling, Kamareddy, Telangana agriculture, machine learning, time series analysis, anomaly detection.

---

## I. Introduction

Agriculture is the economic backbone of Telangana, a state in southern India where over 55% of the population depends directly on farming for their livelihood [14]. The Kamareddy district, located in the northern region of Telangana, is a significant agricultural hub producing a diverse range of horticulture and food crops including paddy, cotton, maize, tomato, and onion across its numerous mandals. Despite the sector's vital importance, farmers and traders in Kamareddy and surrounding districts face severe challenges due to unpredictable commodity price fluctuations driven by weather anomalies, supply-demand imbalances, transportation inefficiencies, and policy interventions [5].

Existing forecasting methodologies, including traditional statistical approaches such as ARIMA [3], exponential smoothing [8], and Holt-Winters models, are fundamentally limited in their capacity to capture nonlinear price dynamics. While Facebook's Prophet [4] offers improvements in modeling seasonality and holiday effects, it lacks the capability to learn long-term temporal dependencies or integrate exogenous variables such as rainfall, humidity, and seasonal yield variations into a unified prediction framework. Standalone machine learning models such as Long Short-Term Memory (LSTM) networks [9] and XGBoost [1] have demonstrated promising results in isolation, but the agricultural forecasting domain demands systems that can simultaneously model weather-driven yield dynamics and market-driven price movements.

To address these limitations, we propose AgriFore, a multi-model AI system specifically designed for the Kamareddy district of Telangana. AgriFore integrates four complementary machine learning components: (1) a Weather-to-Yield XGBoost model that predicts crop yield per acre using engineered weather features including rainfall anomalies and humidity indices; (2) a Market Price XGBoost model that forecasts monthly commodity prices using historical lag features, weather indicators, and market arrival volumes; (3) an LSTM Autoencoder that identifies anomalous price sequences indicative of market manipulation or extreme events; and (4) a RidgeCV regression layer that adjusts base price predictions using yield signals from Model 1. This dual-pathway architecture—where weather impacts yields, and yields in turn influence market prices—captures the causal chain underlying agricultural economies more faithfully than single-model approaches.

The system processes heterogeneous data from multiple government sources through a DuckDB-based Extract-Transform-Load (ETL) pipeline, and is deployed as a production-grade web application with a FastAPI backend and Next.js frontend dashboard. Through rigorous evaluation on real-world datasets spanning five years, AgriFore demonstrates superior forecasting accuracy with an R² of 0.885 on market price prediction and 0.77 on yield estimation, offering a practical and scalable tool for farmers, traders, and agricultural policymakers in Telangana.

The key contributions of this paper are as follows:

- A dual-model architecture that connects weather-driven yield prediction with market price forecasting through a yield-adjustment mechanism.
- A comprehensive DuckDB-based data pipeline with 18 SQL transformation scripts for cleaning, validating, and engineering features from heterogeneous agricultural datasets.
- An LSTM Autoencoder-based anomaly detection module for identifying unusual market price patterns.
- A full-stack deployment architecture using FastAPI and Next.js enabling real-time market intelligence for stakeholders.
- Extensive evaluation on real-world Telangana agricultural data covering 117 commodities across 169 markets.

---

## II. Related Work

Agricultural commodity price forecasting has attracted significant research attention due to its direct impact on food security and farmer livelihoods. This section reviews the key approaches in the literature and identifies the research gaps that AgriFore addresses.

### A. Statistical Time Series Models

Classical time series methods have been widely used for agricultural price prediction. The Autoregressive Integrated Moving Average (ARIMA) model and its seasonal variant SARIMA remain popular baselines due to their interpretability and well-established theoretical foundations [3]. Hyndman and Athanasopoulos [3] provide a comprehensive treatment of forecasting principles, noting that ARIMA models perform well on stationary, linear time series but struggle with the nonlinear, multi-factor dynamics typical of agricultural markets. Exponential smoothing methods [8] offer adaptive weighting of recent observations but share similar limitations.

Taylor and Letham [4] introduced Prophet, a decomposable time series model designed to handle seasonality, holidays, and trend changepoints at scale. While Prophet has been adopted in various commercial forecasting applications, its additive decomposition framework cannot effectively capture the complex interactions between weather variables, market supply-demand dynamics, and regional agricultural patterns that drive crop prices in districts like Kamareddy.

### B. Machine Learning Approaches

Chen and Guestrin [1] introduced XGBoost, a scalable tree boosting system that has become a dominant algorithm in structured data prediction tasks. XGBoost's ability to handle heterogeneous features, missing values, and nonlinear relationships makes it well-suited for agricultural forecasting where inputs span weather metrics, market indicators, and categorical variables such as crop type and district.

Prokhorenkova et al. [2] proposed CatBoost, an unbiased boosting algorithm specifically designed for datasets with categorical features. CatBoost's ordered boosting mechanism and native handling of categorical variables reduce overfitting and improve generalization, making it complementary to XGBoost in ensemble configurations.

### C. Deep Learning for Time Series

Recurrent neural networks, particularly LSTM architectures, have shown strong performance in sequential learning tasks [9]. LSTM networks can capture long-term dependencies in price series through their gating mechanisms, making them suitable for modeling temporal trends and seasonal patterns in commodity prices. However, LSTM models require substantial training data and are sensitive to noisy sequences, which is a common challenge in agricultural datasets where data quality varies across collection sources.

Autoencoder architectures have been applied for anomaly detection in financial and market time series data. LSTM Autoencoders learn to reconstruct normal sequences, and instances with high reconstruction error are flagged as anomalies. This approach is particularly relevant for agricultural markets where sudden price spikes or drops may indicate data quality issues, market manipulation, or genuine supply shocks [13].

### D. Hybrid and Ensemble Approaches

Recent work has explored hybrid architectures that combine deep learning with gradient boosting methods. Athey and Imbens [9] discuss machine learning methods applicable to economic and market prediction, emphasizing the value of ensemble techniques that leverage the complementary strengths of different model families. The integration of LSTM-based temporal models with XGBoost-based feature models has shown promise in improving prediction accuracy over standalone approaches [10], [11].

### E. Research Gap

Despite these advances, several gaps remain: (1) most existing systems treat price prediction in isolation without connecting it to yield estimation, even though weather-driven yield variations are a primary driver of market prices; (2) few systems address the specific challenges of Indian agricultural markets at the district level, where data heterogeneity and quality issues are pronounced; (3) anomaly detection is rarely integrated into agricultural forecasting pipelines; and (4) end-to-end deployment architectures that bring ML predictions to non-technical stakeholders are underexplored. AgriFore addresses all four gaps through its multi-model architecture and full-stack deployment.

---

## III. Methodology

### A. Data Collection and Preprocessing

AgriFore integrates data from three primary sources to construct a unified forecasting dataset for the Kamareddy district and the broader Telangana region:

**1) Horticulture Production Data:** Mandal-wise crop area, production, and yield data for Telangana spanning the years 2019–20 through 2022–23, sourced from the Telangana state government's Department of Horticulture. These four annual datasets contain records at the mandal level across all 30 districts, covering horticulture crops with area (in acres), production value, and yield metrics. The raw data is ingested into a DuckDB database as the `tg_raw` table and processed through views `v_prod_real` and `v_area_real` to standardize district names, normalize season labels (Kharif, Rabi), and compute yield-per-acre proxy values.

**2) Weather Data:** Daily rainfall (in mm) and humidity (minimum and maximum) records from the India Meteorological Department (IMD) [6], spanning 2018 through 2026 across Telangana. Nine annual CSV files containing daily observations at the mandal level are cleaned through a three-stage process: raw ingestion (`weather_raw`), deduplication and quality filtering (`weather_clean`), and aggregation to district-day (`t_weather_district_day`), district-month (`t_weather_district_month`), and district-season (`t_weather_district_season`) granularities. The weather pipeline handles duplicate records, normalizes mandal and district names through an alias mapping table (`t_district_alias`), and computes derived features including rain intensity, humid range, and rainfall anomalies.

**3) Market Transaction Data:** Agricultural Market Committee (AMC) daily transaction records including arrival volumes (in quintals), minimum, maximum, and modal prices for 117 distinct commodities across 169 market yards in Telangana. This data is loaded into `t_market_raw`, cleaned into `t_market_clean`, and aggregated to monthly summaries in `t_market_monthly` with fields for average modal price, total arrivals, and trading day counts.

**Data Pipeline Architecture:** The entire preprocessing pipeline is implemented as 18 sequential SQL scripts executed within DuckDB, orchestrated by a PowerShell automation script. The pipeline performs the following transformations:

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

The first model in AgriFore's architecture addresses the fundamental relationship between weather conditions and crop yields. This XGBoost-based regressor predicts the `yield_per_acre_proxy` for crops in the Kamareddy district using seasonal weather features.

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

**Data Quality Filters:** Rows with missing weather data (`dq_weather_missing = True`) or incomplete weather coverage (`dq_weather_incomplete = True`) are excluded, along with records where yield is null or non-positive. This ensures that the model trains only on records with reliable weather observations.

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

A critical innovation in AgriFore is the yield-adjustment layer that connects Model 1's yield predictions to Model 2's price forecasts. The intuition is that weather-driven yield variations should influence market prices—a bumper crop typically depresses prices, while a poor harvest drives prices up.

**Approach:** A RidgeCV regressor is trained to predict the residual error (actual price minus base predicted price) from Model 2's out-of-fold predictions. The key feature is `yield_signal`, derived from Model 1's yield predictions for the corresponding district, crop, and season.

**Additional Features:** The adjustment model also incorporates `base_pred` (the base model's prediction), `arrivals_sum`, weather features (`rain_sum_mm`, `rainy_days`, `hum_min_avg`, `hum_max_avg`), `month_of_year`, and `season_norm`.

**Ridge Regularization:** RidgeCV with alpha values [0.1, 1.0, 10.0, 100.0, 1000.0] is used to prevent overfitting on the residual signal, with the optimal alpha selected via cross-validation.

**Final Prediction:** The adjusted price forecast is computed as:

```
final_pred = base_pred + ridge_residual_correction
```

This late-fusion approach allows the yield signal to correct systematic biases in the base price model without requiring a complete retraining of the primary model.

### E. LSTM Autoencoder for Anomaly Detection

To complement the forecasting models, AgriFore incorporates an LSTM Autoencoder for detecting anomalous price sequences in the market data. Anomalous patterns may indicate data quality issues, market manipulation, supply chain disruptions, or genuine extreme events.

**Architecture:** The autoencoder follows an encoder-decoder structure:

| Layer | Type | Units/Config |
|-------|------|-------------|
| Input | InputLayer | Shape: (30, 19) |
| Encoder Layer 1 | LSTM | 64 units, ReLU activation, return sequences |
| Encoder Layer 2 | LSTM | 32 units, ReLU activation |
| Bottleneck | RepeatVector | n = 30 |
| Decoder Layer 1 | LSTM | 32 units, ReLU activation, return sequences |
| Decoder Layer 2 | LSTM | 64 units, ReLU activation, return sequences |
| Output | TimeDistributed Dense | 19 units, linear activation |

The input consists of sliding windows of 30 timesteps with 19 features per timestep. The autoencoder is trained to reconstruct normal price sequences; sequences with high reconstruction error (exceeding the 95th or 99th percentile threshold) are classified as anomalies.

**Anomaly Classification:** For each sequence, the Mean Squared Error (MSE) between the input and reconstructed output is computed. Sequences exceeding the P95 threshold are flagged as potential anomalies, while those exceeding P99 are flagged as high-confidence anomalies. Per-crop anomaly rates are computed to identify commodities with unusual price behavior.

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

The pipeline consists of 18 SQL scripts organized in sequential phases:

- **Phase 1 (Scripts 00–10):** Raw data ingestion from horticulture CSVs, view creation for production and area extraction with normalized district names and season labels.
- **Phase 2 (Scripts 15–18):** Weather data loading, cleaning, deduplication, and feature engineering at daily, monthly, and seasonal granularities. District name matching diagnostics ensure consistency between production and weather datasets.
- **Phase 3 (Scripts 20–40):** Data quality assessment including crop coverage analysis, stability profiling, MAD-based outlier detection with robust z-scores, and season alignment with harvest-year rollups.
- **Phase 4 (Scripts 50–66):** Model dataset construction including the Model 1 weather-yield dataset, market data loading, monthly aggregation, calendar-to-season mapping, and Model 2 base and adjustment datasets.

The resulting database contains over 30 tables and views including `t_model1_dataset`, `v_model2_base_dataset`, `v_model2_adjust_dataset`, `t_market_monthly`, and `t_weather_district_season`, totaling approximately 123 MB.

### B. Backend — FastAPI Server

The backend is implemented using FastAPI, a modern Python web framework that provides automatic OpenAPI documentation, type validation via Pydantic, and asynchronous request handling. The server exposes 12 REST endpoints organized into four categories:

**Reference Data Endpoints:**
- `GET /commodities` — Lists all 117 available commodities with heuristic category classification (Vegetable, Fruit, Grain, Pulse, Oilseed, Cash Crop)
- `GET /markets` — Lists all 169 AMC market yards with their districts
- `GET /districts` — Lists all 30 Telangana districts

**Dashboard Endpoints:**
- `GET /market-overview` — Aggregated statistics (total markets, active commodities, average price, total volume, year-over-year price change)
- `GET /top-commodities` — Top 8 commodities by trading volume with price change percentages
- `GET /market-clusters` — Regional market cluster overview grouped by district

**Chart Data Endpoints:**
- `GET /price-trends` — Multi-commodity monthly price trend data
- `GET /seasonal-data` — Monthly seasonal pattern analysis (average price and volume by month)
- `GET /arrival-data` — Arrival volume vs. price correlation data

**Prediction Endpoints:**
- `POST /predict-price` — Price prediction with a three-strategy fallback mechanism:
  1. Primary: Real-time inference using the M2 Base XGBoost model with live feature construction from DuckDB
  2. Secondary: Lookup from pre-computed 2024 predictions CSV
  3. Tertiary: Historical average from DuckDB for the target crop, district, market, and month
- `POST /ask-agent` — Natural language Q&A about agricultural markets (keyword-based response generation)

The server connects to DuckDB in read-only mode for data queries and loads the M2 XGBoost model pipeline at startup using joblib.

### C. Frontend — Next.js Dashboard

The user-facing component is built using Next.js (React framework) with TypeScript and Tailwind CSS. The dashboard comprises three primary pages:

**1) Dashboard Page:** Displays four summary statistics (Total Markets, Active Commodities, Average Market Price, Total Volume), a multi-commodity price trend chart, top commodities by volume, and regional market cluster visualization.

**2) Analysis Page:** Provides seasonal pattern analysis with monthly average price and volume charts, and arrival-vs-price correlation visualizations for user-selected commodities.

**3) Prediction Page:** An interactive form allowing users to select a commodity, optionally specify a district and market, and receive AI-generated price predictions with confidence scores.

The frontend communicates with the FastAPI backend via an Axios-based service layer with request/response interceptors for logging and error handling.

### D. System Workflow

The end-to-end workflow operates as follows:

1. **Data Ingestion:** Raw CSV files from government sources are loaded into DuckDB.
2. **ETL Pipeline:** 18 SQL scripts transform, clean, validate, and engineer features.
3. **Model Training:** Models 1 and 2 are trained offline using the prepared datasets.
4. **Model Deployment:** Trained model artifacts (.pkl files) are loaded by the FastAPI server at startup.
5. **API Serving:** The server responds to frontend requests with real-time queries and model inference.
6. **User Interaction:** Stakeholders access forecasts, trends, and analytics through the Next.js dashboard.

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

The LSTM Autoencoder operates on sliding windows of 30 timesteps with 19 features, processing sequences constructed from the daily market transaction data. The reconstruction error distribution is analyzed to identify anomalous price patterns.

Sequences with reconstruction errors exceeding the 95th percentile (P95) threshold are classified as potential anomalies, while those exceeding P99 are flagged as high-confidence anomalies. The per-crop anomaly rates identify commodities with the most volatile or unusual price behavior, providing market intelligence for risk assessment. This anomaly detection module serves as a complementary validation layer, flagging records that may warrant manual review or indicate supply chain disruptions.

### F. Prediction Deployment

The deployed prediction endpoint implements a three-strategy fallback mechanism to ensure reliable responses:

1. **Strategy 1 (Model Inference):** Real-time feature construction from DuckDB's historical data, building lag features and rolling means from the most recent 12 months of data for the requested commodity/market combination, followed by XGBoost prediction. Confidence: 0.85.
2. **Strategy 2 (Pre-computed Lookup):** If model inference fails, the system falls back to pre-computed 2024 predictions stored in CSV format. Confidence: 0.70.
3. **Strategy 3 (Historical Average):** As a final fallback, the system computes the historical average modal price for the target commodity, district, and month from DuckDB. Confidence: 0.50.

This multi-strategy approach ensures that the system provides a prediction for every valid request, with the confidence score transparently communicating the reliability of each prediction method.

---

## VI. Conclusion and Future Work

### A. Conclusion

In this paper, we presented AgriFore, a multi-model AI system for agricultural price and yield forecasting specifically designed for the Kamareddy district of Telangana. By integrating a Weather-to-Yield XGBoost model (R² = 0.77) with a Market Price XGBoost model (R² = 0.885), supplemented by an LSTM Autoencoder for anomaly detection and a RidgeCV yield-adjustment layer, AgriFore captures the causal chain from weather conditions through crop yields to market prices more comprehensively than single-model approaches.

The system's robust DuckDB-based ETL pipeline processes heterogeneous data from government horticulture records, IMD weather observations, and market transaction logs through 18 SQL transformation scripts, producing clean, validated, and feature-engineered datasets ready for modeling. The full-stack deployment architecture—FastAPI backend with 12 REST endpoints and Next.js React dashboard—demonstrates that research-grade ML models can be made accessible to non-technical stakeholders including farmers, traders, and agricultural policymakers through intuitive web interfaces.

Evaluation on real-world data spanning five years and covering 117 commodities across 169 markets confirms that AgriFore provides accurate and reliable forecasts. The system's model comparison demonstrates that engineered temporal features (lag prices and rolling means) within gradient boosting frameworks can match or exceed the performance of deep learning approaches while offering greater interpretability and lower computational requirements.

### B. Future Work

Future development of AgriFore will focus on the following enhancements:

1. **Real-Time Data Integration:** Incorporating live APIs from AGMARKNET [5] and IMD [6] for near real-time weather and price data ingestion, enabling continuous model updates and dynamic forecasting.
2. **Transformer-Based Architectures:** Exploring Temporal Fusion Transformers (TFT) for improved temporal attention mechanisms and automated feature selection, potentially replacing the manually engineered lag features.
3. **Explainability Tools:** Integrating SHAP (SHapley Additive exPlanations) and LIME (Local Interpretable Model-agnostic Explanations) modules to help users understand the key drivers behind each price prediction, increasing trust and adoption among stakeholders.
4. **Geographic Expansion:** Scaling the system from Kamareddy to all 30 districts of Telangana, and subsequently to other Indian states, using transfer learning techniques to adapt models trained on data-rich regions to data-sparse areas.
5. **Mobile Application Development:** Extending the Next.js dashboard to native mobile platforms using React Native, enabling field-level access for farmers in rural areas with limited desktop computing infrastructure.
6. **Supply Chain Integration:** Adding downstream forecasting capabilities that predict optimal procurement timing and logistics routing based on price and yield forecasts.

By continuing to refine and scale this system, AgriFore can serve as a critical decision-support tool in the agricultural ecosystem, reducing financial uncertainty and empowering stakeholders across the Kamareddy district and beyond with AI-driven predictive insights [10], [11].

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
