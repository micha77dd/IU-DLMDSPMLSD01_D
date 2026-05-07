# pylint: disable=missing-function-docstring,missing-module-docstring,duplicate-code,import-outside-toplevel,line-too-long,wrong-import-position,wrong-import-order
"""Tests for dropdown option helpers."""

from penguin_classifier.ui_options import as_dropdown_options


def test_as_dropdown_options_maps_values_to_label_value_dicts() -> None:
    options = as_dropdown_options(["A", "B"])

    assert options == [
        {"label": "A", "value": "A"},
        {"label": "B", "value": "B"},
    ]
