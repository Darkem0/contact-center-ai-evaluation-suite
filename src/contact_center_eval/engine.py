"""Transparent rule adapters for synthetic conversation evaluation.

The rules are intentionally generic and are not a proxy for a private policy,
client taxonomy, legal determination, or production model.
"""

from __future__ import annotations

from collections.abc import Sequence
from typing import Any


class EvaluationError(ValueError):
    """Raised when an input cannot produce a safe structured result."""


NEGATIVE = {"frustrated", "angry", "delayed", "unhappy", "complaint", "again"}
POSITIVE = {"thank", "thanks", "resolved", "helpful", "great"}
PROFANITY = {"idiot", "stupid", "damn"}
PROHIBITED = {"guaranteed", "hide this", "ignore policy"}
TRANSFER = {"transfer", "escalate", "another team"}
RESOLUTION = {"resolved", "arrange", "follow-up", "summary"}


def _words(text: str) -> set[str]:
    return {word.strip(".,!?;:").lower() for word in text.split() if word.strip()}


def _contains(text: str, terms: set[str]) -> list[str]:
    words = _words(text)
    return sorted(term for term in terms if term in words or term in text.lower())


def _validate_turns(turns: Sequence[dict[str, Any]]) -> None:
    if not turns:
        raise EvaluationError("dialogue must contain at least one turn")
    for index, turn in enumerate(turns):
        if set(turn) != {"role", "text"}:
            raise EvaluationError(f"turn {index} must contain only role and text")
        if turn["role"] not in {"customer", "agent"} or not isinstance(turn["text"], str):
            raise EvaluationError(f"turn {index} has an unsupported role or text")
        if not turn["text"].strip():
            raise EvaluationError(f"turn {index} has empty text")


def evaluate_dialogue(turns: Sequence[dict[str, Any]]) -> dict[str, Any]:
    """Return a stable, JSON-serializable mock evaluation for a dialogue."""
    _validate_turns(turns)
    customer_text = " ".join(turn["text"] for turn in turns if turn["role"] == "customer")
    agent_text = " ".join(turn["text"] for turn in turns if turn["role"] == "agent")
    negative = _contains(customer_text, NEGATIVE)
    positive = _contains(customer_text + " " + agent_text, POSITIVE)
    prohibited = _contains(agent_text, PROHIBITED)
    profanity = _contains(customer_text + " " + agent_text, PROFANITY)
    transfer = _contains(customer_text + " " + agent_text, TRANSFER)
    resolved = _contains(agent_text, RESOLUTION)
    sentiment = "negative" if negative else "positive" if positive else "neutral"
    nps_proxy = 0 if len(negative) >= 2 else 10 if positive and not negative else 5
    summary = customer_text.split(".")[0].strip() or "Synthetic dialogue evaluated."

    return {
        "schema_version": "clean-room.v1",
        "summary": summary,
        "nps_root_cause": {"proxy_score": nps_proxy, "signals": negative or positive},
        "customer": {
            "sentiment": sentiment,
            "dissatisfaction_sources": negative,
            "profanity_risk": {"level": "review" if profanity else "none", "signals": profanity},
        },
        "interaction": {
            "resolution_detected": bool(resolved),
            "transfer_detected": bool(transfer),
            "factuality_review_required": bool(prohibited),
        },
        "agent": {
            "actions": resolved,
            "coaching_signals": ["acknowledge concern"] if negative else [],
            "legal_text_review": {"status": "review" if prohibited else "no_rule_match", "signals": prohibited},
            "insurance_quality": "not_applicable_in_mock",
        },
        "validation": {"structured_output": True, "failure_handling": "input validation enabled"},
        "disclaimer": "Deterministic synthetic-demo output; not a legal, quality, or customer decision.",
    }
