# Basis-Image: Python 3.11 (schlank)
FROM python:3.11-slim

# Arbeitsverzeichnis im Container
WORKDIR /app

# System-Abhängigkeiten installieren
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Python-Abhängigkeiten kopieren und installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Anwendungscode kopieren
COPY ./app ./app

# Umgebungsvariablen setzen
ENV PYTHONPATH=/app
ENV MCP_SERVER_MODE=sse

# Container-Port (falls benötigt)
EXPOSE 8000

# Anwendung starten
CMD ["python", "app/main.py"]