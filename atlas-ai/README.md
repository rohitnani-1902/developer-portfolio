# Atlas AI Studio

Three focused workspaces share one evidence-grounded backend: **Research Desk**, **Code Lens**, and **Ops Flow**. The interface includes source management, execution traces, saved results, draft review and Markdown exports.

## Run locally

Requires Python 3.12+ and a modern browser. Runtime dependencies: Python standard library only.

```sh
python server.py
```

Open http://127.0.0.1:8770. Select a workspace, load its example sources, then run local analysis. Local analysis requires no provider key. Source documents are submitted to the backend for processing; the application does not persist or log document bodies there. Browser storage saves sources and results on this device.

## The three workflows

1. **Research Desk:** bounded text ingestion → overlapping passages with source/line provenance → BM25 ranking → cited excerpts. Optional AI synthesis compares sources and builds a structured brief.
2. **Code Lens:** Python syntax parsing and explicit risky-pattern checks → file/line findings → contextual AI explanation and suggested changes. Uploaded code is never executed. Static findings are review flags, not a complete security audit.
3. **Ops Flow:** the first source is the incoming customer request; subsequent sources are policy context. Keyword rules classify the request and propose a generic response template. Optional AI generation uses request and policy excerpts. Draft edits invalidate previous approval. Review is recorded locally; there are no email, payment, CRM or external-action integrations.

## Enable real AI

Set `OPENAI_API_KEY` in the server environment, or `AI_GATEWAY_API_KEY` for Vercel AI Gateway. Do not put provider keys in the browser or commit them. An environment file is provided as a reference; it is not loaded automatically.

The default model is `gpt-5.4-mini` for OpenAI, or `openai/gpt-5.4-mini` for Gateway. Set `ATLAS_MODEL` to a supported model with structured-output support. Generated results must satisfy a JSON schema. Claim citations must refer to supplied evidence IDs; missing or unknown references withhold the result. This validates reference integrity, not whether the cited text truly supports every claim. Human review is still needed.

When `VERCEL` is set, billable generation additionally requires an `ATLAS_ACCESS_TOKEN` server setting. Enter that workspace token in the UI's AI access panel; it stays in the current tab. This is a small private-demo gate, not a multi-user authentication system.

**Verification status:** the configured OpenAI account accepted a model-list request, but a real generation smoke check returned `credit_balance_exhausted`. Successful real-model generation has not been verified. Provider errors are displayed; the application does not substitute simulated AI answers.

## Architecture

```text
Browser: three workspaces, local storage, review state, export
     │ POST /api/atlas: bounded JSON source text + task
     ▼
Python API: validation, origin check, request trace
     ├── Research: chunking → BM25 → evidence
     ├── Code: AST syntax check + pattern flags
     └── Ops: request classification + response template
     │ optional generation with server-held credentials
     ▼
Model provider: strict structured response
     │ schema/type validation + citation-ID validation
     ▼
Reviewable result with provenance and trace → save/export
```

Each request accepts up to 12 sources, 50,000 characters per source, 150,000 total source characters, 300 passages and a task of 2,000 characters. Code and Ops context prioritizes one passage per source and flagged code passages, within a 20-passage budget. Research returns up to six lexical matches. Content beyond selected evidence is not sent to the model.

Request traces record a generated ID, elapsed time, source and passage counts and a short content fingerprint. Model calls time out after 45 seconds. Two concurrent calls and six calls per minute per process bound a private demo; these limits are not distributed across hosting instances.

## Verification

```sh
python -m unittest discover -s tests -p "test_*.py" -v
node --check public/app.js
```

Seventeen backend checks cover retrieval/no-evidence handling, provenance, Unicode, chunk tails, input limits, syntax and code flags, intake classification, structured generation contracts, invalid citations, unconfigured providers, HTTP boundaries and the hosted-generation gate. Model contract tests use a clearly identified test double; they do not prove real model quality.

Browser checks verify the three example flows, save/reopen behavior and draft review. To explicitly run the small, billable, real-provider fixture check after adding provider credit:

```sh
python tests/smoke_model.py
```

## Deploy

The portfolio release places the UI at `/projects/atlas-ai/`, the Python handler at `/api/atlas`, and shares the same core with local runs. Public preview supports local analysis. Hosted AI is disabled until provider credentials, credit and the private workspace token are configured.

For containers: build this folder and publish port 8770. The Docker entrypoint binds to `0.0.0.0`; local runs default to `127.0.0.1`. Set a workspace token before exposing a model-enabled instance.

## Current boundaries

This is an integrated portfolio MVP, not a production SaaS service. There is no PDF/OCR parser, semantic embeddings, repository execution sandbox, background task queue, team database, distributed rate limiter or user authentication. Browser storage is unencrypted and device-local. Remove sources and saved results when finished. Upload only context you are permitted to process. Research excerpts and AI-generated suggestions require review; code checks do not establish that a project is safe.

Next milestones: independently labeled retrieval evaluation, PDF ingestion, semantic retrieval, per-user authentication/storage, distributed usage budgets, and opt-in business connectors with explicit action approval.

Provider references: [OpenAI structured outputs](https://developers.openai.com/api/docs/guides/structured-outputs) · [Vercel OpenAI-compatible API](https://vercel.com/docs/ai-gateway/sdks-and-apis/openai-chat-completions).

Research source coverage lists every uploaded source, matched question terms, selected citations and a representative excerpt. It distinguishes no lexical match from exclusion by the six-passage limit. Duplicate filenames retain separate source IDs. This view does not automatically detect contradictions or prove coverage; inspect dates, numbers and assumptions in the original excerpts. Coverage also accompanies Markdown exports.
