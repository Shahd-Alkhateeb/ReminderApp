# Daymark

A local-first Android reminder assistant, starting with medication and daily reminders. It is a scheduling tool only and does not provide medical advice.

## Current stage

Phase 1 foundation: a minimal Kivy home screen and the Python project setup. Reminder management, persistence, notifications, and voice input will be added in later stages.

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

Tests will be introduced alongside the reminder model and its behavior in Phase 2.