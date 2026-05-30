# Workspace Organization Guide

## Folder Structure Details

### 01_Data/ — Data Management Hub
**Purpose:** Central storage for all data files (raw, processed, boundaries)

#### Subdirectories:
- **raw/** - Original unmodified source data
  - `india_mobile_latency_full.csv` - Original Ookla dataset (62.7 MB, 562,527 rows)
  
- **processed/** - Cleaned, engineered, ready-for-analysis datasets
  - `ookla_india_latency_holistic.csv` - MAIN DATASET (141 MB, 12 columns, 100% complete)
  - `ookla_data_with_states.csv` - Simplified version (27.9 MB, 8 columns)
  - `state_wise_latency_analysis.csv` - State-level aggregations
  
- **boundaries/** - Geospatial boundary files
  - `natural_earth_boundaries/` - Official admin boundary shapefiles for 36 Indian states
  - Format: Shapefile (.shp, .shx, .dbf, .prj, .cpg components)
  - Source: Natural Earth 10m Admin 1 States/Provinces
  - Accuracy: 99%+ verified

**Usage:**
- Place new raw data in `raw/`
- Store processed outputs in `processed/`
- Reference boundary files for spatial analysis

---

### 02_Notebooks/ — Jupyter Analysis Environment
**Purpose:** Interactive analysis, exploration, and visualization

#### Contents:
- **Ookla_India_Latency_Analysis_Professional.ipynb** (Current)
  - 24 executable code cells + 22 markdown cells
  - Sections: Setup → EDA → Normality Testing → Correlations → Geospatial Analysis → Exports
  - All cells executed successfully (timestamps recorded)
  - Runtime: ~2 minutes total
  - Output: 20+ visualizations + 3 CSV exports

**Workflow:**
1. Open notebook in Jupyter/JupyterLab
2. Run cells sequentially (all dependencies satisfied)
3. View embedded visualizations
4. Access generated reports in `05_Results/`

**Python Environment:**
- Python 3.14.2 (.venv)
- Kernel: ipykernel ready
- Key packages: pandas 3.0.1, geopandas 1.1.3, matplotlib 3.10.8, seaborn 0.13.2

---

### 03_Scripts/ — Reusable Python Code
**Purpose:** Modular scripts for data processing, analysis, and modeling

#### Subdirectories:

- **preprocessing/** - Data cleaning & preparation
  - Data validation routines
  - Missing value handling
  - Outlier detection
  - Feature scaling utilities
  
- **analysis/** - Statistical & exploratory analysis
  - Descriptive statistics
  - Correlation analysis
  - Distribution testing
  - Geographic analysis
  
- **modeling/** - Machine learning model training
  - Model training pipelines
  - Cross-validation scripts
  - Hyperparameter tuning
  - Model evaluation
  
- **utils/** - Helper functions & utilities
  - Data loading helpers
  - Visualization utilities
  - Metric calculation functions
  - I/O utilities

**Usage:**
```python
# Example: Import utilities
from scripts.utils.data_loader import load_processed_data
from scripts.analysis.stats import calculate_state_statistics
```

---

### 04_Models/ — Model Management
**Purpose:** Storage for trained models and configuration files

#### Subdirectories:

- **trained/** - Saved model files (pickle, joblib, h5, etc.)
  - Ready-to-use predictive models
  - Serialized model objects
  
- **backups/** - Model version control & previous versions
  - Historical model snapshots
  - Alternative architectures
  - Comparison versions
  
- **configs/** - Model hyperparameter files (JSON, YAML)
  - Training hyperparameters
  - Architecture definitions
  - Feature lists
  - Preprocessing configs

**Naming Convention:**
- `model_xgboost_v1.joblib`
- `config_catboost_v2.json`
- `backup_ensemble_2026-05-04.pkl`

---

### 05_Results/ — Analysis Outputs
**Purpose:** Store all generated outputs (visualizations, reports, exports)

#### Subdirectories:

- **visualizations/** - Generated plots & charts (PNG, JPG, PDF)
  - Distribution plots (histograms, KDE, box plots)
  - Heatmaps (correlation matrices)
  - Scatter plots (feature relationships)
  - Bar charts (state rankings)
  - Geographic maps (if generated)
  
- **reports/** - Tabular data exports (CSV, Excel)
  - `state_wise_latency_analysis.csv` - State statistics
  - Summary statistics tables
  - Comparison matrices
  - Performance metrics
  
- **exports/** - Final deliverable datasets (production-ready)
  - `ookla_india_latency_holistic.csv` - Complete dataset
  - Export versions with various feature sets
  - Model prediction outputs

**File Organization:**
- Organize by analysis phase or topic
- Include timestamps in filenames for versioning
- Document data dictionary in accompanying README

---

### 06_Documentation/ — Project Documentation
**Purpose:** Professional project documentation and guides

#### Subdirectories:

- **analysis/** - Methodology & technical documentation
  - Data processing methodology
  - Statistical testing approaches
  - Geospatial analysis techniques
  - Model architecture descriptions
  
- **findings/** - Analysis results & discoveries
  - EDA summary
  - Key insights
  - State-level patterns
  - Performance rankings
  
- **recommendations/** - Actionable findings
  - Infrastructure improvement suggestions
  - Geographic insights for planning
  - Best practices
  - Policy recommendations

#### Key Files:
- **DATASET_SUFFICIENCY_ASSESSMENT.md** - Complete project readiness evaluation
  - Scoring: 9.5/10 (Production Ready)
  - Use cases: Modeling, clustering, planning, publication
  - Limitations: Geographic focus (India only)
  - Next steps: Implement predictive models

---

### 07_Archive/ — Legacy & Historical Content
**Purpose:** Store old versions, previous iterations, and redundant files

#### Subdirectories:

- **legacy_scripts/** - Previous script versions
  - `scripts/` - Initial data preparation scripts
  - `scripts_v2/` - Second iteration with feature engineering
  - `scripts_v3/` - Ensemble and optimization attempts
  - `scripts_v6_final/` - Final preprocessing variants
  
- **legacy_outputs/** - Old analysis outputs
  - `outputs/` - Initial model results
  - `outputs_v2/` - Feature engineering results
  - `outputs_v3/` - Ensemble results
  - `outputs_v5/` - Phase 5 results
  - `outputs_v6_final/` - Phase 6 results

**Purpose of Archive:**
- Reference old methods
- Compare approach evolution
- Maintain version history
- Troubleshoot compatibility

**Access Pattern:** Only reference if needed for:
- Understanding methodology evolution
- Comparing old vs. new results
- Debugging issues with legacy code

---

## Workflow Examples

### Adding a New Analysis
```
1. Create analysis script:
   03_Scripts/analysis/new_analysis.py

2. Run analysis and save results:
   - CSV outputs → 05_Results/reports/
   - Visualizations → 05_Results/visualizations/

3. Document findings:
   06_Documentation/findings/new_analysis_report.md

4. Reference in notebook if needed:
   Add code cell to 02_Notebooks/
```

### Developing a Predictive Model
```
1. Create training script:
   03_Scripts/modeling/train_model_xgboost.py

2. Save trained model:
   04_Models/trained/model_xgboost_v1.joblib
   04_Models/configs/config_xgboost_v1.json

3. Store backup:
   04_Models/backups/model_xgboost_v1_backup.pkl

4. Export predictions:
   05_Results/exports/predictions_xgboost_v1.csv

5. Document results:
   06_Documentation/findings/model_performance.md
```

### Processing New Data
```
1. Place raw data:
   01_Data/raw/new_dataset.csv

2. Create processing script:
   03_Scripts/preprocessing/process_new_data.py

3. Output cleaned data:
   01_Data/processed/new_dataset_cleaned.csv

4. Update data dictionary:
   06_Documentation/DATA_DICTIONARY.md
```

---

## File Management Best Practices

### ✅ DO:
- Use descriptive filenames with dates/versions
- Organize by topic/analysis phase
- Include README files in major folders
- Document data dictionaries
- Archive old versions regularly
- Back up critical files

### ❌ DON'T:
- Store raw data in multiple locations
- Leave untitled/temporary files
- Mix processed and raw data
- Store models outside `04_Models/`
- Hard-code file paths (use relative paths)
- Remove archived content without backup

---

## Key File Locations

| What | Where |
|------|-------|
| Main dataset | `01_Data/processed/ookla_india_latency_holistic.csv` |
| Analysis notebook | `02_Notebooks/Ookla_India_Latency_Analysis_Professional.ipynb` |
| State statistics | `05_Results/reports/state_wise_latency_analysis.csv` |
| Visualizations | `05_Results/visualizations/` |
| Boundaries data | `01_Data/boundaries/natural_earth_boundaries/` |
| Documentation | `06_Documentation/` |
| Findings | `06_Documentation/findings/` |
| Old scripts | `07_Archive/legacy_scripts/` |

---

## Environment Setup

### Python Virtual Environment
```bash
# Location: .venv in workspace
# Python: 3.14.2
# Status: Ready to use

# Activate (Windows PowerShell)
.\.venv\Scripts\Activate.ps1

# Activate (Windows Command Prompt)
.venv\Scripts\activate.bat
```

### Key Dependencies
- **Data:** pandas 3.0.1, numpy 2.4.2, pyarrow 2025.1.0
- **Geospatial:** geopandas 1.1.3, shapely 2.1.2
- **Analysis:** scipy 1.17.0, scikit-learn 1.8.0
- **Visualization:** matplotlib 3.10.8, seaborn 0.13.2
- **ML:** CatBoost 1.2.10, LightGBM 4.6.0, XGBoost 3.2.0

---

## Project Status Summary

✅ **Data Acquisition:** Complete (562,527 tiles)  
✅ **Data Processing:** Complete (100% coverage, 36 states)  
✅ **Exploratory Analysis:** Complete (26+ analyses)  
✅ **Documentation:** Complete (Professional notebook, full documentation)  
✅ **Dataset Export:** Complete (Multiple formats available)  
✅ **Organization:** Complete (Folder structure created)  
⏳ **Modeling:** Ready to begin (Dataset prepared and validated)  
⏳ **Presentation:** Ready for final review

---

**Last Updated:** May 4, 2026  
**Status:** All organizational tasks complete  
**Next Phase:** Model development & advanced analysis
