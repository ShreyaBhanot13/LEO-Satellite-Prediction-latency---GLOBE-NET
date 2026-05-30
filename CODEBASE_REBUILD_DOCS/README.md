# Codebase Rebuild Documentation Pack

This folder is a self-contained technical handoff for teammates who do not have access to the source code. It explains what each major file and feature in the canonical project codebase does, why it exists, how the logic flows, what outputs it produces, which dependencies it uses, and what design decisions or caveats matter if someone wants to understand or recreate the work.

The documentation focuses on the canonical implementation files in these locations:

- `app.py`
- `cleanup_comments.py`
- `organize_project.py`
- `scripts/`
- `scripts_v2/`
- `scripts_v3/`
- `09_INDIA_FIRST_ANALYSIS/02_scripts/`

It does not treat duplicate copies inside archived handoff folders as separate source-of-truth implementations. If the same logic exists in a handoff copy and a main script folder, the main script folder is treated as authoritative.

Recommended reading order:

1. `00_system_overview.md`
2. `01_root_dashboard_and_utilities.md`
3. `02_phase1_benchmark_pipeline.md`
4. `03_phase2_feature_engineering.md`
5. `04_phase3_to_phase5_optimization.md`
6. `05_india_pipeline_data_and_modeling.md`
7. `06_india_pipeline_explainability_and_anomalies.md`
8. `07_india_zone_risk_pipeline.md`
9. `08_rebuild_guide_and_dependencies.md`

Each section is written so that a developer can understand the project without seeing the original code.