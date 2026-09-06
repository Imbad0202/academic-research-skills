"""Mutation tests for assemble_calibration_corpus.py (#653)."""

from __future__ import annotations

import json
import hashlib
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent))

import assemble_calibration_corpus as mod
import _calibration_pdf_text as pdftext
from _calibration_pdf_text import TEXT_NORMALIZATION, normalize_extracted_text

pypdf = pytest.importorskip("pypdf")


def make_pool(tmp_path: Path, name: str, ids: list[str]) -> Path:
    path = tmp_path / f"pool-{name}.json"
    path.write_text(json.dumps([{"id": i, "content": {}} for i in ids]), encoding="utf-8")
    return path


def make_pdf(path: Path, pages: int = 2) -> None:
    writer = pypdf.PdfWriter()
    for _ in range(pages):
        writer.add_blank_page(width=200, height=200)
    with path.open("wb") as handle:
        writer.write(handle)


def run_select(tmp_path: Path, **kw) -> dict:
    tmp_path.mkdir(parents=True, exist_ok=True)
    acc = make_pool(tmp_path, "acc", kw.pop("accepted", ["a1", "a2", "a3", "a4"]))
    rej = make_pool(tmp_path, "rej", kw.pop("rejected", ["r1", "r2", "r3", "r4"]))
    out = tmp_path / "selection.json"
    argv = [
        "select", "--accepted-pool", str(acc), "--rejected-pool", str(rej),
        "--seed", kw.pop("seed", "s1"), "--n-accepted", "2", "--n-rejected", "2",
        "--candidate-depth", "4", "--out", str(out),
        "--ids-out-dir", str(tmp_path / "corpus"),
    ]
    if "exclusions" in kw:
        exc = tmp_path / "exclusions.json"
        exc.write_text(json.dumps(kw.pop("exclusions")), encoding="utf-8")
        argv += ["--exclusions", str(exc)]
    assert not kw
    assert mod.main(argv) == 0
    return json.loads(out.read_text(encoding="utf-8"))


def test_select_is_deterministic(tmp_path):
    first = run_select(tmp_path / "one")
    second = run_select(tmp_path / "two")
    assert first["selected"] == second["selected"]
    assert first["pools"] == second["pools"]


def test_seed_changes_order(tmp_path):
    base = run_select(tmp_path / "one")
    other = run_select(tmp_path / "two", seed="s2")
    assert base["candidates"] != other["candidates"]


def test_exclusion_promotes_next_candidate(tmp_path):
    base = run_select(tmp_path / "one")
    victim = base["selected"]["accepted"][0]
    excluded = run_select(
        tmp_path / "two",
        exclusions=[{"paper_id": victim, "reason": "contamination_probe_hit", "note": ""}],
    )
    assert victim not in excluded["selected"]["accepted"]
    assert len(excluded["selected"]["accepted"]) == 2
    assert any(e["paper_id"] == victim for e in excluded["exclusions_applied"])


def test_unknown_exclusion_reason_refused(tmp_path):
    with pytest.raises(SystemExit, match="unknown exclusion reason"):
        run_select(tmp_path, exclusions=[{"paper_id": "a1", "reason": "vibes"}])


def test_pool_overlap_refused(tmp_path):
    with pytest.raises(SystemExit, match="both pools"):
        run_select(tmp_path, accepted=["x1", "a2", "a3"], rejected=["x1", "r2", "r3"])


def test_quota_exhaustion_refused(tmp_path):
    with pytest.raises(SystemExit, match="exhausted"):
        run_select(tmp_path, accepted=["a1"])


def test_pool_ids_written_and_hashed(tmp_path):
    result = run_select(tmp_path)
    ids = (tmp_path / "corpus" / "pool_accepted_ids.txt").read_text().split()
    assert sorted(ids) == ids
    assert mod.pool_ids_hash(ids) == result["pools"]["accepted"]["ids_sha256"]


# --- freeze / verify -------------------------------------------------------

def freeze_env(tmp_path: Path) -> dict:
    selection = run_select(tmp_path)
    pdf_dir = tmp_path / "pdfs"
    pdf_dir.mkdir()
    meta = {"venue_id": "ICLR.cc/2026/Conference", "papers": []}
    for cls, decision in (("accepted", "Accept (Poster)"), ("rejected", "Reject")):
        for pid in selection["selected"][cls]:
            make_pdf(pdf_dir / f"{pid}.pdf")
            meta["papers"].append(
                {
                    "paper_id": pid,
                    "title": f"Title {pid}",
                    "venue_string": "ICLR 2026 Poster" if cls == "accepted" else "Submitted to ICLR 2026",
                    "decision_note_id": f"dec-{pid}",
                    "decision_raw": decision,
                    "pdf_url": f"https://openreview.net/pdf?id={pid}",
                    "retrieved_at": "2026-08-07T00:00:00Z",
                }
            )
    meta_path = tmp_path / "fetched.json"
    meta_path.write_text(json.dumps(meta), encoding="utf-8")
    return {
        "tmp": tmp_path,
        "selection_path": tmp_path / "selection.json",
        "meta_path": meta_path,
        "pdf_dir": pdf_dir,
        "out_dir": tmp_path,  # corpus/ already written there by select
    }


def run_freeze(env: dict, page_cap: int = 60) -> None:
    assert (
        mod.main(
            [
                "freeze", "--selection", str(env["selection_path"]),
                "--metadata", str(env["meta_path"]), "--pdf-dir", str(env["pdf_dir"]),
                "--out-dir", str(env["out_dir"]), "--page-cap", str(page_cap),
            ]
        )
        == 0
    )


def test_freeze_and_verify_roundtrip(tmp_path):
    env = freeze_env(tmp_path)
    run_freeze(env)
    papers = json.loads((tmp_path / "corpus" / "papers.json").read_text())
    labels = json.loads((tmp_path / "manifests" / "gold_labels.json").read_text())
    assert len(papers["papers"]) == 4
    assert {r["label"] for r in labels["labels"]} == {"accept", "reject"}
    assert mod.main(["verify", "--out-dir", str(tmp_path), "--pdf-dir", str(env["pdf_dir"])]) == 0


def test_papers_json_carries_no_decision_vocabulary(tmp_path):
    env = freeze_env(tmp_path)
    run_freeze(env)
    payload = json.loads((tmp_path / "corpus" / "papers.json").read_text())
    entries = payload["papers"]
    for paper in entries:
        paper["title"] = ""
    haystack = json.dumps(entries).lower()
    for token in ("poster", "spotlight", "accept", "reject", "decision", "venue"):
        assert token not in haystack


def test_leak_guard_fires_on_decision_vocab(tmp_path):
    hits = mod.leak_scan({"papers": [{"title": "safe", "note": "was a Poster"}]})
    assert "poster" in hits
    # Title text is exempt: a paper legitimately titled with such words.
    assert mod.leak_scan({"papers": [{"title": "Rejection sampling"}]}) == []


def test_freeze_page_cap_promotes_next(tmp_path):
    env = freeze_env(tmp_path)
    selection = json.loads(env["selection_path"].read_text())
    first = selection["selected"]["accepted"][0]
    spare = selection["candidates"]["accepted"][2]
    # Rebuild the capped paper with too many pages and supply the spare.
    (env["pdf_dir"] / f"{first}.pdf").unlink()
    make_pdf(env["pdf_dir"] / f"{first}.pdf", pages=5)
    make_pdf(env["pdf_dir"] / f"{spare}.pdf")
    meta = json.loads(env["meta_path"].read_text())
    meta["papers"].append(
        {
            "paper_id": spare, "title": f"Title {spare}", "venue_string": "ICLR 2026 Poster",
            "decision_note_id": f"dec-{spare}", "decision_raw": "Accept (Poster)",
            "pdf_url": f"https://openreview.net/pdf?id={spare}",
            "retrieved_at": "2026-08-07T00:00:00Z",
        }
    )
    env["meta_path"].write_text(json.dumps(meta), encoding="utf-8")
    run_freeze(env, page_cap=4)
    papers = json.loads((tmp_path / "corpus" / "papers.json").read_text())
    ids = {p["paper_id"] for p in papers["papers"]}
    assert first not in ids and spare in ids
    exclusions = papers["selection"]["exclusions"]
    assert any(
        e["paper_id"] == first and e["reason"] == "page_count_exceeds_cap" for e in exclusions
    )


def test_freeze_refuses_unexpected_decision(tmp_path):
    env = freeze_env(tmp_path)
    meta = json.loads(env["meta_path"].read_text())
    meta["papers"][0]["decision_raw"] = "Desk Reject"
    env["meta_path"].write_text(json.dumps(meta), encoding="utf-8")
    with pytest.raises(SystemExit, match="unexpected"):
        run_freeze(env)


def test_verify_detects_pdf_tamper(tmp_path):
    env = freeze_env(tmp_path)
    run_freeze(env)
    victim = json.loads((tmp_path / "corpus" / "papers.json").read_text())["papers"][0]
    make_pdf(env["pdf_dir"] / f"{victim['paper_id']}.pdf", pages=3)  # swapped document
    assert mod.main(["verify", "--out-dir", str(tmp_path), "--pdf-dir", str(env["pdf_dir"])]) == 1


def test_verify_detects_label_mutation(tmp_path):
    env = freeze_env(tmp_path)
    run_freeze(env)
    labels_path = tmp_path / "manifests" / "gold_labels.json"
    payload = json.loads(labels_path.read_text())
    payload["labels"][0]["label"] = "maybe"
    labels_path.write_text(json.dumps(payload), encoding="utf-8")
    assert mod.main(["verify", "--out-dir", str(tmp_path), "--pdf-dir", str(env["pdf_dir"])]) == 1


def test_verify_missing_pdf_is_warning_not_failure(tmp_path):
    env = freeze_env(tmp_path)
    run_freeze(env)
    victim = json.loads((tmp_path / "corpus" / "papers.json").read_text())["papers"][0]
    (env["pdf_dir"] / f"{victim['paper_id']}.pdf").unlink()
    assert mod.main(["verify", "--out-dir", str(tmp_path), "--pdf-dir", str(env["pdf_dir"])]) == 0


# --- text normalization (shared with the dispatcher) ------------------------

class _FakePage:
    def __init__(self, text: str) -> None:
        self._text = text

    def extract_text(self) -> str:
        return self._text


class _FakeReader:
    def __init__(self, _path) -> None:
        # a lone high surrogate, as pypdf emits from math/symbol fonts
        self.pages = [_FakePage("alpha \ud835 beta"), _FakePage("")]


def test_lone_surrogate_text_is_hashable_and_deterministic(tmp_path, monkeypatch):
    pdf_path = tmp_path / "s.pdf"
    make_pdf(pdf_path)
    monkeypatch.setattr(pdftext.pypdf, "PdfReader", _FakeReader)
    _, text_sha, pages, _ = mod.pdf_facts(pdf_path)
    expected = hashlib.sha256("alpha \ufffd beta\n".encode("utf-8")).hexdigest()
    assert text_sha == expected
    assert pages == 2
    assert normalize_extracted_text("\ud835\udc00") == "\ufffd\ufffd"
    assert normalize_extracted_text("plain") == "plain"


def test_manifest_records_normalization_rule_and_verify_pins_it(tmp_path):
    env = freeze_env(tmp_path)
    run_freeze(env)
    papers_path = tmp_path / "corpus" / "papers.json"
    payload = json.loads(papers_path.read_text())
    assert payload["extraction"]["text_normalization"] == TEXT_NORMALIZATION
    payload["extraction"]["text_normalization"] = "NFC"  # rule drift, not a version drift
    papers_path.write_text(json.dumps(payload), encoding="utf-8")
    assert mod.main(["verify", "--out-dir", str(tmp_path), "--pdf-dir", str(env["pdf_dir"])]) == 1


def test_malformed_pool_id_refused(tmp_path):
    path = make_pool(tmp_path, "bad", ["okID_1", "../escape"])
    with pytest.raises(SystemExit, match="malformed id"):
        mod.load_pool([path])


def test_verify_detects_label_flip_against_decision(tmp_path):
    env = freeze_env(tmp_path)
    run_freeze(env)
    labels_path = tmp_path / "manifests" / "gold_labels.json"
    payload = json.loads(labels_path.read_text())
    victim = next(r for r in payload["labels"] if r["label"] == "accept")
    victim["label"] = "reject"  # valid enum, contradicts decision_raw
    labels_path.write_text(json.dumps(payload), encoding="utf-8")
    assert mod.main(["verify", "--out-dir", str(tmp_path), "--pdf-dir", str(env["pdf_dir"])]) == 1


def test_verify_detects_synchronized_paper_removal(tmp_path):
    env = freeze_env(tmp_path)
    run_freeze(env)
    papers_path = tmp_path / "corpus" / "papers.json"
    labels_path = tmp_path / "manifests" / "gold_labels.json"
    papers = json.loads(papers_path.read_text())
    labels = json.loads(labels_path.read_text())
    gone = papers["papers"].pop()["paper_id"]
    labels["labels"] = [r for r in labels["labels"] if r["paper_id"] != gone]
    papers_path.write_text(json.dumps(papers), encoding="utf-8")
    labels_path.write_text(json.dumps(labels), encoding="utf-8")
    assert mod.main(["verify", "--out-dir", str(tmp_path), "--pdf-dir", str(env["pdf_dir"])]) == 1
