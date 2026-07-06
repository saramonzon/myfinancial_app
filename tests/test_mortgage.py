"""Tests for mortgage formulas."""

import pytest

from financial_planner.models import MortgageConfig
from financial_planner.mortgage import (
    amortization_schedule,
    interest_saved_by_early_repayment,
    monthly_payment,
)


def test_monthly_payment_fixed_rate() -> None:
    payment = monthly_payment(100_000, 0.03, 30)

    assert payment == pytest.approx(421.604, rel=1e-5)


def test_amortization_schedule_reaches_zero_balance() -> None:
    mortgage = MortgageConfig(
        initial_principal=10_000,
        annual_interest_rate=0.03,
        term_years=2,
    )

    schedule = amortization_schedule(mortgage)

    assert len(schedule) == 24
    assert schedule["ending_balance"].iloc[-1] == pytest.approx(0.0, abs=1e-6)
    assert schedule["interest"].sum() > 0


def test_early_repayment_reduces_interest_and_term() -> None:
    mortgage = MortgageConfig(
        initial_principal=100_000,
        annual_interest_rate=0.03,
        term_years=30,
        annual_extra_amortization=1_200,
    )

    baseline = amortization_schedule(mortgage, annual_extra_amortization=0)
    accelerated = amortization_schedule(mortgage)

    assert accelerated["interest"].sum() < baseline["interest"].sum()
    assert len(accelerated) < len(baseline)
    assert interest_saved_by_early_repayment(mortgage, 1_200) > 0
