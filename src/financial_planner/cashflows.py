"""Household cash-flow rules for yearly simulations."""

from __future__ import annotations

from dataclasses import dataclass

from financial_planner.models import LifeEventConfig, SimulationConfig


@dataclass(frozen=True)
class YearCashFlow:
    available_savings: float
    investable_savings: float
    liquidity: float
    life_event_expenses: float
    savings_multiplier: float


def event_applies(event: LifeEventConfig, year: int) -> bool:
    """Return whether a life event applies in a calendar year."""

    end_year = event.end_year if event.end_year is not None else event.start_year
    return event.start_year <= year <= end_year


def base_annual_savings(config: SimulationConfig) -> float:
    """Return configured or income-derived annual household savings."""

    if not config.household.derive_savings_from_income:
        return config.household.annual_savings
    if config.household.annual_expenses is None:
        raise ValueError("annual_expenses is required when income-derived savings is enabled.")
    gross_income = sum(person.gross_salary for person in config.people)
    net_income = gross_income * (1 - config.household.effective_income_tax_rate)
    return max(net_income - config.household.annual_expenses, 0.0)


def cash_flow_for_year(
    config: SimulationConfig,
    year: int,
    starting_liquidity: float,
) -> YearCashFlow:
    """Apply income, expenses, life events, and emergency-fund investment rules."""

    savings = base_annual_savings(config)
    life_event_expenses = 0.0
    multiplier = 1.0
    for event in config.planning.life_events:
        if not event_applies(event, year):
            continue
        multiplier *= event.savings_multiplier
        life_event_expenses += event.recurring_annual_expense
        if year == event.start_year:
            life_event_expenses += event.one_off_expense

    available_savings = max(savings * multiplier, 0.0)
    liquidity = starting_liquidity
    expense_from_liquidity = min(liquidity, life_event_expenses)
    liquidity -= expense_from_liquidity
    remaining_expense = life_event_expenses - expense_from_liquidity
    available_savings = max(available_savings - remaining_expense, 0.0)

    investable_savings = available_savings
    if config.planning.emergency_fund_blocks_investing:
        liquidity_gap = max(config.household.target_liquidity - liquidity, 0.0)
        liquidity_top_up = min(available_savings, liquidity_gap)
        liquidity += liquidity_top_up
        investable_savings = available_savings - liquidity_top_up

    return YearCashFlow(
        available_savings=available_savings,
        investable_savings=investable_savings,
        liquidity=liquidity,
        life_event_expenses=life_event_expenses,
        savings_multiplier=multiplier,
    )
