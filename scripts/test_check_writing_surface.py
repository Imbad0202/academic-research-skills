"""Formula arithmetic, extraction boundaries and advisory behaviour (#830)."""
import hashlib
import json
import math
import subprocess
import sys
from pathlib import Path

import pytest

from scripts import check_writing_surface as ws

ROOT = Path(__file__).resolve().parents[1]


def test_one_syllable_formula_fixture():
    report = ws.check("The cat sat on the mat.")["document"]
    assert report["counts"] == {"words": 6, "sentences": 1, "syllables_estimated": 6,
                                "polysyllables_estimated": 0, "unsupported_tokens": 0}
    metrics = report["metrics"]
    assert metrics["flesch_reading_ease_estimate"] == pytest.approx(116.145)
    assert metrics["flesch_kincaid_grade_estimate"] == pytest.approx(-1.45)
    assert metrics["fog_estimate"] == pytest.approx(2.4)
    assert metrics["smog_estimate"] is None


def test_known_polysyllabic_counts_and_smog_normalization():
    short = ws.readability(60, 30, 150, 30)
    long = ws.readability(120, 60, 300, 60)
    assert short["smog_estimate"] == pytest.approx(1.043 * math.sqrt(30) + 3.1291)
    assert long == short
    assert ws.readability(58, 29, 145, 29)["smog_estimate"] is None


@pytest.mark.parametrize("text", ["", "```text\nThe cat sat.\n```", "研究結果顯示存在差異。"])
def test_empty_excluded_or_non_latin_text_is_not_a_clean_result(text):
    report = ws.check(text)
    assert report["document"]["coverage"] == "not_checked"
    assert all(v is None for v in report["document"]["metrics"].values())
    assert "not checked" in ws.render(report)


def test_markdown_exclusions_and_line_anchors():
    text = """---
title: Ignored metadata
---
<!--
ignored words
-->
# Introduction
The cat sat on the mat.
```python
ignored = 'unmeasured'
```
~~~text
Ignored fenced words.
~~~
`ignored inline words` $ignored + mathematics$
| Ignored | table |
![Ignored caption](https://example.invalid/a.png)
[Visible words](https://example.invalid/target)
## References
Ignored reference words.
### Nested references
Still ignored.
## Discussion
The dog sat.
"""
    report = ws.check(text)
    assert [(s["title"], s["line"], s["counts"]["words"]) for s in report["sections"]] == [
        ("Introduction", 7, 8), ("Discussion", 23, 3)]
    assert report["document"]["counts"]["words"] == 11


def test_unclosed_code_or_comment_never_enters_metrics():
    assert ws.check("The cat sat.\n```\nHidden words.")["document"]["counts"]["words"] == 3
    assert ws.check("The cat sat.\n<!-- Hidden words.")["document"]["counts"]["words"] == 3


def test_abbreviations_decimals_and_initialisms_are_not_sentence_boundaries():
    report = ws.check("Dr. Smith used 3.5 units in the U.S. study. The trial ended.")
    assert report["document"]["counts"]["sentences"] == 2


def test_phrase_matching_is_token_bounded_longest_and_sentence_local():
    vocab = ws.load_vocabulary()
    assert ws.phrase_hits(["may", "suggest", "may", "support", "maybe"], vocab["hedges"]) == 2
    report = ws.check("For. This cohort was measured. We may suggest a change.")
    count = report["document"]["counts"]["words"]
    assert report["document"]["metrics"]["hedge_hits_per_1000_words"] == pytest.approx(1000 / count)


def test_nominalization_passive_and_flagged_terms_remain_separate_proxies():
    report = ws.check("Implementation was carefully measured. We may suggest a robust assessment.")["document"]
    assert report["metrics"]["nominalization_token_share_heuristic"] == pytest.approx(2 / 10)
    assert report["metrics"]["passive_sentence_share_heuristic"] == 0.5
    assert report["metrics"]["flagged_term_hits_per_1000_words"] == pytest.approx(1000 / 10)
    assert ws.check("The room was red.")["document"]["metrics"]["passive_sentence_share_heuristic"] == 0


def test_population_dispersion_and_section_counts():
    report = ws.check("# First\nCats sleep. Dogs sleep here.\n# Second\nBirds fly.")
    assert report["document"]["metrics"]["sentence_length_population_sd"] == pytest.approx(math.sqrt(2 / 9))
    assert sum(s["counts"]["words"] for s in report["sections"]) == report["document"]["counts"]["words"]


def test_mixed_script_discloses_partial_coverage_and_retains_latin_tokens():
    report = ws.check("The cat sat. 研究結果。")["document"]
    assert report["coverage"] == "partial"
    assert report["counts"]["words"] == 3
    assert report["counts"]["unsupported_tokens"] > 0


def test_vocabulary_errors_are_not_silently_accepted(tmp_path):
    path = tmp_path / "words.json"
    vocab = ws.load_vocabulary()
    vocab["hedges"] = [""]
    path.write_text(json.dumps(vocab))
    with pytest.raises(ValueError):
        ws.load_vocabulary(path)


def test_cli_never_rewrites_and_high_values_never_fail(tmp_path):
    source = tmp_path / "draft.md"
    original = ("Implementation operationalization was evaluated cautiously. " * 31).encode()
    source.write_bytes(original)
    run = subprocess.run([sys.executable, str(ROOT / "scripts/check_writing_surface.py"),
                          "--input", str(source), "--format", "json"], capture_output=True, text=True)
    assert run.returncode == 0
    report = json.loads(run.stdout)
    assert report["enforcement"] == ws.ENFORCEMENT
    assert report["input_sha256"] == hashlib.sha256(original).hexdigest()
    assert source.read_bytes() == original
    assert {p.name for p in tmp_path.iterdir()} == {"draft.md"}
    assert set(report["document"]["metrics"]) == {key for _, key in ws.METRICS}


@pytest.mark.parametrize("content", [b"\xff", b"", "純中文。".encode()])
def test_cli_unreadable_or_empty_inputs_are_explicitly_not_checked(tmp_path, content):
    source = tmp_path / "draft.md"
    source.write_bytes(content)
    run = subprocess.run([sys.executable, str(ROOT / "scripts/check_writing_surface.py"),
                          "--input", str(source)], capture_output=True, text=True)
    assert run.returncode == 2
    assert source.read_bytes() == content


def test_baseline_selection_excludes_prompts_and_blocked_runs():
    from scripts.build_writing_surface_baseline import eligible
    prefix = 'evals/heldout/reviewer_seeded_defects/runs/raw/'
    assert eligible(prefix + 'run/domain.phase2.a1.md')
    assert eligible(prefix + 'run/synthesis.a2.md')
    assert not eligible(prefix + 'blocked/run/synthesis.a1.md')
    assert not eligible(prefix + 'run/domain.phase1.a1.md')
    assert not eligible(prefix + 'run/prompt.md')
    assert not eligible('evals/heldout/revision_claim_drift/runs/2026-08-07/subjects/README.md')


def test_baseline_uses_frozen_blobs_not_working_tree(tmp_path):
    from scripts.build_writing_surface_baseline import build, git
    git(tmp_path, 'init')
    git(tmp_path, 'config', 'user.email', 'fixture@example.invalid')
    git(tmp_path, 'config', 'user.name', 'Fixture')
    path = tmp_path / 'evals/heldout/revision_claim_drift/runs/2026-08-07/subjects/example.md'
    path.parent.mkdir(parents=True)
    raw = b'The cat sat on the mat.'
    path.write_bytes(raw)
    git(tmp_path, 'add', '.')
    git(tmp_path, 'commit', '-m', 'Frozen fixture')
    first = build(tmp_path, 'HEAD')
    path.write_text('Different working tree prose.')
    assert build(tmp_path, first['input_commit']) == first
    assert first['records'][0]['sha256'] == hashlib.sha256(raw).hexdigest()
    assert first['distributions']['drafts']['flesch_reading_ease_estimate']['n'] == 1


@pytest.mark.parametrize('path,required', [
    ('academic-paper/SKILL.md', ['scripts/check_writing_surface.py', 'in-pair evaluator', 'final Markdown']),
    ('academic-paper/agents/draft_writer_agent.md', ['scripts/check_writing_surface.py', 'author-approved scope']),
    ('academic-paper/agents/formatter_agent.md', ['scripts/check_writing_surface.py', 'never block delivery']),
    ('academic-paper-reviewer/SKILL.md', ['scripts/check_writing_surface.py', 'each saved reviewer-seat report', 'before attachments', 'omit these sidecars']),
])
def test_caller_hooks_preserve_advisory_boundaries(path, required):
    text = (ROOT / path).read_text()
    assert all(phrase in text for phrase in required)


def test_design_boundary_and_ladder_remain_unchanged():
    quality = (ROOT / 'academic-paper/references/writing_quality_check.md').read_text()
    assert '**Design boundary**: This checklist improves writing quality. It is NOT a humanizer. We do not aim to fool AI detectors. We aim to produce clear, precise, varied academic prose.' in quality
    ladder = (ROOT / 'shared/references/claim_strength_ladder.md').read_text()
    assert 'observational aggregate evidence from one journal' in ladder
    assert 'Revision must never move a claim\nalong it **silently**' in ladder


def test_frozen_baseline_provenance_and_coverage():
    baseline = json.loads((ROOT / 'evals/writing_surface_baseline/baseline.json').read_text())
    assert baseline['input_commit'] == '060cb3cbffc2ca1bdfb8f7c6d2ffa4883cf09b1a'
    for path, digest in baseline['implementation_sha256'].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest
    assert hashlib.sha256(ws.VOCABULARY.read_bytes()).hexdigest() == baseline['vocabulary_sha256']
    assert len(baseline['records']) == 140
    assert baseline['coverage_counts'] == {'complete': 86, 'partial': 54, 'not_checked': 0}
    for _, metric in ws.METRICS:
        expected = sum(r['coverage'] == 'complete' and r['metrics'][metric] is not None
                       for r in baseline['records'])
        assert baseline['distributions']['all'][metric]['n'] == expected
