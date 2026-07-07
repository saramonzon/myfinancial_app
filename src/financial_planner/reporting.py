"""Shared reporting tables for dashboard and exports."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import pandas as pd

from financial_planner.decision import (
    AmortizeVsInvestDecision,
    BreakEvenCommissionResult,
    amortize_vs_invest_decision,
    break_even_commission,
)
from financial_planner.models import SimulationConfig, StrategyResult
from financial_planner.monte_carlo import monte_carlo_summary
from financial_planner.products import product_comparison_dataframe
from financial_planner.scenarios import run_scenarios, scenario_templates
from financial_planner.sensitivity import commission_return_sensitivity
from financial_planner.simulation import results_to_dataframe, run_simulation
from financial_planner.warnings import ValidationWarning, validation_warnings


@dataclass(frozen=True)
class ReportBundle:
    """All derived outputs needed by dashboard and export layers."""

    config: SimulationConfig
    results: list[StrategyResult]
    yearly: pd.DataFrame
    final: pd.DataFrame
    scenarios: dict[str, list[StrategyResult]]
    scenario_summary: pd.DataFrame
    sensitivity: pd.DataFrame
    warnings: list[ValidationWarning]
    warnings_table: pd.DataFrame
    product_comparison: pd.DataFrame
    break_even: BreakEvenCommissionResult
    amortize_vs_invest: AmortizeVsInvestDecision
    decision_summary: pd.DataFrame
    sanity_check: pd.DataFrame
    monte_carlo: pd.DataFrame
    scenario_templates: pd.DataFrame


def final_results_dataframe(yearly: pd.DataFrame) -> pd.DataFrame:
    """Return one final row per strategy from yearly results."""

    if yearly.empty:
        return yearly.copy()
    return yearly.sort_values("year").groupby("strategy", as_index=False).tail(1)


def scenario_summary_dataframe(
    scenarios: dict[str, list[StrategyResult]],
) -> pd.DataFrame:
    """Flatten final strategy results for every configured scenario."""

    rows: list[dict[str, float | str]] = []
    for scenario_name, scenario_results in scenarios.items():
        scenario_df = results_to_dataframe(scenario_results)
        scenario_final = final_results_dataframe(scenario_df)
        for record in scenario_final.to_dict(orient="records"):
            rows.append(
                {
                    "scenario": scenario_name,
                    "strategy": record["strategy"],
                    "year": record["year"],
                    "net_wealth": record["net_wealth"],
                    "real_net_wealth": record["real_net_wealth"],
                    "gross_wealth": record["gross_wealth"],
                    "taxes_paid": record["taxes_paid"],
                    "fees_paid": record["fees_paid"],
                    "mortgage_balance": record["mortgage_balance"],
                    "liquidity_gap": record["liquidity_gap"],
                }
            )
    return pd.DataFrame(rows)


def warnings_dataframe(warnings: list[ValidationWarning]) -> pd.DataFrame:
    """Convert validation warnings to a stable dataframe."""

    if not warnings:
        return pd.DataFrame(columns=["code", "message", "severity"])
    return pd.DataFrame([asdict(warning) for warning in warnings])


def decision_summary_dataframe(
    break_even: BreakEvenCommissionResult,
    amortize_vs_invest: AmortizeVsInvestDecision,
) -> pd.DataFrame:
    """Return decision-helper outputs in an export-friendly table."""

    return pd.DataFrame(
        [
            {
                "helper": "break_even_commission",
                "metric": "break_even_commission",
                "value": break_even.break_even_commission,
                "detail": f"{break_even.strategy} vs {break_even.benchmark_strategy}",
            },
            {
                "helper": "break_even_commission",
                "metric": "target_net_wealth",
                "value": break_even.target_net_wealth,
                "detail": f"product_type={break_even.product_type}",
            },
            {
                "helper": "amortize_vs_invest",
                "metric": "mortgage_interest_saved",
                "value": amortize_vs_invest.mortgage_interest_saved,
                "detail": "extra amortization scenario",
            },
            {
                "helper": "amortize_vs_invest",
                "metric": "expected_after_tax_investment_gain",
                "value": amortize_vs_invest.expected_after_tax_investment_gain,
                "detail": "investment fund scenario",
            },
            {
                "helper": "amortize_vs_invest",
                "metric": "difference",
                "value": amortize_vs_invest.difference,
                "detail": f"preferred={amortize_vs_invest.preferred_option}",
            },
        ]
    )


def sanity_check_dataframe(config: SimulationConfig, final: pd.DataFrame) -> pd.DataFrame:
    """Return audit rows explaining scale and realism of final values."""

    rows: list[dict[str, float | str | int]] = []
    simulation_years = int(final["year"].max() - config.household.current_year + 1)
    for record in final.to_dict(orient="records"):
        expected_return = ""
        assumptions = record.get("assumptions", {})
        if isinstance(assumptions, dict):
            expected_return = assumptions.get("expected_return", "")
        rows.append(
            {
                "strategy": record["strategy"],
                "simulation_years": simulation_years,
                "annual_savings_assumed": config.household.annual_savings,
                "total_contributions": record.get("total_contributions", 0.0),
                "assumed_nominal_return": expected_return,
                "assumed_inflation": config.assumptions.inflation,
                "real_return_approximation": (
                    ((1 + float(expected_return)) / (1 + config.assumptions.inflation) - 1)
                    if expected_return != ""
                    else ""
                ),
                "total_fees": record.get("fees_paid", 0.0),
                "estimated_taxes": record.get("taxes_paid", 0.0),
                "latent_taxes": record.get("latent_taxes", 0.0),
                "final_nominal_value": record.get("net_wealth", 0.0),
                "final_real_value": record.get("real_net_wealth", 0.0),
                "nominal_warning": "Nominal future euros are not current purchasing power.",
            }
        )
    return pd.DataFrame(rows)


def scenario_template_summary_dataframe(config: SimulationConfig) -> pd.DataFrame:
    """Return final net wealth summaries for built-in scenario templates."""

    rows: list[dict[str, float | str]] = []
    for name, scenario_config in scenario_templates(config).items():
        scenario_results = run_simulation(scenario_config)
        scenario_final = final_results_dataframe(results_to_dataframe(scenario_results))
        for record in scenario_final.to_dict(orient="records"):
            rows.append(
                {
                    "scenario_template": name,
                    "strategy": record["strategy"],
                    "net_wealth": record["net_wealth"],
                    "real_net_wealth": record["real_net_wealth"],
                    "total_contributions": record.get("total_contributions", 0.0),
                }
            )
    return pd.DataFrame(rows)


def build_report_bundle(config: SimulationConfig) -> ReportBundle:
    """Run all v1.0 reporting calculations from one validated config."""

    results = run_simulation(config)
    yearly = results_to_dataframe(results)
    final = final_results_dataframe(yearly)
    scenarios = run_scenarios(config)
    sensitivity = commission_return_sensitivity(config)
    warnings = validation_warnings(config)
    break_even = break_even_commission(config)
    amortize_vs_invest = amortize_vs_invest_decision(config)
    sanity_check = sanity_check_dataframe(config, final)
    return ReportBundle(
        config=config,
        results=results,
        yearly=yearly,
        final=final,
        scenarios=scenarios,
        scenario_summary=scenario_summary_dataframe(scenarios),
        sensitivity=sensitivity,
        warnings=warnings,
        warnings_table=warnings_dataframe(warnings),
        product_comparison=product_comparison_dataframe(config.products),
        break_even=break_even,
        amortize_vs_invest=amortize_vs_invest,
        decision_summary=decision_summary_dataframe(break_even, amortize_vs_invest),
        sanity_check=sanity_check,
        monte_carlo=monte_carlo_summary(config),
        scenario_templates=scenario_template_summary_dataframe(config),
    )
