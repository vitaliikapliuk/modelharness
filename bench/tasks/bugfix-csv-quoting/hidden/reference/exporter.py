import csv
import io


def export_rows(rows: list, columns: list) -> str:
    """Render rows (list of dicts) as CSV text with a header line."""
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=columns, extrasaction="ignore", lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({c: row.get(c, "") for c in columns})
    return buf.getvalue()
