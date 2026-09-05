"""Mutation tests for dispatch_calibration_panel.py (#653). Offline via ScriptedTransport."""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import dispatch_calibration_panel as mod
from _calibration_pdf_text import pdf_facts

pypdf = pytest.importorskip("pypdf")

ANALYSIS = """# Field Analysis

## Reviewer Configuration Cards

### Card #1: EIC
eic config

### Card #2: Methodology
methodology config

### Card #3: Domain
domain config

### Card #4: Perspective
perspective config

## Review Strategy Recommendations
panel-wide notes that must never reach a seat
"""

SEAT_REPORT = "## Review\n\nfindings\n\nWeighted Average: 61.0\n"
SYNTHESIS = "# Part 1\n\n### Decision: [Major Revision]\n\n# Part 2\nroadmap\n"


def make_pdf(path: Path, pages: int = 1) -> None:
    writer = pypdf.PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=200, height=200)
    with path.open("wb") as handle:
        writer.write(handle)


def pdf_hashes(path: Path) -> tuple[str, str]:
    pdf_sha, text_sha, _, _ = pdf_facts(path)
    return pdf_sha, text_sha


@pytest.fixture()
def env(tmp_path):
    corpus_dir = tmp_path / "suite"
    (corpus_dir / "corpus").mkdir(parents=True)
    (corpus_dir / "manifests").mkdir()
    pdf_cache = tmp_path / "pdfs"
    pdf_cache.mkdir()
    make_pdf(pdf_cache / "p1.pdf")
    pdf_sha, text_sha = pdf_hashes(pdf_cache / "p1.pdf")
    (corpus_dir / "corpus" / "papers.json").write_text(
        json.dumps(
            {
                "suite": "reviewer_calibration",
                "papers": [
                    {
                        "paper_id": "p1",
                        "title": "T",
                        "pdf_url": "https://openreview.net/pdf?id=p1",
                        "pdf_sha256": pdf_sha,
                        "extracted_text_sha256": text_sha,
                        "page_count": 1,
                        "retrieved_at": "2026-08-07T00:00:00Z",
                    }
                ],
            }
        ),
        encoding="utf-8",
    )
    (corpus_dir / "manifests" / "gold_labels.json").write_text("{}", encoding="utf-8")
    work = tmp_path / "work"
    return {"corpus": corpus_dir, "cache": pdf_cache, "work": work}


def base_argv(env, stage, replicate=1):
    return [
        "--stage", stage, "--paper", "p1", "--replicate", str(replicate),
        "--corpus-dir", str(env["corpus"]), "--pdf-cache", str(env["cache"]),
        "--work-dir", str(env["work"]), "--date", "2026-08-07",
        "--generated-at", "2026-08-07T00:00:00Z", "--attempt-id", "attempt-1",
        "--transport", "scripted",
    ]


def scripted(tmp_path, responses):
    path = tmp_path / "responses.json"
    path.write_text(json.dumps(responses), encoding="utf-8")
    return ["--scripted-responses", str(path)]


def run_cards(env, tmp_path, analysis=ANALYSIS):
    return mod.main(
        base_argv(env, "cards") + scripted(tmp_path, {"field_analyst": [analysis]})
    )


def panel_responses():
    return {
        "seat-eic": [SEAT_REPORT],
        "seat-methodology": [SEAT_REPORT],
        "seat-domain": [SEAT_REPORT],
        "seat-perspective": [SEAT_REPORT],
        "seat-da": ["## DA Review\n\nchallenges\n"],
        "synthesis": [SYNTHESIS],
    }


def test_cards_stage_freezes_four_cards(env, tmp_path):
    assert run_cards(env, tmp_path) == 0
    cards_dir = env["work"] / "cards" / "p1"
    for index, expected in ((1, "eic config"), (2, "methodology config"),
                            (3, "domain config"), (4, "perspective config")):
        text = (cards_dir / f"card{index}.md").read_text()
        assert expected in text
        assert "panel-wide notes" not in text
    frozen = json.loads((cards_dir / "frozen.json").read_text())
    assert frozen["paper_id"] == "p1"


def test_cards_stage_refuses_missing_card(env, tmp_path):
    truncated = ANALYSIS.replace("### Card #4: Perspective\nperspective config\n", "")
    with pytest.raises(mod.PreconditionFailure, match="Card #4"):
        run_cards(env, tmp_path, analysis=truncated)


def test_panel_complete_record_and_raw(env, tmp_path):
    assert run_cards(env, tmp_path) == 0
    assert mod.main(base_argv(env, "panel") + scripted(tmp_path, panel_responses())) == 0
    record = json.loads((env["work"] / "runs" / "2026-08-07-p1-r1.json").read_text())
    assert record["status"] == "complete"
    assert record["substrate_plan"] == "primary_only"
    assert record["suite"] == "reviewer_calibration"
    assert len(record["completed_calls"]) == 6
    raw = env["work"] / "runs" / "2026-08-07-p1-r1" / "raw"
    assert (raw / "synthesis.md").read_text() == SYNTHESIS
    assert (raw / "seat-da.md").is_file()


def test_panel_without_frozen_cards_aborts(env, tmp_path):
    rc = mod.main(base_argv(env, "panel") + scripted(tmp_path, panel_responses()))
    assert rc == 1
    blocked = json.loads((env["work"] / "runs" / "blocked-2026-08-07-p1-r1.json").read_text())
    assert blocked["status"] == "aborted"
    assert "Card #1" in blocked["abort_reason"]


def test_panel_missing_response_emits_blocked_record(env, tmp_path):
    assert run_cards(env, tmp_path) == 0
    responses = panel_responses()
    responses.pop("synthesis")
    rc = mod.main(base_argv(env, "panel") + scripted(tmp_path, responses))
    assert rc == 1
    blocked = json.loads((env["work"] / "runs" / "blocked-2026-08-07-p1-r1.json").read_text())
    assert blocked["status"] == "aborted"
    assert "seat-da" in blocked["completed_calls"]


def test_synthesizer_never_sees_manuscript(env, tmp_path, monkeypatch):
    transports = []
    real_build = mod.build_transport

    def capture(args):
        transport = real_build(args)
        transports.append(transport)
        return transport

    monkeypatch.setattr(mod, "build_transport", capture)
    assert run_cards(env, tmp_path) == 0
    assert mod.main(base_argv(env, "panel") + scripted(tmp_path, panel_responses())) == 0
    seen = {call.label: call for transport in transports for call, _ in transport.calls}
    synthesis_call = seen["synthesis"]
    assert f"<{mod.MANUSCRIPT_TAG}>" not in synthesis_call.user
    assert not synthesis_call.paper_visible
    for seat in mod.SEATS:
        assert f"<{mod.MANUSCRIPT_TAG}>" in seen[f"seat-{seat}"].user


def test_gold_labels_never_on_read_path(env, tmp_path, monkeypatch):
    """Mutation guard: dispatching a full panel never opens gold_labels.json."""
    labels = env["corpus"] / "manifests" / "gold_labels.json"
    opened = []
    real_read_text = Path.read_text

    def spy(self, *a, **kw):
        if self.name == "gold_labels.json":
            opened.append(self)
        return real_read_text(self, *a, **kw)

    monkeypatch.setattr(Path, "read_text", spy)
    assert run_cards(env, tmp_path) == 0
    assert mod.main(base_argv(env, "panel") + scripted(tmp_path, panel_responses())) == 0
    assert opened == []
    assert labels.is_file()


def test_replicate_cannot_overwrite_existing_evidence(env, tmp_path):
    assert run_cards(env, tmp_path) == 0
    assert mod.main(base_argv(env, "panel") + scripted(tmp_path, panel_responses())) == 0
    with pytest.raises(mod.PreconditionFailure, match="already holds content"):
        mod.main(base_argv(env, "panel") + scripted(tmp_path, panel_responses()))


def test_pdf_hash_mismatch_refused(env, tmp_path):
    make_pdf(env["cache"] / "p1.pdf", pages=2)  # overwrite: different doc
    with pytest.raises(mod.PreconditionFailure, match="pdf_sha256 mismatch"):
        run_cards(env, tmp_path)


def test_symlink_in_pdf_cache_refused(env, tmp_path):
    os.symlink(
        env["corpus"] / "manifests" / "gold_labels.json", env["cache"] / "labels.json"
    )
    with pytest.raises(mod.PreconditionFailure, match="symlink"):
        run_cards(env, tmp_path)


def test_work_dir_inside_repo_refused(env, tmp_path, monkeypatch):
    monkeypatch.setattr(mod, "REPO", env["work"].parent)
    with pytest.raises(mod.PreconditionFailure, match="outside the repository"):
        run_cards(env, tmp_path)


def test_fence_collision_refused():
    with pytest.raises(mod.PreconditionFailure, match="closing delimiter"):
        mod._fence("paper_content", "text with </paper_content> inside")
