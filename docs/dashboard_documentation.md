# Dashboard Documentation - Telco Customer Churn

> Phase 7 deliverable · App: `apps/dashboard/app.py` · Run: `make dashboard` (Streamlit, port 8501 default)

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

Each section shows the chart, the key numbers from the Phase 2 metrics
(`docs/json/q0*_metrics.json`), an **Interpretation** paragraph and a
**Recommended action**.

## 4. Filters

Sidebar filters apply to the KPIs and all charts (computed live from the raw
dataset with the documented TotalCharges cleaning rule):

- **Contract type** (multi-select)
- **Internet service** (multi-select)
- **Payment method** (multi-select)
- **Max tenure** (slider 1-72)

A warning appears when the filter leaves fewer than 50 customers.

## 5. Data and provenance

- Data: `data/raw/Telco-Customer-Churn.csv` loaded via the documented cleaning
  rule (11 blank TotalCharges → tenure × MonthlyCharges).
- Narrative text: `docs/json/insights.json` (Phase 2).
- Segment benchmarks quoted in interpretations come from the Phase 2 scripts
  (`scripts/q0*.py`), so the full-data numbers stay reproducible.
- Cross-sectional caveat is displayed in the footer: correlations are not
  causal effects.

## 6. How to run

```bash
make dashboard   # Streamlit on :8501
```

In Docker Compose the dashboard runs as its own service (`docker compose up`,
dashboard on port 8502 host-side).
