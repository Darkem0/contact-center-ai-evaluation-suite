"""Local FastAPI surface for the deterministic synthetic evaluator."""

from fastapi import FastAPI, HTTPException

from .engine import EvaluationError, evaluate
from .schemas import DialogueRequest, EvaluationReport


app = FastAPI(title="Contact Center AI Evaluation Suite", version="0.2.0")


@app.get("/healthz")
def healthz() -> dict[str, str]:
    return {"status": "ok", "mode": "deterministic-local"}


@app.post("/v1/evaluate", response_model=EvaluationReport)
def evaluate_dialogue(request: DialogueRequest) -> EvaluationReport:
    try:
        return evaluate(request)
    except EvaluationError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error
