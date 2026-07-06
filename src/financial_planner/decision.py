"""Decision helpers for v0.3 planning comparisons."""

from __future__ import annotations

from dataclasses import dataclass

from financial_planner.models import ProductType, SimulationConfig, StrategyName
from financial_planner.mortgage import interest_saved_by_early_repayment
from financial_planner.products import find_product
from financial_planner.sensitivity import replace_product_assumptions
from financial_planner.simulation import results_to_dataframe, run_simulation, simulation_years
from financial_planner.taxes import savings_tax


@dataclass(frozen=True)
class BreakEvenCommissionResult:
    product_type: ProductType
    strategy: StrategyName
    benchmark_strategy: StrategyName
    expected_return: float
    break_even_commission: float | None
    target_net_wealth: float
    low_commission_net_wealth: float
    high_commission_net_wealth: float


@dataclass(frozen=True)
class AmortizeVsInvestDecision:
    annual_extra_amortization: float
    mortgage_interest_saved: float
    expected_after_tax_investment_gain: float
    difference: float
    preferred_option: str
    liquidity_warning: str | None


def final_net_wealth_for_strategy(config: SimulationConfig, strategy: StrategyName) -> float:
    """Return final net wealth for one enabled strategy."""

    df = results_to_dataframe(run_simulation(config))
    strategy_rows = df.loc[df["strategy"] == strategy]
    if strategy_rows.empty:
        raise ValueError(f"Strategy is not enabled: {strategy}")
    return float(strategy_rows.sort_values("year").tail(1)["net_wealth"].iloc[0])


def break_even_commission(
    config: SimulationConfig,
    product_type: ProductType = "investment_fund",
    strategy: StrategyName = "investment_fund_only",
    benchmark_strategy: StrategyName = "mortgage_amortization",
    low: float = 0.0,
    high: float = 0.05,
    tolerance: float = 0.0001,
    max_iterations: int = 40,
) -> BreakEvenCommissionResult:
    """Find the annual commission where a strategy matches a benchmark final net wealth.

    Returns ``None`` for the commission when the benchmark is not crossed inside
    the requested interval.
    """

    product = find_product(config.products, product_type)
    target = final_net_wealth_for_strategy(config, benchmark_strategy)
    low_config = replace_product_assumptions(config, product_type, product.expected_return, low)
    high_config = replace_product_assumptions(config, product_type, product.expected_return, high)
    low_value = final_net_wealth_for_strategy(low_config, strategy)
    high_value = final_net_wealth_for_strategy(high_config, strategy)

    if (low_value - target) * (high_value - target) > 0:
        return BreakEvenCommissionResult(
            product_type=product_type,
            strategy=strategy,
            benchmark_strategy=benchmark_strategy,
            expected_return=product.expected_return,
            break_even_commission=None,
            target_net_wealth=target,
            low_commission_net_wealth=low_value,
            high_commission_net_wealth=high_value,
        )

    lower = low
    upper = high
    mid = (lower + upper) / 2
    for _ in range(max_iterations):
        mid = (lower + upper) / 2
        mid_config = replace_product_assumptions(
            config, product_type, product.expected_return, mid
        )
        mid_value = final_net_wealth_for_strategy(mid_config, strategy)
        if abs(mid_value - target) <= tolerance:
            break
        if (low_value - target) * (mid_value - target) <= 0:
            upper = mid
            high_value = mid_value
        else:
            lower = mid
            low_value = mid_value

    return BreakEvenCommissionResult(
        product_type=product_type,
        strategy=strategy,
        benchmark_strategy=benchmark_strategy,
        expected_return=product.expected_return,
        break_even_commission=mid,
        target_net_wealth=target,
        low_commission_net_wealth=low_value,
        high_commission_net_wealth=high_value,
    )


def amortize_vs_invest_decision(config: SimulationConfig) -> AmortizeVsInvestDecision:
    """Compare extra mortgage amortization with expected after-tax fund growth.

    This helper compares interest saved by applying annual savings to the
    mortgage against a simplified after-tax investment gain over the same horizon.
    It is a planning comparison, not a recommendation.
    """

    fund = find_product(config.products, "investment_fund")
    annual_extra = config.household.annual_savings
    years = simulation_years(config)
    mortgage_interest_saved = interest_saved_by_early_repayment(
        config.mortgage, annual_extra
    )

    balance = 0.0
    total_contributed = 0.0
    for _ in range(years):
        total_contributed += annual_extra
        balance = (balance + annual_extra) * (1 + fund.expected_return)
        balance -= balance * fund.annual_commission
    investment_gain = max(balance - total_contributed, 0.0)
    expected_after_tax_gain = investment_gain - savings_tax(investment_gain, config.tax)
    difference = expected_after_tax_gain - mortgage_interest_saved
    preferred = "investment" if difference > 0 else "mortgage_amortization"
    liquidity_warning = None
    if config.household.current_liquidity < config.household.target_liquidity:
        liquidity_warning = "Current liquidity is below target before allocating extra savings."

    return AmortizeVsInvestDecision(
        annual_extra_amortization=annual_extra,
        mortgage_interest_saved=mortgage_interest_saved,
        expected_after_tax_investment_gain=expected_after_tax_gain,
        difference=difference,
        preferred_option=preferred,
        liquidity_warning=liquidity_warning,
    )
