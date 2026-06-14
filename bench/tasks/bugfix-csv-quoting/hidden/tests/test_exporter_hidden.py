import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
import csv, io
from exporter import export_rows

COLUMNS = ["name", "note"]
ROWS = [
    {"name": "a,b", "note": "comma"},
    {"name": 'say "hi"', "note": "quotes"},
    {"name": "line1\nline2", "note": "newline"},
    {"name": "plain", "note": ""},
]


def test_round_trip_through_stdlib_csv():
    out = export_rows(ROWS, COLUMNS)
    parsed = list(csv.DictReader(io.StringIO(out)))
    assert len(parsed) == len(ROWS)
    for got, want in zip(parsed, ROWS):
        assert got["name"] == want["name"]
        assert got["note"] == want["note"]
