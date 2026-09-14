"""Supporting charts for the documentation reports (data-audit visuals).

Generates the two figures referenced by docs/data_quality_report.md,
docs/problem_statement.md and docs/target_proposal.md:

- docs/images/dq_class_balance.png        (class balance of the Churn flag)
- docs/images/dq_numeric_distributions.png (tenure + MonthlyCharges hists)

Data-only: uses the raw dataset and the documented TotalCharges fix from
src.data.common.load_telco. No target selection, no model evaluation.

Run: make doc-charts
"""

from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import matplotlib.pyplot as plt

from src.data.common import CORAL, DARK, GREY, TEAL, load_telco, pct, save_chart


def class_balance_chart(df) -> None:
    """Bar chart of the Churn flag split (Yes/No) with counts and shares."""
    counts = df["Churn"].value_counts()  # No / Yes
    total = int(counts.sum())
    yes = counts["Yes"]
    no = counts["No"]

    fig, ax = plt.subplots(figsize=(7.2, 4.2))
    bars = ax.bar(
        ["No (retained)", "Yes (churned)"],
        [no, yes],
        color=[TEAL, CORAL],
        width=0.5,
        zorder=3,
    )
    for bar, n in zip(bars, [no, yes]):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            bar.get_height() + total * 0.015,
            f"{n:,}\n({pct(n / total, 1)})",
            ha="center",
            va="bottom",
            fontsize=10,
            color=DARK,
        )
    ax.set_ylim(0, counts.max() * 1.25)
    ax.set_ylabel("Customers")
    ax.set_title("Class balance of the Churn flag (moderate imbalance, 2.77:1)")
    ax.spines[["top", "right"]].set_visible(False)
    ax.text(
        0.5,
        -0.16,
        f"Source: Telco-Customer-Churn.csv ({total:,} customers) · revenue-weighted impact in business_analysis_report.md",
        transform=ax.transAxes,
        ha="center",
        color=GREY,
        fontsize=8.5,
    )
    save_chart(fig, "dq_class_balance")


def numeric_distributions_chart(df) -> None:
    """Two-panel histogram of the numeric feature distributions."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 4))

    # Tenure: visible spike of brand-new customers at 0-3 months
    ax1.hist(df["tenure"], bins=range(0, 74, 2), color=TEAL, zorder=3)
    med_tenure = df["tenure"].median()
    ax1.axvline(med_tenure, color=DARK, ls="--", lw=1.2, zorder=4)
    ax1.text(
        med_tenure + 1.2,
        ax1.get_ylim()[1] * 0.92,
        f"median {med_tenure:.0f} mo",
        color=DARK,
        fontsize=9,
    )
    ax1.set_xlabel("Tenure (months)")
    ax1.set_ylabel("Customers")
    ax1.set_title("Tenure distribution (spike at 0-3 months)")
    ax1.spines[["top", "right"]].set_visible(False)

    # MonthlyCharges: bimodal, low-charge DSL/no-internet vs premium fiber
    ax2.hist(df["MonthlyCharges"], bins=30, color=TEAL, zorder=3)
    med_charge = df["MonthlyCharges"].median()
    ax2.axvline(med_charge, color=DARK, ls="--", lw=1.2, zorder=4)
    ax2.text(
        med_charge + 1.5,
        ax2.get_ylim()[1] * 0.92,
        f"median ${med_charge:.2f}",
        color=DARK,
        fontsize=9,
    )
    ax2.set_xlabel("Monthly charges ($)")
    ax2.set_ylabel("Customers")
    ax2.set_title("Monthly charges distribution (bimodal)")
    ax2.spines[["top", "right"]].set_visible(False)

    fig.suptitle(
        "Numeric feature distributions - no IQR outliers in any column",
        y=1.02,
        fontsize=13,
        fontweight="bold",
        color=DARK,
    )
    fig.text(
        0.01,
        -0.04,
        "Source: Telco-Customer-Churn.csv (7,043 customers), documented TotalCharges fix.",
        color=GREY,
        fontsize=8.5,
    )
    save_chart(fig, "dq_numeric_distributions")


def main() -> None:
    df = load_telco()
    class_balance_chart(df)
    numeric_distributions_chart(df)
    print(
        "Wrote docs/images/dq_class_balance.png, docs/images/dq_numeric_distributions.png"
    )


if __name__ == "__main__":
    main()
