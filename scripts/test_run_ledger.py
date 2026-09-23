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

    def test_reset_pending_decision_names_its_boundary(self) -> None:
        self.open_checkpoint(reset_boundary_hash=BOUNDARY)
        [awaiting] = self.report()["awaiting_answer"]
        self.assertEqual(awaiting["reset_boundary_hash"], BOUNDARY)

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
        self.receipt("verify_submission_package", "passed", input_sha256={"paper.md": "b" * 64},
                     output_sha256="c" * 64, gate_tokens=["PASS"])
        self.append(kind="progress", counters={"fix_round": 2}, stage="5")
        self.append(kind="file_reference", path="/abs/raw.json", sha256="d" * 64, role="raw")
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
        }
        for label, args in cases.items():
            with self.subTest(label):
                result = self.run_cli(*args)
                self.assertEqual(result.returncode, 2, result.stdout)
                self.assertTrue(result.stderr.startswith(run_ledger.ERR_PREFIX), result.stderr)
                self.assertFalse(self.ledger.exists())

    def test_unexpected_errors_exit_2_never_1(self) -> None:
        claims = self.root / "claims.json"
        claims.write_text('{"expected_steps": ["\\ud800"]}', encoding="utf-8")
        result = self.run_cli("report", "--passport-path", str(self.passport), "--claims", str(claims))
        self.assertEqual(result.returncode, 2, result.stdout)
        self.assertIn("unexpected error", result.stderr)

    def test_report_names_an_unreadable_file_as_a_read_error(self) -> None:
        self.append(kind="file_reference", path="raw.bin", sha256="a" * 64, role="raw")
        (self.root / "raw.bin").write_bytes(b"x")
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
