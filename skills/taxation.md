# Spanish taxation skill

Use a simplified configurable model.

This is not tax advice.

## General income tax

Used for:

- Salary
- Public pension
- Pension plan redemption

## Savings income tax

Used for:

- Account interest
- Capital gains
- Fund gains at sale
- Unit linked gains at redemption

## Pension plan

During contribution phase:

```text
tax_saving = contribution * current_marginal_tax_rate
```

During redemption:

- Amount redeemed is taxed as general income.
- Use configurable future marginal/effective tax rate.

## Investment funds

- Gains are tax-deferred until sale.
- Tax only the gain, not full redemption.
- Allow simplified average cost basis.

## Unit linked

- Gains taxed as savings income on redemption.
- Optional insurance cost.
- No pension-plan deduction.
