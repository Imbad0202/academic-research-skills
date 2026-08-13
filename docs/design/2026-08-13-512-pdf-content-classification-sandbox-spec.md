# #512 follow-up — opt-in PDF content advisory with process isolation

**Date:** 2026-08-13 · **Provenance:** safe maintainer-owned replacement for the
useful diagnostic idea in external PR #623 · **Status:** frozen minimal slice

## Decision

The structural contract delivered by #512 remains authoritative and unchanged:
`PASS / FAIL / UNAVAILABLE` says whether the local PDF page structure can license a
page locator. It does not say whether a page contains usable extracted text.

This slice adds one explicit diagnostic consumer without placing a new native parser
inside the structural preflight process:

```text
operator --classify-content
  -> pdf_read_preflight.py (existing structural parse + exact SHA-256)
  -> fixed child worker over the same already-hashed bytes
  -> closed validation in the parent
  -> content_advisory in the sidecar
```

Default Stage-1 and library calls preserve the original sidecar shape and tool version
and do not run the classifier. The classifier is invoked
only when the operator selects `--classify-content` and the structural verdict is
`PASS`. This is an observable, diagnostic-only use path, not an OCR router, anchor gate,
or agent-prompt change.

## Frozen scope

- `scripts/pdf_read_preflight.py`: parent process, closed consumer, timeout/caps,
  sidecar projection, and optional local diagnostic writer.
- `scripts/pdf_content_classifier_worker.py`: the only module that imports or calls
  `pdf_inspector`.
- `shared/contracts/pdf/`: closed Draft 2020-12 schemas for the prompt-facing sidecar,
  worker stdout, and local-only diagnostic.
- `requirements-pdf-content-classifier.txt`: isolated optional dependency pin; the
  package is not added to the default developer/CI environment.
- synthetic and fake-worker tests in `scripts/test_pdf_read_preflight.py`, registered
  in the unified pytest manifest.

No pipeline, agent definition, prompt, claim-audit finalizer, OCR tool, model, network,
or live/private PDF is added. No claim is made that scanned-page detection improves an
academic output or closes a measured reliability gap.

## Trust and process boundaries

### Exact-byte binding

The existing structural preflight reads and hashes the PDF once. The parent sends those
same bytes to the child on stdin. The worker does not reopen a path, so a file replacement
between structural validation and classification cannot bind a result from different
bytes to the structural SHA-256.

### Native parser containment

The parent never imports `pdf_inspector`. It starts the fixed repository worker with an
argv list and `shell=False`. On POSIX the child is the process-group leader of a new
session; the parent kills that group before reader/writer joins, including when the
leader has exited while an ordinary descendant retains inherited pipe handles. Every
terminal path repeats best-effort cleanup. On Windows the portable stdlib path terminates
and reaps only the direct worker and makes no process-tree containment claim. The parent
applies:

- one 5-second execution deadline beginning immediately after child startup;
- one explicitly separate, shared 0.2-second teardown grace (not one grace per wait or
  helper);
- 8,192-byte stdout limit;
- 4,096-byte stderr limit;
- distinct closed outcomes for launch failure, timeout, non-zero exit, signal exit,
  stdout/stderr limit, helper-startup/pipe failure, malformed JSON, and invalid closed
  output.

The loop polls and then immediately observes the monotonic clock. Only a poll result
whose following observation is strictly before the execution deadline may be processed
as a worker exit. A poll that returns at or after the boundary is `WORKER_TIMEOUT`.

Readers drain both pipes concurrently and retain no more than each limit plus one byte.
Those are the only byte caps. The exact PDF input is written on a separate thread, so a
child that never reads stdin cannot block the parent's timeout loop, and a classified
result is accepted only after the complete input write. Helper construction failures are
closed `WORKER_IO_ERROR` outcomes inside the same immediate post-`Popen` cleanup region.
A native abort or segmentation fault terminates the child, not the structural preflight
process.

This is process isolation, not a general OS sandbox. A POSIX descendant that deliberately
detaches into another session or process group, and every host-wide resource failure,
remain outside the containment claim; the optional third-party parser is not trusted.

### Worker stdout contract

`pdf_content_classifier_worker/1` is closed and permits only:

| `status` | `reason` | value fields |
|---|---|---|
| `CLASSIFIED` | `CLASSIFIED` | `TEXT_AVAILABLE` or `OCR_RECOMMENDED`; finite confidence in `[0,1]`; at most 50,000 unique non-negative page indexes |
| `UNAVAILABLE` | `DEPENDENCY_ABSENT`, `CLASSIFIER_ERROR`, or `INVALID_CLASSIFIER_RESULT` | all value fields `null` |

The worker recognizes only the positive upstream combination `pdf_type ==
"text_based"` with an empty OCR-page list as `TEXT_AVAILABLE`. Every other non-empty
upstream type is reduced to `OCR_RECOMMENDED`; the open vendor enum is never emitted.
The parent applies a hand-written validator equivalent to the closed worker schema,
requires sorted unique integer pages, rejects JSON `NaN`/infinities and unknown fields,
and binds every page index to
`0 <= page < reader_page_count` from the structural parse.

### Sidecar semantics

The existing `schema: pdf_read_preflight/1` remains compatible. Calls without the
opt-in keep the original field set and `tool: pdf_read_preflight/1.0.0`; opted-in
sidecars use tool 1.1.0 and gain the following all-or-nothing extension:

- `verdict_scope: STRUCTURE_ONLY` — makes the old verdict's scope explicit;
- `content_advisory` — one of `TEXT_AVAILABLE`,
  `OCR_RECOMMENDED`, `CONTENT_UNAVAILABLE`, or `STRUCTURAL_UNAVAILABLE`;
- `content_classification` — a closed object carrying request state, closed reason,
  classification, confidence, and bounded page indexes.

An image-only PDF may truthfully have:

```json
{
  "verdict": "PASS",
  "verdict_scope": "STRUCTURE_ONLY",
  "content_advisory": "OCR_RECOMMENDED"
}
```

That means the page tree is structurally coherent while text usability was not
established. It is not a content `PASS`. Dependency absence or any worker failure yields
`CONTENT_UNAVAILABLE` and never changes the structural verdict. A non-`PASS` structural
result yields `STRUCTURAL_UNAVAILABLE` without starting the optional child.

### Operator diagnostics

The prompt-facing sidecar contains only closed reason codes. The upstream type and raw
exception are absent. On POSIX, with the separate, explicit
`--classifier-diagnostics <local-path>` option, the operator may create one exclusive,
non-overwriting `0600` JSON file containing:

- the closed reason code;
- observed stdout/stderr byte counts;
- at most 512 bytes of clearly named `untrusted_detail`.

The diagnostic path and detail never appear in the sidecar. The file is local,
unencrypted, untrusted operator evidence and must not be copied into an agent prompt.
Platforms without POSIX `fchmod` reject the diagnostics option before path creation;
the ordinary classifier subprocess remains available under its narrower Windows
direct-worker containment claim.

The stdout-only legacy CLI performs no alias precheck, so an unreadable input or symlink
loop remains an exit-0 structural `UNAVAILABLE` verdict. With either write option, every
write target must resolve safely before structural parsing or worker launch.
NFC/casefold canonical keys conservatively reject literal, `..`, case-only, and Unicode
canonical-equivalent aliases even when their leaves do not exist; resolved keys reject
symlink aliases; existing-inode comparison rejects hard links. Existing-inode errors
fail closed except `ENOENT`, while failure to resolve the input itself stays a structural
preflight concern and does not suppress an otherwise safe output of that verdict.

The local diagnostic remains exclusive-create/no-follow. Its resolved parent directory
is opened and inode-bound before the worker, and final creation is relative to that
dirfd, so a parent-symlink retarget cannot redirect raw diagnostic detail. The created
fd is inode-bound before fchmod/write. On any pre-success fchmod, partial-write,
file-fsync, close, or parent-fsync failure, cleanup performs a fresh no-follow lookup and
unlinks the leaf only if it still identifies the created inode; it then best-effort
parent-fsyncs without replacing the primary error. A malformed partial diagnostic cannot
permanently consume the exclusive destination and immediate retry works. A symlink or
hard-link attacker replacement has a different inode and is not removed.

For ordinary sidecar output on
POSIX, the resolved parent directory is opened and inode-bound before the worker starts.
A fixed-length random-named private `0700` staging directory is created and opened
through that parent dirfd; every later operation is relative to the anchored parent or
staging dirfd, so a parent-symlink retarget cannot redirect publication. Complete bytes
use the fixed staging leaf `payload`, allowing a legal 255-byte destination basename.
After file fsync, the open payload inode must still match the no-follow staging entry;
symlink or hard-link replacement is rejected. Dirfd-relative `os.replace` installs the
payload, its installed inode is rechecked, and the parent is fsynced. Final-component
links are replaced rather than followed and cannot truncate the input or diagnostic.
Cleanup guards close, unlink, staging-dir close/rmdir, and parent close independently;
secondary cleanup failures never replace a primary publication error, and unpublished
staging is removed. Any output `OSError` becomes a CLI usage error. Non-POSIX
`--output` fails closed because the needed anchored dirfd publication surface is absent;
classification to stdout retains its narrower direct-worker Windows contract.

The output parent must be caller-controlled. Python's standard library exposes no
atomic compare-inode-and-rename operation. The private random staging directory is
`0700`, the worker group is terminated before publication, and identity is checked both
immediately before replace and immediately after install. A substitution observed after
install is rejected and the observed attacker entry is removed. Those instantaneous
postconditions cover the tested pre-check and exact check-to-replace swaps; a same-UID
actor that continues racing after the final check is outside this process-isolation
claim.

## Optional dependency model

`pdf-inspector` is not installed by `requirements-dev.txt`. Operators who deliberately
select this diagnostic may install the isolated pin in
`requirements-pdf-content-classifier.txt`. Only a top-level `ModuleNotFoundError` naming
`pdf_inspector` emits the deterministic closed `DEPENDENCY_ABSENT` state. Internal or
transitive import failures emit `CLASSIFIER_ERROR`, with bounded detail available only in
the explicit local diagnostic; structural output is unaffected.

The hermetic suite does not download or execute the real optional package. It inserts a
temporary fake `pdf_inspector` module into the child environment to cover the present,
absent, scanned, text, malformed-result, and exception adapters. Therefore this slice
proves the process and contract boundary, not the current third-party package's empirical
classification accuracy.

## Test matrix

- Existing #512 synthetic structural corpus remains green.
- Default path and structural non-`PASS` path prove the child is not started.
- Actual repository worker with temporary fake module: dependency absent, text,
  scanned/open upstream type, classifier exception, and exact input bytes.
- Fake workers: timeout, non-zero exit, signal, malformed JSON, unknown key/enum,
  non-finite/out-of-range confidence, invalid/duplicate/out-of-range pages, stdout flood,
  stderr flood, all three helper-startup failures, and a direct descendant that inherits
  pipes and must be terminated before joins.
- True top-level dependency absence is distinct from internal and transitive import
  failures; the latter are local-diagnostic-only classifier errors.
- Schema mutations reject the legacy/extension tool versions on the wrong shape.
- Prompt-facing sidecar excludes raw worker detail; local diagnostic is bounded,
  exclusive, mode `0600`, and schema-valid.
- A shared small teardown grace cannot accumulate across sequential waits; conservative
  case/canonical folding, literal/`..`, symlink, hard-link, `samefile` error, and
  malformed-input compatibility cases pin the precheck boundary.
- A clock-before-poll adversarial sequence rejects an otherwise successful exit first
  observable at the deadline.
- Post-check output symlink/hard-link races against both input and diagnostic replace the
  hostile final entry without following it; injected replace failure cleans staging.
- Parent-symlink retargeting stays on the pre-worker bound directory; staging symlink and
  hard-link swaps are rejected by open-inode identity; a secondary close failure neither
  masks the primary error nor leaves staging; a 255-byte basename publishes.
- Diagnostic-parent retargeting likewise stays on its pre-worker bound directory.
- Diagnostic partial-write, file-fsync, and close failures remove only the created inode
  and permit retry; symlink/hard-link attacker replacements survive cleanup unchanged.
- All three Draft 2020-12 schemas validate; the parent contains no
  `pdf_inspector` import.

## Residual risk and follow-on gate

This slice deliberately stops at an operator-visible diagnostic. Automatic OCR routing,
changing anchor eligibility, or sending the advisory into writer/auditor context would
change citation-integrity behavior and agent definitions. That requires a separate
issue-first design, explicit consumer semantics, prompt-injection review for every field,
and its own evidence. This slice is not that authorization.
