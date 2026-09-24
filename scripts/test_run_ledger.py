"""Tests for scripts/run_ledger.py (#887).

Design: docs/design/2026-09-23-887-handoff-integrity-design.md. The six
scenarios in HandoffScenarioTest are the deterministic fixture that the
design's §7 decision 3 and §8 step 3 name. They show that the report reads a
ledger correctly; whether the orchestrator writes the entries stays
prompt-level and unmeasured.
"""
from __future__ import annotations

import contextlib
import hashlib
import io
import json
import os
import threading
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

import yaml

from scripts import run_ledger
from scripts.test_ars_update_check import _additional_context, run_announce
from tests.test_helpers import build_schema_validator, load_json_schema, run_script

SCRIPT = Path(__file__).parent / "run_ledger.py"
REPO = Path(__file__).resolve().parent.parent
SCHEMA_PATH = REPO / "shared" / "contracts" / "passport" / "run_ledger.schema.json"

# SHA-256 of the canonical JSON below, cross-checked with `shasum -a 256`.
# A change here breaks every ledger already written.
PINNED_CANONICAL = (
    '{"at":"2026-09-23T12:00:00Z","kind":"initial_instructions","prev_hash":null,'
    '"seq":1,"user_words":"跑完整流程，引用用 APA 7"}'
)
PINNED_HASH = "f935bb6e11f9c519fef3a8078873e22d43a12444fbc54c822bbde1c7c02ac18e"

GATE = "stage-2.5-gate"
BOUNDARY = "0123456789ab"

# Valid entries that the refusal cases change in one field each.
OPENED = {"kind": "checkpoint_opened", "checkpoint_id": "x", "stage": "1",
          "checkpoint_type": "FULL", "question": "q"}
RECEIPT = {"kind": "tool_receipt", "step": "s", "command": "c", "status": "passed",
           "exit_status": 0, "retries_used": 0}
REFERENCE = {"kind": "file_reference", "path": "raw.bin", "role": "r"}


class _Clock:
    """Deterministic UTC clock that advances one second per call."""

    def __init__(self) -> None:
        self._t = datetime(2026, 9, 23, 12, 0, 0, tzinfo=timezone.utc)

    def __call__(self) -> str:
        self._t += timedelta(seconds=1)
        return self._t.strftime("%Y-%m-%dT%H:%M:%SZ")


class _LedgerCase(unittest.TestCase):
    def setUp(self) -> None:
        tmp = TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = Path(tmp.name)
        self.passport = self.root / "paper_passport.yaml"
        self.passport.write_text("literature_corpus: []\n", encoding="utf-8")
        self.ledger = run_ledger.ledger_path(self.passport)
        self.clock = _Clock()

    def append(self, **fields):
        return run_ledger.append_entry(self.passport, fields, now=self.clock)

    def open_checkpoint(self, checkpoint_id=GATE, *, stage="2.5", checkpoint_type="MANDATORY",
                        question="Close the Stage 2.5 gate?", **extra):
        return self.append(kind="checkpoint_opened", checkpoint_id=checkpoint_id, stage=stage,
                           checkpoint_type=checkpoint_type, question=question, **extra)

    def close_checkpoint(self, answer, user_words, checkpoint_id=GATE, **extra):
        return self.append(kind="checkpoint_closed", checkpoint_id=checkpoint_id,
                           answer=answer, user_words=user_words, **extra)

    def receipt(self, step, status, **extra):
        return self.append(kind="tool_receipt", step=step, command=f"python3 scripts/{step}.py",
                           status=status, exit_status={"passed": 0, "failed": 1}.get(status),
                           retries_used=0, **extra)

    def report(self, claims=None):
        return run_ledger.build_report(self.passport, claims)

    def load_raw(self):
        return yaml.safe_load(self.ledger.read_text(encoding="utf-8"))

    def write_raw(self, data) -> None:
        self.ledger.write_text(
            yaml.safe_dump(data, sort_keys=False, allow_unicode=True), encoding="utf-8"
        )

    def edit_entries(self, mutate) -> None:
        data = self.load_raw()
        mutate(data["entries"])
        self.write_raw(data)


class HandoffScenarioTest(_LedgerCase):
    """The six synthetic scenarios of the design's §8 step 3."""

    def test_summary_drops_a_pending_decision(self) -> None:
        self.append(kind="initial_instructions", user_words="Run the full pipeline; APA 7.")
        self.open_checkpoint()
        self.append(kind="partial_answer", checkpoint_id=GATE, item_id="E6-1",
                    answer="accept", user_words="Accept E6-1 as written.")
        report = self.report({})  # the summary mentions no decision at all
        self.assertEqual(report["ledger_status"], "ok")
        [awaiting] = report["awaiting_answer"]
        self.assertEqual(awaiting["checkpoint_id"], GATE)
        self.assertEqual(awaiting["checkpoint_type"], "MANDATORY")
        self.assertEqual(awaiting["answered_items"], ["E6-1"])
        self.assertTrue(run_ledger.has_items(report))

    def test_summary_claims_an_approval_the_ledger_cannot_show(self) -> None:
        self.open_checkpoint("stage-3-branch", stage="3", question="Revise, restructure, or abort?")
        report = self.report({"decisions": [{"checkpoint_id": "stage-3-branch", "answer": "revise"}]})
        self.assertEqual(report["awaiting_answer"], [])
        [item] = report["cannot_confirm"]
        self.assertEqual(item["claimed"], "revise")
        self.assertEqual(item["reason"], "the checkpoint is still open in the ledger")

        with self.subTest("a decision on a checkpoint the ledger never saw"):
            report = self.report({"decisions": [{"checkpoint_id": "stage-5-entry", "answer": "go"}]})
            reasons = {i["checkpoint_id"]: i["reason"] for i in report["cannot_confirm"]}
            self.assertEqual(reasons["stage-5-entry"], "no answer in the user's words is recorded")

        with self.subTest("a decision that differs from the recorded answer"):
            self.close_checkpoint("abort", "Abort this round.", checkpoint_id="stage-3-branch")
            report = self.report({"decisions": [{"checkpoint_id": "stage-3-branch", "answer": "revise"}]})
            [item] = report["cannot_confirm"]
            self.assertEqual((item["claimed"], item["recorded"]), ("revise", "abort"))
            self.assertEqual(item["reason"], "the ledger records a different answer")

    def test_step_reported_as_passed_without_a_receipt(self) -> None:
        report = self.report({"steps": [{"step": "check_panel_synthesis", "status": "passed"}]})
        self.assertEqual(report["not_run"], [
            {"step": "check_panel_synthesis", "claimed": "passed", "reason": "no receipt"},
        ])

        with self.subTest("a required step nobody mentions"):
            report = self.report({"expected_steps": ["check_phase_conformance"]})
            self.assertEqual(report["not_run"][0]["claimed"], None)

        with self.subTest("a receipt that records not_run"):
            self.receipt("check_revision_token_conservation", "not_run")
            report = self.report()
            self.assertEqual(report["not_run"][0]["reason"], "the receipt records not_run")

        with self.subTest("a claim that contradicts the receipt"):
            self.receipt("check_panel_synthesis", "failed")
            report = self.report({"steps": [{"step": "check_panel_synthesis", "status": "passed"}]})
            [item] = report["cannot_confirm"]
            self.assertEqual((item["claimed"], item["recorded"]), ("passed", "failed"))

    def test_missing_e6_raw_event_file(self) -> None:
        raw = self.root / "e6_events" / "evt-001.json"
        raw.parent.mkdir()
        raw.write_bytes(b'{"event": 1}')
        digest = hashlib.sha256(raw.read_bytes()).hexdigest()
        self.append(kind="file_reference", path="e6_events/evt-001.json", sha256=digest,
                    role="E6 raw session event")
        report = self.report()
        self.assertEqual((report["missing"], report["backed"]), ([], 1))

        raw.write_bytes(b'{"event": 2}')
        self.assertEqual(self.report()["missing"][0]["reason"], "changed")
        raw.unlink()
        [item] = self.report()["missing"]
        self.assertEqual((item["path"], item["reason"]), ("e6_events/evt-001.json", "absent"))

    def test_broken_chain_fails_closed_from_the_break(self) -> None:
        self.open_checkpoint("stage-2-config", stage="2", checkpoint_type="FULL",
                             question="Confirm the Paper Configuration Record?")
        self.close_checkpoint("confirm", "Confirmed, go ahead.", checkpoint_id="stage-2-config")
        self.receipt("check_phase_conformance", "passed")
        self.edit_entries(lambda e: e[1].update(answer="revise"))  # entry 2 changed later

        report = self.report({"steps": [{"step": "check_phase_conformance", "status": "passed"}]})
        self.assertEqual((report["ledger_status"], report["untrusted_from_seq"]), ("chain_broken", 2))
        self.assertEqual([a["checkpoint_id"] for a in report["awaiting_answer"]], ["stage-2-config"])
        self.assertEqual(report["not_run"][0]["step"], "check_phase_conformance")
        before = self.ledger.read_bytes()
        with self.assertRaises(run_ledger.LedgerRefused):
            self.append(kind="progress", counters={"retry_count": 1})
        self.assertEqual(self.ledger.read_bytes(), before)

    def test_normal_close_reports_nothing(self) -> None:
        self.append(kind="initial_instructions", user_words="跑完整流程，引用用 APA 7")
        self.open_checkpoint()
        self.append(kind="partial_answer", checkpoint_id=GATE, item_id="E6-1",
                    answer="accept", user_words="E6-1 照原文接受")
        self.close_checkpoint("continue", "E6 全部接受，進 Stage 3")
        self.receipt("evidence_rows", "passed", output_sha256="a" * 64)
        source = self.root / "sources.json"
        source.write_text("{}", encoding="utf-8")
        self.append(kind="file_reference", path=str(source),
                    sha256=hashlib.sha256(b"{}").hexdigest(), role="evidence source text")
        self.append(kind="progress", counters={"retry_count": 0}, stage="2.5")
        self.append(kind="progress", counters={"loop_count": 1})

        report = self.report({
            "decisions": [{"checkpoint_id": GATE, "answer": "continue"}],
            "steps": [{"step": "evidence_rows", "status": "passed"}],
            "expected_steps": ["evidence_rows"],
        })
        self.assertFalse(run_ledger.has_items(report))
        self.assertEqual(report["backed"], 3)  # the decision, the step, the file
        self.assertEqual(report["counters"], {"2.5": {"retry_count": 0}, "run": {"loop_count": 1}})


class ReportDetailTest(_LedgerCase):
    def test_reset_pending_decision_names_its_boundary(self) -> None:
        self.open_checkpoint(reset_boundary_hash=BOUNDARY)
        [awaiting] = self.report()["awaiting_answer"]
        self.assertEqual(awaiting["reset_boundary_hash"], BOUNDARY)

    def test_contradictory_claims_stay_visible(self) -> None:
        self.open_checkpoint()
        self.close_checkpoint("pause", "先暫停")
        self.receipt("check_panel_synthesis", "failed")
        report = self.report({
            "decisions": [{"checkpoint_id": GATE, "answer": "continue"},
                          {"checkpoint_id": GATE, "answer": "pause"}],
            "steps": [{"step": "check_panel_synthesis", "status": "passed"},
                      {"step": "check_panel_synthesis", "status": "failed"}],
        })
        self.assertEqual(
            [(i["item"], i["claimed"], i["recorded"]) for i in report["cannot_confirm"]],
            [("decision", "continue", "pause"), ("step", "passed", "failed")],
        )
        self.assertEqual(report["backed"], 0)

        with self.subTest("a repeated identical claim is one item"):
            report = self.report({"decisions": [{"checkpoint_id": "stage-9", "answer": "go"}] * 2})
            self.assertEqual(len(report["cannot_confirm"]), 1)

        with self.subTest("each claim about a step without a receipt is listed"):
            report = self.report({"steps": [{"step": "evidence_rows", "status": "passed"},
                                            {"step": "evidence_rows", "status": "failed"}]})
            self.assertEqual([i["claimed"] for i in report["not_run"]], ["passed", "failed"])


class DigestAtWriteTest(_LedgerCase):
    """append hashes the files an entry names and refuses a wrong digest (#898)."""

    def write(self, name: str, content: bytes = b"x") -> str:
        target = self.root / name
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_bytes(content)
        return hashlib.sha256(content).hexdigest()

    def test_file_reference_digest_is_computed_or_checked(self) -> None:
        digest = self.write("raw.bin")
        entry = self.append(kind="file_reference", path="raw.bin", role="raw")
        self.assertEqual(entry["sha256"], digest)
        self.assertEqual(self.append(kind="file_reference", path="raw.bin", sha256=digest,
                                     role="raw again")["sha256"], digest)

    def test_receipt_input_paths_become_input_sha256(self) -> None:
        paper, notes = self.write("paper.md", b"paper"), self.write("notes/n.md", b"notes")
        entry = self.receipt("evidence_rows", "passed", input_paths=["paper.md"],
                             input_sha256={"notes/n.md": notes})
        self.assertEqual(entry["input_sha256"], {"paper.md": paper, "notes/n.md": notes})
        self.assertNotIn("input_paths", self.load_raw()["entries"][0])

    def test_relative_paths_resolve_beside_the_ledger_not_the_working_directory(self) -> None:
        digest = self.write("raw.bin", b"beside")
        elsewhere = TemporaryDirectory()
        self.addCleanup(elsewhere.cleanup)
        (Path(elsewhere.name) / "raw.bin").write_bytes(b"elsewhere")
        cwd = Path.cwd()
        os.chdir(elsewhere.name)
        try:
            entry = self.append(kind="file_reference", path="raw.bin", role="raw")
        finally:
            os.chdir(cwd)
        self.assertEqual(entry["sha256"], digest)

    def test_refused_digests_write_nothing(self) -> None:
        self.write("raw.bin")
        (self.root / "folder").mkdir()
        cases = {
            "wrong file digest": ({**REFERENCE, "sha256": "0" * 64}, "does not match the file"),
            "absent file": ({**REFERENCE, "path": "gone.bin"}, "gone.bin is not a file"),
            "a directory": ({**REFERENCE, "path": "folder"}, "folder is not a file"),
            "wrong input digest": ({**RECEIPT, "input_sha256": {"raw.bin": "0" * 64}},
                                   "does not match the file"),
            "absent input": ({**RECEIPT, "input_paths": ["gone.md"]}, "gone.md is not a file"),
            "input_paths not a list": ({**RECEIPT, "input_paths": "raw.bin"},
                                       "input_paths must be a list"),
            "input_paths too long": ({**RECEIPT, "input_paths": ["raw.bin"] * (run_ledger.LIST_MAX + 1)},
                                     "input_paths must be a list"),
            "empty input path": ({**RECEIPT, "input_paths": [""]}, "input_paths must be a list"),
            "input_paths on another kind": ({**REFERENCE, "input_paths": ["raw.bin"]},
                                            "unknown field input_paths"),
        }
        for label, (fields, message) in cases.items():
            with self.subTest(label):
                with self.assertRaisesRegex(run_ledger.LedgerRefused, message):
                    self.append(**fields)
                self.assertFalse(self.ledger.exists())

    def test_unreadable_file_is_refused(self) -> None:
        self.write("raw.bin")
        with patch.object(run_ledger, "_file_sha256", side_effect=PermissionError("denied")):
            with self.assertRaisesRegex(run_ledger.LedgerRefused, "cannot read raw.bin: denied"):
                self.append(kind="file_reference", path="raw.bin", role="raw")
        self.assertFalse(self.ledger.exists())

    def test_the_caller_mapping_is_not_changed(self) -> None:
        self.write("paper.md")
        fields = {**RECEIPT, "input_paths": ["paper.md"]}
        run_ledger.append_entry(self.passport, fields, now=self.clock)
        self.assertEqual(fields["input_paths"], ["paper.md"])
        self.assertNotIn("input_sha256", fields)


class ReceiptInputTest(_LedgerCase):
    """A receipt whose inputs changed after it was written backs nothing (#898)."""

    def setUp(self) -> None:
        super().setUp()
        self.paper = self.root / "paper.md"
        self.paper.write_text("v1", encoding="utf-8")
        self.receipt("evidence_rows", "passed", input_paths=["paper.md"])
        self.claims = {"steps": [{"step": "evidence_rows", "status": "passed"}]}

    def test_unchanged_inputs_back_the_step(self) -> None:
        report = self.report(self.claims)
        self.assertEqual((report["not_run"], report["backed"]), ([], 1))

    def test_changed_or_absent_inputs_move_the_step_to_not_run(self) -> None:
        for label, change, state in (("changed", lambda: self.paper.write_text("v2", encoding="utf-8"),
                                      "changed"),
                                     ("absent", self.paper.unlink, "absent")):
            with self.subTest(label):
                change()
                report = self.report(self.claims)
                self.assertEqual(report["not_run"], [{
                    "step": "evidence_rows", "claimed": "passed",
                    "reason": "the receipt's inputs changed after it was written",
                    "changed_inputs": [{"path": "paper.md", "reason": state}],
                }])
                self.assertEqual((report["cannot_confirm"], report["backed"]), ([], 0))

    def test_step_outcomes_carry_each_fresh_receipt(self) -> None:
        # An expected step with no claimed status still gets its recorded
        # outcome, so a tracker that lost it can take it from the report.
        self.receipt("check_panel_synthesis", "failed")
        self.receipt("check_revision_token_conservation", "not_run")
        self.receipt("pdf_read_preflight", "passed", input_paths=["paper.md"])
        expected = {"expected_steps": ["evidence_rows", "check_panel_synthesis",
                                       "check_revision_token_conservation", "pdf_read_preflight"]}
        report = self.report(expected)
        self.assertEqual(report["step_outcomes"], {
            "check_panel_synthesis": "failed", "evidence_rows": "passed",
            "pdf_read_preflight": "passed"})
        self.paper.write_text("v2", encoding="utf-8")
        self.assertEqual(self.report(expected)["step_outcomes"], {"check_panel_synthesis": "failed"})

    def test_a_not_run_receipt_keeps_its_own_reason(self) -> None:
        self.receipt("check_panel_synthesis", "not_run", input_paths=["paper.md"])
        self.paper.write_text("v2", encoding="utf-8")
        [item] = [i for i in self.report()["not_run"] if i["step"] == "check_panel_synthesis"]
        self.assertEqual(item, {"step": "check_panel_synthesis", "claimed": None,
                                "reason": "the receipt records not_run"})


class RenderTest(_LedgerCase):
    """The block the orchestrator inserts verbatim (#898)."""

    def scenario(self, question: str, role: str) -> dict:
        self.open_checkpoint(question=question)
        self.append(kind="partial_answer", checkpoint_id=GATE, item_id="E6-2",
                    answer="accept", user_words="E6-2 accept")
        self.open_checkpoint("stage-2-config", stage="2", checkpoint_type="FULL", question="q")
        self.close_checkpoint("confirm", "Confirmed.", checkpoint_id="stage-2-config")
        self.receipt("check_phase_conformance", "passed")
        draft = self.root / "drafts" / "paper_v2.md"
        draft.parent.mkdir()
        draft.write_text("v1", encoding="utf-8")
        self.append(kind="file_reference", path="drafts/paper_v2.md", role=role)
        draft.write_text("v2", encoding="utf-8")
        return self.report({
            "decisions": [{"checkpoint_id": "stage-2-config", "answer": "confirm"},
                          {"checkpoint_id": "stage3-decision", "answer": "major revision"}],
            "steps": [{"step": "check_phase_conformance", "status": "passed"},
                      {"step": "check_panel_synthesis", "status": "passed"}],
        })

    def test_english_block(self) -> None:
        report = self.scenario("Three fix rounds failed. How should we proceed?", "draft")
        self.assertEqual(run_ledger.render_block(report, "en"), "\n".join([
            "### Handoff check",
            "",
            "Awaiting your answer (1)",
            "- stage-2.5-gate, stage 2.5 (MANDATORY):",
            '  "Three fix rounds failed. How should we proceed?"',
            "  1 item recorded: E6-2",
            "",
            "Cannot confirm (1)",
            '- Decision stage3-decision: the summary or report says "major revision"; '
            "no answer in your words is recorded",
            "",
            "Not run (1)",
            "- check_panel_synthesis: no receipt; the summary or report says passed",
            "",
            "Missing (1)",
            "- drafts/paper_v2.md (draft): changed",
            "",
            "The ledger backs 2 items; they will not be asked again.",
        ]))

    def test_traditional_chinese_block(self) -> None:
        report = self.scenario("三輪修正都沒過，要怎麼處理？", "草稿")
        self.assertEqual(run_ledger.render_block(report, "zh-TW"), "\n".join([
            "### 交接檢查",
            "",
            "等你回答（1）",
            "- stage-2.5-gate，階段 2.5（MANDATORY）：",
            "  「三輪修正都沒過，要怎麼處理？」",
            "  已記下 1 項：E6-2",
            "",
            "無法確認（1）",
            "- 決定 stage3-decision：摘要或報告寫「major revision」，紀錄裡沒有你的原話",
            "",
            "沒跑過（1）",
            "- check_panel_synthesis：沒有執行收據，摘要或報告寫通過",
            "",
            "不見了（1）",
            "- drafts/paper_v2.md（草稿）：檔案被改過",
            "",
            "紀錄已確認 2 項，這些不會再問你。",
        ]))

    def test_nothing_to_report_renders_nothing(self) -> None:
        self.open_checkpoint()
        self.close_checkpoint("continue", "Continue.")
        report = self.report({"decisions": [{"checkpoint_id": GATE, "answer": "continue"}]})
        for lang in run_ledger.RENDER_LANGUAGES:
            with self.subTest(lang):
                self.assertEqual(run_ledger.render_block(report, lang), "")

    def test_ledger_problems_are_named_once(self) -> None:
        with self.subTest("missing"):
            report = self.report()
            self.assertEqual(run_ledger.render_block(report, "en").split("\n")[2],
                             "Ledger problem: no paper_passport_run_ledger.yaml beside the Material Passport.")
            self.assertEqual(run_ledger.render_block(report, "zh-TW").split("\n")[-1],
                             "紀錄沒有確認任何項目。")
        with self.subTest("unreadable"):
            self.ledger.write_bytes(b"entries: [\n")
            self.assertIn("紀錄檔問題：paper_passport_run_ledger.yaml 無法讀取。",
                          run_ledger.render_block(self.report(), "zh-TW"))
        with self.subTest("chain broken"):
            self.ledger.unlink()
            self.open_checkpoint()
            self.append(kind="progress", counters={"retry_count": 1})
            self.edit_entries(lambda e: e[1]["counters"].update(retry_count=0))
            block = run_ledger.render_block(self.report(), "en")
            self.assertIn("Ledger problem: entry 2 fails validation; entries from 2 on are not used.",
                          block)
            self.assertEqual(block.count("Ledger problem"), 1)

    def test_line_details(self) -> None:
        self.open_checkpoint(question="# A heading\n\nand a second   line")
        self.append(kind="partial_answer", checkpoint_id=GATE, item_id="E6-1", answer="a",
                    user_words="a")
        self.append(kind="partial_answer", checkpoint_id=GATE, item_id="E6-3", answer="b",
                    user_words="b")
        self.open_checkpoint("stage-3-branch", stage="3", question="Revise?")
        self.close_checkpoint("abort", "Abort.", checkpoint_id="stage-3-branch")
        self.open_checkpoint("stage-4.5-gate", stage="4.5", question="Close the gate?")
        self.receipt("check_panel_synthesis", "failed")
        paper = self.root / "paper.md"
        paper.write_text("v1", encoding="utf-8")
        self.receipt("evidence_rows", "passed", input_paths=["paper.md"])
        self.receipt("check_revision_token_conservation", "not_run")
        paper.unlink()
        report = self.report({
            "decisions": [{"checkpoint_id": "stage-3-branch", "answer": "revise"},
                          {"checkpoint_id": "stage-4.5-gate", "answer": "continue"}],
            "steps": [{"step": "check_panel_synthesis", "status": "passed"},
                      {"step": "evidence_rows", "status": "passed"},
                      {"step": "verify_submission_package", "status": "passed"},
                      {"step": "verify_submission_package", "status": "failed"}],
        })
        en = run_ledger.render_block(report, "en").split("\n")
        self.assertIn('  "\\# A heading and a second line"', en)
        self.assertIn("  2 items recorded: E6-1, E6-3", en)
        self.assertIn('- Decision stage-3-branch: the summary or report says "revise"; '
                      'the ledger records "abort"', en)
        self.assertIn('- Decision stage-4.5-gate: the summary or report says "continue"; '
                      "the checkpoint is still open in the ledger", en)
        self.assertIn("- Step check_panel_synthesis: the summary or report says passed; "
                      "the receipt records failed", en)
        self.assertIn("- evidence_rows: its inputs changed after the receipt was written "
                      "(paper.md: absent); the summary or report says passed", en)
        self.assertIn("- verify_submission_package: no receipt; the summary or report says "
                      "passed and failed", en)
        self.assertIn("- check_revision_token_conservation: the receipt records not run", en)
        self.assertIn("Not run (3)", en)
        self.assertEqual(en[-1], "The ledger backs no items.")
        zh = run_ledger.render_block(report, "zh-TW").split("\n")
        self.assertIn("- 步驟 check_panel_synthesis：摘要或報告寫通過，執行收據記錄的是未通過", zh)
        self.assertIn("- evidence_rows：執行收據寫下後，輸入檔有變動（paper.md：檔案不見了），"
                      "摘要或報告寫通過", zh)
        self.assertIn("- verify_submission_package：沒有執行收據，摘要或報告寫通過和未通過", zh)
        self.assertIn("- check_revision_token_conservation：執行收據記錄為沒跑", zh)

    def test_ledger_text_displays_as_written(self) -> None:
        self.open_checkpoint("_gate_", question="Keep <draft> or *draft*.md? [a] & `b` ~c~")
        draft = self.root / "drafts" / "_v2_.md"
        draft.parent.mkdir()
        draft.write_text("v1", encoding="utf-8")
        self.append(kind="file_reference", path="drafts/_v2_.md", role="draft_v2 & notes")
        draft.unlink()
        en = run_ledger.render_block(self.report(), "en").split("\n")
        self.assertIn("- \\_gate\\_, stage 2.5 (MANDATORY):", en)
        self.assertIn('  "Keep \\<draft\\> or \\*draft\\*.md? \\[a\\] \\& \\`b\\` \\~c\\~"', en)
        self.assertIn("- drafts/\\_v2\\_.md (draft_v2 \\& notes): absent", en)
        try:
            from markdown_it import MarkdownIt
        except ImportError:
            return
        html = MarkdownIt("commonmark").render("\n".join(en))
        self.assertIn("Keep &lt;draft&gt; or *draft*.md? [a] &amp; `b` ~c~", html)
        self.assertIn("drafts/_v2_.md (draft_v2 &amp; notes)", html)

    def test_a_value_that_opens_a_line_item_stays_text(self) -> None:
        self.open_checkpoint("# gate", question="q")
        draft = self.root / "- draft.md"
        draft.write_text("v1", encoding="utf-8")
        self.append(kind="file_reference", path="- draft.md", role="draft")
        draft.unlink()
        self.receipt("1. evidence", "not_run")
        report = self.report()
        for lang in run_ledger.RENDER_LANGUAGES:
            with self.subTest(lang):
                block = run_ledger.render_block(report, lang)
                for shown in ("\\# gate", "\\- draft.md", "1\\. evidence"):
                    self.assertIn(shown, block)
                try:
                    from markdown_it import MarkdownIt
                except ImportError:
                    continue
                html = MarkdownIt("commonmark").render(block)
                self.assertNotIn("<h1>", html)
                self.assertNotIn("<ol", html)
                for shown in ("# gate", "- draft.md", "1. evidence"):
                    self.assertIn(shown, html)

    def test_one_backed_item_is_singular(self) -> None:
        self.open_checkpoint("stage-2-config", stage="2", checkpoint_type="FULL", question="q")
        self.close_checkpoint("confirm", "Confirmed.", checkpoint_id="stage-2-config")
        self.open_checkpoint()
        report = self.report({"decisions": [{"checkpoint_id": "stage-2-config", "answer": "confirm"}]})
        self.assertEqual(run_ledger.render_block(report, "en").split("\n")[-1],
                         "The ledger backs 1 item; it will not be asked again.")
        self.assertEqual(run_ledger.render_block(report, "zh-TW").split("\n")[-1],
                         "紀錄已確認 1 項，這一項不會再問你。")


class ChainLimitTest(_LedgerCase):
    """What the hashes catch and what they do not (module docstring)."""

    def setUp(self) -> None:
        super().setUp()
        self.open_checkpoint()
        self.close_checkpoint("continue", "Continue.")
        self.append(kind="progress", counters={"retry_count": 1})

    def _status_after(self, mutate) -> dict:
        self.edit_entries(mutate)
        return self.report()

    def test_accidental_change_to_the_final_entry_is_caught(self) -> None:
        report = self._status_after(lambda e: e[-1]["counters"].update(retry_count=0))
        self.assertEqual((report["ledger_status"], report["untrusted_from_seq"]), ("chain_broken", 3))

    def test_deleted_middle_entry_is_caught(self) -> None:
        report = self._status_after(lambda e: e.pop(1))
        self.assertEqual((report["ledger_status"], report["untrusted_from_seq"]), ("chain_broken", 2))

    def test_lost_tail_is_not_caught(self) -> None:
        report = self._status_after(lambda e: e.pop())
        self.assertEqual(report["ledger_status"], "ok")
        self.assertEqual(report["counters"], {})

    def test_edit_that_recomputes_the_hashes_is_not_caught(self) -> None:
        def rewrite(entries):
            entries[1]["answer"] = "pause"
            prev = entries[0]["hash"]
            for entry in entries[1:]:
                entry["prev_hash"] = prev
                entry["hash"] = run_ledger.entry_hash(entry)
                prev = entry["hash"]

        report = self._status_after(rewrite)
        self.assertEqual(report["ledger_status"], "ok")
        report = self.report({"decisions": [{"checkpoint_id": GATE, "answer": "continue"}]})
        self.assertEqual(report["cannot_confirm"][0]["recorded"], "pause")


class AppendValidationTest(_LedgerCase):
    def test_writer_assigns_seq_time_and_hashes(self) -> None:
        first = self.append(kind="initial_instructions", user_words="Go.")
        second = self.open_checkpoint()
        self.assertEqual((first["seq"], first["prev_hash"]), (1, None))
        self.assertEqual((second["seq"], second["prev_hash"]), (2, first["hash"]))
        self.assertEqual(second["hash"], run_ledger.entry_hash(second))
        self.assertEqual(first["at"], "2026-09-23T12:00:02Z")  # created_at took the first tick
        data = self.load_raw()
        self.assertEqual(list(data), ["ledger", "created_at", "entries"])
        self.assertEqual(data["ledger"], run_ledger.LEDGER_FORMAT)
        self.assertEqual(data["entries"], [first, second])

    def test_ledger_is_named_after_the_passport_and_sits_beside_it(self) -> None:
        self.assertEqual(self.ledger, self.root / "paper_passport_run_ledger.yaml")
        self.open_checkpoint()
        self.assertTrue(self.ledger.is_file())

    def test_entry_hash_is_sha256_of_canonical_json(self) -> None:
        entry = json.loads(PINNED_CANONICAL)
        self.assertEqual(hashlib.sha256(PINNED_CANONICAL.encode("utf-8")).hexdigest(), PINNED_HASH)
        self.assertEqual(run_ledger.entry_hash(entry), PINNED_HASH)
        self.assertEqual(run_ledger.entry_hash({**entry, "hash": "ignored"}), PINNED_HASH)

    def test_refused_entries_write_nothing(self) -> None:
        cases = {
            "writer field seq": {"kind": "progress", "counters": {"a": 1}, "seq": 9},
            "writer field hash": {"kind": "progress", "counters": {"a": 1}, "hash": "0" * 64},
            "unknown kind": {"kind": "note", "text": "x"},
            "kind not a string": {"kind": ["progress"], "counters": {"a": 1}},
            "missing field": {k: v for k, v in OPENED.items() if k != "question"},
            "unknown field": {"kind": "progress", "counters": {"a": 1}, "summary": "all fine"},
            "bool as a count": {**RECEIPT, "retries_used": True},
            "text exit status": {**RECEIPT, "exit_status": "0"},
            "unknown status": {**RECEIPT, "status": "skipped"},
            "unknown checkpoint type": {**OPENED, "checkpoint_type": "OPTIONAL"},
            "empty words": {"kind": "initial_instructions", "user_words": ""},
            "lone surrogate": {"kind": "initial_instructions", "user_words": "x\ud800"},
            "words too long": {"kind": "initial_instructions",
                               "user_words": "x" * (run_ledger.WORDS_MAX + 1)},
            "empty options": {**OPENED, "options": []},
            "boundary hash not the reset format": {**OPENED, "reset_boundary_hash": "abc123"},
            "counter name": {"kind": "progress", "counters": {"RetryCount": 1}},
            "negative counter": {"kind": "progress", "counters": {"retry_count": -1}},
            "uppercase digest": {"kind": "file_reference", "path": "p", "sha256": "A" * 64,
                                 "role": "r"},
            "bad input digest": {**RECEIPT, "input_sha256": {"draft.md": "abc"}},
        }
        for label, fields in cases.items():
            with self.subTest(label):
                with self.assertRaises(run_ledger.LedgerRefused):
                    self.append(**fields)
                self.assertFalse(self.ledger.exists())
        with self.assertRaisesRegex(run_ledger.LedgerRefused, "seq is assigned by the writer"):
            self.append(**cases["writer field seq"])
        accepted = self.receipt("check_re_review_synthesis", "failed")
        self.assertIsNone(self.receipt("s", "not_run")["exit_status"])
        self.assertEqual(accepted["seq"], 1)

    def test_sequence_rules(self) -> None:
        self.append(kind="initial_instructions", user_words="Go.")
        self.open_checkpoint()
        cases = {
            "a second initial_instructions": {"kind": "initial_instructions", "user_words": "Again."},
            "reopening a checkpoint id": {**OPENED, "checkpoint_id": GATE},
            "closing an unopened checkpoint": {"kind": "checkpoint_closed", "checkpoint_id": "nope",
                                               "answer": "go", "user_words": "Go."},
        }
        before = self.ledger.read_bytes()
        for label, fields in cases.items():
            with self.subTest(label):
                with self.assertRaises(run_ledger.LedgerRefused):
                    self.append(**fields)
                self.assertEqual(self.ledger.read_bytes(), before)
        self.close_checkpoint("continue", "Continue.")
        for kind, extra in (("checkpoint_closed", {}), ("partial_answer", {"item_id": "E6-1"})):
            with self.subTest(f"{kind} after the close"):
                with self.assertRaises(run_ledger.LedgerRefused):
                    self.append(kind=kind, checkpoint_id=GATE, answer="x", user_words="x", **extra)

    def test_failed_replace_keeps_the_previous_ledger(self) -> None:
        self.open_checkpoint()
        before = self.ledger.read_bytes()
        with patch.object(run_ledger.os, "replace", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                self.close_checkpoint("continue", "Continue.")
        self.assertEqual(self.ledger.read_bytes(), before)
        self.assertEqual(list(self.root.glob("*.tmp")) + list(self.root.glob(".*.tmp")), [])

    def test_concurrent_appends_keep_one_chain(self) -> None:
        errors: list[BaseException] = []

        def worker(n: int) -> None:
            try:
                for i in range(5):
                    run_ledger.append_entry(self.passport, {"kind": "progress",
                                                            "counters": {f"w{n}": i}})
            except BaseException as exc:  # pragma: no cover - reported below
                errors.append(exc)

        threads = [threading.Thread(target=worker, args=(n,)) for n in range(4)]
        for thread in threads:
            thread.start()
        for thread in threads:
            thread.join()
        self.assertEqual(errors, [])
        entries = self.load_raw()["entries"]
        self.assertEqual([e["seq"] for e in entries], list(range(1, 21)))
        self.assertIsNone(run_ledger.first_untrusted_seq(entries))
        self.assertEqual(
            sorted(p.name for p in self.root.iterdir()),
            [".paper_passport_run_ledger.yaml.lock", "paper_passport.yaml",
             "paper_passport_run_ledger.yaml"],
        )


class ReadingTest(_LedgerCase):
    def test_missing_ledger_fails_closed(self) -> None:
        report = self.report({
            "decisions": [{"checkpoint_id": GATE, "answer": "continue"}],
            "steps": [{"step": "check_panel_synthesis", "status": "passed"}],
        })
        self.assertEqual(report["ledger_status"], "missing")
        self.assertEqual(report["cannot_confirm"][0]["reason"],
                         "no answer in the user's words is recorded")
        self.assertEqual(report["not_run"][0]["reason"], "no receipt")
        self.assertTrue(run_ledger.has_items(self.report()))

    def test_unreadable_ledgers(self) -> None:
        valid_head = f"ledger: {run_ledger.LEDGER_FORMAT}\ncreated_at: '2026-09-23T12:00:00Z'\n"
        cases = {
            "not YAML": b"entries: [\n",
            "not UTF-8": b"\xff\xfe\x00",
            "duplicate key": (valid_head + "entries: []\nentries: []\n").encode(),
            "other format": b"ledger: other/1.0\ncreated_at: '2026-09-23T12:00:00Z'\nentries: []\n",
            "extra top key": (valid_head + "entries: []\nnote: x\n").encode(),
            "entries not a list": (valid_head + "entries: {}\n").encode(),
            "created_at not UTC": (f"ledger: {run_ledger.LEDGER_FORMAT}\n"
                                   "created_at: '2026-09-23 12:00'\nentries: []\n").encode(),
            "impossible date": (valid_head + "entries:\n- at: 2026-02-30T12:00:00Z\n").encode(),
        }
        for label, payload in cases.items():
            with self.subTest(label):
                self.ledger.write_bytes(payload)
                self.assertEqual(self.report()["ledger_status"], "unreadable")
                with self.assertRaises(run_ledger.LedgerUnreadable):
                    self.open_checkpoint()
                self.assertEqual(self.ledger.read_bytes(), payload)

    def test_hand_edited_timestamp_is_untrusted_not_a_crash(self) -> None:
        self.open_checkpoint()
        second = self.close_checkpoint("continue", "Continue.")
        text = self.ledger.read_text(encoding="utf-8")
        quoted = f"'{second['at']}'"
        self.assertIn(quoted, text)
        self.ledger.write_text(text.replace(quoted, second["at"]), encoding="utf-8")
        report = self.report()
        self.assertEqual((report["ledger_status"], report["untrusted_from_seq"]), ("chain_broken", 2))

    def test_hand_edited_kind_that_is_not_a_string_is_untrusted(self) -> None:
        self.open_checkpoint()
        self.edit_entries(lambda e: e[0].update(kind=["checkpoint_opened"]))
        report = self.report()
        self.assertEqual((report["ledger_status"], report["untrusted_from_seq"]), ("chain_broken", 1))

    def test_hand_edited_lone_surrogate_is_untrusted_not_a_crash(self) -> None:
        self.open_checkpoint()
        text = self.ledger.read_text(encoding="utf-8").replace(
            "question: Close the Stage 2.5 gate?", 'question: "Close \\ud800"')
        self.ledger.write_text(text, encoding="utf-8")
        report = self.report()
        self.assertEqual((report["ledger_status"], report["untrusted_from_seq"]), ("chain_broken", 1))

    def test_hand_edited_integer_too_long_to_print_is_untrusted(self) -> None:
        self.append(kind="progress", counters={"retry_count": 1})
        text = self.ledger.read_text(encoding="utf-8").replace(
            "retry_count: 1", "retry_count: 0b" + "1" * 20000)
        self.ledger.write_text(text, encoding="utf-8")
        report = self.report()
        self.assertEqual((report["ledger_status"], report["untrusted_from_seq"]), ("chain_broken", 1))

    def test_relative_file_reference_resolves_beside_the_ledger(self) -> None:
        (self.root / "raw.bin").write_bytes(b"x")
        self.append(kind="file_reference", path="raw.bin",
                    sha256=hashlib.sha256(b"x").hexdigest(), role="raw")
        self.assertEqual(self.report()["missing"], [])


class SchemaLockstepTest(_LedgerCase):
    def setUp(self) -> None:
        super().setUp()
        self.schema = load_json_schema(SCHEMA_PATH)
        self.defs = self.schema["$defs"]

    def test_schema_is_valid_and_accepts_every_kind(self) -> None:
        self.append(kind="initial_instructions", user_words="全部照預設")
        self.open_checkpoint(options=["continue", "pause"], reset_boundary_hash=BOUNDARY)
        self.append(kind="partial_answer", checkpoint_id=GATE, item_id="E5-1",
                    answer="bounded", user_words="用有界的說法")
        self.close_checkpoint("continue", "繼續")
        (self.root / "paper.md").write_text("# Paper\n", encoding="utf-8")
        self.receipt("verify_submission_package", "passed", input_paths=["paper.md"],
                     output_sha256="c" * 64, gate_tokens=["PASS"])
        self.append(kind="progress", counters={"fix_round": 2}, stage="5")
        raw = self.root / "raw.json"
        raw.write_text("{}", encoding="utf-8")
        self.append(kind="file_reference", path=str(raw), role="raw")
        build_schema_validator(self.schema).validate(self.load_raw())

    def test_module_constants_match_the_schema(self) -> None:
        refs = [item["$ref"].rsplit("/", 1)[1]
                for item in self.schema["properties"]["entries"]["items"]["oneOf"]]
        self.assertEqual(tuple(refs), run_ledger.KINDS)
        for kind in run_ledger.KINDS:
            with self.subTest(kind):
                required, optional = run_ledger.FIELDS[kind]
                definition = self.defs[kind]
                self.assertEqual(set(definition["required"]),
                                 set(required) | set(run_ledger.BASE_FIELDS))
                self.assertEqual(set(definition["properties"]),
                                 set(required) | set(optional) | set(run_ledger.BASE_FIELDS))
                self.assertFalse(definition["additionalProperties"])
        self.assertEqual(tuple(self.defs["checkpoint_opened"]["properties"]["checkpoint_type"]["enum"]),
                         run_ledger.CHECKPOINT_TYPES)
        self.assertEqual(tuple(self.defs["tool_receipt"]["properties"]["status"]["enum"]),
                         run_ledger.RECEIPT_STATUSES)
        self.assertEqual(self.defs["words"]["maxLength"], run_ledger.WORDS_MAX)
        self.assertEqual(self.defs["text"]["maxLength"], run_ledger.TEXT_MAX)
        self.assertEqual(self.defs["short"]["maxLength"], run_ledger.SHORT_MAX)
        self.assertEqual(self.defs["short_list"]["maxItems"], run_ledger.LIST_MAX)
        self.assertEqual(self.defs["file_reference"]["properties"]["path"]["maxLength"],
                         run_ledger.PATH_MAX)
        self.assertEqual(self.schema["properties"]["ledger"]["const"], run_ledger.LEDGER_FORMAT)
        reset = load_json_schema(SCHEMA_PATH.parent / "reset_ledger_entry.schema.json")
        self.assertEqual(
            self.defs["checkpoint_opened"]["properties"]["reset_boundary_hash"]["pattern"],
            reset["$defs"]["boundary"]["properties"]["hash"]["pattern"],
        )


class SchemaAgreementTest(_LedgerCase):
    """The report trusts only entries that the schema also accepts."""

    @staticmethod
    def _chained(entries: list[dict]) -> list[dict]:
        prev = None
        for seq, entry in enumerate(entries, start=1):
            entry.setdefault("at", f"2026-09-23T12:00:{seq:02d}Z")
            entry.update(seq=seq, prev_hash=prev)
            entry["hash"] = run_ledger.entry_hash(entry)
            prev = entry["hash"]
        return entries

    def test_script_refuses_what_the_schema_refuses(self) -> None:
        validator = build_schema_validator(load_json_schema(SCHEMA_PATH))
        cases = {
            "initial_instructions after the first entry": [
                dict(OPENED), {"kind": "initial_instructions", "user_words": "Go."}],
            "non-ASCII digits in at": [
                {"kind": "initial_instructions", "user_words": "Go.",
                 "at": "\u0662\u0660\u0662\u0666-09-23T12:00:01Z"}],
        }
        for label, entries in cases.items():
            with self.subTest(label):
                entries = self._chained(entries)
                data = {"ledger": run_ledger.LEDGER_FORMAT,
                        "created_at": "2026-09-23T12:00:00Z", "entries": entries}
                self.assertFalse(validator.is_valid(data))
                self.assertIsNotNone(run_ledger.first_untrusted_seq(entries))

    def test_script_is_stricter_on_integers_and_whole_string_patterns(self) -> None:
        # JSON Schema counts 1.0 as an integer, and Python's `$` also matches before a
        # final newline, so a schema check may accept these; the script refuses them.
        for label, counters in {"integral float": {"retry_count": 1.0},
                                "trailing newline": {"retry_count\n": 1}}.items():
            with self.subTest(label):
                entries = self._chained([{"kind": "progress", "counters": counters}])
                self.assertEqual(run_ledger.first_untrusted_seq(entries), 1)


class CliTest(_LedgerCase):
    def run_cli(self, *args: str):
        return run_script(SCRIPT, *args)

    def entry_file(self, content: str) -> str:
        path = self.root / f"entry{len(list(self.root.glob('entry*.json')))}.json"
        path.write_text(content, encoding="utf-8")
        return str(path)

    def test_append_and_report(self) -> None:
        entry = self.entry_file(json.dumps({"kind": "initial_instructions", "user_words": "Go."}))
        result = self.run_cli("append", "--passport-path", str(self.passport), "--entry-file", entry)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["seq"], 1)
        self.assertEqual(self.run_cli("report", "--passport-path", str(self.passport)).returncode, 0)

        entry = self.entry_file(json.dumps({
            "kind": "checkpoint_opened", "checkpoint_id": GATE, "stage": "2.5",
            "checkpoint_type": "MANDATORY", "question": "要關閉 Stage 2.5 關卡嗎？",
        }, ensure_ascii=False))
        result = self.run_cli("append", "--passport-path", str(self.passport), "--entry-file", entry)
        self.assertEqual(result.returncode, 0, result.stderr)
        result = self.run_cli("report", "--passport-path", str(self.passport))
        self.assertEqual(result.returncode, 1)
        self.assertIn("要關閉 Stage 2.5 關卡嗎？", result.stdout)

    def test_errors_exit_2_and_write_nothing(self) -> None:
        bad_claims = self.root / "claims.json"
        bad_claims.write_text(json.dumps({"decisions": [{"checkpoint_id": GATE}]}), encoding="utf-8")
        unknown_key = self.root / "claims2.json"
        unknown_key.write_text(json.dumps({"verdict": "all fine"}), encoding="utf-8")
        surrogate = self.root / "claims3.json"
        surrogate.write_text('{"expected_steps": ["\\ud800"]}', encoding="utf-8")
        entries = {
            "invalid entry": json.dumps({"kind": "note"}),
            "entry not an object": "[1]",
            "entry not JSON": "{kind",
            "entry with a duplicate key":
                '{"kind": "initial_instructions", "user_words": "A", "user_words": "B"}',
            "entry with a lone surrogate": '{"kind": "initial_instructions", "user_words": "\\ud800"}',
        }
        cases = {
            label: ("append", "--passport-path", str(self.passport),
                    "--entry-file", self.entry_file(content))
            for label, content in entries.items()
        }
        cases |= {
            "entry file missing": ("append", "--passport-path", str(self.passport),
                                   "--entry-file", str(self.root / "no-entry.json")),
            "passport missing": ("report", "--passport-path", str(self.root / "none.yaml")),
            "claims malformed": ("report", "--passport-path", str(self.passport),
                                 "--claims", str(bad_claims)),
            "claims unknown key": ("report", "--passport-path", str(self.passport),
                                   "--claims", str(unknown_key)),
            "claims with a lone surrogate": ("report", "--passport-path", str(self.passport),
                                             "--claims", str(surrogate)),
        }
        for label, args in cases.items():
            with self.subTest(label):
                result = self.run_cli(*args)
                self.assertEqual(result.returncode, 2, result.stdout)
                self.assertTrue(result.stderr.startswith(run_ledger.ERR_PREFIX), result.stderr)
                self.assertFalse(self.ledger.exists())
        result = self.run_cli(*cases["claims with a lone surrogate"])
        self.assertIn("expected_steps must be a list of strings", result.stderr)

    def test_report_renders_the_block_on_request(self) -> None:
        args = ("report", "--passport-path", str(self.passport))
        result = self.run_cli(*args, "--render", "zh-TW")
        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(result.stdout, "\n".join([
            "### 交接檢查", "", "紀錄檔問題：Material Passport 旁邊沒有 "
            "paper_passport_run_ledger.yaml。", "", "紀錄沒有確認任何項目。", ""]))
        self.append(kind="initial_instructions", user_words="Go.")
        result = self.run_cli(*args, "--render", "en")
        self.assertEqual((result.returncode, result.stdout), (0, ""))
        result = self.run_cli(*args, "--render", "fr")
        self.assertEqual(result.returncode, 2)

    def test_unexpected_errors_exit_2_never_1(self) -> None:
        stderr = io.StringIO()
        with patch.object(run_ledger, "build_report", side_effect=RecursionError("deep")), \
                contextlib.redirect_stderr(stderr):
            code = run_ledger.main(["report", "--passport-path", str(self.passport)])
        self.assertEqual(code, 2)
        self.assertIn("unexpected error: RecursionError: deep", stderr.getvalue())

    def test_passport_path_errors_exit_2(self) -> None:
        too_long = self.root / ("x" * 300) / "paper_passport.yaml"
        result = self.run_cli("report", "--passport-path", str(too_long))
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertTrue(result.stderr.startswith(run_ledger.ERR_PREFIX), result.stderr)

    def test_report_names_an_unreadable_file_as_a_read_error(self) -> None:
        (self.root / "raw.bin").write_bytes(b"x")
        self.append(kind="file_reference", path="raw.bin", role="raw")
        stderr = io.StringIO()
        with patch.object(run_ledger, "_file_sha256", side_effect=PermissionError("denied")), \
                contextlib.redirect_stderr(stderr):
            code = run_ledger.main(["report", "--passport-path", str(self.passport)])
        self.assertEqual(code, 2)
        self.assertIn("cannot read a file the ledger names", stderr.getvalue())



class AnnounceHookTest(unittest.TestCase):
    """The SessionStart compact/resume arm asks for the handoff check (design §4)."""

    def _context(self, source: str) -> str:
        result = run_announce(json.dumps({"source": source}), {})
        self.assertEqual(result.returncode, 0, result.stderr)
        return _additional_context(result.stdout)

    def test_only_compact_and_resume_carry_the_reminder(self) -> None:
        for source in ("compact", "resume"):
            with self.subTest(source):
                self.assertIn("If an ARS pipeline run is in progress, run its handoff check",
                              self._context(source))
        for source in ("startup", "clear"):
            with self.subTest(source):
                self.assertNotIn("handoff check", self._context(source))


if __name__ == "__main__":
    unittest.main()
