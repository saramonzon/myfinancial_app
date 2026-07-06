"""Tests for v0.3 decision helpers."""

from financial_planner.decision import (
    amortize_vs_invest_decision,
    break_even_commission,
    final_net_wealth_for_strategy,
)
from test_simulation import sample_config


def test_final_net_wealth_for_strategy_returns_value() -> None:
    value = final_net_wealth_for_strategy(sample_config(), "investment_fund_only")

    assert isinstance(value, float)


def test_break_even_commission_returns_structured_result() -> None:
    result = break_even_commission(sample_config(), high=0.20)

    assert result.product_type == "investment_fund"
    assert result.strategy == "investment_fund_only"
    assert result.benchmark_strategy == "mortgage_amortization"
    assert result.target_net_wealth != 0
    assert result.low_commission_net_wealth >= result.high_commission_net_wealth


def test_amortize_vs_invest_decision_is_traceable() -> None:
    decision = amortize_vs_invest_decision(sample_config())

    assert decision.annual_extra_amortization == 6_000
    assert decision.mortgage_interest_saved > 0
    assert decision.preferred_option in {"investment", "mortgage_amortization"}
    assert decision.liquidity_warning is not None
