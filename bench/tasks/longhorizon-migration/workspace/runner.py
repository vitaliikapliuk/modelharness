from fetcher import fetch
from processor import process


def run_all(sources: list) -> list:
    results = []
    for source in sources:
        results.append(process(fetch(source)))
    return results
