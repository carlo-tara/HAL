"""Smoke client for local Laya (/var/www/laya)."""
from __future__ import annotations

import os
import sys

import requests

url = os.environ.get("LAYA_URL", "http://127.0.0.1:8091").rstrip("/") + "/v1/predict"
api_key = os.environ.get("LAYA_API_KEY", "sk-local")
payload = {"text": "ciao mamma!"}

print(f"Invio query a {url}: {payload}")

try:
    response = requests.post(
        url,
        json=payload,
        headers={"Authorization": f"Bearer {api_key}"},
        timeout=60.0,
    )
    print(f"Status Code: {response.status_code}")
    print(f"Risposta: {response.text}")
    sys.exit(0 if response.ok else 1)
except requests.exceptions.RequestException as e:
    print(f"Errore di connessione: {e}")
    print("Hint: cd /var/www/laya && make up && curl -sf http://127.0.0.1:8091/health")
    sys.exit(1)
