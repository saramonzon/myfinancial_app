"""Tests for presentation formatting helpers."""

import pandas as pd

from financial_planner.localization import localize_display_dataframe


def test_localize_display_dataframe_formats_large_numbers() -> None:
    df = pd.DataFrame(
        [
            {
                "year": 2053,
                "net_wealth": 1_234_567.891,
                "age": 42,
                "annual_contribution": 6_000,
            }
        ]
    )

    display = localize_display_dataframe(df)

    assert display["año"].iloc[0] == "2053"
    assert display["edad"].iloc[0] == "42"
    assert display["patrimonio_neto"].iloc[0] == "1,234,567.89"
    assert display["aportacion_anual"].iloc[0] == "6,000.00"
