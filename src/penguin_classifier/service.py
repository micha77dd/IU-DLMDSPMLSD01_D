"""Application service layer for penguin persistence."""
# pylint: disable=too-many-arguments, line-too-long, import-error, broad-exception-caught

import random
from datetime import datetime
from pathlib import Path
from typing import Any

import numpy as np

from .models import PenguinRecord
from .preprocessing import load_raw_dataset, build_prediction_frame, FEATURE_COLUMNS
from .models import PredictionInput
from .repository import PenguinRepository
from .training import ensure_model


class PenguinService:
    """Service for persisting and formatting penguin classification records."""

    def __init__(self, database_path: Path | None = None) -> None:
        """Initialize the service with the given database path."""
        self._repository = PenguinRepository(database_path)

    def list_saved_penguins(self) -> list[dict[str, Any]]:
        """List all saved penguin records as table rows."""
        records = self._repository.list_records()
        return [self._to_table_row(record) for record in records]

    def save_classification(
            self,
            *,
            algorithm: str,
            prediction: str | None,
            confidence: float | None,
            features: PredictionInput,
    ) -> dict[str, Any]:
        """Save a new penguin classification record."""
        record = PenguinRecord(
            id=None,
            created_at=datetime.now(),
            algorithm=algorithm,
            prediction=prediction or "",
            confidence=confidence if confidence is not None else 0.0,
            island=features.island,
            sex=features.sex,
            culmen_length_mm=features.culmen_length_mm,
            culmen_depth_mm=features.culmen_depth_mm,
            flipper_length_mm=features.flipper_length_mm,
            body_mass_g=features.body_mass_g,
        )
        saved_record = self._repository.add_record(record)
        return self._to_table_row(saved_record)

    def update_classification(
            self,
            *,
            record_id: int,
            algorithm: str,
            prediction: str | None,
            confidence: float | None,
            features: PredictionInput,
    ) -> bool:
        """Update an existing penguin classification record."""
        record = PenguinRecord(
            id=record_id,
            created_at=datetime.now(),  # not updated in DB
            algorithm=algorithm,
            prediction=prediction or "",
            confidence=confidence if confidence is not None else 0.0,
            island=features.island,
            sex=features.sex,
            culmen_length_mm=features.culmen_length_mm,
            culmen_depth_mm=features.culmen_depth_mm,
            flipper_length_mm=features.flipper_length_mm,
            body_mass_g=features.body_mass_g,
        )
        return self._repository.update_record(record)

    def delete_saved_penguin(self, record_id: int) -> bool:
        """Delete a specific saved penguin record by its ID."""
        return self._repository.delete_record(record_id)

    def delete_all_saved_penguins(self) -> None:
        """Delete all saved penguin records."""
        self._repository.delete_all_records()

    def insert_demo_data(self) -> None:
        """
        Insert random demo data from the raw dataset.
        
        Selects 5 random samples, evaluates them using available models 
        (or manually), and saves the classification records to the database.
        """
        df = load_raw_dataset()
        df["sex"] = df["sex"].astype(str).str.lower()
        df = df.dropna(subset=FEATURE_COLUMNS)
        df = df[df["sex"].isin(["male", "female"])]

        sample_df = df.sample(n=5)
        algorithms = ["Random Forest", "SVM", "Logistic Regression"]

        # Check which models are available
        available_algos = []
        for algo in algorithms:
            try:
                ensure_model(algo, force_retrain=False)
                available_algos.append(algo)
            except (ValueError, RuntimeError, FileNotFoundError):
                pass

        for _, row in sample_df.iterrows():
            input_data = PredictionInput(
                island=row["island"],
                sex=row["sex"],
                culmen_length_mm=row["culmen_length_mm"],
                culmen_depth_mm=row["culmen_depth_mm"],
                flipper_length_mm=row["flipper_length_mm"],
                body_mass_g=row["body_mass_g"]
            )
            pred_df = build_prediction_frame(input_data)

            algo = random.choice(available_algos) if available_algos else "Manuell"

            prediction = None
            confidence = None

            if algo != "Manuell":
                try:
                    pipeline = ensure_model(algo, force_retrain=False)
                    prediction = pipeline.predict(pred_df)[0]
                    if hasattr(pipeline, "predict_proba"):
                        probas = pipeline.predict_proba(pred_df)
                        confidence = float(np.max(probas[0]))
                except (ValueError, RuntimeError):
                    prediction = "Fehler"
                    confidence = 0.0

            if algo == "Manuell":
                prediction = row.get("species", "Manuell")
                confidence = 1.0

            self.save_classification(
                algorithm=algo,
                prediction=prediction,
                confidence=confidence,
                features=input_data,
            )

    @staticmethod
    def _to_table_row(record: PenguinRecord) -> dict[str, Any]:
        """Convert a PenguinRecord into a dictionary formatted for a table row."""
        confidence = "" if record.prediction == "" else f"{record.confidence:.0%}"
        return {
            "id": record.id,
            "timestamp": record.created_at.strftime("%Y-%m-%d %H:%M"),
            "algorithm": record.algorithm,
            "prediction": record.prediction,
            "confidence": confidence,
            "island": record.island,
            "sex": record.sex,
            "culmen_length_mm": record.culmen_length_mm,
            "culmen_depth_mm": record.culmen_depth_mm,
            "flipper_length_mm": record.flipper_length_mm,
            "body_mass_g": record.body_mass_g,
            "delete": "🗑",
        }
