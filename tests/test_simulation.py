"""Tests for the yearly simulation engine."""

from financial_planner.models import (
    AssumptionsConfig,
    HouseholdConfig,
    MortgageConfig,
    Person,
    PlanningConfig,
    ProductConfig,
    ScenarioConfig,
    ScenarioManagerConfig,
    SimulationConfig,
    StrategyConfig,
    WithdrawalConfig,
)
from financial_planner.scenarios import run_scenarios
from financial_planner.sensitivity import commission_return_sensitivity
from financial_planner.simulation import results_to_dataframe, run_simulation


def sample_config() -> SimulationConfig:
    return SimulationConfig(
        household=HouseholdConfig(
            current_year=2026,
            retirement_age=42,
            annual_savings=6_000,
            current_liquidity=5_000,
            target_liquidity=10_000,
        ),
        people=[
            Person(
                name="Person A",
                age=39,
                gross_salary=40_000,
                current_marginal_tax_rate=0.30,
                expected_future_marginal_tax_rate=0.25,
            )
        ],
        mortgage=MortgageConfig(
            initial_principal=50_000,
            annual_interest_rate=0.02,
            term_years=20,
            annual_extra_amortization=2_000,
        ),
        assumptions=AssumptionsConfig(inflation=0.02),
        products=[
            ProductConfig(
                name="Generic investment fund",
                type="investment_fund",
                expected_return=0.05,
                annual_commission=0.005,
                tax_treatment="savings_income_deferred",
                liquidity="high",
            ),
            ProductConfig(
                name="Generic pension plan",
                type="pension_plan",
                expected_return=0.05,
                annual_commission=0.01,
                annual_contribution_limit_per_person=1_500,
                tax_treatment="general_income_on_redemption",
                liquidity="restricted",
            ),
            ProductConfig(
                name="Generic unit linked",
                type="unit_linked",
                expected_return=0.05,
                annual_commission=0.015,
                insurance_cost=0.001,
                tax_treatment="savings_income",
                liquidity="medium_high",
            ),
        ],
    )


def test_run_simulation_returns_all_mvp_strategies() -> None:
    results = run_simulation(sample_config())

    assert [result.strategy for result in results] == [
        "investment_fund_only",
        "pension_plan_reinvest_tax_saving",
        "unit_linked",
        "mortgage_amortization",
    ]
    assert all(len(result.yearly_results) == 3 for result in results)


def test_strategy_comparison_consistency() -> None:
    results = run_simulation(sample_config())
    df = results_to_dataframe(results)

    assert set(df["strategy"]) == {
        "investment_fund_only",
        "pension_plan_reinvest_tax_saving",
        "unit_linked",
        "mortgage_amortization",
    }
    assert df.groupby("strategy")["year"].nunique().eq(3).all()
    assert df["net_wealth"].notna().all()
    assert df["mortgage_balance"].ge(0).all()


def test_mortgage_amortization_strategy_reduces_balance_faster() -> None:
    df = results_to_dataframe(run_simulation(sample_config()))
    final = df.sort_values("year").groupby("strategy").tail(1).set_index("strategy")

    assert (
        final.loc["mortgage_amortization", "mortgage_balance"]
        < final.loc["investment_fund_only", "mortgage_balance"]
    )


def test_inflation_adjusted_values_and_liquidity_gap_are_recorded() -> None:
    df = results_to_dataframe(run_simulation(sample_config()))

    assert "real_net_wealth" in df.columns
    assert "liquidity_gap" in df.columns
    assert df["liquidity_gap"].eq(5_000).all()
    assert (df["real_net_wealth"].abs() <= df["net_wealth"].abs()).all()


def test_mixed_strategy_allocation_runs() -> None:
    config = sample_config().model_copy(
        update={"strategies": StrategyConfig(enabled=["mixed_allocation"])}
    )

    results = run_simulation(config)
    df = results_to_dataframe(results)

    assert [result.strategy for result in results] == ["mixed_allocation"]
    assert df["investment_balance"].iloc[-1] > 0
    assert df["pension_balance"].iloc[-1] > 0
    assert df["unit_linked_balance"].iloc[-1] > 0
    assert df["extra_mortgage_amortization"].iloc[0] == 1_200


def test_configured_withdrawals_reduce_fund_balance_and_record_tax() -> None:
    config = sample_config().model_copy(
        update={
            "planning": PlanningConfig(
                withdrawals=WithdrawalConfig(
                    annual_amount=1_000,
                    start_year=2027,
                    end_year=2027,
                )
            )
        }
    )

    df = results_to_dataframe(run_simulation(config))
    fund_rows = df.loc[df["strategy"] == "investment_fund_only"].sort_values("year")

    assert fund_rows.loc[fund_rows["year"] == 2027, "withdrawal"].iloc[0] == 1_000
    assert fund_rows["withdrawal_tax"].ge(0).all()


def test_scenario_manager_runs_baseline_and_configured_scenario() -> None:
    config = sample_config().model_copy(
        update={
            "scenario_manager": ScenarioManagerConfig(
                scenarios=[
                    ScenarioConfig(name="lower_return", expected_return_shift=-0.01)
                ]
            )
        }
    )

    results = run_scenarios(config)

    assert set(results) == {"baseline", "lower_return"}
    assert len(results["lower_return"]) == 4


def test_commission_return_sensitivity_grid() -> None:
    df = commission_return_sensitivity(sample_config())

    assert len(df) == 9
    assert set(df.columns) >= {
        "expected_return",
        "annual_commission",
        "final_net_wealth",
        "final_real_net_wealth",
    }
