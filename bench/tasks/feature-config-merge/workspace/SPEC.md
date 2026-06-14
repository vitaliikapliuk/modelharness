# load_config spec

`load_config(defaults: dict, file_path: str | None, env: dict, env_prefix: str) -> dict`

Precedence (lowest to highest): defaults < JSON file < env.

- `defaults` is a (possibly nested) dict; never mutated.
- If `file_path` is not None, it is a JSON file containing an object; its keys
  deep-merge over defaults (nested dicts merge recursively; non-dict values replace).
- `env` maps strings to strings. Keys starting with `env_prefix` apply on top:
  strip the prefix, lowercase the rest, split on `__` (double underscore) for
  nesting. `APP_DB__HOST=x` with prefix `APP_` sets result["db"]["host"] = "x".
- Env values are parsed: "true"/"false" (case-insensitive) -> bool; otherwise int()
  if possible; otherwise the raw string.
- Missing file (file_path set but file doesn't exist) raises FileNotFoundError.
