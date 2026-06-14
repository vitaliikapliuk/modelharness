"""Stage B — transformation engine. See SPEC.md. Operates on copies; input
records are never mutated."""

import copy


def _apply(rule, rec):
    rtype = rule["type"]

    if rtype == "rename":
        a, b = rule["from"], rule["to"]
        if a in rec:
            rec[b] = rec.pop(a)
    elif rtype == "default":
        f = rule["field"]
        if rec.get(f) is None:
            rec[f] = rule["value"]
    elif rtype == "scale":
        f = rule["field"]
        if f in rec:
            rec[f] = rec[f] * rule["by"]
    elif rtype == "round":
        f = rule["field"]
        if f in rec:
            rec[f] = round(rec[f], rule["ndigits"])
    elif rtype == "upper":
        f = rule["field"]
        if f in rec:
            rec[f] = rec[f].upper()
    elif rtype == "derive_total":
        q, p, t = rule["qty"], rule["price"], rule["to"]
        if q in rec and p in rec:
            rec[t] = rec[q] * rec[p]
    elif rtype == "tag":
        f, tag = rule["field"], rule["add"]
        lst = rec.get(f)
        if not isinstance(lst, list):
            lst = []
            rec[f] = lst
        if tag not in lst:
            lst.append(tag)
    elif rtype == "drop":
        rec.pop(rule["field"], None)
    else:
        raise ValueError("unknown rule type: %s" % rtype)


def transform_all(valid_records, rules):
    out = []
    for record in valid_records:
        rec = copy.deepcopy(record)
        for rule in rules:
            _apply(rule, rec)
        out.append(rec)
    return out
