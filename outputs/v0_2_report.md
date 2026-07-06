# Financial Planner Report

Simplified planning model only. This is not financial, tax, or legal advice.

## Final Comparison

| strategy | year | net_wealth | real_net_wealth | gross_wealth | taxes_paid | fees_paid | mortgage_balance | liquidity_gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| pension_plan_reinvest_tax_saving | 2053 | 1003279.9233125577 | 576258.4573808793 | 1208121.0640872363 | 161517.8183301613 | 51071.12671439147 | 24875.1215099377 | 20000.0 |
| mortgage_amortization | 2053 | 10000.0 | 5743.745528947001 | 0.0 | 0.0 | 0.0 | 0.0 | 20000.0 |
| unit_linked | 2053 | 783047.2091061089 | 449762.390625764 | 906567.5761863652 | 108645.24557031861 | 182539.09011421437 | 24875.1215099377 | 20000.0 |
| investment_fund_only | 2053 | 965064.9970851592 | 554308.7762151134 | 1155907.0117741053 | 175966.89317900842 | 38365.22874765321 | 24875.1215099377 | 20000.0 |
| mixed_allocation | 2053 | 722681.5987588153 | 415089.92017232155 | 832396.9922778734 | 119715.39351905827 | 69090.54192420478 | 0.0 | 20000.0 |

## Key Assumptions

| section | name | value |
| --- | --- | --- |
| household | current_year | 2026 |
| household | retirement_age | 67 |
| household | annual_savings | 16800.0 |
| household | current_liquidity | 10000.0 |
| household | target_liquidity | 30000.0 |
| mortgage | initial_principal | 281000.0 |
| mortgage | annual_interest_rate | 0.0215 |
| mortgage | term_years | 30 |
| mortgage | annual_extra_amortization | 4800.0 |
| mortgage | extra_amortization_mode | reduce_term |
| assumptions | inflation | 0.02 |
| assumptions | salary_growth | 0.02 |
| assumptions | default_market_return | 0.06 |
| assumptions | default_remunerated_account_return | 0.025 |
| assumptions | pension_redemption_years | 20 |
| product | Remunerated account | remunerated_account, return=0.025, fee=0.0 |
| product | Money market fund | money_market_fund, return=0.025, fee=0.002 |
| product | Global investment fund | investment_fund, return=0.06, fee=0.003 |
| product | Pension plan | pension_plan, return=0.06, fee=0.008 |
| product | Unit linked | unit_linked, return=0.06, fee=0.0167 |

## Model Limitations

- Tax modelling is simplified and configurable.
- Product assumptions are generic and do not represent specific providers.
- Investment returns are deterministic expected returns, not stochastic forecasts.
- Net wealth assumes liquidation taxes where configured by the strategy.
