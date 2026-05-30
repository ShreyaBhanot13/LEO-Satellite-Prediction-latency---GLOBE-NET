# 🎯 FYP PROJECT: Explainable ML for Global Network Performance

## Project Title (Choose One)
**Option A (Comprehensive):** 
"Explainable Machine Learning Framework for Global Internet & LEO Satellite Network Performance Analysis"

**Option B (Simpler):** 
"Predicting and Explaining Global Internet & LEO Satellite Network Performance using Machine Learning"

---

## 🎨 What You're Building

An **AI system** that:
1. **Predicts** network performance (latency, download/upload speed)
2. **Explains** why performance is good/bad (SHAP - Explainable AI)
3. **Detects** anomalies (interference/congestion regions)
4. **Visualizes** insights across global regions

---

## 📊 Your Datasets → FYP Module Mapping

### **Dataset 1: Ookla India Latency (562,527 records)**
```
FILE: ookla_india_latency_holistic.csv
COLUMNS: latitude, longitude, state, avg_lat_ms, download_speed, upload_speed, ...
USE IN:
  ├─ Module 1 (Data Collection): Primary dataset for India
  ├─ Module 2 (Feature Engineering): Extract state, region, urban/rural
  ├─ Module 3 (Prediction): Predict latency using geographic/infrastructure features
  └─ Module 5 (Anomaly Detection): Find unexpected latency spikes
```

### **Dataset 2: TRAI Operator Data (1,767 records for 2025)**
```
FILE: TRAI_2025_all_states_5operators_12months.csv
COLUMNS: operator, technology, speed_kbps, signal_strength, lsa, month, year
USE IN:
  ├─ Module 1 (Data Collection): Operator-specific performance
  ├─ Module 2 (Feature Engineering): Operator type, signal strength as features
  ├─ Module 3 (Prediction): Train models per-operator or globally
  └─ Module 4 (XAI): Explain why Jio > BSNL using SHAP
```

### **Dataset 3: Germany iperf (Osnabrück)**
```
FILE: analysis_data_Osnabrück.csv
COLUMNS: download, upload, ping_avg, timestamp_start, ...
USE IN:
  ├─ Module 1 (Data Collection): Europe comparison baseline
  ├─ Module 3 (Prediction): Train separate model for Europe
  └─ Module 6 (Visualization): India vs Europe heatmaps
```

### **Dataset 4: Netherlands iperf (Enschede)**
```
FILE: analysis_data_Enschede.csv
COLUMNS: download, upload, ping_avg, timestamp_start, ...
USE IN:
  ├─ Module 1 (Data Collection): Europe comparison baseline
  ├─ Module 3 (Prediction): Train separate model for Europe
  └─ Module 6 (Visualization): India vs Europe heatmaps
```

---

## 🏗️ 6-Module FYP Architecture

### **Module 1️⃣: Data Collection & Understanding**

**Goal:** Load, explore, understand all datasets

**Tasks:**
- [ ] Load Ookla India (562K rows)
- [ ] Load TRAI operator data (1,767 rows)
- [ ] Load Germany & Netherlands iperf data
- [ ] Statistical summary (mean, median, std, distribution)
- [ ] Identify missing values & outliers
- [ ] Geographic distribution analysis

**Deliverable:** 
```
outputs/
├─ data_summary_ookla.txt (mean latency, speed stats by state)
├─ data_summary_trai.txt (speed stats by operator)
├─ data_summary_europe.txt (Germany vs Netherlands)
├─ missing_values_report.txt
└─ outlier_analysis.txt
```

**Python Script:** `01_data_collection_understanding.py`

---

### **Module 2️⃣: Feature Engineering & Preprocessing**

**Goal:** Create meaningful features for ML models

**Original Features (Ookla):**
- `avg_lat_ms` → latency (target for regression)
- `download_speed`, `upload_speed` → other targets
- `latitude`, `longitude` → geographic location
- `state` → categorical location

**Engineered Features (You'll create):**
```
1. GEOGRAPHIC FEATURES:
   - latitude_bin, longitude_bin (grid-based regions)
   - distance_to_metro (nearest city center)
   - rural_population_% (proxy for infrastructure)
   - elevation, climate_zone (if available)

2. TEMPORAL FEATURES:
   - month, day_of_week, hour (from timestamp if available)
   - seasonality (monsoon vs summer)
   - traffic_pattern (peak vs off-peak)

3. INFRASTRUCTURE FEATURES:
   - operator_diversity (# of operators in region)
   - tower_density (implied from latency variance)
   - technology_mix (% 4G vs 5G coverage)
   - signal_strength (from TRAI data if matched)

4. STATISTICAL FEATURES:
   - local_mean_latency (average in neighboring cells)
   - local_std_latency (variance - consistency metric)
   - anomaly_flag (is this region unusual?)

5. CROSS-DATASET FEATURES:
   - region_type (Urban/Suburban/Rural)
   - development_proxy (night-time lights equivalent using latency)
   - infrastructure_score (composite from multiple signals)
```

**Feature Selection:**
- Correlation analysis (which features matter most?)
- Feature importance from Random Forest
- Drop low-variance & highly correlated features

**Deliverable:**
```
outputs/
├─ engineered_dataset.csv (original + 20-30 new features)
├─ feature_correlation_matrix.png
├─ feature_selection_report.txt
└─ preprocessing_pipeline.pkl (scalers, encoders)
```

**Python Scripts:**
- `02_feature_engineering.py`
- `03_feature_selection.py`

---

### **Module 3️⃣: ML-Based Performance Prediction**

**Goal:** Train models to predict latency/speed

**Target Variables (What you'll predict):**
1. `latency` (primary target)
2. `download_speed` (secondary)
3. `upload_speed` (secondary)

**Models to Train:**
```
1. RANDOM FOREST
   - Fast, handles non-linear relationships
   - Feature importance built-in
   - Good baseline

2. SUPPORT VECTOR REGRESSION (SVR)
   - Non-linear relationships
   - Good for continuous targets
   - Hyperparameter tuning needed

3. GRADIENT BOOSTING (XGBoost/CatBoost)
   - State-of-the-art performance
   - Best R² scores
   - Slower but more accurate

4. LINEAR REGRESSION
   - Baseline model
   - Interpretable coefficients
```

**Training Pipeline:**
```
For each model:
├─ Split: 70% train, 30% test
├─ Hyperparameter tuning (GridSearchCV)
├─ Cross-validation (5-fold)
├─ Train on all regions or per-region?
├─ Evaluate: R², RMSE, MAE
└─ Save best model + preprocessing pipeline
```

**Evaluation Metrics:**
- R² Score (coefficient of determination)
- RMSE (root mean squared error)
- MAE (mean absolute error)
- MAPE (mean absolute percentage error)

**Deliverable:**
```
outputs/
├─ model_comparison.csv (R² for RF, SVR, XGBoost)
├─ best_model.pkl (highest R² model)
├─ predictions_vs_actual.png (scatter plot)
├─ residual_analysis.png
└─ training_report.txt (accuracy on different regions)
```

**Python Scripts:**
- `04_train_prediction_models.py`
- `05_model_evaluation.py`

---

### **Module 4️⃣: Explainable AI (XAI) - SHAP Analysis**

**Goal:** Answer "WHY is performance good/bad?"

**Using SHAP (SHapley Additive exPlanations):**

**Example Insights:**
```
Question: Why is latency high in rural areas?
SHAP Answer:
├─ Feature "rural_population_%" = +1.2ms impact
├─ Feature "tower_density" = -0.8ms impact
├─ Feature "operator_diversity" = +0.5ms impact
└─ Base value: 30ms (average) + impacts = 31.9ms (actual)

Question: Why is Jio faster than BSNL?
SHAP Answer:
├─ Operator "JIO" = -2ms benefit (newer infra)
├─ Signal strength difference = -1.5ms
├─ Infrastructure age proxy = -1.2ms
└─ Total: BSNL_latency - JIO_latency = 4.7ms (explained!)
```

**Visualizations:**
- **SHAP Summary Plot:** Which features matter most globally?
- **SHAP Force Plot:** Why is THIS specific prediction high/low?
- **SHAP Dependence Plot:** How does feature X affect latency?
- **Feature Importance Bar:** Top 10 most impactful features

**Deliverable:**
```
outputs/
├─ shap_summary_plot.png (global feature importance)
├─ shap_force_plots/ (examples from different regions)
├─ feature_importance_ranking.txt
└─ xai_insights_report.md (interpretation of findings)
```

**Python Script:** `06_explainable_ai_shap.py`

---

### **Module 5️⃣: Anomaly & Interference Risk Detection**

**Goal:** Flag regions where performance is worse than expected

**Scientific Approach:**
```
STEP 1: Get predictions from your ML model
  predicted_latency = model.predict(features)

STEP 2: Calculate residuals
  residual = actual_latency - predicted_latency
  
STEP 3: Detect anomalies
  IF residual < -2ms (much worse than expected):
    → FLAG AS "INTERFERENCE RISK"
    → Likely causes: congestion, spectrum interference, tower issues
    
  IF residual > +2ms (better than expected):
    → FLAG AS "OVER-PERFORMING"
    → Likely causes: low traffic, new infrastructure
```

**Algorithms:**
```
1. STATISTICAL THRESHOLDING (Simplest)
   - If |residual| > 2*std_dev → Anomaly
   
2. ISOLATION FOREST (Robust)
   - Unsupervised anomaly detection
   - Works on high-dimensional residuals
   - Flag top 5% as anomalies
   
3. RESIDUAL DISTRIBUTION ANALYSIS
   - Is residual = normal distribution? No? → Anomalies exist
   - Use Mahalanobis distance for multivariate anomalies
```

**Example Output:**
```
ANOMALY REGIONS IN INDIA:
┌─────────────────────────────────────────┐
│ State: Maharashtra, City: Mumbai         │
│ Tile ID: 12834                          │
│ Predicted Latency: 32ms                 │
│ Actual Latency: 48ms                    │
│ Residual: +16ms (ANOMALY!)              │
│ Confidence: 98%                         │
│ Root Cause: Likely congestion in        │
│            business district            │
└─────────────────────────────────────────┘

INTERPRETATION FOR EXAMINER:
"This region shows performance 16ms worse than 
expected given infrastructure indicators. This 
suggests temporary congestion or spectrum 
interference, not infrastructure deficiency."
```

**Deliverable:**
```
outputs/
├─ anomaly_detection_results.csv (flagged regions)
├─ anomaly_map_india.png (geographic heatmap)
├─ anomaly_analysis_report.txt
└─ interference_risk_by_state.txt
```

**Python Script:** `07_anomaly_detection.py`

---

### **Module 6️⃣: Visualization & Insights**

**Goal:** Create publication-quality visualizations

**Key Visualizations:**
```
1. INDIA PERFORMANCE HEATMAP
   - Geographic map colored by latency
   - Red (high latency) vs Green (low latency)
   - State-level breakdown

2. OPERATOR COMPARISON (Karnataka Focus)
   - Bar chart: Jio vs Airtel vs Vodafone vs BSNL
   - Metrics: Latency, Speed, Signal, Consistency
   
3. FEATURE IMPORTANCE (from SHAP)
   - Which factors matter most?
   - Bar chart ranked by impact

4. PREDICTED vs ACTUAL (Scatter Plot)
   - Model accuracy visualization
   - Highlight anomalies

5. INDIA vs EUROPE COMPARISON
   - Side-by-side heatmaps
   - Mean latency comparison
   - Infrastructure differences

6. ANOMALY DETECTION RESULTS
   - Map flagged regions
   - Statistics on interference zones

7. RESIDUAL DISTRIBUTION
   - Histogram of prediction errors
   - Shows model fairness across regions
```

**Deliverable:**
```
outputs/visualizations/
├─ india_latency_heatmap.png
├─ operator_comparison_karnataka.png
├─ shap_feature_importance.png
├─ predicted_vs_actual_scatter.png
├─ india_vs_europe_comparison.png
├─ anomaly_heatmap.png
└─ residual_distribution.png
```

**Optional Dashboard:**
- Streamlit app with interactive filters
- Click state → See operator breakdown
- Click operator → See SHAP explanations

**Python Scripts:**
- `08_create_visualizations.py`
- `09_streamlit_dashboard.py` (optional)

---

## 📈 ML Tasks Covered (For Viva/Report)

✅ **Data Collection & Exploration**
- Loading multi-source datasets
- Statistical analysis
- Distribution analysis

✅ **Feature Engineering**
- Domain knowledge (geographic, temporal, infrastructure)
- Feature creation (20-30 new features)
- Feature selection (correlation, importance)

✅ **Regression Models**
- Random Forest Regression
- Support Vector Regression
- Gradient Boosting (XGBoost/CatBoost)
- Model comparison & evaluation

✅ **Hyperparameter Tuning**
- GridSearchCV / RandomizedSearchCV
- Cross-validation
- Performance optimization

✅ **Explainable AI**
- SHAP values
- Feature importance
- Local & global explanations

✅ **Anomaly Detection**
- Residual analysis
- Statistical methods
- Isolation Forest
- Interference risk flagging

✅ **Error Analysis**
- Prediction error distribution
- Per-region performance
- Model limitations discussion

---

## 🎯 One-Line Project Summary (For Resume/Viva)

> "Developed an explainable machine learning system to predict and analyze global internet network performance across 3 regions (India, Germany, Netherlands), using SHAP-based explanations and residual-based anomaly detection to identify interference and congestion zones."

---

## 📋 Project Timeline & Effort

| Module | Task | Effort | Timeline |
|--------|------|--------|----------|
| **1** | Data Collection & Understanding | 1-2 days | 🟢 Easy |
| **2** | Feature Engineering | 2-3 days | 🟡 Medium |
| **3** | ML Model Training | 3-4 days | 🟡 Medium |
| **4** | SHAP/XAI Analysis | 2-3 days | 🟡 Medium |
| **5** | Anomaly Detection | 2-3 days | 🟡 Medium |
| **6** | Visualizations | 2-3 days | 🟢 Easy |
| **Report & Viva Prep** | Documentation | 2-3 days | 🟢 Easy |
| **TOTAL** | Full Project | **14-21 days** | **3 weeks** |

---

## ✅ Checklist Before You Start

- [ ] All CSV files downloaded & organized
- [ ] Python environment ready (pandas, sklearn, xgboost, shap, plotly)
- [ ] Jupyter notebooks created for each module
- [ ] Project directory structure created
- [ ] README.md written (project overview)
- [ ] Data understanding complete (explore first!)

---

## 🎓 Why Examiners Will Love This Project

✨ **Real-world data** - Not toy datasets
✨ **End-to-end ML pipeline** - Collection → Engineering → Training → Explanation → Deployment
✨ **Explainable AI** - Not a black box (SHAP is cutting-edge)
✨ **Scalable complexity** - Can add/remove features or models
✨ **Multiple ML tasks** - Regression, selection, tuning, anomaly detection, XAI
✨ **Clear storytelling** - Predicts AND explains findings
✨ **Business value** - ISPs/satellite companies would use this

---

**Next Step:** Module 1 - Data Collection & Understanding (explore your CSVs!)
