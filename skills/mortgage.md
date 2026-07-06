# Mortgage skill

## Monthly payment

```text
M = P * r * (1 + r)^n / ((1 + r)^n - 1)
```

Where:

- `P`: principal
- `r`: monthly interest rate
- `n`: number of months

## Amortization schedule

For every month:

1. Interest = remaining principal * monthly rate.
2. Principal repayment = monthly payment - interest.
3. Remaining principal -= principal repayment.
4. Apply extra repayment when configured.
5. Stop when remaining principal reaches zero.

## Outputs

- Monthly payment
- Annual interest paid
- Annual principal repaid
- Outstanding balance
- Interest saved by early repayment
- Years/months until payoff
