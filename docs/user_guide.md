# User Guide

## Purpose

This application compares generic household financial planning strategies using editable assumptions.
It does not recommend banks, funds, insurers, or commercial products.

## Running the app

```bash
pip install -e ".[dev]"
streamlit run app.py
```

The dashboard reads:

- `data/inputs.example.yaml` for household, mortgage, tax, strategy, scenario, and planning assumptions.
- `data/products.example.yaml` for generic product assumptions.

Use copies of those files for private inputs. Do not commit real personal data.

## Configuration workflow

1. Edit annual savings, liquidity target, people, mortgage, inflation, and tax brackets in the inputs YAML.
2. Edit expected return, commissions, tax treatment, liquidity, and contribution limits in the products YAML.
3. Run the dashboard and review validation warnings before interpreting results.
4. Use filters to compare selected strategies, years, and metrics.
5. Export Excel or Markdown reports for audit and review.

## Dashboard sections

- Overview: final strategy comparison and main wealth charts.
- Simulation: yearly table, tax/fee chart, and mortgage balance chart.
- Decisions: break-even commission and amortize-vs-invest helper.
- Scenarios: baseline and configured scenarios plus return/commission sensitivity.
- Products: configured product comparison and generic templates.
- Exports: Excel workbook and Markdown report.

## Interpreting results

Net wealth includes liquidable assets after simplified taxes, plus current liquidity, minus mortgage balance.
Real net wealth adjusts nominal net wealth by the configured inflation assumption.
Warnings indicate assumptions that deserve review but may not block the simulation.

## Limitations

The model is deterministic and simplified. Tax results are planning approximations, not tax advice.
Investment returns are expected annual returns, not guarantees.
Product entries are generic and should be replaced with user-provided assumptions.
