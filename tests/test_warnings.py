"""Tests for non-fatal validation warnings."""

from financial_planner.models import ProductConfig
from financial_planner.warnings import validation_warnings
from test_simulation import sample_config


def test_validation_warnings_detect_liquidity_gap() -> None:
    warnings = validation_warnings(sample_config())

    assert "liquidity_below_target" in {warning.code for warning in warnings}


def test_validation_warnings_detect_high_cost_product() -> None:
    config = sample_config()
    data = config.model_dump()
    data["products"].append(
        ProductConfig(
            name="High cost generic product",
            type="money_market_fund",
            expected_return=0.01,
            annual_commission=0.03,
            tax_treatment="savings_income_deferred",
            liquidity="high",
        ).model_dump()
    )
    updated = config.model_validate(data)

    codes = {warning.code for warning in validation_warnings(updated)}

    assert "high_commission" in codes
    assert "cost_exceeds_expected_return" in codes
