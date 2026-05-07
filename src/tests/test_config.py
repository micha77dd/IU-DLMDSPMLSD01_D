# pylint: disable=missing-function-docstring,missing-module-docstring,duplicate-code,import-outside-toplevel,line-too-long,wrong-import-position,wrong-import-order
"""Tests for frontend configuration."""

from penguin_classifier.config import AppConfig


def test_app_config_contains_expected_algorithms() -> None:
    config = AppConfig()

    assert config.algorithms == (
        "Random Forest",
        "SVM",
        "Logistic Regression",
    )


def test_app_config_contains_expected_species() -> None:
    config = AppConfig()

    assert config.species == ("Adelie", "Chinstrap", "Gentoo")
