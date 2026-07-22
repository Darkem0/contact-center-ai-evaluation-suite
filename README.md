# Contact Center AI Evaluation Suite

A clean-room, local-first reference suite for evaluating conversational support workflows with synthetic dialogues and deterministic rules. It is a portfolio reconstruction: it does **not** contain employer code, client taxonomies, private prompts, call recordings, production schemas, or production performance claims.

## What it demonstrates

- NPS-style root-cause signals and customer dissatisfaction sources;
- call summary, resolution, and transfer detection;
- representative action, coaching, and training signals;
- generic legal-text, prohibited-phrase, factuality, insurance-quality, and profanity-risk checks;
- schema validation and explicit failure handling for structured JSON output.

The bundled engine is deliberately transparent and deterministic. Replace its rule adapters with independently reviewed models only after validating data rights, safety, fairness, and evaluation criteria.

## Quick start

```bash
python -m pip install -e ".[dev]"
python -m contact_center_eval.demo
pytest
```

The demo reads only [`fixtures/synthetic_dialogue.json`](fixtures/synthetic_dialogue.json) and prints a JSON report.

## Safe data boundary

Use only synthetic dialogues or datasets whose licences and consent terms permit the intended use. Do not add real call audio, transcripts, customer identifiers, client names, original prompts, internal policies, or production-only fields.

## Repository map

```text
src/contact_center_eval/engine.py  deterministic evaluation adapters
fixtures/                          synthetic examples only
tests/                             local unit tests
docs/                              provenance, architecture, and limitations
```

See [Architecture](docs/ARCHITECTURE.md), [Limitations](docs/LIMITATIONS.md), [Provenance](docs/PROVENANCE.md), and [Security](SECURITY.md).

## Status

Clean-room reconstruction of completed professional task families. It is a reference implementation, not a deployed contact-center product or a legal/compliance decision system.
