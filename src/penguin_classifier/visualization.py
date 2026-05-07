"""Plot factory functions for the frontend."""

import hashlib
from typing import Any

import plotly.graph_objects as go

from .prediction import PredictionResult

SPECIES_COLORS = {
    "Adelie": "#1f77b4",
    "Chinstrap": "#ff7f0e",
    "Gentoo": "#2ca02c",
    "": "#9aa5b1",
}


def get_color_for_species(species: str) -> str:
    """Determine the color associated with a species."""
    if species in SPECIES_COLORS:
        return SPECIES_COLORS[species]
    # deterministic random color
    h = hashlib.md5(species.encode()).hexdigest()
    return f"#{h[:6]}"


def build_probability_figure(
        prediction: PredictionResult,
        all_species: list[str],
        previous_prediction: str | None = None,
        previous_confidence: float | None = None
) -> go.Figure:
    """Create a bar chart for class probabilities."""

    species = all_species
    new_probs = [prediction.probabilities.get(s, 0.0) for s in species]
    colors = [get_color_for_species(s) for s in species]

    figure = go.Figure()

    # Immer die ungespeicherte Vorhersage schraffiert darstellen
    figure.add_trace(
        go.Bar(
            name="Modellvorhersage" if not previous_prediction else "Neue Vorhersage",
            x=species,
            y=new_probs,
            marker_color=colors,
            opacity=0.5,
            marker_pattern_shape="/",
            width=0.6,
            offset=-0.4,
        )
    )

    if previous_prediction and previous_confidence is not None:
        # Show saved prediction
        saved_probs = [previous_confidence if s == previous_prediction else 0.0 for s in species]
        figure.add_trace(
            go.Bar(
                name="Gespeicherte Klassifikation",
                x=species,
                y=saved_probs,
                marker_color=colors,
                opacity=1.0,
                width=0.6,
                offset=-0.2,
            )
        )

    figure.update_layout(
        barmode="overlay",
        title="Vorhersagewahrscheinlichkeiten",
        xaxis_title="Pinguinart",
        yaxis_title="Wahrscheinlichkeit",
        yaxis_range=[0, 1],
        template="plotly_white",
    )

    return figure


def build_saved_penguins_scatter(
        saved_penguins: list[dict[str, Any]],
        x_col: str = "culmen_length_mm",
        y_col: str = "culmen_depth_mm",
) -> go.Figure:
    """Create a scatter plot from persisted penguin records."""

    labels = {
        "island": "Insel",
        "sex": "Geschlecht",
        "culmen_length_mm": "Culmen Length (mm)",
        "culmen_depth_mm": "Culmen Depth (mm)",
        "flipper_length_mm": "Flipper Length (mm)",
        "body_mass_g": "Body Mass (g)"
    }

    x_title = labels.get(x_col, x_col)
    y_title = labels.get(y_col, y_col)

    figure = go.Figure()

    if not saved_penguins:
        figure.update_layout(
            title="Datensatz-Vergleich",
            xaxis_title=x_title,
            yaxis_title=y_title,
            template="plotly_white",
            annotations=[
                {
                    "text": "Noch keine gespeicherten Datensätze vorhanden.",
                    "xref": "paper",
                    "yref": "paper",
                    "x": 0.5,
                    "y": 0.5,
                    "showarrow": False,
                    "font": {"size": 14},
                }
            ],
        )
        return figure

    grouped: dict[str, list[dict[str, Any]]] = {}
    for row in saved_penguins:
        prediction = row.get("prediction", "") or ""
        grouped.setdefault(prediction, []).append(row)

    for prediction, rows in grouped.items():
        label = prediction if prediction else "Nicht klassifiziert"
        figure.add_scatter(
            x=[row[x_col] for row in rows],
            y=[row[y_col] for row in rows],
            mode="markers",
            marker={
                "size": 12,
                "color": get_color_for_species(prediction),
                "line": {"width": 1, "color": "#ffffff"},
            },
            name=label,
            customdata=[
                [
                    row["timestamp"],
                    row["algorithm"],
                    row["prediction"] or "Noch offen",
                    row["confidence"] or "",
                    row["island"],
                    row["sex"],
                    row["culmen_length_mm"],
                    row["culmen_depth_mm"],
                    row["flipper_length_mm"],
                    row["body_mass_g"],
                    row[x_col],
                    row[y_col]
                ]
                for row in rows
            ],
            hovertemplate=(
                "<b>%{customdata[2]}</b><br>"
                "Zeitpunkt: %{customdata[0]}<br>"
                "Algorithmus: %{customdata[1]}<br>"
                "Insel: %{customdata[4]}<br>"
                "Geschlecht: %{customdata[5]}<br>"
                "Culmen Length: %{customdata[6]} mm<br>"
                "Culmen Depth: %{customdata[7]} mm<br>"
                "Flipper Length: %{customdata[8]} mm<br>"
                "Body Mass: %{customdata[9]} g<br>"
                "Konfidenz: %{customdata[3]}<extra></extra>"
            ),
        )

    figure.update_layout(
        title="Datensatz-Vergleich",
        xaxis_title=x_title,
        yaxis_title=y_title,
        template="plotly_white",
        legend_title="Vorhersage",
    )
    return figure
