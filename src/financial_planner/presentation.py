"""Presentation tables and glossary metadata for dashboard-style outputs."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal

import pandas as pd

from financial_planner.models import SimulationConfig

ColumnCategory = Literal[
    "main",
    "taxes",
    "fees",
    "mortgage",
    "inflation",
    "liquidity",
    "home_equity",
    "planned_spending",
    "advanced",
    "scenario",
]


@dataclass(frozen=True)
class ColumnDefinition:
    column_name: str
    ui_label_es: str
    definition_es: str
    interpretation_es: str
    default_visible: bool
    category: ColumnCategory


DEFAULT_DASHBOARD_COLUMNS: list[str] = [
    "strategy",
    "final_year",
    "gross_wealth_nominal",
    "net_wealth_after_taxes_fees",
    "real_net_wealth_today_euros",
    "total_contributions",
    "net_gain_after_taxes_fees",
    "total_taxes",
    "total_fees",
    "mortgage_balance",
    "planned_spending_cumulative",
    "retirement_target_status",
]

ADVANCED_DASHBOARD_COLUMNS: list[str] = [
    "patrimonio_bruto",
    "patrimonio_neto",
    "patrimonio_neto_real",
    "impuestos_latentes",
    "comisiones",
    "saldo_hipoteca",
    "liquidez",
    "brecha_liquidez",
    "valor_neto_vivienda",
    "patrimonio_sin_vivienda",
    "patrimonio_con_vivienda",
    "rentabilidad_nominal_asumida",
    "inflacion_asumida",
    "rentabilidad_real_aproximada",
    "aportaciones_totales",
    "intereses_hipoteca_ahorrados",
    "ganancia_inversion_esperada_tras_impuestos",
    "diferencia_amortizar_vs_invertir",
    "home_equity",
    "net_worth_including_home",
    "net_worth_excluding_home",
    "investment_value",
    "emergency_fund_balance",
    "travel_life_bucket_balance",
    "home_improvement_bucket_balance",
    "long_term_investment_balance",
    "pension_plan_balance",
    "unit_linked_balance",
    "money_market_balance",
    "remunerated_account_balance",
]


def _definition(
    column_name: str,
    label: str,
    definition: str,
    interpretation: str,
    default_visible: bool,
    category: ColumnCategory,
) -> ColumnDefinition:
    return ColumnDefinition(
        column_name=column_name,
        ui_label_es=label,
        definition_es=definition,
        interpretation_es=interpretation,
        default_visible=default_visible,
        category=category,
    )


COLUMN_DEFINITIONS: dict[str, ColumnDefinition] = {
    definition.column_name: definition
    for definition in [
        _definition(
            "strategy",
            "Estrategia",
            "Plan financiero simulado.",
            "Compara fondo, amortizacion, pension, unit linked o asignacion mixta.",
            True,
            "main",
        ),
        _definition(
            "final_year",
            "Año final",
            "Ultimo año mostrado en la simulacion.",
            "Permite saber hasta que fecha llega el resultado final.",
            True,
            "main",
        ),
        _definition(
            "gross_wealth_nominal",
            "Patrimonio bruto",
            "Patrimonio proyectado antes de impuestos, comisiones, hipoteca y ajustes.",
            "Se muestra en euros nominales futuros.",
            True,
            "main",
        ),
        _definition(
            "net_wealth_after_taxes_fees",
            "Neto tras impuestos y comisiones",
            "Estimacion despues de comisiones, impuestos y saldo hipotecario.",
            "Es mas cercano al dinero liquidable, con fiscalidad simplificada.",
            True,
            "main",
        ),
        _definition(
            "real_net_wealth_today_euros",
            "Patrimonio neto real",
            "Patrimonio neto convertido a euros de hoy mediante inflacion.",
            "Es la mejor columna para entender poder adquisitivo futuro.",
            True,
            "inflation",
        ),
        _definition(
            "total_contributions",
            "Total aportado",
            "Ahorro propio aportado durante la simulacion.",
            "Separa ahorro propio de crecimiento financiero.",
            True,
            "main",
        ),
        _definition(
            "net_gain_after_taxes_fees",
            "Ganancia neta",
            "Patrimonio neto menos aportaciones totales.",
            "Muestra cuanto viene de rentabilidad estimada tras costes e impuestos.",
            True,
            "main",
        ),
        _definition(
            "total_taxes",
            "Impuestos",
            "Impuestos pagados o latentes estimados.",
            "La fiscalidad es simplificada y configurable.",
            True,
            "taxes",
        ),
        _definition(
            "total_fees",
            "Comisiones",
            "Costes y comisiones acumulados.",
            "Ayuda a comparar productos de bajo o alto coste.",
            True,
            "fees",
        ),
        _definition(
            "mortgage_balance",
            "Hipoteca pendiente",
            "Saldo hipotecario estimado en el año final.",
            "Menor saldo implica menos deuda pendiente.",
            True,
            "mortgage",
        ),
        _definition(
            "planned_spending_cumulative",
            "Gasto vital",
            "Gasto planificado en viajes, reformas, coche u otros eventos.",
            "Se trata como gasto intencional, no como perdida de inversion.",
            True,
            "planned_spending",
        ),
        _definition(
            "retirement_target_status",
            "Estado objetivo",
            "Resultado frente al objetivo real de jubilacion configurado.",
            "Indica si hay superavit o deficit en euros de hoy.",
            True,
            "main",
        ),
    ]
}

for column in ADVANCED_DASHBOARD_COLUMNS:
    COLUMN_DEFINITIONS.setdefault(
        column,
        _definition(
            column,
            column.replace("_", " "),
            "Columna avanzada calculada por el modelo.",
            "Usala para auditoria o diagnostico detallado.",
            False,
            "advanced",
        ),
    )


def column_tooltips() -> dict[str, str]:
    """Return Streamlit-compatible help text for every known presentation column."""

    return {
        name: f"{definition.definition_es} {definition.interpretation_es}"
        for name, definition in COLUMN_DEFINITIONS.items()
    }


def glossary_dataframe() -> pd.DataFrame:
    """Return the export glossary with labels, definitions, and default visibility."""

    return pd.DataFrame([definition.__dict__ for definition in COLUMN_DEFINITIONS.values()])


def retirement_target_status(real_net_wealth: float, target: float) -> str:
    """Return a compact Spanish target status string."""

    difference = real_net_wealth - target
    if difference >= 0:
        return f"superavit {difference:,.2f}"
    return f"deficit {abs(difference):,.2f}"


def dashboard_dataframe(final: pd.DataFrame, config: SimulationConfig) -> pd.DataFrame:
    """Return the simplified final-strategy table for UI and report exports."""

    rows: list[dict[str, float | str | bool]] = []
    for record in final.to_dict(orient="records"):
        net_after_taxes = float(record.get("net_liquidable_wealth", record["net_wealth"]))
        real_net = float(record["real_net_wealth"])
        total_contributions = float(record.get("total_contributions", 0.0))
        taxes = float(record.get("taxes_paid", 0.0)) + float(
            record.get("latent_taxes", 0.0)
        )
        fees = float(record.get("fees_paid", 0.0))
        assumptions = record.get("assumptions", {})
        expected_return = (
            assumptions.get("expected_return", "")
            if isinstance(assumptions, dict)
            else ""
        )
        real_return = (
            ((1 + float(expected_return)) / (1 + config.assumptions.inflation) - 1)
            if expected_return != ""
            else ""
        )
        rows.append(
            {
                "strategy": record["strategy"],
                "final_year": record["year"],
                "gross_wealth_nominal": record["gross_wealth"],
                "net_wealth_after_taxes_fees": net_after_taxes,
                "real_net_wealth_today_euros": real_net,
                "total_contributions": total_contributions,
                "net_gain_after_taxes_fees": net_after_taxes - total_contributions,
                "total_taxes": taxes,
                "total_fees": fees,
                "mortgage_balance": record["mortgage_balance"],
                "planned_spending_cumulative": record.get(
                    "planned_spending_cumulative", 0.0
                ),
                "retirement_target_status": retirement_target_status(
                    real_net, config.planning.retirement_target_real
                ),
                "target_success": real_net >= config.planning.retirement_target_real,
                "surplus_vs_target_real": max(
                    real_net - config.planning.retirement_target_real, 0.0
                ),
                "shortfall_vs_target_real": max(
                    config.planning.retirement_target_real - real_net, 0.0
                ),
                "recommended_available_life_spending": max(
                    real_net - config.planning.retirement_target_real, 0.0
                ),
                "patrimonio_bruto": record["gross_wealth"],
                "patrimonio_neto": record["net_wealth"],
                "patrimonio_neto_real": real_net,
                "impuestos_latentes": record.get("latent_taxes", 0.0),
                "comisiones": fees,
                "saldo_hipoteca": record["mortgage_balance"],
                "liquidez": record.get("liquidity", 0.0),
                "brecha_liquidez": record.get("liquidity_gap", 0.0),
                "valor_neto_vivienda": record.get("home_equity", 0.0),
                "patrimonio_sin_vivienda": record.get(
                    "net_wealth_excluding_home_equity", 0.0
                ),
                "patrimonio_con_vivienda": record.get(
                    "net_wealth_including_home_equity", 0.0
                ),
                "rentabilidad_nominal_asumida": expected_return,
                "inflacion_asumida": config.assumptions.inflation,
                "rentabilidad_real_aproximada": real_return,
                "aportaciones_totales": total_contributions,
                "intereses_hipoteca_ahorrados": 0.0,
                "ganancia_inversion_esperada_tras_impuestos": 0.0,
                "diferencia_amortizar_vs_invertir": 0.0,
                "home_equity": record.get("home_equity", 0.0),
                "net_worth_including_home": record.get(
                    "net_wealth_including_home_equity", 0.0
                ),
                "net_worth_excluding_home": record.get(
                    "net_wealth_excluding_home_equity", 0.0
                ),
                "investment_value": record.get("investment_balance", 0.0),
                "emergency_fund_balance": record.get("emergency_fund_balance", 0.0),
                "travel_life_bucket_balance": record.get(
                    "travel_life_bucket_balance", 0.0
                ),
                "home_improvement_bucket_balance": record.get(
                    "home_improvement_bucket_balance", 0.0
                ),
                "long_term_investment_balance": record.get(
                    "long_term_investment_balance", 0.0
                ),
                "pension_plan_balance": record.get("pension_balance", 0.0),
                "unit_linked_balance": record.get("unit_linked_balance", 0.0),
                "money_market_balance": record.get("money_market_balance", 0.0),
                "remunerated_account_balance": record.get(
                    "remunerated_account_balance", 0.0
                ),
            }
        )
    return pd.DataFrame(rows)


def dashboard_kpis(dashboard: pd.DataFrame) -> dict[str, float | str]:
    """Return compact KPI values from the simplified dashboard table."""

    if dashboard.empty:
        return {}
    return {
        "best_real_net_wealth": dashboard["real_net_wealth_today_euros"].max(),
        "best_net_after_taxes_fees": dashboard["net_wealth_after_taxes_fees"].max(),
        "lowest_fees": dashboard["total_fees"].min(),
        "lowest_taxes": dashboard["total_taxes"].min(),
        "lowest_mortgage_balance": dashboard["mortgage_balance"].min(),
        "highest_planned_life_spending": dashboard[
            "planned_spending_cumulative"
        ].max(),
        "retirement_target_surplus_shortfall": dashboard[
            "surplus_vs_target_real"
        ].max()
        - dashboard["shortfall_vs_target_real"].max(),
    }


def bucket_plan_dataframe(config: SimulationConfig) -> pd.DataFrame:
    """Return configured bucket priorities and annual amounts for auditability."""

    buckets = config.planning.buckets
    rows = [
        {
            "bucket": "emergency_fund",
            "purpose": "Colchon de seguridad.",
            "product": buckets.emergency_fund.product,
            "priority": buckets.emergency_fund.priority,
            "target": buckets.emergency_fund.target,
            "annual_amount": 0.0,
        },
        {
            "bucket": "travel_and_life",
            "purpose": "Viajes, ocio y calidad de vida.",
            "product": buckets.travel_and_life.product,
            "priority": buckets.travel_and_life.priority,
            "target": 0.0,
            "annual_amount": buckets.travel_and_life.annual_budget,
        },
        {
            "bucket": "home_improvements",
            "purpose": "Reformas, muebles, electrodomesticos y mantenimiento.",
            "product": buckets.home_improvements.product,
            "priority": buckets.home_improvements.priority,
            "target": 0.0,
            "annual_amount": buckets.home_improvements.annual_budget,
        },
        {
            "bucket": "long_term_investment",
            "purpose": "Jubilacion o patrimonio de largo plazo.",
            "product": buckets.long_term_investment.product,
            "priority": buckets.long_term_investment.priority,
            "target": 0.0,
            "annual_amount": buckets.long_term_investment.annual_contribution,
        },
        {
            "bucket": "mortgage_extra_amortization",
            "purpose": "Reducir deuda hipotecaria.",
            "product": "mortgage_prepayment",
            "priority": buckets.mortgage_extra_amortization.priority,
            "target": 0.0,
            "annual_amount": buckets.mortgage_extra_amortization.annual_amount,
        },
    ]
    return pd.DataFrame(rows)
