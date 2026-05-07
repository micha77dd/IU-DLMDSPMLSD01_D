# pylint: disable=line-too-long
"""Dash layout definitions."""

import os
from datetime import datetime
from pathlib import Path
from typing import Any

from dash import dash_table, dcc, html

from .config import AppConfig
from .metadata_service import MetadataService
from .prediction import get_placeholder_prediction
from .service import PenguinService
from .ui_options import as_dropdown_options
from .visualization import build_probability_figure, build_saved_penguins_scatter

SCATTER_OPTIONS = [
    {"label": "Insel", "value": "island"},
    {"label": "Geschlecht", "value": "sex"},
    {"label": "Culmen Length", "value": "culmen_length_mm"},
    {"label": "Culmen Depth", "value": "culmen_depth_mm"},
    {"label": "Flipper Length", "value": "flipper_length_mm"},
    {"label": "Body Mass", "value": "body_mass_g"},
]
DELETE_COLUMN_STYLE = {
    "if": {"column_id": "delete"},
    "textAlign": "center",
    "fontSize": "1.1rem",
    "cursor": "pointer",
    "width": "60px",
    "minWidth": "60px",
    "maxWidth": "60px",
}


def get_last_training_time() -> str:
    """Return the formatted modification time of the random forest model, or 'Noch nie'."""
    model_path = Path(__file__).resolve().parent.parent / "data" / "models" / "random_forest.pkl"
    if model_path.exists():
        mtime = os.path.getmtime(model_path)
        return datetime.fromtimestamp(mtime).strftime("%d.%m.%Y %H:%M:%S")
    return "Noch nie"


# pylint: disable=too-many-arguments, too-many-positional-arguments
def _slider_field(
        label: str,
        component_id: str,
        bounds: tuple[float, float, float],
        value: float,
        value_suffix: str,
) -> html.Div:
    return html.Div(
        className="field-group",
        children=[
            html.Div(
                className="field-label-row",
                children=[
                    html.Label(label, className="field-label", htmlFor=component_id),
                    html.Span(f" {value_suffix}", className="slider-value"),
                ],
            ),
            dcc.Slider(
                id=component_id,
                min=bounds[0],
                max=bounds[1],
                step=bounds[2],
                value=value,
                tooltip={"placement": "bottom", "always_visible": False},
            ),
        ],
    )


def _build_app_header(config: AppConfig) -> html.Div:
    return html.Div(
        className="app-header",
        children=[
            html.H1(config.title, className="app-title"),
            html.P(
                "Frontend-Prototyp für die interaktive Pinguinklassifikation.",
                className="app-subtitle",
            ),
        ],
    )


def _build_input_panel(config: AppConfig, metadata_service: MetadataService) -> html.Section:
    return html.Section(
        id="input-panel",
        className="panel",
        children=[
            html.H2("Eingabedaten", className="panel-title"),
            html.Div(
                className="form-grid",
                children=[
                    html.Div(
                        className="field-group",
                        children=[
                            html.Label("Insel", className="field-label", htmlFor="island-dropdown"),
                            dcc.Dropdown(
                                id="island-dropdown",
                                options=as_dropdown_options(metadata_service.get_all_islands()),
                                value=config.islands[0],
                                clearable=False,
                                placeholder="Insel auswählen",
                            ),
                        ],
                    ),
                    html.Div(
                        className="field-group",
                        children=[
                            html.Label("Geschlecht", className="field-label", htmlFor="sex-dropdown"),
                            dcc.Dropdown(
                                id="sex-dropdown",
                                options=as_dropdown_options(config.sexes),
                                value=config.sexes[0],
                                clearable=False,
                                placeholder="Geschlecht auswählen",
                            ),
                        ],
                    ),
                    _slider_field(
                        label="Culmen Length",
                        component_id="culmen-length-slider",
                        bounds=(30, 65, 1),
                        value=config.slider_defaults["culmen_length_mm"],
                        value_suffix="mm",
                    ),
                    _slider_field(
                        label="Culmen Depth",
                        component_id="culmen-depth-slider",
                        bounds=(13, 22, 0.5),
                        value=config.slider_defaults["culmen_depth_mm"],
                        value_suffix="mm",
                    ),
                    _slider_field(
                        label="Flipper Length",
                        component_id="flipper-length-slider",
                        bounds=(170, 235, 1),
                        value=config.slider_defaults["flipper_length_mm"],
                        value_suffix="mm",
                    ),
                    _slider_field(
                        label="Body Mass",
                        component_id="body-mass-slider",
                        bounds=(2500, 6500, 50),
                        value=config.slider_defaults["body_mass_g"],
                        value_suffix="g",
                    ),
                    html.Div(
                        className="action-row",
                        children=[
                            html.Button(
                                "Eingabe zurücksetzen",
                                id="reset-button",
                                n_clicks=0,
                                className="action-button reset-button",
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )


def _build_model_management() -> html.Div:
    return html.Div([
        html.H3("Modell-Verwaltung", className="panel-title", style={"marginTop": "0", "fontSize": "1.2rem"}),
        html.P(f"Letztes Training: {get_last_training_time()}", id="last-training-time"),
        html.Button(
            "Modelle neu trainieren", id="retrain-button", n_clicks=0,
            className="action-button primary-button", style={"marginTop": "1em", "marginRight": "10px"},
        ),
        html.Button(
            "Modelle löschen", id="delete-models-button", n_clicks=0,
            className="action-button secondary-button",
            style={"marginTop": "1em", "backgroundColor": "#dc3545", "color": "white", "borderColor": "#dc3545"},
        ),
        dcc.ConfirmDialog(id="delete-models-confirm-dialog", message="Modelle löschen? System wird zurückgesetzt."),
        html.Div(
            id="retrain-feedback", style={"marginTop": "10px", "textAlign": "left", "fontSize": "0.9rem"},
            children=[
                html.Div(id="ws-status-rf", children="Random Forest: -"),
                html.Div(id="ws-status-svm", children="SVM: -"),
                html.Div(id="ws-status-lr", children="Logistic Regression: -"),
            ],
        ),
    ])


def _build_database_management() -> html.Div:
    return html.Div([
        html.Hr(),
        html.H3("Datenbank-Verwaltung", className="panel-title", style={"marginTop": "10px", "fontSize": "1.2rem"}),
        html.Div(
            style={"display": "flex", "gap": "10px", "marginTop": "1em"},
            children=[
                html.Button("Demo-Daten einfügen", id="insert-demo-data-button", n_clicks=0,
                            className="action-button primary-button"),
                html.Button(
                    "Alle gespeicherten Daten löschen", id="delete-database-button", n_clicks=0,
                    className="action-button secondary-button",
                    style={"backgroundColor": "#dc3545", "color": "white", "borderColor": "#dc3545"},
                ),
            ],
        ),
        dcc.ConfirmDialog(id="delete-database-confirm-dialog",
                          message="Sind Sie sicher, dass Sie alle gespeicherten Daten löschen möchten?"),
    ])


def _build_species_management(metadata_service: MetadataService) -> html.Div:
    return html.Div([
        html.Hr(),
        html.H3("Pinguin-Arten verwalten", className="panel-title", style={"marginTop": "10px", "fontSize": "1.2rem"}),
        dcc.Dropdown(
            id="admin-species-dropdown",
            options=as_dropdown_options(metadata_service.get_custom_species()),
            placeholder="Art auswählen...",
        ),
        dcc.Input(id="admin-species-input", type="text", placeholder="Neue Art oder Umbenennung",
                  style={"marginTop": "10px", "width": "100%"}),
        html.Div(
            style={"marginTop": "10px", "display": "flex", "gap": "10px"},
            children=[
                html.Button("Hinzufügen", id="admin-species-add", className="action-button primary-button"),
                html.Button("Umbenennen", id="admin-species-rename", className="action-button secondary-button"),
                html.Button("Löschen", id="admin-species-delete", className="action-button secondary-button",
                            style={"backgroundColor": "#ef4444", "color": "white"}),
            ],
        ),
        html.Div(id="admin-species-feedback", style={"marginTop": "5px"}),
    ])


def _build_island_management(metadata_service: MetadataService) -> html.Div:
    return html.Div([
        html.H3("Inseln verwalten", className="panel-title", style={"marginTop": "20px", "fontSize": "1.2rem"}),
        dcc.Dropdown(
            id="admin-island-dropdown",
            options=as_dropdown_options(metadata_service.get_custom_islands()),
            placeholder="Insel auswählen...",
        ),
        dcc.Input(id="admin-island-input", type="text", placeholder="Neue Insel oder Umbenennung",
                  style={"marginTop": "10px", "width": "100%"}),
        html.Div(
            style={"marginTop": "10px", "display": "flex", "gap": "10px"},
            children=[
                html.Button("Hinzufügen", id="admin-island-add", className="action-button primary-button"),
                html.Button("Umbenennen", id="admin-island-rename", className="action-button secondary-button"),
                html.Button("Löschen", id="admin-island-delete", className="action-button secondary-button",
                            style={"backgroundColor": "#ef4444", "color": "white"}),
            ],
        ),
        html.Div(id="admin-island-feedback", style={"marginTop": "5px"}),
    ])


def _build_admin_panel(metadata_service: MetadataService) -> html.Section:
    return html.Section(
        id="admin-panel",
        className="panel",
        children=[
            html.H2("Administration", className="panel-title"),
            html.Div(
                style={"marginTop": "20px"},
                children=[
                    _build_model_management(),
                    _build_database_management(),
                    _build_species_management(metadata_service),
                    _build_island_management(metadata_service),
                ],
            ),
        ],
    )


def _build_prediction_summary(prediction: Any) -> html.Div:
    return html.Div(
        id="prediction-summary",
        className="summary-card",
        children=[
            html.Div([
                html.Span("Vorhergesagte Art", className="summary-label"),
                html.Div(prediction.species, className="summary-species"),
            ]),
            html.Div([
                html.Span("Konfidenz", className="summary-label"),
                html.Div(f"{prediction.confidence:.0%}", className="summary-confidence"),
            ]),
        ],
    )


def _build_manual_classification_modal(config: AppConfig, metadata_service: MetadataService) -> html.Div:
    return html.Div(
        id="manual-classification-modal",
        style={
            "display": "none", "position": "fixed", "zIndex": 1000,
            "left": 0, "top": 0, "width": "100%", "height": "100%", "backgroundColor": "rgba(0,0,0,0.4)",
        },
        children=[
            html.Div(
                style={
                    "backgroundColor": "#fefefe", "margin": "15% auto", "padding": "20px",
                    "border": "1px solid #888", "width": "300px", "borderRadius": "8px",
                },
                children=[
                    html.H3("Eigene Klassifikation", style={"marginTop": "0"}),
                    dcc.Dropdown(
                        id="manual-species-dropdown",
                        options=as_dropdown_options(metadata_service.get_all_species()),
                        value=config.species[0],
                        clearable=False,
                    ),
                    html.Div(
                        style={"marginTop": "20px", "display": "flex", "justifyContent": "flex-end", "gap": "10px"},
                        children=[
                            html.Button("Abbrechen", id="cancel-manual-classification", n_clicks=0,
                                        className="action-button secondary-btn"),
                            html.Button("Speichern", id="save-manual-classification", n_clicks=0,
                                        className="action-button primary-button"),
                        ],
                    ),
                ],
            )
        ],
    )


def _build_prediction_panel(config: AppConfig, prediction: Any, metadata_service: MetadataService) -> html.Section:
    return html.Section(
        id="prediction-panel",
        className="panel",
        children=[
            html.H2("Ergebnis", className="panel-title"),
            dcc.Tabs(
                id="algorithm-tabs", value=config.algorithms[0],
                children=[dcc.Tab(label=algo, value=algo) for algo in config.algorithms],
                className="custom-tabs",
            ),
            _build_prediction_summary(prediction),
            dcc.Graph(
                id="probability-chart",
                figure=build_probability_figure(prediction, metadata_service.get_all_species()),
            ),
            html.Div(
                className="action-row", style={"marginTop": "20px"},
                children=[
                    html.Button("Diese Klassifikation speichern", id="save-prediction-button", n_clicks=0,
                                className="action-button primary-button"),
                    dcc.ConfirmDialog(id="overwrite-confirm-dialog", message=""),
                ],
            ),
            html.Div(
                className="action-row", style={"marginTop": "10px"},
                children=[
                    html.Button("Eigene Klassifikation vornehmen", id="manual-classification-button", n_clicks=0,
                                className="action-button secondary-button")
                ],
            ),
            _build_manual_classification_modal(config, metadata_service),
        ],
    )


def _build_saved_penguins_table(saved_penguins: list[dict[str, Any]]) -> html.Div:
    return html.Div([
        html.Div(
            className="table-toolbar", style={"marginTop": "20px"},
            children=[
                html.Div(
                    className="table-page-size",
                    children=[
                        html.Label("Einträge pro Seite", className="field-label", htmlFor="saved-penguins-page-size"),
                        dcc.Dropdown(
                            id="saved-penguins-page-size",
                            options=[{"label": str(v), "value": v} for v in [10, 20, 50, 100]],
                            value=20, clearable=False,
                        ),
                    ],
                ),
            ],
        ),
        dash_table.DataTable(
            id="saved-penguins-table",
            row_selectable="single", selected_rows=[],
            columns=[
                {"name": "Zeitpunkt", "id": "timestamp"},
                {"name": "Algorithmus", "id": "algorithm"},
                {"name": "Vorhersage", "id": "prediction"},
                {"name": "Konfidenz", "id": "confidence"},
                {"name": "Insel", "id": "island"},
                {"name": "Geschlecht", "id": "sex"},
                {"name": "Culmen Length", "id": "culmen_length_mm"},
                {"name": "Culmen Depth", "id": "culmen_depth_mm"},
                {"name": "Flipper Length", "id": "flipper_length_mm"},
                {"name": "Body Mass", "id": "body_mass_g"},
                {"name": "", "id": "delete"},
            ],
            data=saved_penguins,
            sort_action="native", filter_action="native", page_action="native",
            page_current=0, page_size=20,
            css=[{
                "selector": "td.cell--selected, td.focused",
                "rule": "background-color: #dbeafe !important; border-top: 1px solid #2563eb !important; border-bottom: 1px solid #2563eb !important; outline: none !important; box-shadow: none !important;",
            }],
            style_table={"overflowX": "auto"},
            style_cell={"textAlign": "left", "padding": "4px 10px", "height": "auto", "minWidth": "110px",
                        "maxWidth": "220px", "whiteSpace": "normal"},
            style_header={"fontWeight": "700", "backgroundColor": "#eef4fb"},
            style_data_conditional=[DELETE_COLUMN_STYLE],
        ),
    ])


def _build_comparison_scatter(saved_penguins: list[dict[str, Any]]) -> html.Div:
    return html.Div([
        html.Div(
            style={"marginTop": "20px", "display": "flex", "gap": "20px", "marginBottom": "10px"},
            children=[
                html.Div([
                    html.Label("X-Achse:", style={"fontWeight": "bold", "marginRight": "10px"}),
                    dcc.Dropdown(id="scatter-x-axis", options=SCATTER_OPTIONS, value="culmen_length_mm",
                                 clearable=False, style={"width": "200px"}),
                ], style={"display": "flex", "alignItems": "center"}),
                html.Div([
                    html.Label("Y-Achse:", style={"fontWeight": "bold", "marginRight": "10px"}),
                    dcc.Dropdown(id="scatter-y-axis", options=SCATTER_OPTIONS, value="culmen_depth_mm", clearable=False,
                                 style={"width": "200px"}),
                ], style={"display": "flex", "alignItems": "center"}),
            ],
        ),
        html.Div([
            dcc.Graph(id="comparison-scatter", figure=build_saved_penguins_scatter(saved_penguins)),
        ]),
    ])


def _build_data_visualization_panel(saved_penguins: list[dict[str, Any]]) -> html.Section:
    return html.Section(
        id="data-visualization-panel",
        className="panel",
        children=[
            html.H2("Historie und Visualisierung", className="panel-title"),
            dcc.Tabs(
                id="data-view-tabs", value="tab-table", className="custom-tabs",
                children=[
                    dcc.Tab(label="Gespeicherte Datensätze", value="tab-table",
                            children=[_build_saved_penguins_table(saved_penguins)]),
                    dcc.Tab(label="Visualisierung", value="tab-plot",
                            children=[_build_comparison_scatter(saved_penguins)]),
                ],
            ),
        ],
    )


def create_layout(config: AppConfig) -> html.Div:
    """Build the application layout."""
    metadata_service = MetadataService()
    prediction = get_placeholder_prediction()
    penguin_service = PenguinService()
    saved_penguins = penguin_service.list_saved_penguins()

    return html.Div(
        className="app-shell",
        children=[
            _build_app_header(config),
            html.Div(
                className="desktop-grid",
                children=[
                    html.Div(
                        className="left-column",
                        style={"display": "flex", "flexDirection": "column", "gap": "var(--grid-gap, 20px)"},
                        children=[
                            _build_input_panel(config, metadata_service),
                            _build_admin_panel(metadata_service),
                        ],
                    ),
                    html.Div(
                        className="content-grid",
                        children=[
                            _build_prediction_panel(config, prediction, metadata_service),
                            _build_data_visualization_panel(saved_penguins),
                        ],
                    ),
                ],
            ),
        ],
    )
