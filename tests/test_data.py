"""Data quality tests (Phase 1 rules, kept executable)."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW_PATH = ROOT / "data" / "raw" / "Telco-Customer-Churn.csv"

CATEGORICAL_DOMAINS = {
    "gender": {"Female", "Male"},
    "Partner": {"Yes", "No"},
    "Dependents": {"Yes", "No"},
    "PhoneService": {"Yes", "No"},
    "MultipleLines": {"No", "Yes", "No phone service"},
    "InternetService": {"DSL", "Fiber optic", "No"},
    "Contract": {"Month-to-month", "One year", "Two year"},
    "PaperlessBilling": {"Yes", "No"},
    "PaymentMethod": {
        "Electronic check",
        "Mailed check",
        "Bank transfer (automatic)",
        "Credit card (automatic)",
    },
    "Churn": {"Yes", "No"},
}


def test_raw_file_exists():
    assert RAW_PATH.exists(), "Raw dataset missing from data/raw/"


def test_shape_and_key():
    df = pd.read_csv(RAW_PATH)
    assert df.shape == (7043, 21)
    assert df["customerID"].is_unique, "customerID must be a clean primary key"


def test_no_duplicate_rows():
    df = pd.read_csv(RAW_PATH)
    assert df.duplicated().sum() == 0


def test_total_charges_blanks_are_exactly_the_tenure_zero_customers():
    df = pd.read_csv(RAW_PATH)
    total_numeric = pd.to_numeric(df["TotalCharges"], errors="coerce")
    assert int(total_numeric.isna().sum()) == 11
    assert (df.loc[total_numeric.isna(), "tenure"] == 0).all()


def test_categorical_domains_match_data_dictionary():
    df = pd.read_csv(RAW_PATH)
    for col, domain in CATEGORICAL_DOMAINS.items():
        assert set(df[col].unique()) == domain, f"Unexpected values in {col}"


def test_numeric_bounds():
    df = pd.read_csv(RAW_PATH)
    assert df["tenure"].between(0, 72).all()
    assert df["MonthlyCharges"].between(0, 200).all()
    assert (df["SeniorCitizen"].isin([0, 1])).all()


def test_class_distribution_within_expected_band():
    df = pd.read_csv(RAW_PATH)
    churn_rate = (df["Churn"] == "Yes").mean()
    assert 0.20 <= churn_rate <= 0.35, (
        "Churn base rate drifted outside the audited band"
    )
