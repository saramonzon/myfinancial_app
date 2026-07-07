"""Yearly strategy simulation engine."""

from __future__ import annotations

import pandas as pd

from financial_planner.cashflows import cash_flow_for_year
from financial_planner.models import (
    Person,
    ProductConfig,
    ProductType,
    SimulationConfig,
    StrategyName,
    StrategyResult,
    YearlyResult,
)
from financial_planner.mortgage import amortization_schedule, annual_mortgage_summary
from financial_planner.products import (
    find_product,
    grow_one_year,
    liquidation_tax,
    withdraw_proportionally,
)
from financial_planner.taxes import (
    pension_contribution_tax_saving,
    pension_redemption_tax_over_years,
)


def simulation_years(config: SimulationConfig) -> int:
    """Return number of years until the oldest configured person reaches retirement."""

    oldest_age = max(person.age for person in config.people)
    years = config.household.retirement_age - oldest_age
    if years <= 0:
        raise ValueError("At least one simulation year is required before retirement.")
    return years


def average_current_marginal_tax_rate(people: list[Person]) -> float:
    total_salary = sum(person.gross_salary for person in people)
    if total_salary <= 0:
        return sum(person.current_marginal_tax_rate for person in people) / len(people)
    return (
        sum(person.gross_salary * person.current_marginal_tax_rate for person in people)
        / total_salary
    )


def average_future_marginal_tax_rate(people: list[Person]) -> float:
    total_salary = sum(person.gross_salary for person in people)
    if total_salary <= 0:
        return sum(person.expected_future_marginal_tax_rate for person in people) / len(
            people
        )
    return (
        sum(
            person.gross_salary * person.expected_future_marginal_tax_rate
            for person in people
        )
        / total_salary
    )


def total_pension_contribution_limit(
    config: SimulationConfig, pension: ProductConfig
) -> float:
    product_limit = pension.annual_contribution_limit_per_person
    per_person_limit = (
        product_limit
        if product_limit is not None
        else config.tax.pension_contribution_limit_per_person
    )
    return per_person_limit * len(config.people)


def real_value(nominal_value: float, inflation: float, year_index: int) -> float:
    """Convert nominal value to inflation-adjusted value for a simulation year."""

    if year_index < 0:
        raise ValueError("year_index must be non-negative")
    return nominal_value / ((1 + inflation) ** year_index)


def withdrawal_for_year(config: SimulationConfig, year: int) -> float:
    """Return configured annual withdrawal for a calendar year."""

    withdrawal = config.planning.withdrawals
    if withdrawal.annual_amount <= 0:
        return 0.0
    if withdrawal.start_year is not None and year < withdrawal.start_year:
        return 0.0
    if withdrawal.end_year is not None and year > withdrawal.end_year:
        return 0.0
    return withdrawal.annual_amount


def home_equity(config: SimulationConfig, mortgage_balance: float) -> float:
    """Return home equity from configured home value and outstanding mortgage."""

    return max(config.household.home_value - mortgage_balance, 0.0)


def selected_net_wealth(
    config: SimulationConfig,
    net_liquidable_wealth: float,
    home_equity_value: float,
) -> float:
    """Return net wealth according to whether home equity is included."""

    if config.household.include_home_equity_in_net_wealth:
        return net_liquidable_wealth + home_equity_value
    return net_liquidable_wealth


def _mortgage_balance_by_year(
    config: SimulationConfig, years: int, extra: float = 0.0
) -> list[float]:
    schedule = amortization_schedule(config.mortgage, annual_extra_amortization=extra)
    annual = annual_mortgage_summary(schedule)
    balances: list[float] = []
    last_balance = config.mortgage.initial_principal
    for year_index in range(1, years + 1):
        matching = annual.loc[annual["year_index"] == year_index]
        if not matching.empty:
            last_balance = float(matching["ending_balance"].iloc[0])
        else:
            last_balance = 0.0
        balances.append(last_balance)
    return balances


def _base_assumptions(
    config: SimulationConfig, product: ProductConfig | None = None
) -> dict[str, float | str]:
    assumptions: dict[str, float | str] = {
        "annual_savings": config.household.annual_savings,
        "inflation": config.assumptions.inflation,
        "mortgage_interest_rate": config.mortgage.annual_interest_rate,
    }
    if product is not None:
        assumptions.update(
            {
                "product_name": product.name,
                "expected_return": product.expected_return,
                "annual_commission": product.annual_commission,
                "tax_treatment": product.tax_treatment,
            }
        )
    return assumptions


def _simulate_product_strategy(
    config: SimulationConfig,
    strategy: StrategyName,
    product_type: ProductType,
) -> StrategyResult:
    product = find_product(config.products, product_type)
    years = simulation_years(config)
    mortgage_balances = _mortgage_balance_by_year(config, years)
    balance = 0.0
    cost_basis = 0.0
    total_taxes = 0.0
    total_fees = 0.0
    total_contributions = 0.0
    liquidity = config.household.current_liquidity
    rows: list[YearlyResult] = []

    for offset in range(years):
        year = config.household.current_year + offset
        cash_flow = cash_flow_for_year(config, year, liquidity)
        liquidity = cash_flow.liquidity
        grown = grow_one_year(
            balance, cash_flow.investable_savings, product, cost_basis
        )
        balance = grown.ending_balance
        cost_basis = grown.cost_basis
        total_contributions += cash_flow.investable_savings
        total_fees += grown.fee
        withdrawal_result = withdraw_proportionally(
            balance,
            cost_basis,
            withdrawal_for_year(config, year),
            product,
            config.tax,
        )
        balance = withdrawal_result.ending_balance
        cost_basis = withdrawal_result.cost_basis
        liquidation_tax_due = liquidation_tax(balance, cost_basis, product, config.tax)
        net_assets = balance - liquidation_tax_due
        mortgage_balance = mortgage_balances[offset]
        total_taxes = liquidation_tax_due + withdrawal_result.tax
        net_liquidable_wealth = net_assets + liquidity - mortgage_balance
        home_equity_value = home_equity(config, mortgage_balance)
        net_wealth = selected_net_wealth(
            config, net_liquidable_wealth, home_equity_value
        )
        rows.append(
            YearlyResult(
                strategy=strategy,
                year=year,
                age=max(person.age for person in config.people) + offset + 1,
                gross_wealth=balance,
                net_wealth=net_wealth,
                net_liquidable_wealth=net_liquidable_wealth,
                real_net_wealth=real_value(
                    net_wealth, config.assumptions.inflation, offset + 1
                ),
                taxes_paid=total_taxes,
                latent_taxes=liquidation_tax_due,
                fees_paid=total_fees,
                mortgage_balance=mortgage_balance,
                home_equity=home_equity_value,
                net_wealth_excluding_home_equity=net_liquidable_wealth,
                net_wealth_including_home_equity=net_liquidable_wealth
                + home_equity_value,
                liquidity=liquidity,
                liquidity_gap=max(
                    config.household.target_liquidity - liquidity,
                    0.0,
                ),
                investment_balance=balance if product.type != "unit_linked" else 0.0,
                unit_linked_balance=balance if product.type == "unit_linked" else 0.0,
                annual_contribution=cash_flow.investable_savings,
                out_of_pocket_contribution=cash_flow.available_savings,
                total_contributions=total_contributions,
                investable_savings=cash_flow.investable_savings,
                life_event_expenses=cash_flow.life_event_expenses,
                withdrawal=withdrawal_result.withdrawal,
                withdrawal_tax=withdrawal_result.tax,
                assumptions=_base_assumptions(config, product),
            )
        )

    return StrategyResult(strategy=strategy, yearly_results=rows)


def simulate_investment_fund_only(config: SimulationConfig) -> StrategyResult:
    return _simulate_product_strategy(config, "investment_fund_only", "investment_fund")


def simulate_unit_linked(config: SimulationConfig) -> StrategyResult:
    return _simulate_product_strategy(config, "unit_linked", "unit_linked")


def simulate_pension_plan_reinvest_tax_saving(
    config: SimulationConfig,
) -> StrategyResult:
    pension = find_product(config.products, "pension_plan")
    fund = find_product(config.products, "investment_fund")
    years = simulation_years(config)
    mortgage_balances = _mortgage_balance_by_year(config, years)
    current_tax_rate = average_current_marginal_tax_rate(config.people)
    annual_pension_limit = total_pension_contribution_limit(config, pension)

    pension_balance = 0.0
    fund_balance = 0.0
    fund_cost_basis = 0.0
    total_fees = 0.0
    total_contributions = 0.0
    liquidity = config.household.current_liquidity
    rows: list[YearlyResult] = []

    for offset in range(years):
        year = config.household.current_year + offset
        cash_flow = cash_flow_for_year(config, year, liquidity)
        liquidity = cash_flow.liquidity
        pension_contribution = min(cash_flow.investable_savings, annual_pension_limit)
        tax_saving = pension_contribution_tax_saving(
            pension_contribution, current_tax_rate
        )
        fund_contribution = cash_flow.investable_savings - pension_contribution + tax_saving

        pension_year = grow_one_year(pension_balance, pension_contribution, pension)
        fund_year = grow_one_year(
            fund_balance, fund_contribution, fund, fund_cost_basis
        )
        pension_balance = pension_year.ending_balance
        fund_balance = fund_year.ending_balance
        fund_cost_basis = fund_year.cost_basis
        total_contributions += cash_flow.investable_savings
        total_fees += pension_year.fee + fund_year.fee
        withdrawal_result = withdraw_proportionally(
            fund_balance,
            fund_cost_basis,
            withdrawal_for_year(config, year),
            fund,
            config.tax,
        )
        fund_balance = withdrawal_result.ending_balance
        fund_cost_basis = withdrawal_result.cost_basis

        pension_tax_due = pension_redemption_tax_over_years(
            pension_balance,
            config.assumptions.pension_redemption_years,
            config.tax,
        )
        fund_tax_due = liquidation_tax(fund_balance, fund_cost_basis, fund, config.tax)
        taxes_paid = (
            fund_tax_due
            + pension_tax_due
            + withdrawal_result.tax
            - tax_saving * (offset + 1)
        )
        net_assets = pension_balance + fund_balance - pension_tax_due - fund_tax_due
        mortgage_balance = mortgage_balances[offset]
        net_liquidable_wealth = net_assets + liquidity - mortgage_balance
        home_equity_value = home_equity(config, mortgage_balance)
        net_wealth = selected_net_wealth(
            config, net_liquidable_wealth, home_equity_value
        )

        rows.append(
            YearlyResult(
                strategy="pension_plan_reinvest_tax_saving",
                year=year,
                age=max(person.age for person in config.people) + offset + 1,
                gross_wealth=pension_balance + fund_balance,
                net_wealth=net_wealth,
                net_liquidable_wealth=net_liquidable_wealth,
                real_net_wealth=real_value(
                    net_wealth, config.assumptions.inflation, offset + 1
                ),
                taxes_paid=taxes_paid,
                latent_taxes=fund_tax_due + pension_tax_due,
                fees_paid=total_fees,
                mortgage_balance=mortgage_balance,
                home_equity=home_equity_value,
                net_wealth_excluding_home_equity=net_liquidable_wealth,
                net_wealth_including_home_equity=net_liquidable_wealth
                + home_equity_value,
                liquidity=liquidity,
                liquidity_gap=max(
                    config.household.target_liquidity - liquidity,
                    0.0,
                ),
                pension_balance=pension_balance,
                investment_balance=fund_balance,
                annual_contribution=config.household.annual_savings + tax_saving,
                out_of_pocket_contribution=cash_flow.available_savings,
                total_contributions=total_contributions,
                investable_savings=cash_flow.investable_savings,
                life_event_expenses=cash_flow.life_event_expenses,
                withdrawal=withdrawal_result.withdrawal,
                withdrawal_tax=withdrawal_result.tax,
                assumptions={
                    **_base_assumptions(config),
                    "pension_product_name": pension.name,
                    "fund_product_name": fund.name,
                    "current_marginal_tax_rate": current_tax_rate,
                    "annual_pension_limit": annual_pension_limit,
                    "pension_redemption_years": config.assumptions.pension_redemption_years,
                },
            )
        )

    return StrategyResult(
        strategy="pension_plan_reinvest_tax_saving", yearly_results=rows
    )


def simulate_mortgage_amortization(config: SimulationConfig) -> StrategyResult:
    years = simulation_years(config)
    extra = min(config.household.annual_savings, config.mortgage.initial_principal)
    balances = _mortgage_balance_by_year(config, years, extra=extra)
    rows: list[YearlyResult] = []
    liquidity = config.household.current_liquidity
    total_contributions = 0.0
    for offset, mortgage_balance in enumerate(balances):
        year = config.household.current_year + offset
        cash_flow = cash_flow_for_year(config, year, liquidity)
        liquidity = cash_flow.liquidity
        extra_for_year = min(cash_flow.investable_savings, mortgage_balance)
        total_contributions += extra_for_year
        net_liquidable_wealth = liquidity - mortgage_balance
        home_equity_value = home_equity(config, mortgage_balance)
        net_wealth = selected_net_wealth(
            config, net_liquidable_wealth, home_equity_value
        )
        rows.append(
            YearlyResult(
                strategy="mortgage_amortization",
                year=year,
                age=max(person.age for person in config.people) + offset + 1,
                gross_wealth=0.0,
                net_wealth=net_wealth,
                net_liquidable_wealth=net_liquidable_wealth,
                real_net_wealth=real_value(
                    net_wealth, config.assumptions.inflation, offset + 1
                ),
                taxes_paid=0.0,
                latent_taxes=0.0,
                fees_paid=0.0,
                mortgage_balance=mortgage_balance,
                home_equity=home_equity_value,
                net_wealth_excluding_home_equity=net_liquidable_wealth,
                net_wealth_including_home_equity=net_liquidable_wealth
                + home_equity_value,
                liquidity=liquidity,
                liquidity_gap=max(
                    config.household.target_liquidity - liquidity,
                    0.0,
                ),
                annual_contribution=0.0,
                out_of_pocket_contribution=cash_flow.available_savings,
                total_contributions=total_contributions,
                investable_savings=cash_flow.investable_savings,
                life_event_expenses=cash_flow.life_event_expenses,
                extra_mortgage_amortization=extra_for_year,
                assumptions={
                    **_base_assumptions(config),
                    "annual_extra_amortization": extra,
                    "extra_amortization_mode": config.mortgage.extra_amortization_mode,
                },
            )
        )
    return StrategyResult(strategy="mortgage_amortization", yearly_results=rows)


def simulate_mixed_allocation(config: SimulationConfig) -> StrategyResult:
    """Simulate configurable annual allocation across fund, pension, unit linked, and mortgage."""

    fund = find_product(config.products, "investment_fund")
    pension = find_product(config.products, "pension_plan")
    unit_linked = find_product(config.products, "unit_linked")
    years = simulation_years(config)
    allocation = config.planning.mixed_allocation
    extra = config.household.annual_savings * allocation.mortgage_amortization
    mortgage_balances = _mortgage_balance_by_year(config, years, extra=extra)
    pension_limit = total_pension_contribution_limit(config, pension)

    fund_balance = 0.0
    fund_cost_basis = 0.0
    pension_balance = 0.0
    unit_balance = 0.0
    unit_cost_basis = 0.0
    total_fees = 0.0
    total_contributions = 0.0
    liquidity = config.household.current_liquidity
    rows: list[YearlyResult] = []

    for offset in range(years):
        year = config.household.current_year + offset
        cash_flow = cash_flow_for_year(config, year, liquidity)
        liquidity = cash_flow.liquidity
        fund_contribution = cash_flow.investable_savings * allocation.investment_fund
        mortgage_contribution = (
            cash_flow.investable_savings * allocation.mortgage_amortization
        )
        pension_contribution = min(
            cash_flow.investable_savings * allocation.pension_plan,
            pension_limit,
        )
        unit_contribution = cash_flow.investable_savings * allocation.unit_linked

        fund_year = grow_one_year(
            fund_balance, fund_contribution, fund, fund_cost_basis
        )
        pension_year = grow_one_year(pension_balance, pension_contribution, pension)
        unit_year = grow_one_year(
            unit_balance, unit_contribution, unit_linked, unit_cost_basis
        )
        fund_balance = fund_year.ending_balance
        fund_cost_basis = fund_year.cost_basis
        pension_balance = pension_year.ending_balance
        unit_balance = unit_year.ending_balance
        unit_cost_basis = unit_year.cost_basis
        total_contributions += (
            fund_contribution
            + pension_contribution
            + unit_contribution
            + mortgage_contribution
        )
        total_fees += fund_year.fee + pension_year.fee + unit_year.fee

        withdrawal_needed = withdrawal_for_year(config, year)
        fund_withdrawal = withdraw_proportionally(
            fund_balance, fund_cost_basis, withdrawal_needed, fund, config.tax
        )
        fund_balance = fund_withdrawal.ending_balance
        fund_cost_basis = fund_withdrawal.cost_basis

        remaining_withdrawal = max(withdrawal_needed - fund_withdrawal.withdrawal, 0.0)
        unit_withdrawal = withdraw_proportionally(
            unit_balance,
            unit_cost_basis,
            remaining_withdrawal,
            unit_linked,
            config.tax,
        )
        unit_balance = unit_withdrawal.ending_balance
        unit_cost_basis = unit_withdrawal.cost_basis

        fund_tax_due = liquidation_tax(fund_balance, fund_cost_basis, fund, config.tax)
        unit_tax_due = liquidation_tax(
            unit_balance, unit_cost_basis, unit_linked, config.tax
        )
        pension_tax_due = pension_redemption_tax_over_years(
            pension_balance,
            config.assumptions.pension_redemption_years,
            config.tax,
        )
        withdrawal_tax = fund_withdrawal.tax + unit_withdrawal.tax
        net_assets = (
            fund_balance
            + pension_balance
            + unit_balance
            - fund_tax_due
            - unit_tax_due
            - pension_tax_due
        )
        mortgage_balance = mortgage_balances[offset]
        net_liquidable_wealth = net_assets + liquidity - mortgage_balance
        home_equity_value = home_equity(config, mortgage_balance)
        net_wealth = selected_net_wealth(
            config, net_liquidable_wealth, home_equity_value
        )

        rows.append(
            YearlyResult(
                strategy="mixed_allocation",
                year=year,
                age=max(person.age for person in config.people) + offset + 1,
                gross_wealth=fund_balance + pension_balance + unit_balance,
                net_wealth=net_wealth,
                net_liquidable_wealth=net_liquidable_wealth,
                real_net_wealth=real_value(
                    net_wealth, config.assumptions.inflation, offset + 1
                ),
                taxes_paid=fund_tax_due
                + unit_tax_due
                + pension_tax_due
                + withdrawal_tax,
                latent_taxes=fund_tax_due + unit_tax_due + pension_tax_due,
                fees_paid=total_fees,
                mortgage_balance=mortgage_balance,
                home_equity=home_equity_value,
                net_wealth_excluding_home_equity=net_liquidable_wealth,
                net_wealth_including_home_equity=net_liquidable_wealth
                + home_equity_value,
                liquidity=liquidity,
                liquidity_gap=max(
                    config.household.target_liquidity - liquidity,
                    0.0,
                ),
                pension_balance=pension_balance,
                investment_balance=fund_balance,
                unit_linked_balance=unit_balance,
                annual_contribution=fund_contribution
                + pension_contribution
                + unit_contribution,
                out_of_pocket_contribution=cash_flow.available_savings,
                total_contributions=total_contributions,
                investable_savings=cash_flow.investable_savings,
                life_event_expenses=cash_flow.life_event_expenses,
                withdrawal=fund_withdrawal.withdrawal + unit_withdrawal.withdrawal,
                withdrawal_tax=withdrawal_tax,
                extra_mortgage_amortization=mortgage_contribution
                if mortgage_balance > 0
                else 0.0,
                assumptions={
                    **_base_assumptions(config),
                    "investment_fund_allocation": allocation.investment_fund,
                    "pension_plan_allocation": allocation.pension_plan,
                    "unit_linked_allocation": allocation.unit_linked,
                    "mortgage_amortization_allocation": allocation.mortgage_amortization,
                },
            )
        )
    return StrategyResult(strategy="mixed_allocation", yearly_results=rows)


def run_simulation(config: SimulationConfig) -> list[StrategyResult]:
    """Run all enabled MVP strategies."""

    strategies: dict[StrategyName, StrategyResult] = {}
    if "investment_fund_only" in config.strategies.enabled:
        strategies["investment_fund_only"] = simulate_investment_fund_only(config)
    if "pension_plan_reinvest_tax_saving" in config.strategies.enabled:
        strategies["pension_plan_reinvest_tax_saving"] = (
            simulate_pension_plan_reinvest_tax_saving(config)
        )
    if "unit_linked" in config.strategies.enabled:
        strategies["unit_linked"] = simulate_unit_linked(config)
    if "mortgage_amortization" in config.strategies.enabled:
        strategies["mortgage_amortization"] = simulate_mortgage_amortization(config)
    if "mixed_allocation" in config.strategies.enabled:
        strategies["mixed_allocation"] = simulate_mixed_allocation(config)
    return [
        strategies[strategy]
        for strategy in config.strategies.enabled
        if strategy in strategies
    ]


def results_to_dataframe(results: list[StrategyResult]) -> pd.DataFrame:
    """Convert simulation results to a flat dataframe for dashboards and exports."""

    rows = [
        yearly.model_dump()
        for strategy_result in results
        for yearly in strategy_result.yearly_results
    ]
    return pd.DataFrame(rows)
