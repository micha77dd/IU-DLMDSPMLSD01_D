# pylint: disable=missing-function-docstring,missing-module-docstring,duplicate-code,import-outside-toplevel,line-too-long,wrong-import-position,wrong-import-order
"""Tests for Random Forest training and inference."""

from pathlib import Path

from penguin_classifier.inference import ModelInferenceService
from penguin_classifier.preprocessing import PredictionInput
from penguin_classifier.training import ensure_random_forest_model


def test_random_forest_model_can_be_trained_and_saved(tmp_path: Path) -> None:
    model_path = tmp_path / "random_forest.pkl"

    model = ensure_random_forest_model(model_path=model_path, force_retrain=True)

    assert model_path.exists()
    assert hasattr(model, "predict")
    assert hasattr(model, "predict_proba")


def test_random_forest_inference_returns_valid_species_and_probabilities(tmp_path: Path) -> None:
    # Ensure model exists before creating service
    ensure_random_forest_model(model_path=tmp_path / "random_forest.pkl", force_retrain=True)
    service = ModelInferenceService(model_path=tmp_path / "random_forest.pkl")

    result = service.predict_random_forest(
        PredictionInput(
            island="Biscoe",
            sex="male",
            culmen_length_mm=47.0,
            culmen_depth_mm=15.0,
            flipper_length_mm=220.0,
            body_mass_g=5200.0,
        )
    )

    assert result.species in {"Adelie", "Chinstrap", "Gentoo"}
    assert 0.0 <= result.confidence <= 1.0
    assert set(result.probabilities.keys()) == {"Adelie", "Chinstrap", "Gentoo"}
    assert abs(sum(result.probabilities.values()) - 1.0) < 1e-9


from unittest.mock import MagicMock, patch


def test_predict_always_returns_species_with_highest_probability() -> None:
    """
    Stellt sicher, dass die vorhergesagte Art immer der Klasse mit der höchsten 
    Wahrscheinlichkeit entspricht, selbst wenn das Modell via .predict() etwas anderes zurückgeben würde.
    """
    service = ModelInferenceService()

    mock_model = MagicMock()
    # model.predict returns Adelie
    mock_model.predict.return_value = ["Adelie"]
    # model.predict_proba returns Chinstrap as highest (index 1)
    mock_model.predict_proba.return_value = [[0.2, 0.7, 0.1]]
    mock_model.classes_ = ["Adelie", "Chinstrap", "Gentoo"]

    dummy_input = PredictionInput(
        island="Biscoe",
        sex="male",
        culmen_length_mm=47.0,
        culmen_depth_mm=15.0,
        flipper_length_mm=220.0,
        body_mass_g=5200.0,
    )

    with patch("penguin_classifier.inference.ensure_model", return_value=mock_model):
        with patch("penguin_classifier.inference.build_prediction_frame", return_value=MagicMock()):
            result = service.predict("SVM", dummy_input)

            assert result.species == "Chinstrap"
            assert result.confidence == 0.7
