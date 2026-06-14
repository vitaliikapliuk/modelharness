import copy
import json


def _deep_merge(base: dict, over: dict) -> dict:
    out = dict(base)
    for k, v in over.items():
        if isinstance(v, dict) and isinstance(out.get(k), dict):
            out[k] = _deep_merge(out[k], v)
        else:
            out[k] = v
    return out


def _parse(value: str):
    if value.lower() == "true":
        return True
    if value.lower() == "false":
        return False
    try:
        return int(value)
    except ValueError:
        return value


def load_config(defaults, file_path, env, env_prefix):
    result = copy.deepcopy(defaults)
    if file_path is not None:
        with open(file_path) as f:
            result = _deep_merge(result, json.load(f))
    for key, raw in env.items():
        if not key.startswith(env_prefix):
            continue
        path = key[len(env_prefix):].lower().split("__")
        node = result
        for part in path[:-1]:
            node = node.setdefault(part, {})
        node[path[-1]] = _parse(raw)
    return result
