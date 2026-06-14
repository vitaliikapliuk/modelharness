# paginate spec

`paginate(store: ItemStore, cursor: str | None, limit: int) -> dict`

Returns `{"items": [...], "next_cursor": str | None}`.

- Ordering: ascending by item "id" (stable regardless of insertion order).
- `limit` must be 1..100; otherwise raise ValueError.
- `cursor=None` starts from the beginning.
- `next_cursor` is an OPAQUE string (base64 of internal state is fine) that, when
  passed back, returns the next page with no overlap and no gaps — even if new items
  with HIGHER ids were appended between calls. `next_cursor` is None on the last page.
- An invalid/corrupt cursor raises ValueError.
