## Q01 - Output: Overall churn rate and churn by contract type

**Question:** What is the overall churn rate, and how does it vary by contract type?
**Code:** `scripts/q01_churn_rate_by_contract.py`

### Output

| Contract | Customers | Share of base | Churn rate | Monthly revenue churned | Share of total MRR at risk |
| --- | --- | --- | --- | --- | --- |
| **Month-to-month** | 3875 | 55.0% | 42.7% | $120,847 | 26.5% |
| **One year** | 1473 | 20.9% | 11.3% | $14,118 | 3.1% |
| **Two year** | 1695 | 24.1% | 2.8% | $4,165 | 0.9% |

- Overall churn rate: **26.5%** (1,869 of 7,043 customers).
- Total monthly recurring revenue (MRR): **$456,117**; monthly revenue already lost to churned customers: **$139,131** (30.5% of MRR).
- Chart: `docs/images/q01_chart.png` · Metrics: `docs/json/q01_metrics.json`

### Interpretation

Contract commitment is the single strongest structural divide in the base.
Month-to-month customers churn at 42.7% - about
15.1x the rate of two-year customers
(2.8%) - and although they are 55%
of the base, they carry 26.5% of all monthly
revenue at risk. Note the paradox: month-to-month customers also pay the highest
median monthly charge, so the least-committed segment is also the most expensive
to lose.

### Recommended action

Prioritize a contract-migration program: target month-to-month customers with
incentives to move to 1-2 year terms (discount lock-in, bundled add-ons) and
monitor churn rate by contract type monthly. Even a partial migration of the
3,875 month-to-month customers materially reduces the $139,131 monthly exposure.
