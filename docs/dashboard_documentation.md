# Dashboard Documentation - Telco Customer Churn

> Phase 7 deliverable · App: `apps/dashboard/app.py` · Run: `make dashboard` (Streamlit, port 8501 by default — use a different port if the predict app is running on 8501, e.g. `streamlit run apps/dashboard/app.py --server.port 8502`; in Docker Compose it is served on host port 8512)

## 1. Purpose

A business-facing dashboard that communicates the Phase 2 insights. It is not
just charts: every section pairs evidence with interpretation and a
recommended action, and the executive summary answers the three required
questions:

- **What happened?** 26.5% of the base churned, taking 30.5% of MRR
  ($139K/mo ≈ $1.67M annualized) with it; risk concentrates in
  month-to-month contracts, the first year of tenure, unprotected fiber users
  and manual-payment customers.
- **Why did it happen?** Four compounding mechanisms visible in the data:
  exit-cost asymmetry (contract), lifecycle fragility (tenure spike at month
  1), premium-product expectation gap (fiber at 2.2x DSL churn), and monthly
  re-authorization friction (electronic check).
- **What should the business do?** Four levers in priority order:
  1. Contract migration for month-to-month accounts.
  2. 90-day onboarding program for customers < 1 year.
  3. Fiber quality investigation + protection bundling.
  4. A/B-tested migration from electronic check to automatic payments.
  Retention spend weighted by monthly revenue at risk.

![Business dashboard - KPIs and executive summary](images/ui_dashboard_overview.png)
*Filtered KPIs and the global Phase-2 executive summary.*

![Business dashboard - Q1 churn by contract](images/ui_dashboard_question.png)
*Per-question section: live chart + interpretation that follows the sidebar filters + recommended action.*

## 2. KPIs (respond to filters)

| KPI | Definition |
| --- | ---------- |
| Customers | Count in the filtered base |
| Churn rate | Churned share of the filtered base |
| Monthly revenue (MRR) | Sum of MonthlyCharges |
| MRR at risk | MRR held by churned customers |
| ARPU churned vs retained | Mean bill of churned vs retained |

## 3. Sections (the 5 selected business questions)

| Section | Chart (live, respects filters) | Business lever |
| ------- | ------------------------------ | -------------- |
| Q1 · Churn by contract type | Churn rate by Contract | Contract-migration program |
| Q2 · Lifecycle | Churn rate by tenure bucket | 90-day onboarding |
| Q3 · Services & add-ons | By internet type + protection tier | Fiber quality + bundling |
| Q4 · Revenue at risk | Churned MRR by price band | Revenue-weighted budget |
| Q5 · Payment friction | Churn rate by payment method | Payment migration A/B |

Each section shows the chart and an **Interpretation** paragraph whose key
numbers are computed **live from the filtered base** (they follow the sidebar
filters), plus a **Recommended action**. The Phase 2 metrics files
(`docs/json/q0*_metrics.json`) remain the reproducible benchmark for the
full, unfiltered dataset.

## 4. Filters

Sidebar filters apply to the KPIs and all charts (computed live from the raw
dataset with the documented TotalCharges cleaning rule):

- **Contract type** (multi-select)
- **Internet service** (multi-select)
- **Payment method** (multi-select)
- **Max tenure** (slider 1-72)

A warning appears when the filter leaves fewer than 50 customers, and an
error banner appears when no customers match the filters (charts and
per-question interpretations are hidden in that case).

## 5. Data and provenance

- Data: `data/raw/Telco-Customer-Churn.csv` loaded via the documented cleaning
  rule (11 blank TotalCharges → tenure × MonthlyCharges).
- Narrative text: `docs/json/insights.json` (Phase 2) — used only for the
  Executive summary, which is the **global Phase-2 synthesis** and is labeled
  as not affected by the sidebar filters.
- Per-question interpretations: computed live from the filtered base (same
  tenure-bucket edges as the Phase 2 script `scripts/q02_tenure_vs_churn.py`),
  so chart and text always agree.
- Cross-sectional caveat is displayed in the footer: correlations are not
  causal effects.

## 6. How to run

```bash
make dashboard   # Streamlit on :8501
```

In Docker Compose the dashboard runs as its own service (`docker compose up`,
dashboard on port 8502 host-side).
