import json
import sqlite3
from dataclasses import replace
from datetime import date, datetime, time, timezone

from app.database.database import Database
from app.models.reminder import Reminder


class ReminderNotFoundError(LookupError):
    pass


class ReminderRepository:
    def __init__(self, database: Database):
        self._database = database

    def add(self, reminder: Reminder) -> Reminder:
        if reminder.id is not None:
            raise ValueError("new reminders must not have an id")

        with self._database.connection() as connection:
            cursor = connection.execute(
                """
                INSERT INTO reminders (
                    title, time, due_date, days, notes, category, enabled,
                    created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                self._values(reminder),
            )
            reminder_id = cursor.lastrowid

        return replace(reminder, id=reminder_id)

    def get(self, reminder_id: int) -> Reminder | None:
        with self._database.connection() as connection:
            row = connection.execute(
                "SELECT * FROM reminders WHERE id = ?", (reminder_id,)
            ).fetchone()
        return self._from_row(row) if row is not None else None

    def list_all(self, enabled_only: bool = False) -> list[Reminder]:
        query = "SELECT * FROM reminders"
        if enabled_only:
            query += " WHERE enabled = 1"
        query += " ORDER BY id"

        with self._database.connection() as connection:
            rows = connection.execute(query).fetchall()
        return [self._from_row(row) for row in rows]

    def update(self, reminder: Reminder) -> Reminder:
        if reminder.id is None:
            raise ValueError("reminder must have an id before it can be updated")

        updated = replace(reminder, updated_at=datetime.now(timezone.utc))
        with self._database.connection() as connection:
            cursor = connection.execute(
                """
                UPDATE reminders
                SET title = ?, time = ?, due_date = ?, days = ?, notes = ?,
                    category = ?, enabled = ?, created_at = ?, updated_at = ?
                WHERE id = ?
                """,
                (*self._values(updated), updated.id),
            )
            if cursor.rowcount == 0:
                raise ReminderNotFoundError(f"reminder {updated.id} does not exist")
        return updated

    def delete(self, reminder_id: int) -> bool:
        with self._database.connection() as connection:
            cursor = connection.execute(
                "DELETE FROM reminders WHERE id = ?", (reminder_id,)
            )
        return cursor.rowcount > 0

    @staticmethod
    def _values(reminder: Reminder) -> tuple[object, ...]:
        return (
            reminder.title,
            reminder.time.isoformat(),
            reminder.due_date.isoformat() if reminder.due_date else None,
            json.dumps(reminder.days),
            reminder.notes,
            reminder.category,
            int(reminder.enabled),
            reminder.created_at.isoformat(),
            reminder.updated_at.isoformat(),
        )

    @staticmethod
    def _from_row(row: sqlite3.Row) -> Reminder:
        return Reminder(
            id=row["id"],
            title=row["title"],
            time=time.fromisoformat(row["time"]),
            due_date=date.fromisoformat(row["due_date"]) if row["due_date"] else None,
            days=tuple(json.loads(row["days"])),
            notes=row["notes"],
            category=row["category"],
            enabled=bool(row["enabled"]),
            created_at=datetime.fromisoformat(row["created_at"]),
            updated_at=datetime.fromisoformat(row["updated_at"]),
        )