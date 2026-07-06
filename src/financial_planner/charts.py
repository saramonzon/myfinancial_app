"""Chart helpers for the Streamlit dashboard."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
from plotly.graph_objects import Figure

from financial_planner.localization import metric_label, translate_value


def _localized_plot_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    localized = df.copy()
    if "strategy" in localized.columns:
        localized["strategy"] = localized["strategy"].map(translate_value)
    return localized


def wealth_over_time(df: pd.DataFrame) -> Figure:
    return metric_over_time(df, "net_wealth")


def metric_over_time(df: pd.DataFrame, metric: str) -> Figure:
    """Line chart for a selected yearly result metric."""

    if metric not in df.columns:
        raise ValueError(f"Unknown metric: {metric}")
    return px.line(
        _localized_plot_dataframe(df),
        x="year",
        y=metric,
        color="strategy",
        markers=True,
        labels={
            "year": "Año",
            metric: metric_label(metric),
            "strategy": "Estrategia",
        },
        title=f"{metric_label(metric)} por año",
    )


def final_net_wealth(df: pd.DataFrame) -> Figure:
    final = _localized_plot_dataframe(
        df.sort_values("year").groupby("strategy", as_index=False).tail(1)
    )
    return px.bar(
        final,
        x="strategy",
        y="net_wealth",
        color="strategy",
        text_auto=".2s",
        labels={
            "strategy": "Estrategia",
            "net_wealth": "Patrimonio neto",
        },
        title="Patrimonio neto final por estrategia",
    )


def taxes_and_fees(df: pd.DataFrame) -> Figure:
    final = _localized_plot_dataframe(
        df.sort_values("year").groupby("strategy", as_index=False).tail(1)
    )
    melted = final.melt(
        id_vars=["strategy"],
        value_vars=["taxes_paid", "fees_paid"],
        var_name="metric",
        value_name="amount",
    )
    melted["metric"] = melted["metric"].map(metric_label)
    return px.bar(
        melted,
        x="strategy",
        y="amount",
        color="metric",
        barmode="group",
        labels={
            "strategy": "Estrategia",
            "amount": "Importe",
            "metric": "Métrica",
        },
        title="Impuestos y comisiones",
    )


def mortgage_balance(df: pd.DataFrame) -> Figure:
    return px.line(
        _localized_plot_dataframe(df),
        x="year",
        y="mortgage_balance",
        color="strategy",
        markers=True,
        labels={
            "year": "Año",
            "mortgage_balance": "Saldo de hipoteca",
            "strategy": "Estrategia",
        },
        title="Saldo de hipoteca por año",
    )


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
            "x": "Comisión anual",
            "y": "Rentabilidad esperada",
            "color": "Patrimonio neto final",
        },
        title="Sensibilidad: comisión vs rentabilidad",
        aspect="auto",
        text_auto=".2s",
    )


def final_metric_bar(df: pd.DataFrame, metric: str) -> Figure:
    """Bar chart for any final-year strategy metric."""

    if metric not in df.columns:
        raise ValueError(f"Unknown metric: {metric}")
    final = _localized_plot_dataframe(
        df.sort_values("year").groupby("strategy", as_index=False).tail(1)
    )
    return px.bar(
        final,
        x="strategy",
        y=metric,
        color="strategy",
        text_auto=".2s",
        labels={
            "strategy": "Estrategia",
            metric: metric_label(metric),
        },
        title=f"{metric_label(metric)} final por estrategia",
    )
