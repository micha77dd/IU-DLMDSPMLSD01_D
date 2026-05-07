# Palmer Penguins Klassifikator (Deep Learning Projekt)

## Zweck der Applikation
Diese Applikation dient der Klassifikation von Pinguin-Arten (Adélie, Chinstrap, Gentoo) basierend auf dem bekannten "Palmer Penguins" Datensatz. Sie verwendet Deep Learning Modelle für die Vorhersage und bietet eine interaktive Weboberfläche, die mit Plotly Dash umgesetzt wurde. Die zugrundeliegenden Daten und durchgeführten Klassifikationen werden in einer SQLite-Datenbank gespeichert, deren Schema durch Alembic-Migrationen verwaltet wird.

## Wesentliche Funktionalitäten
- **Interaktive Weboberfläche:** Eine benutzerfreundliche UI (Dash), in der Anwender Pinguin-Merkmale (wie Schnabellänge, Schnabeltiefe, Flipperlänge und Gewicht) eingeben können.
- **Deep Learning Klassifikation:** Einbindung trainierter Modelle zur schnellen Vorhersage der Pinguin-Art in Echtzeit anhand der eingegebenen Merkmale.
- **Datenpersistenz:** Speicherung von Eingabedaten und Resultaten in einer strukturierten Datenbank.
- **Datenverwaltung:** Funktionen zur automatischen Befüllung mit Demodaten für schnelle Evaluierungen sowie das Löschen von Datensätzen und der gesamten Datenbank.
- **Hohe Testabdeckung:** Qualitätssicherung durch automatisierte Backend- und Frontend-Tests (Cypress für E2E-Tests, pytest für Unit-Tests).

## Start der Applikation

Die Anwendung kann auf zwei Arten gestartet werden: im Stand-Alone-Betrieb für die lokale Entwicklung oder portabel als Docker-Container.

### 1. Docker-Betrieb (Empfohlen)
Die Anwendung bringt über das mitgelieferte `Dockerfile` alle System- und Python-Abhängigkeiten isoliert mit.

**Voraussetzungen:** Docker ist auf dem System installiert.

Wechseln Sie in das Wurzelverzeichnis des Repositories und führen Sie folgende Befehle aus:

```bash
# Verzeichnis wechseln
cd DLMDSPMLSD01_D_Projekt_DeepLearning

# Docker Image bauen
docker build -t penguin-classifier .

# Docker Container starten (Port 8050 mappen)
docker run -p 8050:8050 penguin-classifier
```
Die Weboberfläche ist anschließend im Browser unter `http://localhost:8050` erreichbar.

**Konfiguration (Umgebungsvariablen):**
Das Verhalten im Docker-Container kann über folgende Umgebungsvariablen gesteuert werden:
- `PENGUIN_APP_HOST`: Host-Binding (Standard: `0.0.0.0`).
- `PENGUIN_APP_PORT`: Port, auf dem die App lauscht (Standard: `8050`).
- `PENGUIN_APP_DEBUG`: Aktiviert den Dash-Debug-Modus (`true` oder `false`, Standard: `false`).
- `PENGUIN_APP_DATA_DIR`: Pfad zum Verzeichnis für die SQLite-Datenbank, trainierte Modelle und Basisdaten (Standard im Container: `/app/data`). Um Daten persistent zu speichern, sollte hier ein Docker Volume gemountet werden.
- `PENGUIN_ADMIN_SECRET`: Geheimnis/Passwort (Token) zur Absicherung von Admin-Funktionen wie dem WebSocket Re-Training (Standard: `admin123`).

*Beispiel mit persistentem Volume und alternativem Port:*
```bash
docker run -p 8080:8050 \
  -e PENGUIN_APP_PORT=8050 \
  -v $(pwd)/my_persistent_data:/app/data \
  penguin-classifier
```

### 2. Stand-Alone-Betrieb (Lokale Entwicklung)
Für die aktive Entwicklung auf dem Host-System empfiehlt sich die Nutzung einer virtuellen Python-Umgebung.

**Voraussetzungen:** Python 3.11+, Node.js (für E2E-Tests).

```bash
cd DLMDSPMLSD01_D_Projekt_DeepLearning/src

# Virtuelle Umgebung erstellen und aktivieren (Linux/macOS)
python -m venv .venv
source .venv/bin/activate

# Python-Abhängigkeiten installieren
pip install -r requirements.txt

# Datenbankmigrationen initial ausführen
alembic upgrade head

# Anwendung lokal starten
python -m penguin_classifier.app
```
*Hinweis: Alternativ kann auf Unix-Systemen auch das Skript `./start_frontend.sh` ausgeführt werden.*
Die Applikation ist nun unter `http://localhost:8050` aufrufbar.

## Testen der Applikation

Das Projekt gewährleistet eine stabile Funktionalität durch striktes Testen auf mehreren Ebenen.

### Unit- & Integrationstests (Backend)
Die Tests für die Python-Module (Datenbank-Interaktionen, Modell-Inferenz) sind mit `pytest` implementiert.

```bash
cd DLMDSPMLSD01_D_Projekt_DeepLearning/src
source .venv/bin/activate

# Alle Pytest-Tests ausführen
pytest tests/
```

### End-to-End Tests (Cypress)
Cypress simuliert echte Nutzerinteraktionen und testet die Benutzeroberfläche ganzheitlich gegen die laufende Instanz.
**Achtung:** Die Applikation muss dafür gestartet sein und unter `localhost:8050` zur Verfügung stehen.

```bash
cd DLMDSPMLSD01_D_Projekt_DeepLearning/src

# Node-Abhängigkeiten installieren (einmalig notwendig)
npm install

# Alle Cypress Tests im Headless-Modus ausführen
npx cypress run

# Alternativ: Cypress interaktiv im Browser-Test-Runner öffnen
npx cypress open
```