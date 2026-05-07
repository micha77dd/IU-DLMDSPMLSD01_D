"""Admin callbacks."""

from dash import Dash, Input, Output, State, callback_context
from ..service import PenguinService
from ..visualization import build_saved_penguins_scatter


def register_admin_callbacks(app: Dash, service: PenguinService) -> None:
    """Register admin callbacks."""

    @app.callback(
        Output("manual-classification-modal", "style"),
        Input("manual-classification-button", "n_clicks"),
        Input("cancel-manual-classification", "n_clicks"),
        Input("save-manual-classification", "n_clicks"),
        prevent_initial_call=True,
    )
    def toggle_manual_modal(*_args):
        triggered_id = callback_context.triggered_id
        if triggered_id == "manual-classification-button":
            return {
                "display": "block",
                "position": "fixed",
                "zIndex": 1000,
                "left": 0,
                "top": 0,
                "width": "100%",
                "height": "100%",
                "backgroundColor": "rgba(0,0,0,0.4)",
            }
        return {
            "display": "none",
            "position": "fixed",
            "zIndex": 1000,
            "left": 0,
            "top": 0,
            "width": "100%",
            "height": "100%",
            "backgroundColor": "rgba(0,0,0,0.4)",
        }

    @app.callback(
        Output("delete-models-confirm-dialog", "displayed"),
        Input("delete-models-button", "n_clicks"),
        prevent_initial_call=True,
    )
    def show_delete_models_dialog(_n_clicks: int) -> bool:
        return True

    @app.callback(
        Output("last-training-time", "children"),
        Input("delete-models-confirm-dialog", "submit_n_clicks"),
        prevent_initial_call=True,
    )
    def delete_models_action(_submit_clicks: int) -> str:
        # pylint: disable=import-outside-toplevel
        from ..training import delete_all_models
        from ..layout import get_last_training_time

        delete_all_models()
        return f"Letztes Training: {get_last_training_time()}"

    @app.callback(
        Output("delete-database-confirm-dialog", "displayed"),
        Input("delete-database-button", "n_clicks"),
        prevent_initial_call=True,
    )
    def show_delete_database_dialog(_n_clicks: int) -> bool:
        return True

    @app.callback(
        Output("saved-penguins-table", "data", allow_duplicate=True),
        Output("comparison-scatter", "figure", allow_duplicate=True),
        Input("delete-database-confirm-dialog", "submit_n_clicks"),
        State("scatter-x-axis", "value"),
        State("scatter-y-axis", "value"),
        prevent_initial_call=True,
    )
    def delete_database_action(_submit_clicks: int, scatter_x: str, scatter_y: str) -> tuple:
        service.delete_all_saved_penguins()
        rows = service.list_saved_penguins()
        return rows, build_saved_penguins_scatter(rows, scatter_x, scatter_y)

    @app.callback(
        Output("saved-penguins-table", "data", allow_duplicate=True),
        Output("comparison-scatter", "figure", allow_duplicate=True),
        Input("insert-demo-data-button", "n_clicks"),
        State("scatter-x-axis", "value"),
        State("scatter-y-axis", "value"),
        prevent_initial_call=True,
    )
    def insert_demo_data_action(_n_clicks: int, scatter_x: str, scatter_y: str) -> tuple:
        service.insert_demo_data()
        rows = service.list_saved_penguins()
        return rows, build_saved_penguins_scatter(rows, scatter_x, scatter_y)
