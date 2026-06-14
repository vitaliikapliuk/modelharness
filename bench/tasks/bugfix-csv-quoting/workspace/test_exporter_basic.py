from exporter import export_rows


def test_simple_rows():
    out = export_rows([{"a": "1", "b": "2"}], ["a", "b"])
    assert out.splitlines()[0] == "a,b"
    assert out.splitlines()[1] == "1,2"
