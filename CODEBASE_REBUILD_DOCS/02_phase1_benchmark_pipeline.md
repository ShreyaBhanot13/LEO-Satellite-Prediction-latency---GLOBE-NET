# Phase 1 Benchmark Pipeline (`scripts/`)

## Purpose of This Subsystem

The files in `scripts/` form the first benchmark pipeline. Their job is to establish a baseline supervised learning workflow for latency prediction using the initial engineered dataset. This phase answers a foundational project question: how well can standard regressors predict average latency from the available numeric features before advanced engineering and optimization are added?

The folder contains both modeling scripts and supporting utilities such as visualization and diagram generation.

## `scripts/01_data_preparation.py`

### What was done

This script loads the initial engineered dataset, performs basic quality checks, isolates the target column `ping_avg`, keeps numeric features only, fills missing numeric values with medians if necessary, and writes train/test splits to disk.

### Why it was done

Every later modeling script needs a stable and reproducible train/test split. Centralizing that split in one script avoids inconsistent sampling across models and ensures comparisons are fair.

### Technical details

- Input dataset: `data/final_engineered_dataset.csv`
- Output artifacts:
  - `outputs/train_data.pkl`
  - `outputs/test_data.pkl`
  - `outputs/data_info.txt`
- Configuration constants:
  - `RANDOM_STATE = 42`
  - `TEST_SIZE = 0.2`

The script uses `train_test_split()` from scikit-learn. It stores train and test data as tuples `(X, y)` in joblib files.

### Step-by-step flow

1. Validate that the input dataset file exists.
2. Load the CSV into a pandas dataframe.
3. Count missing values.
4. If missing values exist, fill numeric columns with medians.
5. Confirm that `ping_avg` exists.
6. Split the dataframe into `X` and `y`.
7. Restrict `X` to numeric columns only.
8. Apply an 80/20 train/test split.
9. Serialize the train and test tuples.
10. Write a human-readable text summary of the resulting dataset.

### Important functions, classes, and methods

This script is written as top-level logic and does not expose reusable internal functions. The most important external methods are:

- `pd.read_csv()`
- `DataFrame.fillna()`
- `train_test_split()`
- `joblib.dump()`

### Design decisions

- Median imputation is used because it is robust to outliers.
- Numeric-only filtering simplifies baseline model training, especially for regressors that expect numeric matrices.
- The fixed random seed ensures stable comparisons.

### Edge cases and error handling

- Raises `FileNotFoundError` if the dataset file is missing.
- Raises `ValueError` if the target column does not exist.

## `scripts/02_train_randomforest.py`

### What was done

This script trains a Random Forest regressor as one of the baseline models for latency prediction.

### Why it was done

Random Forest provides a strong non-linear tree-based baseline that handles feature interactions implicitly and is less sensitive to scaling than many alternatives.

### How it works

The script loads the prepared training and test sets, instantiates a `RandomForestRegressor`, performs evaluation using cross-validation and test metrics, and writes the trained model and results to disk.

### Expected inputs and outputs

- Reads `outputs/train_data.pkl` and `outputs/test_data.pkl`
- Writes a trained model pickle and a results CSV for later comparison

### Developer notes

- This script belongs to a family of parallel baseline trainers and should use the same train/test split as the SVR and XGBoost scripts.
- The exact model hyperparameters are less important than consistency of evaluation and output contract.

### Edge cases

- Feature ordering must remain consistent with what was saved in the split artifacts.
- Any changes to preprocessing should be made upstream in the preparation step rather than here.

## `scripts/03_train_svr.py`

### What was done

This script trains a Support Vector Regressor as another latency baseline.

### Why it was done

SVR provides a non-tree baseline and helps test whether margin-based regression can outperform ensemble trees on the dataset.

### Technical behavior

The script follows the same pattern as the other baseline trainers: load prepared data, train the regressor, evaluate it, and store both the model and results. Because SVR is computationally expensive on larger datasets, this phase typically uses a more conservative evaluation setup than tree models.

### Important implementation reasoning

- SVR is included for comparison diversity, not because it is expected to be the final production model.
- In large tabular settings, SVR often becomes a speed bottleneck, which is why downstream phases continue to focus more on boosting models.

## `scripts/04_train_xgboost.py`

### What was done

This script trains the baseline XGBoost regressor.

### Why it was done

Gradient-boosted trees are a strong default for structured tabular prediction tasks and often outperform both bagging methods and kernel methods when feature interactions matter.

### Technical flow

1. Load prepared train/test splits.
2. Instantiate an `XGBRegressor` with tuned baseline parameters.
3. Train on the training split.
4. Predict on the test split.
5. Compute RMSE, MAE, and $R^2$.
6. Save the model artifact and results.

### Why this file matters

This script becomes the benchmark winner in early phases and therefore sets the baseline that later feature engineering and target transformation attempt to beat.

## `scripts/05_compare_models.py`

### What was done

This script aggregates baseline model results, compares them, identifies the best model, and saves a canonical “best model” checkpoint.

### Why it was done

The project needs one place where model selection is formalized so later phases can refer to the benchmark winner consistently.

### Step-by-step logic

1. Load result CSVs from the baseline trainers.
2. Concatenate or compare them in a common table.
3. Select the highest test-set $R^2$.
4. Copy or save the corresponding model as the benchmark best model.
5. Write summary outputs such as `model_comparison.csv` and `model_selection.txt`.

### Design decisions

- Selection is based on held-out performance rather than only cross-validation.
- The script centralizes comparison logic so the rest of the project does not have to manually inspect multiple result files.

## `scripts/06_generate_visualizations.py`

### What was done

This script generates visual summaries of benchmark model performance.

### Why it was done

The project report and presentations require visual comparison of models, not just result CSVs. This script turns evaluation outputs into charts such as metric comparisons and residual-style plots.

### Dependencies

- `matplotlib`
- `seaborn`
- `pandas`

### Outputs

PNG files under the visualization folder and summary graphics usable in reports or presentations.

### Important developer note

This is not a modeling script. It depends entirely on outputs generated by earlier training steps.

## `scripts/07_run_best_model_inference.py`

### What was done

This script runs inference with the later best benchmark model and reconstructs the advanced feature schema needed for that model, especially the Phase 5 temporal and cyclical features.

### Why it was done

Once the benchmark branch moved beyond the original feature set, inference could no longer rely on raw columns alone. A dedicated inference script is necessary to rebuild the engineered inputs consistently outside training.

### Technical details

The script loads a saved best model, aligns an incoming dataframe to the expected feature schema, adds missing engineered fields such as cyclical encodings, and generates predictions.

### Design reasoning

- Keeping inference separate from training makes deployment simpler.
- Explicit feature alignment protects against silent schema mismatch.

### Edge cases

- If required columns are absent, predictions can become invalid.
- Engineered features must be recomputed exactly as they were during training.

## `scripts/08_download_ookla_india_latency.py`

### What was done

This script downloads Ookla mobile performance data and filters it to India.

### Why it was done

The India-first branch needs a repeatable way to pull or sample geographically relevant source data before profiling and feature building.

### Technical details

- Reads from an Ookla source URL in parquet form.
- Filters records using an India geographic bounding box.
- Writes an India-focused CSV for later phases.

### Important considerations

- This is a data acquisition helper and depends on network availability and the continued validity of the source URL.
- Geography filtering is based on coordinates, so bad coordinates in the source will affect downstream coverage.

## `scripts/generate_architecture_diagram.py`

### What was done

This file generates a system architecture diagram for documentation and presentation.

### Why it was done

The project needs a visual explanation of how data, preprocessing, model training, explainability, anomaly detection, and dashboard outputs connect.

### Developer note

The file is documentation-supporting rather than model-supporting. It is helpful for rebuilding report assets, not for reproducing training logic.

## `scripts/generate_diagrams.py`

### What was done

This is another documentation-asset generator used to create visual diagrams for presentations or reports.

### Why it was done

Different review stages often need simplified or alternate diagrams. This file likely exists to provide those variants.

## `scripts/generate_diagrams_extra.py`

### What was done

This file creates additional diagram variants beyond the main architecture output.

### Why it was done

It supports presentation and documentation refinement, especially where more than one figure style is needed.