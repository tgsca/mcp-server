FROM python:3.11-slim

WORKDIR /app

# Systemabhängigkeiten installieren
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# uv installieren
RUN pip install uv

# Anwendungscode kopieren
COPY * .

# Abhängigkeiten installieren
RUN uv sync

# Port exponieren (falls notwendig)
EXPOSE 8000

# Anwendung starten
CMD ["python", "src/main.py"] 