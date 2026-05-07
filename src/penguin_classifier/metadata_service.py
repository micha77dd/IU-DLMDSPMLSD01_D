"""Service for metadata (species, islands)."""
from typing import List

from .config import AppConfig
from .metadata_repository import MetadataRepository


class MetadataService:
    """Service to handle operations related to species and islands metadata."""

    def __init__(self, database_path=None):
        """Initialize the MetadataService with a given database path."""
        self._repo = MetadataRepository(database_path)
        self._config = AppConfig()

    def get_all_species(self) -> List[str]:
        """Retrieve all species, combining configured and custom ones."""
        return list(self._config.species) + self._repo.list_custom_species()

    def get_all_islands(self) -> List[str]:
        """Retrieve all islands, combining configured and custom ones."""
        return list(self._config.islands) + self._repo.list_custom_islands()

    def get_custom_species(self) -> List[str]:
        """Retrieve only the custom species from the repository."""
        return self._repo.list_custom_species()

    def get_custom_islands(self) -> List[str]:
        """Retrieve only the custom islands from the repository."""
        return self._repo.list_custom_islands()

    def add_species(self, name: str) -> bool:
        """Add a new custom species if it does not already exist."""
        if not name or name in self.get_all_species():
            return False
        self._repo.add_custom_species(name)
        return True

    def rename_species(self, old_name: str, new_name: str) -> bool:
        """
        Rename an existing custom species.
        
        Returns True if successful, False if the old name is a configured species
        or the new name already exists.
        """
        if old_name in self._config.species or not new_name or new_name in self.get_all_species():
            return False
        self._repo.rename_custom_species(old_name, new_name)
        return True

    def delete_species(self, name: str) -> bool:
        """Delete a custom species."""
        if name in self._config.species:
            return False
        self._repo.delete_custom_species(name)
        return True

    def add_island(self, name: str) -> bool:
        """Add a new custom island if it does not already exist."""
        if not name or name in self.get_all_islands():
            return False
        self._repo.add_custom_island(name)
        return True

    def rename_island(self, old_name: str, new_name: str) -> bool:
        """Rename an existing custom island."""
        if old_name in self._config.islands or not new_name or new_name in self.get_all_islands():
            return False
        self._repo.rename_custom_island(old_name, new_name)
        return True

    def delete_island(self, name: str) -> bool:
        """Delete a custom island."""
        if name in self._config.islands:
            return False
        self._repo.delete_custom_island(name)
        return True
