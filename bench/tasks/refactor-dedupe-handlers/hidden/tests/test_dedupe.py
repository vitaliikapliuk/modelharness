import pathlib

ROOT = pathlib.Path(__file__).resolve().parents[2]


def test_validation_block_exists_at_most_once():
    src = (ROOT / "handlers.py").read_text()
    normalized = src.replace("'", '"')
    assert normalized.count("# shared-validation-block") <= 1
    assert normalized.count('"invalid id"') <= 1, "validation literals must not be duplicated"
    assert normalized.count('"not found"') <= 1
    assert normalized.count('"inactive"') <= 1
