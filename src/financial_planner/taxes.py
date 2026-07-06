"""Simplified configurable Spanish tax formulas for planning."""

from __future__ import annotations

from financial_planner.models import TaxBracket, TaxConfig


def progressive_tax(amount: float, brackets: list[TaxBracket]) -> float:
    """Calculate tax using increasing marginal brackets."""

    if amount < 0:
        raise ValueError("amount must be non-negative")
    tax = 0.0
    lower_limit = 0.0
    remaining = amount
    for bracket in brackets:
        upper_limit = bracket.up_to
        bracket_width = (
            remaining if upper_limit is None else max(upper_limit - lower_limit, 0)
        )
        taxable_in_bracket = min(remaining, bracket_width)
        tax += taxable_in_bracket * bracket.rate
        remaining -= taxable_in_bracket
        if remaining <= 0:
            break
        if upper_limit is not None:
            lower_limit = upper_limit
    return tax


def savings_tax(gain: float, tax_config: TaxConfig) -> float:
    """Tax savings income or capital gains under configurable savings brackets."""

    if gain <= 0:
        return 0.0
    return progressive_tax(gain, tax_config.savings_tax_brackets)


def general_income_tax(amount: float, tax_config: TaxConfig) -> float:
    """Tax simplified general income under configurable general-income brackets."""

    if amount <= 0:
        return 0.0
    return progressive_tax(amount, tax_config.general_income_tax_brackets)


def capital_gains_tax(
    proceeds: float, cost_basis: float, tax_config: TaxConfig
) -> float:
    """Tax only the positive capital gain, not the full redemption amount."""

    if proceeds < 0:
        raise ValueError("proceeds must be non-negative")
    if cost_basis < 0:
        raise ValueError("cost_basis must be non-negative")
    return savings_tax(max(proceeds - cost_basis, 0.0), tax_config)


def pension_contribution_tax_saving(
    contribution: float, marginal_tax_rate: float
) -> float:
    """Estimate immediate pension-plan tax saving from deductible contributions."""

    if contribution < 0:
        raise ValueError("contribution must be non-negative")
    if not 0 <= marginal_tax_rate <= 1:
        raise ValueError("marginal_tax_rate must be between 0 and 1")
    return contribution * marginal_tax_rate


def pension_redemption_tax(redemption: float, future_tax_rate: float) -> float:
    """Tax pension plan redemption as simplified future general income."""

    if redemption < 0:
        raise ValueError("redemption must be non-negative")
    if not 0 <= future_tax_rate <= 1:
        raise ValueError("future_tax_rate must be between 0 and 1")
    return redemption * future_tax_rate


def pension_redemption_tax_over_years(
    pension_balance: float,
    years: int,
    tax_config: TaxConfig,
    other_general_income: float = 0.0,
) -> float:
    """Estimate total tax for redeeming a pension balance over equal annual payments.

    Pension plan redemptions are treated as general income. The function taxes
    each annual redemption on top of optional other general income and subtracts
    the baseline tax on that other income to isolate the redemption tax.
    """

    if pension_balance < 0:
        raise ValueError("pension_balance must be non-negative")
    if years <= 0:
        raise ValueError("years must be positive")
    if other_general_income < 0:
        raise ValueError("other_general_income must be non-negative")
    if pension_balance == 0:
        return 0.0

    annual_redemption = pension_balance / years
    baseline_tax = general_income_tax(other_general_income, tax_config)
    annual_incremental_tax = (
        general_income_tax(other_general_income + annual_redemption, tax_config)
        - baseline_tax
    )
    return annual_incremental_tax * years
