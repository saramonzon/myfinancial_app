"""Scenario manager for creating validated simulation variants."""

from __future__ import annotations

from financial_planner.models import LifeEventConfig, ScenarioConfig, SimulationConfig, StrategyResult
from financial_planner.simulation import run_simulation


def apply_scenario(
    config: SimulationConfig, scenario: ScenarioConfig
) -> SimulationConfig:
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


def configured_scenarios(
    config: SimulationConfig,
) -> list[tuple[str, SimulationConfig]]:
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


def scenario_templates(config: SimulationConfig) -> dict[str, SimulationConfig]:
    """Return generic scenario templates for realism checks."""

    current_year = config.household.current_year
    templates: dict[str, SimulationConfig] = {
        "conservative": apply_scenario(
            config,
            ScenarioConfig(
                name="conservative",
                expected_return_shift=-0.02,
                commission_shift=0.002,
                inflation=config.assumptions.inflation + 0.005,
            ),
        ),
        "base": config,
        "optimistic": apply_scenario(
            config,
            ScenarioConfig(
                name="optimistic",
                expected_return_shift=0.015,
                commission_shift=-0.001,
                inflation=max(config.assumptions.inflation - 0.003, 0.0),
            ),
        ),
        "high_inflation": apply_scenario(
            config,
            ScenarioConfig(name="high_inflation", inflation=config.assumptions.inflation + 0.02),
        ),
        "low_savings": apply_scenario(
            config,
            ScenarioConfig(name="low_savings", annual_savings=config.household.annual_savings * 0.7),
        ),
    }

    bad_decade_data = config.model_dump()
    for product in bad_decade_data["products"]:
        product["expected_return"] = max(product["expected_return"] - 0.03, -1.0)
    templates["bad_first_decade"] = SimulationConfig.model_validate(bad_decade_data)

    interruption_data = config.model_dump()
    interruption_data["planning"]["life_events"].append(
        LifeEventConfig(
            name="job_income_interruption",
            start_year=current_year + 1,
            end_year=current_year + 1,
            recurring_annual_expense=0.0,
            savings_multiplier=0.0,
        ).model_dump()
    )
    templates["job_income_interruption"] = SimulationConfig.model_validate(interruption_data)
    return templates
