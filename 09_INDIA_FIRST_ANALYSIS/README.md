# India-First Analysis Workspace

This workspace makes India the primary analysis domain for the final project.

## Scope

1. Phase 1: Data understanding and profiling for India datasets.
2. Phase 2: India-native feature design for modeling.
3. Phase 3: India model training and evaluation.
4. Phase 4: SHAP explainability on the India model.
5. Phase 5: Residual-based anomaly detection for Indian regions.
6. Phase 6: Karnataka provider analysis and final reporting.

## Primary datasets

- `outputs_v5/ookla_data_with_states.csv`
- `outputs_v5/ade6e644-91b8-4d27-97ba-e8c42c48f278_4bc4eb37ff16e2b91e3412bf093ee6e5 (1).csv`

## Phase 1 output targets

- Overall India latency summary from original Ookla state data
- State-wise latency ranking
- Karnataka-specific latency summary
- Karnataka TRAI operator summary based on speed and signal

This folder is intentionally separated from the Europe-schema model artifacts so the
India-first pipeline can be implemented without mixing incompatible schemas.

## Final deliverables

- `04_reports/phase5_phase6_final_narrative.md` - report-ready combined narrative for anomaly detection and Karnataka case-study findings.
- `INDIA_FIRST_FINAL_HANDOFF.txt` - consolidated handoff summary of datasets, models, outputs, key metrics, and limitations.
- `04_reports/phase5_results_and_insights.md` - Phase 5 anomaly-detection interpretation.
- `04_reports/phase6_karnataka_case_study.txt` - Karnataka case-study results.
- `04_reports/phase8_india_zone_risk_modeling.txt` - validated zone-level high-risk internet performance classification benchmark.
- `04_reports/phase9_india_zone_risk_shap_explainability.txt` - SHAP interpretation for the final zone-risk classifier.