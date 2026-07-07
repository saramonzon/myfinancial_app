"""Monte Carlo simulation for selected accumulation strategies."""

from __future__ import annotations

import math

import numpy as np
import pandas as pd

from financial_planner.cashflows import cash_flow_for_year
from financial_planner.models import ProductConfig, SimulationConfig
from financial_planner.products import find_product
from financial_planner.simulation import real_value, simulation_years
from financial_planner.taxes import capital_gains_tax


def sampled_return(
    rng: np.random.Generator,
    mean_return: float,
    volatility: float,
    distribution: str,
) -> float:
    """Sample one annual return from a normal or lognormal distribution."""

    if volatility == 0:
        return mean_return
    if distribution == "normal":
        return max(rng.normal(mean_return, volatility), -1.0)
    if distribution == "lognormal":
        sigma = volatility
        mu = math.log1p(mean_return) - 0.5 * sigma**2
        return max(rng.lognormal(mu, sigma) - 1, -1.0)
    raise ValueError(f"Unsupported distribution: {distribution}")


def run_product_monte_carlo(
    config: SimulationConfig,
    product: ProductConfig | None = None,
) -> pd.DataFrame:
    """Run Monte Carlo paths for the investment-fund-only accumulation model."""

    selected_product = product or find_product(config.products, "investment_fund")
    years = simulation_years(config)
    monte_carlo = config.planning.monte_carlo
    rng = np.random.default_rng(monte_carlo.seed)
    rows: list[dict[str, float | int]] = []

    for simulation_index in range(monte_carlo.simulations):
        balance = 0.0
        cost_basis = 0.0
        liquidity = config.household.current_liquidity
        total_fees = 0.0
        total_contributions = 0.0
        for offset in range(years):
            year = config.household.current_year + offset
            cash_flow = cash_flow_for_year(config, year, liquidity)
            liquidity = cash_flow.liquidity
            annual_return = sampled_return(
                rng,
                selected_product.expected_return,
                selected_product.volatility,
                monte_carlo.distribution,
            )
            invested = balance + cash_flow.investable_savings
            after_return = invested * (1 + annual_return)
            fee = after_return * (
                selected_product.annual_commission + selected_product.insurance_cost
            )
            balance = max(after_return - fee, 0.0)
            cost_basis += cash_flow.investable_savings
            total_fees += fee
            total_contributions += cash_flow.investable_savings

        latent_tax = capital_gains_tax(balance, cost_basis, config.tax)
        final_nominal = balance + liquidity - latent_tax
        rows.append(
            {
                "simulation": simulation_index,
                "final_nominal": final_nominal,
                "final_real": real_value(final_nominal, config.assumptions.inflation, years),
                "gross_final": balance,
                "latent_taxes": latent_tax,
                "total_fees": total_fees,
                "total_contributions": total_contributions,
            }
        )
    return pd.DataFrame(rows)


def monte_carlo_summary(config: SimulationConfig) -> pd.DataFrame:
    """Return percentiles and target probabilities for configured Monte Carlo paths."""

    if not config.planning.monte_carlo.enabled:
        return pd.DataFrame()
    paths = run_product_monte_carlo(config)
    values = paths["final_real"]
    row: dict[str, float | int] = {
        "simulations": config.planning.monte_carlo.simulations,
        "p10": float(values.quantile(0.10)),
        "p25": float(values.quantile(0.25)),
        "p50": float(values.quantile(0.50)),
        "p75": float(values.quantile(0.75)),
        "p90": float(values.quantile(0.90)),
    }
    for target in config.planning.monte_carlo.target_values:
        row[f"probability_target_{int(target)}"] = float((values >= target).mean())
    return pd.DataFrame([row])
