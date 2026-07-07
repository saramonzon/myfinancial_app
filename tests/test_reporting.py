"""Tests for shared v1.0 reporting tables."""

from financial_planner.reporting import build_report_bundle
from test_simulation import sample_config


def test_report_bundle_contains_all_release_tables() -> None:
    bundle = build_report_bundle(sample_config())

    assert not bundle.yearly.empty
    assert not bundle.final.empty
    assert not bundle.scenario_summary.empty
    assert not bundle.sensitivity.empty
    assert not bundle.product_comparison.empty
    assert not bundle.decision_summary.empty
    assert not bundle.sanity_check.empty
    assert {"baseline"} == set(bundle.scenarios)


def test_report_bundle_final_rows_match_strategies() -> None:
    bundle = build_report_bundle(sample_config())

    assert set(bundle.final["strategy"]) == set(bundle.yearly["strategy"])
    assert bundle.final.groupby("strategy")["year"].nunique().eq(1).all()
