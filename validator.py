"""Row validation: airport list loading, single-row checks, record building."""
import math
import re
from datetime import datetime

# The patterns use [A-Za-z0-9] and [0-9] instead of str.isalnum(), str.isupper()
# or \d, because those also accept non-ASCII letters and digits (Ā, é, ٣).
FLIGHT_ID = re.compile(r"[A-Za-z0-9]{2,8}")
AIRPORT = re.compile(r"[A-Z]{3}")
DATETIME = re.compile(r"[0-9]{4}-[0-9]{2}-[0-9]{2} [0-9]{2}:[0-9]{2}")
DATETIME_FORMAT = "%Y-%m-%d %H:%M"


def load_airports(path: str) -> set[str]:
    """Read an airport list file and return the set of codes.

    One code per line. Strip whitespace; skip blank lines and lines
    starting with '#'.
    """
    codes = set()
    with open(path, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                codes.add(line)
    return codes


def parse_datetime(text: str) -> datetime | None:
    """Return the datetime for text in the exact YYYY-MM-DD HH:MM form, else None.

    strptime() alone is not enough: it also accepts "2025-1-5 9:3". So the
    regex checks the shape first (zero-padded, one space), and strptime then
    checks that the date is real (no month 13, no 25:00, no 30 February).
    """
    if not DATETIME.fullmatch(text):
        return None
    try:
        return datetime.strptime(text, DATETIME_FORMAT)
    except ValueError:
        return None


def validate_row(fields: list[str], airports: set[str]) -> str | None:
    """Check one CSV row (fields as returned by csv.reader, not yet stripped).

    Return None if the row is valid, otherwise the error code of the
    FIRST failing check (checks 1-11 in the specification, in order).
    Does not check for duplicates.
    """
    if len(fields) != 6:
        return "WRONG_FIELD_COUNT"
    fields = [field.strip() for field in fields]
    if "" in fields:
        return "MISSING_FIELD"
    flight_id, origin, destination, departure, arrival, price = fields

    if not FLIGHT_ID.fullmatch(flight_id):
        return "INVALID_FLIGHT_ID"
    if not AIRPORT.fullmatch(origin) or origin not in airports:
        return "INVALID_ORIGIN"
    if not AIRPORT.fullmatch(destination) or destination not in airports:
        return "INVALID_DESTINATION"
    if origin == destination:
        return "SAME_ORIGIN_DESTINATION"

    departure_time = parse_datetime(departure)
    if departure_time is None:
        return "INVALID_DEPARTURE"
    arrival_time = parse_datetime(arrival)
    if arrival_time is None:
        return "INVALID_ARRIVAL"
    if arrival_time <= departure_time:
        return "ARRIVAL_NOT_AFTER_DEPARTURE"

    # float() accepts "nan" and "inf", so they need their own check. It comes
    # before the sign check, so "-inf" is INVALID_PRICE and not NON_POSITIVE_PRICE.
    try:
        value = float(price)
    except ValueError:
        return "INVALID_PRICE"
    if not math.isfinite(value):
        return "INVALID_PRICE"
    if value <= 0:
        return "NON_POSITIVE_PRICE"
    return None


def to_record(fields: list[str]) -> dict:
    """Turn a valid row into a flight record dictionary.

    Keys: flight_id, origin, destination, departure_datetime,
    arrival_datetime (stripped strings) and price (float).
    """
    flight_id, origin, destination, departure, arrival, price = [field.strip() for field in fields]
    return {
        "flight_id": flight_id,
        "origin": origin,
        "destination": destination,
        "departure_datetime": departure,
        "arrival_datetime": arrival,
        "price": float(price),
    }
