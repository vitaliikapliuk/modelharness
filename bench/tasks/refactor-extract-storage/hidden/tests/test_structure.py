import ast
import sys, pathlib
ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))


def _module_level_container_bindings(path):
    tree = ast.parse(path.read_text())
    bad = []
    for node in tree.body:
        if isinstance(node, (ast.Assign, ast.AnnAssign)):
            # Dunder metadata assignments (__all__, __version__, ...) are not state.
            targets = node.targets if isinstance(node, ast.Assign) else [node.target]
            if all(isinstance(t, ast.Name) and t.id.startswith("__") and t.id.endswith("__") for t in targets):
                continue
            for sub in ast.walk(node):
                if isinstance(sub, (ast.Dict, ast.List, ast.Set, ast.DictComp, ast.ListComp, ast.SetComp)):
                    bad.append(ast.dump(sub)[:40])
                if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name) and sub.func.id in ("dict", "list", "set"):
                    bad.append(sub.func.id + "()")
    return bad


def test_storage_module_exists_with_class():
    import storage
    assert isinstance(storage.Storage, type)


def test_service_module_exists():
    import service  # noqa: F401


def test_app_is_thin():
    src = (ROOT / "app.py").read_text()
    code_lines = [l for l in src.splitlines() if l.strip() and not l.strip().startswith("#")]
    assert len(code_lines) <= 40, f"app.py has {len(code_lines)} code lines (max 40)"
    tree = ast.parse(src)
    imported = {
        name
        for node in ast.walk(tree)
        if isinstance(node, ast.ImportFrom)
        for name in [node.module]
    } | {
        alias.name
        for node in ast.walk(tree)
        if isinstance(node, ast.Import)
        for alias in node.names
    }
    assert imported & {"service", "storage"}, "app.py must delegate to the new layers"
    assert _module_level_container_bindings(ROOT / "app.py") == [], "app.py must not own container state"


def test_service_does_not_own_container_state():
    assert _module_level_container_bindings(ROOT / "service.py") == [], "state belongs in storage.Storage"
