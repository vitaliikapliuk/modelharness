def export_rows(rows: list, columns: list) -> str:
    """Render rows (list of dicts) as CSV text with a header line."""
    lines = [",".join(columns)]
    for row in rows:
        lines.append(",".join(str(row.get(c, "")) for c in columns))
    return "\n".join(lines) + "\n"
