"""Flight Schedule Parser and Query Tool - command-line entry point.

Run from the project folder, for example:
    python flight_parser.py -i data/db.csv -a data/airports.txt
"""
import argparse
import csv
import json
import logging
import os
import sys

from csv_loader import parse_files
from validator import load_airports

# Plain ASCII, no spaces or underscores: they go into the response file name.
STUDENT_ID = "251ADC006"
FIRST_NAME = "Serhii"
LAST_NAME = "Voitov"

logger = logging.getLogger("flight_parser")
logger.setLevel(logging.INFO)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Validate flight CSV files and query the flights.")
    # required=True makes argparse itself reject "no source" and "two sources" with code 2.
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("-i", metavar="FILE", dest="input", help="parse one CSV file")
    source.add_argument("-d", metavar="FOLDER", dest="folder", help="parse every .csv file in a folder")
    source.add_argument("-j", metavar="FILE", dest="database", help="load an existing JSON database")
    parser.add_argument("-a", metavar="FILE", dest="airports", help="airport list (needed with -i and -d)")
    # No default here, so main() can tell whether -o was given at all.
    parser.add_argument("-o", metavar="FILE", dest="output", help="where to write the database (default: db.json)")
    return parser


def csv_paths(args: argparse.Namespace) -> list[str]:
    """The CSV files to parse: the -i file, or the .csv files of the -d folder in name order."""
    if args.input is not None:
        return [args.input]
    # isfile() skips sub-folders, even one that happens to be called something.csv.
    names = sorted(name for name in os.listdir(args.folder)
                   if name.endswith(".csv") and os.path.isfile(os.path.join(args.folder, name)))
    if not names:
        raise ValueError(f"no .csv files in folder {args.folder}")
    return [os.path.join(args.folder, name) for name in names]


def parse_csv(args: argparse.Namespace) -> list[dict]:
    """Parse the CSV input, write the database and errors.log, and return the database."""
    output = args.output or "db.json"
    log_path = os.path.join(os.path.dirname(output), "errors.log")

    handler = logging.FileHandler(log_path, mode="w", encoding="utf-8")
    handler.setFormatter(logging.Formatter(
        "%(asctime)s %(levelname)s %(message)s", datefmt="%Y-%m-%d %H:%M:%S"))
    logger.addHandler(handler)
    # The handler is removed in finally, also when a file is missing halfway.
    # The autograder calls main() many times in one process, and a handler
    # left behind would write this run's lines into the next run's log.
    try:
        airports = load_airports(args.airports)
        paths = csv_paths(args)
        records, errors = parse_files(paths, airports)
        for message in errors:
            logger.warning(message)
        logger.info("%d valid and %d invalid rows from %d file(s)", len(records), len(errors), len(paths))
        with open(output, "w", encoding="utf-8") as f:
            json.dump(records, f, indent=2)
        print(f"{len(records)} flights written to {output}, {len(errors)} errors in {log_path}")
        return records
    finally:
        logger.removeHandler(handler)
        handler.close()


def load_database(path: str) -> list[dict]:
    """Load a database written by an earlier run (-j)."""
    with open(path, encoding="utf-8") as f:
        db = json.load(f)
    if not isinstance(db, list) or not all(isinstance(record, dict) for record in db):
        raise ValueError(f"{path} is not a JSON array of objects")
    return db


def main(argv: list[str] | None = None) -> int:
    """Run the whole program and return the exit code (0, 1 or 2).

    argv is the argument list without the program name.
    None means use sys.argv[1:] (argparse does this for you).
    Do not call sys.exit() inside main(); return the code instead.
    """
    parser = build_parser()
    # argparse calls sys.exit() on a usage error (code 2) and after -h (code 0).
    # Catching SystemExit turns that into a return value, as main() must not exit.
    try:
        args = parser.parse_args(argv)
        if args.database is None and args.airports is None:
            parser.error("-a is required with -i and -d")
        if args.database is not None and args.output is not None:
            parser.error("-o can only be used with -i or -d")
    except SystemExit as exit_request:
        return exit_request.code

    # Expected runtime problems become one "Error:" line instead of a traceback.
    # OSError covers missing or unreadable files and folders. ValueError covers
    # bad JSON (json.JSONDecodeError), a file that is not UTF-8
    # (UnicodeDecodeError) and the wrong-shape errors raised above.
    try:
        if args.database is not None:
            db = load_database(args.database)
            print(f"{len(db)} flights loaded from {args.database}")
        else:
            db = parse_csv(args)
    except (OSError, ValueError, csv.Error) as error:
        print(f"Error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
