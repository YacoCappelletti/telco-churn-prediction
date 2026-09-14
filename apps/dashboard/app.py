"""Phase 7 - Business dashboard (Streamlit) for the Telco churn analysis.

Communicates the Phase 2 business insights with KPIs, the 5 selected
business questions, filters by relevant dimensions, and interpretation +
recommended actions. Answers: What happened? Why? What should we do?

KPIs, charts and per-question interpretations follow the sidebar filters;
the executive summary is the global Phase-2 synthesis (unfiltered).

Run: make dashboard
"""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[2]
DOCS_JSON = ROOT / "docs" / "json"

st.set_page_config(page_title="Telco Churn Dashboard", page_icon="📊", layout="wide")

TEAL = "#0F6E84"
CORAL = "#E4572E"
DARK = "#1F2937"


@st.cache_data
def load_data() -> pd.DataFrame:
    df = pd.read_csv(ROOT / "data" / "raw" / "Telco-Customer-Churn.csv")
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    df["TotalCharges"] = df["TotalCharges"].fillna(df["tenure"] * df["MonthlyCharges"])
    df["churn_flag"] = (df["Churn"] == "Yes").astype(int)
    return df


@st.cache_data
def load_json(name: str) -> dict:
    return json.loads((DOCS_JSON / f"{name}.json").read_text())


def style_ax(ax):
    ax.spines[["top", "right"]].set_visible(False)
    ax.grid(axis="y", color="#E2E8F0", lw=0.7)
    ax.set_axisbelow(True)


def fmt_pct(value) -> str:
    return f"{value:.1%}" if pd.notna(value) else "n/a"


def rate_bar(
    ax,
    groups: pd.Series,
    counts: pd.Series,
    title: str,
    xlabel: str = "",
    overall_rate: float | None = None,
):
    rates = (groups * 100).dropna()
    counts = counts.reindex(rates.index)
    if not len(rates):
        ax.set_title(title)
        ax.text(
            0.5,
            0.5,
            "no data under current filters",
            ha="center",
            va="center",
            transform=ax.transAxes,
            color=DARK,
        )
        style_ax(ax)
        return
    colors = [CORAL if r == rates.max() else TEAL for r in rates]
    ax.bar(rates.index.astype(str), rates.values, color=colors, width=0.6, zorder=3)
    for i, (rate, n) in enumerate(zip(rates.values, counts.values)):
        ax.text(
            i,
            rate + 0.8,
            f"{rate:.1f}%\n(n={n:,})",
            ha="center",
            fontsize=9,
            color=DARK,
        )
    if overall_rate is not None:
        ax.axhline(overall_rate * 100, color=DARK, lw=1.2, ls="--")
        ax.text(
            len(rates) - 0.4,
            overall_rate * 100 + 1.0,
            f"overall {overall_rate * 100:.1f}%",
            ha="right",
            fontsize=9,
            color=DARK,
        )
    ax.set_ylabel("Churn rate (%)")
    if xlabel:
        ax.set_xlabel(xlabel)
    ax.set_title(title)
    ax.set_ylim(0, rates.max() * 1.28)
    style_ax(ax)


df = load_data()
insights = load_json("insights")

st.title("Telco Customer Churn - Business Dashboard 📊")
st.caption(
    "Answers: What happened? · Why did it happen? · What should the business do? · Data: 7,043-customer snapshot"
)

# --- Filters ---------------------------------------------------------------
st.sidebar.header("Filters")
contracts = st.sidebar.multiselect(
    "Contract type",
    ["Month-to-month", "One year", "Two year"],
    default=["Month-to-month", "One year", "Two year"],
)
internet = st.sidebar.multiselect(
    "Internet service",
    ["Fiber optic", "DSL", "No"],
    default=["Fiber optic", "DSL", "No"],
)
payments = st.sidebar.multiselect(
    "Payment method",
    [
        "Electronic check",
        "Mailed check",
        "Bank transfer (automatic)",
        "Credit card (automatic)",
    ],
    default=[
        "Electronic check",
        "Mailed check",
        "Bank transfer (automatic)",
        "Credit card (automatic)",
    ],
)
tenure_max = st.sidebar.slider("Max tenure (months)", 1, 72, 72)

fdf = df[
    df["Contract"].isin(contracts)
    & df["InternetService"].isin(internet)
    & df["PaymentMethod"].isin(payments)
    & (df["tenure"] <= tenure_max)
]

# --- KPIs -------------------------------------------------------------------
overall = float(fdf["churn_flag"].mean()) if len(fdf) else 0.0
mrr = float(fdf["MonthlyCharges"].sum())
mrr_at_risk = float(fdf.loc[fdf["churn_flag"] == 1, "MonthlyCharges"].sum())
churned_bills = fdf.loc[fdf["churn_flag"] == 1, "MonthlyCharges"]
retained_bills = fdf.loc[fdf["churn_flag"] == 0, "MonthlyCharges"]
arpu_churned = float(churned_bills.mean()) if len(churned_bills) else 0.0
arpu_retained = float(retained_bills.mean()) if len(retained_bills) else 0.0

st.markdown("## KPIs (filtered)")
k1, k2, k3, k4, k5 = st.columns(5)
k1.metric("Customers", f"{len(fdf):,}")
k2.metric(
    "Churn rate",
    f"{overall:.1%}",
    help="Share of customers flagged as churned in the filtered base",
)
k3.metric("Monthly revenue (MRR)", f"${mrr:,.0f}")
k4.metric(
    "MRR at risk (churned)",
    f"${mrr_at_risk:,.0f}",
    help="Monthly revenue held by churned customers",
)
k5.metric(
    "ARPU churned vs retained",
    f"\\${arpu_churned:.0f} vs \\${arpu_retained:.0f}",
    help="Mean monthly bill of churned vs retained customers",
)

if len(fdf) == 0:
    st.error(
        "No customers match the current filters - the charts and "
        "interpretations below are hidden. Widen the filters to explore."
    )
elif len(fdf) < 50:
    st.warning(
        "The current filter leaves fewer than 50 customers - interpret rates with caution."
    )

# --- Executive answers -------------------------------------------------------
st.markdown("## Executive summary")
st.caption("Global synthesis - not affected by the sidebar filters.")
syn = insights["synthesis"]
c1, c2, c3 = st.columns(3)
c1.error(f"**What happened?**\n\n{syn['what_happened']}")
c2.warning(f"**Why did it happen?**\n\n{syn['why_it_happened']}")
c3.success(f"**What should the business do?**\n\n{syn['what_to_do']}")

# --- Q1 ---------------------------------------------------------------------
st.markdown("## Q1 · Churn by contract type")
st.caption(
    "Business lever: contract-migration program (biggest single lever - see interpretation)."
)
if len(fdf):
    fig, ax = plt.subplots(figsize=(7.2, 4))
    g1 = (
        fdf.groupby("Contract")["churn_flag"]
        .agg(["count", "mean"])
        .reindex(["Month-to-month", "One year", "Two year"])
    )
    rate_bar(
        ax, g1["mean"], g1["count"], "Churn rate by contract type", overall_rate=overall
    )
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

    mm = g1["mean"].get("Month-to-month")
    ty = g1["mean"].get("Two year")
    mm_rev_share = (
        fdf.loc[
            (fdf["churn_flag"] == 1) & (fdf["Contract"] == "Month-to-month"),
            "MonthlyCharges",
        ].sum()
        / mrr_at_risk
        if mrr_at_risk
        else float("nan")
    )
    if pd.notna(mm) and pd.notna(ty):
        tail = (
            f", and carries ~{mm_rev_share:.0%} of the churned revenue in this view."
            if pd.notna(mm_rev_share)
            else "."
        )
        interpretation = f"Month-to-month churns at {fmt_pct(mm)} vs {fmt_pct(ty)} for two-year terms{tail}"
    else:
        interpretation = "; ".join(
            f"{idx} churns at {fmt_pct(row['mean'])} (n={int(row['count']):,})"
            for idx, row in g1.dropna(subset=["mean"]).iterrows()
        )
    st.markdown(
        f"**Interpretation (filtered view):** {interpretation}\n\n"
        "**Recommended action:** Contract-migration program: incentivize month-to-month customers "
        "to 1-2 year terms; track churn-by-contract monthly."
    )

# --- Q2 ---------------------------------------------------------------------
st.markdown("## Q2 · Churn across the customer lifecycle")
st.caption("Business lever: 90-day onboarding program for early-tenure customers.")
if len(fdf):
    # Same tenure-bucket edges as the Phase 2 script (scripts/q02_tenure_vs_churn.py)
    bins = [0, 7, 13, 25, 49, 61, 72]
    labels = ["0-6", "7-12", "13-24", "25-48", "49-60", "61-72"]
    cut = pd.cut(fdf["tenure"], bins=bins, labels=labels)
    g2 = (
        fdf.groupby(cut, observed=True)["churn_flag"]
        .agg(["count", "mean"])
        .reindex(labels)
    )
    fig, ax = plt.subplots(figsize=(7.2, 4))
    rate_bar(
        ax,
        g2["mean"],
        g2["count"],
        "Churn rate by tenure bucket",
        xlabel="Months since signup",
        overall_rate=overall,
    )
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

    early = g2["mean"].get("0-6")
    late = g2["mean"].get("61-72")
    churned_n = int(fdf["churn_flag"].sum())
    first12_share = (
        fdf.loc[(fdf["churn_flag"] == 1) & (fdf["tenure"] <= 12)].shape[0] / churned_n
        if churned_n
        else float("nan")
    )
    if pd.notna(early) and pd.notna(late):
        interpretation = (
            f"Risk decays from {fmt_pct(early)} in the first 6 months to {fmt_pct(late)} "
            f"after five years in this view; first-year customers generate "
            f"{fmt_pct(first12_share)} of the churn shown."
        )
    else:
        interpretation = "; ".join(
            f"{idx} months churn at {fmt_pct(row['mean'])} (n={int(row['count']):,})"
            for idx, row in g2.dropna(subset=["mean"]).iterrows()
        )
    st.markdown(
        f"**Interpretation (filtered view):** {interpretation}\n\n"
        "**Recommended action:** Stand up a 90-day onboarding program (setup call, first-invoice check, "
        "expectation management) with month-3/6 cohort survival as its KPI."
    )

# --- Q3 ---------------------------------------------------------------------
st.markdown("## Q3 · Internet service and protection add-ons")
st.caption("Business lever: fiber quality investigation + protection bundling.")
if len(fdf):
    col_a, col_b = st.columns(2)
    fig1, ax1 = plt.subplots(figsize=(5.6, 4))
    g3 = (
        fdf.groupby("InternetService")["churn_flag"]
        .agg(["count", "mean"])
        .reindex(["Fiber optic", "DSL", "No"])
    )
    rate_bar(ax1, g3["mean"], g3["count"], "By internet service", overall_rate=overall)
    col_a.pyplot(fig1, use_container_width=True)
    plt.close(fig1)

    def tier(row):
        protected = (row["OnlineSecurity"] == "Yes") + (row["TechSupport"] == "Yes")
        return "None" if protected == 0 else ("One" if protected == 1 else "Both")

    sub = fdf[fdf["InternetService"] != "No"].copy()
    fig2, ax2 = plt.subplots(figsize=(5.6, 4))
    g3b = None
    if len(sub):
        g3b = (
            sub.assign(tier=sub.apply(tier, axis=1))
            .groupby("tier")["churn_flag"]
            .agg(["count", "mean"])
            .reindex(["None", "One", "Both"])
        )
        rate_bar(
            ax2,
            g3b["mean"],
            g3b["count"],
            "By protection (Security/Support)",
            overall_rate=overall,
        )
    col_b.pyplot(fig2, use_container_width=True)
    plt.close(fig2)

    fib = g3["mean"].get("Fiber optic")
    dsl = g3["mean"].get("DSL")
    both = g3b["mean"].get("Both") if g3b is not None else None
    none_prot = g3b["mean"].get("None") if g3b is not None else None
    parts = []
    if pd.notna(fib) and pd.notna(dsl):
        parts.append(f"Fiber churns at {fmt_pct(fib)} vs {fmt_pct(dsl)} for DSL")
    else:
        parts.append(
            "internet churn in this view: "
            + "; ".join(
                f"{idx} {fmt_pct(row['mean'])} (n={int(row['count']):,})"
                for idx, row in g3.dropna(subset=["mean"]).iterrows()
            )
        )
    if pd.notna(both) and pd.notna(none_prot):
        parts.append(
            f"customers with both protection add-ons churn at {fmt_pct(both)} "
            f"vs {fmt_pct(none_prot)} without them"
        )
    interpretation = "; ".join(parts)
    st.markdown(
        f"**Interpretation (filtered view):** {interpretation}.\n\n"
        "**Recommended action:** 1) Root-cause fiber quality; 2) bundle Security + Support into fiber "
        "onboarding; 3) track the protected-vs-unprotected churn gap."
    )

# --- Q4 ---------------------------------------------------------------------
st.markdown("## Q4 · Revenue at risk by price band")
st.caption("Business lever: revenue-weighted retention budget.")
if len(fdf):
    band_bins = [0, 35, 70, 95, 130]
    band_labels = ["$0-35", "$35-70", "$70-95", "$95+"]
    cut = pd.cut(fdf["MonthlyCharges"], bins=band_bins, labels=band_labels)
    g4 = fdf.groupby(cut, observed=True).apply(
        lambda x: pd.Series(
            {
                "customers": len(x),
                "churn_rate": x["churn_flag"].mean(),
                "mrr_churned": x.loc[x["churn_flag"] == 1, "MonthlyCharges"].sum(),
            }
        ),
        include_groups=False,
    )
    fig, ax = plt.subplots(figsize=(7.2, 4))
    vals = g4["mrr_churned"].fillna(0)
    colors = [CORAL if v == vals.max() else TEAL for v in vals]
    ax.bar(vals.index.astype(str), vals.values, color=colors, width=0.6, zorder=3)
    for i, v in enumerate(vals.values):
        ax.text(
            i, v + mrr_at_risk * 0.02, f"${v:,.0f}", ha="center", fontsize=9, color=DARK
        )
    ax.set_ylabel("Churned monthly revenue ($)")
    ax.set_title("Monthly revenue at risk by price band")
    style_ax(ax)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

    mrr_share = mrr_at_risk / mrr if mrr else float("nan")
    top_band = vals.idxmax() if vals.max() > 0 else None
    interpretation = (
        f"Churners carry higher bills (ARPU \\${arpu_churned:.0f} vs \\${arpu_retained:.0f} "
        f"in this view); {fmt_pct(mrr_share)} of the filtered MRR (\\${mrr_at_risk:,.0f}/mo) "
        f"sits in churned accounts"
        + (f", with the {top_band} band holding the largest share" if top_band else "")
        + "."
    )
    st.markdown(
        f"**Interpretation (filtered view):** {interpretation}\n\n"
        "**Recommended action:** Weight retention spend by monthly revenue at risk; audit the $95+ "
        "premium bundle's price-value gap; report MRR-at-risk as the primary KPI."
    )

# --- Q5 ---------------------------------------------------------------------
st.markdown("## Q5 · Payment method and billing mode")
st.caption("Business lever: A/B-tested migration to automatic payments.")
if len(fdf):
    fig, ax = plt.subplots(figsize=(7.2, 4))
    g5 = (
        fdf.groupby("PaymentMethod")["churn_flag"]
        .agg(["count", "mean"])
        .reindex(
            [
                "Electronic check",
                "Mailed check",
                "Bank transfer (automatic)",
                "Credit card (automatic)",
            ]
        )
    )
    rate_bar(
        ax,
        g5["mean"],
        g5["count"],
        "Churn rate by payment method",
        overall_rate=overall,
    )
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

    echeck = g5["mean"].get("Electronic check")
    auto_vals = [
        g5["mean"].get(m)
        for m in ["Bank transfer (automatic)", "Credit card (automatic)"]
    ]
    auto_min = min((r for r in auto_vals if pd.notna(r)), default=None)
    echeck_paperless = fdf.loc[
        (fdf["PaymentMethod"] == "Electronic check")
        & (fdf["PaperlessBilling"] == "Yes"),
        "churn_flag",
    ]
    cell_rate = (
        float(echeck_paperless.mean()) if len(echeck_paperless) else float("nan")
    )
    parts = []
    if pd.notna(echeck):
        ratio = echeck / auto_min if auto_min is not None and auto_min > 0 else None
        parts.append(
            f"Electronic-check customers churn at {fmt_pct(echeck)}"
            + (f" (~{ratio:.0f}x the automatic methods in this view)" if ratio else "")
        )
    if pd.notna(cell_rate):
        parts.append(
            f"e-check + paperless is the leakiest cell at {fmt_pct(cell_rate)}"
        )
    interpretation = (
        "; ".join(parts) if parts else "not enough data under the current filters"
    )
    st.markdown(
        f"**Interpretation (filtered view):** {interpretation}. "
        "Correlation, not proven causation.\n\n"
        "**Recommended action:** A/B-test an incentive to migrate e-check customers to automatic "
        "payments, starting with the e-check + paperless cell."
    )

# --- Footer -----------------------------------------------------------------
st.divider()
st.caption(
    "Evidence: analysis scripts and metrics in docs/. Cross-sectional snapshot; "
    "correlations are not causal effects."
)
