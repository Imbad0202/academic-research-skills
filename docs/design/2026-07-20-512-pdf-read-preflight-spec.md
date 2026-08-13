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

The closed Draft 2020-12 sidecar schema is
`shared/contracts/pdf/pdf_read_preflight.schema.json`. It accepts this unchanged legacy
shape and the all-or-nothing opt-in extension below.

### Optional content advisory — isolated and diagnostic-only (2026-08-13 follow-up)

`--classify-content` is an explicit opt-in diagnostic consumer. It is not used by the
default Stage-1 invocation and never changes the structural verdict. The parent sends the
exact bytes already read and hashed above to the fixed
`scripts/pdf_content_classifier_worker.py` child over stdin. Only that child imports the
optional native `pdf_inspector` package. The exact input write runs outside the timeout
control loop and is accepted only when complete. The parent uses `shell=False`, one
five-second execution deadline from child startup, one shared 0.2-second teardown grace,
and concurrent 8,192-byte stdout / 4,096-byte stderr caps; there is no claimed stdin cap.
Every loop iteration polls and then immediately observes the monotonic clock. The poll
result is accepted only if that observation is strictly before the deadline. An exit
whose poll returns at or after the boundary is therefore `WORKER_TIMEOUT`.
POSIX cleanup kills the isolated worker group before reader/writer joins, including when
the leader has exited while descendants retain pipe handles. The portable Windows path
terminates only the direct worker. Timeout, helper-startup, non-zero/signal exit, cap
breach, pipe failure, malformed JSON, and invalid output all yield closed outcomes.
Non-`PASS` structural inputs do not start the child.

Calls without this flag preserve the original sidecar field set and
`tool: pdf_read_preflight/1.0.0`. Opted-in sidecars change the tool version to 1.1.0 and
add all three extension fields together: `verdict_scope: STRUCTURE_ONLY`, the closed
`content_advisory`, and the closed `content_classification` object. A partial extension is
schema-invalid.

The parent applies a hand-written closed validator equivalent to
`shared/contracts/pdf/pdf_content_classifier_worker.schema.json`, without adding a
runtime `jsonschema` dependency. It also enforces stricter runtime invariants: exact
keys, finite confidence in `[0,1]`, sorted unique integer OCR pages, and every page index
below the structural `reader_page_count`. Open upstream types collapse to
`TEXT_AVAILABLE` only for the exact positive `text_based` + empty-page combination and
otherwise to `OCR_RECOMMENDED`; raw upstream type and exception strings never enter the
sidecar.

An opted-in scanned result is therefore represented honestly as structural
`verdict: PASS` with `verdict_scope: STRUCTURE_ONLY` and
`content_advisory: OCR_RECOMMENDED`, never as a content pass. A missing optional
dependency is deterministic `CONTENT_UNAVAILABLE / DEPENDENCY_ABSENT` and leaves the
structural verdict unchanged.

On POSIX, `--classifier-diagnostics <path>` requires the opt-in flag and creates an
exclusive, non-overwriting mode-`0600` local JSON file. Platforms without POSIX
`fchmod` reject this option before creating the path; classification without a local
diagnostic remains available. The artifact may contain at most 512 bytes of explicitly
untrusted worker detail plus byte counts; neither its path nor detail appears in the
prompt-facing sidecar. Contract:
`shared/contracts/pdf/pdf_content_classifier_diagnostic.schema.json`. Full frozen design
and residual-risk boundary:
`docs/design/2026-08-13-512-pdf-content-classification-sandbox-spec.md`.

The stdout-only legacy invocation performs no alias precheck: an unreadable input or
symlink loop remains an exit-0 structural `UNAVAILABLE` verdict. When `--output` or
`--classifier-diagnostics` is present, every requested write target must resolve safely
before parsing or worker launch. Conservative NFC/casefold keys cover literal, `..`, case-only,
and canonically equivalent spellings; resolved keys cover symlinks; `samefile` covers
existing hard links. `samefile` errors fail closed except `ENOENT`, which may mean an
uncreated target. Failure to resolve the input itself is left to structural preflight and
does not block a separately safe write target.

The diagnostic remains exclusive-create/no-follow. Its resolved parent directory is
opened and inode-bound before worker launch, and the final file is created relative to
that dirfd; a later parent-symlink retarget cannot redirect raw detail. The created fd's
inode is recorded before fchmod or writing. Any failure before complete publication,
including fchmod, partial write, file fsync, close, or parent fsync, performs a fresh
no-follow lookup and unlinks only when the leaf still names that exact created inode;
parent fsync during cleanup is best-effort and never replaces the primary error. The
exclusive path is therefore retryable after a partial diagnostic, while a symlink or
hard-link attacker replacement is retained rather than deleted.

POSIX sidecar output uses a different publication contract. Before structural parsing or worker launch, the CLI opens the
resolved parent directory, records its inode, and creates through that dirfd a
fixed-length random-named private `0700` staging directory. All subsequent staging and
publication operations are relative to these anchored dirfds, so retargeting the parent
symlink cannot redirect output. Complete bytes go to the fixed staging filename
`payload`, independent of the destination name (so a legal 255-byte basename works).
The open payload is fsynced and its inode is checked against the no-follow staging entry;
a substituted symlink or hard link is rejected. Dirfd-relative `os.replace` atomically
replaces the target entry, the installed inode is rechecked, and the parent is fsynced.
Thus final-component links are replaced rather than followed and cannot overwrite the
source PDF or diagnostic. Cleanup attempts file close, unlink, directory close/rmdir,
and parent close independently, preserves a primary error over secondary close errors,
and removes unpublished staging. Publication failures are usage errors. Non-POSIX
`--output` fails closed because Python does not expose the required anchored publication
contract there; stdout classification remains available.

This publication contract assumes the output parent is caller-controlled. The private
random staging directory is `0700`, and the worker group is terminated before
publication, but Python exposes no atomic compare-inode-and-rename primitive. The
pre-replace open-inode check plus the instantaneous post-install inode check reject both
tested swap timings; if the latter observes an attacker inode, that installed entry is
removed before failure. A same-UID actor that continues changing entries after the final
postcondition remains outside this process-isolation claim.

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

The 2026-08-13 follow-up adds no live PDF or package download. Temporary fake modules and
workers cover dependency present/absent, text/scanned results, exception isolation,
timeout, helper-startup failure, one-deadline/one-grace teardown, leader-exit inherited
pipes, non-zero/signal exits, malformed/invalid/oversize output, finite confidence, page
bounds, clock-before-poll late-exit rejection, stdout-only malformed-input compatibility,
conservative pre-run path-alias rejection, output/diagnostic parent-retarget and final-entry races,
staging symlink/hard-link swaps, close-failure cleanup, 255-byte basenames, diagnostic
partial-write/fsync/close cleanup and attacker-leaf retention, privacy/mode, and all three closed schemas. The test file is also registered in
`scripts/_ci_pytest_manifest.toml`.
