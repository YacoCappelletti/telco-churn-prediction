# Business Questions - Telco Customer Churn

> Dataset: `data/raw/Telco-Customer-Churn.csv` (7,043 customers) · JSON: `docs/json/business_questions.json`

## 1. The 10 candidate business questions

All questions below are answerable with this dataset alone.

| # | Question |
| - | -------- |
| 1 | What is the overall churn rate, and how does it vary by contract type? |
| 2 | How does churn risk change across the customer lifecycle (tenure)? |
| 3 | How does churn differ by internet service type, and do value-added add-ons (security, support) protect against churn? |
| 4 | How much monthly recurring revenue is at risk from churn, and how is that risk distributed across price bands? |
| 5 | How does churn differ by payment method and paperless billing, and is there a compounding effect? |
| 6 | Do customers with partners/dependents churn differently, and which demographic segments concentrate churn? |
| 7 | Which customer profile generates the highest revenue, and how is ARPU distributed across segments? |
| 8 | How does churn interact between contract type and tenure (e.g., are young month-to-month customers the red zone)? |
| 9 | How do entertainment services (StreamingTV/StreamingMovies) relate to churn independently of internet type? |
| 10 | What share of customers have no add-on services at all, and how does that share move revenue exposure? |

## 2. The 5 selected questions and why

Selection scored each question on **business impact**, **feasibility** (data
completeness, analytic simplicity), and **actionability** (executability of a
concrete lever).

| Selected | Question | Impact | Feasibility | Actionability |
| -------- | -------- | ------ | ----------- | ------------- |
| **Q1** | Churn rate by contract type | Highest - contract is the largest structural divide; month-to-month carries ~87% of churned MRR | High | High - contract migration programs |
| **Q2** | Churn across tenure | High - first-year customers generate 55% of all churn | High | High - onboarding programs |
| **Q3** | Churn by service type & add-ons | High - flagship product (fiber) churns at 2.2x DSL | High | Medium-high - bundling + product fixes |
| **Q4** | Revenue at risk | Highest - converts churn into dollars ($139K/mo, $1.67M annualized) | High | High - retention budget allocation |
| **Q5** | Payment method & billing | Medium-high - leaky, addressable segment (e-check × paperless: 49.8% churn) | High | High - cheap, testable campaigns |

Rejected questions and reasons: Q6 (demographics overlap with stronger
contract/tenure signals), Q7 (covered by Q4's price bands), Q8 (action already
covered by Q1+Q2), Q9 (weak differentials vs protection add-ons), Q10 (covered
by Q3's protection tiers).

## 3. Per-question artifacts

| Question | Script | Snippet | Metrics | Chart |
| -------- | ------ | ------- | ------- | ----- |
| Q1 | `scripts/q01_churn_rate_by_contract.py` | `docs/snippets/q01_output.md` | `docs/json/q01_metrics.json` | `docs/images/q01_chart.png` |
| Q2 | `scripts/q02_tenure_vs_churn.py` | `docs/snippets/q02_output.md` | `docs/json/q02_metrics.json` | `docs/images/q02_chart.png` |
| Q3 | `scripts/q03_services_and_churn.py` | `docs/snippets/q03_output.md` | `docs/json/q03_metrics.json` | `docs/images/q03_chart.png` |
| Q4 | `scripts/q04_revenue_at_risk.py` | `docs/snippets/q04_output.md` | `docs/json/q04_metrics.json` | `docs/images/q04_chart.png` |
| Q5 | `scripts/q05_payment_and_billing.py` | `docs/snippets/q05_output.md` | `docs/json/q05_metrics.json` | `docs/images/q05_chart.png` |

Every insight is justified with code: each script loads the raw data, computes
its metrics, and writes the JSON + snippet + chart listed above. Full
interpretation and recommended actions live in
`docs/business_analysis_report.md` and `docs/snippets/*.md`.
