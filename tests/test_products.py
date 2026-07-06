"""Tests for generic product formulas."""

import pytest

from financial_planner.models import ProductConfig
from financial_planner.models import TaxConfig
from financial_planner.products import (
    generic_product_templates,
    grow_one_year,
    product_comparison_dataframe,
    withdraw_proportionally,
)


def test_compound_growth_with_fees() -> None:
    product = ProductConfig(
        name="Generic fund",
        type="investment_fund",
        expected_return=0.06,
        annual_commission=0.01,
        tax_treatment="savings_income_deferred",
        liquidity="high",
    )

    result = grow_one_year(balance=10_000, contribution=1_000, product=product)

    assert result.gross_return_amount == pytest.approx(660)
    assert result.fee == pytest.approx(116.60)
    assert result.ending_balance == pytest.approx(11_543.40)
    assert result.cost_basis == pytest.approx(1_000)


def test_partial_withdrawal_uses_average_cost_basis() -> None:
    product = ProductConfig(
        name="Generic fund",
        type="investment_fund",
        expected_return=0.06,
        annual_commission=0.01,
        tax_treatment="savings_income_deferred",
        liquidity="high",
    )

    result = withdraw_proportionally(
        balance=12_000,
        cost_basis=10_000,
        requested_withdrawal=3_000,
        product=product,
        tax_config=TaxConfig(),
    )

    assert result.withdrawal == pytest.approx(3_000)
    assert result.taxable_gain == pytest.approx(500)
    assert result.tax == pytest.approx(95)
    assert result.ending_balance == pytest.approx(9_000)
    assert result.cost_basis == pytest.approx(7_500)


def test_generic_product_templates_cover_supported_families() -> None:
    templates = generic_product_templates()

    assert {template.product_type for template in templates} == {
        "remunerated_account",
        "money_market_fund",
        "investment_fund",
        "pension_plan",
        "unit_linked",
    }


def test_product_comparison_dataframe_includes_cost_drag() -> None:
    product = ProductConfig(
        name="Generic unit linked",
        type="unit_linked",
        expected_return=0.05,
        annual_commission=0.015,
        insurance_cost=0.002,
        tax_treatment="savings_income",
        liquidity="medium_high",
    )

    df = product_comparison_dataframe([product])

    assert df["total_annual_cost"].iloc[0] == pytest.approx(0.017)
    assert df["simple_net_return_before_tax"].iloc[0] == pytest.approx(0.033)
