from datetime import date, time

import pytest

from app.utils.reminder_input import parse_due_date, parse_local_time, parse_weekdays


def test_parse_local_time_accepts_24_hour_time():
    assert parse_local_time(" 20:15 ") == time(20, 15)


@pytest.mark.parametrize("value", ["25:00", "not a time", "08:30+02:00"])
def test_parse_local_time_rejects_invalid_or_zoned_time(value):
    with pytest.raises(ValueError):
        parse_local_time(value)


def test_parse_due_date_accepts_iso_date():
    assert parse_due_date("2026-10-01") == date(2026, 10, 1)


def test_parse_due_date_rejects_invalid_date():
    with pytest.raises(ValueError, match="YYYY-MM-DD"):
        parse_due_date("2026-02-30")


def test_parse_weekdays_accepts_names_and_deduplicates():
    assert parse_weekdays("Fri, Mon, friday") == (0, 4)


def test_parse_weekdays_requires_known_day_names():
    with pytest.raises(ValueError, match="Unknown weekday"):
        parse_weekdays("Funday")