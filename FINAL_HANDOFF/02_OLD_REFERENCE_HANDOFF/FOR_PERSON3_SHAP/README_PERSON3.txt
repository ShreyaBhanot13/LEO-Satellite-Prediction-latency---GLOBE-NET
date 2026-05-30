================================================================================
               PERSON 3 - SHAP EXPLAINABILITY INSTRUCTIONS
================================================================================

Hi! This folder contains everything you need for SHAP analysis.

================================================================================
FILES IN THIS FOLDER
================================================================================

1. CATBOOST_V6_81.52.pkl    <- USE THIS MODEL FOR SHAP
   - CatBoost model with R2 = 81.52%
   - Single model, works perfectly with SHAP TreeExplainer
   - 42 features

2. test_data_v6_final.pkl   <- USE THIS DATA
   - Contains X_test (features) and y_test (actual latency)
   - 23,392 test samples
   - 42 engineered features

3. ensemble_best_model.pkl  <- OPTIONAL (more complex)
   - Ensemble model with R2 = 81.56%
   - Combines two models - harder to explain with SHAP

4. test_data_v5.pkl         <- OPTIONAL
   - Only needed if using ensemble
   - 32 features (subset of V6)

================================================================================
QUICK START CODE
================================================================================

import joblib
import shap
import matplotlib.pyplot as plt

# Step 1: Load model
model_dict = joblib.load('CATBOOST_V6_81.52.pkl')
model = model_dict['model']
shift = model_dict['shift_amount']  # Log transform shift (if needed)

# Step 2: Load test data
X_test, y_test = joblib.load('test_data_v6_final.pkl')

# Step 3: Create SHAP explainer
explainer = shap.TreeExplainer(model)

# Step 4: Calculate SHAP values (may take a few minutes)
shap_values = explainer.shap_values(X_test)

# Step 5: Summary plot - shows feature importance
shap.summary_plot(shap_values, X_test)
plt.savefig('shap_summary.png', dpi=300, bbox_inches='tight')

# Step 6: Bar plot - simpler feature importance
shap.summary_plot(shap_values, X_test, plot_type='bar')
plt.savefig('shap_bar.png', dpi=300, bbox_inches='tight')

# Step 7: Dependence plots for top features
top_features = ['ping_best', 'ping_worst', 'ping_stddev', 'network_stability', 'download']
for feat in top_features:
    shap.dependence_plot(feat, shap_values, X_test)
    plt.savefig(f'shap_dependence_{feat}.png', dpi=300, bbox_inches='tight')

================================================================================
FEATURE LIST (42 FEATURES)
================================================================================

Original Features (18):
- download, download_std      : Download speed and variability
- upload, upload_std          : Upload speed and variability
- measurement_steps           : Number of measurement steps
- ping_packet_loss            : Packet loss percentage
- ping_packets_send           : Packets sent
- ping_worst, ping_best       : Worst and best ping times
- ping_stddev                 : Ping standard deviation
- temp, rain, barom           : Weather conditions
- hour, day, month            : Time features
- day_of_week                 : Day of week (0-6)
- packet_loss_flag            : Binary flag for packet loss

Temporal Features (14) - Added in Phase 5:
- hour_sin, hour_cos          : Cyclical hour encoding
- day_sin, day_cos            : Cyclical day encoding
- month_sin, month_cos        : Cyclical month encoding
- is_business_hours           : 1 if 9am-5pm weekday
- ping_range                  : ping_worst - ping_best
- peak_hour_volatility        : Volatility during peak hours
- network_stability           : Stability metric
- ping_best_sq, ping_stddev_sq, ping_worst_sq : Squared terms
- hour_month_interaction      : Hour * Month interaction

Interaction Features (10) - Added in Phase 6:
- ping_quality_ratio          : ping_best / ping_worst
- volatility_per_range        : ping_stddev / ping_range
- hour_stability              : hour * network_stability
- day_month_pattern           : day * month
- download_upload_ratio       : download / upload
- speed_variability           : download_std + upload_std
- ping_download_interaction   : ping_stddev * download
- temp_ping_interaction       : temp * ping_stddev
- business_ping               : is_business_hours * ping_stddev
- ping_best_cubed             : ping_best ^ 3

================================================================================
WHAT TO DELIVER
================================================================================

1. SHAP Summary Plot
   - Shows all features ranked by importance
   - Color shows feature value (high/low)

2. SHAP Bar Plot
   - Simpler ranking of feature importance

3. SHAP Dependence Plots (Top 5 Features)
   - Shows how each feature affects predictions
   - Include interaction effects if visible

4. Written Analysis
   - Which features most affect network latency?
   - Any surprising findings?
   - Recommendations based on SHAP insights

================================================================================
TIPS
================================================================================

- If SHAP is slow, use a sample: shap_values = explainer.shap_values(X_test[:1000])
- Install SHAP: pip install shap
- CatBoost has native SHAP support - very efficient

================================================================================
MODEL INFO
================================================================================

Target Variable: ping_avg (average network latency in milliseconds)
Model Type: CatBoost Regressor
Accuracy: R2 = 0.8152 (81.52%)
Training Samples: 93,564
Test Samples: 23,392

Note: Model was trained on log(y + shift) transformed target.
SHAP values explain the log-transformed predictions.

================================================================================
CONTACT
================================================================================

If you have questions, contact Person 2 (ML Modeling).

================================================================================
