FROM python:3.11-slim

# Setze Umgebungsvariablen
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PENGUIN_APP_HOST=0.0.0.0 \
    PENGUIN_APP_PORT=8050 \
    PENGUIN_APP_DEBUG=false \
    PENGUIN_APP_DATA_DIR=/app/data \
    PENGUIN_ADMIN_SECRET=admin123

# Arbeitsverzeichnis erstellen und setzen
WORKDIR /app/src

# Requirements kopieren und installieren
COPY src/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Den restlichen Quellcode selektiv kopieren (ohne Tests, node_modules etc.)
COPY src/penguin_classifier/ ./penguin_classifier/
COPY src/alembic/ ./alembic/
COPY src/alembic.ini .
COPY src/data/penguins.csv ./data/

# Port exponieren
EXPOSE 8050

# App starten
CMD ["python", "-m", "penguin_classifier.app"]
