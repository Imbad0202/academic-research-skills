# 03 — FAST_MERGE_AUDIT
## Merge Readiness Assessment for Low-Effort PRs

---

## CANDIDATE 1: #197 — Command Argument Substitution Fix

**Issue:** `commands/ars-mark-read.md` and `commands/ars-unmark-read.md` use prose-only arg passing, fragile for special characters.

### Current State

```bash
# commands/ars-mark-read.md (current — fragile)
#!/bin/bash
PAPER_PATH="$ARGUMENTS"   # prose substitution
```

```bash
# commands/ars-unmark-read.md (current — fragile)
#!/bin/bash
PAPER_PATH="$ARGUMENTS"   # prose substitution
```

### Required Fix

Replace with canonical bash block with proper `CLAUDE_ARGUMENTS` variable and exit-code handling.

### Change Summary
- **Files:** 2 (`commands/ars-mark-read.md`, `commands/ars-unmark-read.md`)
- **Risk:** Low — isolated to command dispatch
- **Test:** Manual test `/ars-mark-read test.pdf` and `/ars-unmark-read test.pdf`

---

## CANDIDATE 2: #160 — Test Helpers Refactor

**Issue:** `scripts/_test_helpers.py` (underscore/private) imported from outside `scripts/`. PR #158 fixed the import breakage but the structure remains dirty.

### Current State

```
scripts/_test_helpers.py   ← private module
scripts/test_check_claim_audit_consistency.py   ← imports scripts._test_helpers
scripts/test_check_version_consistency.py       ← imports scripts._test_helpers
...
```

### Required Fix

1. Create `tests/test_helpers.py` with content from `scripts/_test_helpers.py`
2. Update all `scripts/test_*.py` imports from `scripts._test_helpers` to `tests.test_helpers`
3. Delete `scripts/_test_helpers.py` (or keep as re-export for backwards compat during transition)
4. Update `requirements-dev.txt` if needed

### Change Summary
- **Files:** ~24 import updates + 1 new file + 1 delete
- **Risk:** Low — pure refactor
- **Validation:** Run `pytest tests/` + `pytest scripts/test_*.py` — both must pass

---

## CANDIDATE 3: #138 — Parallelize OpenAlex + Crossref Calls

**Issue:** `migrate_literature_corpus_to_v3_9_0.py` makes sequential API calls, slow for large corpora.

### Current State

The migration script iterates entries one-by-one, calling OpenAlex then Crossref synchronously.

### Required Fix

Use `concurrent.futures.ThreadPoolExecutor` with 2-3 workers. Maintain 1 req/s rate limit (reuse pattern from `scripts/semantic_scholar_client.py` throttle: `time.monotonic` based).

### Change Summary
- **Files:** 1 (`scripts/migrate_literature_corpus_to_v3_9_0.py`)
- **Risk:** Low — performance only
- **Validation:** Existing migration tests + manual timing test on sample corpus

---

## CANDIDATE 4: D2 — academic-pipeline SKILL.md H1 Version Fix

**Issue:** H1 says `v3.8.2` but frontmatter and suite are `v3.9.4.2`.

### Current State

```markdown
---
name: academic-pipeline
metadata:
  version: "3.9.4.2"   # correct
---
# Academic Pipeline v3.8.2 — ...   # WRONG
```

### Required Fix

```markdown
# Academic Pipeline v3.9.4.2 — ...
```

### Change Summary
- **Files:** 1 (`skills/academic-pipeline/SKILL.md`, line 17)
- **Risk:** None — cosmetic fix
- **Validation:** None needed

---

## CANDIDATE 5: D1 — academic-paper-reviewer SKILL.md H1 Version Fix

**Issue:** H1 says `v1.9.0` but frontmatter says `v1.9.1`.

### Current State

```markdown
---
name: academic-paper-reviewer
metadata:
  version: "1.9.1"   # correct
---
# Academic Paper Reviewer v1.9.0 — ...   # WRONG
```

### Required Fix

```markdown
# Academic Paper Reviewer v1.9.1 — ...
```

### Change Summary
- **Files:** 1 (`skills/academic-paper-reviewer/SKILL.md`, line 15)
- **Risk:** None — cosmetic fix
- **Validation:** None needed

---

## Merge Gate Checklist (per PR)

- [ ] `scripts/check_version_consistency.py` passes (if any version strings touched)
- [ ] `scripts/check_spec_consistency.py` passes (if any markdown files touched)
- [ ] `pytest` full suite passes (for #160 refactor)
- [ ] Manual test of `/ars-mark-read` and `/ars-unmark-read` (for #197)
- [ ] No new lint errors introduced
- [ ] CHANGELOG entry added (if user-visible)
- [ ] README not drifted out of sync with CHANGELOG

---

## CI Workflows to Verify

These workflows run on every PR; ensure changes don't break them:

| Workflow | File | What it checks |
|----------|------|----------------|
| `spec-consistency.yml` | `.github/workflows/spec-consistency.yml` | README/CHANGELOG/ARCHITECTURE consistency; SKILL.md frontmatter |
| `pytest.yml` | `.github/workflows/pytest.yml` | All `test_*.py` + `scripts/test_*.py` |
| `test-count-monotonic.yml` | `.github/workflows/test-count-monotonic.yml` | Test count doesn't decrease |
| `release-cooldown.yml` | `.github/workflows/release-cooldown.yml` | 48h between releases |

---

## NOT Fast-Merge: #151 — Repo Hygiene CI

Adding gitleaks to CI is a legitimate fast-merge candidate, but the issue is labeled `defer:v3.10` and the repo owner may want it as part of a v3.10 hygiene bundle rather than a standalone PR. Recommend opening a Discussion first before filing a PR.

---

## Summary: Fast-Merge Matrix

| PR | Effort | Risk | Files | Validation |
|----|--------|------|-------|------------|
| #197 arg passing | Low | Low | 2 | Manual test |
| #160 test helpers | Medium | Low | ~25 | Full pytest |
| #138 parallelize | Medium | Low | 1 | Migration tests |
| D2 pipeline H1 fix | Trivial | None | 1 | None |
| D1 reviewer H1 fix | Trivial | None | 1 | None |