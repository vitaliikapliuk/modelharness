"""Pipeline — wires Stage A -> B -> C end to end. See SPEC.md."""

from stage_a import validate_all
from stage_b import transform_all
from stage_c import summarize


def run_pipeline(records, config):
    a = validate_all(records, config["validation"])
    transformed = transform_all(a["valid"], config["transform"])
    summary = summarize(transformed)
    return {"summary": summary, "rejected": a["rejected"]}
