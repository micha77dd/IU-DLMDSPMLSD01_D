"""Inference service for penguin classification models."""

from dataclasses import dataclass
from pathlib import Path

from .prediction import PredictionResult
from .preprocessing import build_prediction_frame
from .models import PredictionInput
from .training import ensure_model, ensure_random_forest_model


@dataclass
class ModelInferenceService:
    """Service for running model inference."""

    model_path: Path | None = None
    dataset_path: Path | None = None

    def predict_random_forest(self, prediction_input: PredictionInput) -> PredictionResult:
        """Run a random forest prediction for a single penguin sample."""

        model = ensure_random_forest_model(self.model_path, self.dataset_path)
        frame = build_prediction_frame(prediction_input)
        probabilities = model.predict_proba(frame)[0]
        classes = model.classes_
        probability_map = {
            species: float(probability)
            for species, probability in zip(classes, probabilities, strict=True)
        }
        predicted_species = max(probability_map, key=probability_map.get)
        confidence = probability_map[predicted_species]
        return PredictionResult(
            species=predicted_species,
            confidence=confidence,
            probabilities=probability_map,
        )

    def predict(self, algorithm: str, prediction_input: PredictionInput) -> PredictionResult:
        """Run a prediction for a single penguin sample using the specified algorithm."""
        model = ensure_model(algorithm, self.model_path, self.dataset_path)
        frame = build_prediction_frame(prediction_input)
        probabilities = model.predict_proba(frame)[0]
        classes = model.classes_
        probability_map = {
            species: float(probability)
            for species, probability in zip(classes, probabilities, strict=True)
        }
        predicted_species = max(probability_map, key=probability_map.get)
        confidence = probability_map[predicted_species]
        return PredictionResult(
            species=predicted_species,
            confidence=confidence,
            probabilities=probability_map,
        )
