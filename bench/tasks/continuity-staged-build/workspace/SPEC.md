# Staged data tool — specification

A three-stage, config-driven pipeline that validates raw records, transforms the
valid ones, and emits a summary. Implement it in Python (3.11+, stdlib only) across
these modules, which you create:

- `stage_a.py` — input-validation DSL (Stage A)
- `stage_b.py` — transformation engine (Stage B)
- `stage_c.py` — summary emitter (Stage C)
- `pipeline.py` — wires A -> B -> C end to end

The **public function signatures and their externally observable inputs/outputs are
fixed by this spec** and are exercised by an automated grader. The internal data
shapes that flow between stages are yours to design, as long as the public behavior
below holds exactly.

## Records

A raw record is a `dict`. Fields referenced by the examples:
`id` (str), `amount` (number), `qty` (int), `category` (str), `region` (str),
`status` (str), `tags` (list[str]).

---

## Stage A — input validation (`stage_a.py`)

```python
def validate_record(record: dict, rules: list[dict]) -> tuple[bool, list[str]]:
    """Apply rules to one record. Return (is_valid, sorted_list_of_error_codes)."""

def validate_all(records: list[dict], rules: list[dict]) -> dict:
    """Return {"valid": [records that passed], "rejected": [{"id":..., "errors":[...]}, ...]}.
    'valid' preserves input order. 'rejected' preserves input order and lists the
    error codes from validate_record for each failing record."""
```

A rule is a dict with a `"type"` and parameters. Each rule, when violated, contributes
the error code named below. `validate_record` returns error codes **sorted
ascending, de-duplicated**. The ten rule types:

1. `{"type": "required", "field": F}` — error `"required:F"` if `F` missing or `None`.
2. `{"type": "type", "field": F, "py": "int|float|str|list"}` — error `"type:F"` if
   present and not an instance of that Python type. (`bool` is NOT a valid `int`.)
3. `{"type": "min", "field": F, "value": V}` — error `"min:F"` if present and `< V`.
4. `{"type": "max", "field": F, "value": V}` — error `"max:F"` if present and `> V`.
5. `{"type": "non_empty", "field": F}` — error `"non_empty:F"` if present and the
   value has length 0 (string or list).
6. `{"type": "enum", "field": F, "allowed": [...]}` — error `"enum:F"` if present and
   not in the allowed list.
7. `{"type": "regex", "field": F, "pattern": P}` — error `"regex:F"` if present and
   `re.fullmatch(P, value)` is None.
8. `{"type": "max_len", "field": F, "value": N}` — error `"max_len:F"` if present and
   `len(value) > N`.
9. `{"type": "positive", "field": F}` — error `"positive:F"` if present and `<= 0`.
10. `{"type": "in_set", "field": F, "set": [...]}` — error `"in_set:F"` if present and
    not a subset relation: for a list-valued field, every element must be in `set`;
    for a scalar field, the value must be in `set`. (Same code regardless.)

Rules whose `field` is absent from the record are skipped **unless** the rule type is
`required`. A record is valid iff it produces zero error codes.

### Stage A worked example

```python
rules = [
  {"type": "required", "field": "id"},
  {"type": "type", "field": "qty", "py": "int"},
  {"type": "positive", "field": "qty"},
  {"type": "enum", "field": "status", "allowed": ["new", "paid", "void"]},
]
validate_record({"id": "r1", "qty": 3, "status": "paid"}, rules)   # -> (True, [])
validate_record({"qty": -1, "status": "x"}, rules)
#   -> (False, ["enum:status", "positive:qty", "required:id"])
validate_record({"id": "r2", "qty": True, "status": "new"}, rules)
#   -> (False, ["type:qty"])     # bool is not a valid int
```

---

## Stage B — transformation engine (`stage_b.py`)

```python
def transform_all(valid_records: list[dict], rules: list[dict]) -> list[dict]:
    """Apply transformation rules in order to each valid record; return new records
    (do not mutate inputs). Order of records is preserved."""
```

Rules are applied **in list order**, each to every record. The eight rule types:

1. `{"type": "rename", "from": A, "to": B}` — move field `A` to `B` (drop `A`). No-op
   if `A` absent.
2. `{"type": "default", "field": F, "value": V}` — set `F` to `V` only if `F` is
   missing or `None`.
3. `{"type": "scale", "field": F, "by": K}` — multiply numeric `F` by `K`. No-op if
   `F` absent.
4. `{"type": "round", "field": F, "ndigits": N}` — round numeric `F` to `N` digits
   using Python's built-in `round`. No-op if `F` absent.
5. `{"type": "upper", "field": F}` — uppercase string `F`. No-op if `F` absent.
6. `{"type": "derive_total", "qty": Q, "price": P, "to": T}` — set `T = record[Q] *
   record[P]` (both must be present, else no-op).
7. `{"type": "tag", "field": F, "add": TAG}` — append `TAG` to list field `F`,
   creating the list if `F` is absent. Do not add a duplicate if already present.
8. `{"type": "drop", "field": F}` — remove field `F` if present.

### Stage B worked example

```python
rules = [
  {"type": "default", "field": "qty", "value": 1},
  {"type": "derive_total", "qty": "qty", "price": "price", "to": "total"},
  {"type": "scale", "field": "total", "by": 1.1},
  {"type": "round", "field": "total", "ndigits": 2},
  {"type": "upper", "field": "region"},
  {"type": "tag", "field": "tags", "add": "processed"},
]
transform_all([{"price": 10.0, "qty": 2, "region": "us", "tags": ["a"]}], rules)
# -> [{"price": 10.0, "qty": 2, "region": "US", "tags": ["a", "processed"],
#      "total": 22.0}]
```

---

## Stage C — summary emitter (`stage_c.py`)

```python
def summarize(transformed: list[dict]) -> dict:
    """Emit a summary over transformed records."""
```

The summary is a dict with these six keys:

1. `"count"` — number of records.
2. `"total_sum"` — sum of each record's `total` field (0.0 if none have it), rounded
   to 2 digits.
3. `"by_category"` — dict mapping each distinct `category` value to how many records
   have it (records lacking `category` are ignored).
4. `"regions"` — sorted list of the distinct `region` values present.
5. `"max_total"` — the largest `total` among records that have one, or `None` if no
   record has a `total`.
6. `"tag_counts"` — dict mapping each tag (across all records' `tags` lists) to the
   number of records whose `tags` contain it.

---

## Pipeline (`pipeline.py`)

```python
def run_pipeline(records: list[dict], config: dict) -> dict:
    """config = {"validation": [A-rules], "transform": [B-rules]}.
    Validate with Stage A, transform the VALID records with Stage B, summarize with
    Stage C. Return:
      {"summary": <Stage C output>, "rejected": <Stage A 'rejected' list>}."""
```

## Success criteria

- All three stages implemented exactly to the signatures and behavior above.
- The full pipeline works end to end (`run_pipeline`).
- stdlib only; deterministic.
