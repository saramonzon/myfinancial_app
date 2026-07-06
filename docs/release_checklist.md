# Release Checklist

## Code quality

- Run `python3 -m pytest`.
- Run `ruff check .`.
- Confirm Streamlit starts without import or element-key errors.
- Confirm business logic remains under `src/financial_planner/`.
- Confirm `app.py` only loads config, calls services, and displays results.

## Data safety

- Confirm no real personal data is committed.
- Confirm products remain generic and provider-neutral.
- Confirm all assumptions used by outputs are represented in YAML or documented defaults.

## Outputs

- Generate the Excel export.
- Generate the Markdown report.
- Confirm exports include yearly results, final comparison, scenarios, sensitivity, products, warnings, decisions, and assumptions.

## Documentation

- Review `docs/assumptions.md`.
- Review `docs/formulas.md`.
- Review `docs/user_guide.md`.
- Review `docs/decisions.md`.

## Known limitations

- Tax modelling is simplified.
- Returns are deterministic.
- Salary growth is documented but not yet connected to annual savings.
- Liquidity target is tracked as a gap, not a detailed cash account projection.
