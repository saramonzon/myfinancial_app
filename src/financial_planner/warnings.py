"""Non-fatal validation warnings for planning assumptions."""

from __future__ import annotations

from dataclasses import dataclass

from financial_planner.models import SimulationConfig


@dataclass(frozen=True)
class ValidationWarning:
    code: str
    message: str
    severity: str = "warning"


def validation_warnings(config: SimulationConfig) -> list[ValidationWarning]:
    """Return visible warnings for assumptions that deserve user review."""

    warnings: list[ValidationWarning] = []

    if config.household.current_liquidity < config.household.target_liquidity:
        warnings.append(
            ValidationWarning(
                code="liquidity_below_target",
                message="Current liquidity is below the configured target liquidity.",
            )
        )

    if config.household.annual_savings <= 0:
        warnings.append(
            ValidationWarning(
                code="no_annual_savings",
                message="Annual savings is zero, so accumulation strategies cannot receive contributions.",
            )
        )

    product_types = {product.type for product in config.products}
    for strategy in config.strategies.enabled:
        if strategy == "investment_fund_only" and "investment_fund" not in product_types:
            warnings.append(
                ValidationWarning(
                    code="missing_investment_fund",
                    message="Investment fund strategy is enabled but no investment fund product is configured.",
                    severity="error",
                )
            )
        if strategy == "unit_linked" and "unit_linked" not in product_types:
            warnings.append(
                ValidationWarning(
                    code="missing_unit_linked",
                    message="Unit linked strategy is enabled but no unit linked product is configured.",
                    severity="error",
                )
            )
        if strategy in {"pension_plan_reinvest_tax_saving", "mixed_allocation"} and (
            "pension_plan" not in product_types
        ):
            warnings.append(
                ValidationWarning(
                    code="missing_pension_plan",
                    message="A pension strategy is enabled but no pension plan product is configured.",
                    severity="error",
                )
            )

    for product in config.products:
        total_cost = product.annual_commission + product.insurance_cost
        if total_cost >= product.expected_return and product.expected_return > 0:
            warnings.append(
                ValidationWarning(
                    code="cost_exceeds_expected_return",
                    message=(
                        f"{product.name} has total annual cost greater than or equal "
                        "to expected return."
                    ),
                )
            )
        if product.annual_commission > 0.02:
            warnings.append(
                ValidationWarning(
                    code="high_commission",
                    message=f"{product.name} has an annual commission above 2%.",
                )
            )

    if config.assumptions.pension_redemption_years < 5:
        warnings.append(
            ValidationWarning(
                code="short_pension_redemption",
                message="Pension redemption period is short, which can concentrate taxable income.",
            )
        )

    return warnings
