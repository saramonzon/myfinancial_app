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
from financial_planner.products import generic_product_templates
from financial_planner.reporting import build_report_bundle

DEFAULT_INPUTS = Path("data/inputs.example.yaml")
DEFAULT_PRODUCTS = Path("data/products.example.yaml")
DEFAULT_EXCEL_EXPORT = Path("outputs/v1_0_results.xlsx")
DEFAULT_MARKDOWN_EXPORT = Path("outputs/v1_0_report.md")


st.set_page_config(page_title="Financial Planner", layout="wide")

st.title("Financial Planner")
st.caption("Generic long-term household financial planning tool for Spain.")

with st.sidebar:
    st.header("Configuration")
    inputs_path = Path(st.text_input("Inputs YAML", value=str(DEFAULT_INPUTS)))
    products_path = Path(st.text_input("Products YAML", value=str(DEFAULT_PRODUCTS)))
    run_button = st.button("Run simulation", type="primary")

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
        st.error(f"Configuration or simulation error: {exc}")
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
    st.header("Filters")
    all_strategies = sorted(results_df["strategy"].unique().tolist())
    selected_strategies = st.multiselect(
        "Strategies",
        options=all_strategies,
        default=all_strategies,
    )
    min_year = int(results_df["year"].min())
    max_year = int(results_df["year"].max())
    selected_years = st.slider("Years", min_year, max_year, (min_year, max_year))
    metric = st.selectbox(
        "Metric",
        options=[
            "net_wealth",
            "real_net_wealth",
            "gross_wealth",
            "taxes_paid",
            "fees_paid",
            "mortgage_balance",
            "liquidity_gap",
        ],
    )

filtered_df = results_df.loc[
    (results_df["strategy"].isin(selected_strategies))
    & (results_df["year"].between(selected_years[0], selected_years[1]))
]

if filtered_df.empty:
    st.warning("No rows match the selected dashboard filters.")
    st.stop()

st.subheader("Assumptions")
left, middle, right = st.columns(3)
left.metric("Annual savings", f"{config.household.annual_savings:,.0f}")
middle.metric("Mortgage rate", f"{config.mortgage.annual_interest_rate:.2%}")
right.metric("Retirement age", config.household.retirement_age)

if warnings:
    st.subheader("Validation warnings")
    warnings_df = pd.DataFrame([warning.__dict__ for warning in warnings])
    st.dataframe(warnings_df, width="stretch")

overview_tab, simulation_tab, decision_tab, scenario_tab, product_tab, export_tab = (
    st.tabs(["Overview", "Simulation", "Decisions", "Scenarios", "Products", "Exports"])
)

with overview_tab:
    st.subheader("Strategy comparison")
    final_rows = (
        filtered_df.sort_values("year").groupby("strategy", as_index=False).tail(1)
    )
    st.dataframe(
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
        ],
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
    st.subheader("Yearly simulation")
    st.dataframe(filtered_df, width="stretch")
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
    st.subheader("Decision helpers")
    decision_left, decision_right = st.columns(2)
    decision_left.metric(
        "Break-even commission",
        (
            "Not crossed"
            if break_even.break_even_commission is None
            else f"{break_even.break_even_commission:.2%}"
        ),
    )
    decision_left.caption(f"{break_even.strategy} vs {break_even.benchmark_strategy}")
    decision_right.metric(
        "Amortize vs invest difference",
        f"{amortize_vs_invest.difference:,.0f}",
    )
    decision_right.caption(
        f"Preferred by model assumptions: {amortize_vs_invest.preferred_option}"
    )
    if amortize_vs_invest.liquidity_warning:
        st.warning(amortize_vs_invest.liquidity_warning)
    st.dataframe(bundle.decision_summary, width="stretch")

with scenario_tab:
    st.subheader("Scenario summary")
    st.dataframe(bundle.scenario_summary, width="stretch")
    st.subheader("Sensitivity")
    st.dataframe(sensitivity_df, width="stretch")
    st.plotly_chart(
        sensitivity_heatmap(sensitivity_df),
        width="stretch",
        key="sensitivity_heatmap_chart",
    )

with product_tab:
    st.subheader("Product comparison")
    st.dataframe(product_comparison_df, width="stretch")
    st.subheader("Product templates")
    templates_df = pd.DataFrame(
        [template.__dict__ for template in generic_product_templates()]
    )
    st.dataframe(templates_df, width="stretch")

with export_tab:
    st.subheader("Exports")
    export_path = export_results_to_excel(results, config, DEFAULT_EXCEL_EXPORT)
    st.download_button(
        "Download Excel export",
        data=export_path.read_bytes(),
        file_name=export_path.name,
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )

    markdown_path = export_results_to_markdown(results, config, DEFAULT_MARKDOWN_EXPORT)
    st.download_button(
        "Download Markdown report",
        data=markdown_path.read_bytes(),
        file_name=markdown_path.name,
        mime="text/markdown",
    )

st.caption(
    "Simplified planning model only. This is not financial, tax, or legal advice."
)
