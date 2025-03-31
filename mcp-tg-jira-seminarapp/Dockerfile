FROM python:3.11-slim

WORKDIR /app

# Systemabhängigkeiten installieren
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# uv installieren
RUN pip install uv

# Projektabhängigkeiten kopieren
COPY pyproject.toml requirements.txt* ./

# Abhängigkeiten installieren
RUN uv pip install -r requirements.txt

# Anwendungscode kopieren
COPY src/ ./src/
COPY .env ./.env

# Port exponieren (falls notwendig)
EXPOSE 8000

# Anwendung starten
CMD ["python", "src/main.py"] 