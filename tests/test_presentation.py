"""Tests for dashboard presentation tables and glossary metadata."""

from financial_planner.cashflows import cash_flow_for_year
from financial_planner.models import BucketConfig, BucketsConfig, PlanningConfig
from financial_planner.presentation import (
    ADVANCED_DASHBOARD_COLUMNS,
    COLUMN_DEFINITIONS,
    DEFAULT_DASHBOARD_COLUMNS,
    bucket_plan_dataframe,
    column_tooltips,
    dashboard_dataframe,
    glossary_dataframe,
)
from financial_planner.reporting import build_report_bundle
from financial_planner.simulation import results_to_dataframe, run_simulation
from test_simulation import sample_config


def test_default_dashboard_columns_are_present() -> None:
    bundle = build_report_bundle(sample_config())

    assert DEFAULT_DASHBOARD_COLUMNS == list(
        bundle.dashboard[DEFAULT_DASHBOARD_COLUMNS].columns
    )


def test_advanced_dashboard_columns_can_be_selected() -> None:
    bundle = build_report_bundle(sample_config())
    selected = DEFAULT_DASHBOARD_COLUMNS + ["investment_value", "emergency_fund_balance"]

    assert set(selected).issubset(bundle.dashboard.columns)
    assert "investment_value" in ADVANCED_DASHBOARD_COLUMNS


def test_glossary_includes_all_exported_dashboard_columns() -> None:
    glossary = glossary_dataframe()

    assert set(DEFAULT_DASHBOARD_COLUMNS).issubset(set(glossary["column_name"]))
    assert {"ui_label_es", "definition_es", "interpretation_es", "default_visible"}.issubset(
        glossary.columns
    )


def test_every_default_column_has_tooltip() -> None:
    tooltips = column_tooltips()

    for column in DEFAULT_DASHBOARD_COLUMNS:
        assert tooltips[column]
        assert COLUMN_DEFINITIONS[column].default_visible


def test_dashboard_net_after_taxes_is_not_above_gross_when_costs_apply() -> None:
    bundle = build_report_bundle(sample_config())
    dashboard = bundle.dashboard

    assert (
        dashboard["net_wealth_after_taxes_fees"] <= dashboard["gross_wealth_nominal"]
    ).any()


def test_dashboard_tracks_contributions_separately_from_gain() -> None:
    bundle = build_report_bundle(sample_config())
    row = bundle.dashboard.loc[
        bundle.dashboard["strategy"] == "investment_fund_only"
    ].iloc[-1]

    assert row["total_contributions"] > 0
    assert row["net_gain_after_taxes_fees"] == (
        row["net_wealth_after_taxes_fees"] - row["total_contributions"]
    )


def test_planned_spending_reduces_available_liquidity_and_is_tracked() -> None:
    config = sample_config().model_copy(
        update={
            "planning": PlanningConfig(
                emergency_fund_blocks_investing=False,
                buckets=BucketsConfig(
                    travel_and_life=BucketConfig(annual_budget=1_000, priority=2),
                    home_improvements=BucketConfig(annual_budget=500, priority=2),
                ),
            )
        }
    )

    cash_flow = cash_flow_for_year(config, 2026, config.household.current_liquidity)
    df = results_to_dataframe(run_simulation(config))

    assert cash_flow.planned_spending == 1_500
    assert cash_flow.liquidity == config.household.current_liquidity - 1_500
    assert df["planned_spending_cumulative"].max() > 0


def test_bucket_allocations_sum_correctly() -> None:
    config = sample_config().model_copy(
        update={
            "planning": PlanningConfig(
                buckets=BucketsConfig(
                    travel_and_life=BucketConfig(annual_budget=3_000, priority=2),
                    home_improvements=BucketConfig(annual_budget=3_000, priority=2),
                    long_term_investment=BucketConfig(
                        annual_contribution=7_000,
                        priority=3,
                    ),
                    mortgage_extra_amortization=BucketConfig(
                        annual_amount=3_000,
                        priority=4,
                    ),
                )
            )
        }
    )

    bucket_plan = bucket_plan_dataframe(config)

    assert bucket_plan["annual_amount"].sum() == 16_000


def test_retirement_target_surplus_shortfall_calculation() -> None:
    bundle = build_report_bundle(sample_config())
    dashboard = dashboard_dataframe(bundle.final, sample_config())

    for row in dashboard.to_dict(orient="records"):
        difference = row["real_net_wealth_today_euros"] - 350_000
        assert row["surplus_vs_target_real"] == max(difference, 0)
        assert row["shortfall_vs_target_real"] == max(-difference, 0)


def test_mortgage_vs_invest_includes_interpretation() -> None:
    bundle = build_report_bundle(sample_config())
    interpretation = bundle.mortgage_vs_invest["interpretation"].iloc[0]

    assert "estrategia mixta" in interpretation.lower()
    assert bundle.mortgage_vs_invest["risk_level"].iloc[0]
    assert bundle.mortgage_vs_invest["liquidity_impact"].iloc[0]
