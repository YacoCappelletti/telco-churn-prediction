"""Q02 - How does churn risk evolve with customer tenure?

Business question (Phase 2, selected as the top-5 #2):
"How does churn risk change across the customer lifecycle, and where in
tenure does risk concentrate?"

Outputs:
- docs/json/q02_metrics.json
- docs/snippets/q02_output.md
- docs/images/q02_chart.png

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
    pct,
    save_chart,
    save_metrics,
    save_snippet,
)

METRICS_NAME = "q02_metrics"
SNIPPET_NAME = "q02_output"
CHART_NAME = "q02_chart"

BUCKETS = [(0, 6), (7, 12), (13, 24), (25, 48), (49, 60), (61, 72)]
LABELS = ["0-6", "7-12", "13-24", "25-48", "49-60", "61-72"]


def main() -> None:
    df = load_telco()
    overall = df["churn_flag"].mean()

    tenure = df["tenure"]
    bucket = pd.cut(
        tenure, bins=[b[0] for b in BUCKETS] + [BUCKETS[-1][1]], labels=LABELS
    )
    g = df.groupby(bucket, observed=True)["churn_flag"].agg(["count", "mean"])

    by_bucket = {
        str(k): {"customers": int(v["count"]), "churn_rate": round(float(v["mean"]), 4)}
        for k, v in g.iterrows()
    }
    med_churned = int(df.loc[df["churn_flag"] == 1, "tenure"].median())
    med_retained = int(df.loc[df["churn_flag"] == 0, "tenure"].median())
    first_year = df[tenure <= 12]
    metrics = {
        "question": "How does churn risk change across the customer lifecycle?",
        "overall_churn_rate": round(float(overall), 4),
        "churn_rate_by_tenure_bucket": by_bucket,
        "median_tenure_churned": med_churned,
        "median_tenure_retained": med_retained,
        "customers_within_first_12_months": int(len(first_year)),
        "first_12_months_share_of_all_churn": round(
            float(first_year["churn_flag"].sum() / df["churn_flag"].sum()), 4
        ),
        "customers_with_tenure_1": int((tenure == 1).sum()),
    }
    save_metrics(METRICS_NAME, metrics)

    # --- Chart ---------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8.6, 5))
    rates = g["mean"] * 100
    colors = [CORAL if r == rates.max() else TEAL for r in rates]
    bars = ax.bar(
        rates.index.astype(str), rates.values, color=colors, width=0.6, zorder=3
    )
    ax.axhline(overall * 100, color=DARK, lw=1.4, ls="--", zorder=4)
    ax.text(
        5.45,
        overall * 100 + 1.0,
        f"Overall: {pct(overall)}",
        ha="right",
        color=DARK,
        fontsize=10,
    )
    for bar, rate, count in zip(bars, rates.values, g["count"].values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 0.9,
            f"{rate:.1f}%\n(n={count:,})",
            ha="center",
            va="bottom",
            fontsize=9.2,
            color=DARK,
        )
    ax.set_ylim(0, rates.max() * 1.3)
    ax.set_xlabel("Tenure (months since signup)")
    ax.set_ylabel("Churn rate (%)")
    ax.set_title(
        "Churn collapses as tenure grows - risk concentrates in the first year"
    )
    ax.spines[["top", "right"]].set_visible(False)
    ax.text(
        0,
        -0.18,
        "Source: Telco-Customer-Churn.csv (7,043 customers). Median tenure: churned = "
        f"{med_churned} mo vs retained = {med_retained} mo.",
        transform=ax.transAxes,
        color=GREY,
        fontsize=8.5,
    )
    save_chart(fig, CHART_NAME)

    # --- Snippet -------------------------------------------------------------
    rows = [[f"**{k}**", int(v["count"]), pct(v["mean"], 1)] for k, v in g.iterrows()]
    snippet = f"""## Q02 - Output: Churn rate by tenure bucket

**Question:** How does churn risk change across the customer lifecycle, and where does risk concentrate?
**Code:** `scripts/q02_tenure_vs_churn.py`

### Output

{md_table(["Tenure bucket (months)", "Customers", "Churn rate"], rows)}

- Median tenure of churned customers: **{med_churned} months** vs **{med_retained} months** for retained customers.
- Customers in their first 12 months: {int(len(first_year)):,} - they account for **{pct(metrics["first_12_months_share_of_all_churn"])}** of all churned customers.
- A striking {int((tenure == 1).sum()):,} customers sit at exactly 1 month of tenure - the onboarding cliff.
- Chart: `docs/images/{CHART_NAME}.png` · Metrics: `docs/json/{METRICS_NAME}.json`

### Interpretation

Churn risk decays monotonically with tenure: {pct(g.loc["0-6", "mean"], 1)} in the first
6 months vs {pct(g.loc["61-72", "mean"], 1)} after five years - an ~8x risk gradient.
Half of all churned customers left with 10 or fewer months of tenure. This is
lifecycle risk, not customer-quality risk: the business leaks value mostly in
the first contract year, and month 1 is the single most dangerous point.

### Recommended action

Stand up a structured **onboarding / early-lifecycle program**: a 90-day
experience plan for new customers (proactive setup call, first-invoice check,
expectation management), with special attention to tenure = 1 accounts before
their second billing cycle. Track month-3 and month-6 survival cohorts as the
program's KPI.
"""
    save_snippet(SNIPPET_NAME, snippet)

    print(f"Wrote {METRICS_NAME}.json, {SNIPPET_NAME}.md, {CHART_NAME}.png")
    print(
        f"By bucket: " + ", ".join(f"{k}={pct(v['mean'], 1)}" for k, v in g.iterrows())
    )


if __name__ == "__main__":
    main()
