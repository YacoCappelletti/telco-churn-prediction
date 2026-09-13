## Q03 - Output: Churn by service type and add-ons

**Question:** How does churn differ by internet service type, and are value-added services associated with lower churn?
**Code:** `scripts/q03_services_and_churn.py`

### Output

Churn by internet service type:

| Internet service | Customers | Churn rate |
| --- | --- | --- |
| **Fiber optic** | 3096 | 41.9% |
| **DSL** | 2421 | 19.0% |
| **No** | 1526 | 7.4% |

Churn by protection tier (Security and/or TechSupport, internet users only):

| Protection tier | Customers | Churn rate |
| --- | --- | --- |
| **No protection** | 4079 | 33.4% |
| **Security or Support** | 1865 | 21.8% |
| **Both Security & Support** | 1099 | 9.0% |

- Every add-on follows the same pattern (Yes vs No churn rate): OnlineSecurity 14.6% vs 41.8%; TechSupport 15.2% vs 41.6%; OnlineBackup, DeviceProtection, StreamingTV and StreamingMovies show the same direction.
- Fiber optic monthly revenue: $283,284 - of which $114,300 is currently churning away.
- Chart: `docs/images/q03_chart.png` · Metrics: `docs/json/q03_metrics.json`

### Interpretation

Fiber optic churns at 41.9% - more than double DSL's
19.0% - despite being the premium product. Fiber is the
business's biggest single revenue source AND its biggest leak: $114,300/month
of fiber revenue is churning. Meanwhile, the correlation is inverted for add-ons:
customers *without* OnlineSecurity or TechSupport churn at ~42%, versus ~15% for
those who have them. Two readings are plausible: (a) add-ons genuinely increase
stickiness (bundling effect), and (b) dissatisfied fiber customers may be less
inclined to buy add-ons. Either way, the unprotected-fiber segment
(fiber + no security + no support) is the red zone to manage.

### Recommended action

1. Run a service-quality investigation on fiber (installation, outages, speed
   expectations vs delivery) - a 2x churn premium on the flagship product is a
   product problem before a pricing problem.
2. Bundle OnlineSecurity + TechSupport into fiber onboarding offers at a
   promotional first-year price: the unprotected-fiber segment is both the
   largest and the leakiest.
3. Track the protected-vs-unprotected churn gap as a leading indicator of
   whether bundling actually retains.
