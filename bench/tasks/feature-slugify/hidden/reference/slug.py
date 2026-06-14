import re

_TRANSLIT = {
    "ä": "ae", "ö": "oe", "ü": "ue", "ß": "ss", "å": "a",
    "é": "e", "è": "e", "ñ": "n",
    "Ä": "Ae", "Ö": "Oe", "Ü": "Ue", "Å": "A", "É": "E", "È": "E", "Ñ": "N",
}


def slugify(title: str, max_length: int = 60) -> str:
    for src, dst in _TRANSLIT.items():
        title = title.replace(src, dst)
    title = title.lower()
    title = re.sub(r"[^a-z0-9]+", "-", title).strip("-")
    if len(title) > max_length:
        head = title[:max_length]
        if "-" in head:
            head = head[: head.rfind("-")]
        title = head.rstrip("-")
    return title
