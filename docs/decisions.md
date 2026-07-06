# Design decisions

## Initial decisions

- Build the calculation engine in Python.
- Use Streamlit for the dashboard.
- Export results to Excel and Markdown.
- Keep products generic and configurable.
- Avoid bank-specific recommendations.
- Use YAML files for default input data.
- Keep real personal data out of version control.
- Keep Streamlit free of financial formulas and strategy logic.
- Use Pydantic to validate external YAML inputs.
- Use dataclasses for internal helper return values where useful.
- Use annual deterministic simulations for v1.0.
- Use non-fatal validation warnings for reviewable assumptions and hard validation for invalid input shapes.

## Rationale

Python is easier to test and maintain than a complex Excel workbook.
Excel is still useful as an export format.
Markdown gives a plain-text auditable report that can be versioned or shared without spreadsheet tooling.
