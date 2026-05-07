#!/usr/bin/env bash
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SRC_DIR="${SCRIPT_DIR}/src"
VENV_DIR="${SRC_DIR}/.venv"
PYTHON_BIN="${VENV_DIR}/bin/python"
PIP_BIN="${VENV_DIR}/bin/pip"
APP_HOST="${PENGUIN_APP_HOST:-0.0.0.0}"
APP_PORT="${PENGUIN_APP_PORT:-8050}"
APP_DEBUG="${PENGUIN_APP_DEBUG:-true}"

cd "${SRC_DIR}"

recreate_venv() {
  echo "[INFO] Erstelle virtuelles Environment unter ${VENV_DIR} ..."
  rm -rf "${VENV_DIR}"
  python3 -m venv "${VENV_DIR}"
}

if [[ ! -d "${VENV_DIR}" ]]; then
  recreate_venv
fi

if [[ ! -x "${PYTHON_BIN}" || ! -x "${PIP_BIN}" ]]; then
  echo "[WARN] Virtuelles Environment ist unvollständig oder defekt. Erzeuge es neu ..."
  recreate_venv
fi

if ! "${PYTHON_BIN}" -c 'import sys; print(sys.executable)' >/dev/null 2>&1; then
  echo "[WARN] Python im virtuellen Environment ist nicht lauffähig. Erzeuge es neu ..."
  recreate_venv
fi

echo "[INFO] Installiere/aktualisiere Python-Abhängigkeiten in .venv ..."
"${PIP_BIN}" install -r requirements.txt

echo "[INFO] Starte Frontend aus .venv unter http://${APP_HOST}:${APP_PORT}"
export PENGUIN_APP_HOST="${APP_HOST}"
export PENGUIN_APP_PORT="${APP_PORT}"
export PENGUIN_APP_DEBUG="${APP_DEBUG}"
exec "${PYTHON_BIN}" -m penguin_classifier.app
