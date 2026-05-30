# Root Dashboard and Utility Files

## `app.py`

### What was done

This file implements the main Streamlit dashboard used to present the India-first analytical outputs together with a small amount of benchmark reference context. It loads precomputed CSV files, text reports, GeoJSON boundaries, and a serialized zone-risk classifier, then builds a multi-tab interface with maps, KPI cards, tables, operator views, SHAP charts, and a live scoring form.

### Why it was done

The project needed a user-facing layer so results could be explored without rerunning model-training code. This file exists to turn analytical artifacts into a practical review tool for demo, report, and stakeholder use. It is also the main integration point that shows how the zone-risk classifier, state summaries, anomaly logic, and operator context fit together.

### Major dependencies

- `streamlit` for the web interface
- `plotly.express`, `plotly.graph_objects`, and `plotly.io` for visualisations
- `pandas` and `numpy` for dataframe manipulation and numeric feature preparation
- `joblib` for loading the saved model payload
- `json`, `html`, `re`, and `pathlib` for asset loading and formatting

### Data and file dependencies

The file expects many precomputed artifacts to exist before the app runs. Key required inputs include:

- India state GeoJSON from `assets/india_states.geojson`
- zone dataset and state summary CSVs from `09_INDIA_FIRST_ANALYSIS/03_outputs/`
- detailed prediction outputs and Karnataka extracts from the same output folder
- SHAP outputs for the zone-risk classifier
- TRAI operator summary CSVs
- benchmark phase-5 results and report text
- foreign reference anomaly outputs
- the serialized model payload `india_best_zone_risk_model.pkl`

The function `ensure_files_exist()` performs a hard check at startup and stops the app immediately if any required artifact is missing.

### Important functions and what they do

#### Asset loading and parsing

- `load_csv(path)` loads CSVs with Streamlit caching.
- `load_text(path)` loads report text.
- `load_geojson(path)` loads the map boundary file.
- `load_model_payload()` loads the saved zone-risk model payload.

These functions are cached to reduce repeated disk reads during interaction.

#### Report metric extraction helpers

- `extract_metric()` parses text reports using label names.
- `extract_float()` and `extract_int()` convert text report values into numeric types.
- `parse_phase9_metrics()`, `parse_phase5_metrics()`, and `parse_foreign_anomaly_metrics()` convert report text into structured dictionaries used by the UI.

This is a design choice worth noting: the dashboard does not only load CSVs; it also mines summary text files for KPI-style values.

#### State and context preparation

- `decode_state(df)` recovers state names from one-hot encoded columns.
- `normalize_state_name(name)` makes map and report state naming more consistent.
- `prepare_zone_data()`, `prepare_state_map_data()`, `prepare_state_context()`, and `prepare_operator_context()` transform raw dashboard inputs into chart-ready or scoring-ready structures.

These helpers bridge the gap between model-oriented artifact layout and UI-oriented display logic.

#### Chart builders

The file contains many pure chart-builder functions such as:

- `build_state_rank_chart()`
- `build_india_state_map()`
- `build_state_scatter()`
- `build_zone_geo_map()`
- `build_shap_feature_chart()`
- `build_shap_family_chart()`
- `build_probability_gauge()`
- `build_operator_speed_chart()`
- `build_operator_share_chart()`
- `build_global_reference_map()`
- `build_phase5_benchmark_chart()`
- `build_foreign_region_chart()`
- `build_foreign_feature_chart()`

The purpose of these functions is to keep rendering logic modular and reusable across tabs.

#### Live scoring logic

The live scoring flow is one of the most important features in the app.

- `build_template_choices()` selects example zones from low, medium, and high-risk parts of a state.
- `apply_easy_adjustments()` lets the user change network strength, traffic load, crowding, and stability in simplified language. Under the hood it rescales underlying numeric features such as download, upload, test counts, devices, and variability measures.
- `apply_scenario()` applies larger preset scenarios such as congestion shock, capacity upgrade, or demand spike.
- `build_feature_row()` reconstructs the full model feature vector from a simplified form input. It calculates derived ratios, squared geography terms, throughput sums and gaps, density proxies, usage pressure, log transforms, state-context ratios, and one-hot state indicators.
- `score_zone()` calls `predict_proba()` on the loaded classifier to obtain the high-risk probability and returns both the probability and the reconstructed feature frame.

This is a critical architecture choice: the app does not ask the user to enter every raw model feature. Instead, it derives the full model-compatible feature row from a smaller set of human-editable values plus state context.

#### Render functions

The UI is broken into high-level tab renderers:

- `render_overview_tab()` for the national summary
- `render_state_explorer_tab()` for state and operator exploration
- `render_karnataka_tab()` for the Karnataka case study
- `render_live_scorer_tab()` for manual scoring
- `render_presentation_tab()` for compact presentation views
- `render_global_reference_tab()` for foreign benchmark context
- `render_explainability_tab()` for SHAP interpretation

The top-level `main()` function loads all assets, prepares context data, builds the sidebar, and mounts these tabs.

### Step-by-step logic flow

1. Validate that all required artifact files exist.
2. Inject custom CSS for the visual design.
3. Load all CSV, text, GeoJSON, and model files.
4. Prepare state-level, operator-level, and zone-level derivative tables.
5. Parse report text into top-level metrics.
6. Build sidebar navigation notes.
7. Render hero header.
8. Create tabs and dispatch to tab renderers.
9. Within the live scorer, convert simplified user inputs into a full feature vector and score the zone.

### Design decisions and architecture reasoning

- File-based artifact loading keeps the dashboard decoupled from training.
- Cached loaders reduce repeated I/O.
- Feature reconstruction in `build_feature_row()` ensures the live scorer uses exactly the engineered schema expected by the saved model.
- Text reports are reused as lightweight structured data sources rather than duplicating constants in the app.
- The tab structure mirrors the storytelling flow used in presentations: overview, India, Karnataka, live scoring, benchmark context, explainability.

### Edge cases and error handling

- Missing artifacts cause immediate termination via `st.stop()` after a user-visible error message.
- Ratio features use `max(denominator, 1e-6)` to avoid divide-by-zero.
- Template choice logic handles empty ranked data by returning an empty dictionary.
- State normalization reduces mismatches between map names and dataset names.

### What a developer needs to know to rebuild it

To recreate this file, the most important requirement is not the UI code itself but the artifact contract. The developer must reproduce the expected output CSVs, report texts, and the model payload with the same feature ordering. Without that contract, the dashboard cannot function because the live scorer depends on exact feature alignment.

## `cleanup_comments.py`

### What was done

This file implements a small maintenance utility that removes low-value comments from Python scripts while keeping module docstrings and meaningful annotations.

### Why it was done

It appears to exist to clean generated or overly verbose scripts before handoff, making the codebase easier to read without manually editing every file.

### Major dependencies

- `pathlib`
- `re`
- built-in file I/O

### Core logic

The main function is `cleanup_comments(file_path)`.

It reads the file, splits it into lines, and then applies simple filtering rules:

1. Keep module docstrings near the top of the file.
2. Remove section-divider comments made of repeated `=` signs.
3. Remove “obvious” procedural comments that simply restate the next line of code, such as comments beginning with `# Create`, `# Load`, `# Train`, `# Save`, and similar phrases.
4. Preserve lines containing `print(`.
5. Preserve non-comment code lines as-is.
6. For lines that contain both code and a comment, remove the comment if it is short and not marked as `TODO`, `FIXME`, or `NOTE`.
7. Keep longer standalone comments.

The cleaned file is written back in place.

### Design decisions

- The script prefers heuristic cleaning over syntax-aware parsing.
- It intentionally preserves docstrings and developer markers like `TODO`.
- It modifies files in place, so it is best used on a version-controlled repository.

### Edge cases

- Because the logic is line-based rather than AST-based, very unusual comment formatting could be handled imperfectly.
- The return value is only an approximate removed-line count rather than a formal diff summary.

## `organize_project.py`

### What was done

This file is a one-off project organization script used to archive older folders, create clean handoff directories, copy final models and documentation into those directories, and generate a handoff README.

### Why it was done

The repository contains multiple phases and experimental outputs. A cleanup-and-handoff step was needed to package the project for teammates and final delivery without asking them to manually inspect every historical folder.

### Major dependencies

- `shutil`
- `pathlib`
- built-in file operations

### Technical flow

This script is written as top-level imperative logic instead of reusable functions.

1. Define which folders are essential and which can be archived.
2. Move obsolete directories such as older outputs into archive locations.
3. Create final handoff directories for final models, Person 3 SHAP inputs, Person 4 anomaly inputs, and documentation.
4. Copy the best-performing model artifacts into the final handoff structure.
5. Copy selected documentation and summary files.
6. Generate a README explaining the final folder structure and how to load the model.

### Important implementation details

- The script assumes specific file names for the best model artifacts, such as the ensemble and CatBoost variants.
- It creates subfolders in `FINAL_HANDOFF/` to separate simplified deliverables by consumer.
- It encodes the model hierarchy directly in filenames, for example using labels like `BEST_MODEL_81.56_ensemble.pkl`.

### Design reasoning

- The script is opinionated and handoff-focused rather than general-purpose.
- It makes the final-state project easier for teammates to consume by flattening the most important artifacts into a predictable folder structure.

### Edge cases and caveats

- Because this script performs file moves and copies, it should not be run carelessly in a dirty workspace.
- It assumes the expected outputs already exist; missing files simply result in skipped copy operations.
- There is no rollback logic.