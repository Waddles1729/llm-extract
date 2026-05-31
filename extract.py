"""llm-extract — turn unstructured text into validated structured data."""
from __future__ import annotations
import json
import re

from schema import Field, validate
from providers import get_provider

PROMPT = """You extract structured data from text. Return ONLY a JSON object with these fields:
{fields}
Use null for fields you cannot find. Numbers must be JSON numbers, not strings.
---TEXT---
{text}"""


def build_prompt(text: str, schema: list[Field]) -> str:
    lines = "\n".join(f"- {f.name} ({f.type}): {f.description}" for f in schema)
    return PROMPT.format(fields=lines, text=text)


def _parse_json(s: str) -> dict:
    m = re.search(r"\{.*\}", s, re.S)
    return json.loads(m.group(0)) if m else {}


def extract(text: str, schema: list[Field], provider=None) -> dict:
    provider = provider or get_provider()
    raw = provider.complete(build_prompt(text, schema))
    data = _parse_json(raw)
    return {"data": data, "errors": validate(data, schema), "provider": provider.name}


if __name__ == "__main__":
    schema = [
        Field("email", "string", "contact email"),
        Field("phone", "string", "phone number", required=False),
        Field("amount", "number", "total amount in yen", required=False),
        Field("date", "string", "ISO date if present", required=False),
        Field("urgent", "boolean", "is the request urgent?"),
    ]
    text = open("examples/sample.txt", encoding="utf-8").read()
    print(json.dumps(extract(text, schema), ensure_ascii=False, indent=2))
