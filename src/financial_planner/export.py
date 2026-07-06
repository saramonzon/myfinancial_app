"""Export helpers for simulation outputs."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from financial_planner.models import SimulationConfig, StrategyResult
from financial_planner.reporting import build_report_bundle
from financial_planner.simulation import results_to_dataframe


def dataframe_to_markdown(df: pd.DataFrame) -> str:
    """Render a small dataframe as a Markdown table without optional dependencies."""

    columns = [str(column) for column in df.columns]
    rows = [columns, ["---"] * len(columns)]
    for record in df.to_dict(orient="records"):
        rows.append([str(record[column]) for column in df.columns])
    return "\n".join("| " + " | ".join(row) + " |" for row in rows)


def config_summary_dataframe(config: SimulationConfig) -> pd.DataFrame:
    """Return editable assumptions in tabular form for auditability."""

    rows: list[dict[str, str | float | int]] = [
        {"section": "household", "name": key, "value": value}
        for key, value in config.household.model_dump().items()
    ]
    rows.extend(
        {"section": "mortgage", "name": key, "value": value}
        for key, value in config.mortgage.model_dump().items()
    )
    rows.extend(
        {"section": "assumptions", "name": key, "value": value}
        for key, value in config.assumptions.model_dump().items()
    )
    rows.extend(
        {"section": "tax", "name": key, "value": str(value)}
        for key, value in config.tax.model_dump().items()
    )
    rows.extend(
        {"section": "planning", "name": key, "value": str(value)}
        for key, value in config.planning.model_dump().items()
    )
    rows.extend(
        {"section": "strategies", "name": key, "value": str(value)}
        for key, value in config.strategies.model_dump().items()
    )
    for product in config.products:
        rows.append(
            {
                "section": "product",
                "name": product.name,
                "value": f"{product.type}, return={product.expected_return}, fee={product.annual_commission}",
            }
        )
    return pd.DataFrame(rows)


def export_results_to_excel(
    results: list[StrategyResult],
    config: SimulationConfig,
    path: str | Path,
) -> Path:
    """Write simulation results and assumptions to an Excel workbook."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    bundle = build_report_bundle(config)
    yearly = results_to_dataframe(results)
    final = yearly.sort_values("year").groupby("strategy", as_index=False).tail(1)
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        yearly.to_excel(writer, index=False, sheet_name="yearly_results")
        final.to_excel(writer, index=False, sheet_name="final_comparison")
        bundle.scenario_summary.to_excel(
            writer, index=False, sheet_name="scenario_summary"
        )
        bundle.sensitivity.to_excel(writer, index=False, sheet_name="sensitivity")
        bundle.product_comparison.to_excel(
            writer, index=False, sheet_name="product_comparison"
        )
        bundle.decision_summary.to_excel(
            writer, index=False, sheet_name="decision_helpers"
        )
        bundle.warnings_table.to_excel(writer, index=False, sheet_name="warnings")
        config_summary_dataframe(config).to_excel(
            writer, index=False, sheet_name="assumptions"
        )
    return output_path


def export_results_to_markdown(
    results: list[StrategyResult],
    config: SimulationConfig,
    path: str | Path,
) -> Path:
    """Write a concise Markdown report with assumptions and final comparison."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    bundle = build_report_bundle(config)
    yearly = results_to_dataframe(results)
    final = yearly.sort_values("year").groupby("strategy", as_index=False).tail(1)
    comparison_columns = [
        "strategy",
        "year",
        "net_wealth",
        "real_net_wealth",
        "gross_wealth",
        "taxes_paid",
        "fees_paid",
        "mortgage_balance",
        "liquidity_gap",
    ]
    lines = [
        "# Financial Planner Report",
        "",
        "Simplified planning model only. This is not financial, tax, or legal advice.",
        "",
        "## Final Comparison",
        "",
        dataframe_to_markdown(final[comparison_columns]),
        "",
        "## Decision Helpers",
        "",
        dataframe_to_markdown(bundle.decision_summary),
        "",
        "## Scenario Summary",
        "",
        dataframe_to_markdown(bundle.scenario_summary),
        "",
        "## Sensitivity Summary",
        "",
        dataframe_to_markdown(bundle.sensitivity),
        "",
        "## Product Comparison",
        "",
        dataframe_to_markdown(bundle.product_comparison),
        "",
        "## Validation Warnings",
        "",
        dataframe_to_markdown(bundle.warnings_table),
        "",
        "## Key Assumptions",
        "",
        dataframe_to_markdown(config_summary_dataframe(config)),
        "",
        "## Model Limitations",
        "",
        "- Tax modelling is simplified and configurable.",
        "- Product assumptions are generic and do not represent specific providers.",
        "- Investment returns are deterministic expected returns, not stochastic forecasts.",
        "- Net wealth assumes liquidation taxes where configured by the strategy.",
        "",
    ]
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path
