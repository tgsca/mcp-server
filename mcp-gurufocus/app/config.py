"""
Konfigurationsmodul für die Finanz-API.
"""

import os
from dotenv import load_dotenv

# Lade Umgebungsvariablen aus .env Datei
load_dotenv()

# API-Konfiguration
API_KEY = os.getenv('GURUFOCUS_API_KEY')
BASE_URL = f"https://api.gurufocus.com/public/user/{API_KEY}"
