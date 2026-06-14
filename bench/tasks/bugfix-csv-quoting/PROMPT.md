This CSV exporter corrupts output when field values contain commas, double quotes, or
newlines — downstream parsers see broken rows. Fix `exporter.py` so its output is
valid RFC-4180-style CSV that round-trips through any standard CSV parser. Keep the
public function signature `export_rows(rows: list[dict], columns: list[str]) -> str`.
`test_exporter_basic.py` must keep passing.

Work fully autonomously: do not ask questions; make reasonable assumptions and note
them. You are done only when the stated success criteria hold. Do not modify or
delete existing tests unless the task says so.
