# Daymark

A local-first Android reminder assistant, starting with medication and daily reminders. It is a scheduling tool only and does not provide medical advice.

## Current stage

Phase 4: a Kivy reminder screen with local SQLite storage, add/edit/delete, enable/disable, and weekly recurrence. Reliable background scheduling, Android notifications, and voice input remain to be implemented and tested.

## Requirements

- Python 3.11 on Windows for the local Kivy development environment
- Kivy 2.3.1

Activate the Python 3.11 environment where Kivy is installed, then install the project dependencies:

```powershell
& "$env:USERPROFILE\kivy_env\Scripts\Activate.ps1"
python -m pip install -r requirements-dev.txt
python -m app.main
```

## Tests

Run the test suite with:

```powershell
python -m pytest
```

The reminder model, form parsing, service, and SQLite repository are covered by pytest.