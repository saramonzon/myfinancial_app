"""YAML configuration loading and validation."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from financial_planner.models import ProductConfig, SimulationConfig


def load_yaml_document(path: str | Path) -> Any:
    """Load a YAML document from disk."""
    config_path = Path(path)
    with config_path.open("r", encoding="utf-8") as file:
        data = yaml.safe_load(file)
    if data is None:
        return {}
    return data


def load_yaml(path: str | Path) -> dict[str, Any]:
    """Load a YAML mapping from disk and fail clearly on invalid shape."""

    data = load_yaml_document(path)
    if not isinstance(data, dict):
        raise ValueError(f"YAML file must contain a mapping: {Path(path)}")
    return data


def load_products(path: str | Path) -> list[ProductConfig]:
    """Load generic product assumptions from a YAML file."""

    data = load_yaml_document(path)
    products_data = data.get("products", data) if isinstance(data, dict) else data
    if not isinstance(products_data, list):
        raise ValueError("Product YAML must contain a 'products' list or be a list.")
    return [ProductConfig.model_validate(product) for product in products_data]


def load_config(
    inputs_path: str | Path,
    products_path: str | Path | None = None,
) -> SimulationConfig:
    """Load and validate a complete simulation config from YAML files."""

    data = load_yaml(inputs_path)
    if products_path is not None:
        data["products"] = [
            product.model_dump() for product in load_products(products_path)
        ]
    return SimulationConfig.model_validate(data)
