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

## Decision Helpers

| helper | metric | value | detail |
| --- | --- | --- | --- |
| break_even_commission | break_even_commission | nan | investment_fund_only vs mortgage_amortization |
| break_even_commission | target_net_wealth | 10000.0 | product_type=investment_fund |
| amortize_vs_invest | mortgage_interest_saved | 64840.836205757994 | extra amortization scenario |
| amortize_vs_invest | expected_after_tax_investment_gain | 509540.1185950977 | investment fund scenario |
| amortize_vs_invest | difference | 444699.2823893397 | preferred=investment |

## Scenario Summary

| scenario | strategy | year | net_wealth | real_net_wealth | gross_wealth | taxes_paid | fees_paid | mortgage_balance | liquidity_gap |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| baseline | pension_plan_reinvest_tax_saving | 2053 | 1003279.9233125577 | 576258.4573808793 | 1208121.0640872363 | 161517.8183301613 | 51071.12671439147 | 24875.1215099377 | 20000.0 |
| baseline | mortgage_amortization | 2053 | 10000.0 | 5743.745528947001 | 0.0 | 0.0 | 0.0 | 0.0 | 20000.0 |
| baseline | unit_linked | 2053 | 783047.2091061089 | 449762.390625764 | 906567.5761863652 | 108645.24557031861 | 182539.09011421437 | 24875.1215099377 | 20000.0 |
| baseline | investment_fund_only | 2053 | 965064.9970851592 | 554308.7762151134 | 1155907.0117741053 | 175966.89317900842 | 38365.22874765321 | 24875.1215099377 | 20000.0 |
| baseline | mixed_allocation | 2053 | 722681.5987588153 | 415089.92017232155 | 832396.9922778734 | 119715.39351905827 | 69090.54192420478 | 0.0 | 20000.0 |
| lower_return | pension_plan_reinvest_tax_saving | 2053 | 865164.3474881528 | 496928.3852689427 | 1022064.663584485 | 113576.99365181504 | 45420.609149463126 | 24875.1215099377 | 20000.0 |
| lower_return | mortgage_amortization | 2053 | 10000.0 | 5743.745528947001 | 0.0 | 0.0 | 0.0 | 0.0 | 20000.0 |
| lower_return | unit_linked | 2053 | 685345.0141122964 | 393644.7360593621 | 772728.95290717 | 72508.81728493591 | 163293.95315654486 | 24875.1215099377 | 20000.0 |
| lower_return | investment_fund_only | 2053 | 834796.1856038383 | 479485.68586440565 | 977456.5850873643 | 127785.27797358837 | 34092.385123269974 | 24875.1215099377 | 20000.0 |
| lower_return | mixed_allocation | 2053 | 626732.0911751506 | 359978.9646534875 | 705569.053729881 | 88836.96255473042 | 61650.10248238159 | 0.0 | 20000.0 |
| higher_savings | pension_plan_reinvest_tax_saving | 2053 | 1188198.0411401954 | 682470.7186302582 | 1428293.8282346851 | 196772.46464997245 | 58378.78933299209 | 24875.1215099377 | 20000.0 |
| higher_savings | mortgage_amortization | 2053 | 10000.0 | 5743.745528947001 | 0.0 | 0.0 | 0.0 | 0.0 | 20000.0 |
| higher_savings | unit_linked | 2053 | 933295.2720805941 | 536061.0546200287 | 1079247.1145075778 | 131076.720917046 | 217308.44061216 | 24875.1215099377 | 20000.0 |
| higher_savings | investment_fund_only | 2053 | 1149983.1149127965 | 660521.037464492 | 1376079.7759215538 | 211221.53949881953 | 45672.89136625381 | 24875.1215099377 | 20000.0 |
| higher_savings | mixed_allocation | 2053 | 827363.094791337 | 475216.3076523495 | 955002.0056010954 | 137638.91080975847 | 78967.47707123414 | 0.0 | 20000.0 |

## Sensitivity Summary

| strategy | product_type | expected_return | annual_commission | final_net_wealth | final_real_net_wealth | final_fees_paid | final_taxes_paid |
| --- | --- | --- | --- | --- | --- | --- | --- |
| investment_fund_only | investment_fund | 0.03 | 0.0 | 663552.8573466963 | 381127.8757605094 | 0.0 | 64448.70450861807 |
| investment_fund_only | investment_fund | 0.03 | 0.003 | 637615.6644332163 | 366230.21217748575 | 27207.878548196964 | 54855.49617075559 |
| investment_fund_only | investment_fund | 0.03 | 0.008 | 596852.3938987053 | 342816.82688970026 | 68952.32088946819 | 40760.166940244 |
| investment_fund_only | investment_fund | 0.03 | 0.015 | 544087.9437256126 | 312510.26941279543 | 120586.9021189142 | 24999.357148281262 |
| investment_fund_only | investment_fund | 0.05 | 0.0 | 873314.6173252569 | 501609.6928626005 | 0.0 | 142031.82121301722 |
| investment_fund_only | investment_fund | 0.05 | 0.003 | 834796.1856038383 | 479485.68586440565 | 34092.385123269974 | 127785.27797358837 |
| investment_fund_only | investment_fund | 0.05 | 0.008 | 775498.9703060547 | 445426.87433984043 | 85984.40368988193 | 105853.43121961363 |
| investment_fund_only | investment_fund | 0.05 | 0.015 | 701765.6945422875 | 403076.35703956505 | 149371.17699520232 | 78582.21963575453 |
| investment_fund_only | investment_fund | 0.07 | 0.0 | 1180206.7135128544 | 677880.7033972691 | 0.0 | 255539.85678925196 |
| investment_fund_only | investment_fund | 0.07 | 0.003 | 1122687.4878437074 | 644843.1238707035 | 43323.62067213737 | 234265.6226376496 |
| investment_fund_only | investment_fund | 0.07 | 0.008 | 1034370.3275703724 | 594115.9944257771 | 108733.9880343771 | 201600.37157764894 |
| investment_fund_only | investment_fund | 0.07 | 0.015 | 924995.4462049415 | 531293.8458435968 | 187607.16065925616 | 161146.6483329005 |

## Product Comparison

| name | type | expected_return | annual_commission | insurance_cost | total_annual_cost | simple_net_return_before_tax | tax_treatment | liquidity |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Remunerated account | remunerated_account | 0.025 | 0.0 | 0.0 | 0.0 | 0.025 | savings_income | immediate |
| Money market fund | money_market_fund | 0.025 | 0.002 | 0.0 | 0.002 | 0.023 | savings_income_deferred | high |
| Global investment fund | investment_fund | 0.06 | 0.003 | 0.0 | 0.003 | 0.056999999999999995 | savings_income_deferred | high |
| Pension plan | pension_plan | 0.06 | 0.008 | 0.0 | 0.008 | 0.052 | general_income_on_redemption | restricted |
| Unit linked | unit_linked | 0.06 | 0.0167 | 0.0 | 0.0167 | 0.0433 | savings_income | medium_high |

## Validation Warnings

| code | message | severity |
| --- | --- | --- |
| liquidity_below_target | Current liquidity is below the configured target liquidity. | warning |

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
| tax | savings_tax_brackets | [{'up_to': 6000.0, 'rate': 0.19}, {'up_to': 50000.0, 'rate': 0.21}, {'up_to': 200000.0, 'rate': 0.23}, {'up_to': None, 'rate': 0.27}] |
| tax | general_income_tax_brackets | [{'up_to': 12450.0, 'rate': 0.19}, {'up_to': 20200.0, 'rate': 0.24}, {'up_to': 35200.0, 'rate': 0.3}, {'up_to': 60000.0, 'rate': 0.37}, {'up_to': 300000.0, 'rate': 0.45}, {'up_to': None, 'rate': 0.47}] |
| tax | pension_contribution_limit_per_person | 1500.0 |
| planning | withdrawals | {'annual_amount': 0.0, 'start_year': None, 'end_year': None} |
| planning | mixed_allocation | {'investment_fund': 0.4, 'pension_plan': 0.2, 'unit_linked': 0.2, 'mortgage_amortization': 0.2} |
| planning | sensitivity | {'commission_rates': [0.0, 0.003, 0.008, 0.015], 'expected_returns': [0.03, 0.05, 0.07], 'product_type': 'investment_fund', 'strategy': 'investment_fund_only'} |
| strategies | enabled | ['investment_fund_only', 'pension_plan_reinvest_tax_saving', 'unit_linked', 'mortgage_amortization', 'mixed_allocation'] |
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
