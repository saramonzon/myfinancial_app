"""Chart helpers for the Streamlit dashboard."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
from plotly.graph_objects import Figure


def wealth_over_time(df: pd.DataFrame) -> Figure:
    return metric_over_time(df, "net_wealth")


def metric_over_time(df: pd.DataFrame, metric: str) -> Figure:
    """Line chart for a selected yearly result metric."""

    if metric not in df.columns:
        raise ValueError(f"Unknown metric: {metric}")
    return px.line(df, x="year", y=metric, color="strategy", markers=True)


def final_net_wealth(df: pd.DataFrame) -> Figure:
    final = df.sort_values("year").groupby("strategy", as_index=False).tail(1)
    return px.bar(
        final,
        x="strategy",
        y="net_wealth",
        color="strategy",
        text_auto=".2s",
    )


def taxes_and_fees(df: pd.DataFrame) -> Figure:
    final = df.sort_values("year").groupby("strategy", as_index=False).tail(1)
    melted = final.melt(
        id_vars=["strategy"],
        value_vars=["taxes_paid", "fees_paid"],
        var_name="metric",
        value_name="amount",
    )
    return px.bar(melted, x="strategy", y="amount", color="metric", barmode="group")


def mortgage_balance(df: pd.DataFrame) -> Figure:
    return px.line(df, x="year", y="mortgage_balance", color="strategy", markers=True)


def sensitivity_heatmap(df: pd.DataFrame) -> Figure:
    """Heatmap of final net wealth across return and commission assumptions."""

    if df.empty:
        raise ValueError("Sensitivity dataframe cannot be empty.")
    pivot = df.pivot(
        index="expected_return",
        columns="annual_commission",
        values="final_net_wealth",
    )
    return px.imshow(
        pivot,
        labels={
            "x": "Annual commission",
            "y": "Expected return",
            "color": "Final net wealth",
        },
        aspect="auto",
        text_auto=".2s",
    )


def final_metric_bar(df: pd.DataFrame, metric: str) -> Figure:
    """Bar chart for any final-year strategy metric."""

    if metric not in df.columns:
        raise ValueError(f"Unknown metric: {metric}")
    final = df.sort_values("year").groupby("strategy", as_index=False).tail(1)
    return px.bar(final, x="strategy", y=metric, color="strategy", text_auto=".2s")
