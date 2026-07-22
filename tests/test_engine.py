import json
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from contact_center_eval.api import app
from contact_center_eval.engine import EvaluationError, evaluate_dialogue, validate_structured_json


FIXTURES = Path(__file__).parents[1] / "fixtures"


def _fixture(name: str) -> list[dict[str, str]]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def test_all_task_packs_process_a_synthetic_dialogue() -> None:
    result = evaluate_dialogue(_fixture("synthetic_dialogue.json"))
    assert set(result["task_packs"]) == {
        "call_summary_and_resolution",
        "nps_root_cause_analysis",
        "representative_actions_and_training_needs",
        "team_leader_coaching_analysis",
        "prohibited_phrase_detection",
        "factuality_and_scenario_compliance",
        "profanity_vs_insult_classification",
        "transfer_and_outcome_detection",
    }
    assert result["task_packs"]["call_summary_and_resolution"]["result"]["resolution_detected"] is True
    assert result["task_packs"]["nps_root_cause_analysis"]["result"]["sentiment_proxy"] == "negative"
    assert result["structured_output_valid"] is True


def test_insufficient_evidence_is_explicit_not_invented() -> None:
    result = evaluate_dialogue(_fixture("insufficient_dialogue.json"))
    pack = result["task_packs"]["representative_actions_and_training_needs"]
    assert pack["status"] == "insufficient_evidence"
    assert pack["result"] == {"outcome": "insufficient_evidence"}
    assert result["task_packs"]["transfer_and_outcome_detection"]["status"] == "insufficient_evidence"


def test_profanity_and_insult_are_not_collapsed() -> None:
    result = evaluate_dialogue(_fixture("prohibited_dialogue.json"))
    profanity = result["task_packs"]["profanity_vs_insult_classification"]["result"]
    assert profanity["profanity_terms"] == ["damn"]
    assert profanity["insult_terms"] == ["idiot"]
    assert profanity["classification"] == "insult"
    prohibited = result["task_packs"]["prohibited_phrase_detection"]["result"]
    assert prohibited["review_required"] is True


def test_malformed_dialogue_fails_closed() -> None:
    with pytest.raises(EvaluationError, match="invalid dialogue"):
        evaluate_dialogue([{"role": "customer", "text": "x", "private": "never accepted"}])


def test_structured_json_validation_rejects_unknown_report_fields() -> None:
    good = json.dumps(evaluate_dialogue(_fixture("synthetic_dialogue.json")))
    assert validate_structured_json(good).schema_version == "contact-center-eval.v2"
    invalid = json.loads(good)
    invalid["unapproved"] = True
    with pytest.raises(EvaluationError, match="invalid structured report"):
        validate_structured_json(json.dumps(invalid))


def test_fastapi_health_and_evaluation_endpoints() -> None:
    client = TestClient(app)
    assert client.get("/healthz").json() == {"status": "ok", "mode": "deterministic-local"}
    response = client.post("/v1/evaluate", json={"turns": _fixture("synthetic_dialogue.json")})
    assert response.status_code == 200
    assert response.json()["task_packs"]["transfer_and_outcome_detection"]["result"]["transfer_detected"] is True
    invalid = client.post("/v1/evaluate", json={"turns": [{"role": "unknown", "text": "x"}]})
    assert invalid.status_code == 422
