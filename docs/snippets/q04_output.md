## Q04 - Output: Revenue at risk

**Question:** How much monthly recurring revenue is at risk from churn, and how is that risk distributed across price bands?
**Code:** `scripts/q04_revenue_at_risk.py`

### Output

| Price band | Customers | Churn rate | Monthly revenue | Churned monthly revenue | Share of MRR at risk |
| --- | --- | --- | --- | --- | --- |
| **Low ($0-35)** | 1735 | 10.9% | $38,217 | $4,458 | 3.2% |
| **Mid ($35-70)** | 1725 | 23.9% | $94,597 | $22,182 | 15.9% |
| **High ($70-95)** | 2288 | 37.1% | $188,751 | $69,825 | 50.2% |
| **Premium ($95+)** | 1295 | 32.3% | $134,551 | $42,666 | 30.7% |

- Total MRR: **$456,117** · churned customers' MRR: **$139,131** (30.5%) -> **$1,669,570 annualized** at risk.
- ARPU: churned **$74.44** vs retained **$61.27** (+21.5%).
- Chart: `docs/images/q04_chart.png` · Metrics: `docs/json/q04_metrics.json`

### Interpretation

Churn is not just a volume problem - it is a *value-weighted* problem. The
customers who leave pay on average $74.44/month versus
$61.27 for those who stay, so churn removes a
disproportionate share of revenue: 30.5% of all MRR
sits in churned accounts, well above their 26.5% share of customers. The
premium band ($95+) shows the pattern at its extreme: high churn rate with the
highest per-customer revenue. Retention economics beat acquisition economics
here: every dollar spent keeping a high-bundle customer protects ~4x the
average monthly revenue.

### Recommended action

1. Make retention budget **revenue-weighted**: prioritize saving accounts in
   the $70+ bands (High and Premium), which concentrate the largest share of
   at-risk revenue.
2. Audit pricing/value in the $95+ band: premium bundles churn fast, which
   signals the price-value gap needs fixing (review components, add perks, or
   restructure the bundle).
3. Add "monthly revenue at risk" as the primary KPI next to churn count in
   retention reporting, so leadership sees dollars, not just rates.
