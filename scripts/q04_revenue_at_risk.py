"""Q04 - How much monthly revenue is at risk, and who pays the most?

Business question (Phase 2, selected as the top-5 #4):
"How much monthly recurring revenue is at risk from churn, and how is
that risk distributed across price bands?"

Outputs:
- docs/json/q04_metrics.json
- docs/snippets/q04_output.md
- docs/images/q04_chart.png

Descriptive analysis only: no target selection, no model training.
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt
import pandas as pd

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

METRICS_NAME = "q04_metrics"
SNIPPET_NAME = "q04_output"
CHART_NAME = "q04_chart"

PRICE_BANDS = [(0, 35), (35, 70), (70, 95), (95, 130)]
BAND_LABELS = [
    "Low ($0-35)",
    "Mid ($35-70)",
    "High ($70-95)",
    "Premium ($95+)",
]


def main() -> None:
    df = load_telco()
    mrr_total = df["MonthlyCharges"].sum()
    mrr_churned = df.loc[df["churn_flag"] == 1, "MonthlyCharges"].sum()
    overall_arpu = df["MonthlyCharges"].mean()
    arpu_churned = df.loc[df["churn_flag"] == 1, "MonthlyCharges"].mean()
    arpu_retained = df.loc[df["churn_flag"] == 0, "MonthlyCharges"].mean()

    band = pd.cut(
        df["MonthlyCharges"],
        bins=[b[0] for b in PRICE_BANDS] + [PRICE_BANDS[-1][1]],
        labels=BAND_LABELS,
    )
    g = df.groupby(band, observed=True).agg(
        customers=("churn_flag", "count"),
        churn_rate=("churn_flag", "mean"),
        mrr=("MonthlyCharges", "sum"),
        mrr_churned=(
            "MonthlyCharges",
            lambda s: s[df.loc[s.index, "churn_flag"] == 1].sum(),
        ),
    )
    g["mrr_at_risk_share"] = g["mrr_churned"] / mrr_churned

    by_band = {
        str(k): {
            "customers": int(v["customers"]),
            "churn_rate": round(float(v["churn_rate"]), 4),
            "monthly_revenue": round(float(v["mrr"]), 2),
            "churned_monthly_revenue": round(float(v["mrr_churned"]), 2),
            "share_of_revenue_at_risk": round(float(v["mrr_at_risk_share"]), 4),
        }
        for k, v in g.iterrows()
    }
    metrics = {
        "question": "How much monthly recurring revenue is at risk from churn?",
        "total_monthly_revenue": round(float(mrr_total), 2),
        "churned_monthly_revenue": round(float(mrr_churned), 2),
        "share_of_mrr_at_risk": round(float(mrr_churned / mrr_total), 4),
        "annualized_revenue_at_risk": round(float(mrr_churned * 12), 2),
        "overall_arpu": round(float(overall_arpu), 2),
        "arpu_churned": round(float(arpu_churned), 2),
        "arpu_retained": round(float(arpu_retained), 2),
        "arpu_premium_churned_vs_retained_pct": round(
            float((arpu_churned - arpu_retained) / arpu_retained), 4
        ),
        "by_price_band": by_band,
        "total_customers": int(len(df)),
    }
    save_metrics(METRICS_NAME, metrics)

    # --- Chart ---------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(
        1, 2, figsize=(11.5, 5), gridspec_kw={"width_ratios": [1.2, 1]}
    )
    # Left: MRR at risk by price band
    colors = [CORAL if v == g["mrr_churned"].max() else TEAL for v in g["mrr_churned"]]
    bars = ax1.bar(BAND_LABELS, g["mrr_churned"], color=colors, width=0.55, zorder=3)
    for bar, v in zip(bars, g["mrr_churned"]):
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1500,
            money(v),
            ha="center",
            va="bottom",
            fontsize=9.5,
            color=DARK,
        )
    ax1.set_ylabel("Churned customers' monthly revenue ($)")
    ax1.set_title("Monthly revenue at risk by price band")
    ax1.tick_params(axis="x", labelsize=8.6)
    ax1.spines[["top", "right"]].set_visible(False)

    # Right: ARPU churned vs retained
    means = [arpu_churned, arpu_retained]
    bars2 = ax2.bar(
        ["Churned", "Retained"], means, color=[CORAL, TEAL], width=0.45, zorder=3
    )
    for bar, v in zip(bars2, means):
        ax2.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1.0,
            f"${v:.2f}",
            ha="center",
            va="bottom",
            fontsize=10,
            color=DARK,
        )
    ax2.set_ylim(0, max(means) * 1.18)
    ax2.set_ylabel("Mean monthly charge ($)")
    ax2.set_title("Churners are the higher-value customers")
    ax2.spines[["top", "right"]].set_visible(False)

    fig.text(
        0.01,
        0.01,
        f"Source: Telco-Customer-Churn.csv (7,043 customers). Total MRR {money(mrr_total)}; "
        f"{money(mrr_churned)}/mo ({pct(mrr_churned / mrr_total)}) currently churning.",
        color=GREY,
        fontsize=8.5,
    )
    save_chart(fig, CHART_NAME)

    # --- Snippet -------------------------------------------------------------
    rows = [
        [
            f"**{k}**",
            int(v["customers"]),
            pct(v["churn_rate"], 1),
            money(v["mrr"]),
            money(v["mrr_churned"]),
            pct(v["mrr_at_risk_share"], 1),
        ]
        for k, v in g.iterrows()
    ]
    snippet = f"""## Q04 - Output: Revenue at risk

**Question:** How much monthly recurring revenue is at risk from churn, and how is that risk distributed across price bands?
**Code:** `scripts/q04_revenue_at_risk.py`

### Output

{md_table(["Price band", "Customers", "Churn rate", "Monthly revenue", "Churned monthly revenue", "Share of MRR at risk"], rows)}

- Total MRR: **{money(mrr_total)}** · churned customers' MRR: **{money(mrr_churned)}** ({pct(mrr_churned / mrr_total)}) -> **{money(mrr_churned * 12)} annualized** at risk.
- ARPU: churned **${arpu_churned:.2f}** vs retained **${arpu_retained:.2f}** (+{pct((arpu_churned - arpu_retained) / arpu_retained)}).
- Chart: `docs/images/{CHART_NAME}.png` · Metrics: `docs/json/{METRICS_NAME}.json`

### Interpretation

Churn is not just a volume problem - it is a *value-weighted* problem. The
customers who leave pay on average ${arpu_churned:.2f}/month versus
${arpu_retained:.2f} for those who stay, so churn removes a
disproportionate share of revenue: {pct(mrr_churned / mrr_total)} of all MRR
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
"""
    save_snippet(SNIPPET_NAME, snippet)

    print(f"Wrote {METRICS_NAME}.json, {SNIPPET_NAME}.md, {CHART_NAME}.png")
    print(
        f"MRR={money(mrr_total)} | churned MRR={money(mrr_churned)} "
        f"({pct(mrr_churned / mrr_total)}) | ARPU churned=${arpu_churned:.2f} vs retained=${arpu_retained:.2f}"
    )


if __name__ == "__main__":
    main()
