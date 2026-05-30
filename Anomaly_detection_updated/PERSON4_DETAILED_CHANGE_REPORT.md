# Person 4 Detailed Change Report

This document explains exactly what was changed between the original Person 4 anomaly folder and the updated version in the workspace, so the changes can be reproduced manually.

## 1. Original vs Updated Paths

Original untouched folder:

- `C:\Users\250019004\Downloads\Anomaly_detection`

Updated workspace copy:

- `C:\Users\250019004\FY_ML\PERSON4_UPDATED_ANOMALY_FOLDER`

Important note:

- The original `Anomaly_detection` folder was **not modified**.
- All corrections were made in separate working folders and then copied into the workspace copy.

## 2. Folder Structure

The updated folder intentionally keeps the same top-level structure as the original:

- `Foreign dataset Anomaly/`
- `Indian Dataset Anomaly/`

This means the teammate can navigate the updated folder the same way as the original one.

## 3. Main Conceptual Correction

The biggest issue in the original Person 4 India files was **not code syntax**. It was **logic framing and reporting**.

### Original problem

The original India summary treated residual-threshold counts as if they were the final anomaly counts.

In the original report:

- `High-Risk Cases = 5626`
- `Critical-Risk Cases = 1126`
- top-state ranking was labeled as `High-Risk Rate`

This was misleading because those counts correspond to residual thresholds only.

### Correct project logic

The official project uses a **dual-signal anomaly method**:

1. Residual underperformance: `residual >= P95`
2. Severe residual: `residual >= P99`
3. Classifier high-risk: predicted high-latency class
4. Final anomaly: residual underperformance **and** classifier high-risk
5. Critical anomaly: severe residual **and** classifier high-risk

### Correct final metrics

The updated folder now aligns to the official project metrics:

- Residual underperforming count: `5626`
- Severe residual count: `1126`
- Classifier high-risk count: `32021`
- Dual-signal anomaly count: `3136`
- Critical anomaly count: `663`

## 4. India Folder Changes

## 4.1 File renames

Original -> Updated

- `person4_india_actual_vs_predicted_risk.png` -> `india_actual_vs_predicted_latency.png`
- `person4_india_residual_distribution.png` -> `india_residual_distribution.png`
- `person4_india_top_states_risk_rate.png` -> `india_top_states_dual_signal_rate.png`
- `person4_india_priority_anomalies.csv` -> `india_priority_anomalies.csv`
- `person4_india_residual_anomaly_flags.csv` -> `india_test_predictions_with_anomaly_flags.csv`
- `person4_india_state_risk_summary.csv` -> `india_state_anomaly_summary.csv`

## 4.2 Report replacement

Original:

- `person4_india_anomaly_summary_report.txt`

Updated:

- `phase5_india_anomaly_detection.txt`

### What changed in the report

The updated report now states the full official anomaly logic, including:

- regression model name
- classifier model name
- classifier threshold
- residual threshold rules
- dual-signal anomaly rule
- critical anomaly rule
- official counts and official top-state ranking

### Manual change teammate should make

If doing this manually, replace the old report narrative with:

- a Phase 5 anomaly report heading
- the official threshold definitions
- the five official counts listed above
- top states ranked by `dual_signal_rate`, not `high_risk_rate`

## 4.3 State summary CSV change

Original file:

- `person4_india_state_risk_summary.csv`

Updated file:

- `india_state_anomaly_summary.csv`

### Original columns

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

### Updated columns

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

### What this means

The updated summary no longer mixes residual-based counts with final risk naming.
Instead, it separates:

- residual behavior
- classifier behavior
- final dual-signal anomaly behavior

### Manual change teammate should make

If she wants to patch the old CSV logic herself, she should regenerate the state summary from the official anomaly dataframe using these metrics:

- count rows per state
- count rows where `residual_underperforming_p95 = True`
- count rows where `residual_severe_p99 = True`
- count rows where `classifier_high_risk = True`
- count rows where `dual_signal_anomaly = True`
- count rows where `priority_level = critical`
- compute rates by dividing each count by `samples`

## 4.4 Priority anomaly CSV change

Original file:

- `person4_india_priority_anomalies.csv`

Updated file:

- `india_priority_anomalies.csv`

### Row-count change

- old rows: `5626`
- new rows: `34511`

### Why the row count increased

The updated file reflects the official project behavior:

- keep every row where `priority_level != normal`

This includes:

- `critical`
- `high`
- `medium`
- `watchlist`

The original file was effectively closer to a residual-focused subset.

### Old extra columns removed

- `residual_underperformance`
- `severe_underperformance`
- `better_than_expected`
- `interference_congestion_risk`
- `risk_level`

### Manual change teammate should make

If manually reproducing:

1. Start from the full anomaly dataframe.
2. Filter rows where `priority_level != normal`.
3. Sort by:
   - `priority_score` descending
   - `residual_ms` descending
   - `high_latency_probability` descending
4. Keep the official columns only.

## 4.5 Full anomaly flags CSV change

Original file:

- `person4_india_residual_anomaly_flags.csv`

Updated file:

- `india_test_predictions_with_anomaly_flags.csv`

### Row-count change

- old rows: `112506`
- new rows: `112506`

So coverage of the test set stayed the same.

### What changed

The updated version removed helper/alias columns that were not part of the official project output schema:

- `residual_underperformance`
- `severe_underperformance`
- `better_than_expected`
- `interference_congestion_risk`
- `risk_level`

The official fields already cover the logic:

- `residual_underperforming_p95`
- `residual_severe_p99`
- `better_than_expected_p01`
- `classifier_high_risk`
- `dual_signal_anomaly`
- `priority_score`
- `priority_level`

### Manual change teammate should make

Keep the full anomaly CSV, but drop the redundant helper columns and retain only the official ones.

## 4.6 New added India files

These did not exist in the original folder and were added to make the handoff complete:

- `05_detect_india_anomalies.py`
- `india_anomaly_detection_results.pkl`
- `india_state_anomaly_summary_ranked.csv`
- `karnataka_all_anomaly_cases.csv`
- `karnataka_priority_anomalies.csv`
- `phase10_zone_risk_state_and_karnataka_summary.txt`
- `README_PERSON4_ANOMALY.txt`

### Why these were added

- to include the actual anomaly script
- to include the serialized result artifact
- to include ranked state summary support
- to include Karnataka-focused case-study files
- to include a simple start-here handoff note

## 4.7 Chart changes

The India charts were not only renamed. They were regenerated from official outputs so the chart titles and captions align with the project.

Updated chart files:

- `india_actual_vs_predicted_latency.png`
- `india_residual_distribution.png`
- `india_top_states_dual_signal_rate.png`

### How they were regenerated

Using the new script:

- `09_INDIA_FIRST_ANALYSIS/02_scripts/10_generate_india_anomaly_charts.py`

### What this script does

1. Loads official files:
   - `india_test_predictions_with_anomaly_flags.csv`
   - `india_state_anomaly_summary.csv`
2. Applies a consistent plotting style.
3. Creates:
   - residual distribution with P95, P99, P01 threshold markers
   - actual-vs-predicted scatter with dual-signal and critical anomalies highlighted
   - top-state horizontal bar chart ranked by `dual_signal_rate`
4. Writes the charts to a chosen destination folder.

### Manual command to reproduce

```powershell
C:/Users/250019004/AppData/Local/Programs/Python/Python314/python.exe 09_INDIA_FIRST_ANALYSIS/02_scripts/10_generate_india_anomaly_charts.py --destination "C:\path\to\target\folder"
```

## 5. Foreign Folder Changes

The foreign folder was kept, but explicitly reframed as reference-only material.

## 5.1 File renames

Original -> Updated

- `person4_actual_vs_predicted.png` -> `foreign_reference_actual_vs_predicted_latency.png`
- `person4_anomaly_detection_results.csv` -> `foreign_reference_anomaly_results.csv`
- `person4_anomaly_feature_importance.csv` -> `foreign_reference_anomaly_feature_importance.csv`
- `person4_parameter_impact_analysis.csv` -> `foreign_reference_parameter_impact.csv`
- `person4_residual_distribution.png` -> `foreign_reference_residual_distribution.png`
- `person4_residuals_over_samples.png` -> `foreign_reference_residuals_over_samples.png`
- `person4_summary_report.txt` -> `foreign_reference_anomaly_summary.txt`
- `person4_top_anomaly_parameters.png` -> `foreign_reference_top_anomaly_parameters.png`
- `person4_top_high_risk_samples.csv` -> `foreign_reference_top_high_risk_samples.csv`

## 5.2 Foreign summary text change

Original foreign summary was written as if it was just another anomaly result folder.

Updated foreign summary now explicitly states:

- it is a legacy foreign benchmark
- it is reference-only
- it is not the final India anomaly workflow

### Manual text changes teammate should make

In the foreign summary report:

1. Change the heading to include `REFERENCE ONLY`.
2. Add a short purpose section saying it is background/benchmark material.
3. Keep the original metrics.
4. Add a conclusion saying it should be presented separately from the official India anomaly workflow.

## 6. Handoff / Workspace Packaging Changes

These packaging changes were also made:

### Final handoff folder updated

- `FINAL_HANDOFF/01_INDIA_FINAL_HANDOFF/03_PERSON4_ANOMALY_HANDOFF`

This folder now contains the corrected India charts and updated README.

### Workspace copy created

- `PERSON4_UPDATED_ANOMALY_FOLDER`

This was created so the corrected version can be reused later without touching the original download folder.

### Comparison note added

- `PERSON4_FOLDER_COMPARISON.md`

This contains the shorter comparison summary.

## 7. Exact Manual Reproduction Plan For Teammate

If your teammate wants to reproduce the update herself from the original folder, the cleanest order is:

1. Keep the same outer folder structure:
   - `Foreign dataset Anomaly/`
   - `Indian Dataset Anomaly/`
2. In the India folder:
   - rename the files to the new names listed above
   - replace the old summary report with the official Phase 5 anomaly report
   - replace the old state summary CSV with the official state anomaly summary CSV
   - replace the full anomaly flags CSV with the official full anomaly file
   - replace the priority anomalies CSV with the official priority anomalies CSV
3. Add the supporting India files:
   - anomaly script
   - result pickle
   - ranked state summary
   - Karnataka case-study files
   - README
4. Regenerate the India charts using `10_generate_india_anomaly_charts.py`.
5. In the foreign folder:
   - keep the files
   - rename them as `foreign_reference_*`
   - rewrite the foreign summary to mark it as reference-only

## 8. Bottom Line

The core code/logic change was:

- move from a residual-only presentation to the official dual-signal anomaly logic

The core data change was:

- replace simplified residual-style CSV summaries with the official project outputs

The core presentation change was:

- rename and regenerate charts so their titles and filenames match the final India-first project story

The core packaging change was:

- keep the same folder structure, but make the India folder final-project aligned and the foreign folder explicitly reference-only