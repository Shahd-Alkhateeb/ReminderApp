from dataclasses import dataclass, field
from datetime import date, datetime, time, timedelta, timezone


@dataclass(slots=True)
class Reminder:
    title: str
    time: time
    due_date: date | None = None
    days: tuple[int, ...] = ()
    id: int | None = None
    notes: str = ""
    category: str | None = None
    enabled: bool = True
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))

    def __post_init__(self) -> None:
        if not isinstance(self.title, str) or not self.title.strip():
            raise ValueError("title must not be empty")
        self.title = self.title.strip()

        if not isinstance(self.time, time) or self.time.tzinfo is not None:
            raise ValueError("time must be a local time without a timezone")

        try:
            days = tuple(self.days)
        except TypeError as error:
            raise ValueError("days must be an iterable of weekdays") from error
        if any(type(day) is not int or not 0 <= day <= 6 for day in days):
            raise ValueError("weekdays must be integers from 0 (Monday) to 6 (Sunday)")
        self.days = tuple(sorted(set(days)))

        if self.due_date is not None and type(self.due_date) is not date:
            raise ValueError("due_date must be a date without a time")
        if self.due_date is not None and self.days:
            raise ValueError("a reminder cannot have both a due date and recurring days")
        if self.due_date is None and not self.days:
            raise ValueError("set a due date or at least one recurring weekday")

        if self.id is not None and (type(self.id) is not int or self.id < 1):
            raise ValueError("id must be a positive integer")
        if not isinstance(self.notes, str):
            raise ValueError("notes must be text")
        if self.category is not None:
            if not isinstance(self.category, str):
                raise ValueError("category must be text")
            self.category = self.category.strip() or None
        if not isinstance(self.enabled, bool):
            raise ValueError("enabled must be a boolean")

        for timestamp in (self.created_at, self.updated_at):
            if not isinstance(timestamp, datetime) or timestamp.utcoffset() is None:
                raise ValueError("created_at and updated_at must be timezone-aware")

    @property
    def repeats(self) -> bool:
        return bool(self.days)

    def next_occurrence(self, after: datetime) -> datetime | None:
        if not isinstance(after, datetime) or after.utcoffset() is not None:
            raise ValueError("after must be a local datetime without a timezone")
        if not self.enabled:
            return None

        if self.due_date is not None:
            occurrence = datetime.combine(self.due_date, self.time)
            return occurrence if occurrence > after else None

        for days_ahead in range(8):
            occurrence_date = after.date() + timedelta(days=days_ahead)
            occurrence = datetime.combine(occurrence_date, self.time)
            if occurrence_date.weekday() in self.days and occurrence > after:
                return occurrence
        return None