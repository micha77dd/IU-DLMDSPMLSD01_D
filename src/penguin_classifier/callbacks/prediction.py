"""Prediction callbacks."""

import logging
from dash import Dash, Input, Output, html
import plotly.graph_objects as go

from ..inference import ModelInferenceService
from ..metadata_service import MetadataService
from ..prediction import PredictionResult
from ..preprocessing import PredictionInput
from ..visualization import build_probability_figure

logger = logging.getLogger(__name__)


def build_prediction_summary(prediction: PredictionResult) -> list[html.Div]:
    """Build summary card content for the prediction panel."""
    return [
        html.Div(
            children=[
                html.Span("Vorhergesagte Art", className="summary-label"),
                html.Div(prediction.species, className="summary-species"),
            ]
        ),
        html.Div(
            children=[
                html.Span("Konfidenz", className="summary-label"),
                html.Div(f"{prediction.confidence:.0%}", className="summary-confidence"),
            ]
        ),
    ]


def get_previous_confidence(conf_val: str | float) -> float | None:
    """Parse previous confidence value."""
    if isinstance(conf_val, str) and conf_val.endswith("%"):
        try:
            return float(conf_val.strip("%")) / 100.0
        except ValueError:
            return None
    try:
        return float(conf_val)
    except ValueError:
        return None


def extract_previous_prediction(
    selected_rows: list[int] | None, table_data: list[dict] | None
) -> tuple[str | None, float | None]:
    """Extract previous prediction from table."""
    if selected_rows and table_data and len(selected_rows) > 0:
        row_index = selected_rows[0]
        if 0 <= row_index < len(table_data):
            old_record = table_data[row_index]
            conf = None
            if old_record.get("confidence"):
                conf = get_previous_confidence(old_record.get("confidence"))
            return old_record.get("prediction"), conf
    return None, None


def get_prediction_input(_args) -> PredictionInput:
    """Create prediction input from args."""
    return PredictionInput(
        island=_args[1],
        sex=_args[2],
        culmen_length_mm=_args[3],
        culmen_depth_mm=_args[4],
        flipper_length_mm=_args[5],
        body_mass_g=_args[6],
    )


def register_prediction_callbacks(
    app: Dash, inference_service: ModelInferenceService, metadata_service: MetadataService
) -> None:
    """Register prediction callbacks."""

    @app.callback(
        Output("prediction-summary", "children"),
        Output("probability-chart", "figure"),
        Output("save-prediction-button", "disabled"),
        Input("algorithm-tabs", "value"),
        Input("island-dropdown", "value"),
        Input("sex-dropdown", "value"),
        Input("culmen-length-slider", "value"),
        Input("culmen-depth-slider", "value"),
        Input("flipper-length-slider", "value"),
        Input("body-mass-slider", "value"),
        Input("saved-penguins-table", "selected_rows"),
        Input("saved-penguins-table", "data"),
        Input("admin-species-feedback", "children"),
        Input("last-training-time", "children"),
    )
    def update_prediction_ui(*_args):
        try:
            prediction_input = get_prediction_input(_args)
            logger.info("Starte Vorhersage mit Eingabedaten: %s", prediction_input)
            prediction = inference_service.predict(_args[0], prediction_input)
        except (ValueError, RuntimeError) as e:
            logger.error("Prediction failed: %s", e)
            return (
                [html.Div("Kein trainiertes Modell vorhanden.", style={"color": "red"})],
                go.Figure(),
                True,
            )

        prev_pred, prev_conf = extract_previous_prediction(_args[7], _args[8])
        all_species = metadata_service.get_all_species()

        summary_prediction = prediction
        if prev_pred is not None:
            summary_prediction = PredictionResult(
                species=prev_pred,
                confidence=prev_conf if prev_conf is not None else 1.0,
                probabilities=prediction.probabilities
            )

        return (
            build_prediction_summary(summary_prediction),
            build_probability_figure(prediction, all_species, prev_pred, prev_conf),
            False,
        )
