"""Schema definition and validation for extracted data."""
from __future__ import annotations
from dataclasses import dataclass


@dataclass
class Field:
    name: str
    type: str = "string"  # string | number | integer | boolean | array
    description: str = ""
    required: bool = True


def validate(data: dict, schema: list[Field]) -> list[str]:
    """Return a list of human-readable validation errors (empty == valid)."""
    errors: list[str] = []
    for f in schema:
        if f.name not in data or data[f.name] in (None, ""):
            if f.required:
                errors.append(f"missing required field: {f.name}")
            continue
        v = data[f.name]
        if f.type in ("number", "integer") and not isinstance(v, (int, float)):
            errors.append(f"{f.name}: expected {f.type}, got {type(v).__name__}")
        if f.type == "boolean" and not isinstance(v, bool):
            errors.append(f"{f.name}: expected boolean, got {type(v).__name__}")
        if f.type == "array" and not isinstance(v, list):
            errors.append(f"{f.name}: expected array, got {type(v).__name__}")
    return errors
