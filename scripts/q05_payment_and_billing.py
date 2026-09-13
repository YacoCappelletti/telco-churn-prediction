"""Q05 - Does payment method / paperless billing relate to churn?

Business question (Phase 2, selected as the top-5 #5):
"How does churn differ by payment method and billing mode, and is there
a compounding effect between them?"

Outputs:
- docs/json/q05_metrics.json
- docs/snippets/q05_output.md
- docs/images/q05_chart.png

Descriptive analysis only: no target selection, no model training.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt

from src.data.common import (
    CORAL,
    DARK,
    GREY,
    TEAL,
    load_telco,
    md_table,
    money,
    pct,
    save_chart,
    save_metrics,
    save_snippet,
)

METRICS_NAME = "q05_metrics"
SNIPPET_NAME = "q05_output"
CHART_NAME = "q05_chart"

PAYMENT_ORDER = [
    "Electronic check",
    "Mailed check",
    "Bank transfer (automatic)",
    "Credit card (automatic)",
]


def main() -> None:
    df = load_telco()
    overall = df["churn_flag"].mean()

    g = df.groupby("PaymentMethod")["churn_flag"].agg(["count", "mean"])
    g = g.reindex(PAYMENT_ORDER)
    by_payment = {
        str(k): {"customers": int(v["count"]), "churn_rate": round(float(v["mean"]), 4)}
        for k, v in g.iterrows()
    }

    p = df.groupby("PaperlessBilling")["churn_flag"].agg(["count", "mean"])
    by_paperless = {
        str(k): {"customers": int(v["count"]), "churn_rate": round(float(v["mean"]), 4)}
        for k, v in p.iterrows()
    }

    # Compounding effect: electronic check x paperless billing
    e = df[df["PaymentMethod"] == "Electronic check"]
    ec_paperless = e[e["PaperlessBilling"] == "Yes"]["churn_flag"].mean()
    ec_mail = e[e["PaperlessBilling"] == "No"]["churn_flag"].mean()
    auto_paperless = (
        df[df["PaymentMethod"] != "Electronic check"]
        .groupby("PaperlessBilling")["churn_flag"]
        .mean()
    )
    echeck_mrr = e["MonthlyCharges"].sum()
    echeck_churned_mrr = e.loc[e["churn_flag"] == 1, "MonthlyCharges"].sum()

    metrics = {
        "question": "How does churn differ by payment method and billing mode?",
        "overall_churn_rate": round(float(overall), 4),
        "churn_rate_by_payment_method": by_payment,
        "churn_rate_by_paperless_billing": by_paperless,
        "electronic_check_x_paperless": {
            "echeck_paperless_yes": round(float(ec_paperless), 4),
            "echeck_paperless_no": round(float(ec_mail), 4),
            "other_methods_paperless_yes": round(
                float(auto_paperless.get("Yes", 0)), 4
            ),
            "other_methods_paperless_no": round(float(auto_paperless.get("No", 0)), 4),
        },
        "echeck_customers": int(len(e)),
        "echeck_monthly_revenue": round(float(echeck_mrr), 2),
        "echeck_churned_monthly_revenue": round(float(echeck_churned_mrr), 2),
    }
    save_metrics(METRICS_NAME, metrics)

    # --- Chart ---------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(9, 5.4))
    rates = g["mean"] * 100
    short = [
        "Electronic\ncheck",
        "Mailed\ncheck",
        "Bank transfer\n(automatic)",
        "Credit card\n(automatic)",
    ]
    colors = [CORAL if r == rates.max() else TEAL for r in rates]
    bars = ax.bar(short, rates.values, color=colors, width=0.55, zorder=3)
    for bar, rate, count in zip(bars, rates.values, g["count"].values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1.0,
            f"{rate:.1f}%\n(n={count:,})",
            ha="center",
            va="bottom",
            fontsize=9.5,
            color=DARK,
        )
    ax.axhline(overall * 100, color=DARK, lw=1.4, ls="--")
    ax.text(
        3.45,
        overall * 100 + 1.0,
        f"Overall: {pct(overall)}",
        ha="right",
        color=DARK,
        fontsize=10,
    )
    ax.set_ylim(0, rates.max() * 1.28)
    ax.set_ylabel("Churn rate (%)")
    ax.set_title("Manual payment methods churn 3x more than automatic ones")
    ax.spines[["top", "right"]].set_visible(False)
    ax.text(
        0,
        -0.14,
        f"Source: Telco-Customer-Churn.csv (7,043 customers). Electronic-check MRR churned: {money(echeck_churned_mrr)}/mo.",
        transform=ax.transAxes,
        color=GREY,
        fontsize=8.5,
    )
    save_chart(fig, CHART_NAME)

    # --- Snippet -------------------------------------------------------------
    rows = [[f"**{k}**", int(v["count"]), pct(v["mean"], 1)] for k, v in g.iterrows()]
    rows_p = [[f"**{k}**", int(v["count"]), pct(v["mean"], 1)] for k, v in p.iterrows()]
    snippet = f"""## Q05 - Output: Churn by payment method and billing mode

**Question:** How does churn differ by payment method and billing mode, and is there a compounding effect?
**Code:** `scripts/q05_payment_and_billing.py`

### Output

{md_table(["Payment method", "Customers", "Churn rate"], rows)}

{md_table(["Paperless billing", "Customers", "Churn rate"], rows_p)}

- Compounding effect (electronic check): paperless **{pct(ec_paperless, 1)}** vs paper **{pct(ec_mail, 1)}**; among the other three methods it is {pct(auto_paperless.get("Yes", 0), 1)} (paperless) vs {pct(auto_paperless.get("No", 0), 1)} (paper).
- Electronic check: {int(len(e)):,} customers, {money(echeck_mrr)} MRR, of which {money(echeck_churned_mrr)} is churning away every month.
- Chart: `docs/images/{CHART_NAME}.png` · Metrics: `docs/json/{METRICS_NAME}.json`

### Interpretation

Payment friction correlates strongly with churn: electronic-check customers
churn at {pct(g.loc["Electronic check", "mean"], 1)} vs ~15-17% for the two
automatic methods - roughly 3x. Paperless billing shows the same direction
({pct(p.loc["Yes", "mean"], 1)} vs {pct(p.loc["No", "mean"], 1)}), and the two
compound: electronic-check + paperless customers are the single leakiest
configuration at {pct(ec_paperless, 1)}. A plausible mechanism is engagement:
manual payment means the customer re-authorizes (or notices) the charge every
month, creating a monthly decision point to reassess the service - automatic
payments remove that decision point. Note this is correlation, not proof of
causation: payment type also proxies for customer profile.

### Recommended action

1. Run a **payment-migration campaign**: incentivize electronic-check customers
   to switch to automatic bank transfer / credit card (small monthly discount
   or one-time credit). With {int(len(e)):,} customers and {money(echeck_churned_mrr)} of
   churning e-check MRR, even modest migration is high-ROI.
2. First target the e-check + paperless configuration ({pct(ec_paperless, 1)} churn).
3. Measure via an A/B test so the causal effect of switching payment method is
   isolated from customer-profile effects.
"""
    save_snippet(SNIPPET_NAME, snippet)

    print(f"Wrote {METRICS_NAME}.json, {SNIPPET_NAME}.md, {CHART_NAME}.png")
    print(
        "By payment: " + ", ".join(f"{k}={pct(v['mean'], 1)}" for k, v in g.iterrows())
    )


if __name__ == "__main__":
    main()
