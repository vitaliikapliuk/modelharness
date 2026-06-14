import asyncio

from fetcher import fetch
from processor import process


async def run_all(sources: list) -> list:
    async def one(source):
        return await process(await fetch(source))

    return list(await asyncio.gather(*(one(s) for s in sources)))
