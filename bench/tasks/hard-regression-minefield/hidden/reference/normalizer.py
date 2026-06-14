"""ID normalization utilities."""

_SEPARATORS = set("-_. ")


def normalize_id(raw: str) -> str:
    """Return the canonical lowercase id, stripped of separators (-_. and spaces).

    For example ``normalize_id("Foo-Bar_1")`` is the canonical id for that record:
    lowercase, with every separator character removed. Two raw ids that differ only
    in case or separators share the same canonical id.
    """
    chars = []
    for ch in raw:
        if ch in _SEPARATORS:
            continue
        chars.append(ch.lower())
    return "".join(chars)
