# Architecture

`fixtures/synthetic_dialogue.json` is passed to `evaluate_dialogue`. The input validator accepts only generic `customer` and `agent` turns. Independent deterministic rule groups then produce a JSON-safe report for sentiment, resolution, transfer, generic review signals, and failure handling.

```text
synthetic dialogue -> input validation -> rule adapters -> structured report
```

Production integrations are intentionally outside scope. A future adapter must preserve explicit schema validation, auditability, data minimization, and human review boundaries.
