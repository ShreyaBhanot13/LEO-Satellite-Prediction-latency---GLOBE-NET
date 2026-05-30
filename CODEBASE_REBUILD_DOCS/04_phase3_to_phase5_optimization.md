# Phase 3 to Phase 5 Optimization (`scripts_v3/`)

## Purpose of This Subsystem

The files in `scripts_v3/` push the benchmark pipeline beyond straightforward feature engineering. This phase tests ensemble stacking, alternative boosting libraries, target transformation, more aggressive tuning, and a stronger temporal feature set. The goal is to break through the plateau reached by earlier phases.

## `scripts_v3/01_ensemble_stacking.py`

### What was done

This script builds a stacking ensemble that combines predictions from V2 base learners using a meta-model.

### Why it was done

If different base models make complementary errors, a meta-learner can combine them into a stronger predictor than any individual model.

### Technical details

- Base models: the main V2 regressors
- Meta-features: the base-model predictions
- Meta-learner: Ridge regression

### Step-by-step flow

1. Load trained V2 base models.
2. Generate predictions that become meta-level inputs.
3. Fit a Ridge model on those prediction vectors.
4. Evaluate the stacked prediction on the test set.
5. Save the ensemble artifact and summary results.

### Design caveat

Stacking can overfit if the meta-model learns from over-optimistic predictions. This is why its empirical result matters more than the theoretical appeal.

## `scripts_v3/02_train_lightgbm.py`

### What was done

This script trains a LightGBM regressor on the V2 features.

### Why it was done

LightGBM is a popular high-performance gradient boosting library for tabular data. The script tests whether it can match or beat XGBoost while training faster.

### Technical notes

- It performs parameter tuning over tree and learning-rate settings.
- It outputs a saved model and results CSV for Phase 3 comparison.

## `scripts_v3/03_train_catboost.py`

### What was done

This script trains a CatBoost regressor on the V2 features.

### Why it was done

CatBoost is strong on structured data and often handles interaction structure well, even when the original schema includes categorical effects or mixed feature behavior.

### Important reasoning

The file is part of the project’s transition toward later CatBoost-heavy optimization. Even when it is not yet the absolute final winner, it establishes CatBoost as a serious candidate.

## `scripts_v3/04_target_transformation.py`

### What was done

This script log-transforms the target variable and trains XGBoost on the transformed scale, then inverse-transforms predictions back to the original scale.

### Why it was done

Latency targets can be skewed and heteroscedastic. A log transformation often makes the problem easier to model because large values become less dominant and multiplicative structure becomes more linear.

### Technical details

The script computes a shift value so that all targets are positive before taking logs.

The transformation is:

$$
y_{log} = \log(y + shift)
$$

The inverse prediction step is:

$$
\hat{y} = \exp(\hat{y}_{log}) - shift
$$

### Step-by-step flow

1. Load V2 train/test artifacts.
2. Compute `shift_amount = -min(y_train) + 1`.
3. Add the shift and take the log of train and test targets.
4. Train XGBoost on the transformed target.
5. Predict on the test set in log space.
6. Inverse-transform predictions to the original latency scale.
7. Compute RMSE, MAE, and $R^2$ on the original scale.
8. Save the model, transform metadata, and result CSV.

### Design decisions

- The inverse-transform step ensures evaluation remains interpretable in the original unit.
- The transform info is stored separately so downstream users know how to reconstruct predictions.

### Edge cases

- Negative or very small targets are handled through the positive shift.
- A developer rebuilding this script must preserve the same shift during inference.

## `scripts_v3/05_compare_phase3.py`

### What was done

This script compares all major Phase 3 experiments against the V2 benchmark.

### Why it was done

Once multiple advanced techniques exist, the project needs a single evaluation layer to decide which approach actually improved the benchmark.

### What it likely consolidates

- ensemble stacking results
- LightGBM results
- CatBoost results
- log-transform XGBoost results
- baseline V2 reference

## `scripts_v3/06_phase4_ultra_optimization.py`

### What was done

This script performs more aggressive benchmark optimization through deeper hyperparameter search and additional model variants.

### Why it was done

The project wanted to test whether the benchmark branch could move materially closer to the desired performance ceiling.

### Technical themes

- larger numbers of estimators
- lower learning rates with longer training
- deeper ensembles or stronger tree learners
- more aggressive search over performance-sensitive parameters

### Design caveat

This phase is exploratory by design. Its value is to test how much more signal the benchmark dataset can yield before diminishing returns set in.

## `scripts_v3/07_phase5_feature_engineering.py`

### What was done

This script creates the Phase 5 feature set with stronger temporal, cyclical, and interaction-based features.

### Why it was done

Earlier phases showed that engineered structure helps. Phase 5 pushes further by encoding periodic time behavior and richer interactions that standard raw columns cannot capture.

### Technical details

The main new idea is cyclical encoding. For example, hour-of-day is transformed into sine and cosine coordinates so that the model treats 23:00 and 00:00 as close rather than far apart.

Typical formulas are:

$$
hour_{sin} = \sin(2\pi h / 24), \quad hour_{cos} = \cos(2\pi h / 24)
$$

Analogous encodings can be created for day or month.

### Other feature types

- interaction terms between important features
- possible lag-style or temporal-structure terms if ordered behavior is available
- polynomial features for non-linear numeric effects

### Why it matters

This script sets up the stronger benchmark artifact that later reaches the low-0.81 $R^2$ range.

## `scripts_v3/08_phase5_train_models.py`

### What was done

This script trains the best candidate regressors on the Phase 5 feature set, typically with the improved target-treatment logic already established in earlier phases.

### Why it was done

Creating a stronger feature set only matters if the models are retrained and evaluated under the same benchmark conditions.

### Step-by-step flow

1. Load Phase 5 train/test artifacts.
2. Train candidate regressors such as boosting models and CatBoost.
3. Generate predictions.
4. Evaluate on the held-out test split.
5. Save result tables and the best-performing model.

### Important outcome

This phase produces one of the key benchmark deliverables later referenced in final reports and in the dashboard’s global snapshot.