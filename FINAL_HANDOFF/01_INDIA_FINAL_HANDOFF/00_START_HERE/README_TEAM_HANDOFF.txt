INDIA ZONE-RISK TEAM HANDOFF
========================================

IMPORTANT:
Use this folder as the current final handoff package.
Do not use the older FINAL_HANDOFF root package for the final India-first model,
because that older package contains previous regression-era artifacts.

FINAL PROJECT FRAMING:
- Task: High-risk internet performance zone classification in India
- Final model: CatBoostClassifier
- Final baseline dataset: zone-level India dataset
- Final baseline metrics:
  - Accuracy: 0.8031
  - Balanced accuracy: 0.7283
  - High-risk F1: 0.5892

TOP-LEVEL FOLDERS:
- 01_INDIA_FINAL_MODEL_BASELINE
  Main final baseline package for everyone. Contains final dataset, model, train/test splits, results, reports, and core scripts.

- 02_PERSON3_XAI_HANDOFF
  Give this directly to the Explainable AI person.

- 03_PERSON4_ANOMALY_HANDOFF
  Give this directly to the anomaly detection / risk analysis person.

- 04_INDIA_OPERATOR_CONTEXT_OPTIONAL
  Supplementary operator-context experiment files. These are not the final model.

- 05_FOREIGN_GERMANY_NETHERLANDS_REFERENCE
  Separate foreign-data reference bundle containing the older Germany/Netherlands datasets and Europe benchmark model artifacts.

INTENTIONALLY EXCLUDED FOR NOW:
- UI / dashboard / final presentation packaging
  These are not separated into an individual handoff folder because the team will build and present that part together.

RECOMMENDED TEAM FLOW:
1. Everyone should first look at 01_INDIA_FINAL_MODEL_BASELINE.
2. Person 3 should then use 02_PERSON3_XAI_HANDOFF.
3. Person 4 should then use 03_PERSON4_ANOMALY_HANDOFF.
4. Use 04_INDIA_OPERATOR_CONTEXT_OPTIONAL only as a supplementary telecom-context reference.
5. Use 05_FOREIGN_GERMANY_NETHERLANDS_REFERENCE only if someone needs the older Europe/global benchmark materials.
6. UI and presentation work should be done together from the main repo when the team is ready.
