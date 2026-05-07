# pylint: disable=missing-function-docstring,missing-module-docstring,duplicate-code,import-outside-toplevel,line-too-long,wrong-import-position,wrong-import-order
"""Tests for frontend interaction logic backed by SQLite."""

from pathlib import Path

from penguin_classifier.service import PenguinService
from penguin_classifier.preprocessing import PredictionInput


def test_clicking_delete_equivalent_removes_correct_record(tmp_path: Path) -> None:
    service = PenguinService(tmp_path / "penguins.db")
    first = service.save_classification(
        algorithm="Random Forest",
        prediction="",
        confidence=None,
        features=PredictionInput(
            island="Biscoe",
            sex="male",
            culmen_length_mm=45,
            culmen_depth_mm=17,
            flipper_length_mm=200,
            body_mass_g=4200,
        )
    )
    second = service.save_classification(
        algorithm="SVM",
        prediction="",
        confidence=None,
        features=PredictionInput(
            island="Dream",
            sex="female",
            culmen_length_mm=39,
            culmen_depth_mm=19,
            flipper_length_mm=189,
            body_mass_g=3450,
        )
    )

    deleted = service.delete_saved_penguin(first["id"])
    rows = service.list_saved_penguins()

    assert deleted is True
    assert len(rows) == 1
    assert rows[0]["id"] == second["id"]
    assert rows[0]["algorithm"] == "SVM"
