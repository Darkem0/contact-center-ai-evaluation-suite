"""Deterministic task packs for synthetic support-dialogue evaluation.

The rules are deliberately small and inspectable.  They are not a substitute
for a private contact-center rubric, a model evaluation, or a customer decision.
"""

from __future__ import annotations

from hashlib import sha256
import json
import re
from typing import Any, Protocol, Sequence

from .schemas import (
    DialogueRequest,
    DialogueTurn,
    Evidence,
    EvaluationReport,
    TaskResult,
)


class EvaluationError(ValueError):
    """Raised when a supplied dialogue cannot make a safe structured report."""


class LocalLLMAdapter(Protocol):
    """Optional local-model extension point.

    An adapter may propose an additional result, but callers must validate it
    against ``TaskResult`` and preserve the deterministic evidence boundary.
    No adapter is required for the default demo or CI.
    """

    def evaluate_task(
        self, task_name: str, dialogue: DialogueRequest, evidence: list[Evidence]
    ) -> dict[str, Any]: ...


WORD = re.compile(r"[a-z0-9']+")
ROOT_CAUSE_TERMS = ("delayed", "frustrated", "angry", "unhappy", "complaint", "again")
RESOLUTION_TERMS = ("resolved", "arrange", "follow-up", "follow up", "summary", "check")
TRANSFER_TERMS = ("transfer", "escalate", "another team")
ACTION_TERMS = ("check", "arrange", "send", "follow-up", "follow up", "explain")
PROHIBITED_TERMS = ("guaranteed", "hide this", "ignore policy")
UNCERTAIN_CLAIM_TERMS = ("guaranteed", "always", "never", "definitely")
PROFANITY_TERMS = ("damn", "hell")
INSULT_TERMS = ("idiot", "stupid")


def _tokens(text: str) -> set[str]:
    return set(WORD.findall(text.lower()))


def _matched_terms(text: str, terms: Sequence[str]) -> list[str]:
    haystack = text.lower()
    words = _tokens(text)
    return [term for term in terms if (" " in term and term in haystack) or term in words]


def _excerpt(text: str, limit: int = 180) -> str:
    compact = " ".join(text.split())
    return compact if len(compact) <= limit else f"{compact[: limit - 1]}…"


def _evidence(
    dialogue: DialogueRequest, terms: Sequence[str] = (), role: str | None = None
) -> list[Evidence]:
    collected: list[Evidence] = []
    for index, turn in enumerate(dialogue.turns, start=1):
        if role is not None and turn.role.value != role:
            continue
        matched = _matched_terms(turn.text, terms) if terms else []
        if terms and not matched:
            continue
        collected.append(
            Evidence(
                turn_index=index,
                role=turn.role,
                excerpt=_excerpt(turn.text),
                signals=matched,
            )
        )
    return collected


def _insufficient(reason: str) -> TaskResult:
    return TaskResult(
        status="insufficient_evidence",
        reason=reason,
        evidence=[],
        result={"outcome": "insufficient_evidence"},
    )


def _complete(result: dict[str, Any], evidence: list[Evidence], reason: str) -> TaskResult:
    return TaskResult(status="complete", reason=reason, evidence=evidence, result=result)


def _first_sentence(text: str) -> str:
    candidate = re.split(r"(?<=[.!?])\s+", text.strip(), maxsplit=1)[0]
    return candidate or "No synthetic customer issue was supplied."


def _summary_and_resolution(dialogue: DialogueRequest) -> TaskResult:
    customer_turns = [turn for turn in dialogue.turns if turn.role.value == "customer"]
    agent_turns = [turn for turn in dialogue.turns if turn.role.value == "agent"]
    if not customer_turns:
        return _insufficient("A customer statement is required to summarize the issue.")
    resolution_evidence = _evidence(dialogue, RESOLUTION_TERMS, role="agent")
    issue = _first_sentence(customer_turns[0].text)
    if not agent_turns:
        return _complete(
            {"summary": issue, "resolution": "not_observed", "resolution_detected": False},
            _evidence(dialogue, role="customer"),
            "The issue is present, but no agent turn supports a resolution outcome.",
        )
    return _complete(
        {
            "summary": issue,
            "resolution": "supported" if resolution_evidence else "not_observed",
            "resolution_detected": bool(resolution_evidence),
        },
        _evidence(dialogue, role="customer")[:1] + resolution_evidence,
        "A deterministic summary uses the first customer issue and generic agent action signals.",
    )


def _nps_root_cause(dialogue: DialogueRequest) -> TaskResult:
    customer_evidence = _evidence(dialogue, ROOT_CAUSE_TERMS, role="customer")
    customer_turns = [turn for turn in dialogue.turns if turn.role.value == "customer"]
    if not customer_turns:
        return _insufficient("No customer turn is available for root-cause analysis.")
    signals = sorted({signal for item in customer_evidence for signal in item.signals})
    proxy = "negative" if signals else "neutral"
    return _complete(
        {"sentiment_proxy": proxy, "root_cause_signals": signals, "score": None},
        customer_evidence,
        "This is a deterministic signal summary, not an NPS survey score or prediction.",
    )


def _representative_actions(dialogue: DialogueRequest) -> TaskResult:
    agent_turns = [turn for turn in dialogue.turns if turn.role.value == "agent"]
    if not agent_turns:
        return _insufficient("No agent turn is available to identify actions or training needs.")
    evidence = _evidence(dialogue, ACTION_TERMS, role="agent")
    actions = sorted({signal for item in evidence for signal in item.signals})
    needs = [] if actions else ["Ask for a concrete next step with evidence in the dialogue."]
    return _complete(
        {"observed_actions": actions, "training_needs": needs},
        evidence,
        "Actions are extracted only from generic public-safe phrase matches.",
    )


def _team_leader_coaching(dialogue: DialogueRequest) -> TaskResult:
    agent_turns = [turn for turn in dialogue.turns if turn.role.value == "agent"]
    if not agent_turns:
        return _insufficient("No agent turn is available for a coaching observation.")
    root_cause_evidence = _evidence(dialogue, ROOT_CAUSE_TERMS, role="customer")
    action_evidence = _evidence(dialogue, ACTION_TERMS, role="agent")
    coaching = []
    if root_cause_evidence and not action_evidence:
        coaching.append("Acknowledge the issue and state one observable next step.")
    if not root_cause_evidence:
        coaching.append("Confirm the customer’s issue before proposing a next step.")
    if not coaching:
        coaching.append("Review whether the stated next step is completed in a later turn.")
    return _complete(
        {"coaching_observations": coaching, "human_review_required": True},
        root_cause_evidence + action_evidence,
        "Coaching is a generic review cue, not a personnel rating or employment decision.",
    )


def _prohibited_phrase(dialogue: DialogueRequest) -> TaskResult:
    evidence = _evidence(dialogue, PROHIBITED_TERMS, role="agent")
    matches = sorted({signal for item in evidence for signal in item.signals})
    return _complete(
        {"matches": matches, "review_required": bool(matches)},
        evidence,
        "The small phrase list is illustrative and is not a customer or employer policy taxonomy.",
    )


def _factuality_and_scenario(dialogue: DialogueRequest) -> TaskResult:
    agent_turns = [turn for turn in dialogue.turns if turn.role.value == "agent"]
    if not agent_turns:
        return _insufficient("No agent assertion is available for a factuality or scenario check.")
    evidence = _evidence(dialogue, UNCERTAIN_CLAIM_TERMS, role="agent")
    claims = sorted({signal for item in evidence for signal in item.signals})
    return _complete(
        {
            "unsupported_certainty_terms": claims,
            "scenario_compliance": "review" if claims else "no_generic_rule_match",
            "factuality_status": "requires_source_review" if claims else "insufficient_source_context",
        },
        evidence,
        "The fixture has no external source-of-truth, so factuality is never asserted as verified.",
    )


def _profanity_vs_insult(dialogue: DialogueRequest) -> TaskResult:
    profanity_evidence = _evidence(dialogue, PROFANITY_TERMS)
    insult_evidence = _evidence(dialogue, INSULT_TERMS)
    return _complete(
        {
            "profanity_terms": sorted({s for item in profanity_evidence for s in item.signals}),
            "insult_terms": sorted({s for item in insult_evidence for s in item.signals}),
            "classification": "insult" if insult_evidence else "profanity" if profanity_evidence else "none",
        },
        profanity_evidence + insult_evidence,
        "Generic lexical labels require human review and are not a moderation decision.",
    )


def _transfer_and_outcome(dialogue: DialogueRequest) -> TaskResult:
    transfer_evidence = _evidence(dialogue, TRANSFER_TERMS)
    resolution_evidence = _evidence(dialogue, RESOLUTION_TERMS, role="agent")
    if not transfer_evidence and not resolution_evidence:
        return _insufficient("No generic transfer or outcome signal appears in the supplied dialogue.")
    return _complete(
        {
            "transfer_detected": bool(transfer_evidence),
            "outcome_detected": "resolution_signal" if resolution_evidence else "not_observed",
        },
        transfer_evidence + resolution_evidence,
        "The result records wording signals only; it does not verify an operational outcome.",
    )


def _report_id(dialogue: DialogueRequest) -> str:
    encoded = json.dumps(dialogue.model_dump(mode="json"), sort_keys=True, separators=(",", ":"))
    return f"synthetic-{sha256(encoded.encode('utf-8')).hexdigest()[:12]}"


def evaluate(dialogue: DialogueRequest, adapter: LocalLLMAdapter | None = None) -> EvaluationReport:
    """Evaluate all eight deterministic task packs and validate the final schema.

    ``adapter`` is intentionally unused in the default path.  It documents the
    extension point for a separately evaluated, local model; model output must
    be parsed through ``TaskResult`` before an integration may surface it.
    """
    if adapter is not None and not hasattr(adapter, "evaluate_task"):
        raise EvaluationError("adapter must expose evaluate_task")
    packs = {
        "call_summary_and_resolution": _summary_and_resolution(dialogue),
        "nps_root_cause_analysis": _nps_root_cause(dialogue),
        "representative_actions_and_training_needs": _representative_actions(dialogue),
        "team_leader_coaching_analysis": _team_leader_coaching(dialogue),
        "prohibited_phrase_detection": _prohibited_phrase(dialogue),
        "factuality_and_scenario_compliance": _factuality_and_scenario(dialogue),
        "profanity_vs_insult_classification": _profanity_vs_insult(dialogue),
        "transfer_and_outcome_detection": _transfer_and_outcome(dialogue),
    }
    report = EvaluationReport(
        schema_version="contact-center-eval.v2",
        report_id=_report_id(dialogue),
        mode="deterministic-local",
        task_packs=packs,
        structured_output_valid=True,
        disclaimer=(
            "Synthetic deterministic demonstration; not a customer, employee, legal, quality, or compliance decision."
        ),
    )
    # Exercise schema validation over the exact JSON-compatible output.
    return EvaluationReport.model_validate(report.model_dump(mode="json"))


def evaluate_dialogue(turns: Sequence[dict[str, Any]] | DialogueRequest) -> dict[str, Any]:
    """Compatibility helper returning a JSON-safe dict for a list of turns."""
    try:
        dialogue = turns if isinstance(turns, DialogueRequest) else DialogueRequest(turns=list(turns))
    except Exception as error:  # Pydantic's public errors are intentionally normalized here.
        raise EvaluationError(f"invalid dialogue: {error}") from error
    return evaluate(dialogue).model_dump(mode="json")


def validate_structured_json(payload: str) -> EvaluationReport:
    """Fail closed when a proposed report is not the documented output schema."""
    try:
        return EvaluationReport.model_validate_json(payload)
    except Exception as error:
        raise EvaluationError(f"invalid structured report: {error}") from error
