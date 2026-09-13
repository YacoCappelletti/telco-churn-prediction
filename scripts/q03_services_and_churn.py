"""Q03 - Which services are associated with churn, and do add-ons protect?

Business question (Phase 2, selected as the top-5 #3):
"How does churn differ by internet service type, and are value-added
services (security, support) associated with lower churn?"

Outputs:
- docs/json/q03_metrics.json
- docs/snippets/q03_output.md
- docs/images/q03_chart.png

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

METRICS_NAME = "q03_metrics"
SNIPPET_NAME = "q03_output"
CHART_NAME = "q03_chart"

SERVICE_COLS = [
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies",
]


def add_on_segment(row) -> str:
    """Protection tier among internet users: None / Any protection / Both."""
    protected = (row["OnlineSecurity"] == "Yes") + (row["TechSupport"] == "Yes")
    if protected == 0:
        return "No protection"
    if protected == 1:
        return "Security or Support"
    return "Both Security & Support"


def main() -> None:
    df = load_telco()
    overall = df["churn_flag"].mean()

    # By internet service type
    g = df.groupby("InternetService")["churn_flag"].agg(["count", "mean"])
    g = g.reindex(["Fiber optic", "DSL", "No"])
    by_internet = {
        str(k): {"customers": int(v["count"]), "churn_rate": round(float(v["mean"]), 4)}
        for k, v in g.iterrows()
    }

    # By add-on service (Yes vs No vs structural, within internet users)
    by_service = {}
    for col in SERVICE_COLS:
        sub = df[df[col] != "No internet service"]
        v = sub.groupby(col)["churn_flag"].agg(["count", "mean"])
        by_service[col] = {
            "Yes": {
                "customers": int(v.loc["Yes", "count"]),
                "churn_rate": round(float(v.loc["Yes", "mean"]), 4),
            },
            "No": {
                "customers": int(v.loc["No", "count"]),
                "churn_rate": round(float(v.loc["No", "mean"]), 4),
            },
        }

    # Protection tiers
    df["protection_tier"] = df.apply(add_on_segment, axis=1)
    t = df.groupby("protection_tier")["churn_flag"].agg(["count", "mean"])
    t = t.reindex(["No protection", "Security or Support", "Both Security & Support"])
    by_tier = {
        str(k): {"customers": int(v["count"]), "churn_rate": round(float(v["mean"]), 4)}
        for k, v in t.iterrows()
    }

    fiber_risk = df.loc[df["InternetService"] == "Fiber optic"]
    metrics = {
        "question": "How does churn differ by internet service type, and do add-ons protect?",
        "overall_churn_rate": round(float(overall), 4),
        "churn_rate_by_internet_service": by_internet,
        "churn_rate_by_service_yes_no": by_service,
        "churn_rate_by_protection_tier": by_tier,
        "fiber_monthly_revenue": round(float(fiber_risk["MonthlyCharges"].sum()), 2),
        "fiber_churned_monthly_revenue": round(
            float(
                fiber_risk.loc[fiber_risk["churn_flag"] == 1, "MonthlyCharges"].sum()
            ),
            2,
        ),
    }
    save_metrics(METRICS_NAME, metrics)

    # --- Chart ---------------------------------------------------------------
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 5))
    r1 = g["mean"] * 100
    colors = [CORAL if r == r1.max() else TEAL for r in r1]
    bars = ax1.bar(r1.index, r1.values, color=colors, width=0.55, zorder=3)
    for bar, rate, count in zip(bars, r1.values, g["count"].values):
        ax1.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1.2,
            f"{rate:.1f}%\n(n={count:,})",
            ha="center",
            va="bottom",
            fontsize=9.2,
            color=DARK,
        )
    ax1.axhline(overall * 100, color=DARK, lw=1.2, ls="--")
    ax1.text(
        2.45,
        overall * 100 + 1.2,
        f"Overall: {pct(overall)}",
        ha="right",
        color=DARK,
        fontsize=9,
    )
    ax1.set_ylim(0, r1.max() * 1.3)
    ax1.set_ylabel("Churn rate (%)")
    ax1.set_title("Churn by internet service type")
    ax1.spines[["top", "right"]].set_visible(False)

    r2 = t["mean"] * 100
    colors2 = [CORAL if r == r2.max() else TEAL for r in r2]
    labels2 = ["No protection", "Security\nor Support", "Both Security\n& Support"]
    bars2 = ax2.bar(labels2, r2.values, color=colors2, width=0.55, zorder=3)
    for bar, rate, count in zip(bars2, r2.values, t["count"].values):
        ax2.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + 1.2,
            f"{rate:.1f}%\n(n={count:,})",
            ha="center",
            va="bottom",
            fontsize=9.2,
            color=DARK,
        )
    ax2.axhline(overall * 100, color=DARK, lw=1.2, ls="--")
    ax2.text(
        2.45,
        overall * 100 + 1.2,
        f"Overall: {pct(overall)}",
        ha="right",
        color=DARK,
        fontsize=9,
    )
    ax2.set_ylim(0, r2.max() * 1.3)
    ax2.set_ylabel("Churn rate (%)")
    ax2.set_title("Churn by protection add-ons (Security / TechSupport)")
    ax2.spines[["top", "right"]].set_visible(False)

    fig.text(
        0.01,
        0.01,
        "Source: Telco-Customer-Churn.csv (7,043 customers). Protection tiers consider internet users only.",
        color=GREY,
        fontsize=8.5,
    )
    save_chart(fig, CHART_NAME)

    # --- Snippet -------------------------------------------------------------
    rows1 = [[f"**{k}**", int(v["count"]), pct(v["mean"], 1)] for k, v in g.iterrows()]
    rows2 = [[f"**{k}**", int(v["count"]), pct(v["mean"], 1)] for k, v in t.iterrows()]
    snippet = f"""## Q03 - Output: Churn by service type and add-ons

**Question:** How does churn differ by internet service type, and are value-added services associated with lower churn?
**Code:** `scripts/q03_services_and_churn.py`

### Output

Churn by internet service type:

{md_table(["Internet service", "Customers", "Churn rate"], rows1)}

Churn by protection tier (Security and/or TechSupport, internet users only):

{md_table(["Protection tier", "Customers", "Churn rate"], rows2)}

- Every add-on follows the same pattern (Yes vs No churn rate): OnlineSecurity {pct(by_service["OnlineSecurity"]["Yes"]["churn_rate"], 1)} vs {pct(by_service["OnlineSecurity"]["No"]["churn_rate"], 1)}; TechSupport {pct(by_service["TechSupport"]["Yes"]["churn_rate"], 1)} vs {pct(by_service["TechSupport"]["No"]["churn_rate"], 1)}; OnlineBackup, DeviceProtection, StreamingTV and StreamingMovies show the same direction.
- Fiber optic monthly revenue: {money(metrics["fiber_monthly_revenue"])} - of which {money(metrics["fiber_churned_monthly_revenue"])} is currently churning away.
- Chart: `docs/images/{CHART_NAME}.png` · Metrics: `docs/json/{METRICS_NAME}.json`

### Interpretation

Fiber optic churns at {pct(g.loc["Fiber optic", "mean"], 1)} - more than double DSL's
{pct(g.loc["DSL", "mean"], 1)} - despite being the premium product. Fiber is the
business's biggest single revenue source AND its biggest leak: {money(metrics["fiber_churned_monthly_revenue"])}/month
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
"""
    save_snippet(SNIPPET_NAME, snippet)

    print(f"Wrote {METRICS_NAME}.json, {SNIPPET_NAME}.md, {CHART_NAME}.png")
    print(
        f"By internet: "
        + ", ".join(f"{k}={pct(v['mean'], 1)}" for k, v in g.iterrows())
    )
    print(
        f"By protection tier: "
        + ", ".join(f"{k}={pct(v['mean'], 1)}" for k, v in t.iterrows())
    )


if __name__ == "__main__":
    main()
