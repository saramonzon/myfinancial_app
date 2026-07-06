# Formulas

## Compound interest

```text
FV = PV * (1 + r) ** n
```

## Real value

```text
real_value = nominal_value / ((1 + inflation) ** years)
```

## Mortgage monthly payment

```text
M = P * r * (1 + r)^n / ((1 + r)^n - 1)
```

## Pension tax saving

```text
tax_saving = contribution * current_marginal_tax_rate
```

## Capital gains tax

```text
tax = progressive_savings_tax(max(0, sale_value - cost_basis))
```

## Commission paid

```text
after_return_balance = (starting_balance + contribution) * (1 + expected_return)
fee = after_return_balance * (annual_commission + insurance_cost)
ending_balance = after_return_balance - fee
```

## Partial withdrawal with average cost basis

```text
withdrawal = min(requested_withdrawal, balance)
withdrawal_ratio = withdrawal / balance
withdrawn_basis = cost_basis * withdrawal_ratio
taxable_gain = max(0, withdrawal - withdrawn_basis)
tax = progressive_savings_tax(taxable_gain)
remaining_cost_basis = cost_basis - withdrawn_basis
```

## Pension redemption over multiple years

```text
annual_redemption = pension_balance / pension_redemption_years
baseline_tax = progressive_general_income_tax(other_general_income)
annual_incremental_tax =
  progressive_general_income_tax(other_general_income + annual_redemption)
  - baseline_tax
total_redemption_tax = annual_incremental_tax * pension_redemption_years
```

## Net wealth

```text
net_wealth =
  liquidable_assets_after_tax
  + current_liquidity
  - mortgage_balance
```

## Break-even commission

```text
find commission where:
  final_net_wealth(strategy, commission)
  =
  final_net_wealth(benchmark_strategy)
```
