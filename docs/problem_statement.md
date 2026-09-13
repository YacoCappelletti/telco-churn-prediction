# Problem Statement - Telco Customer Churn Dataset

> Phase 1 deliverable · Generated from `data/raw/Telco-Customer-Churn.csv` (7,043 customers × 21 columns) · See also: `data_dictionary.md`, `data_quality_report.md`, `json/data_quality_metrics.json`

## 1. Business context

The dataset is a full snapshot of a telecom operator's customer base (IBM Telco
Customer Churn sample dataset). For each customer it records:

- **Who they are** - demographics (`gender`, `SeniorCitizen`, `Partner`, `Dependents`)
- **What they bought** - services (`PhoneService`, `MultipleLines`, `InternetService`, six add-on services)
- **How they are contracted and billed** - `Contract`, `PaperlessBilling`, `PaymentMethod`
- **What they pay** - `MonthlyCharges`, `TotalCharges`, `tenure`
- **An outcome flag** - `Churn` (Yes = 26.54% of the base)

The business context implied by this structure is a **subscription business
with material monthly customer attrition**: roughly one in four customers in
the snapshot is recorded as churned. In subscription telecom, acquiring a new
customer typically costs several times more than retaining an existing one, so
unmanaged churn directly erodes recurring revenue (≈ $64.76 mean monthly
charge per customer) and lifetime value.

## 2. Business problems identified

### P1. Customer churn is material and concentrated (primary problem)

26.54% of the customer base (1,869 of 7,043 customers) is flagged as churned.
This is the largest, most directly measurable value leak in the dataset: every
churned customer takes their recurring monthly payment out of the revenue base.
The dataset contains rich pre-outcome context (contract, services, payment,
tenure, charges) that plausibly explains *why* customers leave - making this
problem both diagnosable (descriptive) and predictable (predictive).

### P2. Revenue exposure is quantifiable but not yet localized

The base generates roughly $456K in monthly recurring revenue (7,043 × $64.76
mean). Knowing *which segments* (contract type, service mix, payment method,
tenure band) concentrate the churned customers would let retention budget be
allocated where revenue risk is highest, instead of uniformly.

### P3. The new-customer window appears fragile

`tenure` has a visible spike at 0-3 months, and the 11 zero-tenure customers
are all brand-new (first-invoice only). If early-tenure customers churn at
materially different rates, onboarding and first-contract design become
actionable levers.

### P4. Pricing/product-mix friction signals

Fiber optic carries a median monthly charge of $91.68 vs $56.15 for DSL, and
33.58% of customers pay via electronic check (a manual, non-recurring method).
Both are classic friction/expectation-gap signals worth validating against the
outcome flag.

## 3. Why P1 (churn) is chosen as the primary problem

- **Business impact:** churn attacks recurring revenue at the customer level;
  with ~$456K MRR in the snapshot and 26.5% flagged churn, the exposure is
  large and quantifiable from the data itself.
- **Measurability:** the outcome flag makes the problem fully observable in
  this dataset; no external data is required.
- **Actionability:** the feature set (contract, services, payment method,
  tenure, charges) maps directly to levers the business controls - contract
  migration offers, bundle design, payment-method incentives, onboarding.
- **Predictability potential:** the mix of behavioral, contractual, and price
  variables supports both retrospective analysis and forward-looking scoring.

P2-P4 are treated as **supporting analyses**: they sharpen the churn problem
(where the risk sits, which levers exist) and will be developed as business
questions in Phase 2.

## 4. Business metric expected to be impacted

- **Primary:** churn rate (share of customers leaving in the period) -
  targeted for reduction in the highest-risk segments.
- **Secondary:** monthly recurring revenue retained (sum of `MonthlyCharges`
  over customers prevented from churning), and revenue-weighted retention
  efficiency of any intervention budget.

## 5. Candidate problem types (preliminary hypotheses only)

- **Binary classification** - if the outcome flag is modeled, the natural task
  is classifying customers by the Yes/No flag, ideally outputting a risk
  probability to rank retention actions.
- **Regression / survival-style duration modeling** - `tenure` could support a
  retention-duration view; weaker actionability, kept only as a preliminary
  hypothesis.
- **Descriptive segmentation** - even without modeling, segment-level churn
  and revenue-at-risk analysis (Phase 2) already yields actionable insight.

These are *hypotheses only*. No problem type is decided in this phase.

## 6. Possible candidate variables for future target analysis (unranked)

Columns that could plausibly play an outcome role and therefore merit formal
evaluation in Phase 3 (flagged, **not ranked or selected**, in
`data_dictionary.md`):

- `Churn` - the only Yes/No outcome-like flag in the dataset.
- `tenure` - retention-duration candidate.
- `MonthlyCharges` / `TotalCharges` - price / accumulated-value candidates.

The final choice among them - or none of them - is a Phase 3 decision and
requires explicit user approval before any modeling.

## 7. Explicit Phase 1 compliance statement

**No target variable has been selected, defined, ranked, or proposed in this
phase.** No model has been trained. The observations above are exploratory
hypotheses to be refined by the Phase 2 business analysis and formalized by
the Phase 3 target proposal with user approval.
