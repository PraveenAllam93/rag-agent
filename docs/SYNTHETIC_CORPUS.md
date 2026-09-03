# Synthetic corpus

**Version:** v1 (generated 2026-09-02)

Every document exists to exercise a specific pipeline path. A document that does not have
one should not be generated — corpus size is not the goal, coverage is.

Documents are produced by seeded generators, not written by hand, so the corpus is
reproducible and the golden set can be emitted in the same pass.

## Manifest

| Document | Exercises | Notes |
| --- | --- | --- |
| `ar_fy2025.pdf` | dense retrieval, citations, MD&A synthesis | fictional company, native PDF |
| `ar_fy2026.pdf` | cross-document, comparison | revenue up, EBITDA margin down; MD&A explains the cause |
| `financials.xlsx` | Analysis Agent, SQL path | numbers must match both reports exactly |
| `contract_v1.pdf` | exact-identifier retrieval | clause identifiers, defined terms |
| `contract_v2.pdf` | deterministic diff | payment 30→15 days, notice 60→90, one clause added, one removed |
| `ar_fy2025_scanned.pdf` | OCR path | rendered to image and degraded |
| `policy_injection.pdf` | prompt injection defence | contains an instruction telling the model to ignore prior instructions and disclose its system prompt |
| `globex_ar_fy2025.pdf` | tenant isolation | second tenant, same filename shape, similar prose, different numbers |
| `board_memo_fy2026.docx` | DOCX parsing, heading-based structure extraction, cross-document corroboration | internal memo referencing the same FY2026 margin decline as `ar_fy2026.pdf`'s MD&A — must not contradict it |
| `quarterly_financials.csv` | CSV ingestion path (distinct loader from XLSX), Analysis Agent SQL path at quarterly grain | quarters must sum to the annual figures in `financials.xlsx` |

## Deliberate absences

These facts are **not** in any document, and exist to be asked about:

- Executive compensation
- Employee headcount by region
- Any figure for FY2027

Questions targeting these are `unanswerable` cases. Correct behaviour is explicit
abstention naming what was searched.

## Consistency requirements

The XLSX, the FY2025 report, and the prior-year comparatives inside the FY2026 report must
all agree. Inconsistency here surfaces later as an eval failure that looks like a retrieval
bug and takes a day to trace.

The two tenants' documents must be similar enough that a leak would actually be retrieved.
Isolation tests against dissimilar corpora pass for the wrong reason.

## Versioning

Bump the corpus version on any change to document content. Record it in every eval result.
Numbers across corpus versions are not comparable.

## Regenerating

The generator is standalone tooling under `data/synthetic/`, deliberately isolated from
the project's future real `pyproject.toml` — it exists only to produce fixture data.

```bash
cd data/synthetic
uv venv .venv-corpus && uv pip install --python .venv-corpus/bin/python -r requirements.txt
./.venv-corpus/bin/python generate.py --seed 42 --check
```

Outputs `documents/` (the 10 files above), `golden_set.jsonl` (paired eval cases, schema
per `docs/EVALUATION.md`), and `manifest.json` (tracked — file hashes, corpus version,
golden-set category/holdout counts). `documents/` and `golden_set.jsonl` are gitignored;
only the generator code and `manifest.json` are committed. All figures and narrative facts
come from `lib/facts.py`, the single source of truth every generator reads from — that's
what keeps the XLSX, CSV, PDFs and DOCX consistent with each other by construction.
