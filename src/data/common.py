"""Shared utilities for the Telco business-analysis scripts (Phase 2)."""

from __future__ import annotations

import json
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.figure import Figure

ROOT = Path(__file__).resolve().parents[2]
RAW_PATH = ROOT / "data" / "raw" / "Telco-Customer-Churn.csv"
DOCS_DIR = ROOT / "docs"
JSON_DIR = DOCS_DIR / "json"
SNIPPETS_DIR = DOCS_DIR / "snippets"
IMAGES_DIR = DOCS_DIR / "images"

# Consistent visual identity for all charts
TEAL = "#0F6E84"
CORAL = "#E4572E"
GREY = "#94A3B1"
DARK = "#1F2937"

plt.rcParams.update(
    {
        "figure.facecolor": "white",
        "axes.facecolor": "white",
        "axes.edgecolor": "#CBD5E1",
        "axes.grid": True,
        "grid.color": "#E2E8F0",
        "grid.linewidth": 0.7,
        "axes.axisbelow": True,
        "font.size": 10.5,
        "axes.titlesize": 13,
        "axes.titleweight": "bold",
        "figure.dpi": 110,
    }
)


def load_telco() -> pd.DataFrame:
    """Load the raw dataset with the documented TotalCharges fix.

    Cleaning rule (from docs/data_quality_report.md): coerce TotalCharges to
    numeric; the 11 blank values belong to tenure = 0 customers, impute them
    with tenure x MonthlyCharges (their first invoice).
    """
    df = pd.read_csv(RAW_PATH)
    df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")
    df["TotalCharges"] = df["TotalCharges"].fillna(df["tenure"] * df["MonthlyCharges"])
    df["churn_flag"] = (df["Churn"] == "Yes").astype(int)
    return df


def save_metrics(name: str, payload: dict) -> Path:
    JSON_DIR.mkdir(parents=True, exist_ok=True)
    path = JSON_DIR / f"{name}.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    return path


def save_snippet(name: str, md_text: str) -> Path:
    SNIPPETS_DIR.mkdir(parents=True, exist_ok=True)
    path = SNIPPETS_DIR / f"{name}.md"
    path.write_text(md_text)
    return path


def save_chart(fig: Figure, name: str) -> Path:
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    path = IMAGES_DIR / f"{name}.png"
    fig.tight_layout()
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


def md_table(headers: list[str], rows: list[list]) -> str:
    """Render a list of rows as a GitHub-flavoured Markdown table."""
    lines = ["| " + " | ".join(headers) + " |"]
    lines.append("|" + "|".join(" --- " for _ in headers) + "|")
    for row in rows:
        lines.append("| " + " | ".join(str(c) for c in row) + " |")
    return "\n".join(lines)


def money(v: float) -> str:
    return f"${v:,.0f}"


def pct(v: float, nd: int = 1) -> str:
    return f"{v * 100:.{nd}f}%"
