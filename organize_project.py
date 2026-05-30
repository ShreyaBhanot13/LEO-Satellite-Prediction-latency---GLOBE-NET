"""
Project Organization Script
============================
Organizes the FY_ML project for clean handoff to Person 3 and Person 4.
"""

import shutil
from pathlib import Path
import os

print("="*80)
print("ORGANIZING FY_ML PROJECT FOR HANDOFF")
print("="*80)

BASE = Path(".")

# STEP 1: IDENTIFY FILES & FOLDERS
print("\n[1] Analyzing project structure...")

# ESSENTIAL - Keep these
ESSENTIAL_SCRIPTS = {
    "scripts": "Phase 1 - Baseline models (XGBoost, RF, SVR)",
    "scripts_v2": "Phase 2 - Feature engineering (18→21 features)",
    "scripts_v3": "Phase 3-5 - Advanced methods (Log transform, CatBoost, Temporal)",
    "scripts_v6_final": "Phase 6 - Final optimization (Interactions + Ensemble)"
}

ESSENTIAL_OUTPUTS = {
    "outputs": "Phase 1 outputs - baseline models",
    "outputs_v2": "Phase 2 outputs - engineered features",
    "outputs_v3": "Phase 3-4 outputs - advanced methods",
    "outputs_v5": "Phase 5 outputs - temporal features (81.40%)",
    "outputs_v6_final": "Phase 6 outputs - final ensemble (81.56%)"
}

ESSENTIAL_DATA = ["data"]
ESSENTIAL_VIZ = ["visualizations"]
ESSENTIAL_DOCS = ["reports", "docs", "notebooks"]

# CAN DELETE - Not needed
CAN_DELETE = [
    ".venv-1",
    "scripts_v6",
    "outputs_v6",        # Old experiment (superseded by outputs_v6_final)
    "catboost_info",
]

# REDUNDANT DOCS - Can archive
REDUNDANT_DOCS = [
    "IMPROVEMENT_OPTIONS.txt",
    "V2_PIPELINE_README.md",
    "PHASE3_README.md",
    "ML_PIPELINE_GUIDE.txt",
]

# STEP 2: CLEAN UP UNNECESSARY FILES
print("\n[2] Moving unnecessary files to archive...")

for item in CAN_DELETE:
    src = BASE / item
    if src.exists():
        dst = BASE / "archive" / "old_outputs" / item
        if src.is_dir():
            if not dst.exists():
                shutil.move(str(src), str(dst))
                print(f"   Archived: {item}/")
        else:
            if not dst.exists():
                shutil.move(str(src), str(dst))
                print(f"   Archived: {item}")

for item in REDUNDANT_DOCS:
    src = BASE / item
    if src.exists():
        dst = BASE / "archive" / "redundant_files" / item
        dst.parent.mkdir(parents=True, exist_ok=True)
        if not dst.exists():
            shutil.move(str(src), str(dst))
            print(f"   Archived: {item}")

# STEP 3: CREATE HANDOFF PACKAGES
print("\n[3] Creating handoff packages...")

# --- FINAL MODEL PACKAGE ---
final_model_dir = BASE / "FINAL_HANDOFF" / "FINAL_MODEL"
final_model_dir.mkdir(parents=True, exist_ok=True)

# Copy best model
src_model = BASE / "outputs_v6_final" / "ensemble_best_model.pkl"
if src_model.exists():
    shutil.copy(str(src_model), str(final_model_dir / "BEST_MODEL_81.56_ensemble.pkl"))
    print("   Copied: BEST_MODEL_81.56_ensemble.pkl")

# Also copy V6 standalone (simpler to use)
src_v6 = BASE / "outputs_v6_final" / "catboost_v6_final.pkl"
if src_v6.exists():
    shutil.copy(str(src_v6), str(final_model_dir / "CATBOOST_V6_81.52.pkl"))
    print("   Copied: CATBOOST_V6_81.52.pkl")

# Copy V5 as backup
src_v5 = BASE / "outputs_v5" / "phase5_best_model.pkl"
if src_v5.exists():
    shutil.copy(str(src_v5), str(final_model_dir / "CATBOOST_V5_81.40.pkl"))
    print("   Copied: CATBOOST_V5_81.40.pkl")

# --- DATA PACKAGE FOR PERSON 3 & 4 ---
for person_dir in ["FOR_PERSON3_SHAP", "FOR_PERSON4_ANOMALY"]:
    person_path = BASE / "FINAL_HANDOFF" / person_dir
    person_path.mkdir(parents=True, exist_ok=True)
    
    # Copy final model
    if src_model.exists():
        shutil.copy(str(src_model), str(person_path / "ensemble_best_model.pkl"))
    
    # Copy test data
    src_test_v5 = BASE / "outputs_v5" / "test_data_v5.pkl"
    src_test_v6 = BASE / "outputs_v6_final" / "test_data_v6_final.pkl"
    if src_test_v5.exists():
        shutil.copy(str(src_test_v5), str(person_path / "test_data_v5.pkl"))
    if src_test_v6.exists():
        shutil.copy(str(src_test_v6), str(person_path / "test_data_v6_final.pkl"))
    
    print(f"   Created: {person_dir}/")

# --- DOCUMENTATION PACKAGE ---
doc_dir = BASE / "FINAL_HANDOFF" / "DOCUMENTATION"
doc_dir.mkdir(parents=True, exist_ok=True)

# Copy key docs
key_docs = [
    "00_PROJECT_FINAL_SUMMARY.txt",
    "FYP_COMPLETE_SUMMARY.txt",
    "TEAM_HANDOFF_GUIDE.txt",
    "PHASE5_FINAL_MODEL_REPORT.txt",
    "COMPLETE_MODEL_COMPARISON.csv",
    "OPTIMIZATION_COMPLETE_SUMMARY.csv"
]

for doc in key_docs:
    src = BASE / doc
    if src.exists():
        shutil.copy(str(src), str(doc_dir / doc))
        print(f"   Copied doc: {doc}")

# Copy phase 6 analysis
src_p6 = BASE / "outputs_v6_final" / "phase6_final_analysis.txt"
if src_p6.exists():
    shutil.copy(str(src_p6), str(doc_dir / "phase6_final_analysis.txt"))

# STEP 4: CREATE README FOR HANDOFF
print("\n[4] Creating handoff README...")

readme_content = """
================================================================================
                     FY_ML PROJECT - FINAL HANDOFF PACKAGE
================================================================================

FINAL MODEL ACCURACY: R² = 0.8156 (81.56%)
Total Improvement: +1.89% from baseline (79.67% → 81.56%)

================================================================================
FOLDER STRUCTURE
================================================================================

FINAL_HANDOFF/
├── FINAL_MODEL/
│   ├── BEST_MODEL_81.56_ensemble.pkl
│   ├── CATBOOST_V6_81.52.pkl
│   └── CATBOOST_V5_81.40.pkl
│
├── FOR_PERSON3_SHAP/
│   ├── ensemble_best_model.pkl
│   ├── test_data_v5.pkl
│   └── test_data_v6_final.pkl
│
├── FOR_PERSON4_ANOMALY/
│   ├── ensemble_best_model.pkl
│   ├── test_data_v5.pkl
│   └── test_data_v6_final.pkl
│
└── DOCUMENTATION/
    ├── 00_PROJECT_FINAL_SUMMARY.txt
    ├── FYP_COMPLETE_SUMMARY.txt
    ├── COMPLETE_MODEL_COMPARISON.csv
    └── ...

================================================================================
MAIN SCRIPTS (ORGANIZED BY PHASE)
================================================================================

scripts/                    # Phase 1: Baseline (R² = 79.67%)
├── 01_data_preparation.py
├── 02_train_randomforest.py
├── 03_train_svr.py
├── 04_train_xgboost.py
├── 05_compare_models.py
└── 06_generate_visualizations.py

scripts_v2/                 # Phase 2: Feature Engineering (R² = 79.82%)
├── 00_feature_analysis.py
├── 01_feature_engineering.py
├── 02_train_xgboost_v2.py
├── 03_train_randomforest_v2.py
├── 04_train_svr_v2.py
├── 05_compare_v2_models.py
└── 06_create_final_model.py

scripts_v3/
├── 01_ensemble_stacking.py
├── 02_train_lightgbm.py
├── 03_train_catboost.py
├── 04_target_transformation.py  # Phase 3: Log transform (R² = 80.32%)
├── 05_compare_phase3.py
├── 06_phase4_ultra_optimization.py  # Phase 4: Ultra-opt (R² = 80.93%)
├── 07_phase5_feature_engineering.py # Phase 5: Temporal (32 features)
└── 08_phase5_train_models.py        # Phase 5: CatBoost V5 (R² = 81.40%)

scripts_v6_final/           # Phase 6: Final Optimization (R² = 81.56%)
├── 01_phase6_final_experiment.py    # Interaction features (R² = 81.52%)
└── 02_ensemble_v5_v6.py

================================================================================
HOW TO USE THE FINAL MODEL
================================================================================

import joblib
import numpy as np

ens = joblib.load('FINAL_HANDOFF/FINAL_MODEL/BEST_MODEL_81.56_ensemble.pkl')

X_test_v5, y_test = joblib.load('FINAL_HANDOFF/FOR_PERSON3_SHAP/test_data_v5.pkl')
X_test_v6, _ = joblib.load('FINAL_HANDOFF/FOR_PERSON3_SHAP/test_data_v6_final.pkl')

# Get predictions from both models
pred_v5_log = ens['v5_model'].predict(X_test_v5)
pred_v6_log = ens['v6_model'].predict(X_test_v6)

# Inverse transform
pred_v5 = np.exp(pred_v5_log) - ens['shift_amount']
pred_v6 = np.exp(pred_v6_log) - ens['shift_amount']

# Combine with weights (0.3*V5 + 0.7*V6)
final_pred = ens['weight_v5'] * pred_v5 + ens['weight_v6'] * pred_v6

================================================================================
SIMPLER ALTERNATIVE (Single Model)
================================================================================

If ensemble is too complex, use CatBoost V6 directly:

import joblib
import numpy as np

model_dict = joblib.load('FINAL_HANDOFF/FINAL_MODEL/CATBOOST_V6_81.52.pkl')
model = model_dict['model']
shift = model_dict['shift_amount']

X_test, y_test = joblib.load('FINAL_HANDOFF/FOR_PERSON3_SHAP/test_data_v6_final.pkl')

# Predict
y_pred_log = model.predict(X_test)
y_pred = np.exp(y_pred_log) - shift

================================================================================
FILES ARCHIVED (NOT NEEDED)
================================================================================

Moved to archive/ folder:
- .venv-1/
- outputs_v6/
- catboost_info/
- scripts_v6/
- Various old READMEs

These can be deleted if you need space.

================================================================================
OPTIMIZATION JOURNEY SUMMARY
================================================================================

Phase 1 (Baseline):      R² = 79.67% (XGBoost, 18 features)
Phase 2 (Features):      R² = 79.82% (+0.15%)
Phase 3 (Log Transform): R² = 80.32% (+0.50%)
Phase 4 (Ultra-Opt):     R² = 80.93% (+0.61%)
Phase 5 (Temporal):      R² = 81.40% (+0.47%)
Phase 6 (Interactions):  R² = 81.52% (+0.12%)
Phase 6 (Ensemble):      R² = 81.56% (+0.04%) ← FINAL

Total Improvement: +1.89%

================================================================================
CONTACT
================================================================================

Person 2 (ML Modeling): [Your Name]
Handoff Date: March 31, 2026

For Person 3: Use files in FOR_PERSON3_SHAP/
For Person 4: Use files in FOR_PERSON4_ANOMALY/

================================================================================
"""

with open(BASE / "FINAL_HANDOFF" / "README.txt", 'w', encoding='utf-8') as f:
    f.write(readme_content)

print("   Created: FINAL_HANDOFF/README.txt")

# STEP 5: SUMMARY
print("\n" + "="*80)
print("ORGANIZATION COMPLETE")
print("="*80)

print("""
WHAT TO SEND:
=============

TO PERSON 3 (SHAP):
  → Send: FINAL_HANDOFF/FOR_PERSON3_SHAP/
  Contains: Model + test data + usage guide

TO PERSON 4 (ANOMALY):
  → Send: FINAL_HANDOFF/FOR_PERSON4_ANOMALY/
  Contains: Model + test data + usage guide

FOR FYP REPORT:
  → Use: FINAL_HANDOFF/DOCUMENTATION/
  Contains: All comparison tables and summaries

WHAT YOU CAN DELETE (if needed):
================================
  - archive/           (old/redundant files)
  - .venv-1/           (if still exists)
  - catboost_info/     (if still exists)

PROJECT STRUCTURE NOW:
=====================
FY_ML/
├── FINAL_HANDOFF/       ← MAIN DELIVERABLE
│   ├── FINAL_MODEL/
│   ├── FOR_PERSON3_SHAP/
│   ├── FOR_PERSON4_ANOMALY/
│   ├── DOCUMENTATION/
│   └── README.txt
├── scripts/             ← Phase 1 code
├── scripts_v2/          ← Phase 2 code
├── scripts_v3/          ← Phase 3-5 code
├── scripts_v6_final/    ← Phase 6 code (final)
├── outputs/             ← Phase 1 outputs
├── outputs_v2/          ← Phase 2 outputs
├── outputs_v3/          ← Phase 3-4 outputs
├── outputs_v5/          ← Phase 5 outputs
├── outputs_v6_final/    ← Phase 6 outputs (final)
├── data/                ← Original data
├── visualizations/      ← Charts
├── model_backups/       ← Safety backups
└── archive/             ← Old/redundant files
""")

print("Ready for handoff!")
