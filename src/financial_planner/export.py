"""Export helpers for simulation outputs."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from financial_planner.localization import (
    localize_dataframe,
    localize_display_dataframe,
    translate_value,
)
from financial_planner.models import SimulationConfig, StrategyResult
from financial_planner.presentation import DEFAULT_DASHBOARD_COLUMNS
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
    with pd.ExcelWriter(output_path, engine="openpyxl") as writer:
        bundle.dashboard[DEFAULT_DASHBOARD_COLUMNS].to_excel(
            writer, index=False, sheet_name="Dashboard"
        )
        localize_dataframe(yearly).to_excel(
            writer, index=False, sheet_name="Full results"
        )
        bundle.glossary.to_excel(writer, index=False, sheet_name="Glossary")
        bundle.bucket_plan.to_excel(writer, index=False, sheet_name="Bucket plan")
        bundle.mortgage_vs_invest.to_excel(writer, index=False, sheet_name="Mortgage vs invest")
        bundle.scenario_summary.to_excel(writer, index=False, sheet_name="Scenarios")
        bundle.scenario_templates.to_excel(writer, index=False, sheet_name="Scenario templates")
        bundle.monte_carlo.to_excel(writer, index=False, sheet_name="Monte Carlo")
        localize_dataframe(bundle.sensitivity).to_excel(writer, index=False, sheet_name="Sensitivity")
        localize_dataframe(bundle.sanity_check).to_excel(writer, index=False, sheet_name="Sanity check")
        localize_dataframe(bundle.product_comparison).to_excel(writer, index=False, sheet_name="Products")
        localize_dataframe(bundle.decision_summary).to_excel(writer, index=False, sheet_name="Decisions")
        localize_dataframe(bundle.warnings_table).to_excel(writer, index=False, sheet_name="Warnings")
        localize_dataframe(config_summary_dataframe(config)).to_excel(writer, index=False, sheet_name="Assumptions")
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
    lines = [
        "# Informe de planificación financiera",
        "",
        "Modelo simplificado de planificación. No es asesoramiento financiero, fiscal ni legal.",
        "",
        "## Como leer la tabla",
        "",
        "- El patrimonio bruto es antes de deducciones.",
        "- El neto tras impuestos y comisiones es mas cercano al dinero liquidable.",
        "- El patrimonio neto real convierte euros futuros a poder adquisitivo actual.",
        "- El total aportado es ahorro propio.",
        "- La ganancia neta es rentabilidad estimada despues de impuestos y comisiones.",
        "- Los euros nominales futuros pueden parecer mucho mayores que su valor real.",
        "- El modelo es una herramienta de planificacion, no una prevision.",
        "",
        "## Dashboard",
        "",
        dataframe_to_markdown(
            localize_display_dataframe(bundle.dashboard[DEFAULT_DASHBOARD_COLUMNS])
        ),
        "",
        "## Hipoteca vs inversion",
        "",
        dataframe_to_markdown(localize_display_dataframe(bundle.mortgage_vs_invest)),
        "",
        "## Plan por cubos",
        "",
        dataframe_to_markdown(localize_display_dataframe(bundle.bucket_plan)),
        "",
        "## Ayudantes de decisión",
        "",
        dataframe_to_markdown(localize_display_dataframe(bundle.decision_summary)),
        "",
        "## Resumen de escenarios",
        "",
        dataframe_to_markdown(localize_display_dataframe(bundle.scenario_summary)),
        "",
        "## Plantillas de escenario",
        "",
        dataframe_to_markdown(localize_display_dataframe(bundle.scenario_templates)),
        "",
        "## Comprobación de coherencia",
        "",
        dataframe_to_markdown(localize_display_dataframe(bundle.sanity_check)),
        "",
        "## Monte Carlo",
        "",
        dataframe_to_markdown(localize_display_dataframe(bundle.monte_carlo)),
        "",
        "## Resumen de sensibilidad",
        "",
        dataframe_to_markdown(localize_display_dataframe(bundle.sensitivity)),
        "",
        "## Comparación de productos",
        "",
        dataframe_to_markdown(localize_display_dataframe(bundle.product_comparison)),
        "",
        "## Avisos de validación",
        "",
        dataframe_to_markdown(localize_display_dataframe(bundle.warnings_table)),
        "",
        "## Supuestos clave",
        "",
        dataframe_to_markdown(localize_display_dataframe(config_summary_dataframe(config))),
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
