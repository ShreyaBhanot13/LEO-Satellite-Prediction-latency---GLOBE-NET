# Person 4 Folder Comparison

This note compares the original folder:

- `C:\Users\250019004\Downloads\Anomaly_detection`

against the updated workspace folder:

- `C:\Users\250019004\FY_ML\PERSON4_UPDATED_ANOMALY_FOLDER`

## 1. Folder Structure

### Original folder structure
- `Foreign dataset Anomaly/`
- `Indian Dataset Anomaly/`

### Updated folder structure
- `Foreign dataset Anomaly/`
- `Indian Dataset Anomaly/`

### Meaning of this change
- The updated workspace copy now preserves the same top-level folder structure as the original download.
- This makes it easier to compare old vs new without changing how the teammate navigates the files.
- The content inside the folders was corrected and reorganized, but the outer structure was kept the same.

## 2. File Renames / Replacements

### India chart and file name cleanup
- `person4_india_actual_vs_predicted_risk.png` -> `india_actual_vs_predicted_latency.png`
- `person4_india_residual_distribution.png` -> `india_residual_distribution.png`
- `person4_india_top_states_risk_rate.png` -> `india_top_states_dual_signal_rate.png`
- `person4_india_priority_anomalies.csv` -> `india_priority_anomalies.csv`
- `person4_india_residual_anomaly_flags.csv` -> `india_test_predictions_with_anomaly_flags.csv`
- `person4_india_state_risk_summary.csv` -> `india_state_anomaly_summary.csv`

### Report replacement
- `person4_india_anomaly_summary_report.txt` was replaced by the official project report:
  - `phase5_india_anomaly_detection.txt`

### New supporting files added in updated folder
- `05_detect_india_anomalies.py`
- `india_anomaly_detection_results.pkl`
- `india_state_anomaly_summary_ranked.csv`
- `karnataka_all_anomaly_cases.csv`
- `karnataka_priority_anomalies.csv`
- `phase10_zone_risk_state_and_karnataka_summary.txt`
- `README_PERSON4_ANOMALY.txt`

### Foreign folder file name cleanup
- `person4_actual_vs_predicted.png` -> `foreign_reference_actual_vs_predicted_latency.png`
- `person4_anomaly_detection_results.csv` -> `foreign_reference_anomaly_results.csv`
- `person4_anomaly_feature_importance.csv` -> `foreign_reference_anomaly_feature_importance.csv`
- `person4_parameter_impact_analysis.csv` -> `foreign_reference_parameter_impact.csv`
- `person4_residual_distribution.png` -> `foreign_reference_residual_distribution.png`
- `person4_residuals_over_samples.png` -> `foreign_reference_residuals_over_samples.png`
- `person4_summary_report.txt` -> `foreign_reference_anomaly_summary.txt`
- `person4_top_anomaly_parameters.png` -> `foreign_reference_top_anomaly_parameters.png`
- `person4_top_high_risk_samples.csv` -> `foreign_reference_top_high_risk_samples.csv`

### Meaning of foreign folder change
- The foreign folder is still present, but it is now explicitly labeled as reference material.
- This keeps the original folder layout while reducing confusion between the final India workflow and the older foreign benchmark work.

## 3. Report Content Changes

### Old report problem
The original summary report described the anomaly logic mostly in residual-only terms and labeled these as final risk outputs:

- `High-Risk Cases = 5626`
- `Critical-Risk Cases = 1126`
- ranking title: `Top States by High-Risk Rate`

This was misleading because those counts are residual-threshold counts, not the final anomaly counts used by the official project.

### New report logic
The updated folder uses the official project report `phase5_india_anomaly_detection.txt`, which explicitly defines:

- Residual underperformance: `residual >= P95`
- Severe residual: `residual >= P99`
- Dual-signal anomaly: `residual underperformance + classifier high-risk`
- Critical anomaly: `severe residual underperformance + classifier high-risk`

### Exact metric change in reporting
- Old report emphasized:
  - `5626` as high-risk cases
  - `1126` as critical-risk cases

- New official report states:
  - Residual underperforming count: `5626`
  - Severe residual count: `1126`
  - Classifier high-risk count: `32021`
  - Dual-signal anomaly count: `3136`
  - Critical anomaly count: `663`

### Ranking change in report
- Old wording: `Top States by High-Risk Rate`
- New wording: `Top states by dual-signal anomaly rate`

This is the most important conceptual correction.

## 4. State Summary CSV Changes

### Row count
- Old: `36` rows
- New: `36` rows

### Old columns
- `state`
- `samples`
- `actual_latency_mean_ms`
- `predicted_latency_mean_ms`
- `residual_mean_ms`
- `residual_median_ms`
- `high_risk_count`
- `critical_risk_count`
- `high_risk_rate`
- `critical_risk_rate`

### New columns
- `state`
- `samples`
- `actual_latency_mean_ms`
- `predicted_latency_mean_ms`
- `residual_mean_ms`
- `residual_median_ms`
- `residual_underperforming_count`
- `residual_severe_count`
- `classifier_high_risk_count`
- `dual_signal_count`
- `high_latency_probability_mean`
- `critical_count`
- `residual_underperforming_rate`
- `classifier_high_risk_rate`
- `dual_signal_rate`
- `critical_rate`

### Columns removed from old file
- `high_risk_count`
- `critical_risk_count`
- `high_risk_rate`
- `critical_risk_rate`

### Columns added in new file
- `residual_underperforming_count`
- `residual_severe_count`
- `classifier_high_risk_count`
- `dual_signal_count`
- `high_latency_probability_mean`
- `critical_count`
- `residual_underperforming_rate`
- `classifier_high_risk_rate`
- `dual_signal_rate`
- `critical_rate`

### Meaning of this change
- The old state summary mixed residual-based counts with final risk naming.
- The new state summary separates residual counts, classifier counts, and final dual-signal anomaly counts clearly.

## 5. Priority Anomaly CSV Changes

### Row count
- Old: `5626` rows
- New: `34511` rows

### Old extra columns removed in new file
- `residual_underperformance`
- `severe_underperformance`
- `better_than_expected`
- `interference_congestion_risk`
- `risk_level`

### Meaning of this change
- The updated file keeps the official anomaly output schema only.
- The old file had extra convenience/alias columns layered on top of the official fields.
- The updated file also contains a much wider set of flagged cases because it reflects all non-normal priority levels from the official pipeline, not just the smaller residual-focused subset.

## 6. Full Anomaly Flags CSV Changes

### Row count
- Old: `112506` rows
- New: `112506` rows

### Old extra columns removed in new file
- `residual_underperformance`
- `severe_underperformance`
- `better_than_expected`
- `interference_congestion_risk`
- `risk_level`

### Meaning of this change
- The updated full anomaly file preserves the same test-set coverage.
- It removes duplicate helper labels and keeps the official project fields only.

## 7. Chart Changes

### What changed
- The India PNGs were regenerated from the official project outputs using:
  - `09_INDIA_FIRST_ANALYSIS/02_scripts/10_generate_india_anomaly_charts.py`

### Why this matters
- The original chart names and framing used generic or residual-only wording.
- The updated charts now align with the official project story, especially:
  - `india_top_states_dual_signal_rate.png`
  - `india_actual_vs_predicted_latency.png`
  - `india_residual_distribution.png`

## 8. Foreign Folder Difference

### Original folder contained
- `Foreign dataset Anomaly/` with old benchmark/reference outputs

### Updated folder contains
- `Foreign dataset Anomaly/` is still present
- The files inside it were renamed to make their reference-only role explicit

### Meaning of this change
- The updated Person 4 folder now keeps the same original structure while making the distinction clear:
  - `Indian Dataset Anomaly/` = final project anomaly workflow
  - `Foreign dataset Anomaly/` = legacy benchmark/reference material

## 9. Bottom-Line Summary For Teammate

You can send this summary:

1. The updated Person 4 folder keeps the same original two-folder structure, so the teammate can navigate it exactly like the old version.
2. The biggest correction was conceptual: the old summary treated residual-threshold counts as final anomaly counts.
3. The new folder uses the official dual-signal anomaly logic and official report counts:
   - residual underperforming = `5626`
   - severe residual = `1126`
   - classifier high-risk = `32021`
   - dual-signal anomalies = `3136`
   - critical anomalies = `663`
4. The state summary CSV was expanded so residual, classifier, and dual-signal metrics are separated clearly.
5. The full anomaly CSV kept the same number of rows, but extra helper columns were removed to keep only the official schema.
6. The priority anomaly CSV now reflects the official non-normal priority output rather than a narrower residual-only subset.
7. The India charts were renamed and regenerated to match the official project narrative.
8. The foreign files were kept in place but renamed as `foreign_reference_*` so they are clearly treated as benchmark/reference material.