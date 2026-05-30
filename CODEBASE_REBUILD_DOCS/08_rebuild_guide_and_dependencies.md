# Rebuild Guide and Dependencies

## Purpose of This File

This file explains how a developer could recreate the project structure and execution flow without having the original source code open. It does not provide raw code, but it does provide the architectural order, dependencies, and artifact contracts required to reproduce the work.

## Main Dependencies by Project Area

### Common data and serialization stack

- `pandas`
- `numpy`
- `joblib`
- `pathlib`

These are used across almost every phase for dataframe processing, numeric computation, and saving intermediate artifacts.

### Benchmark modeling stack

- `scikit-learn`
- `xgboost`
- `lightgbm`
- `catboost`

Used for regression and classification model training, evaluation, splitting, and in some cases cross-validation or parameter search.

### Explainability stack

- `shap`

Used to compute global and local feature-importance explanations for the India regression model and the final zone-risk classifier.

### Visualization and dashboard stack

- `matplotlib`
- `seaborn`
- `plotly`
- `streamlit`

Used for offline charts and the final dashboard.

### Utility and integration stack

- `json`
- `re`
- `html`
- `argparse`
- `shutil`

Used for configuration parsing, file operations, text parsing, and handoff packaging.

## End-to-End Execution Order

## Benchmark branch

### Phase 1 baseline

1. Run the dataset preparation script.
2. Train the three baseline regressors.
3. Compare results.
4. Generate visualizations.

### Phase 2 feature engineering

1. Analyze baseline features.
2. Create V2 engineered train/test data.
3. Retrain the candidate models on V2.
4. Compare V2 against V1.
5. Save the best V2 model.

### Phase 3 to Phase 5 optimization

1. Test stacking, LightGBM, CatBoost, and log-target regression.
2. Compare advanced methods against V2.
3. Run ultra-optimization if needed.
4. Build Phase 5 temporal features.
5. Retrain top models on Phase 5 features.
6. Save the best benchmark artifact and summary reports.

## India branch

### Data and context preparation

1. Download or merge TRAI state/provider context.
2. Profile the India datasets.
3. Build the India model dataset with engineered features.

### Raw-sample modeling and explainability

4. Train regression models.
5. Train multi-class latency classifier if needed.
6. Train binary high-latency classifier.
7. Explain the India regression model with SHAP.

### Anomaly layer and case study

8. Run anomaly detection using residuals and classifier outputs.
9. Generate Karnataka-specific analysis and anomaly visualizations.

### Zone-risk branch

10. Build the zone-risk dataset.
11. Train and compare zone-risk classifiers.
12. Tune CatBoost if desired.
13. Explain the final zone-risk classifier with SHAP.
14. Summarize state-wise and Karnataka findings.

### Dashboard delivery

15. Verify that all required CSV, TXT, PKL, and GeoJSON artifacts exist.
16. Launch the Streamlit app.

## Artifact Contract a Rebuilder Must Preserve

To reproduce the system successfully, a developer must preserve more than the model type. The following contracts matter.

### 1. Feature ordering

Saved model payloads assume a fixed feature order. Any rebuild must save the feature list and use it during inference or dashboard scoring.

### 2. Transform metadata

Any model trained on log-transformed targets must store the shift amount and inverse-transform logic.

### 3. Train/test consistency

Comparison across models only remains valid if the same split is used within a phase or experiment family.

### 4. Zone definition policy

Zone rounding precision and minimum support thresholds directly affect the zone-risk dataset. Rebuilds must keep those design choices consistent if they want comparable results.

### 5. Report-text parsing expectations

The dashboard reads values from text reports using label-based extraction. If those report labels change, the dashboard parsing logic must also change.

## Architecture Choices Worth Preserving

### Offline-first analytics

Training and heavy data processing are script-based and offline. The dashboard only reads saved artifacts.

### Explicit file outputs

Every important phase writes outputs that later phases can consume. This makes the system easier to debug and easier to hand off.

### Problem reframing instead of forced regression

One of the most important architectural decisions in the project is to treat weak raw-sample India regression as a signal to change the predictive task. A faithful reconstruction should preserve that reasoning rather than trying to force exact regression to be the final result.

### Explainability integrated into the pipeline

SHAP exports are part of the official outputs, not ad-hoc analysis files. This is central to the project’s identity as an explainable ML system.

## Common Failure Modes When Rebuilding

### Missing artifacts for the dashboard

If the CSV, TXT, PKL, or GeoJSON files expected by `app.py` do not exist, the dashboard cannot start correctly.

### Feature mismatch during inference

If a prediction script rebuilds features differently from the training pipeline, probabilities or predictions will be wrong even if the model file loads successfully.

### Incorrect inverse transformation

Any model trained on transformed targets will report incorrect predictions if the inverse transform or shift value is not preserved.

### Overclaiming the wrong model

A rebuild should preserve the same narrative boundaries as the original repository: the benchmark branch is strong for regression, while the India branch is strongest as a classification-and-anomaly workflow.

## What a New Developer Should Read First

If a developer has no access to the original code, the shortest path to understanding is:

1. Read `00_system_overview.md`.
2. Read `05_india_pipeline_data_and_modeling.md` and `07_india_zone_risk_pipeline.md`.
3. Read `01_root_dashboard_and_utilities.md` to understand how the outputs are consumed.
4. Use the benchmark documents only after the main India-first architecture is clear.