"""LLM provider abstraction.

One interface (`complete(prompt) -> str`). `get_provider()` chooses an
implementation from the environment, falling back to an offline mock so the
repo runs without network access or API keys.
"""
from __future__ import annotations
import os
import json
import re


def get_provider():
    if os.getenv("OPENAI_API_KEY"):
        return OpenAIProvider()
    if os.getenv("ANTHROPIC_API_KEY"):
        return AnthropicProvider()
    return MockProvider()


class OpenAIProvider:
    name = "openai"

    def complete(self, prompt: str) -> str:
        from openai import OpenAI
        client = OpenAI()
        r = client.chat.completions.create(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
        )
        return r.choices[0].message.content


class AnthropicProvider:
    name = "anthropic"

    def complete(self, prompt: str) -> str:
        import anthropic
        client = anthropic.Anthropic()
        r = client.messages.create(
            model=os.getenv("ANTHROPIC_MODEL", "claude-3-5-haiku-latest"),
            max_tokens=1024,
            messages=[{"role": "user", "content": prompt}],
        )
        return r.content[0].text


class MockProvider:
    """Offline fallback so the demo runs without keys.

    Not an LLM — a tiny heuristic extractor for the example fields. Real
    providers replace it automatically when an API key is set.
    """
    name = "mock"

    def complete(self, prompt: str) -> str:
        text = prompt.split("---TEXT---", 1)[-1]
        out: dict = {}
        m = re.search(r"[\w.+-]+@[\w-]+\.[a-zA-Z]{2,}", text)
        if m:
            out["email"] = m.group(0)
        m = re.search(r"(\+?\d[\d\- ]{8,}\d)", text)
        if m:
            out["phone"] = m.group(1).strip()
        m = re.search(r"(?:¥|\$)\s?([\d,]+)", text)
        if m:
            out["amount"] = int(m.group(1).replace(",", ""))
        m = re.search(r"(\d{4}-\d{2}-\d{2})", text)
        if m:
            out["date"] = m.group(1)
        out["urgent"] = bool(re.search(r"急|urgent|asap|すぐ", text, re.I))
        return json.dumps(out, ensure_ascii=False)
