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
- Results are not financial or tax advice.

## Limitations

- Returns are deterministic expected returns, not probability distributions.
- Inflation is applied as a constant annual rate.
- Salary growth is stored as an assumption but not yet used to vary annual savings.
- Taxes are simplified planning approximations, not a legal tax calculator.
- Product models are generic and do not represent specific providers.
- Liquidity is tracked as a target gap; detailed emergency-fund cash flows are not modelled.
