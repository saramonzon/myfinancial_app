# Financial Planner

Local Python/Streamlit app for long-term household financial planning in Spain.

The goal is to compare generic strategies and financial products using configurable assumptions, not to recommend any specific bank or product.

## Main questions

- Should we amortize the mortgage or invest?
- Does a pension plan compensate after taxes?
- At what commission does a product stop being worthwhile?
- How much net wealth could we have at retirement?
- How much would be paid in taxes and fees?

## Stack

- Python 3.12+
- Streamlit
- Pandas
- NumPy
- Plotly
- OpenPyXL
- Pydantic
- Pytest

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
streamlit run app.py
```

## v1.0 outputs

- Streamlit dashboard with strategy, scenario, sensitivity, decision, product, and export views.
- Excel export with yearly results, final comparison, scenarios, sensitivity, products, warnings, decisions, and assumptions.
- Markdown report with the same audit sections in plain text.

See `docs/user_guide.md`, `docs/assumptions.md`, `docs/formulas.md`, and `docs/release_checklist.md`.

## Disclaimer

This is a personal decision-support tool. It is not financial, tax, or legal advice.
