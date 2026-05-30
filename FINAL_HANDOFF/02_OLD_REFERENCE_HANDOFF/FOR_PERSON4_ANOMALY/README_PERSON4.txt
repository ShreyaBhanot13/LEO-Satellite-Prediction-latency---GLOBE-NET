================================================================================
              PERSON 4 - ANOMALY DETECTION INSTRUCTIONS
================================================================================

Hi! This folder contains everything you need for anomaly detection.

================================================================================
FILES IN THIS FOLDER
================================================================================

1. ensemble_best_model.pkl   <- MAIN MODEL (R2 = 81.56%)
   - Best performing model (ensemble of V5 + V6)
   - Requires both test data files

2. test_data_v5.pkl          <- REQUIRED FOR ENSEMBLE
   - 32 features (temporal features)

3. test_data_v6_final.pkl    <- REQUIRED FOR ENSEMBLE
   - 42 features (temporal + interaction features)
   - Also contains y_test (actual latency values)

================================================================================
CONCEPT: RESIDUAL-BASED ANOMALY DETECTION
================================================================================

The idea is simple:
1. Use the trained model to predict network latency
2. Compare predictions to actual values
3. Large differences (residuals) = ANOMALIES

Why this works:
- The model learned "normal" network behavior
- When actual latency is very different from predicted, something unusual happened
- High residual = unexpected network behavior = anomaly

================================================================================
QUICK START CODE
================================================================================

import joblib
import numpy as np
import matplotlib.pyplot as plt

# ============================================================================
# STEP 1: Load Model and Data
# ============================================================================

# Load ensemble model
ens = joblib.load('ensemble_best_model.pkl')

# Load both test datasets (ensemble needs both)
X_test_v5, _ = joblib.load('test_data_v5.pkl')
X_test_v6, y_test = joblib.load('test_data_v6_final.pkl')

print(f"Test samples: {len(y_test)}")

# ============================================================================
# STEP 2: Get Predictions
# ============================================================================

# Predict with both models
pred_v5_log = ens['v5_model'].predict(X_test_v5)
pred_v6_log = ens['v6_model'].predict(X_test_v6)

# Inverse log transform (model was trained on log-transformed target)
shift = ens['shift_amount']
pred_v5 = np.exp(pred_v5_log) - shift
pred_v6 = np.exp(pred_v6_log) - shift

# Combine with ensemble weights (0.3 * V5 + 0.7 * V6)
y_pred = ens['weight_v5'] * pred_v5 + ens['weight_v6'] * pred_v6

print(f"Predictions computed for {len(y_pred)} samples")

# ============================================================================
# STEP 3: Calculate Residuals
# ============================================================================

residuals = y_test - y_pred

print(f"\nResidual Statistics:")
print(f"  Mean: {residuals.mean():.4f} ms")
print(f"  Std:  {residuals.std():.4f} ms")
print(f"  Min:  {residuals.min():.4f} ms")
print(f"  Max:  {residuals.max():.4f} ms")

# ============================================================================
# STEP 4: Detect Anomalies
# ============================================================================

# Method 1: Z-score threshold (2.5 or 3 standard deviations)
threshold_multiplier = 2.5
threshold = threshold_multiplier * residuals.std()

anomaly_mask = np.abs(residuals) > threshold

# Separate positive and negative anomalies
high_anomalies = residuals > threshold   # Actual >> Predicted (network issues)
low_anomalies = residuals < -threshold   # Actual << Predicted (unusually good)

print(f"\nAnomaly Detection Results (threshold = {threshold_multiplier} std):")
print(f"  Threshold: +/- {threshold:.4f} ms")
print(f"  Total anomalies: {anomaly_mask.sum()} ({100*anomaly_mask.mean():.2f}%)")
print(f"  High anomalies (worse than expected): {high_anomalies.sum()}")
print(f"  Low anomalies (better than expected): {low_anomalies.sum()}")

# ============================================================================
# STEP 5: Visualizations
# ============================================================================

# Plot 1: Residual Distribution
plt.figure(figsize=(10, 6))
plt.hist(residuals, bins=100, edgecolor='black', alpha=0.7)
plt.axvline(threshold, color='red', linestyle='--', label=f'+{threshold_multiplier} std')
plt.axvline(-threshold, color='red', linestyle='--', label=f'-{threshold_multiplier} std')
plt.xlabel('Residual (Actual - Predicted) in ms')
plt.ylabel('Frequency')
plt.title('Distribution of Prediction Errors')
plt.legend()
plt.savefig('residual_distribution.png', dpi=300, bbox_inches='tight')
plt.show()

# Plot 2: Actual vs Predicted with Anomalies
plt.figure(figsize=(10, 8))
plt.scatter(y_test[~anomaly_mask], y_pred[~anomaly_mask], alpha=0.3, s=5, label='Normal')
plt.scatter(y_test[anomaly_mask], y_pred[anomaly_mask], alpha=0.7, s=20, c='red', label='Anomaly')
plt.plot([y_test.min(), y_test.max()], [y_test.min(), y_test.max()], 'k--', label='Perfect Prediction')
plt.xlabel('Actual Latency (ms)')
plt.ylabel('Predicted Latency (ms)')
plt.title('Actual vs Predicted with Anomalies Highlighted')
plt.legend()
plt.savefig('actual_vs_predicted_anomalies.png', dpi=300, bbox_inches='tight')
plt.show()

# Plot 3: Residuals over index (time-like)
plt.figure(figsize=(14, 5))
plt.scatter(range(len(residuals)), residuals, alpha=0.3, s=2)
plt.axhline(threshold, color='red', linestyle='--')
plt.axhline(-threshold, color='red', linestyle='--')
plt.xlabel('Sample Index')
plt.ylabel('Residual (ms)')
plt.title('Residuals Over Time with Anomaly Thresholds')
plt.savefig('residuals_over_time.png', dpi=300, bbox_inches='tight')
plt.show()

# ============================================================================
# STEP 6: Analyze Anomalies
# ============================================================================

# Get anomaly indices
anomaly_indices = np.where(anomaly_mask)[0]

# Extract anomaly data for analysis
X_anomalies = X_test_v6[anomaly_mask]
y_anomalies = y_test[anomaly_mask]
pred_anomalies = y_pred[anomaly_mask]
residual_anomalies = residuals[anomaly_mask]

print(f"\nAnomaly Analysis:")
print(f"  Anomaly actual latency - Mean: {y_anomalies.mean():.2f} ms")
print(f"  Normal actual latency - Mean: {y_test[~anomaly_mask].mean():.2f} ms")

# ============================================================================
# STEP 7: Save Results
# ============================================================================

# Save anomaly indices
np.save('anomaly_indices.npy', anomaly_indices)

# Save anomaly details
anomaly_results = {
    'anomaly_mask': anomaly_mask,
    'residuals': residuals,
    'threshold': threshold,
    'y_test': y_test,
    'y_pred': y_pred,
    'n_anomalies': anomaly_mask.sum(),
    'anomaly_rate': anomaly_mask.mean()
}
joblib.dump(anomaly_results, 'anomaly_detection_results.pkl')

print("\nResults saved!")
print("  - anomaly_indices.npy")
print("  - anomaly_detection_results.pkl")

================================================================================
ALTERNATIVE METHODS
================================================================================

You can try different anomaly detection approaches:

# Method 2: IQR-based threshold
Q1 = np.percentile(residuals, 25)
Q3 = np.percentile(residuals, 75)
IQR = Q3 - Q1
lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR
anomalies_iqr = (residuals < lower_bound) | (residuals > upper_bound)

# Method 3: Percentile-based
upper_percentile = np.percentile(residuals, 99)
lower_percentile = np.percentile(residuals, 1)
anomalies_percentile = (residuals > upper_percentile) | (residuals < lower_percentile)

# Method 4: Isolation Forest on residuals
from sklearn.ensemble import IsolationForest
iso = IsolationForest(contamination=0.02, random_state=42)
anomalies_iso = iso.fit_predict(residuals.reshape(-1, 1)) == -1

================================================================================
WHAT TO DELIVER
================================================================================

1. Anomaly Detection Methodology
   - Which method did you use? (Z-score, IQR, percentile, etc.)
   - What threshold did you choose and why?

2. Results Summary
   - Total number of anomalies detected
   - Percentage of data classified as anomalies
   - Breakdown of high vs low anomalies

3. Visualizations
   - Residual distribution histogram with thresholds
   - Actual vs Predicted scatter plot with anomalies highlighted
   - Residuals over time/index

4. Anomaly Analysis
   - What patterns do anomalies show?
   - Are anomalies associated with specific times/conditions?
   - Interpretation of high vs low anomalies

5. Recommendations
   - What network conditions lead to anomalies?
   - Suggestions for network monitoring

================================================================================
INTERPRETATION GUIDE
================================================================================

Residual = Actual - Predicted

POSITIVE residual (Actual > Predicted):
  - Network latency was HIGHER than expected
  - Something caused unexpected delays
  - Could indicate: congestion, hardware issues, interference

NEGATIVE residual (Actual < Predicted):
  - Network latency was LOWER than expected
  - Network performed better than normal
  - Could indicate: light traffic, optimal conditions

================================================================================
MODEL INFO
================================================================================

Target Variable: ping_avg (average network latency in milliseconds)
Model Type: Ensemble (0.3*CatBoost_V5 + 0.7*CatBoost_V6)
Accuracy: R2 = 0.8156 (81.56%)
RMSE: 0.4217 ms
Test Samples: 23,392

================================================================================
CONTACT
================================================================================

If you have questions, contact Person 2 (ML Modeling).

================================================================================
