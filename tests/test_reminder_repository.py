from dataclasses import replace
from datetime import date, time

import pytest

from app.database.database import Database
from app.database.repositories.reminder_repository import (
    ReminderNotFoundError,
    ReminderRepository,
)
from app.models.reminder import Reminder


@pytest.fixture
def repository(tmp_path):
    database = Database(tmp_path / "reminders.sqlite3")
    database.initialize()
    return ReminderRepository(database)


def test_add_and_get_preserve_reminder_fields(repository):
    reminder = Reminder(
        title="Medication",
        time=time(20, 15),
        days=(0, 2, 4),
        notes="Take after dinner",
        category="Health",
    )

    saved = repository.add(reminder)

    assert saved.id == 1
    assert repository.get(saved.id) == saved


def test_list_all_can_filter_disabled_reminders(repository):
    enabled = repository.add(
        Reminder(title="Enabled", time=time(8), due_date=date(2026, 10, 1))
    )
    repository.add(
        Reminder(title="Disabled", time=time(9), due_date=date(2026, 10, 1), enabled=False)
    )

    assert repository.list_all() == [enabled, repository.get(2)]
    assert repository.list_all(enabled_only=True) == [enabled]


def test_update_persists_changes_and_refreshes_updated_at(repository):
    saved = repository.add(
        Reminder(title="Old title", time=time(8), due_date=date(2026, 10, 1))
    )
    changed = replace(saved, title="New title", notes="Updated note")

    updated = repository.update(changed)

    assert updated.title == "New title"
    assert updated.notes == "Updated note"
    assert updated.updated_at >= saved.updated_at
    assert repository.get(saved.id) == updated


def test_update_raises_for_missing_reminder(repository):
    reminder = Reminder(
        id=42,
        title="Missing",
        time=time(8),
        due_date=date(2026, 10, 1),
    )

    with pytest.raises(ReminderNotFoundError):
        repository.update(reminder)


def test_delete_returns_whether_a_row_was_removed(repository):
    saved = repository.add(
        Reminder(title="Temporary", time=time(8), due_date=date(2026, 10, 1))
    )

    assert repository.delete(saved.id)
    assert not repository.delete(saved.id)
    assert repository.get(saved.id) is None


def test_add_rejects_a_reminder_that_already_has_an_id(repository):
    reminder = Reminder(
        id=1,
        title="Existing",
        time=time(8),
        due_date=date(2026, 10, 1),
    )

    with pytest.raises(ValueError, match="must not have an id"):
        repository.add(reminder)