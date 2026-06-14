"""Stage A — config-driven input validation DSL. See SPEC.md."""

import re

_PY_TYPES = {"int": int, "float": float, "str": str, "list": list}


def _present(record, field):
    return field in record and record[field] is not None


def _check(rule, record):
    """Return the error code for a single rule on a record, or None if it passes."""
    rtype = rule["type"]
    field = rule.get("field")

    if rtype == "required":
        return None if _present(record, field) else "required:%s" % field

    # All other rules are skipped when the field is absent/None.
    if not _present(record, field):
        return None
    value = record[field]

    if rtype == "type":
        py = _PY_TYPES[rule["py"]]
        ok = isinstance(value, py)
        if py is int and isinstance(value, bool):
            ok = False  # bool is not a valid int
        return None if ok else "type:%s" % field
    if rtype == "min":
        return None if value >= rule["value"] else "min:%s" % field
    if rtype == "max":
        return None if value <= rule["value"] else "max:%s" % field
    if rtype == "non_empty":
        return None if len(value) > 0 else "non_empty:%s" % field
    if rtype == "enum":
        return None if value in rule["allowed"] else "enum:%s" % field
    if rtype == "regex":
        return None if re.fullmatch(rule["pattern"], value) else "regex:%s" % field
    if rtype == "max_len":
        return None if len(value) <= rule["value"] else "max_len:%s" % field
    if rtype == "positive":
        return None if value > 0 else "positive:%s" % field
    if rtype == "in_set":
        allowed = set(rule["set"])
        if isinstance(value, list):
            ok = all(v in allowed for v in value)
        else:
            ok = value in allowed
        return None if ok else "in_set:%s" % field
    raise ValueError("unknown rule type: %s" % rtype)


def validate_record(record, rules):
    """Apply rules to one record. Return (is_valid, sorted unique error codes)."""
    errors = set()
    for rule in rules:
        code = _check(rule, record)
        if code is not None:
            errors.add(code)
    sorted_errors = sorted(errors)
    return (len(sorted_errors) == 0, sorted_errors)


def validate_all(records, rules):
    """Split records into valid / rejected, preserving input order."""
    valid = []
    rejected = []
    for record in records:
        ok, errors = validate_record(record, rules)
        if ok:
            valid.append(record)
        else:
            rejected.append({"id": record.get("id"), "errors": errors})
    return {"valid": valid, "rejected": rejected}
