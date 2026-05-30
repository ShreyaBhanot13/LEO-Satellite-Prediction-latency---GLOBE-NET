# India Zone-Risk Pipeline (`09_INDIA_FIRST_ANALYSIS/02_scripts/` Part 3)

## Purpose of This Subsystem

This subsystem builds the final India-first predictive framing: zone-level high-risk classification. It aggregates raw samples into geographic zones, engineers zone features, trains several classifiers, tunes CatBoost, explains the winning model with SHAP, and produces state and Karnataka summaries that power the dashboard.

## `07_build_zone_risk_dataset.py`

### What was done

This script aggregates India records into zones and creates the feature matrix for zone-risk modeling.

### Why it was done

Raw-sample regression was not strong enough. Aggregating to the zone level reduces noise and reframes the problem around identifying risky areas instead of predicting exact latency for every row.

### Important functions

- `load_data()` loads the underlying India dataset.
- `load_trai_master()` loads the optional provider context.
- `parse_args()` handles CLI flags such as TRAI-context inclusion.
- `to_feature_key()` standardizes feature naming.
- `summarize_operator_metric()` builds operator summary stats.
- `build_operator_share_statistics()` creates provider share metrics.
- `add_record_features()` adds per-record features before aggregation.
- `aggregate_zones()` groups records into geographic zones.
- `build_trai_state_context()` prepares state-level telecom context for merging.
- `add_zone_features()` engineers zone-level summary features.
- `encode_features()` creates model-ready encodings.
- `build_support_summary()` describes zone support distribution.
- `write_outputs()` saves the zone dataset and report.
- `main()` orchestrates the build.

### Step-by-step flow

1. Load the source India records.
2. Optionally load merged TRAI context.
3. Add record-level helper features.
4. Group by rounded geographic bins to define zones.
5. Compute zone-level aggregations such as means, medians, upper-tail latency, variability, sample counts, and activity measures.
6. Filter out low-support zones below the minimum sample threshold.
7. Add zone-level engineered features, including state-relative context ratios.
8. Optionally merge state-level TRAI context.
9. Encode categorical features.
10. Write the final zone dataset and a support-summary report.

### Design decisions

- A minimum sample threshold improves zone-label reliability.
- Zone features emphasize both absolute performance and performance relative to state context.
- The target-like latency fields can be retained for label construction while being excluded from model features.

### Edge cases

- Sparse zones can create noisy labels and are filtered out.
- Geographic rounding precision materially changes the number and size of zones.

## `08_train_zone_risk_models.py`

### What was done

This script trains multiple classifiers to predict whether a zone is high risk.

### Why it was done

This is the project’s strongest India-first predictive problem formulation. It is more aligned with operational needs than exact regression.

### Important functions

- `parse_args()` parses dataset path and risk-quantile settings.
- `load_dataset()` reads the zone dataset and target source.
- `split_data()` creates train/test splits.
- `to_risk_target()` converts a latency-derived source into a binary risk label.
- `get_models()` returns Random Forest, Extra Trees, XGBoost, and CatBoost candidates.
- `evaluate_model()` computes classification metrics.
- `evaluate_quantile()` tests one risk-threshold setting.
- `write_outputs()` saves result files, payloads, and confusion matrices.
- `main()` orchestrates the phase.

### Technical flow

1. Load the zone dataset.
2. Split data into train and test.
3. For one or more quantile thresholds, convert the source latency measure into a binary risk label.
4. Train multiple classifiers.
5. Evaluate each classifier with accuracy, balanced accuracy, macro F1, high-risk precision, recall, and F1.
6. Compare model/threshold combinations.
7. Select the best configuration.
8. Save the winning payload and detailed outputs.

### Design decisions

- Multiple quantile thresholds are tested because the business meaning of “high risk” is configurable.
- Balanced or imbalance-aware settings are used because the positive class is not dominant.
- The file keeps metric reporting richer than raw accuracy so the model is evaluated fairly.

### Why this file matters

This script produces the final zone-risk model consumed by the dashboard.

## `08a_tune_catboost_zone_risk.py`

### What was done

This script performs a focused hyperparameter search for CatBoost on the zone-risk task.

### Why it was done

Once CatBoost emerged as a strong candidate, a dedicated tuning pass became worthwhile.

### Important functions

- `load_dataset()` loads train/test-ready zone inputs.
- `evaluate_params()` iterates over the tuning grid and records metrics.
- `main()` runs the tuning sweep.

### Design reasoning

- Targeted tuning is cheaper and easier to reason about than repeating a full search across all model families.
- High-risk F1 and balanced accuracy are prioritized because the positive class matters operationally.

## `09_explain_zone_risk_model.py`

### What was done

This script computes SHAP explanations for the winning zone-risk classifier.

### Why it was done

The final model needs to be interpretable enough for reporting, stakeholder communication, and dashboard integration.

### Important functions

- `load_artifacts()` loads the saved classifier and test data.
- `evaluate()` recomputes validation metrics for consistency.
- `get_feature_family()` groups feature names into broader categories.
- `decode_state(row)` infers state identity from encoded columns.
- `run_shap()` computes global, family-level, and local explanations.
- `write_outputs()` persists SHAP CSVs and a report.
- `main()` orchestrates the phase.

### Technical flow

1. Load the saved zone-risk payload.
2. Confirm evaluation metrics on the held-out test set.
3. Sample the test data for manageable SHAP computation.
4. Compute SHAP values.
5. Build global rankings.
6. Aggregate importance by feature family.
7. Extract a representative local explanation for a high-risk sample.
8. Save outputs for the dashboard and report.

### Design decisions

- Sampling is necessary because SHAP on large tree ensembles can be expensive.
- Family-level grouping supports easier storytelling in the report and dashboard.

## `10_generate_india_anomaly_charts.py`

### What was done

This script creates presentation-ready anomaly visualizations such as residual distributions, actual-vs-predicted scatter plots, and top-state charts.

### Why it was done

The anomaly logic is more convincing when it is visualized. This file turns dense analytical outputs into communication artifacts.

### Important functions

- `parse_args()`
- `load_inputs()`
- `apply_chart_style()`
- `plot_residual_distribution()`
- `plot_actual_vs_predicted()`
- `plot_top_states()`
- `main()`

### Developer note

This file depends entirely on prior anomaly outputs. It does not perform detection itself.

## `10_summarize_zone_risk_findings.py`

### What was done

This script creates the final state-level and Karnataka-level summaries for the zone-risk classifier.

### Why it was done

The dashboard and report require per-state rates, detailed predictions, and Karnataka extracts rather than only raw test-set predictions.

### Important functions

- `load_artifacts()` loads the dataset, saved payload, and test data.
- `decode_state_from_features()` reconstructs readable state labels.
- `build_prediction_frame()` adds probabilities, predictions, and correctness indicators.
- `build_state_summary()` aggregates performance and risk rates by state.
- `build_karnataka_outputs()` extracts Karnataka-specific outputs.
- `write_outputs()` saves state summary CSVs, detailed prediction CSVs, Karnataka files, and the final report.
- `main()` orchestrates the phase.

### Step-by-step flow

1. Load the saved classifier and test matrices.
2. Score the test zones.
3. Decode state identity.
4. Build a detailed prediction frame.
5. Aggregate per-state metrics.
6. Extract Karnataka-specific subsets.
7. Save all summary outputs.

### Why it matters

This file directly produces the tables and maps that the dashboard consumes.