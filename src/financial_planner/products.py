"""Generic product growth calculations."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from financial_planner.models import ProductConfig, ProductType, TaxConfig
from financial_planner.taxes import capital_gains_tax, savings_tax


@dataclass(frozen=True)
class ProductYear:
    starting_balance: float
    contribution: float
    gross_return_amount: float
    fee: float
    ending_balance: float
    cost_basis: float


@dataclass(frozen=True)
class ProductWithdrawal:
    starting_balance: float
    withdrawal: float
    taxable_gain: float
    tax: float
    ending_balance: float
    cost_basis: float


@dataclass(frozen=True)
class ProductTemplate:
    product_type: ProductType
    name: str
    description: str
    default_expected_return: float
    default_volatility: float
    default_annual_commission: float
    tax_treatment: str
    liquidity: str
    default_annual_contribution_limit_per_person: float | None = None
    default_insurance_cost: float = 0.0
    notes: str = "Generic template. Replace assumptions before using."


def find_product(
    products: list[ProductConfig], product_type: ProductType
) -> ProductConfig:
    """Find the first configured product of the requested generic type."""

    for product in products:
        if product.type == product_type:
            return product
    raise ValueError(f"Missing required product configuration: {product_type}")


def grow_one_year(
    balance: float,
    contribution: float,
    product: ProductConfig,
    cost_basis: float = 0.0,
) -> ProductYear:
    """Apply annual contribution, gross return, commission, and insurance cost.

    Contributions are assumed to occur at the start of the year. The product then
    earns its configured gross return, and fees are charged on assets after return.
    """

    if balance < 0:
        raise ValueError("balance must be non-negative")
    if contribution < 0:
        raise ValueError("contribution must be non-negative")
    if cost_basis < 0:
        raise ValueError("cost_basis must be non-negative")

    invested_balance = balance + contribution
    gross_return_amount = invested_balance * product.expected_return
    after_return_balance = invested_balance + gross_return_amount
    fee_rate = product.annual_commission + product.insurance_cost
    fee = after_return_balance * fee_rate
    ending_balance = after_return_balance - fee
    return ProductYear(
        starting_balance=balance,
        contribution=contribution,
        gross_return_amount=gross_return_amount,
        fee=fee,
        ending_balance=max(ending_balance, 0.0),
        cost_basis=cost_basis + contribution,
    )


def liquidation_tax(
    balance: float,
    cost_basis: float,
    product: ProductConfig,
    tax_config: TaxConfig,
) -> float:
    """Calculate tax due if a product balance were liquidated now."""

    if product.tax_treatment in {"savings_income", "savings_income_deferred"}:
        return capital_gains_tax(balance, cost_basis, tax_config)
    return 0.0


def withdraw_proportionally(
    balance: float,
    cost_basis: float,
    requested_withdrawal: float,
    product: ProductConfig,
    tax_config: TaxConfig,
) -> ProductWithdrawal:
    """Withdraw from a product using average cost basis for taxable gains.

    The withdrawn amount is capped at the current balance. Cost basis is reduced
    in the same proportion as the withdrawal, and savings tax applies only to the
    gain portion of the withdrawal for taxable/deferred savings products.
    """

    if balance < 0:
        raise ValueError("balance must be non-negative")
    if cost_basis < 0:
        raise ValueError("cost_basis must be non-negative")
    if requested_withdrawal < 0:
        raise ValueError("requested_withdrawal must be non-negative")
    if balance == 0 or requested_withdrawal == 0:
        return ProductWithdrawal(balance, 0.0, 0.0, 0.0, balance, cost_basis)

    withdrawal = min(requested_withdrawal, balance)
    withdrawal_ratio = withdrawal / balance
    withdrawn_basis = min(cost_basis * withdrawal_ratio, withdrawal)
    taxable_gain = max(withdrawal - withdrawn_basis, 0.0)
    tax = liquidation_tax(withdrawal, withdrawn_basis, product, tax_config)
    ending_balance = balance - withdrawal
    ending_cost_basis = max(cost_basis - withdrawn_basis, 0.0)
    return ProductWithdrawal(
        starting_balance=balance,
        withdrawal=withdrawal,
        taxable_gain=taxable_gain,
        tax=tax,
        ending_balance=ending_balance,
        cost_basis=ending_cost_basis,
    )


def interest_tax(interest: float, tax_config: TaxConfig) -> float:
    """Tax annual account interest as savings income."""

    return savings_tax(max(interest, 0.0), tax_config)


def generic_product_templates() -> list[ProductTemplate]:
    """Return generic product templates without provider-specific assumptions."""

    return [
        ProductTemplate(
            product_type="remunerated_account",
            name="Remunerated account template",
            description="Liquid cash-like product with annual interest taxed as savings income.",
            default_expected_return=0.02,
            default_volatility=0.005,
            default_annual_commission=0.0,
            tax_treatment="savings_income",
            liquidity="immediate",
        ),
        ProductTemplate(
            product_type="money_market_fund",
            name="Money market fund template",
            description="Low-volatility fund with deferred savings taxation on gains.",
            default_expected_return=0.025,
            default_volatility=0.01,
            default_annual_commission=0.002,
            tax_treatment="savings_income_deferred",
            liquidity="high",
        ),
        ProductTemplate(
            product_type="investment_fund",
            name="Investment fund template",
            description="Market-risk fund with deferred savings taxation on gains.",
            default_expected_return=0.05,
            default_volatility=0.15,
            default_annual_commission=0.005,
            tax_treatment="savings_income_deferred",
            liquidity="high",
        ),
        ProductTemplate(
            product_type="pension_plan",
            name="Pension plan template",
            description="Restricted-liquidity product with contribution deduction and general-income redemption.",
            default_expected_return=0.05,
            default_volatility=0.15,
            default_annual_commission=0.008,
            tax_treatment="general_income_on_redemption",
            liquidity="restricted",
            default_annual_contribution_limit_per_person=1_500,
        ),
        ProductTemplate(
            product_type="unit_linked",
            name="Unit linked template",
            description="Insurance wrapper with savings taxation on gains and configurable insurance cost.",
            default_expected_return=0.05,
            default_volatility=0.16,
            default_annual_commission=0.015,
            tax_treatment="savings_income",
            liquidity="medium_high",
            default_insurance_cost=0.0,
        ),
    ]


def product_comparison_dataframe(products: list[ProductConfig]) -> pd.DataFrame:
    """Compare configured generic products by return, fee drag, tax treatment, and liquidity."""

    rows: list[dict[str, float | str]] = []
    for product in products:
        total_fee = product.annual_commission + product.insurance_cost
        rows.append(
            {
                "name": product.name,
                "type": product.type,
                "expected_return": product.expected_return,
                "volatility": product.volatility,
                "annual_commission": product.annual_commission,
                "annual_contribution_limit_per_person": (
                    product.annual_contribution_limit_per_person
                ),
                "insurance_cost": product.insurance_cost,
                "total_annual_cost": total_fee,
                "simple_net_return_before_tax": product.expected_return - total_fee,
                "tax_treatment": product.tax_treatment,
                "liquidity": product.liquidity,
                "notes": product.notes or "",
            }
        )
    return pd.DataFrame(rows)
