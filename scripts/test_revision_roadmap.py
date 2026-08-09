"""Hermetic mutation tests for the #670 non-ranking revision contract."""
from __future__ import annotations

import copy
import json
import os
import tempfile
import unittest
from pathlib import Path

from scripts._block_parser import base_draft_hash, parse_document
from scripts.ars_anchorize_draft import anchorize_text, build_manifest
from scripts.ars_apply_revision_patch import ApplyRejection, run
from scripts.revision_roadmap import (
    ArtifactStore,
    ContractError,
    author_decision_digest,
    build_author_adjudication,
    build_integrity_authorization,
    bytes_hash,
    load_json_path,
    render_markdown,
    source_finding_projection,
    validate_author_adjudication,
    validate_block_manifest,
    validate_bundle,
    validate_claim_surface_manifest,
    validate_integrity_authorization,
    validate_integrity_patch_authorization,
    validate_review_patch_authorization,
    validate_roadmap,
)

MANIFEST_ID = "M-2026-08-10T00:00:00Z-abcd"
CLAIM_ID = "C-001"
ORIGINAL_CLAIM = "The treatment is associated with improved outcomes."
REPLACEMENT_CLAIM = "The treatment causes improved outcomes."


def _raw(value: dict) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        + "\n"
    ).encode("utf-8")


def _write(path: Path, value: dict) -> bytes:
    raw = _raw(value)
    path.write_bytes(raw)
    return raw


def _artifact(path: Path, root: Path) -> dict:
    raw = path.read_bytes()
    return {"path": path.relative_to(root).as_posix(), "sha256": bytes_hash(raw)}


def _target(block_id: str, *ops: str) -> dict:
    order = {"replace_block": 0, "insert_after": 1, "delete_block": 2}
    return {"block_id": block_id, "allowed_operations": sorted(ops, key=order.__getitem__)}


class RevisionFixture:
    def __init__(
        self,
        *,
        declined_overlap: bool = False,
        claim_authorized: bool = False,
        all_declined: bool = False,
    ):
        self.root = Path(tempfile.mkdtemp())
        self.base_path = self.root / "base.md"
        self.base = anchorize_text(
            "# Study\n\n"
            f"{ORIGINAL_CLAIM}\n\n"
            "A separate reporting sentence.\n"
        )
        self.base_raw = self.base.encode("utf-8")
        self.base_path.write_bytes(self.base_raw)
        parsed = parse_document(self.base)
        self.claim_block_id = "B0002"
        self.other_block_id = "B0003"

        self.block_manifest = build_manifest(self.base_raw, parsed)
        self.block_manifest_path = self.root / "block-manifest.json"
        self.block_manifest_raw = _write(self.block_manifest_path, self.block_manifest)

        self.claim_intent = {
            "manifest_version": "1.0",
            "manifest_id": MANIFEST_ID,
            "emitted_by": "draft_writer_agent",
            "emitted_at": "2026-08-10T00:00:00Z",
            "claims": [
                {
                    "claim_id": CLAIM_ID,
                    "claim_text": ORIGINAL_CLAIM,
                    "intended_evidence_kind": "empirical",
                    "planned_refs": [],
                }
            ],
            "manifest_negative_constraints": [],
        }
        self.claim_intent_path = self.root / "claim-intent.json"
        self.claim_intent_raw = _write(self.claim_intent_path, self.claim_intent)

        items = [
            self._roadmap_item(
                "REV-001", 1, self.claim_block_id, "replace_block"
            )
        ]
        if declined_overlap:
            items.append(
                self._roadmap_item(
                    "REV-002", 2, self.claim_block_id, "replace_block"
                )
            )
        self.roadmap = {
            "schema_version": "revision-roadmap/1.0",
            "revision_round": 1,
            "base_draft_sha256": bytes_hash(self.base_raw),
            "block_manifest_sha256": bytes_hash(self.block_manifest_raw),
            "items": items,
            "total_items": len(items),
            "obligation_counts": {
                "must_fix": 1,
                "should_fix": len(items) - 1,
                "consider": 0,
            },
            "editorial_decision": "Major Revision",
            "consensus_summary": "The declared finding set requires author adjudication.",
            "dissenting_opinions": [],
        }
        self.roadmap_path = self.root / "roadmap.json"
        self.roadmap_raw = _write(self.roadmap_path, self.roadmap)

        start = self.base_raw.index(ORIGINAL_CLAIM.encode("utf-8"))
        end = start + len(ORIGINAL_CLAIM.encode("utf-8"))
        self.surface = {
            "surface_id": "CLAIM-SURFACE-001",
            "scoped_manifest_id": MANIFEST_ID,
            "claim_id": CLAIM_ID,
            "block_id": self.claim_block_id,
            "utf8_start": start,
            "utf8_end": end,
            "original_text": ORIGINAL_CLAIM,
            "original_text_sha256": bytes_hash(ORIGINAL_CLAIM.encode("utf-8")),
            "intent_claim_text_sha256": bytes_hash(ORIGINAL_CLAIM.encode("utf-8")),
            "current_rung": "association",
        }
        self.claim_surface = {
            "schema_version": "claim-surface-manifest/1.0",
            "revision_round": 1,
            "roadmap_sha256": bytes_hash(self.roadmap_raw),
            "base_draft_sha256": bytes_hash(self.base_raw),
            "claim_intent_sources": [
                {
                    "scoped_manifest_id": MANIFEST_ID,
                    "artifact": _artifact(self.claim_intent_path, self.root),
                }
            ],
            "surfaces": [self.surface],
        }
        self.claim_surface_path = self.root / "claim-surfaces.json"
        self.claim_surface_raw = _write(self.claim_surface_path, self.claim_surface)
        self.surfaces = validate_claim_surface_manifest(
            self.claim_surface,
            claim_surface_raw=self.claim_surface_raw,
            roadmap=self.roadmap,
            roadmap_raw=self.roadmap_raw,
            base_raw=self.base_raw,
            artifact_store=ArtifactStore(self.root),
        )

        event_id = "AUTHOR-EVENT-fixture"
        claim_auth = self._claim_authorization(event_id) if claim_authorized else None
        decisions = []
        for item in items:
            declined = all_declined or item["id"] == "REV-002"
            if declined:
                decisions.append(
                    {
                        "item_id": item["id"],
                        "author_event_id": event_id,
                        "author_triage": "wont_address",
                        "author_reason": "The author explicitly declines this item.",
                        "authorized_targets": [],
                        "claim_strength_authorizations": [],
                    }
                )
            else:
                decisions.append(
                    {
                        "item_id": item["id"],
                        "author_event_id": event_id,
                        "author_triage": "will_address",
                        "authorized_targets": item["proposed_targets"],
                        "claim_strength_authorizations": [claim_auth] if claim_auth else [],
                    }
                )
        self.author = {
            "schema_version": "author-adjudication/1.0",
            "revision_round": 1,
            "roadmap_sha256": bytes_hash(self.roadmap_raw),
            "base_draft_sha256": bytes_hash(self.base_raw),
            "claim_surface_manifest_sha256": bytes_hash(self.claim_surface_raw),
            "adjudication_status": "complete",
            "author_events": [
                {
                    "event_id": event_id,
                    "source": "explicit_session_user_message",
                    "actor_role": "author",
                    "input_sha256": bytes_hash(b"explicit fixture author decision"),
                }
            ],
            "display_order": {
                "mode": "source_traceability",
                "item_ids": [item["id"] for item in items],
                "author_event_id": event_id,
            },
            "author_adjudications": decisions,
            "collateral_authorizations": [],
        }
        self.author_path = self.root / "author.json"
        self.author_raw = _write(self.author_path, self.author)

        replacement = REPLACEMENT_CLAIM if claim_authorized else ORIGINAL_CLAIM + " Added context."
        op = {
            "op": "replace_block",
            "block_id": self.claim_block_id,
            "old_hash": parsed.block_by_id()[self.claim_block_id].norm_hash,
            "new_text": replacement,
            "roadmap_item_ids": ["REV-001"],
            "claim_strength_changes": [self._claim_change(claim_auth)] if claim_auth else [],
            "collateral_authorization_ids": [],
        }
        self.patch = {
            "patch_format_version": "1.1",
            "authorization_context": "review_roadmap",
            "revision_round": 1,
            "base_draft_hash": base_draft_hash(self.base_raw),
            "roadmap_sha256": bytes_hash(self.roadmap_raw),
            "author_adjudication_sha256": bytes_hash(self.author_raw),
            "author_decision_digest": author_decision_digest(self.author),
            "claim_surface_manifest_sha256": bytes_hash(self.claim_surface_raw),
            "ops": [op],
            "emitted_by": "draft_writer_agent",
        }
        self.patch_path = self.root / "patch.json"
        self.patch_raw = _write(self.patch_path, self.patch)
        self.output_path = self.root / "revised.md"
        self.report_path = self.root / "report.json"

    def _roadmap_item(self, item_id: str, ordinal: int, block_id: str, op: str) -> dict:
        return {
            "id": item_id,
            "source_refs": [
                {
                    "seat": "R1",
                    "channel": "finding",
                    "ordinal": ordinal,
                    "subclaim_ordinal": 0,
                }
            ],
            "description": f"Finding {item_id}",
            "reviewer": "R1",
            "obligation_class": "must_fix" if item_id == "REV-001" else "should_fix",
            "severity": "major",
            "evidence_anchor": {
                "anchor_type": "text",
                "locator": "Study paragraph",
                "quote": ORIGINAL_CLAIM,
            },
            "confidence": 5,
            "competence_basis": "Declared fixture competence.",
            "cost_scope": {"kind": "sentence", "locator": "Study claim sentence"},
            "consequence_if_unaddressed": {
                "code": "claim_scope_unsupported",
                "target": {"kind": "claim", "locator": f"{MANIFEST_ID}/{CLAIM_ID}"},
            },
            "target_section": "Study",
            "suggested_action": "Revise the declared sentence.",
            "consensus_level": "SINGLE-VERIFIER",
            "verification_criteria": "The declared claim surface is checked.",
            "proposed_targets": [_target(block_id, op)],
        }

    def _claim_authorization(self, event_id: str) -> dict:
        return {
            "authorization_id": "CLAIM-AUTH-001",
            "author_event_id": event_id,
            "surface_id": self.surface["surface_id"],
            "scoped_manifest_id": MANIFEST_ID,
            "claim_id": CLAIM_ID,
            "block_id": self.claim_block_id,
            "original_text_sha256": self.surface["original_text_sha256"],
            "replacement_text": REPLACEMENT_CLAIM,
            "replacement_text_sha256": bytes_hash(REPLACEMENT_CLAIM.encode("utf-8")),
            "from_rung": "association",
            "to_rung": "causal",
            "direction": "strengthen",
            "reason": "The author explicitly authorizes these exact replacement bytes.",
        }

    @staticmethod
    def _claim_change(authorization: dict) -> dict:
        return {
            field: authorization[field]
            for field in (
                "authorization_id",
                "surface_id",
                "scoped_manifest_id",
                "claim_id",
                "block_id",
                "original_text_sha256",
                "replacement_text_sha256",
                "from_rung",
                "to_rung",
                "direction",
            )
        }

    def validate_authority(self, patch: dict | None = None) -> dict:
        return validate_review_patch_authorization(
            patch or self.patch,
            base_raw=self.base_raw,
            roadmap=self.roadmap,
            roadmap_raw=self.roadmap_raw,
            adjudication=self.author,
            adjudication_raw=self.author_raw,
            claim_surface=self.claim_surface,
            claim_surface_raw=self.claim_surface_raw,
            surfaces_by_id=self.surfaces,
        )

    def apply(self) -> dict:
        return run(
            self.base_path,
            self.patch_path,
            self.output_path,
            self.report_path,
            acknowledge_structural=False,
            touched_ratio_threshold=None,
            block_manifest_path=self.block_manifest_path,
            roadmap_path=self.roadmap_path,
            author_adjudication_path=self.author_path,
            claim_surface_manifest_path=self.claim_surface_path,
            artifact_root=self.root,
        )


class TestImmutableRoadmap(unittest.TestCase):
    def test_core_and_author_sidecar_validate_separately(self):
        fixture = RevisionFixture()
        validate_block_manifest(
            fixture.block_manifest, fixture.block_manifest_raw, fixture.base_raw
        )
        validate_roadmap(
            fixture.roadmap,
            roadmap_raw=fixture.roadmap_raw,
            base_raw=fixture.base_raw,
            block_manifest=fixture.block_manifest,
            block_manifest_raw=fixture.block_manifest_raw,
        )
        validate_author_adjudication(
            fixture.author,
            adjudication_raw=fixture.author_raw,
            roadmap=fixture.roadmap,
            roadmap_raw=fixture.roadmap_raw,
            claim_surface=fixture.claim_surface,
            claim_surface_raw=fixture.claim_surface_raw,
            base_raw=fixture.base_raw,
            surfaces_by_id=fixture.surfaces,
        )

    def test_reviewer_core_rejects_embedded_author_choice(self):
        fixture = RevisionFixture()
        mutated = copy.deepcopy(fixture.roadmap)
        mutated["author_adjudications"] = []
        with self.assertRaises(ContractError):
            validate_roadmap(mutated)

    def test_sidecar_digest_rejects_rewritten_obligation(self):
        fixture = RevisionFixture()
        mutated = copy.deepcopy(fixture.roadmap)
        mutated["items"][0]["obligation_class"] = "consider"
        mutated["obligation_counts"] = {"must_fix": 0, "should_fix": 0, "consider": 1}
        mutated_raw = _raw(mutated)
        with self.assertRaisesRegex(ContractError, "roadmap_sha256"):
            validate_author_adjudication(
                fixture.author,
                adjudication_raw=fixture.author_raw,
                roadmap=mutated,
                roadmap_raw=mutated_raw,
                claim_surface=fixture.claim_surface,
                claim_surface_raw=fixture.claim_surface_raw,
                base_raw=fixture.base_raw,
                surfaces_by_id=fixture.surfaces,
            )

    def test_source_order_is_mechanical_and_author_view_does_not_mutate_findings(self):
        fixture = RevisionFixture(declined_overlap=True)
        before = source_finding_projection(fixture.roadmap)
        fixture.author["display_order"]["mode"] = "user_selected"
        fixture.author["display_order"]["item_ids"].reverse()
        self.assertEqual(source_finding_projection(fixture.roadmap), before)
        mutated = copy.deepcopy(fixture.roadmap)
        mutated["items"].reverse()
        with self.assertRaisesRegex(ContractError, "primary-source order"):
            validate_roadmap(mutated)

    def test_work_order_and_acceptance_prediction_language_fail_closed(self):
        fixture = RevisionFixture()
        mutations = (
            ("suggested_action", "Do this revision first.", "work-rank"),
            ("suggested_action", "This is rank 1 work.", "work-rank"),
            (
                "consequence_locator",
                "The manuscript will be accepted",
                "acceptance-prediction",
            ),
            (
                "consequence_locator",
                "75 percent acceptance probability",
                "acceptance-prediction",
            ),
        )
        for field, value, expected in mutations:
            with self.subTest(field=field, value=value):
                mutated = copy.deepcopy(fixture.roadmap)
                if field == "consequence_locator":
                    mutated["items"][0]["consequence_if_unaddressed"]["target"][
                        "locator"
                    ] = value
                else:
                    mutated["items"][0][field] = value
                with self.assertRaisesRegex(ContractError, expected):
                    validate_roadmap(mutated)

        transported = copy.deepcopy(fixture.roadmap)
        transported["items"][0]["description"] = (
            "The study ranks outcomes observed after two weeks."
        )
        validate_roadmap(transported)

    def test_builder_uses_only_explicit_choice_input_and_computed_bindings(self):
        fixture = RevisionFixture()
        choice = {
            "schema_version": "author-adjudication-input/1.0",
            "author_events": fixture.author["author_events"],
            "display_order": fixture.author["display_order"],
            "author_adjudications": fixture.author["author_adjudications"],
            "collateral_authorizations": [],
        }
        built = build_author_adjudication(
            choice,
            roadmap=fixture.roadmap,
            roadmap_raw=fixture.roadmap_raw,
            claim_surface=fixture.claim_surface,
            claim_surface_raw=fixture.claim_surface_raw,
            base_raw=fixture.base_raw,
            surfaces_by_id=fixture.surfaces,
        )
        self.assertEqual(built, fixture.author)
        bad = copy.deepcopy(choice)
        bad["reviewer_obligation_override"] = "consider"
        with self.assertRaises(ContractError):
            build_author_adjudication(
                bad,
                roadmap=fixture.roadmap,
                roadmap_raw=fixture.roadmap_raw,
                claim_surface=fixture.claim_surface,
                claim_surface_raw=fixture.claim_surface_raw,
                base_raw=fixture.base_raw,
                surfaces_by_id=fixture.surfaces,
            )

    def test_will_address_author_reason_is_rejected_at_authority_boundary(self):
        fixture = RevisionFixture()
        mutated = copy.deepcopy(fixture.author)
        mutated["author_adjudications"][0]["author_reason"] = (
            "A producer-authored explanation must not masquerade as author input."
        )
        with self.assertRaises(ContractError):
            validate_author_adjudication(
                mutated,
                adjudication_raw=_raw(mutated),
                roadmap=fixture.roadmap,
                roadmap_raw=fixture.roadmap_raw,
                claim_surface=fixture.claim_surface,
                claim_surface_raw=fixture.claim_surface_raw,
                base_raw=fixture.base_raw,
                surfaces_by_id=fixture.surfaces,
            )

        choice = {
            "schema_version": "author-adjudication-input/1.0",
            "author_events": mutated["author_events"],
            "display_order": mutated["display_order"],
            "author_adjudications": mutated["author_adjudications"],
            "collateral_authorizations": [],
        }
        with self.assertRaises(ContractError):
            build_author_adjudication(
                choice,
                roadmap=fixture.roadmap,
                roadmap_raw=fixture.roadmap_raw,
                claim_surface=fixture.claim_surface,
                claim_surface_raw=fixture.claim_surface_raw,
                base_raw=fixture.base_raw,
                surfaces_by_id=fixture.surfaces,
            )


class TestExactAuthority(unittest.TestCase):
    def test_accepted_item_cannot_authorize_arbitrary_block(self):
        fixture = RevisionFixture()
        patch = copy.deepcopy(fixture.patch)
        patch["ops"][0]["block_id"] = fixture.other_block_id
        patch["ops"][0]["old_hash"] = parse_document(fixture.base).block_by_id()[
            fixture.other_block_id
        ].norm_hash
        with self.assertRaisesRegex(ContractError, "outside accepted item"):
            fixture.validate_authority(patch)

    def test_declined_overlap_requires_exact_collateral(self):
        fixture = RevisionFixture(declined_overlap=True)
        with self.assertRaisesRegex(ContractError, "no-touch coverage mismatch"):
            fixture.validate_authority()

        event = fixture.author["author_events"][0]["event_id"]
        collateral = {
            "authorization_id": "COLLATERAL-AUTH-001",
            "author_event_id": event,
            "authorizing_item_id": "REV-001",
            "constrained_item_id": "REV-002",
            "block_id": fixture.claim_block_id,
            "operation": "replace_block",
            "reason": "The author explicitly permits this exact shared-block operation.",
        }
        fixture.author["collateral_authorizations"] = [collateral]
        fixture.author_raw = _raw(fixture.author)
        fixture.patch["author_adjudication_sha256"] = bytes_hash(fixture.author_raw)
        fixture.patch["author_decision_digest"] = author_decision_digest(fixture.author)
        fixture.patch["ops"][0]["collateral_authorization_ids"] = [
            collateral["authorization_id"]
        ]
        self.assertEqual(fixture.validate_authority()["status"], "pass")

        fixture.patch["ops"][0]["op"] = "delete_block"
        fixture.patch["ops"][0].pop("new_text")
        with self.assertRaises(ContractError):
            fixture.validate_authority()

    def test_known_claim_surface_cannot_change_without_exact_authorization(self):
        fixture = RevisionFixture()
        patch = copy.deepcopy(fixture.patch)
        patch["ops"][0]["new_text"] = REPLACEMENT_CLAIM
        with self.assertRaisesRegex(ContractError, "must remain exact or use authorization"):
            fixture.validate_authority(patch)

    def test_exact_claim_replacement_passes_and_is_reported(self):
        fixture = RevisionFixture(claim_authorized=True)
        witness = fixture.validate_authority()
        self.assertEqual(witness["registered_claim_surfaces_checked"], 1)
        self.assertTrue(witness["unregistered_claim_drift_review_required"])
        report = fixture.apply()
        self.assertEqual(report["report_format_version"], "1.3")
        self.assertIn(REPLACEMENT_CLAIM, fixture.output_path.read_text())
        self.assertEqual(
            report["ops_applied"][0]["claim_strength_changes"],
            fixture.patch["ops"][0]["claim_strength_changes"],
        )

    def test_claim_authorization_is_single_use_and_field_exact(self):
        fixture = RevisionFixture(claim_authorized=True)
        patch = copy.deepcopy(fixture.patch)
        duplicate = copy.deepcopy(patch["ops"][0]["claim_strength_changes"][0])
        duplicate["to_rung"] = "causal-plus"
        patch["ops"][0]["claim_strength_changes"].append(duplicate)
        with self.assertRaisesRegex(ContractError, "reused|differs"):
            fixture.validate_authority(patch)

    def test_distinct_authorization_ids_cannot_target_one_claim_surface(self):
        fixture = RevisionFixture(claim_authorized=True)
        duplicate = copy.deepcopy(
            fixture.author["author_adjudications"][0][
                "claim_strength_authorizations"
            ][0]
        )
        duplicate["authorization_id"] = "CLAIM-AUTH-002"
        duplicate["replacement_text"] = "The treatment may improve outcomes."
        duplicate["replacement_text_sha256"] = bytes_hash(
            duplicate["replacement_text"].encode("utf-8")
        )
        duplicate["to_rung"] = "qualified-association"
        duplicate["direction"] = "weaken"
        fixture.author["author_adjudications"][0][
            "claim_strength_authorizations"
        ].append(duplicate)
        with self.assertRaisesRegex(ContractError, "surface_id .* authorized more than once"):
            validate_author_adjudication(
                fixture.author,
                adjudication_raw=_raw(fixture.author),
                roadmap=fixture.roadmap,
                roadmap_raw=fixture.roadmap_raw,
                claim_surface=fixture.claim_surface,
                claim_surface_raw=fixture.claim_surface_raw,
                base_raw=fixture.base_raw,
                surfaces_by_id=fixture.surfaces,
            )

    def test_claim_surface_manifest_rejects_wrong_intent_pair_and_utf8_span(self):
        fixture = RevisionFixture()
        wrong_pair = copy.deepcopy(fixture.claim_surface)
        wrong_pair["surfaces"][0]["claim_id"] = "C-999"
        with self.assertRaisesRegex(ContractError, "does not resolve"):
            validate_claim_surface_manifest(
                wrong_pair,
                claim_surface_raw=_raw(wrong_pair),
                roadmap=fixture.roadmap,
                roadmap_raw=fixture.roadmap_raw,
                base_raw=fixture.base_raw,
                artifact_store=ArtifactStore(fixture.root),
            )
        wrong_span = copy.deepcopy(fixture.claim_surface)
        wrong_span["surfaces"][0]["utf8_start"] += 1
        with self.assertRaisesRegex(ContractError, "UTF-8 span"):
            validate_claim_surface_manifest(
                wrong_span,
                claim_surface_raw=_raw(wrong_span),
                roadmap=fixture.roadmap,
                roadmap_raw=fixture.roadmap_raw,
                base_raw=fixture.base_raw,
                artifact_store=ArtifactStore(fixture.root),
            )

        wrong_surface = copy.deepcopy(fixture.claim_surface)
        unrelated = "A separate reporting sentence."
        unrelated_raw = unrelated.encode("utf-8")
        start = fixture.base_raw.index(unrelated_raw)
        wrong_surface["surfaces"][0].update(
            {
                "block_id": fixture.other_block_id,
                "utf8_start": start,
                "utf8_end": start + len(unrelated_raw),
                "original_text": unrelated,
                "original_text_sha256": bytes_hash(unrelated_raw),
            }
        )
        with self.assertRaisesRegex(ContractError, "must equal.*ClaimIntent"):
            validate_claim_surface_manifest(
                wrong_surface,
                claim_surface_raw=_raw(wrong_surface),
                roadmap=fixture.roadmap,
                roadmap_raw=fixture.roadmap_raw,
                base_raw=fixture.base_raw,
                artifact_store=ArtifactStore(fixture.root),
            )

    def test_current_apply_rejects_patch_1_0_downgrade(self):
        fixture = RevisionFixture()
        legacy = {
            "patch_format_version": "1.0",
            "revision_round": 1,
            "base_draft_hash": base_draft_hash(fixture.base_raw),
            "ops": [
                {
                    "op": "replace_block",
                    "block_id": fixture.claim_block_id,
                    "old_hash": parse_document(fixture.base).block_by_id()[
                        fixture.claim_block_id
                    ].norm_hash,
                    "new_text": ORIGINAL_CLAIM,
                    "roadmap_item_ids": ["REV-001"],
                }
            ],
            "emitted_by": "draft_writer_agent",
        }
        fixture.patch_path.write_bytes(_raw(legacy))
        with self.assertRaises(ApplyRejection) as captured:
            fixture.apply()
        self.assertTrue(
            all(row["kind"] == "schema_invalid" for row in captured.exception.failures)
        )


class TestRendering(unittest.TestCase):
    def test_renderer_separates_fields_without_worklist_labels_or_time(self):
        fixture = RevisionFixture()
        rendered = render_markdown(
            fixture.roadmap,
            fixture.author,
            adjudication_raw=fixture.author_raw,
            roadmap_raw=fixture.roadmap_raw,
            claim_surface=fixture.claim_surface,
            claim_surface_raw=fixture.claim_surface_raw,
            base_raw=fixture.base_raw,
            surfaces_by_id=fixture.surfaces,
        )
        self.assertIn("Obligation class", rendered)
        self.assertIn("Severity", rendered)
        self.assertIn("Cost scope", rendered)
        self.assertNotIn("Priority 1", rendered)
        self.assertNotIn("Priority 2", rendered)
        self.assertNotIn("Priority 3", rendered)
        self.assertNotIn("Estimated Effort", rendered)
        self.assertIn("Proposed targets (proposal only; no write authority):", rendered)
        self.assertIn("Exact authorized targets:", rendered)
        self.assertIn("B0002: replace_block", rendered)

    def test_renderer_displays_exact_authority_and_declined_items_grant_none(self):
        fixture = RevisionFixture(declined_overlap=True)
        rendered = render_markdown(
            fixture.roadmap,
            fixture.author,
            adjudication_raw=fixture.author_raw,
            roadmap_raw=fixture.roadmap_raw,
            claim_surface=fixture.claim_surface,
            claim_surface_raw=fixture.claim_surface_raw,
            base_raw=fixture.base_raw,
            surfaces_by_id=fixture.surfaces,
        )
        accepted = rendered.split("## REV-001", 1)[1].split("## REV-002", 1)[0]
        declined = rendered.split("## REV-002", 1)[1]
        self.assertIn("Exact authorized targets:\n  - B0002: replace_block", accepted)
        self.assertIn("Proposed targets (proposal only; no write authority):", declined)
        self.assertIn("  - B0002: replace_block", declined)
        self.assertIn("Exact authorized targets: none — no write authority", declined)

    def test_author_renderer_requires_full_cross_artifact_replay(self):
        fixture = RevisionFixture()
        with self.assertRaisesRegex(ContractError, "replay inputs required"):
            render_markdown(fixture.roadmap, fixture.author)

        mutations = []
        missing = copy.deepcopy(fixture.author)
        missing["author_adjudications"] = []
        mutations.append((missing, "exactly one record"))
        duplicate = copy.deepcopy(fixture.author)
        duplicate["author_adjudications"].append(
            copy.deepcopy(duplicate["author_adjudications"][0])
        )
        mutations.append((duplicate, "duplicate item_id|exactly one record"))
        nonresolving = copy.deepcopy(fixture.author)
        nonresolving["author_adjudications"][0]["author_event_id"] = (
            "AUTHOR-EVENT-nonresolving"
        )
        mutations.append((nonresolving, "author_event_id does not resolve"))
        wrong_surface = copy.deepcopy(fixture.author)
        wrong_surface["claim_surface_manifest_sha256"] = "f" * 64
        mutations.append((wrong_surface, "claim_surface_manifest_sha256"))

        for mutated, expected in mutations:
            with self.subTest(expected=expected):
                with self.assertRaisesRegex(ContractError, expected):
                    render_markdown(
                        fixture.roadmap,
                        mutated,
                        adjudication_raw=_raw(mutated),
                        roadmap_raw=fixture.roadmap_raw,
                        claim_surface=fixture.claim_surface,
                        claim_surface_raw=fixture.claim_surface_raw,
                        base_raw=fixture.base_raw,
                        surfaces_by_id=fixture.surfaces,
                    )

    def test_pending_renderer_never_infers_author_choice(self):
        fixture = RevisionFixture()
        rendered = render_markdown(fixture.roadmap)
        self.assertIn("PENDING AUTHOR DECISION", rendered)
        self.assertIn(
            "Exact authorized targets: PENDING AUTHOR DECISION — no write authority",
            rendered,
        )
        self.assertNotIn("will_address", rendered)


class TestIntegrityCorrectionAuthority(unittest.TestCase):
    def _case(self):
        fixture = RevisionFixture()
        correction_id = "IL-MEDIUM-1"
        issue_list = {
            "schema_version": "integrity-correction-list/1.0",
            "revision_round": 1,
            "base_draft_sha256": bytes_hash(fixture.base_raw),
            "issues": [
                {
                    "correction_id": correction_id,
                    "description": "Correct the reporting sentence.",
                    "proposed_targets": [
                        _target(fixture.other_block_id, "replace_block")
                    ],
                }
            ],
        }
        issue_path = fixture.root / "integrity-issues.json"
        issue_raw = _write(issue_path, issue_list)
        patch = {
            "patch_format_version": "1.1",
            "authorization_context": "integrity_correction",
            "revision_round": 1,
            "base_draft_hash": base_draft_hash(fixture.base_raw),
            "issue_list_sha256": bytes_hash(issue_raw),
            "ops": [
                {
                    "op": "replace_block",
                    "block_id": fixture.other_block_id,
                    "old_hash": parse_document(fixture.base).block_by_id()[
                        fixture.other_block_id
                    ].norm_hash,
                    "new_text": "A corrected reporting sentence.",
                    "roadmap_item_ids": [correction_id],
                    "claim_strength_changes": [],
                    "collateral_authorization_ids": [],
                }
            ],
            "emitted_by": "draft_writer_agent",
        }
        patch_path = fixture.root / "integrity-patch.json"
        patch_raw = _write(patch_path, patch)
        event_id = "AUTHOR-EVENT-integrity-fixture"
        choices = {
            "schema_version": "integrity-correction-authorization-input/1.0",
            "revision_patch_sha256": bytes_hash(patch_raw),
            "author_events": [
                {
                    "event_id": event_id,
                    "source": "explicit_session_user_message",
                    "actor_role": "author",
                    "input_sha256": bytes_hash(
                        b"explicit author approval of the exact integrity patch"
                    ),
                }
            ],
            "author_decisions": [
                {
                    "correction_id": correction_id,
                    "author_event_id": event_id,
                    "decision": "authorize",
                    "authorized_targets": [
                        _target(fixture.other_block_id, "replace_block")
                    ],
                }
            ],
        }
        authorization = build_integrity_authorization(
            choices,
            issue_list=issue_list,
            issue_list_raw=issue_raw,
            patch=patch,
            patch_raw=patch_raw,
            base_raw=fixture.base_raw,
        )
        authorization_path = fixture.root / "integrity-authorization.json"
        authorization_raw = _write(authorization_path, authorization)
        return {
            "fixture": fixture,
            "issue_list": issue_list,
            "issue_path": issue_path,
            "issue_raw": issue_raw,
            "patch": patch,
            "patch_path": patch_path,
            "patch_raw": patch_raw,
            "authorization": authorization,
            "authorization_path": authorization_path,
            "authorization_raw": authorization_raw,
            "choices": choices,
        }

    @staticmethod
    def _validate(case):
        return validate_integrity_patch_authorization(
            case["patch"],
            patch_raw=case["patch_raw"],
            base_raw=case["fixture"].base_raw,
            issue_list=case["issue_list"],
            issue_list_raw=case["issue_raw"],
            integrity_authorization=case["authorization"],
            integrity_authorization_raw=case["authorization_raw"],
        )

    def test_exact_author_patch_approval_is_required_and_replayed(self):
        case = self._case()
        witness = self._validate(case)
        self.assertEqual(witness["status"], "pass")
        self.assertEqual(
            witness["authorization_kind"],
            "explicit_author_exact_integrity_patch",
        )
        fixture = case["fixture"]
        output = fixture.root / "integrity-output.md"
        report = fixture.root / "integrity-report.json"
        applied = run(
            fixture.base_path,
            case["patch_path"],
            output,
            report,
            acknowledge_structural=False,
            touched_ratio_threshold=None,
            block_manifest_path=fixture.block_manifest_path,
            integrity_issue_list_path=case["issue_path"],
            integrity_authorization_path=case["authorization_path"],
        )
        self.assertEqual(applied["authorization_witness"], witness)
        self.assertIn("corrected reporting", output.read_text(encoding="utf-8"))

        without_authorization = self._case()
        second = without_authorization["fixture"]
        with self.assertRaisesRegex(ApplyRejection, "validation failure") as captured:
            run(
                second.base_path,
                without_authorization["patch_path"],
                second.root / "unauthorized-output.md",
                second.root / "unauthorized-report.json",
                acknowledge_structural=False,
                touched_ratio_threshold=None,
                block_manifest_path=second.block_manifest_path,
                integrity_issue_list_path=without_authorization["issue_path"],
            )
        self.assertIn(
            "--integrity-authorization",
            str(captured.exception.failures),
        )

    def test_patch_issue_and_scope_mutations_fail_closed(self):
        case = self._case()

        changed_patch = copy.deepcopy(case["patch"])
        changed_patch["ops"][0]["new_text"] = "An unapproved replacement."
        changed_patch_raw = _raw(changed_patch)
        with self.assertRaisesRegex(ContractError, "revision_patch_sha256"):
            validate_integrity_authorization(
                case["authorization"],
                authorization_raw=case["authorization_raw"],
                issue_list=case["issue_list"],
                issue_list_raw=case["issue_raw"],
                patch=changed_patch,
                patch_raw=changed_patch_raw,
                base_raw=case["fixture"].base_raw,
            )
        with self.assertRaisesRegex(ContractError, "input revision_patch_sha256"):
            build_integrity_authorization(
                case["choices"],
                issue_list=case["issue_list"],
                issue_list_raw=case["issue_raw"],
                patch=changed_patch,
                patch_raw=changed_patch_raw,
                base_raw=case["fixture"].base_raw,
            )

        changed_issue = copy.deepcopy(case["issue_list"])
        changed_issue["issues"][0]["description"] = "Rewritten proposal."
        changed_issue_raw = _raw(changed_issue)
        changed_patch = copy.deepcopy(case["patch"])
        changed_patch["issue_list_sha256"] = bytes_hash(changed_issue_raw)
        changed_patch_raw = _raw(changed_patch)
        with self.assertRaisesRegex(ContractError, "issue_list_sha256|revision_patch_sha256"):
            validate_integrity_authorization(
                case["authorization"],
                authorization_raw=case["authorization_raw"],
                issue_list=changed_issue,
                issue_list_raw=changed_issue_raw,
                patch=changed_patch,
                patch_raw=changed_patch_raw,
                base_raw=case["fixture"].base_raw,
            )

        widened = copy.deepcopy(case["authorization"])
        widened["author_decisions"][0]["authorized_targets"] = [
            _target(case["fixture"].claim_block_id, "replace_block")
        ]
        with self.assertRaisesRegex(ContractError, "exceeds proposed scope"):
            validate_integrity_authorization(
                widened,
                authorization_raw=_raw(widened),
                issue_list=case["issue_list"],
                issue_list_raw=case["issue_raw"],
                patch=case["patch"],
                patch_raw=case["patch_raw"],
                base_raw=case["fixture"].base_raw,
            )

        stopped = copy.deepcopy(case["authorization"])
        stopped["author_decisions"][0].update(
            {
                "decision": "stop_without_write",
                "authorized_targets": [],
                "reason": "The author stops this correction without granting write authority.",
            }
        )
        case["authorization"] = stopped
        case["authorization_raw"] = _raw(stopped)
        with self.assertRaisesRegex(ContractError, "stop_without_write"):
            self._validate(case)

    def test_author_decision_event_and_binding_mutations_fail_closed(self):
        case = self._case()
        mutations = []
        missing = copy.deepcopy(case["authorization"])
        missing["author_decisions"] = []
        mutations.append(missing)
        duplicate = copy.deepcopy(case["authorization"])
        duplicate["author_decisions"].append(
            copy.deepcopy(duplicate["author_decisions"][0])
        )
        mutations.append(duplicate)
        bad_event = copy.deepcopy(case["authorization"])
        bad_event["author_decisions"][0]["author_event_id"] = (
            "AUTHOR-EVENT-missing"
        )
        mutations.append(bad_event)
        bad_base = copy.deepcopy(case["authorization"])
        bad_base["base_draft_sha256"] = "f" * 64
        mutations.append(bad_base)
        bad_round = copy.deepcopy(case["authorization"])
        bad_round["revision_round"] = 2
        mutations.append(bad_round)

        for mutated in mutations:
            with self.subTest(mutated=mutated):
                with self.assertRaises(ContractError):
                    validate_integrity_authorization(
                        mutated,
                        authorization_raw=_raw(mutated),
                        issue_list=case["issue_list"],
                        issue_list_raw=case["issue_raw"],
                        patch=case["patch"],
                        patch_raw=case["patch_raw"],
                        base_raw=case["fixture"].base_raw,
                    )

    def test_bundle_requires_the_exact_integrity_authorization_sidecar(self):
        case = self._case()
        fixture = case["fixture"]
        output = fixture.root / "integrity-bundle-output.md"
        report = fixture.root / "integrity-bundle-report.json"
        run(
            fixture.base_path,
            case["patch_path"],
            output,
            report,
            acknowledge_structural=False,
            touched_ratio_threshold=None,
            block_manifest_path=fixture.block_manifest_path,
            integrity_issue_list_path=case["issue_path"],
            integrity_authorization_path=case["authorization_path"],
        )
        receipt_path = fixture.root / "integrity-chain-start.json"
        _write(
            receipt_path,
            {
                "schema_version": "integrity-pass-receipt/1.0",
                "receipt_id": "INTEGRITY-PASS-integrity-auth-fixture",
                "checked_draft_sha256": bytes_hash(fixture.base_raw),
                "verdict": "PASS",
                "open_issue_count": 0,
                "issued_by": "integrity_verification_agent",
            },
        )
        bundle = {
            "schema_version": "revision-evidence-bundle/1.0",
            "chain_start": {
                "first_revision_round": 1,
                "draft": _artifact(fixture.base_path, fixture.root),
                "block_manifest": _artifact(
                    fixture.block_manifest_path, fixture.root
                ),
                "integrity_pass_receipt": _artifact(receipt_path, fixture.root),
            },
            "rounds": [
                {
                    "kind": "integrity_correction",
                    "revision_round": 1,
                    "pre_round_draft": _artifact(
                        fixture.base_path, fixture.root
                    ),
                    "pre_round_block_manifest": _artifact(
                        fixture.block_manifest_path, fixture.root
                    ),
                    "issue_list": _artifact(case["issue_path"], fixture.root),
                    "integrity_authorization": _artifact(
                        case["authorization_path"], fixture.root
                    ),
                    "revision_patch": _artifact(case["patch_path"], fixture.root),
                    "apply_report": _artifact(report, fixture.root),
                    "post_round_draft": _artifact(output, fixture.root),
                }
            ],
            "final_draft": _artifact(output, fixture.root),
        }
        validate_bundle(bundle, root=fixture.root)

        missing = copy.deepcopy(bundle)
        del missing["rounds"][0]["integrity_authorization"]
        with self.assertRaises(ContractError):
            validate_bundle(missing, root=fixture.root)

        stopped = copy.deepcopy(case["authorization"])
        stopped["author_decisions"][0].update(
            {
                "decision": "stop_without_write",
                "authorized_targets": [],
                "reason": "No write authority is granted.",
            }
        )
        stopped_path = fixture.root / "stopped-integrity-authorization.json"
        _write(stopped_path, stopped)
        swapped = copy.deepcopy(bundle)
        swapped["rounds"][0]["integrity_authorization"] = _artifact(
            stopped_path, fixture.root
        )
        with self.assertRaisesRegex(ContractError, "stop_without_write"):
            validate_bundle(swapped, root=fixture.root)


class TestRevisionEvidenceBundle(unittest.TestCase):
    def _integrity_receipt(self, fixture: RevisionFixture) -> Path:
        path = fixture.root / "integrity-pass.json"
        _write(
            path,
            {
                "schema_version": "integrity-pass-receipt/1.0",
                "receipt_id": "INTEGRITY-PASS-fixture",
                "checked_draft_sha256": bytes_hash(fixture.base_raw),
                "verdict": "PASS",
                "open_issue_count": 0,
                "issued_by": "integrity_verification_agent",
            },
        )
        return path

    def test_write_round_replays_to_exact_final_draft(self):
        fixture = RevisionFixture(claim_authorized=True)
        fixture.apply()
        receipt_path = self._integrity_receipt(fixture)
        bundle = {
            "schema_version": "revision-evidence-bundle/1.0",
            "chain_start": {
                "first_revision_round": 1,
                "draft": _artifact(fixture.base_path, fixture.root),
                "block_manifest": _artifact(fixture.block_manifest_path, fixture.root),
                "integrity_pass_receipt": _artifact(receipt_path, fixture.root),
            },
            "rounds": [
                {
                    "kind": "review_roadmap",
                    "revision_round": 1,
                    "pre_round_draft": _artifact(fixture.base_path, fixture.root),
                    "pre_round_block_manifest": _artifact(
                        fixture.block_manifest_path, fixture.root
                    ),
                    "revision_roadmap": _artifact(fixture.roadmap_path, fixture.root),
                    "claim_surface_manifest": _artifact(
                        fixture.claim_surface_path, fixture.root
                    ),
                    "author_adjudication": _artifact(fixture.author_path, fixture.root),
                    "revision_patch": _artifact(fixture.patch_path, fixture.root),
                    "apply_report": _artifact(fixture.report_path, fixture.root),
                    "post_round_draft": _artifact(fixture.output_path, fixture.root),
                }
            ],
            "final_draft": _artifact(fixture.output_path, fixture.root),
        }
        validate_bundle(bundle, root=fixture.root)

        gap = copy.deepcopy(bundle)
        gap["rounds"][0]["revision_round"] = 2
        with self.assertRaisesRegex(ContractError, "continuous"):
            validate_bundle(gap, root=fixture.root)

        # Re-hashing a forged post draft and rewriting the report's declared
        # output hash is insufficient: the authorized patch itself must
        # deterministically produce the exact post bytes.
        forged_post = fixture.root / "forged-post.md"
        forged_post.write_text(
            "<!--block:B0001-->\nThe treatment is guaranteed to cure every patient.\n",
            encoding="utf-8",
        )
        forged_report = fixture.root / "forged-report.json"
        report = json.loads(fixture.report_path.read_text(encoding="utf-8"))
        report["output_draft_hash"] = base_draft_hash(forged_post.read_bytes())
        _write(forged_report, report)
        forged_bundle = copy.deepcopy(bundle)
        forged_bundle["rounds"][0]["post_round_draft"] = _artifact(
            forged_post, fixture.root
        )
        forged_bundle["rounds"][0]["apply_report"] = _artifact(
            forged_report, fixture.root
        )
        forged_bundle["final_draft"] = _artifact(forged_post, fixture.root)
        with self.assertRaisesRegex(ContractError, "deterministic patch output bytes"):
            validate_bundle(forged_bundle, root=fixture.root)

    def test_all_declined_round_has_explicit_noop_branch(self):
        fixture = RevisionFixture(all_declined=True)
        # Persist the all-declined sidecar bytes after constructor-created patch.
        fixture.author_raw = _write(fixture.author_path, fixture.author)
        receipt_path = self._integrity_receipt(fixture)
        bundle = {
            "schema_version": "revision-evidence-bundle/1.0",
            "chain_start": {
                "first_revision_round": 1,
                "draft": _artifact(fixture.base_path, fixture.root),
                "block_manifest": _artifact(fixture.block_manifest_path, fixture.root),
                "integrity_pass_receipt": _artifact(receipt_path, fixture.root),
            },
            "rounds": [
                {
                    "kind": "review_noop",
                    "revision_round": 1,
                    "pre_round_draft": _artifact(fixture.base_path, fixture.root),
                    "pre_round_block_manifest": _artifact(
                        fixture.block_manifest_path, fixture.root
                    ),
                    "revision_roadmap": _artifact(fixture.roadmap_path, fixture.root),
                    "claim_surface_manifest": _artifact(
                        fixture.claim_surface_path, fixture.root
                    ),
                    "author_adjudication": _artifact(fixture.author_path, fixture.root),
                    "post_round_draft": _artifact(fixture.base_path, fixture.root),
                }
            ],
            "final_draft": _artifact(fixture.base_path, fixture.root),
        }
        validate_bundle(bundle, root=fixture.root)
        bundle["rounds"][0]["kind"] = "review_roadmap"
        with self.assertRaises(ContractError):
            validate_bundle(bundle, root=fixture.root)

    @unittest.skipUnless(hasattr(os, "symlink"), "symlink support required")
    def test_bundle_store_rejects_symlink_artifact(self):
        fixture = RevisionFixture(all_declined=True)
        link = fixture.root / "linked-base.md"
        link.symlink_to(fixture.base_path)
        store = ArtifactStore(fixture.root)
        with self.assertRaisesRegex(ContractError, "no-symlink"):
            store.read(
                {"path": link.name, "sha256": bytes_hash(fixture.base_raw)},
                "linked base",
            )

    def test_runtime_json_loader_rejects_duplicate_keys_and_nonfinite_values(self):
        fixture = RevisionFixture(all_declined=True)
        for name, raw in (
            ("duplicate.json", b'{"schema_version":"x","schema_version":"y"}'),
            ("nonfinite.json", b'{"value":NaN}'),
        ):
            path = fixture.root / name
            path.write_bytes(raw)
            with self.assertRaisesRegex(ContractError, "duplicate|non-finite"):
                load_json_path(path, name)


if __name__ == "__main__":
    unittest.main()
