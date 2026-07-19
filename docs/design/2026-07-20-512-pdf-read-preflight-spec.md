# #512 — PDF read-integrity preflight for locally-extracted page/quote anchors

**Date:** 2026-07-20 · **Issue:** #512 · **Status:** implemented in the same PR

## Problem

The v3.7.3 Three-Layer Citation Emission guards locator *presence* and the #182 gate guards
citation *existence*, but nothing guards the **local extraction channel** those locators come
from. PDF readers silently truncate documents with malformed cross-reference tables and
misreport page counts; a real, correctly-cited source can then acquire an apparently valid
`page` anchor derived from a truncated or mispaginated read and pass every existing gate
(the emitters anchor in good faith from poisoned context; the v3.7.3 lint checks anchor
shape, not faithfulness; the #182 gate reduces anchors to a kind-only boolean).

Provenance: mechanism observed in kengo006/alexandria (page-tree `/Count` cross-check before
trusting page numbers); dual-track in-repo verification (2026-07-11) confirmed the gap.

## Design

Two layers, enforcement upstream of the writers (Bucket A agents cannot run Bash):

### Layer 1 — `scripts/pdf_read_preflight.py`

Stdlib CLI + `pypdf` for object plumbing, following the repo's existing
`verify_submission_package.py` precedent (`try: import pypdf / except ImportError: pypdf =
None`; CI installs it via `requirements-dev.txt`, local runs without it degrade). Not "grep
the first `/Count`": pypdf's xref machinery covers classic tables, xref streams, `/Prev`
incremental-update chains, and object streams; the script then computes **three independent
page-count signals** on top of it:

1. `declared_page_count` — the root page tree's `/Count`, read from the raw `/Root → /Pages`
   object (not from pypdf's page list).
2. `enumerated_page_count` — a recursive walk of `/Kids`, counting `/Type /Page` leaves,
   with a visited-set cycle guard and a node budget.
3. `reader_page_count` — `len(reader.pages)` (pypdf's own flattening), as a third opinion.

Parser warnings are captured from the `pypdf` logger (repair chatter is exactly the
"silently repaired xref" signal the issue names) and recorded.

**Trailing-data check** (cross-model review round 1, P1): a PDF truncated partway through
an incremental update keeps an OLDER valid `%%EOF`; pypdf silently reads that previous
revision, so all three counts agree on the OLD page tree — the exact truncation case the
preflight exists to catch. Non-whitespace bytes after the LAST `%%EOF` are that
signature: recorded as a `trailing-data` warning and a PASS veto. Complete incremental
updates always end with their own `%%EOF`, so legitimate multi-revision files pass.

**Verdict** (single enum, mirrors the repo's PASS-posture vocabulary):

| Verdict | Condition |
|---|---|
| `PASS` | all three counts agree, count > 0, no captured parser warnings, no trailing data after the final `%%EOF` |
| `FAIL` | parse completed but the counts disagree — the truncation/mispagination signal |
| `UNAVAILABLE` | anything preventing a confident parse: unreadable/missing file, encryption, missing/malformed page tree, cycle or node-budget hit, pypdf not installed, count agreement but parser-repair warnings or trailing data present |

Parser warnings captured before a structural failure survive every early exit (they are
appended in the capture handler's `finally`), so a repair warning that preceded a later
encryption/tree error still reaches the sidecar.

`UNAVAILABLE` (not `FAIL`) on repair warnings with agreeing counts: a repaired read may
still be complete, but the preflight cannot vouch for it — and only `PASS` licenses a page
anchor downstream, so the conservative bucket is the honest one.

**Sidecar** — JSON to stdout or `--output`; shape (`schema: "pdf_read_preflight/1"`):

```json
{
  "schema": "pdf_read_preflight/1",
  "verdict": "PASS | FAIL | UNAVAILABLE",
  "file": "<path as given>",
  "sha256": "<file hash, null when unreadable>",
  "declared_page_count": 12,
  "enumerated_page_count": 12,
  "reader_page_count": 12,
  "warnings": ["<pypdf/parser warnings, structural notes>"],
  "generated_at": "<UTC ISO-8601>",
  "tool": "pdf_read_preflight/<version>"
}
```

Exit code 0 whenever a verdict was produced (the verdict is data, not an error); 2 on usage
errors only — so orchestration can always consume the JSON without exit-code branching.

### Layer 2 — prompt rules

- **Three emitters** (`synthesis_agent`, `draft_writer_agent`, `report_compiler_agent`): a
  `PDF Read-Integrity Precondition (#512)` rule appended inside the existing
  `## Three-Layer Citation Emission (v3.7.3)` section — a `page` anchor whose value derives
  from a locally-read PDF may be emitted only when the orchestration layer supplied a
  preflight `PASS` for that file; on `FAIL`/`UNAVAILABLE` (or no sidecar), emit
  `anchor:none` (the existing precedence-zero NO-LOCATOR machinery then surfaces it) or an
  independently-visible non-page locator, plus an explicit PDF-integrity warning line. The
  R-L3-1-C no-frontmatter-reads inversion is untouched: the sidecar verdict arrives in
  context like the corpus itself.
- **`claim_ref_alignment_audit_agent`** (the Stage 4→5 L3 audit): the precondition binds to
  the existing Step 2 `ref_retrieval_method == manual_pdf` discriminator (the machine-readable
  "locally-read PDF" signal), not a re-inferred prose test. Sidecars join on `ref_slug`; the
  sidecar `sha256` is confirmatory only — until #513's read ledger lands, no anchor-side field
  carries a file hash, so a hash cannot be the primary key. Non-`PASS` or missing sidecar
  becomes the `[pdf_read_integrity_unverified]` advisory rationale tag (never an UNSUPPORTED
  verdict on this basis alone — terminality stays with the existing formatter gate machinery).
- **Executable audit path** (cross-model review round 1, P1): the prose rule alone never
  executes in `scripts/claim_audit_pipeline.py`. `run_audit_pipeline` gains
  `pdf_preflight_sidecars: dict[ref_slug → sidecar] | None` — `None` (unwired caller) is
  byte-equivalent legacy; a provided map tags every completed `manual_pdf` page-anchor row
  without a `PASS` sidecar at the single Step-6 emission point, AFTER cache resolution, so a
  cache hit cannot bypass the check and the tag never enters the cached judge body. The tag
  is appended (INV-6/INV-14 `startswith` contracts untouched) within the rationale budget.
  `claim_audit_finalizer.classify_claim_audit_result` surfaces
  `[LOW-WARN-PDF-READ-INTEGRITY-UNVERIFIED]` (advisory, never gate-refuse) on SUPPORTED rows
  carrying the tag — otherwise the expected common case (content-based fallback finds
  support) would render the advisory invisible at the formatter.
- **`pipeline_orchestrator_agent`** (the layer that CAN run Bash): run the preflight once per
  locally-read PDF in the `literature_corpus[]` **at Stage 1 corpus intake, independent of
  audit mode** (cross-model review round 1, P1: the Stage 4→5 audit is opt-in default OFF
  while the emitters run earlier — an audit-gated preflight would leave default-mode runs
  sidecar-less at R-L3-1-D, forcing valid local-PDF page citations to `anchor:none` and a
  gate refusal). Deliberately NOT "only PDFs that sourced a page anchor": anchor→file
  provenance is not recorded anywhere the orchestrator can read, an extra preflight is cheap
  and deterministic, and the audit side narrows via `manual_pdf`. Sidecars ride the emitters'
  and audit contexts keyed by `ref_slug`. This file is one of the five #528 content-locked
  surfaces — the `CONTENT_LOCKS` hash in `scripts/check_pipeline_boundary_semantics.py` is
  updated in the same commit per that lint's documented procedure.

## Out of scope (deliberate, from the issue)

- Extending `check_v3_7_3_three_layer_citation.py` (it lints emitted Markdown, not PDFs).
- Quote-accuracy verification against source text (the L3 claim-audit channel, tracked
  separately).
- A passport schema aggregate. The sidecar is a file-level retrieval artifact; if #513
  (`read_scope` ledger) lands, the sidecar's `sha256` + verdict are the natural join keys,
  and naming here follows `citation_provenance.schema.json` precedent for that future join.

## Test plan

`scripts/test_pdf_read_preflight.py` (auto-discovered by `pytest.yml`'s `pytest scripts/`),
synthetic in-test PDFs (no binary fixtures): flat valid PDF (PASS), nested page tree (PASS,
enumeration exercises recursion), lying root `/Count` (FAIL), truncated tail (UNAVAILABLE or
FAIL, never PASS), encrypted marker (UNAVAILABLE), page-tree cycle (UNAVAILABLE via guard),
non-PDF bytes (UNAVAILABLE), missing file (UNAVAILABLE), pypdf absent (monkeypatched →
UNAVAILABLE with `pypdf-not-installed` warning), sidecar shape + hash stability, exit codes.
