## Q02 - Output: Churn rate by tenure bucket

**Question:** How does churn risk change across the customer lifecycle, and where does risk concentrate?
**Code:** `scripts/q02_tenure_vs_churn.py`

### Output

| Tenure bucket (months) | Customers | Churn rate |
| --- | --- | --- |
| **0-6** | 1601 | 52.2% |
| **7-12** | 683 | 35.1% |
| **13-24** | 994 | 28.1% |
| **25-48** | 1581 | 20.1% |
| **49-60** | 842 | 13.4% |
| **61-72** | 1331 | 6.4% |

- Median tenure of churned customers: **10 months** vs **38 months** for retained customers.
- Customers in their first 12 months: 2,186 - they account for **55.5%** of all churned customers.
- A striking 613 customers sit at exactly 1 month of tenure - the onboarding cliff.
- Chart: `docs/images/q02_chart.png` · Metrics: `docs/json/q02_metrics.json`

### Interpretation

Churn risk decays monotonically with tenure: 52.2% in the first
6 months vs 6.4% after five years - an ~8x risk gradient.
Half of all churned customers left with 10 or fewer months of tenure. This is
lifecycle risk, not customer-quality risk: the business leaks value mostly in
the first contract year, and month 1 is the single most dangerous point.

### Recommended action

Stand up a structured **onboarding / early-lifecycle program**: a 90-day
experience plan for new customers (proactive setup call, first-invoice check,
expectation management), with special attention to tenure = 1 accounts before
their second billing cycle. Track month-3 and month-6 survival cohorts as the
program's KPI.
