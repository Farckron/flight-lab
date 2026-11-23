"""Running queries against the flight database."""
from validator import parse_datetime

RECORD_KEYS = ("flight_id", "origin", "destination", "departure_datetime", "arrival_datetime", "price")


def is_number(value) -> bool:
    # bool is a subclass of int in Python, so True would pass as 1 without this.
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def is_valid(query) -> bool:
    """True if every key of the query is allowed and has a value of the right type."""
    if not isinstance(query, dict):
        return False
    for key, value in query.items():
        if key in ("flight_id", "origin", "destination"):
            ok = isinstance(value, str)
        elif key in ("departure_datetime", "arrival_datetime"):
            ok = isinstance(value, str) and parse_datetime(value) is not None
        elif key in ("price", "min_price"):
            ok = is_number(value)
        elif key == "sort_by":
            ok = value in RECORD_KEYS
        elif key == "order":
            ok = value in ("asc", "desc") and "sort_by" in query
        elif key == "limit":
            ok = isinstance(value, int) and not isinstance(value, bool) and value >= 0
        else:
            ok = False      # unknown key
        if not ok:
            return False
    return True


def matches(flight: dict, query: dict) -> bool:
    """True if the flight passes every condition in the query (AND)."""
    for key in ("flight_id", "origin", "destination"):
        if key in query and flight[key] != query[key]:
            return False
    # Times in the YYYY-MM-DD HH:MM form sort as text in the same order as in
    # time, so plain string comparison is enough here.
    if "departure_datetime" in query and flight["departure_datetime"] < query["departure_datetime"]:
        return False
    if "arrival_datetime" in query and flight["arrival_datetime"] > query["arrival_datetime"]:
        return False
    if "price" in query and flight["price"] > query["price"]:
        return False
    if "min_price" in query and flight["price"] < query["min_price"]:
        return False
    return True


def run_query(db: list[dict], query: dict) -> dict:
    """Return one response entry for one query object.

    Valid query:   {"query": query, "matches": [...]}
    Invalid query: {"query": query, "error": "INVALID_QUERY", "matches": []}
    """
    if not is_valid(query):
        return {"query": query, "error": "INVALID_QUERY", "matches": []}

    found = [flight for flight in db if matches(flight, query)]
    if "sort_by" in query:
        # sorted() is stable, also with reverse=True, so flights with equal
        # values keep their database order in both directions.
        found = sorted(found, key=lambda flight: flight[query["sort_by"]],
                       reverse=query.get("order") == "desc")
    if "limit" in query:
        found = found[:query["limit"]]
    return {"query": query, "matches": found}


def run_queries(db: list[dict], queries: dict | list) -> list[dict]:
    """Accept one query object or a list of them; always return a list."""
    if isinstance(queries, dict):
        queries = [queries]
    return [run_query(db, query) for query in queries]
