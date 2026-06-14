import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[2]))
import json
import pytest
from config import load_config

DEFAULTS = {"db": {"host": "localhost", "port": 5432}, "debug": False, "name": "app"}


def test_defaults_only():
    assert load_config(DEFAULTS, None, {}, "APP_") == DEFAULTS


def test_defaults_not_mutated(tmp_path):
    f = tmp_path / "c.json"
    f.write_text(json.dumps({"db": {"host": "filehost"}}))
    snapshot = json.loads(json.dumps(DEFAULTS))
    load_config(DEFAULTS, str(f), {"APP_DEBUG": "true"}, "APP_")
    assert DEFAULTS == snapshot


def test_file_deep_merges(tmp_path):
    f = tmp_path / "c.json"
    f.write_text(json.dumps({"db": {"host": "filehost"}}))
    out = load_config(DEFAULTS, str(f), {}, "APP_")
    assert out["db"]["host"] == "filehost"
    assert out["db"]["port"] == 5432


def test_env_overrides_file_and_parses_types(tmp_path):
    f = tmp_path / "c.json"
    f.write_text(json.dumps({"db": {"port": 1111}}))
    env = {"APP_DB__PORT": "2222", "APP_DEBUG": "TRUE", "APP_NAME": "prod-app", "OTHER_X": "ignored"}
    out = load_config(DEFAULTS, str(f), env, "APP_")
    assert out["db"]["port"] == 2222
    assert out["debug"] is True
    assert out["name"] == "prod-app"
    assert "x" not in out


def test_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        load_config(DEFAULTS, "/nonexistent/path.json", {}, "APP_")
