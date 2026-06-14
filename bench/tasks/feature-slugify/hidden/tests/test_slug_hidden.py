import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
from slug import slugify


def test_basic():
    assert slugify("Hello, World!") == "hello-world"


def test_transliteration():
    assert slugify("Müller & Söhne GmbH — Straße") == "mueller-soehne-gmbh-strasse"
    assert slugify("Ångström café piñata") == "angstroem-cafe-pinata"


def test_collapses_runs_and_strips():
    assert slugify("  --- a    b ---  ") == "a-b"


def test_cut_at_word_boundary():
    title = "one two three four five six seven eight nine ten eleven twelve"
    out = slugify(title, max_length=30)
    assert len(out) <= 30
    assert not out.endswith("-")
    assert out == "one-two-three-four-five-six"


def test_hard_cut_without_hyphen():
    assert slugify("a" * 100, max_length=10) == "a" * 10


def test_empty_and_symbol_only():
    assert slugify("") == ""
    assert slugify("!!! ***") == ""
