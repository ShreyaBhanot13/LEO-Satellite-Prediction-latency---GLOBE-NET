***

# **CHAPTER - 6**

# **SYSTEM TESTING**

***

## **6.1 Introduction to System Testing**

System testing was carried out to ensure that the proposed machine learning pipeline, analytical modules, and interactive dashboard operate correctly both as independent components and as a complete integrated system. In this project, testing was not limited to checking whether the code executes successfully. It also focused on the **correctness, reliability, performance, interpretability, and usability** of the overall solution. Since the system includes data preprocessing, feature engineering, model training, anomaly detection, explainability analysis, zone-level classification, and live dashboard scoring, each stage had to be validated individually as well as in relation to the other stages.

***

## **6.2 Types of Testing Performed**

### **6.2.1 Unit Testing**

Unit testing in this project refers to validating whether each major module performs its own intended function correctly before being connected to later stages. Although the project was not developed with a traditional software unit-test framework, each analytical module was individually executed and checked for correctness.

Examples of unit-level validation include the confirmation that missing values were handled correctly during preprocessing, engineered features were created successfully during feature engineering, regression and classification models completed training without runtime errors, and explainability outputs were generated for the selected models. The anomaly-detection stage was also tested independently to ensure that residual computation and high-risk flag generation were functioning as expected.

**Examples from the project:**

* Data preprocessing correctly cleaned invalid and incomplete records
* Feature engineering correctly produced derived, transformed, and contextual variables
* Model-training modules executed successfully for regression and classification tasks
* Explainability outputs were produced successfully for the selected models
* Zone aggregation correctly formed spatial groups before risk classification

### **6.2.2 Integration Testing**

Integration testing was performed to verify the interaction between modules and to ensure that the output of one stage was accepted correctly by the next stage. This was essential because the project follows an artifact-driven pipeline in which processed data, trained models, summaries, and predictions are reused across multiple analytical stages.

The preprocessing outputs were verified before being passed into feature engineering, engineered datasets were checked before being supplied to the machine learning models, and model outputs were then tested for reuse in explainability analysis, anomaly detection, zone-risk analysis, and dashboard presentation. The live scoring component of the dashboard also served as an integration test because it reconstructed the required model inputs and verified that the saved trained model could accept them correctly.

**Examples from the project:**

* Cleaned data were successfully used by feature engineering modules
* Engineered feature sets were accepted correctly by regression and classification models
* Model outputs were successfully reused in anomaly detection and explainability stages
* Zone-level summaries were successfully integrated into the visualization and dashboard layer
* Live dashboard scoring remained consistent with the trained classifier schema

### **6.2.3 Functional Testing**

Functional testing was carried out to confirm that the system performs the tasks for which it was designed. This means verifying that prediction modules, anomaly-detection logic, explainability summaries, and the dashboard interface all produce the intended outputs.

The regression models were tested to verify that they produce latency predictions, the classification models were tested to verify that they assign risk labels correctly, the anomaly-detection stage was tested to ensure that abnormal cases were prioritized according to the defined rules, and the dashboard was tested to ensure that it displayed outputs in a meaningful and interactive form.

**Examples from the project:**

* Regression models generated latency predictions for unseen data
* High-latency classifiers produced class labels and risk scores
* Zone-level classifiers correctly categorized areas into high-risk and low-risk groups
* Explainability outputs provided interpretable model insights
* The dashboard displayed state-wise, regional, and live-scoring results correctly

### **6.2.4 Model Validation Testing**

Model validation testing is one of the most important parts of the project because it demonstrates whether the trained machine learning models are accurate and generalizable. Regression models were evaluated using **RMSE, MAE, and $R^2$**, while classification models were evaluated using **accuracy, balanced accuracy, precision, recall, F1 score, and confusion matrices**.

The benchmark regression stream showed strong performance improvement across successive optimization phases, eventually reaching a final benchmark result of **$R^2 = 0.8156$**, **RMSE = 0.4217**, and **MAE = 0.3026**. In the India-focused branch, direct latency regression was comparatively weak, with **$R^2 = 0.0810$**, indicating that exact point prediction was not sufficiently reliable on the available feature set. The binary high-latency classifier performed better as a screening tool, with **accuracy = 0.7496**, **balanced accuracy = 0.7124**, and **recall = 0.6655**. The strongest project-specific predictive model was the zone-level CatBoost classifier, which achieved **accuracy = 0.8031**, **balanced accuracy = 0.7283**, and **macro F1 = 0.7298**.

Table 1 summarizes the most important model-validation results.

| Model or Task | Key Validation Result | Interpretation |
|---|---|---|
| Final benchmark ensemble | R² = 0.8156, RMSE = 0.4217, MAE = 0.3026 | Strong final regression performance |
| India latency regression | R² = 0.0810, RMSE = 44.1730 ms, MAE = 14.7069 ms | Weak exact latency prediction |
| Binary high-latency classifier | Accuracy = 0.7496, Balanced Accuracy = 0.7124, Recall = 0.6655 | Useful for screening high-risk conditions |
| Zone-risk CatBoost classifier | Accuracy = 0.8031, Balanced Accuracy = 0.7283, Macro F1 = 0.7298 | Best practical model for regional risk detection |

### **6.2.5 Performance Testing**

Performance testing was used to assess whether the system could handle large datasets efficiently and produce outputs within a practical time frame. This was especially important because the project includes large-scale telecom records, repeated model training, summary generation, and dashboard interaction.

The offline analytical pipeline was tested to ensure that preprocessing, feature construction, training, and summary generation completed successfully on the available dataset sizes. The saved-model approach also improved performance by avoiding retraining during dashboard use. In the interactive layer, testing confirmed that the dashboard remained responsive because it only loaded validated outputs and applied live scoring through a pre-trained model rather than executing the full training pipeline.

**Examples from the project:**

* Large benchmark and India datasets were processed without pipeline failure
* Trained models generated predictions on test data successfully
* Dashboard interaction remained lightweight because it used saved outputs
* Live scoring was executed through a stored model rather than full retraining

### **6.2.6 Usability Testing**

Usability testing focused on the dashboard interface, since it is the main interaction point for users, evaluators, and service providers. The aim was to ensure that the interface was understandable, that the inputs were meaningful, and that the displayed outputs were easy to interpret.

Testing confirmed that users could navigate between different views such as benchmark context, India summaries, Karnataka-focused findings, and live scoring. The dashboard inputs were designed in a simplified form so that users did not need to enter the full training schema manually. The outputs were displayed through readable charts, summaries, and classifications, making the system suitable for demonstration and interpretation.

**Usability observations include:**

* Interface sections were organized clearly for different analytical goals
* User inputs for live scoring were simplified and understandable
* Output visuals and summaries were readable and meaningful
* The dashboard supported interactive exploration rather than static reporting only

### **6.2.7 Data Validation Testing**

Data validation testing was especially important in this project because the quality of the machine learning outputs depends directly on the correctness of the data pipeline. Validation checks were applied to ensure that no leakage occurred, train-test separation was maintained correctly, and transformed targets were handled consistently.

During preprocessing and dataset preparation, missing values and invalid values were checked and corrected. During feature engineering, derived features were validated to prevent unstable values. In the India-focused branch, target-derived leakage was removed explicitly before training. In the benchmark branch, the target transformation process was also validated to ensure that transformed values were converted back correctly to the original scale during evaluation.

**Examples from the project:**

* Missing and invalid values were detected and cleaned before training
* Data leakage was prevented by excluding target-derived information from predictors
* Train-test split consistency was maintained for fair evaluation
* Target transformations were correctly reversed before final reporting
* Zones with insufficient support were excluded to reduce statistical instability

***

## **6.3 Test Cases**

Table 2 presents representative test cases used to validate the major stages of the system.

| Test Case ID | Description | Input | Expected Output | Result |
|---|---|---|---|---|
| TC01 | Data cleaning and preprocessing | Raw benchmark and telecom datasets | Cleaned and validated datasets | Pass |
| TC02 | Feature engineering validation | Cleaned dataset | Engineered features created successfully | Pass |
| TC03 | Regression model execution | Training and test data | Latency predictions and evaluation metrics | Pass |
| TC04 | Classification model execution | Engineered feature dataset | Risk labels and classifier metrics | Pass |
| TC05 | Anomaly-detection logic | Regression outputs and classifier risk flags | Prioritized anomaly cases and summaries | Pass |
| TC06 | Zone aggregation and classification | Spatially grouped zone data | High-risk and low-risk zone labels | Pass |
| TC07 | Dashboard live scoring | User inputs and saved model | Real-time prediction and displayed output | Pass |

***

## **6.4 Testing Results**

The testing results show that the overall system performed successfully across its major modules. The preprocessing and feature-engineering stages generated valid datasets, the machine learning models executed correctly, and the downstream analytical stages such as explainability analysis, anomaly detection, and zone-risk classification produced meaningful outputs. The interactive dashboard also displayed the required summaries, charts, and live-scoring outputs as expected.

From a model-performance perspective, the benchmark stream showed strong regression quality, the India regression task was found to be relatively weak, the binary classifier proved useful as a screening mechanism, and the zone-level classifier emerged as the most operationally effective predictive component. These testing outcomes were important because they guided the final project emphasis toward explainability, anomaly detection, and zone-level risk classification rather than over-relying on weak exact regression in the India branch.

A project-specific validation step was also carried out to strengthen the reliability of the final solution. SHAP explanations were verified to ensure that the important predictors were interpretable and consistent with the domain context. Residual-based anomaly detection was validated by confirming that anomaly prioritization depended on both regression underperformance and high-risk classification rather than on a single signal. Zone aggregation was checked to ensure that geographic grouping and support thresholds produced meaningful regional units. In addition, live dashboard scoring was validated against the trained model schema so that the interactive predictions remained consistent with the offline training pipeline.

***

## **6.5 Error Handling**

Error handling was incorporated into the system to ensure that invalid or incomplete conditions were managed safely. In the data pipeline, missing values and unstable derived values were detected and corrected before model training. In the modeling stages, train-test consistency and transformed-target recovery were checked to prevent misleading evaluation results. In the dashboard layer, required inputs were verified before display and feature reconstruction was protected against invalid user conditions such as unsafe ratio calculations.

The system therefore does not rely only on successful execution; it also includes safeguards that prevent silent failure or inconsistent outputs. This improves system reliability and demonstrates a more mature implementation approach.

**Examples of error handling include:**

* Missing data handled through preprocessing and validation checks
* Invalid derived values corrected before model training
* Leakage-prone inputs excluded from the predictive feature set
* Dashboard logic protected against inconsistent or incomplete inputs
* Live-scoring inputs converted into the correct model-ready structure before inference

***

## **6.6 Summary of Testing**

In summary, system testing confirmed that the proposed solution functions correctly as a machine learning pipeline, analytical framework, and interactive dashboard. The individual modules were validated, the integration between stages was verified, and the trained models were evaluated using appropriate statistical and performance-based measures. The testing process also confirmed that anomaly detection, explainability analysis, zone-risk classification, and live scoring behaved in a reliable and interpretable manner.

Overall, the testing results show that the system is **correct, reliable, usable, and operationally meaningful**. While some predictive tasks such as India latency regression remain limited, the full system performs satisfactorily for the final project objective and provides a strong, well-validated foundation for telecom risk analysis and interactive decision support.

***