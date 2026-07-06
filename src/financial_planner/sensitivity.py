"""Sensitivity analysis for product commission and expected return assumptions."""

from __future__ import annotations

import pandas as pd

from financial_planner.models import ProductType, SimulationConfig, StrategyName
from financial_planner.simulation import results_to_dataframe, run_simulation


def replace_product_assumptions(
    config: SimulationConfig,
    product_type: ProductType,
    expected_return: float,
    annual_commission: float,
) -> SimulationConfig:
    """Return a validated config with one product's return and commission replaced."""

    data = config.model_dump()
    replaced = False
    for product in data["products"]:
        if product["type"] == product_type:
            product["expected_return"] = expected_return
            product["annual_commission"] = annual_commission
            replaced = True
    if not replaced:
        raise ValueError(f"Missing product for sensitivity analysis: {product_type}")
    return SimulationConfig.model_validate(data)


def commission_return_sensitivity(
    config: SimulationConfig,
    product_type: ProductType | None = None,
    strategy: StrategyName | None = None,
) -> pd.DataFrame:
    """Run a grid of commission and return assumptions and collect final net wealth."""

    sensitivity = config.planning.sensitivity
    selected_product_type = product_type or sensitivity.product_type
    selected_strategy = strategy or sensitivity.strategy
    rows: list[dict[str, float | str]] = []

    for expected_return in sensitivity.expected_returns:
        for annual_commission in sensitivity.commission_rates:
            scenario_config = replace_product_assumptions(
                config,
                selected_product_type,
                expected_return,
                annual_commission,
            )
            df = results_to_dataframe(run_simulation(scenario_config))
            strategy_rows = df.loc[df["strategy"] == selected_strategy]
            if strategy_rows.empty:
                raise ValueError(f"Strategy is not enabled: {selected_strategy}")
            final = strategy_rows.sort_values("year").tail(1).iloc[0]
            rows.append(
                {
                    "strategy": selected_strategy,
                    "product_type": selected_product_type,
                    "expected_return": expected_return,
                    "annual_commission": annual_commission,
                    "final_net_wealth": float(final["net_wealth"]),
                    "final_real_net_wealth": float(final["real_net_wealth"]),
                    "final_fees_paid": float(final["fees_paid"]),
                    "final_taxes_paid": float(final["taxes_paid"]),
                }
            )
    return pd.DataFrame(rows)
