"""Stage C — summary emitter. See SPEC.md."""


def summarize(transformed):
    count = len(transformed)

    totals = [r["total"] for r in transformed if "total" in r]
    total_sum = round(sum(totals), 2) if totals else 0.0
    max_total = max(totals) if totals else None

    by_category = {}
    for r in transformed:
        if "category" in r:
            by_category[r["category"]] = by_category.get(r["category"], 0) + 1

    regions = sorted({r["region"] for r in transformed if "region" in r})

    tag_counts = {}
    for r in transformed:
        for tag in r.get("tags", []):
            tag_counts[tag] = tag_counts.get(tag, 0) + 1

    return {
        "count": count,
        "total_sum": total_sum,
        "by_category": by_category,
        "regions": regions,
        "max_total": max_total,
        "tag_counts": tag_counts,
    }
