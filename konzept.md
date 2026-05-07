# Pinguinklassifizierer
## Konzeptionsphase
### Datengrundlage:
Der Palmer Penguins-Datensatz dient als Basis: Enthält 344 Messungen von 3 Pinguinarten (Adelie: 152, Gentoo: 124, Chinstrap: 68) 
mit Features wie Island, Culmen Length (Schnabellänge), Culmen Depth (Schnabeltiefe), Flipper Length (Flossenlänge),
Body Mass (Körpermasse), Sex und Year. Train/Test-Split für Modelltraining (80/20); 
Metriken: Accuracy >95%, Precision/Recall/F1 pro Klasse.

### Technologie:
Python (pandas, scikit-learn, plotly/dash). 
Dash für UI – interaktiv, responsiv. 
Erweiterung: Dropdown-Auswahl für Klassifizierer (Random Forest, SVM, Logistic Regression) – Nutzer wählt Algo, 
App lädt korrektes trainiertes Modell (Pickle pro Algo), zeigt Prediction + Metriken/Feature Importance.

### Architektur:
* **Frontend (Dash):** \
Eingabe-Form (Sliders/Dropdowns), Algo-DropdownAlgo-Dropdown (RF/SVM/LR), Submit → Prediction, Confidence, Vergleichsplot.
* **Backend:** \
  Modell-Dict; Preprocessing (One-Hot); SQLite für Speicherung; Alembic für DB-Migration.
* **Modell-Training:** \
  Separate Skripte: RF, SVM, LR – Cross-Validation, Feature Importance Plots.
* **UML-Sequenz:** \
  User → UI → Algo-Auswahl → Load Model → Predict → Plotly-Scatter (neuer Punkt vs. Trainingsdaten, farblich pro Art) → DB.

### UI-Design (schematisch):
* **Oben:**
  - Eingabe-Felder (Neue Daten) 
  - Dropdown: "Wähle Algorithmus:" Random Forest | SVM | Logistic Regression.
* **Mitte:**
  - Ergebnis (Pred. Art, Wahrsch. Balken, Metriken-Tabelle).
* **Unten:**
  - PCA-Scatter (Features vs. Dataset), gespeicherte Daten-Tabelle (CSV-Export).

### Deployment:
* **Docker-Container:** \
Dockerfile mit Python-Env, requirements.txt, app.py → docker build → docker run.
Plattformunabhängig (Windows/Linux/Mac); optional GitHub Pages für Demo.
* **Skalierbarkeit:** \
Dank Docker-Container und SQLite DB vertikal skalierbare lokale Ausführung 
und horizontal skalierbar für Cloud-Deployments.
* **Modell-Updates:** \
Neuer Trainings-Button (DB → Retrain → Pickle-Export). Batch-Uploads für Expeditionen.

### Sicherheit:
Lokale DB (SQLite, verschlüsselt); keine Cloud-Übertragung (Datenschutz GPS-sensitive Daten); Input-
Validierung gegen Injection.