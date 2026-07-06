"""Validated input models and result structures for the financial planner."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, PositiveInt, field_validator

ProductType = Literal[
    "remunerated_account",
    "money_market_fund",
    "investment_fund",
    "pension_plan",
    "unit_linked",
]
TaxTreatment = Literal[
    "savings_income",
    "savings_income_deferred",
    "general_income_on_redemption",
]
StrategyName = Literal[
    "investment_fund_only",
    "pension_plan_reinvest_tax_saving",
    "unit_linked",
    "mortgage_amortization",
    "mixed_allocation",
]


class PlannerBaseModel(BaseModel):
    """Base model that rejects unknown configuration keys."""

    model_config = ConfigDict(extra="forbid")


class Person(PlannerBaseModel):
    name: str
    age: int = Field(ge=0, le=120)
    gross_salary: float = Field(ge=0)
    current_marginal_tax_rate: float = Field(ge=0, le=1)
    expected_future_marginal_tax_rate: float = Field(ge=0, le=1)


class HouseholdConfig(PlannerBaseModel):
    current_year: int = Field(ge=1900, le=2200)
    retirement_age: int = Field(ge=18, le=120)
    annual_savings: float = Field(ge=0)
    current_liquidity: float = Field(ge=0)
    target_liquidity: float = Field(ge=0)


class MortgageConfig(PlannerBaseModel):
    initial_principal: float = Field(ge=0)
    annual_interest_rate: float = Field(ge=0, le=1)
    term_years: PositiveInt
    annual_extra_amortization: float = Field(default=0, ge=0)
    extra_amortization_mode: Literal["reduce_term"] = "reduce_term"


class TaxBracket(PlannerBaseModel):
    up_to: float | None = Field(default=None, gt=0)
    rate: float = Field(ge=0, le=1)


class TaxConfig(PlannerBaseModel):
    """Simplified editable tax assumptions.

    The default savings brackets are deliberately generic planning defaults, not
    a legal representation of any tax year. Users can replace them in YAML.
    """

    savings_tax_brackets: list[TaxBracket] = Field(
        default_factory=lambda: [
            TaxBracket(up_to=6_000, rate=0.19),
            TaxBracket(up_to=50_000, rate=0.21),
            TaxBracket(up_to=200_000, rate=0.23),
            TaxBracket(up_to=None, rate=0.27),
        ]
    )
    general_income_tax_brackets: list[TaxBracket] = Field(
        default_factory=lambda: [
            TaxBracket(up_to=12_450, rate=0.19),
            TaxBracket(up_to=20_200, rate=0.24),
            TaxBracket(up_to=35_200, rate=0.30),
            TaxBracket(up_to=60_000, rate=0.37),
            TaxBracket(up_to=300_000, rate=0.45),
            TaxBracket(up_to=None, rate=0.47),
        ]
    )
    pension_contribution_limit_per_person: float = Field(default=1_500, ge=0)

    @field_validator("savings_tax_brackets")
    @classmethod
    def validate_savings_brackets(cls, brackets: list[TaxBracket]) -> list[TaxBracket]:
        return validate_tax_brackets(brackets)

    @field_validator("general_income_tax_brackets")
    @classmethod
    def validate_general_brackets(cls, brackets: list[TaxBracket]) -> list[TaxBracket]:
        return validate_tax_brackets(brackets)


def validate_tax_brackets(brackets: list[TaxBracket]) -> list[TaxBracket]:
    """Validate increasing tax brackets with one final open-ended bracket."""

    if not brackets:
        raise ValueError("At least one tax bracket is required.")
    previous_limit = 0.0
    open_brackets = 0
    for bracket in brackets:
        if bracket.up_to is None:
            open_brackets += 1
            continue
        if bracket.up_to <= previous_limit:
            raise ValueError("Tax bracket limits must be increasing.")
        previous_limit = bracket.up_to
    if open_brackets > 1:
        raise ValueError("Only one open-ended tax bracket is allowed.")
    if brackets[-1].up_to is not None:
        raise ValueError("The last tax bracket must be open-ended.")
    return brackets


class WithdrawalConfig(PlannerBaseModel):
    annual_amount: float = Field(default=0, ge=0)
    start_year: int | None = Field(default=None, ge=1900, le=2200)
    end_year: int | None = Field(default=None, ge=1900, le=2200)

    @field_validator("end_year")
    @classmethod
    def validate_year_order(cls, end_year: int | None, info: object) -> int | None:
        data = getattr(info, "data", {})
        start_year = data.get("start_year") if isinstance(data, dict) else None
        if start_year is not None and end_year is not None and end_year < start_year:
            raise ValueError("end_year must be greater than or equal to start_year.")
        return end_year


class MixedAllocationConfig(PlannerBaseModel):
    investment_fund: float = Field(default=0.40, ge=0, le=1)
    pension_plan: float = Field(default=0.20, ge=0, le=1)
    unit_linked: float = Field(default=0.20, ge=0, le=1)
    mortgage_amortization: float = Field(default=0.20, ge=0, le=1)

    @field_validator("mortgage_amortization")
    @classmethod
    def validate_total_allocation(cls, value: float, info: object) -> float:
        data = getattr(info, "data", {})
        if isinstance(data, dict):
            total = (
                data.get("investment_fund", 0)
                + data.get("pension_plan", 0)
                + data.get("unit_linked", 0)
                + value
            )
            if abs(total - 1.0) > 1e-9:
                raise ValueError("Mixed strategy allocations must sum to 1.0.")
        return value


class SensitivityConfig(PlannerBaseModel):
    commission_rates: list[float] = Field(default_factory=lambda: [0.0, 0.005, 0.01])
    expected_returns: list[float] = Field(default_factory=lambda: [0.03, 0.05, 0.07])
    product_type: ProductType = "investment_fund"
    strategy: StrategyName = "investment_fund_only"

    @field_validator("commission_rates", "expected_returns")
    @classmethod
    def validate_rates(cls, rates: list[float]) -> list[float]:
        if not rates:
            raise ValueError("Sensitivity rate lists cannot be empty.")
        for rate in rates:
            if not -1 <= rate <= 1:
                raise ValueError("Sensitivity rates must be between -1 and 1.")
        return rates


class ScenarioConfig(PlannerBaseModel):
    name: str
    annual_savings: float | None = Field(default=None, ge=0)
    inflation: float | None = Field(default=None, ge=-1, le=1)
    salary_growth: float | None = Field(default=None, ge=-1, le=1)
    mortgage_interest_rate: float | None = Field(default=None, ge=0, le=1)
    expected_return_shift: float = Field(default=0, ge=-1, le=1)
    commission_shift: float = Field(default=0, ge=-1, le=1)

    @field_validator("name")
    @classmethod
    def validate_name(cls, name: str) -> str:
        if not name.strip():
            raise ValueError("Scenario name cannot be blank.")
        return name


class ScenarioManagerConfig(PlannerBaseModel):
    scenarios: list[ScenarioConfig] = Field(default_factory=list)


class PlanningConfig(PlannerBaseModel):
    withdrawals: WithdrawalConfig = Field(default_factory=WithdrawalConfig)
    mixed_allocation: MixedAllocationConfig = Field(
        default_factory=MixedAllocationConfig
    )
    sensitivity: SensitivityConfig = Field(default_factory=SensitivityConfig)


class ProductConfig(PlannerBaseModel):
    name: str
    type: ProductType
    expected_return: float = Field(ge=-1, le=1)
    annual_commission: float = Field(ge=0, le=1)
    tax_treatment: TaxTreatment
    liquidity: str
    annual_contribution_limit_per_person: float | None = Field(default=None, ge=0)
    insurance_cost: float = Field(default=0, ge=0, le=1)
    notes: str | None = None


class AssumptionsConfig(PlannerBaseModel):
    inflation: float = Field(default=0, ge=-1, le=1)
    salary_growth: float = Field(default=0, ge=-1, le=1)
    default_market_return: float = Field(default=0.05, ge=-1, le=1)
    default_remunerated_account_return: float = Field(default=0.02, ge=-1, le=1)
    pension_redemption_years: PositiveInt = 20


class StrategyConfig(PlannerBaseModel):
    enabled: list[StrategyName] = Field(
        default_factory=lambda: [
            "investment_fund_only",
            "pension_plan_reinvest_tax_saving",
            "unit_linked",
            "mortgage_amortization",
        ]
    )

    @field_validator("enabled")
    @classmethod
    def validate_enabled(cls, enabled: list[StrategyName]) -> list[StrategyName]:
        if not enabled:
            raise ValueError("At least one strategy must be enabled.")
        return enabled


class SimulationConfig(PlannerBaseModel):
    household: HouseholdConfig
    people: list[Person] = Field(min_length=1)
    mortgage: MortgageConfig
    assumptions: AssumptionsConfig = Field(default_factory=AssumptionsConfig)
    tax: TaxConfig = Field(default_factory=TaxConfig)
    products: list[ProductConfig] = Field(default_factory=list)
    strategies: StrategyConfig = Field(default_factory=StrategyConfig)
    planning: PlanningConfig = Field(default_factory=PlanningConfig)
    scenario_manager: ScenarioManagerConfig = Field(
        default_factory=ScenarioManagerConfig
    )


class YearlyResult(PlannerBaseModel):
    strategy: StrategyName
    year: int
    age: int
    gross_wealth: float
    net_wealth: float
    real_net_wealth: float = 0
    taxes_paid: float
    fees_paid: float
    mortgage_balance: float
    liquidity: float
    liquidity_gap: float = 0
    pension_balance: float = 0
    investment_balance: float = 0
    unit_linked_balance: float = 0
    annual_contribution: float = 0
    withdrawal: float = 0
    withdrawal_tax: float = 0
    extra_mortgage_amortization: float = 0
    assumptions: dict[str, float | str] = Field(default_factory=dict)


class StrategyResult(PlannerBaseModel):
    strategy: StrategyName
    yearly_results: list[YearlyResult]

    def final_year(self) -> YearlyResult:
        if not self.yearly_results:
            raise ValueError("StrategyResult has no yearly results.")
        return self.yearly_results[-1]
