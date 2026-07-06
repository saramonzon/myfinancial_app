# Architecture

## Goal

Build a modular financial planning engine with a Streamlit dashboard.

The system must compare household strategies year by year until retirement.

## Layers

```text
UI layer
  ↓
Application services
  ↓
Simulation engine
  ↓
Financial models
  ↓
Configuration and exports
```

## Modules

### `app.py`

Streamlit entrypoint. It must not contain business logic.

### `src/financial_planner/models.py`

Pydantic models and shared data structures.

Expected models:

- `Person`
- `HouseholdConfig`
- `MortgageConfig`
- `TaxConfig`
- `ProductConfig`
- `SimulationConfig`
- `StrategyConfig`
- `YearlyResult`
- `StrategyResult`

### `src/financial_planner/config.py`

Load and validate YAML configuration.

### `src/financial_planner/mortgage.py`

Mortgage engine:

- Monthly payment calculation.
- Amortization schedule.
- Early repayment.
- Interest savings.
- Compare amortization vs investing.

### `src/financial_planner/taxes.py`

Simplified Spanish tax engine:

- General income tax.
- Savings tax.
- Pension contribution deduction.
- Pension redemption taxation.
- Capital gains taxation.
- Interest taxation.

All tax brackets and rates must be configurable.

### `src/financial_planner/products.py`

Generic product engine:

- Remunerated accounts.
- Money market funds.
- Investment funds.
- Pension plans.
- Unit linked products.
- Commission drag.

### `src/financial_planner/simulation.py`

Year-by-year simulation engine.

### `src/financial_planner/sensitivity.py`

Sensitivity analysis.

### `src/financial_planner/charts.py`

Charts for Streamlit.

### `src/financial_planner/export.py`

Excel, CSV and Markdown exports.

## Data flow

```text
YAML config + UI overrides
        ↓
Validated pydantic models
        ↓
Simulation engine
        ↓
Strategy results
        ↓
Dashboard + exports
```

## Avoid

- Hidden assumptions.
- Bank-specific logic.
- Hardcoded tax rates.
- Business logic in Streamlit.
- Unvalidated YAML values.
