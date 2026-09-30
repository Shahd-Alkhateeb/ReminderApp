from datetime import date, datetime, time, timezone

import pytest

from app.models.reminder import Reminder


def test_one_time_reminder_normalizes_text_and_finds_occurrence():
    reminder = Reminder(title="  Medication  ", time=time(9), due_date=date(2026, 10, 1))

    assert reminder.title == "Medication"
    assert not reminder.repeats
    assert reminder.next_occurrence(datetime(2026, 10, 1, 8)) == datetime(2026, 10, 1, 9)


def test_one_time_reminder_has_no_occurrence_after_its_scheduled_time():
    reminder = Reminder(title="Dose", time=time(9), due_date=date(2026, 10, 1))

    assert reminder.next_occurrence(datetime(2026, 10, 1, 9)) is None


def test_recurring_days_are_sorted_and_deduplicated():
    reminder = Reminder(title="Walk", time=time(8), days=(4, 0, 4))

    assert reminder.days == (0, 4)
    assert reminder.repeats


def test_recurring_reminder_skips_today_when_time_has_passed():
    reminder = Reminder(title="Medication", time=time(8), days=(2,))

    assert reminder.next_occurrence(datetime(2026, 9, 30, 8)) == datetime(2026, 10, 7, 8)


def test_recurring_reminder_finds_next_weekday_across_week_boundary():
    reminder = Reminder(title="Check-in", time=time(9), days=(0,))

    assert reminder.next_occurrence(datetime(2026, 10, 2, 10)) == datetime(2026, 10, 5, 9)


def test_disabled_reminder_has_no_occurrence():
    reminder = Reminder(title="Dose", time=time(9), due_date=date(2026, 10, 1), enabled=False)

    assert reminder.next_occurrence(datetime(2026, 9, 30, 8)) is None


@pytest.mark.parametrize(
    "values",
    [
        {"title": "  ", "time": time(9), "due_date": date(2026, 10, 1)},
        {"title": "Dose", "time": time(9)},
        {"title": "Dose", "time": time(9), "due_date": date(2026, 10, 1), "days": (0,)},
        {"title": "Dose", "time": time(9), "days": (7,)},
    ],
)
def test_invalid_reminders_are_rejected(values):
    with pytest.raises(ValueError):
        Reminder(**values)


def test_next_occurrence_requires_local_naive_datetime():
    reminder = Reminder(title="Dose", time=time(9), due_date=date(2026, 10, 1))

    with pytest.raises(ValueError, match="local datetime"):
        reminder.next_occurrence(datetime(2026, 9, 30, 8, tzinfo=timezone.utc))