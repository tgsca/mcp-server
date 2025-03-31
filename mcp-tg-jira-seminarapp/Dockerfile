FROM python:3.11-slim

WORKDIR /app

# Systemabhängigkeiten installieren
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Poetry installieren
RUN pip install poetry

# Projektabhängigkeiten kopieren
COPY pyproject.toml poetry.lock* ./

# Poetry konfigurieren, um virtualenv im Projekt zu erstellen
RUN poetry config virtualenvs.create false

# Abhängigkeiten installieren
RUN poetry install --no-dev --no-interaction --no-ansi

# Anwendungscode kopieren
COPY src/ ./src/
COPY .env ./.env

# Port exponieren (falls notwendig)
EXPOSE 8000

# Anwendung starten
CMD ["poetry", "run", "python", "src/main.py"] 