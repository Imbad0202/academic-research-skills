# 02 — ISSUE_TRIAGE
## Open Issues Assessed for Fast-Merge Candidates

**Triage Criteria:** low-risk, self-contained, documentation/schema/validation-script only, no behavioral change to core agents or pipeline.

---

## Issue Summary Table

| # | Priority | Category | Title | Fast-Merge? | Notes |
|---|----------|----------|-------|-------------|-------|
| **#197** | P2 | enhancement | `commands/ars-{,un}mark-read.md`: prose-only arg passing is fragile; add explicit `$ARGUMENTS` substitution | **YES** | Bash substitution fix, 2 files, low risk |
| **#160** | defer:v3.10 | enhancement | Refactor `scripts/_test_helpers.py` → `tests/test_helpers.py` | **YES** | Pure refactor, already designed, no behavior change |
| **#138** | enhancement | v3.7+ | Parallelize OpenAlex + Crossref calls in migration script | **YES** | Performance optimization, isolated script |
| **#151** | defer:v3.10 | enhancement | Add generic repo-hygiene CI (gitleaks, etc.) | **YES** | CI-only, no agent/pipeline changes |
| **#184** | defer:v3.10 | enhancement | Build local gold set; require lift gate on ranking-method changes | MAYBE | Requires gold set construction + test changes |
| **#183** | defer:v3.10 | enhancement | Add mandatory epistemic_status field | MAYBE | Schema change + agent prompt update |
| **#182** | defer:v3.10 | enhancement | Add deterministic citation verification gate | MAYBE | Larger scope, requires design doc |
| **#219** | epic (paper-derived) | research | Co-Scientist meta-analysis | NO | Research tracking issue |
| **#217** | epic (paper-derived) | research | Kim et al. 2026 peer-review findings | NO | Research tracking issue |
| **#216** | enhancement | research | Reviewer-type asymmetry parity audit | NO | Complex research task |
| **#215** | enhancement | v3.7+ | Field-norm severity calibration | NO | Requires domain expert input |
| **#214** | enhancement | v3.7+ | Sub-claim inventory before consensus aggregation | NO | Complex synthesis change |
| **#213** | enhancement | v3.7+ | Decompose multi-part claims before citation judgment | NO | Core agent logic change |
| **#198** | umbrella | enhancement | v3.10 deterministic verification layer umbrella | NO | Too large, split already happening |
| **#223–220** | P2 | research | Co-Scientist L1–L4 control-plane analysis | NO | Research/analysis |
| **#226** | docs(spec) | PR | v3.10 deterministic verification layer specs | NO (already PR) | PR exists |

---

## Issue Detail: #197 — Command Arg Passing Fragility (★ Fast-Merge)

**Severity:** P2
**Labels:** `enhancement`
**Problem:** `commands/ars-mark-read.md` and `commands/ars-unmark-read.md` use prose-only argument passing. They embed user text directly into bash variable substitution without an explicit `$ARGUMENTS` block, making them fragile when arguments contain special characters or multi-word phrases.

**Current pattern (fragile):**
```bash
# In ars-mark-read.md — prose substitution
PAPER_PATH="$ARGUMENTS"   # works for simple paths but not complex args
```

**What a fix looks like:**
```bash
# Canonical bash block with proper quoting
ARGUMENTS="${CLAUDE_ARGUMENTS:-}"
if [[ -z "$ARGUMENTS" ]]; then
  echo "Usage: /ars-mark-read <paper-path>"
  exit 1
fi
PAPER_PATH="$ARGUMENTS"
```

**Files to change:** `commands/ars-mark-read.md`, `commands/ars-unmark-read.md`

**Risk:** Low — only changes how command arguments are parsed; no downstream agent behavior affected.

---

## Issue Detail: #160 — Test Helpers Refactor (★ Fast-Merge)

**Severity:** defer:v3.10
**Labels:** `enhancement`
**Problem:** `scripts/_test_helpers.py` is a private module (underscore prefix) but is imported by test files outside `scripts/`. Should be refactored to `tests/test_helpers.py` with proper namespace.

**Related:** PR #158 already fixed the import issue (`scripts/` is not an importable package); this is the cleaner structural fix.

**Files to change:** `scripts/_test_helpers.py` → `tests/test_helpers.py`, update all `import scripts._test_helpers` → `import tests.test_helpers` across `scripts/test_*.py` files.

**Risk:** Low — pure refactor, no behavior change. Need to verify all callers update.

---

## Issue Detail: #138 — Parallelize OpenAlex + Crossref in Migration Script (★ Fast-Merge)

**Severity:** enhancement
**Labels:** `v3.7+`
**Problem:** `scripts/migrate_literature_corpus_to_v3_9_0.py` makes sequential API calls to OpenAlex + Crossref per entry. For large corpora, this is slow. Parallelization was discussed in v3.9.3 (#128 §4) but deferred.

**What to change:** Use `concurrent.futures.ThreadPoolExecutor` or `asyncio` to parallelize per-entry API calls. Rate-limit remains at 1 req/s per the Semantic Scholar client throttle pattern.

**Files to change:** `scripts/migrate_literature_corpus_to_v3_9_0.py`

**Risk:** Low — performance optimization, no schema/output change.

---

## Issue Detail: #151 — Generic Repo Hygiene CI (★ Fast-Merge)

**Severity:** defer:v3.10
**Labels:** `enhancement`
**Problem:** No gitleaks, secret scanning, or standard open-source hygiene tooling in CI.

**What to add:**
- `.github/workflows/security.yml` — run `trufflehog` or `gitleaks` on PRs
- Consider `pyupgrade`, `ruff`, `action-linguist` for language detection

**Files to change:** New `.github/workflows/security.yml`

**Risk:** Low — CI-only, no source code change.

---

## Documentation Inconsistencies Found During Triage

### D1: academic-paper-reviewer SKILL.md version header says v1.9.0, frontmatter says v1.9.1
- **File:** `skills/academic-paper-reviewer/SKILL.md`
- **Line 5:** `version: "1.9.1"` (frontmatter ✓)
- **Line 15:** `# Academic Paper Reviewer v1.9.0 — Multi-Perspective...` (H1 ✗)
- **Impact:** Low — display only, frontmatter is authoritative

### D2: academic-pipeline SKILL.md H1 says v3.8.2, frontmatter says v3.9.4.2
- **File:** `skills/academic-pipeline/SKILL.md`
- **Line 5:** `version: "3.9.4.2"` (frontmatter ✓)
- **Line 17:** `# Academic Pipeline v3.8.2 — Full Academic Research Workflow Orchestrator` (H1 ✗)
- **Impact:** Medium — visible to users, creates confusion about current version
- **Fix:** Update H1 to match frontmatter

### D3: MODE_REGISTRY.md last_updated says v3.9.4.2 (2026-05-19) ✓

---

## Closed Issues Worth Noting

| # | Category | Note |
|---|----------|------|
| #195 | bug | `/ars-mark-read` crashed on real YAML passports (json.load vs yaml.safe_load) — FIXED in PR #196 |
| #154 | bug | `scripts/` not importable — FIXED in PR #158 |
| #155 | enhancement | test-count-monotonic CI hardening — MERGED |
| #179 | post-ship | post-squash-review lexicographic compare fix — MERGED |
| #178 | enhancement | check_version_consistency 4-segment semver cap — MERGED |

---

## Recommended Triage Action

1. **Create PR for #197** — `commands/ars-*.md` bash argument fix
2. **Create PR for #160** — `scripts/_test_helpers.py` → `tests/test_helpers.py` refactor
3. **Create PR for #138** — parallelize OpenAlex + Crossref in migration script
4. **File issue for #151** — add gitleaks CI workflow
5. **Fix D1 + D2 immediately** — version string inconsistencies in SKILL.md H1 lines