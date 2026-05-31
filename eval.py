"""Tiny eval harness: run extract() over labeled cases and score field accuracy.

This is the smallest useful version of the regression evals I build around LLM
features — add golden cases, run on every prompt/model change, watch the score.
"""
from __future__ import annotations

from schema import Field
from extract import extract

CASES = [
    {"text": "連絡は hana@test.jp まで。至急対応希望、予算 ¥50,000。",
     "expect": {"email": "hana@test.jp", "amount": 50000, "urgent": True}},
    {"text": "Please email bob@acme.com. Budget $3,000, due 2025-06-01.",
     "expect": {"email": "bob@acme.com", "amount": 3000, "date": "2025-06-01", "urgent": False}},
]
SCHEMA = [Field("email"), Field("amount", "number", required=False),
          Field("date", "string", required=False), Field("urgent", "boolean")]


def score() -> None:
    total = hits = 0
    for c in CASES:
        got = extract(c["text"], SCHEMA)["data"]
        for k, v in c["expect"].items():
            total += 1
            if got.get(k) == v:
                hits += 1
            else:
                print(f"  miss {k}: got {got.get(k)!r} expected {v!r}")
    print(f"field accuracy: {hits}/{total} = {hits / total:.0%}")


if __name__ == "__main__":
    score()
