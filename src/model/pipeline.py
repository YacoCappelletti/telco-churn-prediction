"""Model pipeline utilities shared by training scripts and the API."""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

ROOT = Path(__file__).resolve().parents[2]
CONFIG_PATH = ROOT / "configs" / "model_config.json"
RAW_PATH = ROOT / "data" / "raw" / "Telco-Customer-Churn.csv"

TARGET = "Churn"
ID_COLUMN = "customerID"

NUMERIC_FEATURES = ["tenure", "MonthlyCharges", "TotalCharges", "SeniorCitizen"]
CATEGORICAL_FEATURES = [
    "gender",
    "Partner",
    "Dependents",
    "PhoneService",
    "MultipleLines",
    "InternetService",
    "OnlineSecurity",
    "OnlineBackup",
    "DeviceProtection",
    "TechSupport",
    "StreamingTV",
    "StreamingMovies",
    "Contract",
    "PaperlessBilling",
    "PaymentMethod",
]
FEATURES = NUMERIC_FEATURES + CATEGORICAL_FEATURES


def load_config() -> dict:
    with open(CONFIG_PATH) as fh:
        return json.load(fh)


def load_training_data() -> tuple[pd.DataFrame, pd.Series]:
    """Load raw data and return (X, y) with the documented TotalCharges fix.

    y encodes the approved target (Churn) as 1 for 'Yes' (positive class).
    """
    df = pd.read_csv(RAW_PATH)
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    df["TotalCharges"] = df["TotalCharges"].fillna(df["tenure"] * df["MonthlyCharges"])
    y = (df[TARGET] == "Yes").astype(int)
    X = df[FEATURES].copy()
    return X, y


def build_preprocessor() -> ColumnTransformer:
    """Preprocessing pipeline per docs/model_report.md.

    - Numeric: median imputation + standard scaling (required by logistic
      regression; harmless for trees).
    - Categorical: one-hot encoding, unknown categories ignored.
    """
    numeric = Pipeline(
        steps=[
            ("imputer", SimpleImputer(strategy="median")),
            ("scaler", StandardScaler()),
        ]
    )
    categorical = Pipeline(
        steps=[
            ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
        ]
    )
    return ColumnTransformer(
        transformers=[
            ("num", numeric, NUMERIC_FEATURES),
            ("cat", categorical, CATEGORICAL_FEATURES),
        ],
        remainder="drop",
    )


def get_splits(config: dict):
    """Deterministic stratified train/validation/test split.

    Uses the same random_state in both stages so every script reproduces
    identical splits (train 60% / val 20% / test 20% by default).
    """
    from sklearn.model_selection import train_test_split

    X, y = load_training_data()
    rs = config["random_state"]
    test_frac = config["test_fraction"]
    val_frac = config["validation_fraction"]
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_frac, random_state=rs, stratify=y
    )
    val_rel = val_frac / (1.0 - test_frac)
    X_train, X_val, y_train, y_val = train_test_split(
        X_train, y_train, test_size=val_rel, random_state=rs, stratify=y_train
    )
    return X_train, X_val, X_test, y_train, y_val, y_test


def risk_band(probability: float, config: dict | None = None) -> str:
    cfg = config or load_config()
    if probability >= cfg["risk_bands"]["high_min_probability"]:
        return "high"
    if probability >= cfg["risk_bands"]["medium_min_probability"]:
        return "medium"
    return "low"
