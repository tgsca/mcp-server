# PROJECT.md - MCP Text Pseudonymizer

## Projektübersicht

**Ziel**: Ein MCP-Server zur automatischen Pseudonymisierung von Texten mittels Named Entity Recognition (NER), der sensible Informationen durch konsistente Platzhalter ersetzt und dabei die Lesbarkeit des Textes erhält.

**Problem**: Datenschutzkonforme Verarbeitung von Texten erfordert die Entfernung personenbezogener und sensibler Daten. Manuelle Pseudonymisierung ist zeitaufwändig und fehleranfällig.

**Lösung**: Automatische Erkennung und Ersetzung von Entitäten basierend auf der erkannten Textsprache mit spezialisierten NER-Modellen aus Huggingface.

## Tech Stack

### Core Technologies
- **Python 3.12+**: Hauptprogrammiersprache
- **FastMCP**: Framework für MCP-Server-Implementierung
- **uv**: Package Manager für schnelle Dependency-Verwaltung
- **Docker & Docker Compose**: Containerisierung und Orchestrierung

### NLP/ML Stack
- **Huggingface Transformers**: Model Hub Integration
- **flair/ner-german**: NER-Modell für deutsche Texte
- **flair/ner-english**: NER-Modell für englische Texte
- **langdetect**: Spracherkennung als Fallback
- **spacy**: Zusätzliche NLP-Pipeline für erweiterte Entity-Erkennung

### Erweiterte Entity-Erkennung
- **dateparser**: Datumserkennung in verschiedenen Formaten
- **phonenumbers**: Internationale Telefonnummernerkennung
- **email-validator**: E-Mail-Adressen-Erkennung
- **Regex-Patterns**: Custom Patterns für IDs, Kontonummern, etc.

## Fachlicher Deep Dive

### Entity-Erkennung und Pseudonymisierung

**Unterstützte Entity-Typen**:
1. **Standard NER**: 
   - PER (Personen): → PERSON_[ID]
   - LOC (Orte): → LOCATION_[ID]
   - ORG (Organisationen): → ORGANIZATION_[ID]

2. **Erweiterte Entitäten**:
   - DATE (Daten): → DATE_[ID]
   - EMAIL (E-Mail-Adressen): → EMAIL_[ID]
   - PHONE (Telefonnummern): → PHONE_[ID]
   - ID (Identifikationsnummern): → ID_[ID]
   - IBAN (Kontonummern): → IBAN_[ID]
   - LICENSE (Führerschein/Ausweisnummern): → LICENSE_[ID]

### Spracherkennung und Modellauswahl

```python
language_models = {
    "de": "flair/ner-german",
    "en": "flair/ner-english"
}
```

**Erkennungsprozess**:
1. Primär: Analyse der ersten 200 Zeichen mittels Huggingface language-detection
2. Fallback: langdetect Library
3. Default: Englisch bei Unsicherheit

### Konsistenz und Mapping

**Mapping-Strategie**:
- Gleiche Entitäten erhalten gleiche Platzhalter innerhalb eines Dokuments
- Mapping-Tabelle wird pro Session gespeichert
- Format: `{original_entity: placeholder, ...}`

**Beispiel**:
```
Original: "Max Müller wohnt in Berlin. Max arbeitet bei Siemens."
Pseudonymisiert: "PERSON_1 wohnt in LOCATION_1. PERSON_1 arbeitet bei ORGANIZATION_1."
Mapping: {"Max Müller": "PERSON_1", "Berlin": "LOCATION_1", "Siemens": "ORGANIZATION_1"}
```

### Batch-Verarbeitung

- Parallele Verarbeitung mehrerer Texte
- Gemeinsame Mapping-Tabelle für Konsistenz über Dokumente
- Progress-Tracking für große Batches

## Anforderungen an Ausgaben

### MCP Tools Spezifikation

#### 1. `pseudonymize_text`
**Input**:
```json
{
  "text": "string | array<string>",
  "language": "auto | de | en" (optional, default: "auto"),
  "preserve_formatting": "boolean" (optional, default: true)
}
```

**Output**:
```json
{
  "pseudonymized": "string | array<string>",
  "detected_language": "de | en",
  "entity_count": "number"
}
```

#### 2. `detect_language`
**Input**:
```json
{
  "text": "string"
}
```

**Output**:
```json
{
  "language": "de | en",
  "confidence": "number (0-1)"
}
```

#### 3. `list_supported_languages`
**Output**:
```json
{
  "languages": [
    {"code": "de", "name": "German", "model": "flair/ner-german"},
    {"code": "en", "name": "English", "model": "flair/ner-english"}
  ]
}
```

#### 4. `get_entity_mappings`
**Input**:
```json
{
  "session_id": "string" (optional)
}
```

**Output**:
```json
{
  "mappings": {
    "Max Müller": "PERSON_1",
    "Berlin": "LOCATION_1",
    ...
  },
  "statistics": {
    "total_entities": "number",
    "by_type": {
      "PERSON": "number",
      "LOCATION": "number",
      ...
    }
  }
}
```

### Performance-Anforderungen

- **Latenz**: < 2s für Texte bis 1000 Wörter
- **Durchsatz**: Min. 10 Texte/Sekunde bei Batch-Verarbeitung
- **Speicher**: Max. 4GB RAM bei vollem Modell-Load
- **Modell-Caching**: Modelle bleiben nach erstem Load im Speicher

### Fehlerbehandlung

- Graceful Degradation bei Modell-Ausfall
- Klare Fehlermeldungen bei ungültigen Eingaben
- Timeout-Handling für lange Texte
- Logging aller Fehler mit Context

### Docker-Konfiguration

```dockerfile
FROM python:3.12-slim
# Multi-stage build für optimierte Image-Größe
# Vorgeladene Modelle im Image für schnellen Start
```

```yaml
# docker-compose.yml
services:
  mcp-pseudonymizer:
    build: .
    ports:
      - "3000:3000"
    environment:
      - MODEL_CACHE_DIR=/models
      - LOG_LEVEL=INFO
    volumes:
      - model-cache:/models
```