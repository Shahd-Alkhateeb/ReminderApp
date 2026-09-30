# Daymark

A local-first Android reminder assistant, starting with medication and daily reminders. It is a scheduling tool only and does not provide medical advice.

## Current stage

Phase 3: a minimal Kivy home screen, a validated reminder model, and a SQLite repository for local CRUD. Kivy screens, scheduling, Android notifications, and voice input remain to be implemented and tested.

## Requirements

- Python 3.12 on Windows for the local Kivy development environment
- Kivy 2.3.1

The existing Python 3.14 environment does not have a compatible Kivy wheel. Install Python 3.12, then create a separate environment so the existing `.venv` is left untouched:

```powershell
py -3.12 -m venv .venv312
.\.venv312\Scripts\Activate.ps1
python -m pip install -r requirements-dev.txt
python -m app.main
```

## Tests

Run the test suite with:

```powershell
python -m pytest
```

The reminder model and SQLite repository can be tested independently of Kivy with:

```powershell
python -m pytest
```