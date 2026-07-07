"""Spanish presentation helpers for dashboards and exports."""

from __future__ import annotations

from typing import Any

import pandas as pd


COLUMN_LABELS_ES: dict[str, str] = {
    "strategy": "estrategia",
    "year": "año",
    "age": "edad",
    "gross_wealth": "patrimonio_bruto",
    "net_wealth": "patrimonio_neto",
    "net_liquidable_wealth": "patrimonio_neto_liquidable",
    "real_net_wealth": "patrimonio_neto_real",
    "taxes_paid": "impuestos",
    "latent_taxes": "impuestos_latentes",
    "fees_paid": "comisiones",
    "mortgage_balance": "saldo_hipoteca",
    "home_equity": "valor_neto_vivienda",
    "net_wealth_excluding_home_equity": "patrimonio_sin_vivienda",
    "net_wealth_including_home_equity": "patrimonio_con_vivienda",
    "liquidity": "liquidez",
    "liquidity_gap": "brecha_liquidez",
    "pension_balance": "saldo_plan_pensiones",
    "investment_balance": "saldo_fondo_inversion",
    "unit_linked_balance": "saldo_unit_linked",
    "annual_contribution": "aportacion_anual",
    "withdrawal": "rescate",
    "withdrawal_tax": "impuesto_rescate",
    "out_of_pocket_contribution": "aportacion_de_bolsillo",
    "total_contributions": "aportaciones_totales",
    "investable_savings": "ahorro_invertible",
    "life_event_expenses": "gastos_eventos_vida",
    "extra_mortgage_amortization": "amortizacion_extra_hipoteca",
    "assumptions": "supuestos",
    "scenario": "escenario",
    "expected_return": "rentabilidad_esperada",
    "annual_commission": "comision_anual",
    "final_net_wealth": "patrimonio_neto_final",
    "final_real_net_wealth": "patrimonio_neto_real_final",
    "final_fees_paid": "comisiones_finales",
    "final_taxes_paid": "impuestos_finales",
    "product_type": "tipo_producto",
    "name": "nombre",
    "type": "tipo",
    "insurance_cost": "coste_seguro",
    "total_annual_cost": "coste_anual_total",
    "simple_net_return_before_tax": "rentabilidad_neta_simple_antes_impuestos",
    "tax_treatment": "tratamiento_fiscal",
    "helper": "ayudante",
    "metric": "metrica",
    "value": "valor",
    "detail": "detalle",
    "code": "codigo",
    "message": "mensaje",
    "severity": "severidad",
    "section": "seccion",
    "product_name": "nombre_producto",
    "simulation_years": "años_simulacion",
    "annual_savings_assumed": "ahorro_anual_asumido",
    "assumed_nominal_return": "rentabilidad_nominal_asumida",
    "assumed_inflation": "inflacion_asumida",
    "real_return_approximation": "rentabilidad_real_aproximada",
    "total_fees": "comisiones_totales",
    "estimated_taxes": "impuestos_estimados",
    "final_nominal_value": "valor_nominal_final",
    "final_real_value": "valor_real_final",
    "nominal_warning": "aviso_nominal",
    "scenario_template": "plantilla_escenario",
    "simulations": "simulaciones",
    "final_nominal": "valor_nominal_final",
    "final_real": "valor_real_final",
    "gross_final": "valor_bruto_final",
}

VALUE_LABELS_ES: dict[str, str] = {
    "investment_fund_only": "solo_fondo_inversion",
    "pension_plan_reinvest_tax_saving": "plan_pensiones_reinvierte_ahorro_fiscal",
    "unit_linked": "unit_linked",
    "mortgage_amortization": "amortizacion_hipoteca",
    "mixed_allocation": "asignacion_mixta",
    "investment_fund": "fondo_inversion",
    "money_market_fund": "fondo_monetario",
    "remunerated_account": "cuenta_remunerada",
    "pension_plan": "plan_pensiones",
    "savings_income": "base_ahorro",
    "savings_income_deferred": "base_ahorro_diferida",
    "general_income_on_redemption": "base_general_en_rescate",
    "household": "hogar",
    "mortgage": "hipoteca",
    "assumptions": "supuestos",
    "tax": "fiscalidad",
    "planning": "planificacion",
    "strategies": "estrategias",
    "product": "producto",
    "baseline": "base",
    "warning": "aviso",
    "error": "error",
    "break_even_commission": "comision_equilibrio",
    "amortize_vs_invest": "amortizar_vs_invertir",
    "target_net_wealth": "patrimonio_neto_objetivo",
    "mortgage_interest_saved": "intereses_hipoteca_ahorrados",
    "expected_after_tax_investment_gain": "ganancia_inversion_esperada_tras_impuestos",
    "difference": "diferencia",
    "investment": "inversion",
    "preferred=investment": "preferido=inversion",
    "preferred=mortgage_amortization": "preferido=amortizacion_hipoteca",
    "liquidity_below_target": "liquidez_por_debajo_del_objetivo",
    "conservative": "conservador",
    "optimistic": "optimista",
    "high_inflation": "inflacion_alta",
    "low_savings": "ahorro_bajo",
    "bad_first_decade": "mala_primera_decada",
    "job_income_interruption": "interrupcion_ingresos",
    "Nominal future euros are not current purchasing power.": (
        "Los euros nominales futuros no equivalen a poder adquisitivo actual."
    ),
}

METRIC_LABELS_ES: dict[str, str] = {
    "net_wealth": "Patrimonio neto",
    "real_net_wealth": "Patrimonio neto real",
    "gross_wealth": "Patrimonio bruto",
    "taxes_paid": "Impuestos",
    "fees_paid": "Comisiones",
    "mortgage_balance": "Saldo de hipoteca",
    "liquidity_gap": "Brecha de liquidez",
}

def translate_value(value: Any) -> Any:
    """Translate known display values to Spanish and leave other values unchanged."""

    if isinstance(value, str):
        translated = VALUE_LABELS_ES.get(value, value)
        if translated == value and value.startswith("preferred="):
            preferred_value = value.split("=", maxsplit=1)[1]
            translated = f"preferido={VALUE_LABELS_ES.get(preferred_value, preferred_value)}"
        if translated == value and " vs " in value:
            left, right = value.split(" vs ", maxsplit=1)
            translated = f"{translate_value(left)} vs {translate_value(right)}"
        if translated == value and "=" in value:
            left, right = value.split("=", maxsplit=1)
            translated = f"{translate_value(left)}={translate_value(right)}"
        return translated
    if isinstance(value, dict):
        return {translate_value(key): translate_value(item) for key, item in value.items()}
    if isinstance(value, list):
        return [translate_value(item) for item in value]
    return value


def localize_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """Return a dataframe with Spanish column labels and translated common values."""

    localized = df.copy()
    for column in localized.columns:
        localized[column] = localized[column].map(translate_value)
    return localized.rename(columns=COLUMN_LABELS_ES)


def metric_label(metric: str) -> str:
    """Return a Spanish human label for a metric key."""

    return METRIC_LABELS_ES.get(metric, metric)
