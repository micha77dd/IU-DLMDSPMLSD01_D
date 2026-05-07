# pylint: disable=missing-function-docstring,missing-module-docstring,duplicate-code,import-outside-toplevel,line-too-long,wrong-import-position,wrong-import-order
"""Tests for Dash app creation."""

from penguin_classifier.app import create_app
from penguin_classifier.config import AppConfig


def test_create_app_sets_expected_title() -> None:
    app = create_app(AppConfig())

    assert app.title == "Pinguinklassifizierer"
