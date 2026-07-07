# Assumptions

## Implemented assumptions

- Simulations are annual unless otherwise specified.
- Contributions are applied at the start of each simulated year.
- Investment returns are nominal before inflation.
- Inflation-adjusted values are calculated separately.
- Product fees and insurance costs are charged annually after gross return.
- Tax model is simplified and configurable.
- Savings-income and general-income tax brackets are configured in YAML.
- Fund and unit-linked withdrawals use average cost basis.
- Pension plan redemption is modelled as equal annual redemptions over the configured period.
- Mortgage early repayment reduces term while keeping the monthly payment constant.
- Net wealth is calculated as liquidable assets plus current liquidity minus mortgage balance.
- Home equity is reported separately and included in net wealth only when configured.
- Emergency-fund rules can block investing until target liquidity is reached.
- Annual savings can be fixed or derived from income and expenses.
- Life events can reduce liquidity, reduce annual savings, or add one-off/recurring expenses.
- Monte Carlo uses configured product mean return, volatility, distribution, simulations, and seed.
- Results are not financial or tax advice.

## Limitations

- Savings tax defaults are 19% to 6,000; 21% to 50,000; 23% to 200,000; 27% to 300,000; 30% above 300,000.
- Deterministic returns are explainability assumptions, not forecasts.
- Inflation is applied as a constant annual rate for real-value conversion.
- Taxes are simplified planning approximations, not a legal tax calculator.
- Product models are generic and do not represent specific providers.
- Monte Carlo assumes independent yearly returns and does not model serial correlation or regime changes.
