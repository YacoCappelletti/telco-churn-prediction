"""Pydantic schemas for the Telco churn prediction API.

Input validation mirrors the data dictionary: categorical domains match the
observed value sets; numeric fields carry physical bounds so malformed
inputs are rejected with 422 responses.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field

GenderType = Literal["Female", "Male"]
YesNoType = Literal["Yes", "No"]
MultipleLinesType = Literal["No", "Yes", "No phone service"]
InternetServiceType = Literal["DSL", "Fiber optic", "No"]
AddOnType = Literal["No", "Yes", "No internet service"]
ContractType = Literal["Month-to-month", "One year", "Two year"]
PaymentMethodType = Literal[
    "Electronic check",
    "Mailed check",
    "Bank transfer (automatic)",
    "Credit card (automatic)",
]


class PredictionInput(BaseModel):
    """One customer observation (all model features, no target)."""

    gender: GenderType = Field(description="Customer gender")
    SeniorCitizen: int = Field(ge=0, le=1, description="Senior flag (0/1)")
    Partner: YesNoType = Field(description="Has partner")
    Dependents: YesNoType = Field(description="Has dependents")
    tenure: int = Field(ge=0, le=72, description="Tenure in completed months")
    PhoneService: YesNoType = Field(description="Has phone service")
    MultipleLines: MultipleLinesType = Field(description="Multiple phone lines")
    InternetService: InternetServiceType = Field(description="Internet service type")
    OnlineSecurity: AddOnType = Field(description="Online security add-on")
    OnlineBackup: AddOnType = Field(description="Online backup add-on")
    DeviceProtection: AddOnType = Field(description="Device protection add-on")
    TechSupport: AddOnType = Field(description="Tech support add-on")
    StreamingTV: AddOnType = Field(description="Streaming TV add-on")
    StreamingMovies: AddOnType = Field(description="Streaming movies add-on")
    Contract: ContractType = Field(description="Contract type")
    PaperlessBilling: YesNoType = Field(description="Paperless billing")
    PaymentMethod: PaymentMethodType = Field(description="Payment method")
    MonthlyCharges: float = Field(ge=0, le=500, description="Monthly charge in USD")
    TotalCharges: float = Field(
        ge=0, le=20000, description="Total accumulated charges in USD"
    )


class ContributingFactor(BaseModel):
    feature: str
    direction: Literal["increases_risk", "decreases_risk"]
    description: str


class CustomerRisk(BaseModel):
    """Risk summary block: probability, binary prediction and business band."""

    churn_probability: float = Field(
        ge=0,
        le=1,
        description="Churn probability (positive class = churn)",
    )
    prediction: Literal["Yes", "No"] = Field(
        description="Churn prediction at the 0.5 decision threshold"
    )
    risk_level: Literal["high", "medium", "low"] = Field(
        description="Business risk band (thresholds in configs/model_config.json)"
    )


class PredictionOutput(BaseModel):
    customer_risk: CustomerRisk = Field(description="Risk summary block")
    contributing_factors: list[ContributingFactor]
    business_recommendation: str
    model_version: str
    model_name: str
    timestamp: str


class HealthOutput(BaseModel):
    status: str
    model_loaded: bool
    model_name: str
    model_version: str
    timestamp: str
