"""Export helpers for simulation outputs."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from financial_planner.localization import localize_dataframe, translate_value
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
                "value": (
                    f"{translate_value(product.type)}, "
                    f"rentabilidad={product.expected_return}, "
                    f"comision={product.annual_commission}"
                ),
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
        localize_dataframe(yearly).to_excel(
            writer, index=False, sheet_name="resultados_anuales"
        )
        localize_dataframe(final).to_excel(
            writer, index=False, sheet_name="comparacion_final"
        )
        localize_dataframe(bundle.scenario_summary).to_excel(
            writer, index=False, sheet_name="escenarios"
        )
        localize_dataframe(bundle.sensitivity).to_excel(
            writer, index=False, sheet_name="sensibilidad"
        )
        localize_dataframe(bundle.product_comparison).to_excel(
            writer, index=False, sheet_name="productos"
        )
        localize_dataframe(bundle.decision_summary).to_excel(
            writer, index=False, sheet_name="decisiones"
        )
        localize_dataframe(bundle.warnings_table).to_excel(
            writer, index=False, sheet_name="avisos"
        )
        localize_dataframe(config_summary_dataframe(config)).to_excel(
            writer, index=False, sheet_name="supuestos"
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
        "# Informe de planificación financiera",
        "",
        "Modelo simplificado de planificación. No es asesoramiento financiero, fiscal ni legal.",
        "",
        "## Comparación final",
        "",
        dataframe_to_markdown(localize_dataframe(final[comparison_columns])),
        "",
        "## Ayudantes de decisión",
        "",
        dataframe_to_markdown(localize_dataframe(bundle.decision_summary)),
        "",
        "## Resumen de escenarios",
        "",
        dataframe_to_markdown(localize_dataframe(bundle.scenario_summary)),
        "",
        "## Resumen de sensibilidad",
        "",
        dataframe_to_markdown(localize_dataframe(bundle.sensitivity)),
        "",
        "## Comparación de productos",
        "",
        dataframe_to_markdown(localize_dataframe(bundle.product_comparison)),
        "",
        "## Avisos de validación",
        "",
        dataframe_to_markdown(localize_dataframe(bundle.warnings_table)),
        "",
        "## Supuestos clave",
        "",
        dataframe_to_markdown(localize_dataframe(config_summary_dataframe(config))),
        "",
        "## Limitaciones del modelo",
        "",
        "- La fiscalidad es simplificada y configurable.",
        "- Los supuestos de producto son genericos y no representan proveedores concretos.",
        "- Las rentabilidades son expectativas deterministas, no previsiones estocasticas.",
        "- El patrimonio neto incorpora impuestos de liquidacion cuando la estrategia lo configura.",
        "",
    ]
    output_path.write_text("\n".join(lines), encoding="utf-8")
    return output_path
