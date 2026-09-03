# Glossary

**Block** — A typed unit of parsed document structure carrying page, bbox, type, and
heading path. Sits between the raw document and chunks. The reason citations can resolve.

**Chunk** — An embedded, retrievable slice of a document, built from blocks. Carries
metadata and ACL groups.

**Dense retrieval** — Semantic search over embeddings. Strong on paraphrase, weak on exact
identifiers.

**Sparse / BM25** — Lexical retrieval. Strong on identifiers, codes, and names; weak on
paraphrase. The complement to dense, which is the whole argument for hybrid.

**RRF** — Reciprocal Rank Fusion. Combines ranked lists by rank rather than score, so it
needs no normalization between retrievers.

**Reranker** — Cross-encoder scoring query and passage jointly. Improves ordering within a
candidate set. Cannot improve recall.

**Evidence bundle** — Structured set of retrieved chunks with provenance and scores, passed
to generation. Never a concatenated string.

**Execution context** — Request-scoped `tenant_id`, `user_id`, resolved `acl_groups`,
`trace_id`. Constructed from the verified JWT, passed explicitly, never model-supplied.

**Groundedness / faithfulness** — Degree to which generated claims are supported by the
evidence actually retrieved.

**Abstention** — Explicitly declining to answer when evidence is insufficient. A measured
outcome, not a fallback.

**Small-to-big** — Retrieve small chunks for precision, expand to the parent section for
generation context.

**RLS** — Postgres Row Level Security. Database-enforced tenant filtering, the backstop for
application-level filters.

**Tenant payload index** — Qdrant payload index created with `is_tenant=True`, which groups
storage by tenant so filtered queries touch contiguous data.
