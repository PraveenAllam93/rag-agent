# Roadmap

Ordered by dependency. Each phase has an exit criterion that is observable, not a feeling.

The ordering differs from the original specification in one place: **evaluation moves ahead
of hybrid retrieval and reranking.** Building those first means building them blind. The
sentence you want later is "adding a cross-encoder moved Recall@5 from 0.71 to 0.86", and
that sentence requires the harness to exist before the reranker does.

---

**Phase 1 — Foundation**
Postgres schema with `tenant_id` and RLS on every tenant-scoped table. JWT auth. MinIO.
Docker Compose for the whole local stack.
*Exit:* two tenants exist, a user authenticates, and
`tests/integration/test_tenant_isolation.py` passes against seeded data. This test is
written in Phase 1 and never removed.

**Phase 2 — Synthetic corpus**
Generators for the document set in `docs/SYNTHETIC_CORPUS.md`, producing documents and
paired golden-set entries in the same pass.
*Exit:* `make corpus` reproducibly generates the corpus from a seed, and the golden set has
50+ cases across all categories including explicitly-absent facts.

**Phase 3 — Ingestion**
Upload → validate → store → queue → parse → block model → chunk → persist. State machine
with dead-letter handling. OCR path.
*Exit:* a scanned PDF and a native PDF both reach READY, and every chunk resolves to a page
number that is correct when checked by hand against the source.

**Phase 4 — Dense retrieval and citations**
Embeddings, Qdrant collection with tenant payload index, filtered search, evidence bundle,
generation with citations.
*Exit:* a question returns an answer whose citation resolves to the correct document, page,
and section. Isolation test still green with vectors in play.

**Phase 5 — Evaluation harness**
Recall@k, MRR, nDCG, Precision@k against the golden set. Result recording with full
configuration. Baseline established.
*Exit:* `make eval` prints a baseline and writes it to `evaluation/results/`.

**Phase 6 — Hybrid retrieval**
Sparse vectors, Query API prefetch, RRF fusion.
*Exit:* measured delta against the Phase 5 baseline, segmented by category, recorded in
`EXPERIMENTS.md`. Exact-identifier cases should improve markedly; if they do not, the
implementation is wrong and the aggregate number would have hidden it.

**Phase 7 — Reranking**
Cross-encoder over a wide candidate set.
*Exit:* MRR and nDCG improve with recall roughly flat, and the latency cost is recorded.

**Phase 8 — Research Agent**
LangGraph workflow: query planning, retrieval, evidence assessment, synthesis, citation
binding, abstention.
*Exit:* multi-document questions answered with per-document citations, and the
deliberately-absent facts produce explicit abstention rather than invention.

**Phase 9 — Comparison Agent**
Structured extraction, section alignment, deterministic diff, semantic impact.
*Exit:* the contract V1/V2 payment-term change is detected by code, not by generation, and
the explanation of its business impact is cited.

**Phase 10 — Analysis Agent**
Analytics schema, read-only SQL role, sandboxed Python, chart generation.
*Exit:* the margin-decline question is answered with numbers that came from a tool result
and an explanation that came from retrieved commentary. Sandbox escape attempts fail.

**Phase 11 — Supervisor**
Intent classification, planning, routing, bounded loops, checkpointing.
*Exit:* a three-part request decomposes correctly, and the trace shows why each specialist
was invoked.

**Phase 12 — Report Agent**
Outline, evidence binding, generation, citation validation, PDF/DOCX.
*Exit:* a generated report where every factual claim carries a citation that a validator
confirms actually supports it.

**Phase 13 — Observability**
OpenTelemetry spans throughout, Langfuse, token and cost tracking, generation metrics in
the eval harness.
*Exit:* one trace shows the full path from request to answer with per-stage latency and
cost.

**Phase 14 — Security hardening**
Prompt injection defences, rate limiting, request limits, audit log completeness, secrets
management.
*Exit:* `/tenant-audit` reports clean, and the injection document in the corpus is refused.

**Phase 15 — Deployment and CI/CD**
GitHub Actions, image builds, regression gate, staging on the homelab.
*Exit:* a push runs lint, types, tests, and the retrieval regression gate, then deploys.

---

## What "done" means for the first milestone

Not "the chatbot works". The first real milestone is: a user uploads a document, the system
processes it asynchronously, indexes it with metadata and permissions, answers a question
using hybrid retrieval and reranking, and returns a citation pointing at the correct page —
while a second tenant holding a near-identical document sees none of it.
