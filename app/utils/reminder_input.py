from datetime import date, time


_WEEKDAYS = {
    "mon": 0,
    "monday": 0,
    "tue": 1,
    "tues": 1,
    "tuesday": 1,
    "wed": 2,
    "wednesday": 2,
    "thu": 3,
    "thur": 3,
    "thurs": 3,
    "thursday": 3,
    "fri": 4,
    "friday": 4,
    "sat": 5,
    "saturday": 5,
    "sun": 6,
    "sunday": 6,
}


def parse_local_time(value: str) -> time:
    try:
        parsed = time.fromisoformat(value.strip())
    except ValueError as error:
        raise ValueError("Enter a valid time in 24-hour format, such as 08:30.") from error
    if parsed.tzinfo is not None:
        raise ValueError("Enter a local time without a timezone.")
    return parsed


def parse_due_date(value: str) -> date:
    try:
        return date.fromisoformat(value.strip())
    except ValueError as error:
        raise ValueError("Enter a valid date in YYYY-MM-DD format.") from error


def parse_weekdays(value: str) -> tuple[int, ...]:
    tokens = [token.strip().casefold() for token in value.split(",") if token.strip()]
    if not tokens:
        raise ValueError("Enter at least one weekday, such as Mon, Wed, Fri.")

    unknown = [token for token in tokens if token not in _WEEKDAYS]
    if unknown:
        raise ValueError(f"Unknown weekday: {unknown[0]}.")
    return tuple(sorted({_WEEKDAYS[token] for token in tokens}))