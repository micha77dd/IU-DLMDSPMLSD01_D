"""Repository layer for penguin persistence."""

from datetime import datetime
from pathlib import Path

from .database import get_connection, initialize_database
from .models import PenguinRecord


class PenguinRepository:
    """Repository for CRUD operations on penguin records."""

    def __init__(self, database_path: Path | None = None) -> None:
        """Initialize the repository and ensure the database is initialized."""
        self._database_path = database_path
        initialize_database(self._database_path)

    def list_records(self) -> list[PenguinRecord]:
        """Retrieve all penguin records from the database, ordered by creation date."""
        with get_connection(self._database_path) as connection:
            rows = connection.execute(
                """
                SELECT id,
                       created_at,
                       algorithm,
                       prediction,
                       confidence,
                       island,
                       sex,
                       culmen_length_mm,
                       culmen_depth_mm,
                       flipper_length_mm,
                       body_mass_g
                FROM penguin_records
                ORDER BY created_at DESC, id DESC
                """
            ).fetchall()
        return [self._row_to_model(row) for row in rows]

    def add_record(self, record: PenguinRecord) -> PenguinRecord:
        """Add a new penguin record to the database."""
        with get_connection(self._database_path) as connection:
            cursor = connection.execute(
                """
                INSERT INTO penguin_records (created_at,
                                             algorithm,
                                             prediction,
                                             confidence,
                                             island,
                                             sex,
                                             culmen_length_mm,
                                             culmen_depth_mm,
                                             flipper_length_mm,
                                             body_mass_g)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    record.created_at.isoformat(timespec="minutes"),
                    record.algorithm,
                    record.prediction,
                    record.confidence,
                    record.island,
                    record.sex,
                    record.culmen_length_mm,
                    record.culmen_depth_mm,
                    record.flipper_length_mm,
                    record.body_mass_g,
                ),
            )
            connection.commit()
            created_id = cursor.lastrowid
        return PenguinRecord(
            id=created_id,
            created_at=record.created_at,
            algorithm=record.algorithm,
            prediction=record.prediction,
            confidence=record.confidence,
            island=record.island,
            sex=record.sex,
            culmen_length_mm=record.culmen_length_mm,
            culmen_depth_mm=record.culmen_depth_mm,
            flipper_length_mm=record.flipper_length_mm,
            body_mass_g=record.body_mass_g,
        )

    def update_record(self, record: PenguinRecord) -> bool:
        """Update an existing penguin record in the database."""
        with get_connection(self._database_path) as connection:
            cursor = connection.execute(
                '''
                UPDATE penguin_records
                SET algorithm         = ?,
                    prediction        = ?,
                    confidence        = ?,
                    island            = ?,
                    sex               = ?,
                    culmen_length_mm  = ?,
                    culmen_depth_mm   = ?,
                    flipper_length_mm = ?,
                    body_mass_g       = ?
                WHERE id = ?
                ''',
                (
                    record.algorithm,
                    record.prediction,
                    record.confidence,
                    record.island,
                    record.sex,
                    record.culmen_length_mm,
                    record.culmen_depth_mm,
                    record.flipper_length_mm,
                    record.body_mass_g,
                    record.id,
                ),
            )
            connection.commit()
        return cursor.rowcount > 0

    def delete_record(self, record_id: int) -> bool:
        """Delete a penguin record from the database by its ID."""
        with get_connection(self._database_path) as connection:
            cursor = connection.execute(
                "DELETE FROM penguin_records WHERE id = ?",
                (record_id,),
            )
            connection.commit()
        return cursor.rowcount > 0

    def delete_all_records(self) -> None:
        """Delete all penguin records from the database."""
        with get_connection(self._database_path) as connection:
            connection.execute("DELETE FROM penguin_records")
            connection.commit()

    @staticmethod
    def _row_to_model(row) -> PenguinRecord:
        """Convert a database row into a PenguinRecord model."""
        return PenguinRecord(
            id=row["id"],
            created_at=datetime.fromisoformat(row["created_at"]),
            algorithm=row["algorithm"],
            prediction=row["prediction"],
            confidence=row["confidence"],
            island=row["island"],
            sex=row["sex"],
            culmen_length_mm=row["culmen_length_mm"],
            culmen_depth_mm=row["culmen_depth_mm"],
            flipper_length_mm=row["flipper_length_mm"],
            body_mass_g=row["body_mass_g"],
        )
