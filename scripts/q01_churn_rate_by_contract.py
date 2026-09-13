"""Q01 - What is the overall churn rate, and how does it vary by contract type?

Business question (Phase 2, selected as the top-5 #1):
"What share of the customer base churns, and how does churn concentrate
across contract types?"

Outputs:
- docs/json/q01_metrics.json
- docs/snippets/q01_output.md
- docs/images/q01_chart.png

This is a descriptive business analysis. It does not select or propose a
modeling target variable and does not train any model.
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

METRICS_NAME = "q01_metrics"
SNIPPET_NAME = "q01_output"
CHART_NAME = "q01_chart"


def main() -> None:
    df = load_telco()
    n = len(df)
    overall_rate = df["churn_flag"].mean()
    mrr_total = df["MonthlyCharges"].sum()

    g = df.groupby("Contract")["churn_flag"].agg(["count", "mean"])
    g["share_base"] = g["count"] / n
    g["mrr_churned"] = (
        df[df["churn_flag"] == 1].groupby("Contract")["MonthlyCharges"].sum()
    )
    g["mrr_at_risk_share"] = g["mrr_churned"] / mrr_total
    g = g.reindex(["Month-to-month", "One year", "Two year"])

    by_contract = {
        str(k): {
            "customers": int(v["count"]),
            "share_of_base": round(float(v["share_base"]), 4),
            "churn_rate": round(float(v["mean"]), 4),
            "monthly_revenue_at_risk": round(float(v["mrr_churned"]), 2),
            "share_of_total_mrr_at_risk": round(float(v["mrr_at_risk_share"]), 4),
        }
        for k, v in g.iterrows()
    }
    metrics = {
        "question": "What is the overall churn rate, and how does it vary by contract type?",
        "overall_churn_rate": round(float(overall_rate), 4),
        "overall_churned_customers": int(df["churn_flag"].sum()),
        "total_customers": n,
        "total_monthly_revenue": round(float(mrr_total), 2),
        "total_monthly_revenue_at_risk": round(
            float(df.loc[df["churn_flag"] == 1, "MonthlyCharges"].sum()), 2
        ),
        "by_contract": by_contract,
        "rate_multiple_month_to_month_vs_two_year": round(
            float(g.loc["Month-to-month", "mean"] / g.loc["Two year", "mean"]), 1
        ),
    }
    save_metrics(METRICS_NAME, metrics)

    # --- Chart ---------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8.2, 5))
    rates = g["mean"] * 100
    colors = [CORAL if r == rates.max() else TEAL for r in rates]
    bars = ax.bar(rates.index, rates.values, color=colors, width=0.55, zorder=3)
    ax.axhline(overall_rate * 100, color=DARK, lw=1.4, ls="--", zorder=4)
    ax.text(
        2.42,
        overall_rate * 100 + 1.2,
        f"Overall churn: {pct(overall_rate)}",
        ha="right",
        color=DARK,
        fontsize=10,
    )
    for bar, (ct, rate, share, mrr) in zip(
        bars, zip(g.index, rates.values, g["share_base"], g["mrr_churned"])
    ):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1.1,
            f"{rate:.1f}%\n{pct(share, 0)} of base\n{money(mrr)}/mo at risk",
            ha="center",
            va="bottom",
            fontsize=9.2,
            color=DARK,
        )
    ax.set_ylim(0, rates.max() * 1.28)
    ax.set_ylabel("Churn rate (%)")
    ax.set_title("Churn rate by contract type - commitment locks customers in")
    ax.spines[["top", "right"]].set_visible(False)
    ax.text(
        0,
        -0.16,
        "Source: Telco-Customer-Churn.csv (7,043 customers). Churn = Yes share within each contract type.",
        transform=ax.transAxes,
        color=GREY,
        fontsize=8.5,
    )
    save_chart(fig, CHART_NAME)

    # --- Snippet -------------------------------------------------------------
    rows = [
        [
            f"**{idx}**",
            int(v["count"]),
            pct(v["share_base"], 1),
            pct(v["mean"], 1),
            money(v["mrr_churned"]),
            pct(v["mrr_at_risk_share"], 1),
        ]
        for idx, v in g.iterrows()
    ]
    snippet = f"""## Q01 - Output: Overall churn rate and churn by contract type

**Question:** What is the overall churn rate, and how does it vary by contract type?
**Code:** `scripts/q01_churn_rate_by_contract.py`

### Output

{md_table(["Contract", "Customers", "Share of base", "Churn rate", "Monthly revenue churned", "Share of total MRR at risk"], rows)}

- Overall churn rate: **{pct(overall_rate)}** ({int(df["churn_flag"].sum()):,} of {n:,} customers).
- Total monthly recurring revenue (MRR): **{money(mrr_total)}**; monthly revenue already lost to churned customers: **{money(df.loc[df["churn_flag"] == 1, "MonthlyCharges"].sum())}** ({pct(df.loc[df["churn_flag"] == 1, "MonthlyCharges"].sum() / mrr_total)} of MRR).
- Chart: `docs/images/{CHART_NAME}.png` · Metrics: `docs/json/{METRICS_NAME}.json`

### Interpretation

Contract commitment is the single strongest structural divide in the base.
Month-to-month customers churn at {pct(g.loc["Month-to-month", "mean"], 1)} - about
{metrics["rate_multiple_month_to_month_vs_two_year"]}x the rate of two-year customers
({pct(g.loc["Two year", "mean"], 1)}) - and although they are {pct(g.loc["Month-to-month", "share_base"], 0)}
of the base, they carry {pct(g.loc["Month-to-month", "mrr_at_risk_share"], 1)} of all monthly
revenue at risk. Note the paradox: month-to-month customers also pay the highest
median monthly charge, so the least-committed segment is also the most expensive
to lose.

### Recommended action

Prioritize a contract-migration program: target month-to-month customers with
incentives to move to 1-2 year terms (discount lock-in, bundled add-ons) and
monitor churn rate by contract type monthly. Even a partial migration of the
3,875 month-to-month customers materially reduces the {money(metrics["total_monthly_revenue_at_risk"])} monthly exposure.
"""
    save_snippet(SNIPPET_NAME, snippet)

    print(f"Wrote {METRICS_NAME}.json, {SNIPPET_NAME}.md, {CHART_NAME}.png")
    print(
        f"Overall churn={pct(overall_rate)} | by contract: "
        + ", ".join(f"{k}={pct(v['mean'], 1)}" for k, v in g.iterrows())
    )


if __name__ == "__main__":
    main()
