# pylint: disable=too-many-arguments,too-many-positional-arguments,too-many-return-statements,line-too-long
"""Callbacks module."""

import logging
from dash import Dash, Input, Output, State, callback_context, no_update
from ..config import AppConfig
from ..inference import ModelInferenceService
from ..layout import DELETE_COLUMN_STYLE
from ..preprocessing import PredictionInput
from ..service import PenguinService
from ..visualization import build_saved_penguins_scatter

logger = logging.getLogger(__name__)


def get_current_record(selected_rows, table_data, derived_virtual_data):
    """Get the currently selected record."""
    if not selected_rows or not table_data or len(selected_rows) == 0:
        return None
    row_index = selected_rows[0]
    current_data = derived_virtual_data if derived_virtual_data is not None else table_data
    if current_data and 0 <= row_index < len(current_data):
        return current_data[row_index]
    return None


def handle_scatter_axes(service, scatter_x, scatter_y):
    """Handle scatter plot axes change."""
    rows = service.list_saved_penguins()
    return (
        no_update,
        build_saved_penguins_scatter(rows, scatter_x, scatter_y),
        no_update,
        no_update,
        no_update,
    )


def handle_save_prediction(
    service, inference_service, algorithm, pred_input, scatter_x, scatter_y, old_record
):
    """Handle normal save prediction."""
    if old_record:
        msg = f"Möchten Sie die bestehende Klassifikation {old_record['prediction']} ({old_record['algorithm']}) überschreiben? [Ja/Abbrechen]"
        return no_update, no_update, True, msg, no_update

    try:
        prediction = inference_service.predict(algorithm, pred_input)
    except (ValueError, RuntimeError) as e:
        logger.error("Prediction failed on save: %s", e)
        return no_update, no_update, no_update, no_update, no_update

    service.save_classification(
        algorithm=algorithm,
        prediction=prediction.species,
        confidence=prediction.confidence,
        features=pred_input,
    )
    rows = service.list_saved_penguins()
    return rows, build_saved_penguins_scatter(rows, scatter_x, scatter_y), no_update, no_update, [0]


def handle_save_manual(
    service, manual_species, pred_input, scatter_x, scatter_y, old_record, selected_rows
):
    """Handle saving a manual classification."""
    if old_record:
        service.update_classification(
            record_id=int(old_record["id"]),
            algorithm="Manuell",
            prediction=manual_species,
            confidence=1.0,
            features=pred_input,
        )
        rows = service.list_saved_penguins()
        return (
            rows,
            build_saved_penguins_scatter(rows, scatter_x, scatter_y),
            no_update,
            no_update,
            selected_rows,
        )

    service.save_classification(
        algorithm="Manuell",
        prediction=manual_species,
        confidence=1.0,
        features=pred_input,
    )
    rows = service.list_saved_penguins()
    return (
        rows,
        build_saved_penguins_scatter(rows, scatter_x, scatter_y),
        no_update,
        no_update,
        [0],
    )


def handle_overwrite_confirm(
    service,
    inference_service,
    algorithm,
    pred_input,
    scatter_x,
    scatter_y,
    old_record,
    selected_rows,
):
    """Handle confirmation of overwrite."""
    if not old_record:
        return no_update, no_update, no_update, no_update, no_update

    try:
        prediction = inference_service.predict(algorithm, pred_input)
    except (ValueError, RuntimeError) as e:
        logger.error("Prediction failed on update: %s", e)
        return no_update, no_update, no_update, no_update, no_update

    service.update_classification(
        record_id=int(old_record["id"]),
        algorithm=algorithm,
        prediction=prediction.species,
        confidence=prediction.confidence,
        features=pred_input,
    )
    rows = service.list_saved_penguins()
    return (
        rows,
        build_saved_penguins_scatter(rows, scatter_x, scatter_y),
        no_update,
        no_update,
        selected_rows,
    )


def handle_delete_row(service, active_cell, table_data, derived_virtual_data, scatter_x, scatter_y):
    """Handle deletion of a row."""
    if not active_cell or active_cell.get("column_id") != "delete":
        return no_update, no_update, no_update, no_update, no_update

    record_id = active_cell.get("row_id")
    if record_id is None:
        row_index = active_cell.get("row")
        current_data = derived_virtual_data if derived_virtual_data is not None else table_data
        if current_data is None or row_index is None or not 0 <= row_index < len(current_data):
            return no_update, no_update, no_update, no_update, no_update
        record_id = current_data[row_index].get("id")

    if record_id is None:
        return no_update, no_update, no_update, no_update, no_update

    service.delete_saved_penguin(int(record_id))
    rows = service.list_saved_penguins()
    return rows, build_saved_penguins_scatter(rows, scatter_x, scatter_y), no_update, no_update, []


def process_table_action(triggered_id, **kwargs):
    """Route table action to appropriate handler."""
    service = kwargs["service"]
    scatter_x = kwargs["scatter_x"]
    scatter_y = kwargs["scatter_y"]

    if triggered_id in ("scatter-x-axis", "scatter-y-axis"):
        return handle_scatter_axes(service, scatter_x, scatter_y)

    if triggered_id == "saved-penguins-table":
        return handle_delete_row(
            service,
            kwargs["active_cell"],
            kwargs["table_data"],
            kwargs["derived_virtual_data"],
            scatter_x,
            scatter_y,
        )

    try:
        pred_input = PredictionInput(
            island=kwargs["island"],
            sex=kwargs["sex"],
            culmen_length_mm=kwargs["culmen_length_mm"],
            culmen_depth_mm=kwargs["culmen_depth_mm"],
            flipper_length_mm=kwargs["flipper_length_mm"],
            body_mass_g=kwargs["body_mass_g"],
        )
    except ValueError as e:
        logger.error("Invalid input: %s", e)
        return no_update, no_update, no_update, no_update, no_update

    old_record = get_current_record(
        kwargs["selected_rows"], kwargs["table_data"], kwargs["derived_virtual_data"]
    )

    if triggered_id == "save-prediction-button":
        return handle_save_prediction(
            service,
            kwargs["inference_service"],
            kwargs["algorithm"],
            pred_input,
            scatter_x,
            scatter_y,
            old_record,
        )

    if triggered_id == "save-manual-classification":
        return handle_save_manual(
            service,
            kwargs["manual_species"],
            pred_input,
            scatter_x,
            scatter_y,
            old_record,
            kwargs["selected_rows"],
        )

    if triggered_id == "overwrite-confirm-dialog":
        return handle_overwrite_confirm(
            service,
            kwargs["inference_service"],
            kwargs["algorithm"],
            pred_input,
            scatter_x,
            scatter_y,
            old_record,
            kwargs["selected_rows"],
        )

    return no_update, no_update, no_update, no_update, no_update


def handle_reset_or_empty(base_style):
    """Handle resetting inputs."""
    app_config = AppConfig()
    return (
        app_config.islands[0],
        app_config.sexes[0],
        app_config.slider_defaults["culmen_length_mm"],
        app_config.slider_defaults["culmen_depth_mm"],
        app_config.slider_defaults["flipper_length_mm"],
        app_config.slider_defaults["body_mass_g"],
        False,
        False,
        False,
        False,
        False,
        False,
        [],
        None,
        base_style,
    )


def handle_row_selection(row_data, selected_rows, clear_active_cell, base_style, row_id_val):
    """Handle a selected row."""
    if not row_data:
        return (no_update,) * 15

    active_style = base_style.copy()
    active_style.append(
        {
            "if": {"filter_query": f"{{id}} = {row_id_val}"},
            "backgroundColor": "#dbeafe",
            "borderTop": "1px solid #2563eb",
            "borderBottom": "1px solid #2563eb",
        }
    )

    return (
        row_data["island"],
        row_data["sex"],
        float(row_data["culmen_length_mm"]),
        float(row_data["culmen_depth_mm"]),
        float(row_data["flipper_length_mm"]),
        float(row_data["body_mass_g"]),
        True,
        True,
        True,
        True,
        True,
        True,
        selected_rows,
        None if clear_active_cell else no_update,
        active_style,
    )


def register_saved_penguins_callbacks(
    app: Dash, service: PenguinService, inference_service: ModelInferenceService
) -> None:
    """Register saved penguins callbacks."""

    @app.callback(
        Output("saved-penguins-table", "data"),
        Output("comparison-scatter", "figure"),
        Output("overwrite-confirm-dialog", "displayed"),
        Output("overwrite-confirm-dialog", "message"),
        Output("saved-penguins-table", "selected_rows", allow_duplicate=True),
        Input("save-prediction-button", "n_clicks"),
        Input("saved-penguins-table", "active_cell"),
        Input("overwrite-confirm-dialog", "submit_n_clicks"),
        Input("scatter-x-axis", "value"),
        Input("scatter-y-axis", "value"),
        Input("save-manual-classification", "n_clicks"),
        State("saved-penguins-table", "selected_rows"),
        State("saved-penguins-table", "data"),
        State("saved-penguins-table", "derived_virtual_data"),
        State("algorithm-tabs", "value"),
        State("island-dropdown", "value"),
        State("sex-dropdown", "value"),
        State("culmen-length-slider", "value"),
        State("culmen-depth-slider", "value"),
        State("flipper-length-slider", "value"),
        State("body-mass-slider", "value"),
        State("manual-species-dropdown", "value"),
        prevent_initial_call=True,
    )
    def manage_saved_penguins(*_args):
        return process_table_action(
            callback_context.triggered_id,
            service=service,
            inference_service=inference_service,
            active_cell=_args[1],
            scatter_x=_args[3],
            scatter_y=_args[4],
            selected_rows=_args[6],
            table_data=_args[7],
            derived_virtual_data=_args[8],
            algorithm=_args[9],
            island=_args[10],
            sex=_args[11],
            culmen_length_mm=_args[12],
            culmen_depth_mm=_args[13],
            flipper_length_mm=_args[14],
            body_mass_g=_args[15],
            manual_species=_args[16],
        )

    @app.callback(
        Output("island-dropdown", "value"),
        Output("sex-dropdown", "value"),
        Output("culmen-length-slider", "value"),
        Output("culmen-depth-slider", "value"),
        Output("flipper-length-slider", "value"),
        Output("body-mass-slider", "value"),
        Output("island-dropdown", "disabled"),
        Output("sex-dropdown", "disabled"),
        Output("culmen-length-slider", "disabled"),
        Output("culmen-depth-slider", "disabled"),
        Output("flipper-length-slider", "disabled"),
        Output("body-mass-slider", "disabled"),
        Output("saved-penguins-table", "selected_rows"),
        Output("saved-penguins-table", "active_cell"),
        Output("saved-penguins-table", "style_data_conditional"),
        Input("reset-button", "n_clicks"),
        Input("saved-penguins-table", "selected_rows"),
        Input("saved-penguins-table", "active_cell"),
        State("saved-penguins-table", "data"),
        State("saved-penguins-table", "derived_virtual_data"),
        prevent_initial_call=True,
    )
    def update_inputs_from_selection_or_reset(*_args):
        selected_rows, active_cell = _args[1], _args[2]
        table_data, derived_virtual_data = _args[3], _args[4]
        triggered_id = callback_context.triggered_id
        triggered_prop = (
            callback_context.triggered[0]["prop_id"] if callback_context.triggered else ""
        )

        base_style = [DELETE_COLUMN_STYLE]
        clear_active_cell = False

        if triggered_prop == "saved-penguins-table.active_cell" and active_cell:
            if active_cell.get("column_id") != "delete":
                selected_rows = [active_cell["row"]]
                clear_active_cell = True
            else:
                return (no_update,) * 15

        if triggered_id == "reset-button" or not selected_rows or len(selected_rows) == 0:
            return handle_reset_or_empty(base_style)

        row_index = selected_rows[0]
        current_data = derived_virtual_data if derived_virtual_data is not None else table_data
        
        row_data = None
        row_id_val = None
        if current_data and 0 <= row_index < len(current_data):
            row_data = current_data[row_index]
            row_id_val = row_data.get("id")

        return handle_row_selection(
            row_data, selected_rows, clear_active_cell, base_style, row_id_val
        )

    @app.callback(
        Output("saved-penguins-table", "page_size"),
        Input("saved-penguins-page-size", "value"),
    )
    def update_page_size(page_size: int) -> int:
        return page_size
