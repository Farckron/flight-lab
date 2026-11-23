"""Reading CSV files into flight records and error messages."""
import csv
import os

from validator import to_record, validate_row


def parse_files(paths: list[str], airports: set[str]) -> tuple[list[dict], list[str]]:
    """Process the CSV files in the order given.

    Return (records, errors):
      records - valid flight records, in input order
      errors  - one message per invalid row, in input order, formatted as
                "<file name>:<line number>: <ERROR_CODE> | <free text>"
                (base file name only, no timestamp or level, no newline)

    Also performs the DUPLICATE_FLIGHT check across all the files.
    Does not write any files and does not log anything itself.
    """
    records = []
    errors = []
    # (flight_id, departure_datetime) of every valid row so far. It is shared
    # by all the files, so a flight repeated in a later file is caught too.
    seen = set()

    for path in paths:
        name = os.path.basename(path)
        with open(path, encoding="utf-8") as f:
            # The file is read line by line instead of giving the whole file
            # to csv.reader, so that the line number is always the physical
            # line in the file, blank lines and comments included.
            for number, line in enumerate(f, start=1):
                if number == 1 or line.strip() == "" or line.strip().startswith("#"):
                    continue
                fields = next(csv.reader([line]))
                text = line.rstrip("\r\n")

                code = validate_row(fields, airports)
                if code is None:
                    record = to_record(fields)
                    key = (record["flight_id"], record["departure_datetime"])
                    if key in seen:
                        code = "DUPLICATE_FLIGHT"
                    else:
                        seen.add(key)
                        records.append(record)

                if code is not None:
                    errors.append(f"{name}:{number}: {code} | {text}")

    return records, errors
