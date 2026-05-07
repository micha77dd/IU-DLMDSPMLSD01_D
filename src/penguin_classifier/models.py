"""Domain models for persisted penguin classifications."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class PredictionInput:
    """Input values for a single penguin prediction."""

    island: str
    sex: str
    culmen_length_mm: float
    culmen_depth_mm: float
    flipper_length_mm: float
    body_mass_g: float

    def __post_init__(self):
        if self.culmen_length_mm <= 0:
            raise ValueError("culmen_length_mm must be > 0")
        if self.culmen_depth_mm <= 0:
            raise ValueError("culmen_depth_mm must be > 0")
        if self.flipper_length_mm <= 0:
            raise ValueError("flipper_length_mm must be > 0")
        if self.body_mass_g <= 0:
            raise ValueError("body_mass_g must be > 0")


@dataclass(frozen=True)
class PenguinRecord(PredictionInput):
    """Persisted penguin classification record."""

    id: int | None
    created_at: datetime
    algorithm: str
    prediction: str
    confidence: float
