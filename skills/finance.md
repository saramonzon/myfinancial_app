# Finance skill

## Required concepts

- Compound interest
- Inflation adjustment
- Net present value
- Annualized return
- Contribution schedules
- Commission drag
- Real vs nominal values

## Compound growth

```text
future_value = principal * (1 + annual_return) ** years
```

## Commission drag

Annual commissions must be applied every year to assets under management.

Approximation:

```text
net_return = gross_return - annual_commission
```

More explicit model:

```text
balance *= (1 + gross_return)
fee = balance * annual_commission
balance -= fee
```

Track fees separately.

## Inflation adjustment

```text
real_value = nominal_value / ((1 + inflation) ** years)
```
