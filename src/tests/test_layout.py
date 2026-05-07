# pylint: disable=missing-function-docstring,missing-module-docstring,duplicate-code,import-outside-toplevel,line-too-long,wrong-import-position,wrong-import-order
"""Tests for Dash layout composition."""

from dash import html

from penguin_classifier.config import AppConfig
from penguin_classifier.layout import create_layout


def test_layout_contains_expected_sections() -> None:
    layout = create_layout(AppConfig())

    assert isinstance(layout, html.Div)
    assert layout.children[0].children[0].children == "Pinguinklassifizierer"


def test_layout_contains_required_component_ids() -> None:
    layout = create_layout(AppConfig())

    component_ids = set()

    def collect_ids(node) -> None:
        if hasattr(node, "id") and node.id is not None:
            component_ids.add(node.id)
        children = getattr(node, "children", None)
        if children is None:
            return
        if isinstance(children, (list, tuple)):
            for child in children:
                collect_ids(child)
        else:
            collect_ids(children)

    collect_ids(layout)

    assert {
        "algorithm-tabs",
        "overwrite-confirm-dialog",
        "island-dropdown",
        "sex-dropdown",
        "culmen-length-slider",
        "culmen-depth-slider",
        "flipper-length-slider",
        "body-mass-slider",
        "reset-button",
        "prediction-summary",
        "probability-chart",
        "comparison-scatter",
        "saved-penguins-table",
        "saved-penguins-page-size",
    }.issubset(component_ids)
