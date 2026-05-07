"""Callbacks module."""

from dash import Dash, Input, Output, State, callback_context, html
from ..metadata_service import MetadataService
from ..ui_options import as_dropdown_options


def handle_manage_islands(metadata_service, triggered_id, selected_island, new_name):
    """Logic to manage islands."""
    feedback = ""
    if triggered_id == "admin-island-add":
        if metadata_service.add_island(new_name):
            feedback = html.Span(f"Insel '{new_name}' hinzugefügt.", style={"color": "green"})
            selected_island, new_name = None, ""
        else:
            feedback = html.Span(
                "Fehler: Insel existiert bereits oder Name ist leer.", style={"color": "red"}
            )
    elif triggered_id == "admin-island-rename":
        if metadata_service.rename_island(selected_island, new_name):
            feedback = html.Span(f"Insel umbenannt in '{new_name}'.", style={"color": "green"})
            selected_island, new_name = None, ""
        else:
            feedback = html.Span(
                (
                    "Fehler: Standard-Inseln können nicht umbenannt werden, "
                    "oder Name existiert bereits."
                ),
                style={"color": "red"},
            )
    elif triggered_id == "admin-island-delete":
        if metadata_service.delete_island(selected_island):
            feedback = html.Span(f"Insel '{selected_island}' gelöscht.", style={"color": "green"})
            selected_island, new_name = None, ""
        else:
            feedback = html.Span(
                "Fehler: Standard-Inseln können nicht gelöscht werden.", style={"color": "red"}
            )
    return feedback, selected_island, new_name


def handle_manage_species(metadata_service, triggered_id, selected_species, new_name):
    """Logic to manage species."""
    feedback = ""
    if triggered_id == "admin-species-add":
        if metadata_service.add_species(new_name):
            feedback = html.Span(f"Art '{new_name}' hinzugefügt.", style={"color": "green"})
            selected_species, new_name = None, ""
        else:
            feedback = html.Span(
                "Fehler: Art existiert bereits oder Name ist leer.", style={"color": "red"}
            )
    elif triggered_id == "admin-species-rename":
        if metadata_service.rename_species(selected_species, new_name):
            feedback = html.Span(f"Art umbenannt in '{new_name}'.", style={"color": "green"})
            selected_species, new_name = None, ""
        else:
            feedback = html.Span(
                (
                    "Fehler: Standard-Arten können nicht umbenannt werden, "
                    "oder Name existiert bereits."
                ),
                style={"color": "red"},
            )
    elif triggered_id == "admin-species-delete":
        if metadata_service.delete_species(selected_species):
            feedback = html.Span(f"Art '{selected_species}' gelöscht.", style={"color": "green"})
            selected_species, new_name = None, ""
        else:
            feedback = html.Span(
                "Fehler: Standard-Arten können nicht gelöscht werden.", style={"color": "red"}
            )
    return feedback, selected_species, new_name


def register_metadata_callbacks(app: Dash, metadata_service: MetadataService) -> None:
    """Register metadata callbacks."""

    @app.callback(
        Output("island-dropdown", "options"),
        Output("admin-island-dropdown", "options"),
        Output("admin-island-feedback", "children"),
        Output("admin-island-dropdown", "value"),
        Output("admin-island-input", "value"),
        Input("admin-island-add", "n_clicks"),
        Input("admin-island-rename", "n_clicks"),
        Input("admin-island-delete", "n_clicks"),
        State("admin-island-dropdown", "value"),
        State("admin-island-input", "value"),
        prevent_initial_call=True,
    )
    def manage_islands(_add_clicks, _rename_clicks, _delete_clicks, selected_island, new_name):
        triggered_id = callback_context.triggered_id
        feedback, selected_island, new_name = handle_manage_islands(
            metadata_service, triggered_id, selected_island, new_name
        )

        all_opts = as_dropdown_options(metadata_service.get_all_islands())
        custom_opts = as_dropdown_options(metadata_service.get_custom_islands())
        return all_opts, custom_opts, feedback, selected_island, new_name

    @app.callback(
        Output("manual-species-dropdown", "options"),
        Output("admin-species-dropdown", "options"),
        Output("admin-species-feedback", "children"),
        Output("admin-species-dropdown", "value"),
        Output("admin-species-input", "value"),
        Input("admin-species-add", "n_clicks"),
        Input("admin-species-rename", "n_clicks"),
        Input("admin-species-delete", "n_clicks"),
        State("admin-species-dropdown", "value"),
        State("admin-species-input", "value"),
        prevent_initial_call=True,
    )
    def manage_species(_add_clicks, _rename_clicks, _delete_clicks, selected_species, new_name):
        triggered_id = callback_context.triggered_id
        feedback, selected_species, new_name = handle_manage_species(
            metadata_service, triggered_id, selected_species, new_name
        )

        all_opts = as_dropdown_options(metadata_service.get_all_species())
        custom_opts = as_dropdown_options(metadata_service.get_custom_species())
        return all_opts, custom_opts, feedback, selected_species, new_name
