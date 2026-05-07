"""Reusable option builders for UI components."""

from collections.abc import Iterable


def as_dropdown_options(values: Iterable[str]) -> list[dict[str, str]]:
    """Convert string values into Dash dropdown options."""

    return [{"label": value, "value": value} for value in values]
