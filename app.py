"""Streamlit entrypoint for the financial planner v1.0 dashboard."""

from __future__ import annotations

from pathlib import Path

import pandas as pd
import streamlit as st

from financial_planner.charts import (
    final_metric_bar,
    final_net_wealth,
    metric_over_time,
    mortgage_balance,
    sensitivity_heatmap,
    taxes_and_fees,
    wealth_over_time,
)
from financial_planner.config import load_config
from financial_planner.export import export_results_to_excel, export_results_to_markdown
from financial_planner.localization import (
    format_number_for_display,
    localize_display_dataframe,
    metric_label,
    translate_value,
)
from financial_planner.products import generic_product_templates
from financial_planner.reporting import build_report_bundle

DEFAULT_INPUTS = Path("data/inputs.example.yaml")
DEFAULT_PRODUCTS = Path("data/products.example.yaml")
DEFAULT_EXCEL_EXPORT = Path("outputs/resultados_v1_0.xlsx")
DEFAULT_MARKDOWN_EXPORT = Path("outputs/informe_v1_0.md")


st.set_page_config(page_title="Planificador financiero", layout="wide")

st.title("Planificador financiero")
st.caption("Herramienta genérica de planificación financiera familiar a largo plazo para España.")

with st.sidebar:
    st.header("Configuración")
    inputs_path = Path(st.text_input("YAML de entradas", value=str(DEFAULT_INPUTS)))
    products_path = Path(st.text_input("YAML de productos", value=str(DEFAULT_PRODUCTS)))
    run_button = st.button("Ejecutar simulación", type="primary")

required_state_keys = {
    "bundle",
    "config",
    "results",
    "results_df",
    "sensitivity_df",
    "warnings",
    "product_comparison_df",
    "break_even",
    "amortize_vs_invest",
}

if run_button or not required_state_keys.issubset(st.session_state.keys()):
    try:
        config = load_config(inputs_path, products_path)
        bundle = build_report_bundle(config)
        results = bundle.results
        st.session_state["config"] = config
        st.session_state["bundle"] = bundle
        st.session_state["results"] = results
        st.session_state["results_df"] = bundle.yearly
        st.session_state["sensitivity_df"] = bundle.sensitivity
        st.session_state["warnings"] = bundle.warnings
        st.session_state["product_comparison_df"] = bundle.product_comparison
        st.session_state["break_even"] = bundle.break_even
        st.session_state["amortize_vs_invest"] = bundle.amortize_vs_invest
    except (
        Exception
    ) as exc:  # pragma: no cover - Streamlit displays the validation detail.
        st.error(f"Error de configuración o simulación: {exc}")
        st.stop()

config = st.session_state["config"]
bundle = st.session_state["bundle"]
results = st.session_state["results"]
results_df = st.session_state["results_df"]
sensitivity_df = st.session_state["sensitivity_df"]
warnings = st.session_state["warnings"]
product_comparison_df = st.session_state["product_comparison_df"]
break_even = st.session_state["break_even"]
amortize_vs_invest = st.session_state["amortize_vs_invest"]

with st.sidebar:
    st.header("Filtros")
    all_strategies = sorted(results_df["strategy"].unique().tolist())
    selected_strategies = st.multiselect(
        "Estrategias",
        options=all_strategies,
        default=all_strategies,
        format_func=translate_value,
    )
    min_year = int(results_df["year"].min())
    max_year = int(results_df["year"].max())
    selected_years = st.slider("Años", min_year, max_year, (min_year, max_year))
    metric_options = [
        "net_wealth",
        "real_net_wealth",
        "gross_wealth",
        "taxes_paid",
        "fees_paid",
        "mortgage_balance",
        "liquidity_gap",
    ]
    metric = st.selectbox(
        "Métrica",
        options=metric_options,
        format_func=metric_label,
    )

filtered_df = results_df.loc[
    (results_df["strategy"].isin(selected_strategies))
    & (results_df["year"].between(selected_years[0], selected_years[1]))
]

if filtered_df.empty:
    st.warning("Ninguna fila coincide con los filtros seleccionados.")
    st.stop()

st.subheader("Supuestos")
left, middle, right = st.columns(3)
left.metric("Ahorro anual", format_number_for_display(config.household.annual_savings))
middle.metric("Tipo de hipoteca", f"{config.mortgage.annual_interest_rate:.2%}")
right.metric("Edad de jubilación", config.household.retirement_age)

if warnings:
    st.subheader("Avisos de validación")
    warnings_df = pd.DataFrame([warning.__dict__ for warning in warnings])
    st.dataframe(localize_display_dataframe(warnings_df), width="stretch")

overview_tab, simulation_tab, decision_tab, scenario_tab, product_tab, export_tab = (
    st.tabs(["Resumen", "Simulación", "Decisiones", "Escenarios", "Productos", "Exportaciones"])
)

with overview_tab:
    st.subheader("Comparación de estrategias")
    final_rows = (
        filtered_df.sort_values("year").groupby("strategy", as_index=False).tail(1)
    )
    st.dataframe(
        localize_display_dataframe(
            final_rows[
                [
                    "strategy",
                    "year",
                    "net_wealth",
                    "real_net_wealth",
                    "gross_wealth",
                    "taxes_paid",
                    "fees_paid",
                    "mortgage_balance",
                    "liquidity",
                    "liquidity_gap",
                ]
            ]
        ),
        width="stretch",
    )
    chart_left, chart_right = st.columns(2)
    chart_left.plotly_chart(
        metric_over_time(filtered_df, metric),
        width="stretch",
        key="metric_over_time_chart",
    )
    chart_right.plotly_chart(
        final_metric_bar(filtered_df, metric),
        width="stretch",
        key="final_metric_bar_chart",
    )
    chart_left.plotly_chart(
        wealth_over_time(filtered_df),
        width="stretch",
        key="wealth_over_time_chart",
    )
    chart_right.plotly_chart(
        final_net_wealth(filtered_df),
        width="stretch",
        key="final_net_wealth_chart",
    )

with simulation_tab:
    st.subheader("Simulación anual")
    st.dataframe(localize_display_dataframe(filtered_df), width="stretch")
    chart_left, chart_right = st.columns(2)
    chart_left.plotly_chart(
        taxes_and_fees(filtered_df),
        width="stretch",
        key="taxes_and_fees_chart",
    )
    chart_right.plotly_chart(
        mortgage_balance(filtered_df),
        width="stretch",
        key="mortgage_balance_chart",
    )

with decision_tab:
    st.subheader("Ayudantes de decisión")
    decision_left, decision_right = st.columns(2)
    decision_left.metric(
        "Comisión de equilibrio",
        (
            "No se cruza"
            if break_even.break_even_commission is None
            else f"{break_even.break_even_commission:.2%}"
        ),
    )
    decision_left.caption(
        f"{translate_value(break_even.strategy)} vs {translate_value(break_even.benchmark_strategy)}"
    )
    decision_right.metric(
        "Diferencia amortizar vs invertir",
        format_number_for_display(amortize_vs_invest.difference),
    )
    decision_right.caption(
        f"Opción preferida por los supuestos: {translate_value(amortize_vs_invest.preferred_option)}"
    )
    if amortize_vs_invest.liquidity_warning:
        st.warning("La liquidez actual está por debajo del objetivo antes de asignar ahorro extra.")
    st.dataframe(localize_display_dataframe(bundle.decision_summary), width="stretch")

with scenario_tab:
    st.subheader("Resumen de escenarios")
    st.dataframe(localize_display_dataframe(bundle.scenario_summary), width="stretch")
    st.subheader("Plantillas de escenario")
    st.dataframe(localize_display_dataframe(bundle.scenario_templates), width="stretch")
    st.subheader("Comprobación de coherencia")
    st.warning("Los euros nominales futuros no equivalen a poder adquisitivo actual.")
    st.dataframe(localize_display_dataframe(bundle.sanity_check), width="stretch")
    if not bundle.monte_carlo.empty:
        st.subheader("Monte Carlo")
        st.dataframe(localize_display_dataframe(bundle.monte_carlo), width="stretch")
    st.subheader("Sensibilidad")
    st.dataframe(localize_display_dataframe(sensitivity_df), width="stretch")
    st.plotly_chart(
        sensitivity_heatmap(sensitivity_df),
        width="stretch",
        key="sensitivity_heatmap_chart",
    )

with product_tab:
    st.subheader("Comparación de productos")
    st.dataframe(localize_display_dataframe(product_comparison_df), width="stretch")
    st.subheader("Plantillas de producto")
    templates_df = pd.DataFrame(
        [template.__dict__ for template in generic_product_templates()]
    )
    st.dataframe(localize_display_dataframe(templates_df), width="stretch")

with export_tab:
    st.subheader("Exportaciones")
    export_path = export_results_to_excel(results, config, DEFAULT_EXCEL_EXPORT)
    st.download_button(
        "Descargar Excel",
        data=export_path.read_bytes(),
        file_name=export_path.name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    markdown_path = export_results_to_markdown(results, config, DEFAULT_MARKDOWN_EXPORT)
    st.download_button(
        "Descargar informe Markdown",
        data=markdown_path.read_bytes(),
        file_name=markdown_path.name,
        mime="text/markdown",
    )

st.caption(
    "Modelo simplificado de planificación. No es asesoramiento financiero, fiscal ni legal."
)
