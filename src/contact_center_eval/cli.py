"""Command-line interface for the synthetic, deterministic vertical slice."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Sequence

from .engine import EvaluationError, evaluate
from .schemas import DialogueRequest


ROOT = Path(__file__).parents[2]
DEFAULT_FIXTURE = ROOT / "fixtures" / "synthetic_dialogue.json"


def _load_dialogue(path: Path) -> DialogueRequest:
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
        return DialogueRequest(turns=raw if isinstance(raw, list) else raw["turns"])
    except (OSError, KeyError, TypeError, json.JSONDecodeError, ValueError) as error:
        raise EvaluationError(f"cannot load dialogue {path}: {error}") from error


def _write_report(dialogue_path: Path, output: Path | None) -> str:
    report = evaluate(_load_dialogue(dialogue_path))
    rendered = report.model_dump_json(indent=2)
    if output is not None:
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(f"{rendered}\n", encoding="utf-8")
    return rendered


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Evaluate a synthetic dialogue with eight deterministic task packs.")
    subcommands = parser.add_subparsers(dest="command")
    for name in ("demo", "evaluate"):
        command = subcommands.add_parser(name)
        command.add_argument("--input", type=Path, default=DEFAULT_FIXTURE, help="JSON array of synthetic dialogue turns")
        command.add_argument("--output", type=Path, help="Optional JSON report path")
    serve = subcommands.add_parser("serve", help="Run the local FastAPI application.")
    serve.add_argument("--host", default="127.0.0.1")
    serve.add_argument("--port", type=int, default=8000)
    return parser


def main(argv: Sequence[str] | None = None) -> None:
    args = build_parser().parse_args(argv)
    command = args.command or "demo"
    if command == "serve":
        import uvicorn

        uvicorn.run("contact_center_eval.api:app", host=args.host, port=args.port, reload=False)
        return
    try:
        print(_write_report(args.input, args.output))
    except EvaluationError as error:
        raise SystemExit(f"error: {error}") from error


if __name__ == "__main__":
    main()
