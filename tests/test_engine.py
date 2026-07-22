from contact_center_eval.engine import EvaluationError, evaluate_dialogue


def test_evaluation_returns_stable_structure() -> None:
    result = evaluate_dialogue([
        {"role": "customer", "text": "I am frustrated by a delayed request."},
        {"role": "agent", "text": "I am sorry and will arrange a follow-up."},
    ])
    assert result["customer"]["sentiment"] == "negative"
    assert result["interaction"]["resolution_detected"] is True
    assert result["validation"]["structured_output"] is True


def test_invalid_shape_fails_closed() -> None:
    try:
        evaluate_dialogue([{"role": "customer", "text": "x", "private": "never accepted"}])
    except EvaluationError:
        pass
    else:
        raise AssertionError("unexpected input must be rejected")
