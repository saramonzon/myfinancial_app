"""Tests for simplified tax formulas."""

import pytest

from financial_planner.models import TaxConfig
from financial_planner.taxes import (
    capital_gains_tax,
    general_income_tax,
    pension_contribution_tax_saving,
    pension_redemption_tax_over_years,
    pension_redemption_tax,
    savings_tax,
)


def test_savings_tax_uses_progressive_brackets() -> None:
    tax = savings_tax(10_000, TaxConfig())

    assert tax == pytest.approx(6_000 * 0.19 + 4_000 * 0.21)


def test_savings_tax_uses_30_percent_above_300000() -> None:
    tax = savings_tax(350_000, TaxConfig())

    assert tax == pytest.approx(
        6_000 * 0.19
        + (50_000 - 6_000) * 0.21
        + (200_000 - 50_000) * 0.23
        + (300_000 - 200_000) * 0.27
        + 50_000 * 0.30
    )


def test_capital_gains_tax_taxes_only_gain() -> None:
    tax = capital_gains_tax(15_000, 10_000, TaxConfig())

    assert tax == pytest.approx(5_000 * 0.19)


def test_pension_contribution_tax_saving() -> None:
    saving = pension_contribution_tax_saving(1_500, 0.37)

    assert saving == pytest.approx(555)


def test_pension_redemption_tax() -> None:
    tax = pension_redemption_tax(20_000, 0.30)

    assert tax == pytest.approx(6_000)


def test_general_income_tax_uses_configurable_brackets() -> None:
    tax = general_income_tax(15_000, TaxConfig())

    assert tax == pytest.approx(12_450 * 0.19 + (15_000 - 12_450) * 0.24)


def test_pension_redemption_tax_over_multiple_years() -> None:
    tax = pension_redemption_tax_over_years(
        pension_balance=20_000,
        years=2,
        tax_config=TaxConfig(),
    )

    assert tax == pytest.approx(20_000 * 0.19)
