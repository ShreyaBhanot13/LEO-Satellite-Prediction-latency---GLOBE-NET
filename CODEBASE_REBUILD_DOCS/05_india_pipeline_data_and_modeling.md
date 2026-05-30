# India Pipeline: Data Preparation and Modeling (`09_INDIA_FIRST_ANALYSIS/02_scripts/` Part 1)

## Purpose of This Subsystem

These files build the India-first modeling workflow from raw or merged inputs through regression and classification artifacts. They are the foundation for the project’s operational branch.

## `00_download_trai_2025_api.py`

### What was done

This script downloads 2025 operator-related performance data from the TRAI or data.gov.in API in a paginated way.

### Why it was done

The project needs state/provider context for India analysis, and that context must be collected in a reproducible way rather than by manual CSV handling alone.

### Libraries and dependencies

- `argparse`
- `pandas`
- HTTP request utilities used inside the script
- environment-variable based API key access

### Important functions

- `parse_args()` parses CLI parameters such as operator set, year, and fetch size.
- `fetch_page()` performs one API request and includes retry logic.
- `fetch_operator_data()` iterates through pages for a given operator.
- `operator_file_name()` standardizes output naming.
- `build_summary()` builds a textual or tabular summary of the retrieved frames.
- `main()` orchestrates the full download.

### API usage logic

The script likely calls the external API with operator, year, limit, and offset parameters. It uses pagination so it can fetch large result sets incrementally instead of relying on one oversized request.

### Error handling

- Retries on rate limits or server failures
- bounded retry count
- backoff behavior to reduce repeated API pressure

### Rebuild note

Anyone recreating this file must secure an API key and confirm the endpoint schema, because external APIs change more often than local files.

## `00_merge_state_service_provider.py`

### What was done

This script merges and normalizes state-wise service-provider files into a common master table and summary.

### Why it was done

TRAI or telecom data often uses LSA or circle names rather than clean state labels. The project needs a normalized state-linked table before it can join operator context into later analysis.

### Important functions

- `list_input_files()` finds candidate input CSV files.
- `normalize_operator()` standardizes provider naming.
- `normalize_lsa()` normalizes geographic circle labels.
- `load_file()` reads a single input file.
- `add_merge_keys()` constructs state or merge keys.
- `build_summary()` creates aggregated provider summaries.
- `build_report()` writes a textual merge report.
- `main()` coordinates the process.

### Design reasoning

The script treats normalization as a first-class problem because geographic and operator names are often inconsistent across telecom datasets.

### Edge cases

- unmapped LSAs
- multi-state circles
- metro circles that do not directly match a single state name

## `01_profile_india_datasets.py`

### What was done

This script profiles the main India datasets and writes descriptive reports.

### Why it was done

Before building models, the project needs to understand coverage, per-state variation, Karnataka suitability, and the quality of the available Ookla and TRAI inputs.

### Important functions

- `ensure_directories()` ensures output folders exist.
- `load_dataset()` validates columns and loads a dataset.
- `summarize_series()` computes descriptive statistics.
- `build_state_summary()` creates per-state summaries from Ookla data.
- `build_karnataka_trai_summary()` extracts the Karnataka subset from TRAI context.
- `representative_states()` selects reference states.
- `write_report()` writes the profiling report.
- `main()` runs the phase.

### Step-by-step flow

1. Create required output directories.
2. Load Ookla and TRAI sources.
3. Compute descriptive statistics.
4. Summarize by state.
5. Build a Karnataka-specific summary.
6. Write report files for Phase 1 understanding.

## `02_build_india_model_dataset.py`

### What was done

This script constructs the India model-ready dataset used by the early India regression and classification stages.

### Why it was done

The raw India measurements are not directly suitable for learning. The script adds engineered features that capture usage pressure, throughput relationships, spatial patterns, and state-relative context.

### Important functions

- `load_data()` reads the source dataset.
- `add_features(df)` creates engineered fields.
- `encode_features(df)` converts categorical state information into encoded model features.
- `write_outputs(source_df, model_df)` saves both the processed dataset and supporting documentation.
- `main()` orchestrates the full build.

### Technical details of feature engineering

The script creates multiple feature families.

- ratio features such as tests per device or download/upload relationships
- log transforms for throughput and activity counts
- geographic combinations such as tile interactions and rounded grid bins
- context aggregates such as state averages and cell averages
- relative-position features comparing local values with state or cell baselines
- encoded state indicators for model compatibility

### Step-by-step logic

1. Load source data.
2. Add raw-to-engineered feature transformations.
3. Build contextual aggregates from state or cell groupings.
4. Encode categorical variables, especially state.
5. Remove leakage-prone columns.
6. Save the final model dataset and any derived metadata.

### Design decisions

- The file explicitly avoids target-derived leakage.
- Context features are heavily emphasized because India network performance must be interpreted relative to regional conditions.

### Edge cases

- Safe division is needed for ratio features.
- Sparse cells can distort contextual aggregates if not handled carefully.

## `03_train_india_models.py`

### What was done

This script trains regression models for exact latency prediction on the India feature set.

### Why it was done

The project first needs to test whether direct regression is viable before deciding whether to change the problem framing.

### Important functions

- `load_dataset()` loads features and target.
- `split_data()` creates the 80/20 train/test split.
- `log_transform_target()` applies the shift-plus-log transformation.
- `get_models()` returns the candidate regressors.
- `evaluate_model()` computes inverse-transformed metrics.
- `train_and_compare()` fits all candidate models and ranks them.
- `write_outputs()` saves models, test data, and results.
- `main()` coordinates the training phase.

### Technical behavior

The script log-transforms the target before training and inverse-transforms predictions before computing RMSE, MAE, and $R^2$. Candidate models include Random Forest, XGBoost, and CatBoost regressors.

### Step-by-step flow

1. Load the prepared India dataset.
2. Split into train and test.
3. Compute a positive shift and log-transform the target.
4. Instantiate candidate regressors.
5. Train each model.
6. Predict on the test set.
7. Inverse-transform predictions.
8. Compute metrics and rank models.
9. Save the best payload and evaluation outputs.

### Why this file is important

This script produces a technically honest result: direct India regression is attempted seriously, but its limited performance becomes the evidence for later reframing.

### Edge cases and caveats

- Any inference code must preserve the same shift amount used here.
- Developers should not overclaim this model’s predictive strength because the downstream reports explicitly characterize it as limited.

## `03b_train_india_latency_classifier.py`

### What was done

This script reframes latency prediction into a three-band classification task.

### Why it was done

If exact regression is weak, a discrete prediction task may still be useful for screening broad performance bands.

### Important functions

- `load_dataset()`
- `split_data()`
- `derive_thresholds()` computes training-data cutoffs
- `to_latency_bands()` converts numeric latency to class labels
- `get_models()` returns classifier candidates
- `evaluate_model()` computes classification metrics
- `train_and_compare()` runs the full experiment
- `band_distribution()` summarises class balance
- `write_outputs()` saves results and payloads
- `main()` orchestrates the phase

### Design reasoning

- Thresholds are derived from the training data so that label creation does not peek into the test distribution.
- Balanced class handling is important because not every band is equally frequent.

### Caveat

This is not the final India predictive task. It is an intermediate reframing step that tests whether classification is more defensible than regression.

## `03c_train_india_high_latency_classifier.py`

### What was done

This script builds a binary classifier that predicts whether a sample belongs to a high-latency condition.

### Why it was done

Binary high-risk screening is more operationally useful than raw point prediction in noisy settings. It can act as a first warning signal and later becomes one half of the dual-signal anomaly workflow.

### Important functions

- `load_dataset()` and `split_data()` load and split data
- `to_high_latency_target()` converts latency into a binary label using a cutoff
- `get_models()` defines classifier candidates
- `evaluate_model()` computes accuracy, balanced accuracy, precision, recall, and F1
- `evaluate_threshold()` compares multiple threshold choices
- `write_outputs()` saves result tables, confusion matrices, and payloads
- `main()` drives the script

### Step-by-step flow

1. Load the India feature dataset.
2. Split train and test.
3. Convert numeric latency into binary labels at one or more percentile thresholds.
4. Train multiple classifiers.
5. Evaluate them with class-sensitive metrics.
6. Select the best threshold/model pair.
7. Save the best classifier payload and reports.

### Design decisions

- Positive-class imbalance is explicitly handled.
- The script evaluates threshold choices because the operational meaning of “high latency” matters.

### Why a developer should care

This file is the main source of the classifier later reused in anomaly detection.