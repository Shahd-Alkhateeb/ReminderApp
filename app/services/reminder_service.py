from datetime import date, time
from dataclasses import replace

from app.database.repositories.reminder_repository import (
    ReminderNotFoundError,
    ReminderRepository,
)
from app.models.reminder import Reminder


class ReminderService:
    def __init__(self, repository: ReminderRepository):
        self._repository = repository

    def create_one_time(
        self,
        title: str,
        scheduled_time: time,
        due_date: date,
        notes: str = "",
        category: str | None = None,
    ) -> Reminder:
        reminder = Reminder(
            title=title,
            time=scheduled_time,
            due_date=due_date,
            notes=notes,
            category=category,
        )
        return self._repository.add(reminder)

    def create_recurring(
        self,
        title: str,
        scheduled_time: time,
        days: tuple[int, ...],
        notes: str = "",
        category: str | None = None,
    ) -> Reminder:
        reminder = Reminder(
            title=title,
            time=scheduled_time,
            days=days,
            notes=notes,
            category=category,
        )
        return self._repository.add(reminder)

    def list_reminders(self, enabled_only: bool = False) -> list[Reminder]:
        return self._repository.list_all(enabled_only=enabled_only)

    def update(self, reminder: Reminder) -> Reminder:
        return self._repository.update(reminder)

    def set_enabled(self, reminder_id: int, enabled: bool) -> Reminder:
        if not isinstance(enabled, bool):
            raise ValueError("enabled must be a boolean")
        reminder = self._repository.get(reminder_id)
        if reminder is None:
            raise ReminderNotFoundError(f"reminder {reminder_id} does not exist")
        return self._repository.update(replace(reminder, enabled=enabled))

    def delete(self, reminder_id: int) -> bool:
        return self._repository.delete(reminder_id)