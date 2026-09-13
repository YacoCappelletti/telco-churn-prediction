## Q05 - Output: Churn by payment method and billing mode

**Question:** How does churn differ by payment method and billing mode, and is there a compounding effect?
**Code:** `scripts/q05_payment_and_billing.py`

### Output

| Payment method | Customers | Churn rate |
| --- | --- | --- |
| **Electronic check** | 2365 | 45.3% |
| **Mailed check** | 1612 | 19.1% |
| **Bank transfer (automatic)** | 1544 | 16.7% |
| **Credit card (automatic)** | 1522 | 15.2% |

| Paperless billing | Customers | Churn rate |
| --- | --- | --- |
| **No** | 2872 | 16.3% |
| **Yes** | 4171 | 33.6% |

- Compounding effect (electronic check): paperless **49.8%** vs paper **32.7%**; among the other three methods it is 21.9% (paperless) vs 11.8% (paper).
- Electronic check: 2,365 customers, $180,345 MRR, of which $84,289 is churning away every month.
- Chart: `docs/images/q05_chart.png` · Metrics: `docs/json/q05_metrics.json`

### Interpretation

Payment friction correlates strongly with churn: electronic-check customers
churn at 45.3% vs ~15-17% for the two
automatic methods - roughly 3x. Paperless billing shows the same direction
(33.6% vs 16.3%), and the two
compound: electronic-check + paperless customers are the single leakiest
configuration at 49.8%. A plausible mechanism is engagement:
manual payment means the customer re-authorizes (or notices) the charge every
month, creating a monthly decision point to reassess the service - automatic
payments remove that decision point. Note this is correlation, not proof of
causation: payment type also proxies for customer profile.

### Recommended action

1. Run a **payment-migration campaign**: incentivize electronic-check customers
   to switch to automatic bank transfer / credit card (small monthly discount
   or one-time credit). With 2,365 customers and $84,289 of
   churning e-check MRR, even modest migration is high-ROI.
2. First target the e-check + paperless configuration (49.8% churn).
3. Measure via an A/B test so the causal effect of switching payment method is
   isolated from customer-profile effects.
