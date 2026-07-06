# AGENTS.md

## Role

You are helping build a local Python application for long-term household financial planning in Spain.

The application must be generic, configurable, auditable, and maintainable.

## Non-negotiable rules

1. Do not hardcode real personal data.
2. Do not recommend specific banks or commercial products.
3. Keep Streamlit UI separate from business logic.
4. Keep all financial assumptions explicit and editable.
5. Use type hints.
6. Use small, testable functions.
7. Add tests for critical formulas.
8. Prefer clarity over cleverness.
9. Do not silently ignore invalid inputs.
10. Every result must be traceable to input assumptions.

## Architecture rules

Business logic belongs in `src/financial_planner/`.

The Streamlit app should only orchestrate user input, call service functions, and display results.

Do not put tax formulas, mortgage formulas, product simulations, or strategy logic directly inside `app.py`.

## Coding style

- Python 3.12+
- Use `pydantic` models for external inputs.
- Use `dataclasses` for internal value objects where appropriate.
- Use `pandas` for yearly simulation tables.
- Use pure functions where possible.
- Prefer explicit variable names.
- Add docstrings to financial formulas.
- Use `pytest` for tests.

## Testing requirements

At minimum, test:

- Mortgage monthly payment.
- Mortgage amortization schedule.
- Early repayment reducing interest.
- Compound growth with fees.
- Pension plan tax saving.
- Pension plan redemption tax.
- Capital gains tax.
- Strategy comparison consistency.
- Sensitivity break-even calculations.

## Product modelling

Products must be generic.

Supported product families:

- Remunerated account
- Money market fund
- Investment fund
- Pension plan
- Unit linked / life-saving insurance
- Mortgage amortization

Each product should be modelled through parameters:

- Expected annual return
- Annual commission
- Tax treatment
- Liquidity
- Contribution limits
- Redemption rules

## Tax modelling

Use a simplified configurable Spanish tax model.

The model must clearly document assumptions and limitations.
