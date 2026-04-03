"""
data.py
-------
Data layer for the SaaS Business Performance Dashboard.
Handles dataset generation, KPI calculations, and data-health checks.
Completely independent of Streamlit — importable and testable on its own.
"""

import random
from datetime import datetime, timedelta

import numpy as np
import pandas as pd


# ── Constants ─────────────────────────────────────────────────────────────────

COUNTRIES: dict[str, float] = {
    "United States": 0.30, "United Kingdom": 0.12, "Germany": 0.09,
    "France": 0.07,        "Canada": 0.06,          "Australia": 0.05,
    "Brazil": 0.05,        "India": 0.06,            "Japan": 0.05,
    "Netherlands": 0.04,   "Spain": 0.03,            "Sweden": 0.03,
    "Singapore": 0.02,     "South Africa": 0.02,     "Mexico": 0.01,
}

# tier_name -> (base_price, selection_weight)
TIERS: dict[str, tuple[int, float]] = {
    "Starter":      (29,  0.40),
    "Professional": (79,  0.38),
    "Enterprise":   (299, 0.22),
}

CHURN_PROBABILITY = 0.18
DATASET_START     = datetime(2023, 1, 1)
DATASET_END       = datetime(2024, 1, 1)


# ── Dataset generation ────────────────────────────────────────────────────────

def generate_dataset(n: int = 1200, seed: int = 42) -> pd.DataFrame:
    """
    Generate a mock SaaS subscription dataset with realistic distributions.

    Intentionally injects dirty data (duplicate rows + null Countries) so the
    Data Health section has real issues to surface.

    Parameters
    ----------
    n    : number of base subscribers to generate
    seed : random seed for reproducibility

    Returns
    -------
    pd.DataFrame with columns:
        User ID, Country, Subscription Tier, Monthly Revenue,
        Churn Date, Signup Date
    """
    random.seed(seed)
    np.random.seed(seed)

    countries  = random.choices(list(COUNTRIES.keys()), weights=list(COUNTRIES.values()), k=n)
    tier_names = random.choices(list(TIERS.keys()),    weights=[v[1] for v in TIERS.values()], k=n)
    signup_dates = [DATASET_START + timedelta(days=random.randint(0, 365)) for _ in range(n)]

    monthly_revenue: list[float] = []
    churn_dates: list[str | None] = []

    for tier, sd in zip(tier_names, signup_dates):
        base_price = TIERS[tier][0]
        revenue    = round(base_price + np.random.normal(0, base_price * 0.05), 2)
        monthly_revenue.append(max(revenue, base_price * 0.80))

        if random.random() < CHURN_PROBABILITY:
            churn_d = sd + timedelta(days=random.randint(30, 365))
            churn_dates.append(
                churn_d.strftime("%Y-%m-%d") if churn_d <= DATASET_END else None
            )
        else:
            churn_dates.append(None)

    df = pd.DataFrame({
        "User ID":           [f"USR-{1000 + i}" for i in range(n)],
        "Country":           countries,
        "Subscription Tier": tier_names,
        "Monthly Revenue":   monthly_revenue,
        "Churn Date":        churn_dates,
        "Signup Date":       [d.strftime("%Y-%m-%d") for d in signup_dates],
    })

    # ── Inject dirty data (demo purposes) ────────────────────────────────────
    dup_idx  = random.sample(range(n), 5)
    df       = pd.concat([df, df.iloc[dup_idx]], ignore_index=True)

    null_idx = random.sample(range(len(df)), 8)
    df.loc[null_idx, "Country"] = np.nan

    return df


# ── KPI calculations ──────────────────────────────────────────────────────────

def compute_kpis(df: pd.DataFrame) -> dict:
    """
    Compute core SaaS KPIs from a subscriber DataFrame.

    Returns
    -------
    dict with keys:
        mrr          – Monthly Recurring Revenue (sum of active users' revenue)
        churn_rate   – % of total subscribers who have churned
        arpu         – Average Revenue Per (active) User
        active_count – number of non-churned subscribers
        churned_count
    """
    active        = df[df["Churn Date"].isna()]
    churned_count = int(df["Churn Date"].notna().sum())
    total         = len(df)

    return {
        "mrr":           round(active["Monthly Revenue"].sum(), 2),
        "churn_rate":    round((churned_count / total * 100) if total else 0, 2),
        "arpu":          round(active["Monthly Revenue"].mean(), 2),
        "active_count":  len(active),
        "churned_count": churned_count,
    }


def compute_revenue_trend(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aggregate active subscribers' revenue by signup month.

    Returns
    -------
    pd.DataFrame with columns: Month (Timestamp), MRR (float)
    """
    df2          = df.copy()
    df2["Signup Date"] = pd.to_datetime(df2["Signup Date"])
    df2["Month"] = df2["Signup Date"].dt.to_period("M").dt.to_timestamp()

    return (
        df2[df2["Churn Date"].isna()]
        .groupby("Month")["Monthly Revenue"]
        .sum()
        .reset_index()
        .rename(columns={"Monthly Revenue": "MRR"})
    )


def compute_geo_distribution(df: pd.DataFrame) -> pd.DataFrame:
    """Count subscribers per country (null Countries excluded)."""
    return (
        df.dropna(subset=["Country"])
        .groupby("Country")
        .size()
        .reset_index(name="Users")
    )


def compute_tier_revenue(df: pd.DataFrame) -> pd.DataFrame:
    """Sum monthly revenue by subscription tier, sorted ascending."""
    return (
        df.groupby("Subscription Tier")["Monthly Revenue"]
        .sum()
        .reset_index()
        .sort_values("Monthly Revenue", ascending=True)
    )


# ── Data health checks ────────────────────────────────────────────────────────

def run_health_checks(df: pd.DataFrame) -> dict:
    """
    Run automated data-quality checks on the raw DataFrame.

    Returns
    -------
    dict with keys:
        null_counts   – pd.Series  (nulls per column)
        total_nulls   – int
        dup_count     – int
        total_rows    – int
        total_cols    – int
        completeness  – float (0–100 %)
    """
    null_counts = df.isnull().sum()
    total_nulls = int(null_counts.sum())
    total_rows  = len(df)
    total_cols  = len(df.columns)

    completeness = round(
        (1 - total_nulls / (total_rows * total_cols)) * 100, 2
    ) if total_rows * total_cols > 0 else 100.0

    return {
        "null_counts":  null_counts,
        "total_nulls":  total_nulls,
        "dup_count":    int(df.duplicated().sum()),
        "total_rows":   total_rows,
        "total_cols":   total_cols,
        "completeness": completeness,
    }