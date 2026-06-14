import time


def fetch(source: dict) -> dict:
    """Simulate fetching a record from a source."""
    time.sleep(source.get("delay", 0))
    if "id" not in source:
        raise ValueError("source needs id")
    return {"id": source["id"], "payload": f"data-{source['id']}"}
