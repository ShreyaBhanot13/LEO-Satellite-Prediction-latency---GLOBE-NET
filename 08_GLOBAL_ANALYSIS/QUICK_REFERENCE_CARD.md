# 📌 FYP QUICK REFERENCE CARD

## PROJECT IN 30 SECONDS
**Title:** Explainable ML for Global Network Performance  
**Goal:** Predict + Explain + Detect anomalies in network latency  
**Data:** India (Ookla, TRAI) + Germany + Netherlands  
**Modules:** 6 (Data → Features → Models → SHAP → Anomalies → Visualizations)  
**Timeline:** 3-4 weeks  

---

## YOUR DATASETS AT A GLANCE

| Dataset | Records | Key Metric | Use |
|---------|---------|-----------|-----|
| **Ookla India** | 562,527 | Latency (ms) | PRIMARY - Train models |
| **TRAI 2025** | 1,767 | Speed (Kbps) | Operator comparison |
| **Germany** | ~10K | Latency (ms) | Europe baseline |
| **Netherlands** | ~10K | Latency (ms) | Europe baseline |

---

## 6 MODULES (Week by Week)

```
WEEK 1
┌─ Module 1: Data Understanding (3 days)
│  - Load all datasets
│  - Stats, distributions, quality check
│  └─ Output: Summary report + plots
│
└─ Module 2: Feature Engineering (2-3 days)
   - Create 20-30 features
   - Geographic, temporal, infrastructure
   └─ Output: Engineered dataset

WEEK 2
┌─ Module 3: ML Models (4 days)
│  - Train: RF, SVR, XGBoost
│  - Tune hyperparameters
│  - Compare (R² scores)
│  └─ Output: Best model

WEEK 3
┌─ Module 4: SHAP Explanations (2-3 days)
│  - Feature importance
│  - Local explanations (why THIS prediction?)
│  └─ Output: SHAP plots + insights
│
└─ Module 5: Anomaly Detection (2-3 days)
   - Residual analysis
   - Flag interference zones
   └─ Output: Anomaly map

WEEK 4
└─ Module 6: Visualizations (2-3 days)
   - Heatmaps, dashboards, comparisons
   - Final report + viva prep
   └─ Output: Publication-quality plots
```

---

## KEY METRICS TO REMEMBER

**Model Performance (Regression):**
- **R² Score**: How much variance explained? (target: >0.75)
- **RMSE**: Average prediction error (lower is better)
- **MAE**: Mean absolute error (lower is better)

**Data Quality:**
- **Missing values**: % of null data per column
- **Outliers**: Values >3 std dev from mean
- **Distribution**: Normal or skewed?

**Feature Importance (SHAP):**
- Which factors matter most?
- How do they affect latency?
- Are findings realistic?

---

## MODELS TO TRAIN

1. **Random Forest** ← Good baseline, fast
2. **SVR** ← Non-linear, may need tuning
3. **XGBoost** ← Usually best performance

**Comparison criteria:**
- R² score (highest wins)
- Training time (speed matters)
- Interpretability (SHAP compatibility)

---

## PYTHON PACKAGES YOU'LL USE

```python
# Data
import pandas as pd
import numpy as np

# ML Models
from sklearn.ensemble import RandomForestRegressor
from sklearn.svm import SVR
from xgboost import XGBRegressor

# Feature Engineering
from sklearn.preprocessing import StandardScaler
from sklearn.feature_selection import SelectKBest

# Evaluation
from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.metrics import r2_score, mean_squared_error, mean_absolute_error

# Explainability
import shap

# Anomaly Detection
from sklearn.ensemble import IsolationForest

# Visualization
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px

# Dashboard (optional)
import streamlit as st
```

---

## FOLDER STRUCTURE

```
08_GLOBAL_ANALYSIS/
├── README.md (start here)
├── QUICK_START.md
├── PROJECT_VISUAL_SUMMARY.md
├── 00_FYP_PROJECT_BLUEPRINT.md
├── 01_MODULE1_DATA_UNDERSTANDING_GUIDE.md
│
├── 01_Data/ (your CSV files)
├── 02_Scripts/ (Python code you write)
├── 03_Notebooks/ (Jupyter notebooks)
├── 04_Reports/ (Text outputs)
└── 05_Visualizations/ (PNG plots)
```

---

## MUST-HAVE OUTPUTS (For Report)

✅ **Module 1 Outputs:**
- data_summary_report.txt
- Missing_values_report.txt
- Distribution plots (PNG)

✅ **Module 2 Outputs:**
- engineered_dataset.csv
- feature_correlation_matrix.png
- feature_importance_ranking.txt

✅ **Module 3 Outputs:**
- model_comparison.csv (R² for each model)
- best_model.pkl (saved model)
- predictions_vs_actual.png

✅ **Module 4 Outputs:**
- shap_summary_plot.png
- shap_force_plots/ (examples)
- xai_insights_report.md

✅ **Module 5 Outputs:**
- anomaly_detection_results.csv
- anomaly_heatmap.png
- interference_risk_by_state.txt

✅ **Module 6 Outputs:**
- india_latency_heatmap.png
- operator_comparison.png
- india_vs_europe_comparison.png
- interactive_dashboard.py (optional)

---

## VIVA QUESTIONS (Be Ready)

**Q1: "What problem does your project solve?"**
→ Explaining network performance variations scientifically

**Q2: "Why use ML instead of statistics?"**
→ ML captures non-linear relationships & complex interactions

**Q3: "What makes your project unique?"**
→ SHAP-based explainability (cutting-edge) + anomaly detection

**Q4: "How do you validate your model?"**
→ Test set, cross-validation, per-region fairness, SHAP validation

**Q5: "How do you handle missing data?"**
→ [Your approach - either drop, impute, or document as limitation]

**Q6: "Why three countries?"**
→ Validates generalization across geographic diversity

**Q7: "What's your best R² score?"**
→ [Your actual number - expect 0.70-0.85 range is good]

**Q8: "What did you learn about network performance?"**
→ [Key findings - e.g., rural areas have high latency, Jio performs better, etc.]

---

## COMMON PITFALLS & FIXES

❌ **Data not loading**
→ Check file path, encoding, column names

❌ **Model R² too low (<0.60)**
→ Add more features, tune hyperparameters, check for data issues

❌ **SHAP plots not showing**
→ Ensure model is trained, data is normalized

❌ **Anomalies not making sense**
→ Review threshold, visualize residuals first

❌ **Forgot to split train-test**
→ Always: `X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3)`

---

## TIMELINE SANITY CHECK

| Time | Milestone | Status |
|------|-----------|--------|
| **Today** | Read all docs | ← You are here |
| **End of Week 1** | Module 1+2 done | Data understood, features created |
| **End of Week 2** | Module 3 done | Best model trained, R² ≥ 0.70 |
| **End of Week 3** | Module 4+5 done | SHAP + anomalies analyzed |
| **End of Week 4** | Module 6 done | Visualizations complete, report written |
| **Week 5** | Viva prep | Practice answers, optimize report |

---

## SUCCESS CHECKLIST (Copy & Print)

### Module 1 ✅
- [ ] All datasets loaded
- [ ] Data shape printed
- [ ] Missing values checked
- [ ] Statistics calculated (mean, median, std)
- [ ] Distributions visualized
- [ ] Summary report written

### Module 2 ✅
- [ ] 20+ features created
- [ ] Feature scaling applied
- [ ] Correlation analysis done
- [ ] Feature selection performed
- [ ] Engineered dataset saved

### Module 3 ✅
- [ ] RF model trained & evaluated
- [ ] SVR model trained & evaluated
- [ ] XGBoost model trained & evaluated
- [ ] Models compared (R² scores)
- [ ] Best model selected
- [ ] Hyperparameters tuned

### Module 4 ✅
- [ ] SHAP values computed
- [ ] Summary plot created
- [ ] Top 10 features ranked
- [ ] Local explanations generated
- [ ] Insights documented

### Module 5 ✅
- [ ] Residuals calculated
- [ ] Anomalies detected
- [ ] Threshold set scientifically
- [ ] Regions flagged
- [ ] Anomaly report written

### Module 6 ✅
- [ ] Geographic heatmap created
- [ ] Operator comparisons plotted
- [ ] Feature importance visualized
- [ ] India vs Europe dashboard
- [ ] Report written
- [ ] Viva slides prepared

---

## FINAL ADVICE

✨ **Take your time with Module 1** - Understanding data is 80% of the work

✨ **Document everything** - Your process matters as much as results

✨ **Use SHAP early** - It gives you confidence that your model is learning real patterns

✨ **Visualize constantly** - Plots help you spot issues early

✨ **Practice your viva answers** - Record yourself, watch back

✨ **Make it reproducible** - Clean code, saved models, documented pipelines

---

## QUICK START (Today)

```bash
# Step 1: Read
open "08_GLOBAL_ANALYSIS/README.md"
open "08_GLOBAL_ANALYSIS/QUICK_START.md"

# Step 2: Create notebook
jupyter notebook "08_GLOBAL_ANALYSIS/Module_1_Data_Understanding.ipynb"

# Step 3: Explore
# (Run data loading & exploration code)

# Step 4: Generate report
# (Save summary statistics & plots)
```

**You're ready! 🚀 Go build something awesome!**
