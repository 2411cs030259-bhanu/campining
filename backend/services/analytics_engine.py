"""
services/analytics_engine.py
Core data-processing engine for campaign datasets.

This module is intentionally decoupled from Flask - it takes a
file path or DataFrame in, and returns plain Python dicts/lists out.
That keeps analytics logic testable and reusable (e.g. by a future
scheduled batch job) without depending on the request/response cycle.
"""

import pandas as pd
import numpy as np

REQUIRED_COLUMNS = [
    "campaign",
    "platform",
    "impressions",
    "clicks",
    "ad_spend",
    "conversions",
    "revenue",
]

NUMERIC_COLUMNS = ["impressions", "clicks", "ad_spend", "conversions", "revenue"]


class AnalyticsError(Exception):
    """Raised when a dataset cannot be processed."""
    pass


def _normalize_column_name(col: str) -> str:
    """'Ad Spend' -> 'ad_spend'"""
    return str(col).strip().lower().replace(" ", "_").replace("-", "_")


def load_and_clean_csv(file_path: str) -> pd.DataFrame:
    """Load a CSV, normalize columns, validate schema, and clean values."""
    try:
        df = pd.read_csv(file_path)
    except Exception as exc:
        raise AnalyticsError("Unable to read this file. Please upload a valid CSV.") from exc

    if df.empty:
        raise AnalyticsError("The uploaded file has no data rows.")

    df.columns = [_normalize_column_name(c) for c in df.columns]

    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise AnalyticsError(
            "Unable to process this file. Missing required columns: " + ", ".join(missing)
        )

    return clean_dataframe(df)


def clean_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Handle missing values and coerce numeric fields."""
    df = df.copy()

    df["campaign"] = df["campaign"].fillna("Unnamed Campaign").astype(str).str.strip()
    df["platform"] = df["platform"].fillna("Unknown").astype(str).str.strip()

    for col in NUMERIC_COLUMNS:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)
        df[col] = df[col].clip(lower=0)  # negative spend/clicks etc. don't make sense

    df = df[df["campaign"] != ""]

    if df.empty:
        raise AnalyticsError("No valid rows remained after cleaning the dataset.")

    return df.reset_index(drop=True)


def _safe_divide(numerator: float, denominator: float) -> float:
    if denominator in (0, 0.0) or pd.isna(denominator):
        return 0.0
    return float(numerator) / float(denominator)


def calculate_kpis(df: pd.DataFrame) -> dict:
    """Calculate the headline KPI set for the whole dataset."""
    total_spend = float(df["ad_spend"].sum())
    total_revenue = float(df["revenue"].sum())
    total_impressions = float(df["impressions"].sum())
    total_clicks = float(df["clicks"].sum())
    total_conversions = float(df["conversions"].sum())

    ctr = _safe_divide(total_clicks, total_impressions)
    cpc = _safe_divide(total_spend, total_clicks)
    cpa = _safe_divide(total_spend, total_conversions)
    roas = _safe_divide(total_revenue, total_spend)

    return {
        "total_spend": round(total_spend, 2),
        "total_revenue": round(total_revenue, 2),
        "total_impressions": int(total_impressions),
        "total_clicks": int(total_clicks),
        "total_conversions": int(total_conversions),
        "ctr": round(ctr * 100, 2),      # expressed as a percentage
        "cpc": round(cpc, 2),
        "cpa": round(cpa, 2),
        "roas": round(roas, 2),
    }


def campaign_breakdown(df: pd.DataFrame) -> list:
    """Per-campaign aggregation, sorted by revenue descending."""
    grouped = df.groupby("campaign", as_index=False).agg(
        ad_spend=("ad_spend", "sum"),
        revenue=("revenue", "sum"),
        clicks=("clicks", "sum"),
        impressions=("impressions", "sum"),
        conversions=("conversions", "sum"),
    )
    grouped["roas"] = grouped.apply(
        lambda r: round(_safe_divide(r["revenue"], r["ad_spend"]), 2), axis=1
    )
    grouped = grouped.sort_values("revenue", ascending=False)
    return grouped.round(2).to_dict(orient="records")


def platform_breakdown(df: pd.DataFrame) -> list:
    """Per-platform aggregation (Facebook / Google / Instagram / etc.)."""
    grouped = df.groupby("platform", as_index=False).agg(
        ad_spend=("ad_spend", "sum"),
        revenue=("revenue", "sum"),
        clicks=("clicks", "sum"),
        impressions=("impressions", "sum"),
    )
    grouped["roas"] = grouped.apply(
        lambda r: round(_safe_divide(r["revenue"], r["ad_spend"]), 2), axis=1
    )
    grouped = grouped.sort_values("revenue", ascending=False)
    return grouped.round(2).to_dict(orient="records")


def generate_insights(kpis: dict, campaigns: list) -> list:
    """Rule-based, human-readable insights derived from the KPIs."""
    insights = []

    if kpis["roas"] < 1:
        insights.append(
            "Your overall ROAS is below 1, which means campaigns are currently generating a loss."
        )
    elif kpis["roas"] >= 4:
        insights.append(
            f"Strong performance: your ROAS of {kpis['roas']} means campaigns are generating "
            f"${kpis['roas']} in revenue for every $1 spent."
        )

    if campaigns:
        best = campaigns[0]
        insights.append(
            f"'{best['campaign']}' generated the highest revenue at ${best['revenue']:,}."
        )

    if kpis["ctr"] < 1:
        insights.append("Your click-through rate is low. Consider improving ad creatives or targeting.")

    if kpis["cpa"] > 0 and kpis["total_conversions"] > 0 and kpis["cpc"] > 0:
        if kpis["cpa"] > (5 * kpis["cpc"]):
            insights.append(
                "Cost per acquisition is high relative to cost per click - review your conversion funnel."
            )

    if not insights:
        insights.append("Campaign performance looks stable. Keep monitoring spend versus revenue.")

    return insights


def analyze_dataset(file_path: str) -> dict:
    """Full pipeline: load, clean, calculate KPIs, breakdowns, and insights."""
    df = load_and_clean_csv(file_path)
    kpis = calculate_kpis(df)
    campaigns = campaign_breakdown(df)
    platforms = platform_breakdown(df)
    insights = generate_insights(kpis, campaigns)

    return {
        "kpis": kpis,
        "campaigns": campaigns,
        "platforms": platforms,
        "insights": insights,
        "row_count": int(len(df)),
    }
