# Mortgage math notes

A fixed-rate mortgage payment is calculated so that the loan reaches zero after `n` months.

Early repayment can be modelled in two ways:

1. Reduce term while keeping monthly payment.
2. Reduce monthly payment while keeping term.

The model should support both eventually, but MVP can implement term reduction first.

When comparing amortization vs investing, compare:

- Guaranteed interest saved by amortization.
- Expected after-tax investment return.
- Liquidity lost by amortization.
