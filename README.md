# Amriswil Markt Quantum-Avatar

## Installation

1. Python 3.13+ installieren (Docker nutzt 3.13).
2. `python -m pip install -r requirements.txt`

## Start

- API starten: `python quantum_avatar/ui/app.py`
- Demo-Skript starten: `python amriswil_core.py`

## Tests

- Offline (keine Model-Downloads):
	- PowerShell: `$env:HF_HUB_OFFLINE=1; $env:TRANSFORMERS_OFFLINE=1; python -m unittest discover -s quantum_avatar/tests -p "test_*.py"`

## Cloud-Deployment

- Docker verwenden: `docker build -t amriswil .`
- `docker run amriswil`
