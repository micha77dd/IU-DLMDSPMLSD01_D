# pylint: disable=missing-function-docstring,missing-module-docstring,duplicate-code,import-outside-toplevel,line-too-long,wrong-import-position,wrong-import-order
"""Tests for app callback registration."""

from penguin_classifier.app import create_app
from penguin_classifier.config import AppConfig


def test_app_registers_prediction_update_and_page_size_callbacks() -> None:
    app = create_app(AppConfig())

    callback_keys = set(app.callback_map.keys())

    expected_outputs = [
        "saved-penguins-table.data",
        "comparison-scatter.figure",
        "prediction-summary.children",
        "probability-chart.figure"
    ]
    for expected in expected_outputs:
        assert any(expected in key for key in callback_keys), f"Missing {expected} in callbacks"
    assert "saved-penguins-table.page_size" in callback_keys
