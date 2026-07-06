"""Mortgage formulas and amortization schedules."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from financial_planner.models import MortgageConfig


@dataclass(frozen=True)
class MortgageSummary:
    monthly_payment: float
    total_interest: float
    payoff_month: int
    final_balance: float


def monthly_payment(
    principal: float, annual_interest_rate: float, term_years: int
) -> float:
    """Calculate the fixed monthly payment for an amortizing mortgage.

    Formula: M = P * r * (1 + r)^n / ((1 + r)^n - 1), where P is principal,
    r is the monthly interest rate, and n is the number of monthly payments.
    """

    if principal < 0:
        raise ValueError("principal must be non-negative")
    if annual_interest_rate < 0:
        raise ValueError("annual_interest_rate must be non-negative")
    if term_years <= 0:
        raise ValueError("term_years must be positive")
    if principal == 0:
        return 0.0

    number_of_months = term_years * 12
    monthly_rate = annual_interest_rate / 12
    if monthly_rate == 0:
        return principal / number_of_months
    growth_factor = (1 + monthly_rate) ** number_of_months
    return principal * monthly_rate * growth_factor / (growth_factor - 1)


def amortization_schedule(
    mortgage: MortgageConfig,
    annual_extra_amortization: float | None = None,
) -> pd.DataFrame:
    """Build a month-by-month amortization schedule.

    The MVP supports early repayment by reducing term: the contractual monthly
    payment stays unchanged and configured extra amortization is applied once per
    year at month 12, 24, 36, and so on until the loan is paid off.
    """

    if annual_extra_amortization is None:
        annual_extra_amortization = mortgage.annual_extra_amortization
    if annual_extra_amortization < 0:
        raise ValueError("annual_extra_amortization must be non-negative")

    payment = monthly_payment(
        mortgage.initial_principal,
        mortgage.annual_interest_rate,
        mortgage.term_years,
    )
    monthly_rate = mortgage.annual_interest_rate / 12
    balance = mortgage.initial_principal
    rows: list[dict[str, float | int]] = []

    for month in range(1, mortgage.term_years * 12 + 1):
        if balance <= 0:
            break
        interest = balance * monthly_rate
        principal_payment = min(payment - interest, balance)
        if principal_payment < 0:
            raise ValueError("Monthly payment does not cover accrued interest.")
        balance -= principal_payment

        extra_payment = 0.0
        if annual_extra_amortization and month % 12 == 0 and balance > 0:
            extra_payment = min(annual_extra_amortization, balance)
            balance -= extra_payment

        rows.append(
            {
                "month": month,
                "year_index": (month - 1) // 12 + 1,
                "payment": round(principal_payment + interest, 10),
                "interest": round(interest, 10),
                "principal": round(principal_payment, 10),
                "extra_principal": round(extra_payment, 10),
                "ending_balance": round(max(balance, 0.0), 10),
            }
        )
        if balance <= 1e-8:
            break

    return pd.DataFrame(rows)


def annual_mortgage_summary(schedule: pd.DataFrame) -> pd.DataFrame:
    """Aggregate a monthly mortgage schedule into yearly planning rows."""

    if schedule.empty:
        return pd.DataFrame(
            columns=[
                "year_index",
                "payment",
                "interest",
                "principal",
                "extra_principal",
                "ending_balance",
            ]
        )
    grouped = (
        schedule.groupby("year_index", as_index=False)
        .agg(
            payment=("payment", "sum"),
            interest=("interest", "sum"),
            principal=("principal", "sum"),
            extra_principal=("extra_principal", "sum"),
            ending_balance=("ending_balance", "last"),
        )
        .reset_index(drop=True)
    )
    return grouped


def mortgage_summary(schedule: pd.DataFrame) -> MortgageSummary:
    """Return total interest and payoff timing for a mortgage schedule."""

    if schedule.empty:
        return MortgageSummary(0.0, 0.0, 0, 0.0)
    return MortgageSummary(
        monthly_payment=float(schedule.loc[0, "payment"]),
        total_interest=float(schedule["interest"].sum()),
        payoff_month=int(schedule["month"].iloc[-1]),
        final_balance=float(schedule["ending_balance"].iloc[-1]),
    )


def interest_saved_by_early_repayment(
    mortgage: MortgageConfig, annual_extra: float
) -> float:
    """Calculate interest avoided by annual early repayments."""

    baseline = mortgage_summary(
        amortization_schedule(mortgage, annual_extra_amortization=0)
    )
    accelerated = mortgage_summary(
        amortization_schedule(mortgage, annual_extra_amortization=annual_extra)
    )
    return baseline.total_interest - accelerated.total_interest
