"""Typed public schemas for the synthetic evaluation API and CLI."""

from __future__ import annotations

from enum import Enum
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field


class Role(str, Enum):
    CUSTOMER = "customer"
    AGENT = "agent"


class DialogueTurn(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    role: Role
    text: str = Field(min_length=1, max_length=2_000)


class DialogueRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    turns: list[DialogueTurn] = Field(min_length=1, max_length=100)


class Evidence(BaseModel):
    model_config = ConfigDict(extra="forbid")

    turn_index: int = Field(ge=1)
    role: Role
    excerpt: str = Field(min_length=1, max_length=180)
    signals: list[str] = Field(default_factory=list)


class TaskResult(BaseModel):
    model_config = ConfigDict(extra="forbid")

    status: Literal["complete", "insufficient_evidence", "review"]
    reason: str = Field(min_length=1)
    evidence: list[Evidence] = Field(default_factory=list)
    result: dict[str, Any]


class EvaluationReport(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schema_version: Literal["contact-center-eval.v2"]
    report_id: str = Field(pattern=r"^synthetic-[a-f0-9]{12}$")
    mode: Literal["deterministic-local"]
    task_packs: dict[str, TaskResult]
    structured_output_valid: Literal[True]
    disclaimer: str = Field(min_length=1)
