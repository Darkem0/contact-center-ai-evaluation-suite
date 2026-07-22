# Architecture

The default path is intentionally local and deterministic. It accepts a small JSON dialogue, validates it with Pydantic, runs eight task packs against transparent generic terms, and serializes a typed report. It has no remote model, private policy corpus, or external score service.

```mermaid
flowchart LR
    I["Synthetic dialogue JSON"] --> V["Pydantic request validation"]
    V --> E["Deterministic evaluation engine"]
    E --> P1["Summary and resolution"]
    E --> P2["Root cause and coaching"]
    E --> P3["Safety, factuality, transfer packs"]
    P1 --> R["Typed JSON report with evidence"]
    P2 --> R
    P3 --> R
    R --> C["CLI, FastAPI, example report"]
    L["Optional local LLM adapter"] -. validated extension .-> E
```

## Boundaries

- `schemas.py` is the request and response contract. Unknown input and report fields are rejected.
- `engine.py` contains the deterministic, public-safe task-pack logic and emits `insufficient_evidence` rather than guessing.
- `cli.py` loads a fixture or caller-supplied local JSON and writes the same structured report as the API.
- `api.py` is a minimal FastAPI wrapper with `/healthz` and `/v1/evaluate`.
- `LocalLLMAdapter` is a protocol only. An implementation must be local, independently evaluated, schema-validated, and able to cite the supplied evidence before being exposed.

The Docker image runs only the API. It does not add authentication, data retention, queueing, or a production policy engine.
