# Phase 2 Feature Engineering (`scripts_v2/`)

## Purpose of This Subsystem

The files in `scripts_v2/` extend the benchmark pipeline beyond the raw baseline. Their role is to inspect feature usefulness, design new features, retrain the benchmark models on the expanded schema, compare the updated results against Phase 1, and save the best V2 artifact.

This phase is important because it shows that the project does not treat the initial dataset as fixed. Instead, it actively engineers additional signal from the original measurements.

## `scripts_v2/00_feature_analysis.py`

### What was done

This script performs feature analysis to identify which raw inputs appear most predictive and where engineering effort might pay off.

### Why it was done

Feature engineering should not be random. This script exists to provide evidence for which columns deserve interaction terms, ratio construction, or transformation.

### Technical behavior

The script uses model-based importance and correlation analysis to identify influential features and possible multicollinearity. Its outputs are textual summaries rather than trained production artifacts.

### Outputs

- feature-importance notes
- engineering suggestions for the V2 phase

### Design reasoning

- This script front-loads exploratory analysis so feature engineering can be justified.
- It reduces the chance of adding arbitrary or low-value engineered features.

## `scripts_v2/01_feature_engineering.py`

### What was done

This script creates the V2 engineered feature set from the original benchmark train/test data.

### Why it was done

The goal of this file is to improve predictive performance by exposing interactions and non-linear relationships that the original features may not express well on their own.

### Major dependencies

- `pandas`
- `numpy`
- `joblib`
- `sklearn.preprocessing.PolynomialFeatures` is imported even though the visible script applies handcrafted squared terms instead of full generated polynomial matrices.

### Step-by-step logic

1. Load `train_data.pkl` and `test_data.pkl` from the Phase 1 output folder.
2. Record the original feature list.
3. Build interaction features among selected top features, such as time or location combinations.
4. Add squared terms for selected continuous columns.
5. Add a ratio feature, for example loss relative to signal strength, using a tiny constant to avoid divide-by-zero.
6. Add an `hour_period` bucket feature using `pd.cut()`.
7. Check the resulting matrix for `NaN` or infinite values.
8. Clean any problematic values with medians.
9. Save V2 train/test splits and a text file describing the final feature set.

### Important engineered features

- interaction terms such as `weekday_x_hour`-style combinations
- squared continuous features
- `loss_signal_ratio`
- `hour_period`

### Design decisions

- The script uses handcrafted feature additions rather than a large automatic polynomial expansion, which keeps the feature set interpretable.
- Safe division offsets are used so ratio features cannot crash on zeros.
- Output is written as a new artifact set rather than overwriting the original Phase 1 files.

### Edge cases and error handling

- Missing columns are handled defensively by checking whether a feature exists before using it.
- Infinite and missing values created by feature engineering are explicitly cleaned before saving.

## `scripts_v2/02_train_xgboost_v2.py`

### What was done

This script retrains the XGBoost regressor on the V2 feature set.

### Why it was done

XGBoost was strong in Phase 1, so it is a natural candidate to test whether engineered features actually improve predictive performance.

### Technical flow

1. Load `train_data_v2.pkl` and `test_data_v2.pkl`.
2. Train an XGBoost regressor with the expanded feature schema.
3. Evaluate on the unchanged held-out test split.
4. Save the V2 model and a result file.

### Developer note

The unchanged split is important. It ensures improvements come from better features or modeling, not from easier sampling.

## `scripts_v2/03_train_randomforest_v2.py`

### What was done

This script retrains the Random Forest baseline on the engineered V2 inputs.

### Why it was done

The project needs to know whether the new features benefit all model families equally or mainly help boosting-based learners.

### Interpretation use

If Random Forest improves less than XGBoost, that finding supports later architectural emphasis on boosting models.

## `scripts_v2/04_train_svr_v2.py`

### What was done

This script retrains the SVR model on the V2 feature set.

### Why it was done

It tests whether the engineered feature set helps kernel regression, even though SVR is computationally heavier and less scalable than tree ensembles in this project.

### Caveat

SVR can degrade or become less practical as feature complexity and dataset size grow, which is one reason later phases continue moving toward boosting methods.

## `scripts_v2/05_compare_v2_models.py`

### What was done

This script compares Phase 2 model performance against both the original Phase 1 results and the new V2 results.

### Why it was done

Feature engineering needs to be justified empirically. This script formalizes that comparison.

### Outputs

- comparison tables
- improvement-analysis text

### Important reasoning

The script tells the team whether V2 is a real improvement, which model benefited the most, and whether feature engineering should remain part of later phases.

## `scripts_v2/06_create_final_model.py`

### What was done

This script selects and packages the best V2 model as the Phase 2 final artifact.

### Why it was done

Downstream work such as Phase 3 comparisons and handoff needs a single authoritative V2 best model.

### Technical flow

1. Read comparison results.
2. Select the best performer under the project’s metric policy.
3. Save the winning estimator as the V2 final model.
4. Write a summary report for documentation.

### Developer note

This file closes the Phase 2 loop in the same way `05_compare_models.py` closes Phase 1.