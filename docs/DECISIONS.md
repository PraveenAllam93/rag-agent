# Architecture decision records

Format: Context, Options, Decision, Consequences, Reversal cost, Status.

An ADR records a decision that was genuinely open. Do not write ADRs for choices with one
plausible answer.

---

## ADR-001 — Shared-schema multi-tenancy with Postgres RLS

**Context.** Multiple tenants share one deployment. Isolation failures in this class of
system are silent: nothing errors, the wrong data simply appears in an answer.

**Options.** (a) Database per tenant — strongest isolation, operationally heavy, migrations
multiply, poor fit for a homelab. (b) Schema per tenant — middling on every axis, connection
pooling gets awkward. (c) Shared schema with `tenant_id` and RLS — one migration path, one
pool, isolation enforced by the database rather than by developer discipline.

**Decision.** (c). `tenant_id` on every tenant-scoped table, RLS policies on all of them,
`SET LOCAL app.tenant_id` at transaction start. Application-level filtering remains as the
first layer.

**Consequences.** Every session must set the GUC or queries return nothing — a loud failure,
which is the desired direction. RLS adds planning overhead. A misconfigured superuser
connection bypasses RLS entirely, so the application role must not be superuser and that
needs a test.

**Reversal cost.** Moderate. Moving to database-per-tenant later is a data migration, not a
rewrite, because `tenant_id` is already the partition key everywhere.

**Status.** Accepted.

---

## ADR-002 — Qdrant over Chroma and pgvector

**Context.** Every query in this system is filtered by tenant, and usually by ACL group and
collection as well. Filtered ANN behaviour is therefore the deciding property, not raw
unfiltered recall or benchmark QPS.

**Options.** (a) Chroma — simplest to start, but metadata filtering behaves closer to
pre/post filtering and degrades badly as the filter becomes selective, which is precisely
this workload. (b) pgvector — collapses the stack by one service, and RLS would cover
vectors too, which is genuinely attractive; weaker at hybrid search and at high-cardinality
filtered ANN. (c) Qdrant — filtering applied during graph traversal, native sparse vectors,
server-side fusion in the Query API, and a documented tenant payload-index pattern.

**Decision.** (c) Qdrant. Single collection, `tenant_id` payload index with `is_tenant=True`.

**Consequences.** One more service to run and monitor. Vector-store isolation is enforced by
application-supplied filters rather than by the database, so the isolation test carries more
weight than it would under pgvector.

**Reversal cost.** Low-moderate. Re-indexing from stored chunks is a batch job, and the
retrieval interface is behind a service boundary.

**Status.** Accepted. pgvector remains a reasonable fallback below roughly one million
chunks and should be reconsidered if operational burden becomes the binding constraint.

---

## ADR-003 — Structured block model rather than Markdown as the parsed representation

**Context.** The citation model requires document, version, page, and section. Converting
parsed documents to Markdown and chunking the Markdown is the common shortcut.

**Options.** (a) Markdown as storage — simple, one format, every tool understands it, but
page numbers and bounding boxes do not survive the conversion. (b) Typed block model with
Markdown generated on demand for model consumption.

**Decision.** (b). Blocks carry page, bbox, type, and heading path. Markdown is a rendering.

**Consequences.** More code in the parser and a schema to maintain. In exchange, citations
resolve to a page, PDF highlighting becomes possible without reprocessing, and structure-
aware chunking has real structure to work with.

**Reversal cost.** High if deferred. Adding provenance later means reprocessing the entire
corpus and invalidating every stored eval result.

**Status.** Accepted.

---

## ADR-004 — Postgres for RBAC; no MongoDB

**Context.** The system needs somewhere to store tenants, users, roles, permissions, jobs,
audit events, and the tabular data the Analysis Agent queries.

**Options.** (a) MongoDB for flexibility. (b) Postgres for everything.

**Decision.** (b). RBAC is inherently relational — users to roles to permissions to
resources — and wants foreign keys, transactions, and RLS. Postgres is required anyway for
the analytics schema and for job state. Adding Mongo means operating two databases to do one
database's work, and forfeits RLS, which is the isolation mechanism in ADR-001.

**Consequences.** Schema migrations are mandatory discipline rather than optional. JSONB
covers the genuinely schemaless metadata cases.

**Reversal cost.** High, and there is no identified reason to reverse.

**Status.** Accepted.

---

## ADR-005 — Container as the Python execution boundary

**Context.** The Analysis Agent generates and executes Python. Model-generated code is
untrusted by construction.

**Options.** (a) AST allowlisting in-process — fast, simple, and defeated by any escape not
on the list, which is an open-ended set. (b) Container isolation — no network, read-only
rootfs, non-root, resource and time limits, seccomp. (c) WASM via Pyodide — no syscall
surface at all, weaker library support, awkward for pandas-heavy analysis.

**Decision.** (b), with AST checking retained purely as a fast pre-filter that produces
useful error messages.

**Consequences.** Container startup latency on every analysis, mitigated by a warm pool.
Data must be materialized to a read-only mount rather than passed in memory.

**Reversal cost.** Low. The execution interface is a single tool.

**Status.** Accepted. Pyodide worth revisiting if per-call latency becomes the constraint.

---

## ADR-006 — Queue: arq or Celery

**Context.** Ingestion is asynchronous. FastAPI is async; Celery is not natively.

**Options.** (a) Celery — ubiquitous, well documented, recognized on a CV, and awkward
inside an async codebase. (b) arq — async-native, much smaller, less material available when
something goes wrong.

**Decision.** Not yet made.

**Consequences.** Pending.

**Reversal cost.** Low. Job handlers should be written as plain async functions with the
queue framework as a thin adapter, which keeps this cheap either way — do that regardless of
which is chosen.

**Status.** Provisional. Decide before Phase 2 and update this record.
