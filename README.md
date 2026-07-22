# Contact Center AI Evaluation Suite

Evaluate a **synthetic** support dialogue through eight typed, deterministic task packs, then return an evidence-linked JSON report through a CLI or local FastAPI endpoint.

It demonstrates how a product can separate observed wording, unsupported claims, and insufficient evidence instead of producing an opaque score. The default path is useful for testing structured-output contracts before a separately governed local model is introduced.

## Run it

```bash
python -m pip install -e ".[dev]"
python -m contact_center_eval.cli demo --output examples/demo-report.json
pytest -q
```

Start the API when needed:

```bash
python -m contact_center_eval.cli serve
# POST a JSON body with {"turns": [...]} to http://127.0.0.1:8000/v1/evaluate
```

## Expected output

The real demo reads [`fixtures/synthetic_dialogue.json`](fixtures/synthetic_dialogue.json) and creates [`examples/demo-report.json`](examples/demo-report.json). It contains all eight task packs, per-turn evidence excerpts, structured validation status, and explicit `insufficient_evidence` results where the dialogue cannot support a conclusion.

```json
{
  "schema_version": "contact-center-eval.v2",
  "mode": "deterministic-local",
  "structured_output_valid": true
}
```

## What is real, mock, and optional?

- **Real and runnable:** Pydantic schemas, deterministic processing, CLI, FastAPI contract, fixtures, report generation, and tests.
- **Mock by design:** the phrase-level task-pack rules and their output are synthetic examples, not customer or staff assessments.
- **Optional:** `LocalLLMAdapter` is a protocol for a separately evaluated local model. The default demo and CI do not download a model or use a paid API.

## Included task packs

1. Call summary and resolution
2. NPS root-cause analysis (generic signal summary, not a survey score)
3. Representative actions and training needs
4. Team-leader coaching analysis
5. Prohibited-phrase detection
6. Factuality and scenario-compliance review cues
7. Profanity versus insult classification
8. Transfer and outcome detection

Each task pack produces `complete` or `insufficient_evidence`, a brief reason, source-turn excerpts, and a typed result. The engine never treats a missing source of truth as a factuality confirmation.

## Product surface

```text
fixtures/                public-safe synthetic dialogue inputs
src/contact_center_eval/ schemas, deterministic engine, CLI, FastAPI API
examples/                generated demo report
tests/                   normal, malformed, schema, and API cases
```

The [`Dockerfile`](Dockerfile) starts the local API. The included [architecture diagram](docs/ARCHITECTURE.md) explains the flow and the [example report](examples/demo-report.json) is produced by the command above.

## API example

```bash
curl -X POST http://127.0.0.1:8000/v1/evaluate \
  -H "content-type: application/json" \
  --data @examples/api-request.json
```

The API request wrapper lives in [`examples/api-request.json`](examples/api-request.json); the CLI accepts the fixture’s top-level array directly.

## Safe data boundary

Use only synthetic data or datasets whose consent, licence, retention, and purpose limits support the intended work. Do not add call recordings, customer identifiers, customer transcripts, employer prompts, customer-specific taxonomies, private scoring rules, or production claims.

Read [Architecture](docs/ARCHITECTURE.md), [Provenance](docs/PROVENANCE.md), [Limitations](docs/LIMITATIONS.md), and [Security](SECURITY.md) before extending the example.
