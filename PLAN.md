# Analytical Project Plan

## Objective

You will receive a dataset. The raw dataset must be placed under `/data/raw/`. Your job is to explore it, discover what business value can be extracted from it, propose a target variable for user approval, build a predictive model only after the target has been approved, and deliver a complete end-to-end analytical solution including an API, a predictive app, a business dashboard, and Docker deployment.

The business analysis and the target variable selection/proposal must be independent processes.

The agent must not select a target variable during Phase 1 or Phase 2. The target variable must be proposed in Phase 3 and explicitly approved by the user before model training begins.

---

## Global Rule for Target Selection

- Phase 1 must not select or propose a final target variable.
- Phase 2 must focus only on business analysis and must not select or propose a target variable.
- Phase 3 must propose the target variable using:
    - the data dictionary,
    - the data quality report,
    - the business analysis.
- The user must explicitly approve the target variable before Phase 4.
- No model may be trained before target approval.

---

## Task List

Use this checklist to execute the project in order. Do not move to the next phase until all blocking tasks for the current phase are completed.

### Project Setup

- [x]  Verify that the raw dataset is available in `/data/raw/`.
- [x]  Create the full project directory structure.
- [x]  Create `requirements.txt`.
- [x]  Create `Makefile` or equivalent run commands.
- [x]  Create `.env.example`.
- [x]  Create `.gitignore`.
- [x]  Verify that the project can be executed from a clean environment.

### Phase 1: Data Audit and Problem Discovery

- [x]  Load and inspect the dataset.
- [x]  Identify basic structure, rows, columns, and data types.
- [x]  Create the data dictionary.
- [x]  Add data source reference if available.
- [x]  Identify missing values, duplicates, constant columns, outliers, and data type issues.
- [x]  Generate basic distributions and initial hypotheses.
- [x]  Identify relevant business problems or predictive opportunities.
- [x]  Write `/docs/problem_statement.md` without selecting a target variable.
- [x]  Save `/docs/data_dictionary.md`.
- [x]  Save `/docs/json/data_dictionary.json`.
- [x]  Save `/docs/data_quality_report.md`.
- [x]  Confirm that no target variable has been selected in this phase.

### Phase 2: Business Analysis

- [x]  Generate 10 business questions that can be answered with the dataset.
- [x]  Select the 5 most important questions.
- [x]  Justify the selection based on business impact, feasibility, and actionability.
- [x]  Create one Python script per selected question.
- [x]  Generate one Markdown snippet per question.
- [x]  Generate one JSON metrics file per question.
- [x]  Generate one chart per question when applicable.
- [x]  Write `/docs/business_questions.md`.
- [x]  Save `/docs/json/business_questions.json`.
- [x]  Write `/docs/business_analysis_report.md`.
- [x]  Save `/docs/json/insights.json`.
- [x]  Confirm that no target variable has been selected or proposed in this phase.

### Phase 3: Target Variable Proposal

- [x]  Read `/docs/problem_statement.md`.
- [x]  Read `/docs/business_analysis_report.md`.
- [x]  Read `/docs/data_dictionary.md`.
- [x]  Read `/docs/json/data_dictionary.json`.
- [x]  Read `/docs/data_quality_report.md`.
- [x]  Read `/docs/json/insights.json`.
- [x]  Identify candidate target variables.
- [x]  Evaluate candidate variables using business relevance, data quality, leakage risk, availability, and feasibility.
- [x]  Select one recommended target variable.
- [x]  Identify alternative target variables if applicable.
- [x]  Determine the preliminary problem type: classification or regression.
- [x]  Write the business, technical, and data quality justification.
- [x]  Save `/docs/target_proposal.md`.
- [x]  Save `/docs/json/target_proposal.json`.
- [x]  Save `/docs/json/target_approval.json` with approval status set to `pending`.
- [x]  Ask the user to approve, reject, or request changes.
- [x]  Stop execution until the target approval status is `approved`.

### Phase 4: Machine Learning Model

- [x]  Confirm that Phase 3 approval status is `approved`.
- [x]  Load the approved target variable.
- [x]  Confirm whether the problem is classification or regression.
- [x]  Create a baseline model.
- [x]  Split data into training, validation, and test sets.
- [x]  Build preprocessing pipelines.
- [x]  Train candidate models appropriate for the problem type.
- [x]  Evaluate models using cross-validation.
- [x]  Select the best model using a validation metric aligned with the business objective.
- [x]  Evaluate the final model only once on the test set.
- [x]  Analyze feature importance.
- [x]  Save model artifacts.
- [x]  Save model metadata.
- [x]  Write `/docs/model_report.md`.
- [x]  Save `/docs/json/model_performance.json`.
- [x]  Save `/docs/model_card.md`.
- [x]  Save `/docs/json/feature_importance.json`.
- [x]  Save `/docs/images/model_performance_charts.png`.

### Phase 5: Prediction API

- [x]  Create FastAPI application.
- [x]  Implement `/health` endpoint.
- [x]  Implement `/v1/predict` endpoint.
- [x]  Implement `/v1/model-card` endpoint.
- [x]  Add Pydantic input validation.
- [x]  Add error handling.
- [x]  Add logging.
- [x]  Add model versioning.
- [x]  Include prediction explanation and business recommendation in the response.
- [x]  Write API documentation.
- [x]  Save API examples as JSON.
- [x]  Write API tests.

### Phase 6: Predictive App with Streamlit

- [x]  Create Streamlit predictive app.
- [x]  Add input form for prediction.
- [x]  Connect the app to the prediction API.
- [x]  Display predicted probability or predicted value.
- [x]  Display main contributing factors.
- [x]  Display business recommendation.
- [x]  Display warnings for invalid inputs.
- [x]  Write app documentation.

### Phase 7: Business Dashboard with Streamlit

- [x]  Create Streamlit dashboard.
- [x]  Add KPIs.
- [x]  Add charts related to the 5 selected business questions.
- [x]  Add filters by relevant dimensions.
- [x]  Include clear titles and business interpretation.
- [x]  Include recommended actions.
- [x]  Ensure the dashboard answers:
    - What happened?
    - Why did it happen?
    - What should the business do?
- [x]  Write dashboard documentation.

### Deployment

- [x]  Create `Dockerfile`.
- [x]  Create `docker-compose.yml`.
- [x]  Include services for API, predictive app, and dashboard.
- [x]  Create `.env.example` if not already created.
- [x]  Write deployment documentation.
- [x]  Verify that the project runs using Docker from a clean environment.

---

## Phases

### Phase 1: Data Audit and Problem Discovery

Analyze the dataset and create a data dictionary. Add the data source reference if possible.

This phase is exploratory and diagnostic. It must not select, define, or propose a final target variable.

Deliverables:

- `/docs/data_dictionary.md`
- `/docs/json/data_dictionary.json`
- `/docs/data_quality_report.md`
- `/docs/problem_statement.md`

The data dictionary must include:

- Column name, description, data type
- Possible values, missing values, unique values
- Example values, business meaning
- Whether the column can be used as a feature
- Whether the column could be considered as a candidate target in Phase 3
- Whether the column has potential data leakage

The data quality report must include:

- Number of rows and columns
- Missing values by column
- Duplicated rows
- Constant columns
- Data type issues
- Outliers
- Class imbalance, if applicable
- Basic distributions
- Initial hypotheses

The problem statement must include:

- What business problem or problems were identified as the most relevant
- Why the main problem was chosen over others
- Candidate business opportunities or predictive opportunities
- What business metric is expected to be impacted
- Candidate problem types, if applicable, only as preliminary hypotheses
- Possible candidate variables for future target analysis, without selecting or ranking them
- Explicit statement that no target variable has been selected in this phase

Restrictions for this phase:

- Do not select a target variable.
- Do not define a final modeling target.
- Do not start model training.
- Do not make final decisions about classification or regression.

---

### Phase 2: Business Analysis

Perform a business-oriented analysis of the data.

This phase is independent from target selection. Its purpose is to understand the business value that can be extracted from the dataset, generate business questions, and produce data-backed insights.

Tasks:

1. Generate 10 business questions that can be answered using the dataset.
2. Select the 5 most important questions based on business impact, feasibility and actionability.
3. Answer each selected question with code.
4. Justify every insight with code, charts, metrics and written interpretation.

Deliverables:

- `/docs/business_questions.md`
- `/docs/json/business_questions.json`
- `/docs/business_analysis_report.md`
- `/docs/json/insights.json`
- One Python script per question inside `/scripts`
- Markdown snippets inside `/docs/snippets`
- JSON metrics inside `/docs/json`
- Chart images inside `/docs/images`

Script naming convention:

```bash
/scripts/q01_<short_description>.py
/scripts/q02_<short_description>.py
/scripts/q03_<short_description>.py
/scripts/q04_<short_description>.py
/scripts/q05_<short_description>.py
```

Output convention per question:

```bash
/docs/snippets/q01_output.md
/docs/json/q01_metrics.json
/docs/images/q01_chart.png
```

Each insight must contain:

- Question
- Business relevance
- Code used
- Output
- Interpretation
- Recommended action

Restrictions for this phase:

- Do not select a target variable.
- Do not propose a final target variable.
- Do not define the final machine learning target.
- Do not train predictive models.

The outputs of this phase must be used as business input for the target proposal in Phase 3.

---

### Phase 3: Target Variable Proposal

Propose the target variable to the user. This phase must not train models.

The agent must use the following inputs:

- `/docs/data_dictionary.md`
- `/docs/json/data_dictionary.json`
- `/docs/data_quality_report.md`
- `/docs/problem_statement.md`
- `/docs/business_analysis_report.md`
- `/docs/json/insights.json`
- The dataset located in `/data/raw/`, or `/data/processed/` if available

Tasks:

1. Review the business problem identified in Phase 1.
2. Review the business insights generated in Phase 2.
3. Review the data dictionary and the data quality report.
4. Identify possible candidate variables that could be used as the target.
5. Evaluate each candidate variable using the following criteria:
    - Alignment with the business problem
    - Business relevance
    - Actionability
    - Availability at prediction time
    - Data quality
    - Missing values
    - Data type consistency
    - Reliability of the variable definition
    - Presence of outliers or inconsistent values
    - Class imbalance, if applicable
    - Potential data leakage
    - Temporal consistency
    - Ethical or legal restrictions
    - Feasibility for machine learning
6. Select one recommended target variable.
7. Optionally list alternative target variables.
8. Determine the preliminary problem type:
    - classification
    - regression
9. Explain why the recommended target is the best option.
10. Present the proposal to the user and request explicit approval.
11. Do not continue to Phase 4 until the user approves the target variable.

Deliverables:

- `/scripts/02_target_proposal.py`
- `/docs/target_proposal.md`
- `/docs/json/target_proposal.json`
- `/docs/json/target_approval.json`

The target proposal document must include:

- Recommended target variable
- Alternative target variables, if applicable
- Preliminary problem type
- Business justification
- Technical justification
- Data quality justification
- Evidence from the data dictionary
- Evidence from the data quality report
- Evidence from the business analysis
- Assumptions
- Risks
- Limitations
- Data leakage checks
- Open questions for the user
- Approval status

The target proposal JSON must include at least:

```json
{
  "recommended_target": "",
  "alternative_targets": [],
  "problem_type": "",
  "business_justification": "",
  "technical_justification": "",
  "data_quality_justification": "",
  "data_dictionary_evidence": "",
  "data_quality_evidence": "",
  "business_analysis_evidence": "",
  "assumptions": [],
  "risks": [],
  "limitations": [],
  "data_leakage_checks": [],
  "open_questions": [],
  "approval_status": "pending_user_approval"
}
```

The target approval JSON must include at least:

```json
{
  "approved_target": null,
  "approved_problem_type": null,
  "approval_status": "pending",
  "user_comments": "",
  "approval_timestamp": null
}
```

Possible approval statuses:

- `pending`
- `approved`
- `rejected`
- `changes_requested`

Restrictions for this phase:

- Do not train models.
- Do not create final features.
- Do not assume the target has been approved.
- Do not continue to Phase 4 without explicit user approval.
- If no suitable target variable can be proposed, report the blockers and ask the user for additional data, clarification, or problem redefinition.

---

### Phase 4: Machine Learning Model

Train a predictive model based on the target variable approved in Phase 3.

This phase must only start if the target approval status is `approved`.

Tasks:

1. Confirm that the target variable was approved in Phase 3.
2. Determine whether the problem is classification or regression based on the approved target and the business analysis. Justify the decision in the model report.
3. Create a baseline model.
4. Split data into training, validation and test sets.
5. Build preprocessing pipelines.
6. Train candidate models appropriate for the problem type:
    - For regression: Linear Regression, Decision Tree Regressor, Random Forest Regressor
    - For classification: Logistic Regression, Decision Tree Classifier, Random Forest Classifier
7. Evaluate models using cross-validation.
8. Select the best model using a validation metric aligned with the business objective.
9. Evaluate the final model only once on the test set.
10. Analyze feature importance using a robust method such as permutation importance or SHAP.
11. Save model artifacts and metadata.

Deliverables:

- `/scripts/train_baseline.py`
- `/scripts/train_candidate_models.py`
- `/scripts/evaluate_final_model.py`
- `/models/final_model.joblib`
- `/models/preprocessor.joblib`
- `/models/model_metadata.json`
- `/docs/model_report.md`
- `/docs/json/model_performance.json`
- `/docs/model_card.md`
- `/docs/json/feature_importance.json`
- `/docs/images/model_performance_charts.png`

The model report must include:

- Problem definition
- Approved target variable
- Reference to the target approval from Phase 3
- Justification for classification vs regression
- Train/validation/test split
- Preprocessing steps
- Models tested
- Metrics for each model
- Selected model and why
- Final test performance
- Feature importance
- Limitations
- Risks
- Next steps

For classification, include:

- Accuracy, Precision, Recall, F1-score
- ROC-AUC
- PR-AUC if imbalanced
- Confusion matrix
- Calibration if probabilities are important

For regression, include:

- MAE, RMSE, MAPE, R²

The model metadata must include at least:

- Model name
- Model version
- Approved target variable
- Problem type
- Target approval reference
- Training timestamp
- Feature list
- Preprocessing summary
- Validation metrics
- Test metrics
- Library versions
- Notes and limitations

Restrictions for this phase:

- Do not train a model if the target variable has not been approved.
- Do not change the approved target variable without restarting or updating Phase 3.
- Do not evaluate the final model multiple times on the test set.

---

### Phase 5: Prediction API

Expose the trained model through an API using FastAPI.

API requirements:

- `/health` endpoint
- `/v1/predict` endpoint
- `/v1/model-card` endpoint
- Input validation with Pydantic
- Error handling
- Logging
- Model versioning

Prediction output must include:

- Predicted probability or predicted value
- Main contributing factors
- Risk level or business outcome
- Business recommendation
- Model version
- Timestamp

Deliverables:

- `/src/api/main.py`
- `/src/api/schemas.py`
- `/src/api/predict.py`
- `/docs/api_documentation.md`
- `/docs/json/api_examples.json`
- `/tests/test_api.py`

---

### Phase 6: Predictive App with Streamlit

Build a predictive application using Streamlit.

The app must:

- Provide a form for entering observation values
- Call the prediction API
- Show the predicted probability or predicted value
- Show the main factors influencing the prediction
- Show a business recommendation
- Display warnings if input values are invalid

Deliverables:

- `/apps/predict_app/app.py`
- `/docs/predict_app_documentation.md`

---

### Phase 7: Business Dashboard with Streamlit

Build a dashboard to communicate the business insights from Phase 2.

The dashboard must include:

- KPIs
- Charts related to the 5 selected business questions
- Filters by relevant dimensions
- Clear titles
- Business interpretation
- Recommended actions

The dashboard must not only show charts. It must answer:

- What happened?
- Why did it happen?
- What should the business do?

Deliverables:

- `/apps/dashboard/app.py`
- `/docs/dashboard_documentation.md`

---

## Directory Structure

```bash
project/
│
├── README.md
├── PLAN.md
├── requirements.txt
├── Makefile
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── .gitignore
│
├── data/
│   ├── raw/
│   ├── processed/
│   └── external/
│
├── configs/
│   ├── project_config.json
│   └── model_config.json
│
├── scripts/
│   ├── 00_data_audit.py
│   ├── 01_create_data_dictionary.py
│   ├── 02_target_proposal.py
│   ├── q01_<description>.py
│   ├── q02_<description>.py
│   ├── q03_<description>.py
│   ├── q04_<description>.py
│   ├── q05_<description>.py
│   ├── train_baseline.py
│   ├── train_candidate_models.py
│   └── evaluate_final_model.py
│
├── src/
│   ├── __init__.py
│   ├── data/
│   ├── features/
│   ├── model/
│   └── api/
│       ├── __init__.py
│       ├── main.py
│       ├── schemas.py
│       └── predict.py
│
├── apps/
│   ├── predict_app/
│   │   └── app.py
│   └── dashboard/
│       └── app.py
│
├── models/
│   ├── final_model.joblib
│   ├── preprocessor.joblib
│   └── model_metadata.json
│
├── tests/
│   ├── test_data.py
│   ├── test_model.py
│   └── test_api.py
│
└── docs/
    ├── data_dictionary.md
    ├── data_quality_report.md
    ├── problem_statement.md
    ├── business_questions.md
    ├── business_analysis_report.md
    ├── target_proposal.md
    ├── model_report.md
    ├── model_card.md
    ├── api_documentation.md
    ├── predict_app_documentation.md
    ├── dashboard_documentation.md
    ├── deployment_documentation.md
    │
    ├── snippets/
    │   ├── q01_output.md
    │   ├── q02_output.md
    │   ├── q03_output.md
    │   ├── q04_output.md
    │   └── q05_output.md
    │
    ├── json/
    │   ├── data_dictionary.json
    │   ├── business_questions.json
    │   ├── insights.json
    │   ├── q01_metrics.json
    │   ├── q02_metrics.json
    │   ├── q03_metrics.json
    │   ├── q04_metrics.json
    │   ├── q05_metrics.json
    │   ├── target_proposal.json
    │   ├── target_approval.json
    │   ├── model_performance.json
    │   ├── feature_importance.json
    │   └── api_examples.json
    │
    └── images/
        ├── q01_chart.png
        ├── q02_chart.png
        ├── q03_chart.png
        ├── q04_chart.png
        ├── q05_chart.png
        └── model_performance_charts.png
```

---

## Deployment

Package the project using Docker.

Deliverables:

- `Dockerfile`
- `docker-compose.yml`
- `.env.example`
- `/docs/deployment_documentation.md`

The `docker-compose.yml` must include services for:

- API
- Predictive app
- Dashboard

---

## Requirements

- All project documentation and code comments must be in English.
- No Jupyter notebooks. Use Python scripts, Markdown files and JSON files only.
- Every insight must be justified with code.
- All markdown reports go in `/docs`.
- All markdown snippets go in `/docs/snippets`.
- All JSON files go in `/docs/json`.
- All image files go in `/docs/images`.
- No mixing of file types inside the same folder.
- The project must be reproducible u sing Docker.
- The API must include input validation and error handling.
- The model must be persisted with metadata.
- Include `requirements.txt` with pinned dependencies.
- Include a `Makefile` or clear run commands.
- Include basic tests.
- Include `.env.example` and `.gitignore`.
- The project must be executable from a clean environment.
- The business analysis and target selection/proposal must be independent processes.
- The target variable must not be selected in Phase 1 or Phase 2.
- The target variable must be proposed in Phase 3 using the data dictionary, the data quality report, and the business analysis.
- The target variable must be explicitly approved by the user before model training.
- No model training may begin before Phase 3 approval is recorded.