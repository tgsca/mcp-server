# MCP-Server

Der MCP-Server ist eine Microservice-Architektur, die verschiedene Dienste für das Management Control Panel (MCP) bereitstellt. Das Projekt besteht aus mehreren unabhängigen Microservices, die jeweils spezifische Funktionalitäten anbieten.

## Microservices

### MCP GuruFocus Service
Ein Service zur Integration von Finanzdaten von GuruFocus. Dieser Service bietet Endpunkte für:
- Aktieninformationen
- Finanzielle Kennzahlen
- Analysten-Schätzungen
- Segmentdaten
- Nachrichten

### MCP TG JIRA SeminarApp Service
Ein Service zur Integration von JIRA und Zephyr für das Testmanagement. Dieser Service bietet Endpunkte für:
- Projekt-Informationen
- Anforderungsmanagement
- Testfall-Management
- Testausführungs-Management

## Erste Schritte

1. Klone das Repository:
```bash
git clone <repository-url>
```

2. Erstelle für jeden Service eine `.env` Datei basierend auf der jeweiligen `.env.template`.

## Entwicklung

Jeder Microservice:
- Verwendet Python 3.12
- Hat seine eigene virtuelle Umgebung
- Wird mit `pyproject.toml` verwaltet
- Verwendet `uv` als Package-Manager

### Neuer MCP-Server

Führe das Setup-Skript aus:
```bash
./new_mcp_server.sh
```

## Lizenz

Alle Rechte vorbehalten. 