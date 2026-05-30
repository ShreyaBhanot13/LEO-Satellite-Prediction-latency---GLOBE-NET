# India Pipeline: Explainability, Anomalies, and Karnataka Analysis (`09_INDIA_FIRST_ANALYSIS/02_scripts/` Part 2)

## `04_explain_india_model.py`

### What was done

This script computes SHAP explanations for the India regression model and exports global feature importance, feature-family summaries, and a representative local explanation.

### Why it was done

Even though the India regression model is not the strongest predictive artifact, it still reveals which feature families the model depends on. That helps the team understand the data and justify the later transition toward context-aware classification.

### Important functions

- `load_artifacts()` loads the saved regression payload and test data.
- `inverse_predict()` reconstructs predictions on the original scale.
- `evaluate()` computes the model’s validation metrics.
- `get_feature_family()` maps raw feature names into broader categories such as context, throughput, geography, usage, and state.
- `run_shap()` runs SHAP on a capped test sample and produces ranking tables.
- `write_outputs()` saves CSV outputs and a text report.
- `main()` orchestrates the workflow.

### Technical flow

1. Load the saved best regression model and its shift metadata.
2. Recompute evaluation metrics to confirm the payload matches the expected result.
3. Sample the test set for computationally manageable SHAP analysis.
4. Run the SHAP explainer.
5. Aggregate mean absolute SHAP values globally.
6. Group them into feature families.
7. Extract a representative local explanation.
8. Write outputs to CSV and report files.

### Design decisions

- SHAP is capped to a manageable sample size for speed.
- Feature-family grouping is used because raw feature lists can be too granular for report writing.

### Caveat

SHAP explains model behavior, not causal truth.

## `05_detect_india_anomalies.py`

### What was done

This script implements the India anomaly-detection pipeline by combining regression residuals with the high-latency classifier.

### Why it was done

Average or predicted latency alone is not enough for operational prioritization. The project needs a way to identify places that behave worse than expected relative to the modeled baseline and are also flagged as risky by the classifier.

### Important functions

- `load_artifacts()` loads the regression payload, classifier payload, and test data.
- `inverse_predict()` converts regression predictions back to the original scale.
- `classifier_scores()` computes class predictions and probabilities from the classifier.
- `decode_state()` reconstructs state labels from one-hot columns.
- `build_anomaly_frame()` combines actual values, predictions, residuals, classifier outputs, and anomaly flags into one dataframe.
- `build_state_summary()` aggregates anomaly metrics by state.
- `write_outputs()` saves detailed outputs and summary artifacts.
- `main()` orchestrates the anomaly phase.

### Step-by-step logic

1. Load the regression model, classifier model, and held-out test features.
2. Generate inverse-transformed regression predictions.
3. Compute residuals as `actual - predicted`.
4. Generate classifier probabilities and labels.
5. Decode the state for each row.
6. Apply residual thresholds such as P95 and P99 to identify underperformance and severe underperformance.
7. Combine residual flags with classifier risk flags to form dual-signal anomalies and critical anomalies.
8. Build a detailed anomaly dataframe.
9. Aggregate state-level anomaly summaries.
10. Save detailed results, priority tables, and text summaries.

### Why this file matters

This is the operational core of the anomaly workflow. It converts raw predictive outputs into prioritised incident-like artifacts that can be acted on.

### Design decisions

- Dual-signal logic is more defensible than using only a residual threshold or only a classifier threshold.
- State decoding is built into the pipeline so that anomaly outputs can be grouped geographically without separately joining metadata later.

### Edge cases

- Feature alignment between saved classifier payload and test matrix must be preserved.
- Residual thresholds depend on the held-out distribution and should be regenerated if the model or test split changes.

## `06_analyze_karnataka_findings.py`

### What was done

This script extracts Karnataka-specific findings from the broader India anomaly outputs and prepares a focused case-study report.

### Why it was done

The project needed one concrete state-level narrative that could be discussed in depth. Karnataka had sufficient data and contextual relevance for that role.

### Important functions

- `load_inputs()` loads state summary, anomaly detail, and phase reports.
- `add_rank_columns()` adds comparative rankings across states.
- `summarize_karnataka()` computes Karnataka’s position relative to the national distribution.
- `extract_karnataka_cases()` filters anomaly records for Karnataka and ranks them.
- `summarize_case_mix()` breaks down the case types and severity.
- `phase5_results_and_insights_text()` reuses prior narrative context.
- `build_phase6_report()` writes the case-study report.
- `write_outputs()` saves Karnataka-specific tables.
- `main()` orchestrates the phase.

### Technical flow

1. Load national anomaly outputs.
2. Add rank columns for state comparison.
3. Isolate Karnataka rows.
4. Summarize Karnataka rates, means, and ranks.
5. Extract Karnataka anomaly cases.
6. Build top-case and full-case outputs.
7. Write a Karnataka-focused report that places the state in national context.

### Design reasoning

- The case study is comparative, not standalone.
- Karnataka is intentionally presented as meaningful but not the worst case.

### Caveat

The script’s provider-related conclusions are limited by the available TRAI extract.