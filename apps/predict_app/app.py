"""Phase 6 - Predictive app (Streamlit) for the Telco churn model.

Calls the prediction API (Phase 5) and shows the churn probability,
contributing factors, business recommendation and input warnings.

Run: make predict-app   (expects the API on API_BASE_URL, default localhost:8000)
"""

from __future__ import annotations

import os
from datetime import datetime

import requests
import streamlit as st

API_URL = os.getenv("API_BASE_URL", "http://localhost:8000").rstrip("/")

st.set_page_config(
    page_title="Telco Churn Predictor",
    page_icon="📶",
    layout="wide",
)

CONTRACTS = ["Month-to-month", "One year", "Two year"]
PAYMENTS = [
    "Electronic check",
    "Mailed check",
    "Bank transfer (automatic)",
    "Credit card (automatic)",
]
INTERNET = ["DSL", "Fiber optic", "No"]
ADDONS = ["No", "Yes", "No internet service"]
YES_NO = ["Yes", "No"]
MULTI_LINES = ["No", "Yes", "No phone service"]


@st.cache_data(ttl=30)
def check_api() -> dict | None:
    """Cached health probe (30s TTL) so reruns don't hammer the API."""
    try:
        response = requests.get(f"{API_URL}/health", timeout=5)
        response.raise_for_status()
        return {**response.json(), "_checked_at": datetime.now().strftime("%H:%M:%S")}
    except requests.RequestException:
        return None


def call_api(payload: dict) -> tuple[dict | None, str | None]:
    try:
        response = requests.post(f"{API_URL}/v1/predict", json=payload, timeout=10)
        if response.status_code == 422:
            detail = response.json().get("detail", response.text)
            return None, f"Validation error (422): {detail}"
        response.raise_for_status()
        return response.json(), None
    except requests.ConnectionError:
        return None, (
            f"Cannot reach the API at {API_URL}. Start it with `make api` "
            "or set API_BASE_URL."
        )
    except requests.RequestException as exc:
        return None, f"API request failed: {exc}"


@st.cache_data(ttl=60)
def load_risk_bands() -> dict:
    """Fetch risk-band thresholds from the API model card (source of truth:
    configs/model_config.json). Falls back to the documented defaults."""
    bands = {"high_min_probability": 0.6, "medium_min_probability": 0.35}
    try:
        response = requests.get(f"{API_URL}/v1/model-card", timeout=5)
        response.raise_for_status()
        rb = response.json().get("risk_bands") or {}
        if "high_min_probability" in rb:
            bands["high_min_probability"] = float(rb["high_min_probability"])
        if "medium_min_probability" in rb:
            bands["medium_min_probability"] = float(rb["medium_min_probability"])
    except requests.RequestException:
        pass
    return bands


def build_payload(data: dict) -> tuple[dict, list[str]]:
    """Assemble the API payload and collect consistency warnings."""
    warnings: list[str] = []
    if data["tenure"] == 0 and data["TotalCharges"] > data["MonthlyCharges"] * 1.5:
        warnings.append(
            "A brand-new customer (tenure = 0) with TotalCharges well above one "
            "monthly invoice looks inconsistent - please check the values."
        )
    if data["tenure"] > 1 and data["TotalCharges"] < data["MonthlyCharges"] * 0.25:
        warnings.append(
            "TotalCharges is far below tenure × MonthlyCharges - please verify."
        )
    payload = dict(data)
    payload["SeniorCitizen"] = 1 if data["SeniorCitizen"] else 0
    return payload, warnings


st.title("Telco Churn Predictor 📶")
st.caption(
    "Predicts how likely a customer is to churn, explains the main drivers and "
    "gives a business recommendation. Model: logistic regression v1.0.0 "
    "(target `Churn`, approved in Phase 3)."
)

if st.sidebar.button("Re-check API status"):
    check_api.clear()
health = check_api()
if health and health.get("model_loaded"):
    st.sidebar.success(
        f"API OK · model v{health['model_version']} · {health['_checked_at']}"
    )
elif health:
    st.sidebar.error("API up, but model NOT loaded")
else:
    st.sidebar.error(f"API unreachable at {API_URL} - run `make api`")
st.sidebar.info(f"API: `{API_URL}` · status cached 30s")

with st.form("customer_form"):
    st.subheader("Customer profile")
    col1, col2, col3 = st.columns(3)
    with col1:
        gender = st.selectbox("Gender", ["Female", "Male"])
        senior = st.checkbox("Senior citizen (65+)")
        partner = st.selectbox("Partner", YES_NO)
        dependents = st.selectbox("Dependents", YES_NO)
        tenure = st.number_input("Tenure (months)", 0, 72, 12)
    with col2:
        phone = st.selectbox("Phone service", YES_NO)
        multiple = st.selectbox("Multiple lines", MULTI_LINES)
        internet = st.selectbox("Internet service", INTERNET)
        security = st.selectbox("Online security", ADDONS)
        backup = st.selectbox("Online backup", ADDONS)
    with col3:
        device = st.selectbox("Device protection", ADDONS)
        tech = st.selectbox("Tech support", ADDONS)
        stv = st.selectbox("Streaming TV", ADDONS)
        smovies = st.selectbox("Streaming movies", ADDONS)

    st.subheader("Contract & billing")
    col4, col5, col6 = st.columns(3)
    with col4:
        contract = st.selectbox("Contract", CONTRACTS)
        paperless = st.selectbox("Paperless billing", YES_NO)
    with col5:
        payment = st.selectbox("Payment method", PAYMENTS)
        monthly = st.number_input("Monthly charges ($)", 0.0, 500.0, 70.0, step=0.05)
    with col6:
        total = st.number_input("Total charges ($)", 0.0, 20000.0, 850.0, step=0.05)

    submitted = st.form_submit_button("Predict churn risk", type="primary")

if submitted:
    data = {
        "gender": gender,
        "SeniorCitizen": senior,
        "Partner": partner,
        "Dependents": dependents,
        "tenure": int(tenure),
        "PhoneService": phone,
        "MultipleLines": multiple,
        "InternetService": internet,
        "OnlineSecurity": security,
        "OnlineBackup": backup,
        "DeviceProtection": device,
        "TechSupport": tech,
        "StreamingTV": stv,
        "StreamingMovies": smovies,
        "Contract": contract,
        "PaperlessBilling": paperless,
        "PaymentMethod": payment,
        "MonthlyCharges": float(monthly),
        "TotalCharges": float(total),
    }
    payload, warnings = build_payload(data)

    if warnings:
        st.warning("⚠️ **Input warnings**\n\n" + "\n\n".join(f"- {w}" for w in warnings))

    if not health:
        st.error("The prediction API is unreachable. Start it with `make api`.")
        st.stop()

    result, error = call_api(payload)
    if error:
        st.error(error)
        st.stop()

    risk = result["customer_risk"]
    prob = risk["churn_probability"]
    color = {"high": "#E4572E", "medium": "#E9A03B", "low": "#2E9E6B"}[
        risk["risk_level"]
    ]
    bands = load_risk_bands()

    st.subheader("Prediction")
    m1, m2, m3 = st.columns(3)
    m1.metric(
        "Churn probability",
        f"{prob:.1%}",
        help="Probability of churn for the positive class (Churn = Yes).",
    )
    m2.metric(
        "Risk level",
        risk["risk_level"].upper(),
        help=(
            f"Business bands (from the API model card): high ≥ "
            f"{bands['high_min_probability']:.0%}, medium ≥ "
            f"{bands['medium_min_probability']:.0%}, low below that. "
            "This band drives the business recommendation, not the 0.5 flag."
        ),
    )
    m3.metric(
        "Prediction (0.5 cut)",
        risk["prediction"],
        help=(
            "Binary churn flag at a 0.5 decision threshold, tuned for "
            "precision (test recall ≈ 0.53 at this cut). Retention teams "
            "usually work off the risk bands above or a lower threshold to "
            "prioritize coverage."
        ),
    )
    st.progress(prob, text=f"Churn probability: {prob:.1%}")
    st.markdown(
        f"<div style='padding:6px 12px;border-left:6px solid {color};background:#F8FAFC;'>"
        f"<b>{risk['risk_level'].upper()}</b> risk band</div>",
        unsafe_allow_html=True,
    )

    st.subheader("Main contributing factors")
    for factor in result["contributing_factors"]:
        icon = "🔴" if factor["direction"] == "increases_risk" else "🟢"
        st.markdown(f"- {icon} **{factor['feature']}** — {factor['description']}")

    st.subheader("Business recommendation")
    st.info(result["business_recommendation"])

    st.caption(
        f"Model {result['model_name']} v{result['model_version']} · "
        f"scored at {result['timestamp']}"
    )
