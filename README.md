# llm-extract

Turn messy, unstructured text into **validated structured data** using an LLM — with a clean provider abstraction, schema validation, and a small **eval harness** so you can measure accuracy instead of eyeballing it.

This is a compact reference for how I build LLM features in production: keep the model behind an interface, validate everything it returns, and put a regression eval around it.

```
  raw text ─▶ build prompt (from schema) ─▶ LLM provider ─▶ parse JSON ─▶ validate vs schema ─▶ {data, errors}
                                            │
                            OpenAI / Anthropic / offline mock
```

## Why

“Ask the model for JSON” is easy to prototype and hard to trust. This repo shows the parts that make it reliable:

- **Schema-driven prompts** — you declare fields once (`Field(name, type, description, required)`); the prompt and the validator are both generated from that schema.
- **Validation** — the model’s output is parsed and checked against the schema (required fields present, numbers are numbers, booleans are booleans). You get back `data` **and** a list of `errors`.
- **Provider-agnostic** — swap OpenAI / Anthropic via env vars. With no API key set it falls back to an offline **mock** so the demo and tests run anywhere.
- **Eval harness** — `eval.py` runs the extractor over labeled cases and reports field-level accuracy, the same pattern I use to catch regressions when prompts or models change.

## Quickstart

Runs offline out of the box (mock provider — no key needed):

```bash
python extract.py        # extract from examples/sample.txt
python eval.py           # run the eval harness
```

Use a real model by setting a key:

```bash
export OPENAI_API_KEY=sk-...      # or ANTHROPIC_API_KEY=...
pip install openai               # or: pip install anthropic
python extract.py
```

## Example

`examples/sample.txt`:

```
お世話になっております。至急お見積もりをお願いします。
連絡先は taro@example.com、電話は 090-1234-5678 です。
ご予算は ¥120,000 程度、納期は 2025-04-30 を希望します。
```

```bash
$ python extract.py
{
  "data": {
    "email": "taro@example.com",
    "phone": "090-1234-5678",
    "amount": 120000,
    "date": "2025-04-30",
    "urgent": true
  },
  "errors": [],
  "provider": "mock"
}
```

The eval harness over labeled cases:

```bash
$ python eval.py
field accuracy: 7/7 = 100%
```

## Defining a schema

```python
from schema import Field
from extract import extract

schema = [
    Field("email", "string", "contact email"),
    Field("amount", "number", "total amount in yen", required=False),
    Field("urgent", "boolean", "is the request urgent?"),
]
result = extract("至急、予算 ¥50,000。連絡は a@b.com", schema)
# {'data': {...}, 'errors': [], 'provider': 'mock'}
```

## How it works

| File | Responsibility |
|------|----------------|
| `schema.py` | `Field` definition + `validate(data, schema)`. |
| `providers.py` | Provider abstraction: `OpenAIProvider`, `AnthropicProvider`, and an offline `MockProvider`. `get_provider()` picks one from the environment. |
| `extract.py` | Builds the schema-driven prompt, calls the provider, parses & validates the JSON. |
| `eval.py` | Tiny regression eval: labeled cases → field-level accuracy. |
| `examples/sample.txt` | A sample input. |

## Design notes

- The **prompt is derived from the schema**, so adding a field never means editing the prompt by hand.
- Output is parsed defensively (extracts the first JSON object) and then **validated** — the caller always learns whether the result is trustworthy.
- The provider interface is one method (`complete(prompt) -> str`), which keeps models swappable and makes the offline mock trivial.
- The mock is **not** an LLM — it’s a small heuristic extractor so the repo runs and tests without network or keys. Real providers replace it the moment a key is present.
- The eval harness is deliberately minimal but is the same shape I scale up in real systems (golden cases, per-field scoring, run on every change).

## Requirements

Python 3.10+. No required dependencies for the offline path. Install `openai` or `anthropic` only if you use those providers.
