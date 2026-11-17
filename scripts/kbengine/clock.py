"""What day it is, for the engine's staleness and sweep logic (#205). Stdlib only.

today()     the date the engine treats as today: $KB_TODAY (YYYY-MM-DD) when set, else the real date.
            Called each time it is needed, never once at import, so a value set before a call is
            honoured by it. A malformed $KB_TODAY raises BadToday: silently falling back to the real
            date would let a test, or a person, believe a frozen clock was in force.
guard(f, *args)   f(*args), or the message on stderr and exit code 2 when $KB_TODAY is malformed.

Only the date logic reads this: a stamp's age, a sweep's age, a record's `date:`. A timestamp written
as a timestamp (kb-report's `generated` and ISO week, logs, backups, kb-prepare's `prepared:`) stays
on the real clock, as do transcript dates, which are UTC.
"""
import datetime, os, pathlib, re, sys

FORM = re.compile(r"\d{4}-\d{2}-\d{2}")


class BadToday(ValueError):
    """$KB_TODAY is set and is not a YYYY-MM-DD date."""


def today() -> datetime.date:
    raw = os.environ.get("KB_TODAY")
    if not raw:
        return datetime.date.today()
    try:
        if not FORM.fullmatch(raw):
            raise ValueError
        return datetime.date.fromisoformat(raw)
    except ValueError:
        raise BadToday(f"KB_TODAY={raw!r} is not a date: use YYYY-MM-DD, or unset it") from None


def guard(f, *args) -> int:
    try:
        return f(*args)
    except BadToday as e:
        print(f"{pathlib.Path(sys.argv[0]).name}: {e}", file=sys.stderr)
        return 2
