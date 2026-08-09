"""Tests for ars_apply_revision_patch.py (#89 Item 7 Slice A, spec §8.2 + §8.3).

Covers: per-op positive/negative paths, the two-phase fail-closed
contract (any failure → whole patch rejected, no artifact), schema
rejections (incl. the DOC-BODY-START hash-less exemption being the ONLY
legal hash-less shape), structural-shape triggers + acknowledge flag,
pure-move detection, atomic-write injected failure, post-apply marker
uniqueness, and the §8.3 byte-identity property test — the core §4
claim tested directly over seeded randomized patches.

Run standalone:
    python -m unittest scripts/test_ars_apply_revision_patch.py -v
"""
from __future__ import annotations

import hashlib
import json
import random
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts._block_parser import base_draft_hash, parse_document
from scripts.ars_anchorize_draft import anchorize_text, build_manifest
from scripts.ars_apply_revision_patch import (
    DEFAULT_TOUCHED_RATIO_THRESHOLD,
    ApplyRejection,
    StructuralRefusal,
    main,
    run,
)
from scripts.legacy import ars_apply_revision_patch_v1_0 as legacy_apply
from scripts.revision_roadmap import author_decision_digest

FIXTURE_BODY = """# Introduction

First paragraph of the introduction with a citation.<!--ref:smith2024-->

Second paragraph, destined for surgery.

## Methods

- step one
- step two

```python
sacred_code = True
```

> A quoted remark.

Closing paragraph.
"""

FIXTURE_WITH_FRONTMATTER = "---\ntitle: fixture\n---\n\n" + FIXTURE_BODY


class TestVersionIsolation(unittest.TestCase):
    def test_legacy_loader_is_pinned_to_archived_v1_0_schema(self):
        self.assertEqual(
            legacy_apply.PATCH_SCHEMA_PATH,
            Path(__file__).resolve().parent.parent
            / "shared"
            / "contracts"
            / "patch"
            / "legacy"
            / "v1_0"
            / "revision_patch.schema.json",
        )
        schema = legacy_apply._load_patch_schema()
        self.assertEqual(schema["properties"]["patch_format_version"]["const"], "1.0")


def _hash_of(anchored: str, block_id: str) -> str:
    return parse_document(anchored).block_by_id()[block_id].norm_hash


def _base_patch(anchored: str, ops: list[dict], round_: int = 1) -> dict:
    current_ops = []
    for source in ops:
        op = dict(source)
        op.setdefault("claim_strength_changes", [])
        op.setdefault("collateral_authorization_ids", [])
        current_ops.append(op)
    return {
        "patch_format_version": "1.1",
        "authorization_context": "review_roadmap",
        "revision_round": round_,
        "base_draft_hash": base_draft_hash(anchored.encode("utf-8")),
        "ops": current_ops,
        "emitted_by": "draft_writer_agent",
    }


def _json_bytes(value: dict) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def _authority_fixture(root: Path, anchored: str, patch: dict) -> dict:
    """Write a minimal exact #670 review authority chain for structural tests."""
    base_raw = anchored.encode("utf-8")
    manifest = build_manifest(base_raw, parse_document(anchored))
    manifest_raw = _json_bytes(manifest)
    manifest_path = root / "block-manifest.json"
    manifest_path.write_bytes(manifest_raw)

    item_targets: dict[str, dict[str, set[str]]] = {}
    for op in patch.get("ops", []):
        for item_id in op.get("roadmap_item_ids", []):
            item_targets.setdefault(item_id, {}).setdefault(op["block_id"], set()).add(
                op["op"]
            )
    op_order = {"replace_block": 0, "insert_after": 1, "delete_block": 2}
    items = []
    for ordinal, item_id in enumerate(sorted(item_targets), start=1):
        targets = [
            {
                "block_id": block_id,
                "allowed_operations": sorted(operations, key=op_order.__getitem__),
            }
            for block_id, operations in sorted(
                item_targets[item_id].items(),
                key=lambda pair: (-1 if pair[0] == "DOC-BODY-START" else int(pair[0][1:])),
            )
        ]
        items.append(
            {
                "id": item_id,
                "source_refs": [
                    {
                        "seat": "R1",
                        "channel": "finding",
                        "ordinal": ordinal,
                        "subclaim_ordinal": 0,
                    }
                ],
                "description": f"Fixture finding {item_id}",
                "reviewer": "R1",
                "obligation_class": "must_fix",
                "severity": "major",
                "evidence_anchor": {
                    "anchor_type": "text",
                    "locator": "fixture",
                    "quote": "fixture",
                },
                "confidence": 5,
                "competence_basis": "fixture",
                "cost_scope": {"kind": "sentence", "locator": "fixture block"},
                "consequence_if_unaddressed": {
                    "code": "acceptance_criterion_unmet",
                    "target": {"kind": "section", "locator": "fixture"},
                },
                "target_section": "fixture",
                "suggested_action": "Apply the declared block-local change.",
                "consensus_level": "SINGLE-VERIFIER",
                "verification_criteria": "Declared bytes are present.",
                "proposed_targets": targets,
            }
        )
    roadmap = {
        "schema_version": "revision-roadmap/1.0",
        "revision_round": patch.get("revision_round", 1),
        "base_draft_sha256": hashlib.sha256(base_raw).hexdigest(),
        "block_manifest_sha256": hashlib.sha256(manifest_raw).hexdigest(),
        "items": items,
        "total_items": len(items),
        "obligation_counts": {
            "must_fix": len(items),
            "should_fix": 0,
            "consider": 0,
        },
        "editorial_decision": "Major Revision",
        "consensus_summary": "Fixture consensus.",
        "dissenting_opinions": [],
    }
    roadmap_raw = _json_bytes(roadmap)
    roadmap_path = root / "roadmap.json"
    roadmap_path.write_bytes(roadmap_raw)

    claim_surface = {
        "schema_version": "claim-surface-manifest/1.0",
        "revision_round": patch.get("revision_round", 1),
        "roadmap_sha256": hashlib.sha256(roadmap_raw).hexdigest(),
        "base_draft_sha256": hashlib.sha256(base_raw).hexdigest(),
        "claim_intent_sources": [],
        "surfaces": [],
    }
    claim_raw = _json_bytes(claim_surface)
    claim_path = root / "claim-surfaces.json"
    claim_path.write_bytes(claim_raw)

    event_id = "AUTHOR-EVENT-test-fixture"
    adjudication = {
        "schema_version": "author-adjudication/1.0",
        "revision_round": patch.get("revision_round", 1),
        "roadmap_sha256": hashlib.sha256(roadmap_raw).hexdigest(),
        "base_draft_sha256": hashlib.sha256(base_raw).hexdigest(),
        "claim_surface_manifest_sha256": hashlib.sha256(claim_raw).hexdigest(),
        "adjudication_status": "complete",
        "author_events": [
            {
                "event_id": event_id,
                "source": "explicit_session_user_message",
                "actor_role": "author",
                "input_sha256": hashlib.sha256(b"explicit fixture author choice").hexdigest(),
            }
        ],
        "display_order": {
            "mode": "source_traceability",
            "item_ids": [item["id"] for item in items],
            "author_event_id": event_id,
        },
        "author_adjudications": [
            {
                "item_id": item["id"],
                "author_event_id": event_id,
                "author_triage": "will_address",
                "authorized_targets": item["proposed_targets"],
                "claim_strength_authorizations": [],
            }
            for item in items
        ],
        "collateral_authorizations": [],
    }
    author_raw = _json_bytes(adjudication)
    author_path = root / "author-adjudication.json"
    author_path.write_bytes(author_raw)

    patch["roadmap_sha256"] = hashlib.sha256(roadmap_raw).hexdigest()
    patch["author_adjudication_sha256"] = hashlib.sha256(author_raw).hexdigest()
    patch["author_decision_digest"] = author_decision_digest(adjudication)
    patch["claim_surface_manifest_sha256"] = hashlib.sha256(claim_raw).hexdigest()
    return {
        "block_manifest_path": manifest_path,
        "roadmap_path": roadmap_path,
        "author_adjudication_path": author_path,
        "claim_surface_manifest_path": claim_path,
        "artifact_root": root,
    }


class ApplyHarness(unittest.TestCase):
    """Shared helpers: write base+patch to a temp dir and run the apply."""

    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.base_path = self.tmp / "base.md"
        self.patch_path = self.tmp / "patch.json"
        self.output_path = self.tmp / "revised.md"
        self.report_path = self.tmp / "revised.md.apply-report.json"
        self.authority_kwargs: dict = {}

    def _write(self, anchored: str, patch: dict) -> None:
        self.base_path.write_bytes(anchored.encode("utf-8"))
        self.authority_kwargs = _authority_fixture(self.tmp, anchored, patch)
        self.patch_path.write_text(json.dumps(patch), encoding="utf-8")

    def _run(self, **kwargs) -> dict:
        defaults = dict(acknowledge_structural=False, touched_ratio_threshold=None)
        defaults.update(kwargs)
        return run(
            self.base_path,
            self.patch_path,
            self.output_path,
            self.report_path,
            **self.authority_kwargs,
            **defaults,
        )

    def _cli_authority_args(self) -> list[str]:
        return [
            "--block-manifest",
            str(self.authority_kwargs["block_manifest_path"]),
            "--roadmap",
            str(self.authority_kwargs["roadmap_path"]),
            "--author-adjudication",
            str(self.authority_kwargs["author_adjudication_path"]),
            "--claim-surface-manifest",
            str(self.authority_kwargs["claim_surface_manifest_path"]),
            "--artifact-root",
            str(self.authority_kwargs["artifact_root"]),
        ]

    def _assert_no_artifacts(self):
        self.assertFalse(self.output_path.exists())
        self.assertFalse(self.report_path.exists())

    def anchored_fixture(self, with_frontmatter: bool = False) -> str:
        return anchorize_text(FIXTURE_WITH_FRONTMATTER if with_frontmatter else FIXTURE_BODY)


class TestReplaceBlock(ApplyHarness):
    def test_replace_keeps_marker_and_preserves_everything_else(self):
        anchored = self.anchored_fixture()
        target = "B0003"  # "Second paragraph, destined for surgery."
        patch = _base_patch(
            anchored,
            [
                {
                    "op": "replace_block",
                    "block_id": target,
                    "old_hash": _hash_of(anchored, target),
                    "new_text": "Second paragraph, fully revised.",
                    "roadmap_item_ids": ["REV-001"],
                }
            ],
        )
        self._write(anchored, patch)
        report = self._run()
        out = self.output_path.read_text()
        self.assertIn("<!--block:B0003-->\nSecond paragraph, fully revised.\n", out)
        self.assertNotIn("destined for surgery", out)
        self.assertEqual(report["counters"]["blocks_touched"], 1)
        self.assertEqual(report["counters"]["blocks_preserved_byte_identical"], 7)
        self.assertEqual(report["ops_applied"][0]["new_block_ids"], [])

    def test_multi_block_replace_head_keeps_id_rest_fresh(self):
        anchored = self.anchored_fixture()
        target = "B0003"
        patch = _base_patch(
            anchored,
            [
                {
                    "op": "replace_block",
                    "block_id": target,
                    "old_hash": _hash_of(anchored, target),
                    "new_text": "Head paragraph.\n\nTail paragraph one.\n\nTail paragraph two.",
                    "roadmap_item_ids": ["REV-001"],
                }
            ],
        )
        self._write(anchored, patch)
        report = self._run()
        out_doc = parse_document(self.output_path.read_text())
        ids = [b.block_id for b in out_doc.blocks]
        self.assertIn("B0003", ids)
        self.assertEqual(report["ops_applied"][0]["new_block_ids"], ["B0009", "B0010"])
        head = out_doc.block_by_id()["B0003"]
        self.assertEqual(head.normalized_text, "Head paragraph.")

    def test_replace_final_block_without_trailing_newline(self):
        anchored = anchorize_text("Para one.\n\nFinal no EOL")
        target = "B0002"
        patch = _base_patch(
            anchored,
            [
                {
                    "op": "replace_block",
                    "block_id": target,
                    "old_hash": _hash_of(anchored, target),
                    "new_text": "Replaced final.",
                    "roadmap_item_ids": ["REV-001"],
                }
            ],
        )
        self._write(anchored, patch)
        self._run()
        self.assertTrue(self.output_path.read_text().endswith("Replaced final."))


class TestInsertAfter(ApplyHarness):
    def test_insert_after_multi_paragraph_fresh_ids(self):
        anchored = self.anchored_fixture()
        anchor = "B0002"
        patch = _base_patch(
            anchored,
            [
                {
                    "op": "insert_after",
                    "block_id": anchor,
                    "old_hash": _hash_of(anchored, anchor),
                    "new_text": "A new paragraph.\n\nAnd a second new paragraph.",
                    "roadmap_item_ids": ["REV-002"],
                }
            ],
        )
        self._write(anchored, patch)
        report = self._run()
        out = self.output_path.read_text()
        self.assertEqual(report["ops_applied"][0]["new_block_ids"], ["B0009", "B0010"])
        self.assertIn(
            "<!--block:B0009-->\nA new paragraph.\n\n<!--block:B0010-->\nAnd a second new paragraph.\n",
            out,
        )
        # Anchor content untouched, insertion lands between anchor and next block.
        pos_anchor = out.index("citation.<!--ref:smith2024-->")
        pos_new = out.index("A new paragraph.")
        pos_next = out.index("destined for surgery")
        self.assertTrue(pos_anchor < pos_new < pos_next)

    def test_doc_body_start_with_frontmatter(self):
        anchored = self.anchored_fixture(with_frontmatter=True)
        patch = _base_patch(
            anchored,
            [
                {
                    "op": "insert_after",
                    "block_id": "DOC-BODY-START",
                    "new_text": "A brand-new opening paragraph.",
                    "roadmap_item_ids": ["REV-003"],
                }
            ],
        )
        self._write(anchored, patch)
        self._run()
        out = self.output_path.read_text()
        self.assertTrue(out.startswith("---\ntitle: fixture\n---\n"))
        pos_fm_end = out.index("---\n", 4) + 4
        pos_new = out.index("A brand-new opening paragraph.")
        pos_intro = out.index("# Introduction")
        self.assertTrue(pos_fm_end < pos_new < pos_intro)

    def test_doc_body_start_without_frontmatter(self):
        anchored = self.anchored_fixture()
        patch = _base_patch(
            anchored,
            [
                {
                    "op": "insert_after",
                    "block_id": "DOC-BODY-START",
                    "new_text": "Opening paragraph.",
                    "roadmap_item_ids": ["REV-003"],
                }
            ],
        )
        self._write(anchored, patch)
        self._run()
        out = self.output_path.read_text()
        pos_new = out.index("Opening paragraph.")
        pos_intro = out.index("# Introduction")
        self.assertTrue(pos_new < pos_intro)


class TestDeleteBlock(ApplyHarness):
    def test_delete_removes_block_and_marker(self):
        anchored = self.anchored_fixture()
        target = "B0007"  # the blockquote
        patch = _base_patch(
            anchored,
            [
                {
                    "op": "delete_block",
                    "block_id": target,
                    "old_hash": _hash_of(anchored, target),
                    "roadmap_item_ids": ["REV-004"],
                }
            ],
        )
        self._write(anchored, patch)
        report = self._run()
        out = self.output_path.read_text()
        self.assertNotIn("A quoted remark.", out)
        self.assertNotIn("<!--block:B0007-->", out)
        self.assertEqual(report["counters"]["blocks_touched"], 1)

    def test_delete_last_block_leaves_no_trailing_blank(self):
        anchored = anchorize_text("Para one.\n\nPara two.\n")
        target = "B0002"
        patch = _base_patch(
            anchored,
            [
                {
                    "op": "delete_block",
                    "block_id": target,
                    "old_hash": _hash_of(anchored, target),
                    "roadmap_item_ids": ["REV-004"],
                }
            ],
        )
        self._write(anchored, patch)
        self._run()
        self.assertEqual(self.output_path.read_text(), "<!--block:B0001-->\nPara one.\n")


class TestPhase1Rejections(ApplyHarness):
    def test_stale_base_hash_rejects_whole_patch(self):
        anchored = self.anchored_fixture()
        patch = _base_patch(
            anchored,
            [
                {
                    "op": "delete_block",
                    "block_id": "B0001",
                    "old_hash": _hash_of(anchored, "B0001"),
                    "roadmap_item_ids": ["REV-001"],
                }
            ],
        )
        patch["base_draft_hash"] = "0" * 12
        self._write(anchored, patch)
        with self.assertRaises(ApplyRejection) as ctx:
            self._run()
        self.assertEqual(ctx.exception.failures[0]["kind"], "base_hash_mismatch")
        self._assert_no_artifacts()

    def test_one_stale_op_rejects_whole_patch_two_phase(self):
        anchored = self.anchored_fixture()
        good = {
            "op": "replace_block",
            "block_id": "B0002",
            "old_hash": _hash_of(anchored, "B0002"),
            "new_text": "Valid replacement.",
            "roadmap_item_ids": ["REV-001"],
        }
        stale = {
            "op": "replace_block",
            "block_id": "B0003",
            "old_hash": "f" * 12,
            "new_text": "Stale replacement.",
            "roadmap_item_ids": ["REV-001"],
        }
        self._write(anchored, _base_patch(anchored, [good, stale]))
        with self.assertRaises(ApplyRejection) as ctx:
            self._run()
        kinds = {f["kind"] for f in ctx.exception.failures}
        self.assertEqual(kinds, {"hash_mismatch"})
        self.assertEqual(ctx.exception.failures[0]["op_index"], 1)
        self._assert_no_artifacts()

    def test_unknown_block_id(self):
        anchored = self.anchored_fixture()
        patch = _base_patch(
            anchored,
            [
                {
                    "op": "delete_block",
                    "block_id": "B9999",
                    "old_hash": "a" * 12,
                    "roadmap_item_ids": ["REV-001"],
                }
            ],
        )
        self._write(anchored, patch)
        with self.assertRaises(ApplyRejection) as ctx:
            self._run()
        self.assertEqual(ctx.exception.failures[0]["kind"], "unknown_block_id")

    def test_duplicate_target_any_role(self):
        anchored = self.anchored_fixture()
        h = _hash_of(anchored, "B0003")
        ops = [
            {
                "op": "replace_block",
                "block_id": "B0003",
                "old_hash": h,
                "new_text": "Replacement.",
                "roadmap_item_ids": ["REV-001"],
            },
            {
                "op": "insert_after",
                "block_id": "B0003",
                "old_hash": h,
                "new_text": "Insertion on the same anchor.",
                "roadmap_item_ids": ["REV-001"],
            },
        ]
        self._write(anchored, _base_patch(anchored, ops))
        with self.assertRaises(ApplyRejection) as ctx:
            self._run()
        kinds = [f["kind"] for f in ctx.exception.failures]
        self.assertIn("duplicate_target", kinds)

    def test_marker_in_new_text_rejected(self):
        anchored = self.anchored_fixture()
        patch = _base_patch(
            anchored,
            [
                {
                    "op": "replace_block",
                    "block_id": "B0002",
                    "old_hash": _hash_of(anchored, "B0002"),
                    "new_text": "<!--block:B0099-->\nSmuggled marker.",
                    "roadmap_item_ids": ["REV-001"],
                }
            ],
        )
        self._write(anchored, patch)
        with self.assertRaises(ApplyRejection) as ctx:
            self._run()
        self.assertEqual(ctx.exception.failures[0]["kind"], "marker_in_new_text")

    def test_new_text_unsupported_construct_rejected_by_name(self):
        anchored = self.anchored_fixture()
        patch = _base_patch(
            anchored,
            [
                {
                    "op": "replace_block",
                    "block_id": "B0002",
                    "old_hash": _hash_of(anchored, "B0002"),
                    "new_text": "Heading text\n===",
                    "roadmap_item_ids": ["REV-001"],
                }
            ],
        )
        self._write(anchored, patch)
        with self.assertRaises(ApplyRejection) as ctx:
            self._run()
        self.assertEqual(
            ctx.exception.failures[0]["kind"],
            "new_text_invalid:unsupported_construct:setext_underline",
        )

    def test_schema_rejects_hashless_op_of_any_other_shape(self):
        anchored = self.anchored_fixture()
        patch = _base_patch(
            anchored,
            [
                {
                    "op": "replace_block",
                    "block_id": "B0002",
                    "new_text": "No old_hash on a replace.",
                    "roadmap_item_ids": ["REV-001"],
                }
            ],
        )
        self._write(anchored, patch)
        with self.assertRaises(ApplyRejection) as ctx:
            self._run()
        self.assertTrue(all(f["kind"] == "schema_invalid" for f in ctx.exception.failures))

    def test_schema_rejects_doc_body_start_with_hash(self):
        anchored = self.anchored_fixture()
        patch = _base_patch(
            anchored,
            [
                {
                    "op": "insert_after",
                    "block_id": "DOC-BODY-START",
                    "old_hash": "a" * 12,
                    "new_text": "Opening.",
                    "roadmap_item_ids": ["REV-001"],
                }
            ],
        )
        self._write(anchored, patch)
        with self.assertRaises(ApplyRejection) as ctx:
            self._run()
        self.assertTrue(all(f["kind"] == "schema_invalid" for f in ctx.exception.failures))

    def test_duplicate_doc_body_start_rejected(self):
        anchored = self.anchored_fixture()
        op = {
            "op": "insert_after",
            "block_id": "DOC-BODY-START",
            "new_text": "Opening.",
            "roadmap_item_ids": ["REV-001"],
        }
        self._write(anchored, _base_patch(anchored, [op, dict(op)]))
        with self.assertRaises(ApplyRejection) as ctx:
            self._run()
        self.assertIn("duplicate_target", [f["kind"] for f in ctx.exception.failures])

    def test_output_naming_base_is_rejected(self):
        anchored = self.anchored_fixture()
        patch = _base_patch(
            anchored,
            [
                {
                    "op": "delete_block",
                    "block_id": "B0008",
                    "old_hash": _hash_of(anchored, "B0008"),
                    "roadmap_item_ids": ["REV-001"],
                }
            ],
        )
        self._write(anchored, patch)
        base_bytes = self.base_path.read_bytes()
        with self.assertRaises(ApplyRejection) as ctx:
            run(
                self.base_path,
                self.patch_path,
                self.base_path,  # --output naming the base
                self.report_path,
                acknowledge_structural=False,
                touched_ratio_threshold=None,
            )
        self.assertEqual(ctx.exception.failures[0]["kind"], "artifact_path_collision")
        self.assertEqual(self.base_path.read_bytes(), base_bytes)

    def test_report_naming_base_is_rejected(self):
        anchored = self.anchored_fixture()
        patch = _base_patch(
            anchored,
            [
                {
                    "op": "delete_block",
                    "block_id": "B0008",
                    "old_hash": _hash_of(anchored, "B0008"),
                    "roadmap_item_ids": ["REV-001"],
                }
            ],
        )
        self._write(anchored, patch)
        base_bytes = self.base_path.read_bytes()
        with self.assertRaises(ApplyRejection) as ctx:
            run(
                self.base_path,
                self.patch_path,
                self.output_path,
                self.base_path,  # --report-out naming the base
                acknowledge_structural=False,
                touched_ratio_threshold=None,
            )
        self.assertEqual(ctx.exception.failures[0]["kind"], "artifact_path_collision")
        self.assertEqual(self.base_path.read_bytes(), base_bytes)
        self.assertFalse(self.output_path.exists())

    def test_existing_output_is_rejected_not_overwritten(self):
        anchored = self.anchored_fixture()
        patch = _base_patch(
            anchored,
            [
                {
                    "op": "delete_block",
                    "block_id": "B0008",
                    "old_hash": _hash_of(anchored, "B0008"),
                    "roadmap_item_ids": ["REV-001"],
                }
            ],
        )
        self._write(anchored, patch)
        self.output_path.write_text("pre-existing artifact, not ours to replace")
        with self.assertRaises(ApplyRejection) as ctx:
            self._run()
        self.assertEqual(ctx.exception.failures[0]["kind"], "artifact_already_exists")
        self.assertEqual(
            self.output_path.read_text(), "pre-existing artifact, not ours to replace"
        )

    def test_report_naming_output_is_rejected(self):
        anchored = self.anchored_fixture()
        patch = _base_patch(
            anchored,
            [
                {
                    "op": "delete_block",
                    "block_id": "B0008",
                    "old_hash": _hash_of(anchored, "B0008"),
                    "roadmap_item_ids": ["REV-001"],
                }
            ],
        )
        self._write(anchored, patch)
        with self.assertRaises(ApplyRejection) as ctx:
            run(
                self.base_path,
                self.patch_path,
                self.output_path,
                self.output_path,  # --report-out naming the output
                acknowledge_structural=False,
                touched_ratio_threshold=None,
            )
        self.assertEqual(ctx.exception.failures[0]["kind"], "artifact_path_collision")
        self._assert_no_artifacts()

    def test_report_write_failure_removes_output(self):
        anchored = self.anchored_fixture()
        patch = _base_patch(
            anchored,
            [
                {
                    "op": "delete_block",
                    "block_id": "B0008",
                    "old_hash": _hash_of(anchored, "B0008"),
                    "roadmap_item_ids": ["REV-001"],
                }
            ],
        )
        self._write(anchored, patch)
        real_atomic = __import__(
            "scripts.ars_apply_revision_patch", fromlist=["atomic_write_bytes"]
        ).atomic_write_bytes

        def fail_on_report(path, data):
            if str(path) == str(self.report_path):
                raise OSError("disk full")
            real_atomic(path, data)

        with mock.patch(
            "scripts.ars_apply_revision_patch.atomic_write_bytes", side_effect=fail_on_report
        ):
            with self.assertRaises(OSError):
                self._run()
        self._assert_no_artifacts()

    def test_unanchored_base_block_cannot_be_targeted(self):
        # A base with an unlabeled block parses fine; only labeled blocks
        # are addressable. (Phase 1 sees the unknown ID.)
        base = "<!--block:B0001-->\nLabeled.\n\nUnlabeled paragraph.\n"
        patch = _base_patch(
            base,
            [
                {
                    "op": "delete_block",
                    "block_id": "B0002",
                    "old_hash": "a" * 12,
                    "roadmap_item_ids": ["REV-001"],
                }
            ],
        )
        self._write(base, patch)
        with self.assertRaises(ApplyRejection) as ctx:
            self._run()
        self.assertEqual(ctx.exception.failures[0]["kind"], "unknown_block_id")


class TestStructuralTriggers(ApplyHarness):
    def _heading_patch(self, anchored: str) -> dict:
        target = "B0001"  # "# Introduction"
        return _base_patch(
            anchored,
            [
                {
                    "op": "replace_block",
                    "block_id": target,
                    "old_hash": _hash_of(anchored, target),
                    "new_text": "# Renamed Introduction",
                    "roadmap_item_ids": ["REV-005"],
                }
            ],
        )

    def test_heading_op_refused_without_acknowledge(self):
        anchored = self.anchored_fixture()
        self._write(anchored, self._heading_patch(anchored))
        with self.assertRaises(StructuralRefusal) as ctx:
            self._run()
        self.assertEqual(ctx.exception.flags["heading_op_indexes"], [0])
        self._assert_no_artifacts()

    def test_heading_op_proceeds_with_acknowledge_and_is_recorded(self):
        anchored = self.anchored_fixture()
        self._write(anchored, self._heading_patch(anchored))
        report = self._run(acknowledge_structural=True)
        self.assertTrue(report["structural_flags"]["any"])
        self.assertTrue(report["structural_flags"]["acknowledged"])
        self.assertIn("# Renamed Introduction", self.output_path.read_text())

    def test_insert_after_heading_anchor_exempt_when_no_heading_segments(self):
        # #424 heading-anchor exemption: an insert_after ANCHORED on a
        # heading does not flag when its new_text contains no heading —
        # the heading's bytes are untouched and "insert body text after a
        # section heading" is the most common legitimate insertion.
        anchored = self.anchored_fixture()
        patch = _base_patch(
            anchored,
            [
                {
                    "op": "insert_after",
                    "block_id": "B0004",
                    "old_hash": _hash_of(anchored, "B0004"),
                    "new_text": "Plain body text right after the Methods heading.",
                    "roadmap_item_ids": ["REV-005"],
                }
            ],
        )
        self._write(anchored, patch)
        report = self._run()
        self.assertEqual(report["structural_flags"]["heading_op_indexes"], [])
        self.assertEqual(report["structural_flags"]["section_count_delta"], 0)
        self.assertFalse(report["structural_flags"]["any"])

    def test_insert_after_heading_anchor_with_heading_segments_still_fires(self):
        # The exemption is anchor-only: heading-bearing new_text flags via
        # its segments regardless of what the anchor is.
        anchored = self.anchored_fixture()
        patch = _base_patch(
            anchored,
            [
                {
                    "op": "insert_after",
                    "block_id": "B0004",
                    "old_hash": _hash_of(anchored, "B0004"),
                    "new_text": "## Sneaky New Section\n\nBody under it.",
                    "roadmap_item_ids": ["REV-005"],
                }
            ],
        )
        self._write(anchored, patch)
        with self.assertRaises(StructuralRefusal) as ctx:
            self._run()
        self.assertEqual(ctx.exception.flags["heading_op_indexes"], [0])
        self.assertEqual(ctx.exception.flags["section_count_delta"], 1)

    def test_section_count_change_fires(self):
        anchored = self.anchored_fixture()
        patch = _base_patch(
            anchored,
            [
                {
                    "op": "insert_after",
                    "block_id": "B0003",
                    "old_hash": _hash_of(anchored, "B0003"),
                    "new_text": "## A Whole New Section\n\nWith body text.",
                    "roadmap_item_ids": ["REV-005"],
                }
            ],
        )
        self._write(anchored, patch)
        with self.assertRaises(StructuralRefusal) as ctx:
            self._run()
        self.assertEqual(ctx.exception.flags["section_count_delta"], 1)

    def test_touched_ratio_triggers_only_with_threshold(self):
        anchored = anchorize_text("One.\n\nTwo.\n\nThree.\n\nFour.\n")
        ops = [
            {
                "op": "replace_block",
                "block_id": bid,
                "old_hash": _hash_of(anchored, bid),
                "new_text": f"Rewritten {bid}.",
                "roadmap_item_ids": ["REV-001"],
            }
            for bid in ("B0001", "B0002", "B0003")
        ]
        self._write(anchored, _base_patch(anchored, ops))
        with self.assertRaises(StructuralRefusal) as ctx:
            self._run(touched_ratio_threshold=0.5)
        self.assertTrue(ctx.exception.flags["touched_ratio_exceeded"])
        self.assertAlmostEqual(ctx.exception.flags["touched_ratio"], 0.75)

        # API-level None: the ratio is recorded but never triggers (kept
        # for callers that own their own escalation policy; the CLI
        # default is DEFAULT_TOUCHED_RATIO_THRESHOLD, tested below).
        report = self._run()
        self.assertAlmostEqual(report["structural_flags"]["touched_ratio"], 0.75)
        self.assertFalse(report["structural_flags"]["touched_ratio_exceeded"])
        self.assertIsNone(report["structural_flags"]["touched_ratio_threshold"])

    def test_cli_default_threshold_is_the_ship_decision(self):
        # #424 ship decision: the CLI defaults to 0.6 and the comparator
        # is strict — 0.75 > 0.6 fires without any flag passed.
        self.assertEqual(DEFAULT_TOUCHED_RATIO_THRESHOLD, 0.6)
        anchored = anchorize_text("One.\n\nTwo.\n\nThree.\n\nFour.\n")
        ops = [
            {
                "op": "replace_block",
                "block_id": bid,
                "old_hash": _hash_of(anchored, bid),
                "new_text": f"Rewritten {bid}.",
                "roadmap_item_ids": ["REV-001"],
            }
            for bid in ("B0001", "B0002", "B0003")
        ]
        self._write(anchored, _base_patch(anchored, ops))
        argv = [
            str(self.base_path),
            str(self.patch_path),
            *self._cli_authority_args(),
            "--output",
            str(self.output_path),
        ]
        self.assertEqual(main(argv), 3)
        self.assertFalse(self.output_path.exists())
        # Strict comparator boundary: a threshold equal to the ratio does
        # not fire ("above a threshold", spec §3.3) — and 1.0 disables.
        self.assertEqual(main(argv + ["--touched-ratio-threshold", "0.75"]), 0)

    def test_nonfinite_and_out_of_range_threshold_rejected_at_cli(self):
        # codex P2: NaN makes `ratio > NaN` silently False (disables the
        # trigger off the documented 1.0 path); inf disables; negatives
        # over-trigger. argparse must reject all of them before run().
        anchored = anchorize_text("One.\n\nTwo.\n\nThree.\n\nFour.\n")
        ops = [
            {
                "op": "replace_block",
                "block_id": "B0001",
                "old_hash": _hash_of(anchored, "B0001"),
                "new_text": "Rewritten B0001.",
                "roadmap_item_ids": ["REV-001"],
            }
        ]
        self._write(anchored, _base_patch(anchored, ops))
        argv = [
            str(self.base_path),
            str(self.patch_path),
            *self._cli_authority_args(),
            "--output",
            str(self.output_path),
        ]
        for bad in ("nan", "inf", "-0.1", "1.5"):
            with self.assertRaises(SystemExit) as ctx:
                main(argv + ["--touched-ratio-threshold", bad])
            self.assertEqual(ctx.exception.code, 2)  # argparse usage error
            self.assertFalse(self.output_path.exists())


class TestPureMove(ApplyHarness):
    def test_byte_equal_relocation_recorded(self):
        anchored = self.anchored_fixture()
        moved_text = "Second paragraph, destined for surgery."
        ops = [
            {
                "op": "delete_block",
                "block_id": "B0003",
                "old_hash": _hash_of(anchored, "B0003"),
                "roadmap_item_ids": ["REV-006"],
            },
            {
                "op": "insert_after",
                "block_id": "B0007",
                "old_hash": _hash_of(anchored, "B0007"),
                "new_text": moved_text,
                "roadmap_item_ids": ["REV-006"],
            },
        ]
        self._write(anchored, _base_patch(anchored, ops))
        report = self._run()
        pairs = report["pure_move_pairs"]
        self.assertEqual(len(pairs), 1)
        self.assertEqual(pairs[0]["from_block_id"], "B0003")
        self.assertEqual(pairs[0]["to_block_id"], "B0009")

    def test_reworded_relocation_not_claimed_as_pure(self):
        anchored = self.anchored_fixture()
        ops = [
            {
                "op": "delete_block",
                "block_id": "B0003",
                "old_hash": _hash_of(anchored, "B0003"),
                "roadmap_item_ids": ["REV-006"],
            },
            {
                "op": "insert_after",
                "block_id": "B0007",
                "old_hash": _hash_of(anchored, "B0007"),
                "new_text": "Second paragraph, reworded during the move.",
                "roadmap_item_ids": ["REV-006"],
            },
        ]
        self._write(anchored, _base_patch(anchored, ops))
        report = self._run()
        self.assertEqual(report["pure_move_pairs"], [])


class TestAtomicityAndSelfCheck(ApplyHarness):
    def test_injected_rename_failure_leaves_no_artifacts(self):
        anchored = self.anchored_fixture()
        patch = _base_patch(
            anchored,
            [
                {
                    "op": "replace_block",
                    "block_id": "B0002",
                    "old_hash": _hash_of(anchored, "B0002"),
                    "new_text": "Replacement.",
                    "roadmap_item_ids": ["REV-001"],
                }
            ],
        )
        self._write(anchored, patch)
        base_bytes = self.base_path.read_bytes()
        with mock.patch("scripts._block_parser.os.replace", side_effect=OSError("disk full")):
            with self.assertRaises(OSError):
                self._run()
        self._assert_no_artifacts()
        self.assertEqual(self.base_path.read_bytes(), base_bytes)
        stray = [p for p in self.tmp.iterdir() if p.name.startswith(".revised")]
        self.assertEqual(stray, [])

    def test_post_apply_output_reparses_with_unique_markers(self):
        anchored = self.anchored_fixture()
        ops = [
            {
                "op": "insert_after",
                "block_id": "B0005",
                "old_hash": _hash_of(anchored, "B0005"),
                "new_text": "Inserted A.\n\nInserted B.",
                "roadmap_item_ids": ["REV-001"],
            },
            {
                "op": "replace_block",
                "block_id": "B0008",
                "old_hash": _hash_of(anchored, "B0008"),
                "new_text": "New closing.\n\nExtra closing block.",
                "roadmap_item_ids": ["REV-001"],
            },
        ]
        self._write(anchored, _base_patch(anchored, ops))
        self._run()
        out_doc = parse_document(self.output_path.read_text())
        ids = [b.block_id for b in out_doc.blocks]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(i is not None for i in ids))


class TestReportOutputHash(ApplyHarness):
    """#576 pre-work: the apply report binds the revised draft it describes.

    Without an output-side hash, a report can be paired with a draft that was
    rewritten after apply (e.g. a finalizer pass) and nothing detects the swap
    at the Stage 4 -> 3' handoff.
    """

    def _single_replace_patch(self, anchored: str) -> dict:
        return _base_patch(
            anchored,
            [
                {
                    "op": "replace_block",
                    "block_id": "B0003",
                    "old_hash": _hash_of(anchored, "B0003"),
                    "new_text": "Second paragraph, fully revised.",
                    "roadmap_item_ids": ["REV-001"],
                }
            ],
        )

    def test_report_carries_output_draft_hash_of_written_bytes(self):
        anchored = self.anchored_fixture()
        self._write(anchored, self._single_replace_patch(anchored))
        report = self._run()
        self.assertEqual(
            report["output_draft_hash"],
            base_draft_hash(self.output_path.read_bytes()),
        )
        self.assertNotEqual(report["output_draft_hash"], report["base_draft_hash"])

    def test_persisted_report_matches_returned_report(self):
        anchored = self.anchored_fixture()
        self._write(anchored, self._single_replace_patch(anchored))
        report = self._run()
        persisted = json.loads(self.report_path.read_text(encoding="utf-8"))
        self.assertEqual(persisted["output_draft_hash"], report["output_draft_hash"])

    def test_report_format_version_bumped_for_authorization_witness(self):
        anchored = self.anchored_fixture()
        self._write(anchored, self._single_replace_patch(anchored))
        report = self._run()
        self.assertEqual(report["report_format_version"], "1.3")
        self.assertEqual(report["authorization_witness"]["status"], "pass")
        self.assertTrue(
            report["authorization_witness"]["unregistered_claim_drift_review_required"]
        )

    def test_report_carries_patch_digest_of_exact_patch_bytes(self):
        anchored = self.anchored_fixture()
        self._write(anchored, self._single_replace_patch(anchored))
        report = self._run()
        self.assertEqual(
            report["patch_digest"],
            hashlib.sha256(self.patch_path.read_bytes()).hexdigest(),
        )


class TestCliExitCodes(ApplyHarness):
    def test_ok_is_0_rejection_is_2_structural_is_3(self):
        anchored = self.anchored_fixture()
        patch = _base_patch(
            anchored,
            [
                {
                    "op": "replace_block",
                    "block_id": "B0002",
                    "old_hash": _hash_of(anchored, "B0002"),
                    "new_text": "Replacement.",
                    "roadmap_item_ids": ["REV-001"],
                }
            ],
        )
        self._write(anchored, patch)
        argv = [
            str(self.base_path),
            str(self.patch_path),
            *self._cli_authority_args(),
            "--output",
            str(self.output_path),
        ]
        self.assertEqual(main(argv), 0)

        patch["base_draft_hash"] = "0" * 12
        self.patch_path.write_text(json.dumps(patch))
        self.assertEqual(main(argv + ["--report-out", str(self.tmp / "r2.json")]), 2)

        heading_patch = _base_patch(
            anchored,
            [
                {
                    "op": "replace_block",
                    "block_id": "B0001",
                    "old_hash": _hash_of(anchored, "B0001"),
                    "new_text": "# Renamed",
                    "roadmap_item_ids": ["REV-001"],
                }
            ],
        )
        self._write(anchored, heading_patch)
        out2 = self.tmp / "revised2.md"
        self.assertEqual(
            main(
                [
                    str(self.base_path),
                    str(self.patch_path),
                    *self._cli_authority_args(),
                    "--output",
                    str(out2),
                ]
            ),
            3,
        )
        self.assertFalse(out2.exists())


class TestByteIdentityProperty(ApplyHarness):
    """§8.3: the core §4 claim tested directly, not asserted.

    For seeded randomized patches over fixture drafts, every block not
    named in ops — including its marker line and, when the neighbor is
    also untouched with no insertion between them, the separator bytes —
    is byte-equal between base and apply output.
    """

    def _random_patch(self, anchored: str, rng: random.Random) -> dict:
        doc = parse_document(anchored)
        # Avoid heading blocks so structural triggers stay quiet: this
        # property test is about preservation, not escalation.
        candidates = [b for b in doc.blocks if b.kind != "heading" and b.block_id]
        rng.shuffle(candidates)
        ops: list[dict] = []
        used: set[str] = set()
        n_ops = rng.randint(1, max(1, len(candidates) // 2))
        verbs = ["replace", "insert", "delete"]
        for block in candidates[:n_ops]:
            verb = rng.choice(verbs)
            if block.block_id in used:
                continue
            used.add(block.block_id)
            if verb == "replace":
                ops.append(
                    {
                        "op": "replace_block",
                        "block_id": block.block_id,
                        "old_hash": block.norm_hash,
                        "new_text": f"Rewritten content {rng.randint(0, 9999)}.",
                        "roadmap_item_ids": ["REV-RND"],
                    }
                )
            elif verb == "insert":
                ops.append(
                    {
                        "op": "insert_after",
                        "block_id": block.block_id,
                        "old_hash": block.norm_hash,
                        "new_text": f"Inserted paragraph {rng.randint(0, 9999)}.\n\nSecond insert paragraph.",
                        "roadmap_item_ids": ["REV-RND"],
                    }
                )
            else:
                ops.append(
                    {
                        "op": "delete_block",
                        "block_id": block.block_id,
                        "old_hash": block.norm_hash,
                        "roadmap_item_ids": ["REV-RND"],
                    }
                )
        return _base_patch(anchored, ops)

    def test_untouched_blocks_byte_identical_across_random_patches(self):
        # Fixture variants rotate LF / frontmatter / CRLF / no-final-EOL
        # so newline-byte regressions (CRLF translation, EOF handling)
        # cannot hide behind text-mode reads: all comparisons run over
        # translation-free decodes of the raw output bytes.
        variants = [
            anchorize_text(FIXTURE_BODY),
            anchorize_text(FIXTURE_WITH_FRONTMATTER),
            anchorize_text(FIXTURE_BODY.replace("\n", "\r\n")),
            anchorize_text(FIXTURE_BODY[:-1]),  # final block without EOL
        ]
        for seed in range(12):
            rng = random.Random(seed)
            anchored = variants[seed % len(variants)]
            patch = self._random_patch(anchored, rng)
            tmp = Path(tempfile.mkdtemp())
            base_path = tmp / "base.md"
            patch_path = tmp / "patch.json"
            output_path = tmp / "out.md"
            base_path.write_bytes(anchored.encode("utf-8"))
            authority_kwargs = _authority_fixture(tmp, anchored, patch)
            patch_path.write_text(json.dumps(patch))
            run(
                base_path,
                patch_path,
                output_path,
                tmp / "report.json",
                acknowledge_structural=False,
                touched_ratio_threshold=None,
                **authority_kwargs,
            )
            out_text = output_path.read_bytes().decode("utf-8")

            base_doc = parse_document(anchored)
            out_doc = parse_document(out_text)
            named = {op["block_id"] for op in patch["ops"]}
            inserted_after = {
                op["block_id"] for op in patch["ops"] if op["op"] == "insert_after"
            }
            out_by_id = out_doc.block_by_id()

            base_blocks = base_doc.blocks
            for i, block in enumerate(base_blocks):
                if block.block_id in named:
                    continue
                # Marker line + content bytes byte-equal (§4 row 1).
                base_unit = anchored[block.full_start : block.span[1]]
                out_block = out_by_id[block.block_id]
                out_unit = out_text[out_block.full_start : out_block.span[1]]
                self.assertEqual(
                    base_unit, out_unit, f"seed {seed}: block {block.block_id} not byte-identical"
                )
                # Separator bytes to the next block, when that neighbor is
                # untouched too and nothing was inserted between them.
                if i + 1 < len(base_blocks):
                    nxt = base_blocks[i + 1]
                    if (
                        nxt.block_id not in named
                        and block.block_id not in inserted_after
                    ):
                        base_sep = anchored[block.span[1] : nxt.full_start]
                        out_nxt = out_by_id[nxt.block_id]
                        out_sep = out_text[out_block.span[1] : out_nxt.full_start]
                        self.assertEqual(
                            base_sep,
                            out_sep,
                            f"seed {seed}: separator after {block.block_id} changed",
                        )


if __name__ == "__main__":
    unittest.main()
