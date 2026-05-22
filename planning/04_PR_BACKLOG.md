# 04 — PR_BACKLOG
## Pull Request Candidates

---

## OPEN PRs

| # | Title | Status | Category | Ready? |
|---|-------|--------|----------|--------|
| **#226** | `docs(spec): v3.10 deterministic verification layer specs (#198)` | OPEN | docs/spec | YES — review |
| **#225** | `feat(ars): replace prose-based command dispatch with deterministic bash execution` | OPEN | enhancement | YES — review |

### PR #225 Detail — Deterministic Bash Execution

This PR addresses the root cause of #197 (prose-only arg passing fragility) with a complete solution:
- Replaces prose-based command dispatch with canonical bash execution blocks
- Uses `$CLAUDE_ARGUMENTS` with proper quoting and error handling
- Likely makes the separate #197 issue redundant once merged

**Review focus:**
1. Does the bash block handle empty arguments gracefully?
2. Are all 13 `/ars-*` commands updated consistently?
3. Does `spec-consistency.yml` still pass?
4. No behavioral regression for edge cases (paths with spaces, special chars)

---

## LIKELY CANDIDATES (issue exists, no PR yet)

### From Issue #197
**Title:** `fix(commands): canonical bash block for arg passing in ars-mark-read + ars-unmark-read`

If PR #225 hasn't fully addressed the arg-passing concern, this would be the targeted fix for just the two mark-read commands.

**Changes:** `commands/ars-mark-read.md` + `commands/ars-unmark-read.md`
**Test:** `/ars-mark-read "path/with spaces.pdf"` + `/ars-unmark-read "path/with spaces.pdf"`

---

### From Issue #160
**Title:** `refactor(tests): move _test_helpers.py to tests/test_helpers.py`

**Changes:**
- Create `tests/test_helpers.py`
- Update imports in 24 `scripts/test_*.py` files
- Delete `scripts/_test_helpers.py` (or deprecate with re-export)

**Test:** `pytest scripts/ tests/` both pass

---

### From Issue #138
**Title:** `perf(migrate): parallelize OpenAlex + Crossref calls per entry`

**Changes:** `scripts/migrate_literature_corpus_to_v3_9_0.py` — add `ThreadPoolExecutor`
**Test:** Existing migration test fixtures + manual timing on sample corpus

---

### From D1 + D2 Fixes
**Title:** `docs: fix H1 version strings in academic-paper-reviewer and academic-pipeline SKILL.md`

- `skills/academic-paper-reviewer/SKILL.md` line 15: `v1.9.0` → `v1.9.1`
- `skills/academic-pipeline/SKILL.md` line 17: `v3.8.2` → `v3.9.4.2`

**Changes:** 2 lines in 2 files
**Test:** None needed (cosmetic only)

---

### From Issue #151
**Title:** `ci(security): add gitleaks repo hygiene check`

Before filing, check with repo owner whether they want this standalone or bundled in v3.10.

**Changes:** New `.github/workflows/security.yml`
**Test:** Workflow syntax validation (`workflowlint` or manual review)

---

## PR Template Suggestion

The repo uses GitHub's default PR template. A custom template aligned with the project's CI gates would help. Suggested sections:

```markdown
## Changes
- What changed and why?

## Validation
- [ ] `python scripts/check_version_consistency.py` — 0 errors
- [ ] `python scripts/check_spec_consistency.py` — 0 errors  
- [ ] `pytest scripts/test_*.py tests/` — all pass
- [ ] `/ars-[mode]` manual smoke test (if command change)

## CHANGELOG entry
<!-- Add a one-liner in the style of recent v3.9.x entries -->

## Related issues
Fixes #XXX
```

---

## Backlink: CI Gate Files to Update on Each PR

When filing a PR, these lint/validation scripts are gatekeepers:

| Script | Gate |
|--------|------|
| `scripts/check_version_consistency.py` | All version strings consistent across SKILL.md frontmatter |
| `scripts/check_spec_consistency.py` | README/CHANGELOG/ARCHITECTURE not drifted |
| `scripts/check_sprint_contract.py` | If any contract template changed |
| `scripts/check_pipeline_integrity.py` | If any agent prompt changed (phase boundary check) |
| `scripts/check_data_access_level.py` | If any SKILL.md data_access_level changed |
| `.github/workflows/spec-consistency.yml` | CI runs above on every PR |
| `.github/workflows/test-count-monotonic.yml` | Test count must not decrease |

---

## Merge Sequencing Recommendations

1. **Merge #225 first** — if it fully addresses #197, close #197 as part of #225
2. **Then file #197-fix** for any residual mark-read issues not covered by #225
3. **File D1+D2 fix PR** — trivial, can go anytime
4. **File #160 refactor PR** — depends on #225 (if any shared test utilities overlap)
5. **File #138 perf PR** — independent, good second PR after D1+D2
6. **File #151 security PR** — confirm with owner re: v3.10 bundling preference first