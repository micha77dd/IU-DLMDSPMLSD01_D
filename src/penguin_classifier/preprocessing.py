"""Preprocessing helpers for penguin model training and inference."""

import os
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .repository import PenguinRepository
from .models import PredictionInput


def _get_data_dir() -> Path:
    env_dir = os.getenv("PENGUIN_APP_DATA_DIR")
    if env_dir:
        return Path(env_dir)
    return Path(__file__).resolve().parent.parent / "data"


DATASET_PATH = Path(__file__).resolve().parent.parent / "data" / "penguins.csv"
FEATURE_COLUMNS = [
    "island",
    "sex",
    "culmen_length_mm",
    "culmen_depth_mm",
    "flipper_length_mm",
    "body_mass_g",
]
TARGET_COLUMN = "species"


@dataclass(frozen=True)
class PreparedDataset:
    """Prepared dataset for model training."""

    features: pd.DataFrame
    target: pd.Series


@dataclass(frozen=True)
class FeatureMapping:
    """Mapping information for feature names."""

    rename_map: dict[str, str]


def load_raw_dataset(dataset_path: Path | None = None) -> pd.DataFrame:
    """Load the Palmer Penguins dataset and normalize column names."""

    path = dataset_path or DATASET_PATH
    if not path.exists():
        fallback = Path(__file__).resolve().parent.parent / "data" / "penguins.csv"
        if fallback.exists():
            path = fallback
    dataframe = pd.read_csv(path)
    return dataframe.rename(
        columns={
            "bill_length_mm": "culmen_length_mm",
            "bill_depth_mm": "culmen_depth_mm",
        }
    )


def prepare_training_dataset(
    dataset_path: Path | None = None,
    database_path: Path | None = None
) -> PreparedDataset:
    """Prepare cleaned training data for the random forest model."""
    dataframe = load_raw_dataset(dataset_path).copy()

    # Load DB records and append
    repo = PenguinRepository(database_path)
    records = repo.list_records()
    if records:
        db_data = []
        for r in records:
            if r.prediction:  # Only use records with a prediction
                db_data.append({
                    "island": r.island,
                    "sex": r.sex,
                    "culmen_length_mm": r.culmen_length_mm,
                    "culmen_depth_mm": r.culmen_depth_mm,
                    "flipper_length_mm": r.flipper_length_mm,
                    "body_mass_g": r.body_mass_g,
                    "species": r.prediction
                })
        if db_data:
            df_db = pd.DataFrame(db_data)
            dataframe = pd.concat([dataframe, df_db], ignore_index=True)

    dataframe["sex"] = dataframe["sex"].astype(str).str.lower()
    dataframe = dataframe.dropna(subset=FEATURE_COLUMNS + [TARGET_COLUMN])
    dataframe = dataframe[dataframe["sex"].isin(["male", "female"])]
    features = dataframe[FEATURE_COLUMNS].copy()
    target = dataframe[TARGET_COLUMN].copy()
    return PreparedDataset(features=features, target=target)


def build_prediction_frame(prediction_input: PredictionInput) -> pd.DataFrame:
    """Convert a single prediction input into a DataFrame."""

    return pd.DataFrame(
        [
            {
                "island": prediction_input.island,
                "sex": prediction_input.sex.lower(),
                "culmen_length_mm": prediction_input.culmen_length_mm,
                "culmen_depth_mm": prediction_input.culmen_depth_mm,
                "flipper_length_mm": prediction_input.flipper_length_mm,
                "body_mass_g": prediction_input.body_mass_g,
            }
        ]
    )
