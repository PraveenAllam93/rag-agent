# Document Intelligence & Agentic RAG Platform

Multi-tenant document intelligence system. Users upload documents, ask questions across
them, compare versions, run numerical analysis, and generate evidence-grounded reports.
RAG is a reusable tool, not a chatbot feature.

Full spec: `docs/ARCHITECTURE.md`. Decisions and their rationale: `docs/DECISIONS.md`.
Build order and exit criteria: `docs/ROADMAP.md`.

<!-- This file is loaded into every session. Keep it under 200 lines. Anything that only
matters for one part of the codebase belongs in .claude/rules/ with paths: frontmatter. -->

## Working agreement — read before doing anything

**Default mode is advisory, not autopilot.** The owner is building this to develop
engineering depth. Writing the code for them defeats the purpose of the project.

Unless the message contains an explicit build instruction, do not write implementation
code. Instead: explain the approach, name the trade-off that actually matters, point out
the failure mode the naive version has, and offer to write a failing test.

Explicit build instructions look like "implement X", "write it", "scaffold", "generate the
file", "fix this". Questions ("how do I…", "what about…", "should I…", "can we…") are
questions. Answer them.

**Allowed without asking:**
- Reading code, running tests, running linters and type checks
- Writing tests, especially failing tests that pin down desired behaviour
- Reviewing a diff against `.claude/rules/security-invariants.md`
- Generating synthetic corpus data under `data/synthetic/`
- Writing docs, ADRs, and evaluation harness scaffolding

**Never without being asked:**
- Refactoring code the owner just wrote
- Adding a dependency
- Changing chunk size, `top_k`, fusion weights, reranker model, or prompt text — these are
  experiment variables, and changing one silently invalidates every eval number on record
- Writing a whole module when the question was about one function

## Review standard

Lead with the most serious problem. Do not open with praise. If code is correct but naive
in a way that breaks at scale, say so *and say at what scale*. If it's fine, say it's fine
and stop talking.

## Stack

Decisions are recorded in `docs/DECISIONS.md`. Do not silently substitute alternatives.

| Layer | Choice | Note |
| --- | --- | --- |
| API | FastAPI, Python 3.12, async | |
| Metadata + RBAC + analytics | PostgreSQL 16 | Row Level Security is load-bearing |
| Vector store | Qdrant | one collection, tenant payload index |
| Sparse | Qdrant sparse vectors (BM25-style) | fused server-side via Query API |
| Reranker | cross-encoder from HuggingFace, local | `bge-reranker-v2-m3` baseline |
| Parsing | Docling primary; PyMuPDF + pdfplumber fallback | |
| OCR | OCRmyPDF (wraps Tesseract) | writes text layer back into the PDF |
| Queue | Redis + arq | Celery is acceptable; pick one, record it |
| Object storage | MinIO locally, S3 API | |
| Agent runtime | LangGraph | |
| Tracing | OpenTelemetry → Langfuse (self-hosted) | |
| Packaging | uv, ruff, mypy strict, pytest | |

No MongoDB. RBAC is relational and needs foreign keys, transactions, and RLS.

## Non-negotiables

Full text and rationale in `.claude/rules/security-invariants.md`, which is always loaded.
Summary, so they're never more than one glance away:

1. Tenant filter is applied **inside** the search, never after it.
2. `tenant_id` and `user_id` never appear in an LLM-callable tool signature.
3. Retrieved document text is untrusted input, never a system instruction.
4. The Python sandbox boundary is the container. AST checks are a UX nicety.
5. Every cache key includes tenant and the caller's ACL group set.

## Commands

<!-- Update these as the project is scaffolded. Wrong commands are worse than none. -->

```bash
make up          # docker compose up: postgres, qdrant, redis, minio, langfuse
make down
make migrate     # alembic upgrade head
make test        # pytest -q
make test-fast   # pytest -q -m "not slow and not llm"
make lint        # ruff check . && ruff format --check .
make types       # mypy --strict .
make eval        # evaluation harness against the golden set, prints metric deltas
make corpus      # regenerate data/synthetic/ and the paired golden set
```

Run `make lint && make types && make test-fast` before proposing any commit.

## Layout

```
apps/
  api/             routes/ (thin, no business logic) + main.py (app instance, router mounts)
  dependencies/    FastAPI Depends() factories: DB session, external clients, JWT auth
  middlewares/     ASGI middleware (RBAC enforcement, etc.)
  models.py        SQLAlchemy ORM tables
  schemas/         Pydantic request/response schemas, one file per area (auth, user, tenant, ...)
  utils/           generic, stateless helpers (security.py hashing, logs.py logging) — no I/O
  repository.py    DB-I/O classes (UserRepository, TenantRepository, ...)
```

Flat under `apps/` while the system is API + identity/auth only (Phase 1). The
services/ingestion, services/retrieval, services/agents, services/analytics,
services/reporting split — each a subsystem runnable independently of the API
process (agents via LangGraph, ingestion/eval via `make corpus`/`make eval`) —
gets introduced starting Phase 3, not before. Likewise `tools/` (LLM-callable
tools), `evaluation/` (golden sets, metrics, regression gate), and
`data/synthetic/` (generated corpus) arrive with the phases that need them.
`infrastructure/` (docker, terraform, k8s) already exists.

## Current phase

<!-- Update this line at the end of each session. It is the single most useful piece of
state in this file: it tells Claude what "next" means. -->

**Phase 0 — nothing built yet.** Next: Postgres schema with RLS, and the two-tenant
isolation test that must stay green forever (`docs/ROADMAP.md`, Phase 1).

## Things that are easy to get wrong here

- Markdown is a *rendering* of a parsed document, never the storage format. Markdown cannot
  carry page numbers or bounding boxes, and the citation model requires both.
- Small chunks retrieve better than they generate. Retrieve small, expand to the parent
  section before handing context to the model.
- ACLs in chunk payloads are group IDs, never user IDs. Storing user IDs means a permission
  change forces a re-index.
- An agent that cannot say "the documents don't cover this" is a liability. Abstention is a
  measured outcome, not a fallback.
