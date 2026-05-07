"""Application configuration values."""

from dataclasses import dataclass, field


@dataclass(frozen=True)
class AppConfig:
    """Configuration for the Dash frontend."""

    title: str = "Pinguinklassifizierer"
    algorithms: tuple[str, ...] = (
        "Random Forest",
        "SVM",
        "Logistic Regression",
    )
    islands: tuple[str, ...] = (
        "Biscoe",
        "Dream",
        "Torgersen",
    )
    sexes: tuple[str, ...] = (
        "female",
        "male",
    )
    species: tuple[str, ...] = (
        "Adelie",
        "Chinstrap",
        "Gentoo",
    )
    slider_defaults: dict[str, int] = field(
        default_factory=lambda: {
            "culmen_length_mm": 45,
            "culmen_depth_mm": 17,
            "flipper_length_mm": 200,
            "body_mass_g": 4200,
        }
    )
