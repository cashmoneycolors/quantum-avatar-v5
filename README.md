# Amriswil Markt Quantum-Avatar

## Installation

1. Python 3.13 installieren (Docker nutzt 3.13; 3.14 kann je nach spaCy/pydantic v1 Warnungen/Probleme verursachen).
2. Optional (Windows): `py -3.13 -m venv .venv`
3. Install: `python -m pip install -r requirements.txt`

## Start

- API starten: `python quantum_avatar/ui/app.py`
- Demo-Skript starten: `python amriswil_core.py`

## Tests

- Offline (keine Model-Downloads):
 	- PowerShell: `$env:HF_HUB_OFFLINE=1; $env:TRANSFORMERS_OFFLINE=1; py -3.13 -m unittest discover -s quantum_avatar/tests -p "test_*.py" -t .`

## Konfiguration (ENV)

- Stripe: `STRIPE_API_KEY`
- Twilio WhatsApp: `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_WHATSAPP_FROM`
- Vorlage: `.env.example`

## CI

- GitHub Actions nutzt `requirements-ci.txt` (minimal), damit Tests auf Python 3.13 ohne optionalen ML/Quantum-Stack laufen.

## Cloud-Deployment

- Docker verwenden: `docker build -t amriswil .`
- `docker run amriswil`
