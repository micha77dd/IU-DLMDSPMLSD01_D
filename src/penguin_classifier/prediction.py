"""Prediction result models."""

from dataclasses import dataclass


@dataclass(frozen=True)
class PredictionResult:
    """Prediction result returned by the model inference service."""

    species: str
    confidence: float
    probabilities: dict[str, float]


def get_placeholder_prediction() -> PredictionResult:
    """Return an initial neutral prediction state for the UI."""

    probabilities = {
        "Adelie": 0.0,
        "Chinstrap": 0.0,
        "Gentoo": 0.0,
    }
    return PredictionResult(
        species="Noch keine Vorhersage",
        confidence=0.0,
        probabilities=probabilities,
    )
