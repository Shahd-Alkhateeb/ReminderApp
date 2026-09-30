from datetime import date, time

import pytest

from app.database.database import Database
from app.database.repositories.reminder_repository import (
    ReminderNotFoundError,
    ReminderRepository,
)
from app.services.reminder_service import ReminderService


@pytest.fixture
def service(tmp_path):
    database = Database(tmp_path / "reminders.sqlite3")
    database.initialize()
    return ReminderService(ReminderRepository(database))


def test_service_creates_one_time_and_recurring_reminders(service):
    one_time = service.create_one_time("Dose", time(8), date(2026, 10, 1))
    recurring = service.create_recurring("Walk", time(7), (0, 2, 4))

    assert one_time.id is not None
    assert one_time.due_date == date(2026, 10, 1)
    assert recurring.days == (0, 2, 4)
    assert service.list_reminders() == [one_time, recurring]


def test_service_toggles_enabled_state(service):
    reminder = service.create_one_time("Dose", time(8), date(2026, 10, 1))

    disabled = service.set_enabled(reminder.id, False)

    assert not disabled.enabled
    assert service.list_reminders(enabled_only=True) == []
    assert service.list_reminders() == [disabled]


def test_service_reports_missing_reminders_when_toggling(service):
    with pytest.raises(ReminderNotFoundError):
        service.set_enabled(99, False)


def test_service_rejects_non_boolean_enabled_state(service):
    with pytest.raises(ValueError, match="enabled must be a boolean"):
        service.set_enabled(1, 0)


def test_service_deletes_reminders(service):
    reminder = service.create_one_time("Dose", time(8), date(2026, 10, 1))

    assert service.delete(reminder.id)
    assert service.list_reminders() == []