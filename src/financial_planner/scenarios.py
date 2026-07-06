"""Scenario manager for creating validated simulation variants."""

from __future__ import annotations

from financial_planner.models import ScenarioConfig, SimulationConfig, StrategyResult
from financial_planner.simulation import run_simulation


def apply_scenario(config: SimulationConfig, scenario: ScenarioConfig) -> SimulationConfig:
    """Return a validated config with scenario overrides applied."""

    data = config.model_dump()
    if scenario.annual_savings is not None:
        data["household"]["annual_savings"] = scenario.annual_savings
    if scenario.inflation is not None:
        data["assumptions"]["inflation"] = scenario.inflation
    if scenario.salary_growth is not None:
        data["assumptions"]["salary_growth"] = scenario.salary_growth
    if scenario.mortgage_interest_rate is not None:
        data["mortgage"]["annual_interest_rate"] = scenario.mortgage_interest_rate

    if scenario.expected_return_shift or scenario.commission_shift:
        for product in data["products"]:
            product["expected_return"] = max(
                min(product["expected_return"] + scenario.expected_return_shift, 1.0),
                -1.0,
            )
            product["annual_commission"] = max(
                min(product["annual_commission"] + scenario.commission_shift, 1.0),
                0.0,
            )
    return SimulationConfig.model_validate(data)


def configured_scenarios(config: SimulationConfig) -> list[tuple[str, SimulationConfig]]:
    """Return baseline plus all configured scenario variants."""

    scenarios = [("baseline", config)]
    scenarios.extend(
        (scenario.name, apply_scenario(config, scenario))
        for scenario in config.scenario_manager.scenarios
    )
    return scenarios


def run_scenarios(config: SimulationConfig) -> dict[str, list[StrategyResult]]:
    """Run the simulation for baseline and configured scenarios."""

    return {
        scenario_name: run_simulation(scenario_config)
        for scenario_name, scenario_config in configured_scenarios(config)
    }
