"""
Claude-backed ResearchProvider for the Strategy 7 checklist.

Answers the open-ended research questions (conditions 3-5: "does the
reason for the decline still apply?", "proven track record?", "future
growth prospect?") by calling the Claude API. Uses only the stdlib
(urllib) so the strategy/research layer keeps its zero-dependency rule -
`requests` stays reserved for the data fetcher.

HONESTY BOUNDARY, stated plainly: a plain API call has no live web
access, so its knowledge of current events may be stale. The system
prompt instructs the model to answer UNCLEAR unless it is confident, and
every verdict - even a confident PASS - flows into a Signal that is
already requires_human_confirmation=True. This provider is research
ASSISTANCE for the human reviewer, not a substitute for them (Section 5.5
flag 1: this strategy is the strongest human-in-the-loop candidate in
the framework).

Errors never propagate: any API/parsing failure degrades to
NEEDS_RESEARCH with the error in the detail, consistent with the
framework-wide "missing data must never crash signal generation" rule.
"""

from __future__ import annotations

import json
import os
import urllib.error
import urllib.request
from typing import Callable, Optional

from sunabha_agent.research.turnaround_checklist import ChecklistStatus, ResearchAnswer

API_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"
DEFAULT_MODEL = "claude-sonnet-5"
DEFAULT_MAX_TOKENS = 1024

SYSTEM_PROMPT = """\
You are a research assistant for an Indian stock-market turnaround checklist
(the "Three Times in Three Years" strategy). You will be asked to verify one
qualitative condition about one NSE-listed company.

Rules:
- Answer ONLY with a JSON object: {"verdict": "PASS" | "FAIL" | "UNCLEAR",
  "reasoning": "<2-4 sentences citing your evidence>"}
- PASS means the condition is clearly satisfied; FAIL means it is clearly
  not satisfied; UNCLEAR means you cannot verify it confidently.
- You have NO live market data or news access. If verifying the condition
  requires current information you cannot be certain about, you MUST answer
  UNCLEAR rather than guess. A wrong PASS costs the user real money; an
  UNCLEAR merely sends the question to a human.
- Your answer is reviewed by a human before any trade - be direct about
  what you do and do not know."""


def _default_transport(payload: dict, api_key: str, timeout: float) -> dict:
    request = urllib.request.Request(
        API_URL,
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "content-type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": ANTHROPIC_VERSION,
        },
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8"))


class ClaudeResearchProvider:
    """
    ResearchProvider backed by the Claude API.

    `transport` is injectable for testing (and for callers who want to
    route through their own HTTP stack): it receives the request payload
    dict and must return the parsed response body dict.
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = DEFAULT_MODEL,
        timeout_seconds: float = 60.0,
        transport: Optional[Callable[[dict], dict]] = None,
    ):
        self._api_key = api_key or os.environ.get("ANTHROPIC_API_KEY", "")
        self._model = model
        self._timeout = timeout_seconds
        self._transport = transport

    def research(self, question: str, context: dict) -> ResearchAnswer:
        if not self._api_key and self._transport is None:
            return ResearchAnswer(
                ChecklistStatus.NEEDS_RESEARCH,
                "No ANTHROPIC_API_KEY configured - answer this manually.",
            )

        payload = {
            "model": self._model,
            "max_tokens": DEFAULT_MAX_TOKENS,
            "system": SYSTEM_PROMPT,
            "messages": [
                {
                    "role": "user",
                    "content": (
                        f"Question:\n{question}\n\n"
                        f"Known data (may be partial):\n{json.dumps(context, default=str)}"
                    ),
                }
            ],
        }
        try:
            if self._transport is not None:
                body = self._transport(payload)
            else:
                body = _default_transport(payload, self._api_key, self._timeout)
            text = body["content"][0]["text"]
            verdict = _parse_verdict(text)
        except (urllib.error.URLError, OSError, KeyError, IndexError, ValueError) as exc:
            return ResearchAnswer(
                ChecklistStatus.NEEDS_RESEARCH,
                f"LLM research failed ({exc}) - answer this manually.",
            )

        status = {
            "PASS": ChecklistStatus.PASS,
            "FAIL": ChecklistStatus.FAIL,
            "UNCLEAR": ChecklistStatus.NEEDS_RESEARCH,
        }.get(verdict["verdict"], ChecklistStatus.NEEDS_RESEARCH)
        return ResearchAnswer(status, f"[Claude, human-review required] {verdict['reasoning']}")


def _parse_verdict(text: str) -> dict:
    """Pull the verdict JSON out of the model's reply, tolerating prose or
    code fences around it."""
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end <= start:
        raise ValueError(f"no JSON object in model reply: {text[:120]!r}")
    parsed = json.loads(text[start : end + 1])
    if "verdict" not in parsed:
        raise ValueError("model reply JSON has no 'verdict' key")
    parsed.setdefault("reasoning", "(no reasoning given)")
    return parsed
