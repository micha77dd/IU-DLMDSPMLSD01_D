# pylint: disable=missing-function-docstring,missing-module-docstring,duplicate-code,import-outside-toplevel,line-too-long,wrong-import-position,wrong-import-order
"""Tests for placeholder prediction behavior."""

from penguin_classifier.prediction import get_placeholder_prediction


def test_placeholder_prediction_is_neutral_initial_state() -> None:
    prediction = get_placeholder_prediction()

    assert prediction.species == "Noch keine Vorhersage"
    assert prediction.confidence == 0.0
    assert prediction.probabilities == {
        "Adelie": 0.0,
        "Chinstrap": 0.0,
        "Gentoo": 0.0,
    }
    assert sum(prediction.probabilities.values()) == 0.0
