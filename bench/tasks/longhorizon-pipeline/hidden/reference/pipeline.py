import math


def parse_line(line: str):
    parts = line.split()
    if len(parts) != 5:
        return None
    ts, method, path, status_s, dur_s = parts
    if not dur_s.endswith("ms"):
        return None
    try:
        status = int(status_s)
        ms = int(dur_s[:-2])
    except ValueError:
        return None
    return {"ts": ts, "method": method, "path": path, "status": status, "ms": ms}


def aggregate(lines):
    by_path = {}
    for line in lines:
        rec = parse_line(line)
        if rec is None:
            continue
        bucket = by_path.setdefault(rec["path"], {"count": 0, "errors": 0, "durations": []})
        bucket["count"] += 1
        if rec["status"] >= 500:
            bucket["errors"] += 1
        bucket["durations"].append(rec["ms"])
    out = {}
    for path, b in by_path.items():
        durations = sorted(b["durations"])
        p95 = durations[math.ceil(0.95 * len(durations)) - 1]
        out[path] = {"count": b["count"], "errors": b["errors"], "p95_ms": p95}
    return out


def render_report(agg: dict) -> str:
    rows = sorted(agg.items(), key=lambda kv: (-kv[1]["count"], kv[0]))
    lines = ["| path | count | errors | p95_ms |", "|---|---|---|---|"]
    for path, b in rows:
        lines.append(f"| {path} | {b['count']} | {b['errors']} | {b['p95_ms']} |")
    return "\n".join(lines)
