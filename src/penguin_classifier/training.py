"""Training helpers for the Random Forest penguin classifier."""

import os
import pickle
import hmac
import hashlib
from pathlib import Path

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.svm import SVC

from .preprocessing import prepare_training_dataset


def _get_data_dir() -> Path:
    """Get the directory path for storing data and models."""
    env_dir = os.getenv("PENGUIN_APP_DATA_DIR")
    if env_dir:
        return Path(env_dir)
    return Path(__file__).resolve().parent.parent / "data"


MODEL_PATH = _get_data_dir() / "models" / "random_forest.pkl"
CATEGORICAL_COLUMNS = ["island", "sex"]
NUMERICAL_COLUMNS = [
    "culmen_length_mm",
    "culmen_depth_mm",
    "flipper_length_mm",
    "body_mass_g",
]


def _get_secret_key() -> bytes:
    key_path = _get_data_dir() / "secret.key"
    if not key_path.exists():
        key_path.write_bytes(os.urandom(32))
    return key_path.read_bytes()


def _sign_model(path: Path) -> None:
    data = path.read_bytes()
    key = _get_secret_key()
    signature = hmac.new(key, data, hashlib.sha256).hexdigest()
    sig_path = path.with_suffix(path.suffix + ".sig")
    sig_path.write_text(signature)


def _verify_model(path: Path) -> bool:
    if not path.exists():
        return False
    sig_path = path.with_suffix(path.suffix + ".sig")
    if not sig_path.exists():
        return False
    data = path.read_bytes()
    key = _get_secret_key()
    expected = hmac.new(key, data, hashlib.sha256).hexdigest()
    actual = sig_path.read_text().strip()
    return hmac.compare_digest(expected, actual)


def build_random_forest_pipeline() -> Pipeline:
    """Create the scikit-learn pipeline for random forest classification."""

    preprocessor = ColumnTransformer(
        transformers=[
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                CATEGORICAL_COLUMNS,
            ),
            ("numerical", "passthrough", NUMERICAL_COLUMNS),
        ]
    )
    classifier = RandomForestClassifier(
        n_estimators=300,
        random_state=42,
        min_samples_leaf=2,
    )
    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("classifier", classifier),
        ]
    )


def train_random_forest_model(
    dataset_path: Path | None = None, database_path: Path | None = None
) -> Pipeline:
    """Train the random forest model from the penguins dataset."""

    prepared = prepare_training_dataset(dataset_path, database_path)
    pipeline = build_random_forest_pipeline()
    pipeline.fit(prepared.features, prepared.target)
    return pipeline


def save_random_forest_model(model: Pipeline, model_path: Path | None = None) -> Path:
    """Persist the trained model as a pickle file."""

    path = model_path or MODEL_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as file_handle:
        pickle.dump(model, file_handle)
    _sign_model(path)
    return path


def load_random_forest_model(model_path: Path | None = None) -> Pipeline:
    """Load a persisted random forest model from disk."""

    path = model_path or MODEL_PATH
    if not _verify_model(path):
        raise ValueError(
            "Model signature verification failed. The file may have been tampered with."
        )
    with path.open("rb") as file_handle:
        return pickle.load(file_handle)


def ensure_random_forest_model(
    model_path: Path | None = None,
    dataset_path: Path | None = None,
    database_path: Path | None = None,
    force_retrain: bool = False,
) -> Pipeline:
    """Load an existing model or train and persist a new one."""

    path = model_path or MODEL_PATH
    if path.exists() and not force_retrain:
        return load_random_forest_model(path)

    if not force_retrain:
        raise ValueError("Random Forest model is not trained yet.")

    model = train_random_forest_model(dataset_path, database_path)
    save_random_forest_model(model, path)
    return model


def build_svm_pipeline() -> Pipeline:
    """Create the scikit-learn pipeline for SVM classification."""
    preprocessor = ColumnTransformer(
        transformers=[
            ("categorical", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_COLUMNS),
            ("numerical", StandardScaler(), NUMERICAL_COLUMNS),
        ]
    )
    classifier = SVC(probability=True, random_state=42)
    return Pipeline(steps=[("preprocessor", preprocessor), ("classifier", classifier)])


def build_logistic_regression_pipeline() -> Pipeline:
    """Create the scikit-learn pipeline for Logistic Regression classification."""
    preprocessor = ColumnTransformer(
        transformers=[
            ("categorical", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL_COLUMNS),
            ("numerical", StandardScaler(), NUMERICAL_COLUMNS),
        ]
    )
    classifier = LogisticRegression(max_iter=1000, random_state=42)
    return Pipeline(steps=[("preprocessor", preprocessor), ("classifier", classifier)])


def ensure_model(
    algorithm: str,
    model_path: Path | None = None,
    dataset_path: Path | None = None,
    database_path: Path | None = None,
    force_retrain: bool = False,
) -> Pipeline:
    """Ensure a model for the given algorithm is loaded or retrained if necessary."""
    if algorithm == "Random Forest":
        return ensure_random_forest_model(model_path, dataset_path, database_path, force_retrain)

    # Generic approach for others
    filename = algorithm.lower().replace(" ", "_") + ".pkl"
    path = (model_path.parent if model_path else MODEL_PATH.parent) / filename
    if path.exists() and not force_retrain:
        if not _verify_model(path):
            raise ValueError(
                "Model signature verification failed. The file may have been tampered with."
            )
        with path.open("rb") as f:
            return pickle.load(f)

    if not force_retrain:
        raise ValueError(f"{algorithm} model is not trained yet.")

    prepared = prepare_training_dataset(dataset_path, database_path)
    if algorithm == "SVM":
        pipeline = build_svm_pipeline()
    else:
        pipeline = build_logistic_regression_pipeline()

    pipeline.fit(prepared.features, prepared.target)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("wb") as f:
        pickle.dump(pipeline, f)
    _sign_model(path)
    return pipeline


def delete_all_models(model_dir: Path | None = None) -> None:
    """Delete all trained model pickle files."""
    directory = model_dir or MODEL_PATH.parent
    if directory.exists():
        for file_path in directory.glob("*.pkl"):
            file_path.unlink()


def retrain_all_models(
    dataset_path: Path | None = None, database_path: Path | None = None, status_callback=None
):
    """
    Retrain all existing models using combined data and persist them.

    Calls the status_callback (if provided) with updates for each algorithm.
    Returns a dictionary containing the newly trained models.
    """
    algorithms = ["Random Forest", "SVM", "Logistic Regression"]

    if status_callback:
        for algo in algorithms:
            status_callback(algo, "pending")

    models = {}
    for algo in algorithms:
        if status_callback:
            status_callback(algo, "gestartet")
        models[algo] = ensure_model(
            algo, dataset_path=dataset_path, database_path=database_path, force_retrain=True
        )
        if status_callback:
            status_callback(algo, "abgeschlossen")
    return models
