# #454 — Windows Python hook portability + graceful no-Python degradation

**Status**: design (awaiting user review)
**Issue**: #454 (`ncwuguo`) — `ars_write_scope_guard.py` crashes with exit 49, empty stderr, on Windows alongside RTK
**Branch**: `fix/454-windows-python-hook-portability`
**Date**: 2026-06-17

## 1. Problem

The PreToolUse write-scope guard hook is registered as:

```json
{ "type": "command", "command": "python3 \"${CLAUDE_PLUGIN_ROOT}/scripts/ars_write_scope_guard.py\"" }
```

On the reporter's Windows machine every Bash/Write/Edit tool call makes this hook fail (exitCode 49, empty stderr, log spam). The guard's own Python only ever `return 0`s, so the failure is at the **interpreter-launch layer, before Python runs**: `python3` on Windows is commonly a 0-byte Microsoft Store App Execution Alias stub, not real Python.

### Empirically established (first-party, Windows 11 VM)
- On this Windows class, `python3`/`python`/`py` are 0-byte Store alias stubs under `…\AppData\Local\Microsoft\WindowsApps\`, not real Python. (CONFIRMED on VM.)
- The exact "exit 49 + empty stderr" signature was NOT reproduced (`prlctl exec` runs as SYSTEM, not the interactive user; the alias's real behavior only fires in the user's interactive session). The exact emitter of 49 remains UNCONFIRMED — but the root-cause CLASS (hook hardcodes a `python3` that is a non-functional alias) is established.

### Ground truth (official Claude Code hook docs, verified this session)
- Shell-form hook runs via `sh -c` (macOS/Linux), Git Bash (Windows), or **PowerShell when Git Bash isn't installed**.
- `${CLAUDE_PLUGIN_ROOT}` is substituted by Claude Code itself before the shell — the unexpanded value in the user's log is display text, not the executed command. (So "variable didn't expand" is NOT the bug.)
- Exit codes: `0` = no block (normal permission flow); `2` = blocks the tool; **any other non-zero (1, 49…) = NON-BLOCKING error — the action proceeds**, first stderr line shows as a hook-error notice, full stderr to debug log.
- Hooks for one event run **in parallel**; one hook's failure does NOT short-circuit siblings. (So ARS's failing hook does NOT serially "break" RTK — that earlier claim was wrong; RTK's hook runs regardless. ARS's only real harm is its own log spam.)
- No per-OS conditional command field. Exec form (`args` array) bypasses the shell but does NOT fix a wrong interpreter.

## 2. The deciding fact: ARS core does not require Python

Verified by repo inspection + independent codex/gemini fact-check:
- **Core skill use (research / write / review) requires NO Python.** README prerequisites list only Claude Code + API key; there is a `requirements-dev.txt` but no `requirements.txt`. SKILL.md/agent files are prompt/markdown that Claude reads.
- The guard hook is the **sole auto-running Python at user runtime**, and is an **optional security hardening layer** added in v3.10 (#134), not a core feature.
- **Nuance (codex catch — must stay honest):** ARS is not 100% prompt-only. These *opt-in / advanced* features DO execute real Python when the user invokes them:
  - revision mode: `scripts/ars_anchorize_draft.py`, `scripts/ars_apply_revision_patch.py`
  - pipeline submission verifier: `scripts/verify_submission_package.py`
  - slash commands: `/ars-cache-invalidate`, `/ars-mark-read`, `/ars-unmark-read`
  These are user-triggered (not auto-running hooks), so they fail visibly and the user can choose to install Python. They are **out of scope for this fix** (tracked as follow-up, §6).

### Consequence → Plan A (graceful degradation)
Forcing a Python install on a user whose ARS usage never needed Python (Plan B: fail-closed / exit 2) would turn an optional hardening layer into a global prerequisite, contradicting the setup docs and ARS's established "don't assume the environment has X; degrade if it's missing" principle (cf. #413 symlink→materialized copies for Windows). Both codex and gemini independently endorsed Plan A.

## 3. Design

### 3.1 A launcher that finds real Python (the fix for the bug body)
Add `hooks/run_guard.sh` (POSIX sh, Bash 3.2 compatible, same style/shape as the existing `scripts/announce-ars-loaded.sh`). Responsibilities:

1. Detect a REAL Python interpreter by trying, in order: `py -3`, `python3`, `python`.
2. For each candidate, VERIFY it actually executes by running a marker probe — `<candidate> -c "import sys;print('ARS_PY_OK')"` — and requiring the marker on stdout. A 0-byte Store stub fails to execute / prints nothing → skipped. Probe stdout/stderr suppressed except the marker check. Each probe wrapped in a short `timeout` (when `timeout` is available) to avoid hanging on a broken install.
3. First verified interpreter is used to `exec` the guard: `exec "<py>" "${CLAUDE_PLUGIN_ROOT}/scripts/ars_write_scope_guard.py"`, forwarding stdin, stdout, and exit code unchanged.

### 3.2 No-Python posture (Plan A)
If NO candidate verifies (no real Python on the machine): the launcher emits a valid pass-through hook JSON `{"hookSpecificOutput":{"hookEventName":"PreToolUse"}}` and **exits 0**, plus writes a one-line advisory to stderr.

Rationale (grounded in §1 ground truth + §2 fact):
- A non-zero (non-2) exit blocks nothing anyway (GT) — "fail closed via nonzero" is an illusion that only spams logs.
- Exit 2 (true block) would hard-lock a user out of all inspected writes/Bash for an environment gap — wrong for an optional hardening layer on a Python-free core (§2).
- So pass-through + exit 0 + stderr advisory: no spam, no block, not silent.
- Note: stderr visibility on exit-0 hooks is not doc-guaranteed (codex P2). The advisory is best-effort; the primary user-facing surface for "guard not active" is the docs note (§3.4), not the stderr line.

### 3.3 Bash 3.2 / cross-platform constraints
- POSIX sh only; no bashisms requiring bash 4+. Mirrors `announce-ars-loaded.sh` (which README notes runs on macOS stock bash with no `brew install bash`).
- The single `.sh` launcher covers macOS, Linux, and Windows-with-Git-Bash. On Windows WITHOUT Git Bash (CC falls back to PowerShell, which can't run `.sh`), the launcher simply doesn't run → guard not active. Under Plan A this is an ACCEPTABLE degradation (guard is optional hardening), not a security failure. We deliberately do NOT add a `.ps1` twin or a compiled binary — both were evaluated and rejected as disproportionate to an optional layer (see §5).

### 3.4 hooks.json + docs
- `hooks.json` PreToolUse command changes from `python3 "…ars_write_scope_guard.py"` to `bash "${CLAUDE_PLUGIN_ROOT}/hooks/run_guard.sh"` (same shape as the announce hook).
- README / docs/SETUP.md gain a short note: the write-scope guard needs a real Python interpreter to be active; if none is found it cleanly no-ops and core (Python-free) skills are unaffected. Plus the honest list (§2 nuance): revision / submission-verify / those 3 slash commands need real Python.

### 3.5 Tests (close the codex-flagged blind spot)
Existing tests invoke the guard via `[sys.executable, guard_path]` — they never exercise interpreter resolution. Add launch-layer tests for `run_guard.sh`:
- No real Python on PATH (simulate via a temp PATH dir containing only non-executing `python3`/`python`/`py` stubs — i.e. 0-byte files or scripts that print nothing — so the marker probe fails for every candidate) → asserts launcher emits valid pass-through JSON + exit 0. The launcher must treat a missing `timeout` binary as "run the probe without a timeout" (degrade, don't error), and the test covers both with- and without-`timeout` hosts.
- A real Python present → asserts the launcher forwards the guard's deny (exit/stdout) and allow correctly (e.g. an out-of-scope Bucket A write still denied through the launcher).
- A stub-then-real ordering (first candidate is a stub, a later one is real) → asserts it skips the stub and uses the real one.
- (POSIX host simulation only; an actual Windows repro is still needed to confirm the Store-alias path — noted as a known test-environment limit, not blocking.)

### 3.6 Seams to update (cross-file, dual-track flagged)
- **CI**: `.github/workflows/spec-consistency.yml` (~line 419) asserts `"ars_write_scope_guard.py" in cmds` directly in hooks.json's PreToolUse command — this WILL break. Update it to assert the wiring is now `run_guard.sh` AND that `run_guard.sh` execs the guard script (so the chain is still pinned).
- **Infra self-protection**: `INFRA_PROTECTED_GLOBS` in `ars_write_scope_guard.py` already covers `hooks/*.sh`, so `hooks/run_guard.sh` is auto-protected. Confirm (no change needed) — and add a test asserting a subagent write to `hooks/run_guard.sh` is denied.
- **`.gitattributes`**: ensure `*.sh` (and at least `hooks/run_guard.sh`) is `text eol=lf` so a Windows CRLF checkout can't break the hot-path hook.
- **Executable bit**: `run_guard.sh` committed with `+x` (matches `announce-ars-loaded.sh`).

## 4. What this does NOT change
- The guard's `evaluate_decision` logic is untouched (it was never the bug).
- No per-OS branching (impossible per GT), no `.ps1` twin, no compiled binary.
- No change to the SessionStart announce hook (it's `bash` too; same no-Git-Bash caveat, but it's a context-injection nicety, not a security control — tracked as follow-up if desired, §6).

## 5. Rejected alternatives
- **exec form + hardcoded `node`/`python`**: collapses to the same bug class (a hardcoded interpreter that may be absent; `node` is NOT guaranteed on PATH for native-binary CC installs — codex verified against setup docs).
- **`.sh` + `.ps1` twin (universal launcher)**: solves no-Git-Bash Windows, but disproportionate maintenance shape for an OPTIONAL hardening layer; under Plan A, no-Git-Bash Windows degrading to "guard inactive" is acceptable.
- **Compiled native binary (Go/Rust)**: truly zero-dependency, but saddles a prompt/Python repo with a permanent cross-platform build+sign toolchain. Both reviewers called it overkill.
- **Plan B (fail-closed exit 2 for Bucket A when no Python)**: rejected per §2 — turns optional hardening into a global Python prerequisite on a Python-free core.

## 6. Follow-up (separate issues, not this PR)
- Harden the OTHER hardcoded-`python`/`python3` user-runtime call sites (revision scripts, submission verifier, the 3 slash commands) the same way, or document the Python requirement at those touch points.
- SessionStart announce hook: same no-Git-Bash-Windows caveat (cosmetic, non-security).
- CI Windows runner to actually exercise the Store-alias path (currently no Windows CI).
- Reply to codex repo #31 (`ncyunju`, Windows symlink/skill-registration) — same "ARS assumes a Windows capability" family.
