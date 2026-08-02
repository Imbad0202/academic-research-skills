# PDF content classification — advisory extension to the #512 read-integrity preflight

**Date:** 2026-08-01 · **Issue:** none (local addition, not yet filed upstream) · **Status:** implemented in this local repo instance, not submitted upstream

## Problem

The #512 read-integrity preflight (`scripts/pdf_read_preflight.py`) cross-checks three
independent page-count signals to guard the local-extraction channel behind a `page`
anchor — but it only vouches for page-tree **structure**. A scanned or image-only PDF
can carry perfectly consistent, agreeing page counts (three-count agreement, no parser
repair warnings, no trailing data) while `pypdf` extracts empty or meaningless text from
every page. Such a file legitimately earns a structural `PASS`, and nothing in the
existing sidecar says whether the text a `page` or `quote` anchor was minted from was
ever real. This is a distinct failure mode from the one #512 closes (structural
truncation/mispagination) and was out of that issue's scope by design (#512 §Out of
scope explicitly defers "quote-accuracy verification against source text" to the L3
claim-audit channel — this addition sits one layer earlier, at "was there text to read
at all").

Provenance: identified during an external review of candidate third-party tools for
this ARS instance (`firecrawl/pdf-inspector`, a Rust-backed PDF classification/
extraction library) against the existing preflight mechanism; not derived from an
upstream-tracked issue or external paper.

## Design

Single addition to Layer 1 (`scripts/pdf_read_preflight.py`), no Layer 2 (prompt/agent)
changes in this pass — see **Out of scope** below.

### `_classify_content()` — advisory-only, non-gating

Runs `pdf_inspector.classify_pdf_bytes(data)` (optional dependency; Rust-backed,
~10-50ms, no OCR) immediately after the file is read and hashed, **independent of and
before** the pypdf-based structural checks — so a file the structural checks later
reject (encrypted, malformed tree) is still classified, since content classification
answers an orthogonal question.

Verified against the installed package (`pdf-inspector` 0.2.6) rather than assumed from
its README: `classify_pdf_bytes()` returns an object with `pdf_type` (string, e.g.
`"text_based"` / `"scanned"`), `confidence` (float), and `pages_needing_ocr` (list of
0-indexed page numbers).

**Degradation, matching the pypdf-absent precedent but NOT identical to it**: `pypdf`
is a required dependency, so its absence is a real problem and is loudly flagged
(`UNAVAILABLE` + warning). `pdf_inspector` is a fully optional advisory extra — its
plain absence is the common, expected default state and degrades **silently** to
`available: false` (no warning). Only two things are warned about:

1. `pdf_inspector` is installed but raises on this file — a real anomaly.
2. The classification came back non-`text_based` or flagged `pages_needing_ocr` — the
   actionable finding this extension exists to surface.

**Verdict independence (the load-bearing invariant):** `result["verdict"]` is computed
purely by the pre-existing three-count-agreement / parser-warning / trailing-data logic
in `run_preflight()`. That logic reads `collector.messages` (pypdf's own parser log) and
`trailing_ok` — it never reads `result["warnings"]`, the list `_classify_content()`
appends to. This was verified by inspection of the existing verdict branch (not changed
by this patch) and pinned by test (`test_scanned_pdf_adds_advisory_warning_but_verdict_
still_pass`, `test_classification_runs_even_when_structural_verdict_is_unavailable`).

**Sidecar** — new field only, schema id unchanged (additive, backward compatible per the
`contamination_signals` precedent — absence of the field in code reading an old sidecar
is not possible here since this is a same-commit addition, but the shape stays additive
for any external consumer):

```json
{
  "schema": "pdf_read_preflight/1",
  "verdict": "PASS | FAIL | UNAVAILABLE",
  "...": "... (unchanged fields) ...",
  "content_classification": {
    "available": true,
    "pdf_type": "text_based | scanned | ...",
    "confidence": 0.97,
    "pages_needing_ocr": []
  },
  "tool": "pdf_read_preflight/1.1.0"
}
```

`content_classification` is `null` only when the file was never read far enough to
attempt classification (unreadable path, missing file) — i.e. it follows the same
early-return shape as `sha256`.

## Out of scope (deliberate, not attempted in this pass)

- **Layer 2 prompt wiring.** The three emitters (`synthesis_agent`, `draft_writer_agent`,
  `report_compiler_agent`), `claim_ref_alignment_audit_agent`, and
  `pipeline_orchestrator_agent` are unchanged. #512's Layer 2 precondition ("a `page`
  anchor may be emitted only when the orchestration layer supplied a preflight `PASS`")
  is untouched by this addition — `content_classification` is informational metadata in
  the sidecar today, not yet consumed by any gate or advisory-tag machinery downstream
  (contrast with `[LOW-WARN-PDF-READ-INTEGRITY-UNVERIFIED]`, which #512 *does* wire into
  `claim_audit_finalizer`). Wiring an equivalent advisory tag for scanned content would
  be a follow-on change touching agent definitions — per `CONTRIBUTING.md`, agent
  definition changes require maintainer approval + discussion (open an issue) before a
  PR, which has not happened here.
- **OCR routing / remediation.** `pages_needing_ocr` is surfaced as data only; nothing
  in this pass invokes OCR or blocks on the finding.
- **Quote-text accuracy.** Same boundary #512 drew: whether extracted text *matches* a
  cited quote is the L3 claim-audit channel's job, not this preflight's.
- **CONTENT_LOCKS / #528 hash pinning.** `pipeline_orchestrator_agent.md` is one of the
  five #528 content-locked surfaces; this patch does not touch it, so no `CONTENT_LOCKS`
  hash update is required.

## Test plan

`scripts/test_pdf_read_preflight.py`, `ContentClassificationTest`: `pdf_inspector`
absent (silent degradation, verdict unaffected), text-based with no OCR pages (no
advisory warning), scanned/OCR-needed (advisory warning present, verdict still `PASS`
on a structurally clean file), classification raising an exception (advisory warning,
never fatal), classification attempted even when the structural verdict is
`UNAVAILABLE`. A dedicated `_flat_text_pdf()` fixture (real `Tj` text content, unlike
the pre-existing content-free `_flat_pdf()`) keeps the "fully clean, zero warnings on
every axis" golden-path test meaningful when `pdf_inspector` is genuinely installed,
without perturbing the ~30 pre-existing structural-only tests that intentionally reuse
content-free fixtures.

## Provenance / process note

This spec is written retroactively, after implementation, to bring the change up to
this repo's own documentation standard — it did not go through the issue-first flow
`CONTRIBUTING.md` describes for maintainer-reviewed changes, and has not undergone the
cross-model review round this repo applies to citation-integrity-adjacent mechanisms
(#512 itself closed an 8-round cross-model review; this addition has had none). It is a
local-instance addition, not an upstream contribution, unless and until a maintainer
reviews it via a real PR.
