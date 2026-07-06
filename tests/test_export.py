"""Tests for report exports."""

from openpyxl import load_workbook

from financial_planner.export import export_results_to_excel, export_results_to_markdown
from financial_planner.simulation import run_simulation
from test_simulation import sample_config


def test_markdown_export_contains_final_comparison(tmp_path) -> None:
    config = sample_config()
    results = run_simulation(config)

    path = export_results_to_markdown(results, config, tmp_path / "report.md")

    text = path.read_text(encoding="utf-8")
    assert "# Financial Planner Report" in text
    assert "Final Comparison" in text
    assert "Decision Helpers" in text
    assert "Scenario Summary" in text
    assert "Sensitivity Summary" in text
    assert "investment_fund_only" in text


def test_excel_export_contains_v1_sheets(tmp_path) -> None:
    config = sample_config()
    results = run_simulation(config)

    path = export_results_to_excel(results, config, tmp_path / "results.xlsx")
    workbook = load_workbook(path, read_only=True)

    assert {
        "yearly_results",
        "final_comparison",
        "scenario_summary",
        "sensitivity",
        "product_comparison",
        "decision_helpers",
        "warnings",
        "assumptions",
    }.issubset(set(workbook.sheetnames))
