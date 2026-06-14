# Grading integrity

Every task is graded by a hidden, binary test suite the agent never sees
(`tasks/<task>/hidden/`). There is no LLM judge. Each task also ships a reference
solution, and `scripts/selfcheck.sh --all` proves every task fails on the
untouched workspace and passes on its reference — so a "pass" means the suite is
real and the task is solvable, not that the grader is lenient.

## Hand-audited failures

Every non-passing run in the capture was inspected by hand before being counted.
The only quality failure in the 408-run dataset (bare Haiku 4.5 on
`continuity-staged-build`, one rep) was confirmed to be a genuine
out-of-turns failure, not a grading artifact.

## Two grader corrections made during capture

While capturing results we found two cases where the hidden grader rejected
*correct* solutions. Both were corrected, and both corrections are in the
**models' favor** (they let valid work pass that the original check wrongly
failed). Neither weakens what the task verifies. Both are in
`refactor-extract-storage`, whose structural test was over-specified.

### 1. Accept `from ... import` delegation style

The structural check required a literal `import service` / `import storage`
substring to prove `app.py` delegates to the extracted layers. Models that
delegated correctly with `from service import create_app` were wrongly failed.
Fix: parse the AST and accept both `Import` and `ImportFrom` of the new modules.

```python
# before: substring match — rejects valid from-imports
assert "import service" in src or "import storage" in src

# after: AST-based — accepts any valid import of the new layers
tree = ast.parse(src)
imported = {node.module for node in ast.walk(tree) if isinstance(node, ast.ImportFrom)} \
         | {alias.name for node in ast.walk(tree) if isinstance(node, ast.Import)
            for alias in node.names}
assert imported & {"service", "storage"}, "app.py must delegate to the new layers"
```

### 2. Exempt dunder metadata from the container-state check

The same task forbids module-level mutable state in `app.py` after the refactor.
The check flagged every module-level assignment — including `__all__`, which is
metadata, not state. Solutions that correctly declared `__all__` were wrongly
failed. Fix: skip dunder assignments.

```python
# Dunder metadata assignments (__all__, __version__, ...) are not state.
targets = node.targets if isinstance(node, ast.Assign) else [node.target]
if all(isinstance(t, ast.Name) and t.id.startswith("__") and t.id.endswith("__") for t in targets):
    continue
```

Both fixes are reproducible: they live in
`tasks/refactor-extract-storage/hidden/tests/test_structure.py`, and
`scripts/selfcheck.sh refactor-extract-storage` still proves the task fails
untouched and passes on the reference solution.
