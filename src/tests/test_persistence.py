# pylint: disable=missing-function-docstring,missing-module-docstring,duplicate-code,import-outside-toplevel,line-too-long,wrong-import-position,wrong-import-order
"""Tests for SQLite persistence layer."""

from pathlib import Path

from penguin_classifier.database import initialize_database
from penguin_classifier.service import PenguinService
from penguin_classifier.preprocessing import PredictionInput


def test_initialize_database_creates_sqlite_file(tmp_path: Path) -> None:
    database_path = tmp_path / "penguins.db"

    initialize_database(database_path)

    assert database_path.exists()


def test_service_can_save_and_list_records(tmp_path: Path) -> None:
    service = PenguinService(tmp_path / "penguins.db")

    service.save_classification(
        algorithm="Random Forest",
        prediction="Gentoo",
        confidence=0.91,
        features=PredictionInput(
            island="Biscoe",
            sex="male",
            culmen_length_mm=47.0,
            culmen_depth_mm=15.2,
            flipper_length_mm=217.0,
            body_mass_g=5100.0,
        )
    )

    rows = service.list_saved_penguins()

    assert len(rows) == 1
    assert rows[0]["algorithm"] == "Random Forest"
    assert rows[0]["prediction"] == "Gentoo"
    assert rows[0]["confidence"] == "91%"


def test_service_saves_empty_prediction_and_confidence(tmp_path: Path) -> None:
    service = PenguinService(tmp_path / "penguins.db")

    service.save_classification(
        algorithm="SVM",
        prediction="",
        confidence=None,
        features=PredictionInput(
            island="Dream",
            sex="female",
            culmen_length_mm=38.5,
            culmen_depth_mm=18.9,
            flipper_length_mm=190.0,
            body_mass_g=3500.0,
        )
    )

    rows = service.list_saved_penguins()

    assert len(rows) == 1
    assert rows[0]["prediction"] == ""
    assert rows[0]["confidence"] == ""


def test_service_can_delete_record(tmp_path: Path) -> None:
    service = PenguinService(tmp_path / "penguins.db")
    saved = service.save_classification(
        algorithm="SVM",
        prediction="Adelie",
        confidence=0.88,
        features=PredictionInput(
            island="Dream",
            sex="female",
            culmen_length_mm=38.5,
            culmen_depth_mm=18.9,
            flipper_length_mm=190.0,
            body_mass_g=3500.0,
        )
    )

    deleted = service.delete_saved_penguin(saved["id"])

    assert deleted is True
    assert service.list_saved_penguins() == []

def test_list_saved_penguins_returns_expected_columns(tmp_path: Path) -> None:
    database_path = tmp_path / "penguins.db"
    service = PenguinService(database_path)
    service.insert_demo_data()

    rows = service.list_saved_penguins()

    assert len(rows) >= 1
    assert {
        "id",
        "timestamp",
        "algorithm",
        "prediction",
        "confidence",
        "island",
        "sex",
        "culmen_length_mm",
        "culmen_depth_mm",
        "flipper_length_mm",
        "body_mass_g",
        "delete",
    }.issubset(rows[0].keys())
