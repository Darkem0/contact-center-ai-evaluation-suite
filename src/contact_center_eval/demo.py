"""Run the synthetic dialogue demonstration."""

from __future__ import annotations

import json
from pathlib import Path

from .engine import evaluate_dialogue


def main() -> None:
    fixture = Path(__file__).parents[2] / "fixtures" / "synthetic_dialogue.json"
    print(json.dumps(evaluate_dialogue(json.loads(fixture.read_text(encoding="utf-8"))), indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
