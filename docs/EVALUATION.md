# Evaluation

## Why this exists early

Retrieval changes are indistinguishable from noise without measurement. Every interesting
claim about this system — that hybrid beats dense, that reranking helps, that the chunker
matters — is either a number or an opinion.

## Golden set

Generated alongside the corpus. Each case:

```json
{
  "id": "gc_0142",
  "question": "What was consolidated revenue in FY2025?",
  "expected_answer": "412 crore",
  "expected_key_facts": ["412"],
  "relevant_document_ids": ["doc_ar_fy2025"],
  "relevant_pages": [14],
  "relevant_chunk_hints": ["consolidated revenue"],
  "category": "fact_lookup",
  "difficulty": "easy",
  "corpus_version": "v3",
  "answerable": true
}
```

Categories, with what each is meant to stress:

| Category | Stresses |
| --- | --- |
| `fact_lookup` | basic dense retrieval |
| `exact_identifier` | sparse retrieval — this is where BM25 earns its place |
| `multi_hop` | evidence assembly across sections |
| `cross_document` | multi-document research |
| `comparison` | version alignment and diff |
| `analytics` | SQL/Python path, not retrieval |
| `unanswerable` | abstention |
| `injection` | prompt injection refusal |

Hold out 20% of cases and never inspect them while tuning. Tuning against the full set
produces a model of the golden set rather than of retrieval.

## Metrics

**Retrieval.** Recall@k (was the evidence retrieved at all — the ceiling on everything
downstream), MRR (how high the first relevant result landed), nDCG (graded ordering
quality), Precision@k (how much of the context was noise).

**Generation.** Faithfulness, answer relevance, citation correctness, citation
completeness, abstention quality. Abstention quality deserves equal billing: a system that
answers everything scores well on relevance and is dangerous.

**Agents.** Task success, tool-call count, expected-trajectory match, loop rate. Assertions,
not judges.

**Cost.** p50/p95 latency and tokens per query alongside every quality number. A quality
result without its cost is half a result.

## Result records

`evaluation/results/<timestamp>_<config_hash>.json` with the full configuration: embedding
model, chunk size, overlap, candidate width, fusion method and weights, `top_k`, reranker,
prompt version, corpus version, seed. `EXPERIMENTS.md` holds the narrative log.

Numbers from different corpus versions are not comparable. Do not put them in the same
table.

## Regression gate

30 pinned cases in CI. Recall@5 dropping more than 2 points fails the build. The gate is
what stops an unrelated chunking change from quietly degrading retrieval.
