"""Repository layer for custom species and islands."""

from typing import List

from .database import get_connection, initialize_database


class MetadataRepository:
    """Repository for managing custom species and islands in the database."""

    def __init__(self, database_path=None):
        self._database_path = database_path
        initialize_database(self._database_path)

    def list_custom_species(self) -> List[str]:
        """Retrieve all custom species from the database."""
        with get_connection(self._database_path) as conn:
            rows = conn.execute("SELECT name FROM custom_species ORDER BY name").fetchall()
        return [row["name"] for row in rows]

    def add_custom_species(self, name: str):
        """Add a new custom species to the database."""
        with get_connection(self._database_path) as conn:
            conn.execute("INSERT OR IGNORE INTO custom_species (name) VALUES (?)", (name,))
            conn.commit()

    def rename_custom_species(self, old_name: str, new_name: str):
        """Rename a custom species in both metadata and records."""
        with get_connection(self._database_path) as conn:
            conn.execute("UPDATE custom_species SET name = ? WHERE name = ?", (new_name, old_name))
            conn.execute(
                "UPDATE penguin_records SET prediction = ? WHERE prediction = ?",
                (new_name, old_name),
            )
            conn.commit()

    def delete_custom_species(self, name: str):
        """Delete a custom species from the database."""
        with get_connection(self._database_path) as conn:
            conn.execute("DELETE FROM custom_species WHERE name = ?", (name,))
            # optional: update records, but simple delete is fine
            conn.commit()

    def list_custom_islands(self) -> List[str]:
        """Retrieve all custom islands from the database."""
        with get_connection(self._database_path) as conn:
            rows = conn.execute("SELECT name FROM custom_islands ORDER BY name").fetchall()
        return [row["name"] for row in rows]

    def add_custom_island(self, name: str):
        """Add a new custom island to the database."""
        with get_connection(self._database_path) as conn:
            conn.execute("INSERT OR IGNORE INTO custom_islands (name) VALUES (?)", (name,))
            conn.commit()

    def rename_custom_island(self, old_name: str, new_name: str):
        """Rename a custom island in both metadata and records."""
        with get_connection(self._database_path) as conn:
            conn.execute("UPDATE custom_islands SET name = ? WHERE name = ?", (new_name, old_name))
            conn.execute(
                "UPDATE penguin_records SET island = ? WHERE island = ?", (new_name, old_name)
            )
            conn.commit()

    def delete_custom_island(self, name: str):
        """Delete a custom island from the database."""
        with get_connection(self._database_path) as conn:
            conn.execute("DELETE FROM custom_islands WHERE name = ?", (name,))
            conn.commit()
