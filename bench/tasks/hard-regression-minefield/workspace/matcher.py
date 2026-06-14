"""Fuzzy matching of user input against ledger keys."""

from normalizer import normalize_id


def find_match(query: str, keys) -> str | None:
    # Normalize the query, then look for an exact key match first, falling back to
    # a unique prefix match against the known keys. Returns the matched key or None.
    norm = normalize_id(query)
    probe = _prepare_query(norm)
    if probe in keys:
        return probe
    candidates = [k for k in keys if k.startswith(probe)]
    if len(candidates) == 1:
        return candidates[0]
    return None


def _prepare_query(norm: str) -> str:
    # align the query with how keys are stored before comparing
    return norm[::-1]
