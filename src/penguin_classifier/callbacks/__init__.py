"""Callback modules."""

from dash import Dash
from ..service import PenguinService
from ..inference import ModelInferenceService
from ..metadata_service import MetadataService

from .metadata import register_metadata_callbacks
from .prediction import register_prediction_callbacks
from .saved_penguins import register_saved_penguins_callbacks
from .admin import register_admin_callbacks


def register_all_callbacks(app: Dash) -> None:
    """Register all frontend callbacks."""
    service = PenguinService()
    inference_service = ModelInferenceService()
    metadata_service = MetadataService()

    register_metadata_callbacks(app, metadata_service)
    register_prediction_callbacks(app, inference_service, metadata_service)
    register_saved_penguins_callbacks(app, service, inference_service)
    register_admin_callbacks(app, service)
