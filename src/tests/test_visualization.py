# pylint: disable=missing-function-docstring,missing-module-docstring,duplicate-code,import-outside-toplevel,line-too-long,wrong-import-position,wrong-import-order
"""Tests for plot creation."""

from penguin_classifier.prediction import get_placeholder_prediction
from penguin_classifier.visualization import (
    build_probability_figure,
    build_saved_penguins_scatter,
)


def test_build_probability_figure_contains_neutral_initial_values() -> None:
    figure = build_probability_figure(get_placeholder_prediction(), ["Adelie", "Chinstrap", "Gentoo"])

    assert figure.layout.title.text == "Vorhersagewahrscheinlichkeiten"
    assert list(figure.data[0].x) == ["Adelie", "Chinstrap", "Gentoo"]
    assert list(figure.data[0].y) == [0.0, 0.0, 0.0]


def test_build_saved_penguins_scatter_uses_species_colors_and_gray_for_unknown() -> None:
    figure = build_saved_penguins_scatter(
        [
            {
                "timestamp": "2026-04-02 20:00",
                "algorithm": "RF",
                "prediction": "Adelie",
                "confidence": "80%",
                "island": "Dream",
                "sex": "female",
                "culmen_length_mm": 39.1,
                "culmen_depth_mm": 18.7,
                "flipper_length_mm": 181,
                "body_mass_g": 3750,
            },
            {
                "timestamp": "2026-04-02 20:01",
                "algorithm": "RF",
                "prediction": "",
                "confidence": "",
                "island": "Biscoe",
                "sex": "male",
                "culmen_length_mm": 46.5,
                "culmen_depth_mm": 15.3,
                "flipper_length_mm": 211,
                "body_mass_g": 4500,
            },
        ]
    )

    assert figure.layout.title.text == "Datensatz-Vergleich"
    assert len(figure.data) == 2
    assert figure.data[0].name == "Adelie"
    assert figure.data[0].marker.color == "#1f77b4"
    assert figure.data[1].name == "Nicht klassifiziert"
    assert figure.data[1].marker.color == "#9aa5b1"
