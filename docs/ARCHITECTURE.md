# Architecture

Condensed working reference. The full narrative specification lives in
`Document_Intelligence_Agent_Architecture.docx`. This file is what Claude Code reads; keep
it current, and prefer editing this over the docx when they diverge.

## Shape

```
Client → FastAPI → Supervisor → specialist agent → tools → evidence → answer + citations
                 ↘ upload → queue → worker → parse/OCR → chunk → embed → index
```

Two independent paths. The ingest path is asynchronous and eventually consistent; the query
path is synchronous and latency-bound. They share only Postgres and the vector store.

## Subsystems

| Subsystem | Responsibility | Technology |
| --- | --- | --- |
| API | auth, CRUD, orchestration entry, SSE streaming | FastAPI |
| Ingestion | parse, OCR, structure, chunk, embed, index | Python workers, arq |
| Retrieval | filter, hybrid search, fuse, rerank, bundle | Qdrant |
| Agents | stateful workflows over tools | LangGraph |
| Analytics | SQL + sandboxed Python | Postgres + container |
| Reporting | PDF/DOCX, citation validation | reportlab / python-docx |
| Metadata | tenants, users, docs, jobs, audit, analytics tables | Postgres 16 |
| Blob | originals and generated artifacts | MinIO / S3 |
| Observability | traces, cost, latency | OpenTelemetry → Langfuse |

## Domain model

`Tenant → Users, Collections, Documents, Conversations, Reports, AuditEvents`

`Document → versions → Blocks → Chunks`

The `Block` layer sits between the parsed document and the chunks, and it is the reason
citations can resolve to a page and a bounding box. See `.claude/rules/ingestion.md`.

Chunk payload in Qdrant carries: `tenant_id`, `document_id`, `collection_id`,
`document_version`, `page`, `heading_path`, `chunk_index`, `parent_section_id`,
`acl_groups`, `content_hash`, `created_at`.

Payload indexes on: `tenant_id` (with `is_tenant=True`), `collection_id`, `document_id`,
`acl_groups`, `document_version`. An unindexed filter field is a latency bug you will not
see in results.

## Query path in detail

1. Authenticate; build execution context (`tenant_id`, `user_id`, resolved `acl_groups`).
2. Supervisor classifies intent and constructs a plan.
3. Specialist agent invokes tools. Tools re-authorize against the context independently.
4. RAG tool: normalize query → build filter → dense + sparse prefetch → RRF fusion →
   cross-encoder rerank → dedupe → context budget → evidence bundle.
5. Generation, from the bundle only, with evidence delimited and labelled untrusted.
6. Citation validation against chunk ids.
7. Response with `trace_id`; telemetry and audit written.

## Agent responsibilities

| Agent | Does | Does not |
| --- | --- | --- |
| Supervisor | classify, plan, route, inspect, decide next step | produce the final answer directly |
| Research | multi-document evidence gathering and synthesis | compute numbers |
| Analysis | generate + execute SQL/Python, interpret results | do arithmetic in the completion |
| Comparison | deterministic diff + semantic impact explanation | decide equality by generation |
| Report | outline, bind evidence, generate, validate citations | search for its own evidence |

Compliance Agent is deliberately out of scope for v1. It needs a real policy corpus and a
real domain problem; without those it is a demo, not a capability.

## Deferred

Multi-agent swarms, fine-tuning, real-time collaboration, voice, domain rule engines.
