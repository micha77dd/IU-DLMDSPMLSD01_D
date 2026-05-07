"""Dash application entry point."""

import json
import logging
import os
import threading

from dash import Dash
from flask_sock import Sock

from .config import AppConfig
from .layout import create_layout
from .callbacks import register_all_callbacks

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

_TRAINING_LOCK = threading.Lock()
ADMIN_SECRET = os.getenv('ADMIN_SECRET', 'admin123')

def create_app(config: AppConfig | None = None) -> Dash:
    """Create and configure the Dash application."""

    app_config = config or AppConfig()
    dash_app = Dash(__name__, eager_loading=True)
    dash_app.title = app_config.title
    dash_app.layout = lambda: create_layout(app_config)

    register_all_callbacks(dash_app)

    sock = Sock(dash_app.server)

    @sock.route('/ws/retrain')
    def ws_retrain(ws):
        # pylint: disable=import-outside-toplevel
        from .training import retrain_all_models
        from .layout import get_last_training_time

        while True:
            data = ws.receive()
            if not data:
                continue

            try:
                msg = json.loads(data)
                if msg.get('action') == 'retrain':
                    if msg.get('token') != ADMIN_SECRET:
                        ws.send(json.dumps({
                            "model": "System",
                            "status": "Fehler: Ungültiges Admin-Token"
                        }))
                        logger.warning("Unautorisierter Trainings-Versuch")
                        continue

                    # pylint: disable=consider-using-with
                    if not _TRAINING_LOCK.acquire(blocking=False):
                        ws.send(json.dumps({
                            "model": "System",
                            "status": "Fehler: Ein Training läuft bereits"
                        }))
                        logger.warning("Trainings-Versuch blockiert: Lock aktiv")
                        continue

                    try:
                        def status_cb(algo, status):
                            ws.send(json.dumps({"model": algo, "status": status}))

                        logger.info("Starte manuelles Re-Training via WebSocket...")
                        retrain_all_models(status_callback=status_cb)

                        ws.send(json.dumps({
                            "action": "complete",
                            "last_training_time": get_last_training_time()
                        }))
                        logger.info("Re-Training erfolgreich abgeschlossen.")
                    finally:
                        _TRAINING_LOCK.release()
            except Exception as e:  # pylint: disable=broad-exception-caught
                logger.error("WebSocket error: %s", e)

    return dash_app


app = create_app()

if __name__ == "__main__":
    app_host = os.getenv("PENGUIN_APP_HOST", "0.0.0.0")
    app_port = int(os.getenv("PENGUIN_APP_PORT", "8050"))
    app_debug = os.getenv("PENGUIN_APP_DEBUG", "false").lower() == "true"
    app.run(host=app_host, port=app_port, debug=app_debug)
