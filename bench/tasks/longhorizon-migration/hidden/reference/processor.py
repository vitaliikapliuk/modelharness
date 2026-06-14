async def process(record: dict) -> dict:
    """Enrich a fetched record."""
    return {**record, "processed": True, "length": len(record["payload"])}
