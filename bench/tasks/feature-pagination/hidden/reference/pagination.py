import base64
import json

from store import ItemStore


def paginate(store: ItemStore, cursor, limit: int) -> dict:
    if not 1 <= limit <= 100:
        raise ValueError("limit must be 1..100")
    after_id = -1
    if cursor is not None:
        try:
            payload = json.loads(base64.urlsafe_b64decode(cursor.encode()).decode())
            after_id = int(payload["after_id"])
        except Exception as exc:
            raise ValueError("invalid cursor") from exc
    ordered = sorted(store.all_items(), key=lambda i: i["id"])
    remaining = [i for i in ordered if i["id"] > after_id]
    page = remaining[:limit]
    next_cursor = None
    if len(remaining) > limit:
        next_cursor = base64.urlsafe_b64encode(
            json.dumps({"after_id": page[-1]["id"]}).encode()
        ).decode()
    return {"items": page, "next_cursor": next_cursor}
