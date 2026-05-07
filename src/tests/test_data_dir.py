# pylint: disable=missing-function-docstring,missing-module-docstring,duplicate-code,import-outside-toplevel,line-too-long,wrong-import-position,wrong-import-order
import os
from pathlib import Path
from unittest import mock


def test_data_dir_can_be_configured_via_env_var():
    with mock.patch.dict(os.environ, {"PENGUIN_APP_DATA_DIR": "/custom/data/path"}):
        from penguin_classifier.database import _get_data_dir as db_get_data_dir
        from penguin_classifier.training import _get_data_dir as train_get_data_dir
        from penguin_classifier.preprocessing import _get_data_dir as prep_get_data_dir

        assert db_get_data_dir() == Path("/custom/data/path")
        assert train_get_data_dir() == Path("/custom/data/path")
        assert prep_get_data_dir() == Path("/custom/data/path")


def test_data_dir_defaults_to_parent_data_dir():
    with mock.patch.dict(os.environ, clear=True):
        from penguin_classifier.database import _get_data_dir as db_get_data_dir

        expected = Path(__file__).resolve().parent.parent / "data"
        assert db_get_data_dir() == expected
