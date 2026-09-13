"""Phase 7 - Business dashboard (Streamlit) for the Telco churn analysis.

Communicates the Phase 2 business insights with KPIs, the 5 selected
business questions, filters by relevant dimensions, and interpretation +
recommended actions. Answers: What happened? Why? What should we do?

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


def rate_bar(ax, groups: pd.Series, counts: pd.Series, title: str, xlabel: str = ""):
    rates = groups * 100
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
    ax.axhline(overall * 100, color=DARK, lw=1.2, ls="--")
    ax.text(
        len(rates) - 0.4,
        overall * 100 + 1.0,
        f"overall {overall * 100:.1f}%",
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
q_metrics = {
    name: load_json(name)
    for name in [
        "q01_metrics",
        "q02_metrics",
        "q03_metrics",
        "q04_metrics",
        "q05_metrics",
    ]
}

st.title("Telco Customer Churn - Business Dashboard 📊")
st.caption(
    "Phase 7 deliverable · Answers: What happened? · Why did it happen? · What should the business do? · Data: 7,043-customer snapshot"
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
arpu_churned = float(fdf.loc[fdf["churn_flag"] == 1, "MonthlyCharges"].mean() or 0)
arpu_retained = float(fdf.loc[fdf["churn_flag"] == 0, "MonthlyCharges"].mean() or 0)

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
    f"${arpu_churned:.0f} vs ${arpu_retained:.0f}",
    help="Mean monthly bill of churned vs retained customers",
)

if len(fdf) < 50:
    st.warning(
        "The current filter leaves fewer than 50 customers - interpret rates with caution."
    )

# --- Executive answers -------------------------------------------------------
st.markdown("## Executive summary")
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
    g = (
        fdf.groupby("Contract")["churn_flag"]
        .agg(["count", "mean"])
        .reindex(["Month-to-month", "One year", "Two year"])
    )
    rate_bar(ax, g["mean"], g["count"], "Churn rate by contract type")
    st.pyplot(fig)
    plt.close(fig)
b = q_metrics["q01_metrics"]["by_contract"]
st.markdown(
    f"**Interpretation:** Month-to-month churns at {b['Month-to-month']['churn_rate']:.1%} vs "
    f"{b['Two year']['churn_rate']:.1%} for two-year terms, and carries ~87% of all churned revenue.\n\n"
    "**Recommended action:** Contract-migration program: incentivize month-to-month customers "
    "to 1-2 year terms; track churn-by-contract monthly."
)

# --- Q2 ---------------------------------------------------------------------
st.markdown("## Q2 · Churn across the customer lifecycle")
st.caption("Business lever: 90-day onboarding program for early-tenure customers.")
if len(fdf):
    bins = [0, 6, 12, 24, 48, 60, 72]
    labels = ["0-6", "7-12", "13-24", "25-48", "49-60", "61-72"]
    cut = pd.cut(fdf["tenure"], bins=bins, labels=labels)
    g2 = fdf.groupby(cut, observed=True)["churn_flag"].agg(["count", "mean"])
    fig, ax = plt.subplots(figsize=(7.2, 4))
    rate_bar(
        ax,
        g2["mean"],
        g2["count"],
        "Churn rate by tenure bucket",
        xlabel="Months since signup",
    )
    st.pyplot(fig)
    plt.close(fig)
q2 = q_metrics["q02_metrics"]
st.markdown(
    f"**Interpretation:** Risk decays from {q2['churn_rate_by_tenure_bucket']['0-6']['churn_rate']:.1%} "
    f"(first 6 months) to {q2['churn_rate_by_tenure_bucket']['61-72']['churn_rate']:.1%} after five years; "
    f"first-year customers generate {q2['first_12_months_share_of_all_churn']:.0%} of all churn.\n\n"
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
    rate_bar(ax1, g3["mean"], g3["count"], "By internet service")
    col_a.pyplot(fig1)
    plt.close(fig1)

    def tier(row):
        protected = (row["OnlineSecurity"] == "Yes") + (row["TechSupport"] == "Yes")
        return "None" if protected == 0 else ("One" if protected == 1 else "Both")

    sub = fdf[fdf["InternetService"] != "No"].copy()
    fig2, ax2 = plt.subplots(figsize=(5.6, 4))
    if len(sub):
        g3b = (
            sub.assign(tier=sub.apply(tier, axis=1))
            .groupby("tier")["churn_flag"]
            .agg(["count", "mean"])
            .reindex(["None", "One", "Both"])
        )
        rate_bar(ax2, g3b["mean"], g3b["count"], "By protection (Security/Support)")
    col_b.pyplot(fig2)
    plt.close(fig2)
q3 = q_metrics["q03_metrics"]
st.markdown(
    f"**Interpretation:** Fiber churns at {q3['churn_rate_by_internet_service']['Fiber optic']['churn_rate']:.1%} "
    f"vs {q3['churn_rate_by_internet_service']['DSL']['churn_rate']:.1%} for DSL, and customers with both "
    f"protection add-ons churn at {q3['churn_rate_by_protection_tier']['Both Security & Support']['churn_rate']:.1%} "
    f"vs {q3['churn_rate_by_protection_tier']['No protection']['churn_rate']:.1%} without them.\n\n"
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
    st.pyplot(fig)
    plt.close(fig)
q4 = q_metrics["q04_metrics"]
st.markdown(
    f"**Interpretation:** Churners carry higher bills (ARPU ${q4['arpu_churned']} vs "
    f"${q4['arpu_retained']}); 30.5% of all MRR (${q4['churned_monthly_revenue']:,.0f}/mo, "
    f"${q4['annualized_revenue_at_risk']:,.0f} annualized) sits in churned accounts, with the $70-95 "
    "band holding half of it.\n\n"
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
    )
    st.pyplot(fig)
    plt.close(fig)
q5 = q_metrics["q05_metrics"]
st.markdown(
    f"**Interpretation:** Electronic-check customers churn at "
    f"{q5['churn_rate_by_payment_method']['Electronic check']['churn_rate']:.1%} (~3x automatic methods); "
    f"e-check + paperless is the leakiest cell at "
    f"{q5['electronic_check_x_paperless']['echeck_paperless_yes']:.1%}. Correlation, not proven causation.\n\n"
    "**Recommended action:** A/B-test an incentive to migrate e-check customers to automatic "
    "payments, starting with the e-check + paperless cell."
)

# --- Footer -----------------------------------------------------------------
st.divider()
st.caption(
    "Evidence: scripts q01-q05 (docs/snippets), metrics (docs/json), model report and "
    "target approval (Phase 3). Cross-sectional snapshot; correlations are not causal effects."
)
