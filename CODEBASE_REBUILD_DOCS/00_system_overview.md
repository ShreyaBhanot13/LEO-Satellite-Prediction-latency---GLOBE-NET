# System Overview

## What the Project Is

The project is an explainable machine learning system for network-performance analysis. It has two connected technical streams.

The first stream is a benchmark latency-prediction pipeline based on a global or Europe-style dataset. This stream exists to establish the machine learning methodology. It starts with raw engineered measurements, creates train/test datasets, trains baseline regressors, adds engineered features, tests stronger learners, applies target transformation, and progressively improves the predictive baseline. This stream answers the question, “Can the team build and optimize a serious latency-prediction pipeline under a controlled setup?”

The second stream is an India-first operational pipeline. This stream exists because the final project needed a realistic deployment-oriented use case rather than only a benchmark model. It starts with India Ookla and TRAI data, profiles the data, builds India-native features, attempts direct latency regression, discovers that exact regression is weak, and then reframes the problem into classification, anomaly detection, and zone-level high-risk identification. This stream answers the question, “How can noisy real-world telemetry be converted into interpretable, prioritised operational insight?”

## High-Level Architecture

The codebase is organized as a staged analytics system rather than a single program.

The benchmark branch is implemented in `scripts/`, `scripts_v2/`, and `scripts_v3/`.

- `scripts/` contains the Phase 1 baseline pipeline.
- `scripts_v2/` contains feature engineering and re-training on expanded inputs.
- `scripts_v3/` contains advanced methods such as stacking, LightGBM, CatBoost, target transformation, ultra-optimization, and phase-5 temporal engineering.

The India branch is implemented in `09_INDIA_FIRST_ANALYSIS/02_scripts/`.

- It begins with TRAI ingestion and merging.
- It profiles the India data.
- It builds model-ready datasets.
- It trains regression and classification models.
- It runs SHAP explainability.
- It detects anomalies.
- It performs Karnataka-focused analysis.
- It builds zone-level risk datasets.
- It trains and explains the final zone-risk classifier.
- It generates state and presentation summaries.

The user-facing delivery layer is `app.py`, a Streamlit dashboard that loads saved artifacts from the India pipeline together with benchmark reference outputs and presents them as maps, charts, state comparisons, explainability views, and a live scoring workflow.

## Main Technical Features

The codebase implements the following major features.

### 1. Supervised regression for benchmark latency prediction

This is the main task in the benchmark branch. Multiple regressors are trained and compared using a fixed train/test split, cross-validation, and common regression metrics such as RMSE, MAE, and $R^2$.

### 2. Iterative feature engineering

The benchmark branch grows from the original numeric feature set into richer representations using interactions, polynomial terms, ratio features, binned time features, cyclical encodings, temporal features, and later interaction-heavy improvements.

### 3. Target transformation

The project applies log transformation to the latency target to reduce skew and heteroscedasticity. This becomes a major turning point in the benchmark stream because it improves stability and accuracy while preserving the ability to report predictions in the original unit after inverse transformation.

### 4. India regression and task reframing

The India branch first attempts direct latency regression on a large, India-native feature set. Because the result remains weak, the project uses that evidence to pivot toward more defensible predictive tasks.

### 5. Binary and multi-class classification

The India branch includes both multi-band latency classification and binary high-latency classification. These tasks are useful because they turn a difficult numeric prediction problem into an operationally relevant risk-screening problem.

### 6. Dual-signal anomaly detection

The anomaly layer combines regression residuals with classifier risk signals. This allows the project to distinguish between locations that are simply slow and locations that are performing worse than the model expects given their context.

### 7. Zone-level high-risk classification

This is the strongest India-first predictive contribution. Instead of predicting exact latency for raw observations, the code aggregates records into zones and classifies whether a zone is high risk based on the upper tail of latency behavior.

### 8. Explainability with SHAP

SHAP is used both for the India regression model and for the final zone-risk classifier. Global rankings and local explanations are exported so the model can be interpreted by operators and report writers.

### 9. Dashboard-based exploration and live scoring

The Streamlit app loads saved model payloads, zone summaries, state summaries, SHAP outputs, Karnataka results, and operator context so users can inspect patterns and simulate a zone through a live scoring interface.

## Data Storage Model

The project is file-based rather than database-driven.

- Raw and intermediate datasets are stored as CSV or parquet-derived CSV files.
- Model-ready train/test splits are serialized with `joblib` as `.pkl` files.
- Model payloads are stored as `.pkl` dictionaries or estimator objects.
- Reports are stored as plain text or markdown files.
- Visual outputs are stored as PNG images.
- The dashboard reads these files at runtime rather than querying an API or database.

This is important for reconstruction: anyone reproducing the project needs a disciplined artifact layout rather than a database server.

## Important Design Principles

### Separation between offline analytics and presentation

The training and feature-engineering logic is kept in scripts. The dashboard does not retrain anything. It loads artifacts and visualizes them. This keeps the application responsive and makes the modeling workflow reproducible.

### Evidence-driven reframing

The codebase does not force one modeling objective on every dataset. Where exact regression is not defensible, the pipeline shifts to classification and anomaly analysis. This is a deliberate architecture and methodology decision.

### Reproducibility through file outputs

Every major phase writes outputs that become inputs for the next stage. This creates explicit data lineage and makes it possible to inspect, hand off, and re-run the pipeline in parts.

### Interpretability as a first-class output

SHAP exports, state summaries, anomaly summaries, and dashboard views are treated as core deliverables rather than optional extras.