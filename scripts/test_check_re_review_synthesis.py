"""Mutation suite for scripts/check_re_review_synthesis.py (#576 Spec B §13).

Convention (Spec A §13 witness style): three hand-pinned golden scenarios
pass end-to-end; each invariant then has a fixture violating exactly it,
asserting the graded exit code and the invariant-specific message. The §10
card-normalization fixtures pin the two shipped example files line-by-line
(neither example has a DA seat, so DA vocabulary coverage rides synthetic
fixtures). The schema-parity tests run the golden artifacts through the
four shared/contracts/re_review/*.schema.json documents with jsonschema so
the checker's self-contained validators and the schema files cannot drift
apart on the positive path.
"""
from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import jsonschema
import pytest

from scripts import check_re_review_synthesis as crs
from scripts._block_parser import base_draft_hash, parse_document
from scripts.ars_anchorize_draft import build_manifest
from scripts.ars_apply_revision_patch import run as apply_revision_patch
from scripts.revision_roadmap import author_decision_digest

REPO = Path(__file__).resolve().parents[1]
SCHEMA_DIR = REPO / "shared" / "contracts" / "re_review"
EXAMPLES = REPO / "academic-paper-reviewer" / "examples"

ORIGINAL_BYTES = b"<!--block:B0001-->\nOriginal body.\n"
REVISED_BYTES = b"<!--block:B0001-->\nRevised body.\n"
PATCH_BYTES = b'{"synthetic": "patch bytes"}\n'
ORIGINAL_SHA = hashlib.sha256(ORIGINAL_BYTES).hexdigest()
REVISED_SHA = hashlib.sha256(REVISED_BYTES).hexdigest()
PATCH_SHA = hashlib.sha256(PATCH_BYTES).hexdigest()
SYNTH_SHA = hashlib.sha256(b"synthetic artifact").hexdigest()

MANUSCRIPT_ANCHOR = 'text: §3.2 "power analysis"'


def _entry(ref: str, sha: str, version_label=None, origin_date=None):
    return {
        "present": True,
        "path_or_passport_ref": ref,
        "sha256": sha,
        "version_label": version_label,
        "origin_date": origin_date,
    }


def _anchor(text=MANUSCRIPT_ANCHOR, artifact="manuscript"):
    return {"anchor": text, "anchor_artifact": artifact}


def _new_issue(n, attribution, severity, nearest=None):
    return {
        "new_issue_id": f"NEW-{n}",
        "description": f"New issue {n}",
        "location_anchor": 'text: §4 "issue span"',
        "severity": severity,
        "found_by": "R1",
        "confidence": 4,
        "competence_basis": "methods reviewer",
        "attribution": attribution,
        "attribution_evidence": "diff-supported comparison" if attribution == "regression" else "anchored in both versions",
        "nearest_roadmap_item": nearest,
        "non_match_rationale": "outside every committed criterion scope",
    }


# --- golden scenario 1: minimal Accept ----------------------------------------


def scenario_accept():
    roadmap = {
        "items": [
            {
                "id": "REV-001",
                "description": "Justify the sample size",
                "reviewer": "R1",
                "type": "Major",
                "obligation_class": "must_fix",
                "severity": "major",
                "target_section": "Methods",
                "suggested_action": "Add a power analysis",
                "consensus_level": "CONSENSUS-3",
                "verification_criteria": "A power analysis with a stated effect size appears in Methods.",
            },
            {
                "id": "REV-002",
                "description": "Clarify limitations",
                "reviewer": "EIC",
                "type": "Minor",
                "obligation_class": "should_fix",
                "severity": "minor",
                "target_section": "Discussion",
                "suggested_action": "Add a limitations paragraph",
                "consensus_level": "CONSENSUS-3",
                "verification_criteria": "A limitations paragraph names the generalizability bounds.",
            },
        ],
        "total_items": 2,
        "must_fix_count": 1,
        "editorial_decision": "Major Revision",
        "consensus_summary": "Panel agreed on the two items.",
        "dissenting_opinions": [],
    }
    letter = (
        "# Editorial Decision\n\n"
        "## Required Revisions * (Must Fix)\n\n"
        "### Required Item Details\n\n"
        "**R1: Sample size justification**\n"
        "- **Problem**: Sample size is asserted, not justified.\n"
        "- **Requirement**: Add a formal power analysis.\n"
        "- **Acceptance criteria**: A formal power analysis appears in Methods §3.2.\n\n"
        "## Closing\n"
    )
    precommitment = {
        "contract_version": "1.1",
        "round_id": "round-2",
        "input_manifest_hash": "0" * 64,
        "items": [
            {
                "item_id": "REV-001",
                "obligation_class": "must_fix",
                "inherited_criterion": {
                    "roadmap_text": "A power analysis with a stated effect size appears in Methods.",
                    "letter_text": "A formal power analysis appears in Methods §3.2.",
                    "letter_item_ref": "R1",
                },
                "operationalization": {
                    "fully_addressed": "Methods carries a power analysis naming effect size, alpha, and power.",
                    "partially_addressed": "A power analysis appears but omits the effect size.",
                    "made_worse_discriminator": "The revision removes the existing sample-size rationale.",
                },
                "expected_change_surface": "Methods §3.2",
                "equivalence_policy": "allowed",
                "source_reviewer": "R1",
                "source_reviewer_labels": ["R1"],
            },
            {
                "item_id": "REV-002",
                "obligation_class": "should_fix",
                "inherited_criterion": {
                    "roadmap_text": "A limitations paragraph names the generalizability bounds.",
                },
                "operationalization": {
                    "fully_addressed": "Discussion carries a limitations paragraph naming generalizability bounds.",
                },
                "expected_change_surface": "Discussion",
                "equivalence_policy": "allowed",
                "source_reviewer": "EIC",
                "source_reviewer_labels": ["EIC"],
            },
        ],
        "new_standards": [],
    }
    verdict_record = {
        "contract_version": "1.1",
        "round_id": "round-2",
        "precommitment_hash": "0" * 64,
        "items": [
            {
                "item_id": "REV-001",
                "verdict": "FULLY_ADDRESSED",
                "evidence_anchor": [MANUSCRIPT_ANCHOR],
                "change_summary": "Methods §3.2 gains a formal power analysis.",
                "verified_by": "R1",
                "applied_criterion": "precommitted",
            },
            {
                "item_id": "REV-002",
                "verdict": "FULLY_ADDRESSED",
                "evidence_anchor": ['text: §5 "limitations"'],
                "change_summary": "Discussion gains a limitations paragraph.",
                "verified_by": "EIC",
                "applied_criterion": "precommitted",
            },
        ],
        "new_issues": [],
        "dissents": [],
        "escalation_exceptions": [],
    }
    traceability = {
        "contract_version": "1.1",
        "round_id": "round-2",
        "revision": 1,
        "verdict_record_hash": "0" * 64,
        "rows": [
            {
                "item_id": "REV-001",
                "concern_id": "R1",
                "obligation_class": "MUST_FIX",
                "original_comment": "Sample size is asserted, not justified.",
                "authors_claim": "We added a power analysis in §3.2.",
                "revision_location": "Methods §3.2",
                "verified": "YES",
                "status": "FULLY_ADDRESSED",
                "quality_assessment": "Meets the committed pattern.",
                "final_verdict": "FULLY_ADDRESSED",
                "phase2a_verdict": "FULLY_ADDRESSED",
                "verified_by": "R1",
                "cross_model_status": "not_configured",
            },
            {
                "item_id": "REV-002",
                "concern_id": "S1",
                "obligation_class": "SHOULD_FIX",
                "original_comment": "Limitations are unclear.",
                "authors_claim": "We added a limitations paragraph.",
                "revision_location": "Discussion §5",
                "verified": "YES",
                "status": "FULLY_ADDRESSED",
                "quality_assessment": "Adequate.",
                "final_verdict": "FULLY_ADDRESSED",
                "phase2a_verdict": "FULLY_ADDRESSED",
                "verified_by": "EIC",
            },
        ],
        "adjustments": [],
        "new_issues": [],
        "post_letter_observations": [],
        "dissent_adjudications": [],
        "resolution_intents": [],
        "cross_model_resolutions": [],
        "rebuttal_adjudications": [],
        "g2d_acceptances": [],
        "pending_rebuttal_upgrades": [],
        "escalation_approvals": [],
        "reapplications": [],
        "decision_inputs": {
            "per_item": [
                {"item_id": "REV-001", "final_verdict": "FULLY_ADDRESSED", "driving_severity": "major"},
            ],
            "verdict_counts": _counts(must_fix={"FULLY_ADDRESSED": 1}, should_fix={"FULLY_ADDRESSED": 1}),
            "residual_obligation_class_counts": _magnitudes(),
            "should_fix_addressed_rate": {"numerator": 1, "denominator": 1},
            "regressions": [],
            "non_regression_new_issue_ids": [],
            "escalations": [],
            "reject_recommended": False,
            "apply_chain_witness": "pass",
        },
        "decision_state": "Accept",
    }
    return {
        "cross_model_active": False,
        "roadmap": roadmap,
        "letter": letter,
        "reports": [
            {
                "report_format_version": "1.3",
                "base_draft_hash": ORIGINAL_SHA[:12],
                "output_draft_hash": REVISED_SHA[:12],
            }
        ],
        "precommitment": precommitment,
        "verdict_record": verdict_record,
        "traceability": traceability,
        "manifest_overrides": {},
    }


def _counts(must_fix=None, should_fix=None, consider=None):
    result = {}
    for name, given in (("must_fix", must_fix), ("should_fix", should_fix), ("consider", consider)):
        bucket = {verdict: 0 for verdict in crs.VERDICTS}
        bucket.update(given or {})
        result[name] = bucket
    return result


def _magnitudes(must_fix=None, should_fix=None, consider=None):
    result = {}
    for name, given in (("must_fix", must_fix), ("should_fix", should_fix), ("consider", consider)):
        bucket = {mag: 0 for mag in crs.RESIDUAL_OBLIGATION_CLASSES}
        bucket.update(given or {})
        result[name] = bucket
    return result


# --- golden scenario 2: complex Minor Revision (cross-model active) ------------


def scenario_complex():
    roadmap = {
        "items": [
            {
                "id": "REV-001",
                "description": "Confounded treatment assignment",
                "reviewer": "R1, R3",
                "type": "Major",
                "obligation_class": "must_fix",
                "severity": "critical",
                "target_section": "Design",
                "suggested_action": "Re-run with matched controls or rebut",
                "consensus_level": "CONSENSUS-4",
                "verification_criteria": "Assignment confound is removed or rebutted with evidence.",
            },
            {
                "id": "REV-002",
                "description": "Missing robustness checks",
                "reviewer": "Peer Reviewer 2 (Domain)",
                "type": "Major",
                "obligation_class": "must_fix",
                "severity": "major",
                "target_section": "Results",
                "suggested_action": "Add robustness table",
                "consensus_level": "CONSENSUS-3",
                "verification_criteria": "A robustness table covers the two alternative specifications.",
            },
            {
                "id": "REV-003",
                "description": "Terminology drift",
                "reviewer": "EIC",
                "type": "Editorial",
                "obligation_class": "should_fix",
                "severity": "minor",
                "target_section": "Throughout",
                "suggested_action": "Unify terminology",
                "consensus_level": "CONSENSUS-3",
                "verification_criteria": "The construct is named consistently throughout.",
            },
            {
                "id": "REV-004",
                "description": "Consider a figure for the pipeline",
                "reviewer": "EIC",
                "type": "Editorial",
                "obligation_class": "consider",
                "source_kind": "editorial",
                "target_section": "Methods",
                "suggested_action": "Optional figure",
                "consensus_level": "CONSENSUS-3",
                "verification_criteria": "A pipeline figure exists or the omission is reasonable.",
            },
            {
                "id": "REV-005",
                "description": "Legacy-style item without transported severity",
                "reviewer": "R2",
                "type": "Minor",
                "obligation_class": "should_fix",
                "target_section": "Appendix",
                "suggested_action": "Tidy appendix tables",
                "consensus_level": "SPLIT",
                "verification_criteria": "Appendix tables carry readable headers.",
            },
        ],
        "total_items": 5,
        "must_fix_count": 2,
        "editorial_decision": "Major Revision",
        "consensus_summary": "Two structural concerns dominate.",
        "dissenting_opinions": ["R3 doubts the confound is fatal."],
    }
    letter = (
        "# Editorial Decision\n\n"
        "## Required Revisions * (Must Fix)\n\n"
        "### Required Item Details\n\n"
        "**R1: Confounded treatment assignment**\n"
        "- **Problem**: Assignment correlates with cohort.\n"
        "- **Requirement**: Remove or rebut the confound.\n"
        "- **Acceptance criteria**: The confound is removed by design or rebutted with matched evidence.\n\n"
        "**R2: Missing robustness checks**\n"
        "- **Problem**: Single specification only.\n"
        "- **Requirement**: Add the robustness table.\n"
        "- **Acceptance criteria**: A robustness table covers both alternative specifications.\n\n"
        "## Closing\n"
    )
    pre_items = [
        {
            "item_id": "REV-001",
            "obligation_class": "must_fix",
            "inherited_criterion": {
                "roadmap_text": "Assignment confound is removed or rebutted with evidence.",
                "letter_text": "The confound is removed by design or rebutted with matched evidence.",
                "letter_item_ref": "R1",
            },
            "operationalization": {
                "fully_addressed": "Design removes the confound or the rebuttal carries matched-cohort evidence.",
                "partially_addressed": "A partial control is added but one cohort remains unmatched.",
                "made_worse_discriminator": "The revision introduces an additional assignment confound.",
            },
            "expected_change_surface": "Design §2",
            "equivalence_policy": "allowed",
            "source_reviewer": "R1, R3",
            "source_reviewer_labels": ["R1", "R3"],
        },
        {
            "item_id": "REV-002",
            "obligation_class": "must_fix",
            "inherited_criterion": {
                "roadmap_text": "A robustness table covers the two alternative specifications.",
                "letter_text": "A robustness table covers both alternative specifications.",
                "letter_item_ref": "R2",
            },
            "operationalization": {
                "fully_addressed": "Results carries a robustness table with both alternative specifications.",
                "partially_addressed": "The table covers only one alternative specification.",
                "made_worse_discriminator": "The revision drops the primary specification results.",
            },
            "expected_change_surface": "Results §4",
            "equivalence_policy": "allowed",
            "source_reviewer": "Peer Reviewer 2 (Domain)",
            "source_reviewer_labels": ["R2"],
        },
        {
            "item_id": "REV-003",
            "obligation_class": "should_fix",
            "inherited_criterion": {"roadmap_text": "The construct is named consistently throughout."},
            "operationalization": {"fully_addressed": "One construct name is used consistently in every section."},
            "expected_change_surface": "Throughout",
            "equivalence_policy": "allowed",
            "source_reviewer": "EIC",
            "source_reviewer_labels": ["EIC"],
        },
        {
            "item_id": "REV-005",
            "obligation_class": "should_fix",
            "inherited_criterion": {"roadmap_text": "Appendix tables carry readable headers."},
            "operationalization": {"fully_addressed": "Every appendix table carries descriptive column headers."},
            "expected_change_surface": "Appendix",
            "equivalence_policy": "allowed",
            "source_reviewer": "R2",
            "source_reviewer_labels": ["R2"],
        },
    ]
    precommitment = {
        "contract_version": "1.1",
        "round_id": "round-2",
        "input_manifest_hash": "0" * 64,
        "items": pre_items,
        "new_standards": [
            {
                "new_standard_id": "NS-1",
                "item_id": "REV-001",
                "standard_text": "The design section must disclose cohort recruitment windows.",
                "why_not_in_round1": "Round 1 never named recruitment windows explicitly.",
                "classification": "escalation_requested",
            }
        ],
    }
    dissent = {
        "dissent_id": "DIS-1",
        "item_id": "REV-003",
        "criterion_hash": "0" * 64,  # recomputed at emit
        "reason_code": "criterion_ambiguous",
        "original_operationalization": "One construct name is used consistently in every section.",
        "replacement_operationalization": "One construct name is used consistently in body sections; appendix aliases allowed.",
        "evidence": 'text: §A.1 "alias table"',
        "decision_impact_note": "Slightly narrows the consistency surface.",
    }
    verdict_record = {
        "contract_version": "1.1",
        "round_id": "round-2",
        "precommitment_hash": "0" * 64,
        "items": [
            {
                "item_id": "REV-001",
                "verdict": "PARTIALLY_ADDRESSED",
                "evidence_anchor": ['text: §2 "matched controls"'],
                "change_summary": "Design adds matched controls for one cohort.",
                "residual_gap": {"text": "Second cohort remains unmatched.", "residual_obligation_class": "should_fix"},
                "verified_by": "R1",
                "applied_criterion": "precommitted",
            },
            {
                "item_id": "REV-002",
                "verdict": "NOT_ADDRESSED",
                "evidence_anchor": ['absence: Results §4 — expected robustness table; checked Results and appendix'],
                "change_summary": "No robustness table was added.",
                "verified_by": "R2",
                "applied_criterion": "precommitted",
            },
            {
                "item_id": "REV-003",
                "verdict": "FULLY_ADDRESSED",
                "evidence_anchor": ['text: §1-§5 "construct naming"'],
                "change_summary": "Terminology unified in body sections.",
                "verified_by": "EIC",
                "applied_criterion": "dissented:DIS-1",
            },
            {
                "item_id": "REV-004",
                "verdict": "FULLY_ADDRESSED",
                "evidence_anchor": ['figure: Figure 2'],
                "change_summary": "A pipeline figure was added.",
                "verified_by": "EIC",
                "applied_criterion": "not_precommitted",
            },
            {
                "item_id": "REV-005",
                "verdict": "MADE_WORSE",
                "evidence_anchor": ['table: Table A2'],
                "change_summary": "Appendix headers were replaced with opaque codes.",
                "verified_by": "R2",
                "applied_criterion": "precommitted",
            },
        ],
        "new_issues": [
            _new_issue(1, "regression", "minor"),
            _new_issue(2, "previously_missed", "major"),
            _new_issue(3, "indeterminate", "minor"),
        ],
        "dissents": [dissent],
        "escalation_exceptions": [
            {
                "exception_id": "ESC-1",
                "new_standard_ref": "NS-1",
                "escalation_class": "fatal_validity",
                "reason_code": "undisclosed-recruitment-window",
                "evidence_anchor": 'text: §2 "recruitment"',
                "why_round1_missed_it": "Round 1 focused on assignment, not recruitment.",
                "mechanical_decision_impact": "Major Revision",
                "approval_state": "pending",
            }
        ],
    }
    rebuttal_anchors = [_anchor('text: §2 "matched cohort evidence"'), _anchor('text: letter §3 "counter-evidence"', "letter")]
    adj1 = {
        "adjustment_id": "ADJ-1",
        "item_id": "REV-001",
        "from_verdict": "PARTIALLY_ADDRESSED",
        "to_verdict": "FULLY_ADDRESSED",
        "basis": "valid_rebuttal",
        "evidence_anchor": rebuttal_anchors,
        "critical_rebuttal_check": "adjudicated:RADJ-1",
        "rationale": "The rebuttal's matched-cohort evidence rebuts the residual on the merits.",
    }
    rap1_anchors = [_anchor('table: Table 4 [robustness]')]
    adj2 = {
        "adjustment_id": "ADJ-2",
        "item_id": "REV-002",
        "from_verdict": "NOT_ADDRESSED",
        "to_verdict": "FULLY_ADDRESSED",
        "basis": "cross_model_adjudication",
        "evidence_anchor": rap1_anchors,
        "rationale": "Re-application located the robustness table in the appendix.",
        "source_ref": "reapplication:RAP-1",
    }
    traceability = {
        "contract_version": "1.1",
        "round_id": "round-2",
        "revision": 2,
        "supersedes_hash": "ab" * 32,
        "verdict_record_hash": "0" * 64,
        "rows": [
            {
                "item_id": "REV-001",
                "concern_id": "R1",
                "obligation_class": "MUST_FIX",
                "original_comment": "Assignment correlates with cohort.",
                "authors_claim": "We disagree; matched evidence attached.",
                "revision_location": "Design §2",
                "verified": "YES",
                "status": "FULLY_ADDRESSED",
                "quality_assessment": "Rebuttal upheld by the adjudication pass.",
                "final_verdict": "FULLY_ADDRESSED",
                "phase2a_verdict": "PARTIALLY_ADDRESSED",
                "verified_by": "R1",
                "adjustment_id": "ADJ-1",
                "addressed_by_rebuttal": True,
                "cross_model_status": "agree",
                "cross_model_verdict": "FULLY_ADDRESSED",
            },
            {
                "item_id": "REV-002",
                "concern_id": "R2",
                "obligation_class": "MUST_FIX",
                "original_comment": "Single specification only.",
                "authors_claim": "Robustness table added (appendix).",
                "revision_location": "Appendix Table 4",
                "verified": "YES",
                "status": "FULLY_ADDRESSED",
                "quality_assessment": "Located by re-application after divergence.",
                "final_verdict": "FULLY_ADDRESSED",
                "phase2a_verdict": "NOT_ADDRESSED",
                "verified_by": "R2",
                "adjustment_id": "ADJ-2",
                "cross_model_status": "agree",
                "cross_model_verdict": "FULLY_ADDRESSED",
            },
            {
                "item_id": "REV-003",
                "concern_id": "S1",
                "obligation_class": "SHOULD_FIX",
                "original_comment": "Terminology drifts.",
                "authors_claim": "Unified throughout.",
                "revision_location": "Body sections",
                "verified": "YES",
                "status": "FULLY_ADDRESSED",
                "quality_assessment": "Consistent under the dissented criterion.",
                "final_verdict": "FULLY_ADDRESSED",
                "phase2a_verdict": "FULLY_ADDRESSED",
                "verified_by": "EIC",
            },
            {
                "item_id": "REV-004",
                "concern_id": "S2",
                "obligation_class": "CONSIDER",
                "original_comment": "A pipeline figure would help.",
                "authors_claim": "Figure 2 added.",
                "revision_location": "Methods Figure 2",
                "verified": "YES",
                "status": "FULLY_ADDRESSED",
                "quality_assessment": "Nice addition.",
                "final_verdict": "FULLY_ADDRESSED",
                "phase2a_verdict": "FULLY_ADDRESSED",
                "verified_by": "EIC",
            },
            {
                "item_id": "REV-005",
                "concern_id": "S3",
                "obligation_class": "SHOULD_FIX",
                "original_comment": "Appendix tables unreadable.",
                "authors_claim": "Headers streamlined.",
                "revision_location": "Appendix",
                "verified": "NO",
                "status": "MADE_WORSE",
                "quality_assessment": "Headers replaced with opaque codes.",
                "final_verdict": "MADE_WORSE",
                "phase2a_verdict": "MADE_WORSE",
                "verified_by": "R2",
            },
        ],
        "adjustments": [adj1, adj2],
        "new_issues": [
            _new_issue(1, "regression", "minor"),
            _new_issue(2, "previously_missed", "major"),
            _new_issue(3, "indeterminate", "minor"),
        ],
        "post_letter_observations": ["Abstract tone reads more promotional after the letter."],
        "dissent_adjudications": [],
        "resolution_intents": [{"intent_id": "INT-1", "item_id": "REV-002", "answered_by": "system"}],
        "cross_model_resolutions": [
            {
                "resolution_id": "RES-1",
                "item_id": "REV-002",
                "intent_id": "INT-1",
                "reapplication_id": "RAP-1",
                "state": "primary_revised",
                "resolved_by": "system",
                "rationale": "Re-application located the table; verdict revised.",
            }
        ],
        "rebuttal_adjudications": [
            {
                "rebuttal_adjudication_id": "RADJ-1",
                "item_id": "REV-001",
                "verdict": "upheld",
                "rationale": "Counter-evidence rebuts the original finding on the merits.",
            }
        ],
        "g2d_acceptances": [],
        "pending_rebuttal_upgrades": [
            {
                "proposal_id": "PRB-1",
                "item_id": "REV-001",
                "drafted_adjustment": {
                    "item_id": "REV-001",
                    "from_verdict": "PARTIALLY_ADDRESSED",
                    "to_verdict": "FULLY_ADDRESSED",
                    "basis": "valid_rebuttal",
                    "evidence_anchor": copy.deepcopy(rebuttal_anchors),
                    "rationale": "The rebuttal's matched-cohort evidence rebuts the residual on the merits.",
                },
                "disposition": "booked:ADJ-1",
            }
        ],
        "escalation_approvals": [
            {"exception_id": "ESC-1", "approval_state": "rejected", "approved_by": "user"}
        ],
        "reapplications": [
            {
                "reapplication_id": "RAP-1",
                "item_id": "REV-002",
                "answer_refs": ["intent:INT-1"],
                "pre_reapplication_verdict": "NOT_ADDRESSED",
                "reapplied_verdict": "FULLY_ADDRESSED",
                "evidence_anchor": copy.deepcopy(rap1_anchors),
                "rationale": "Re-application located the robustness table in the appendix.",
                "criterion_ref": "phase1:REV-002",
            }
        ],
        "decision_inputs": {
            "per_item": [
                {"item_id": "REV-001", "final_verdict": "FULLY_ADDRESSED", "driving_severity": "critical"},
                {"item_id": "REV-002", "final_verdict": "FULLY_ADDRESSED", "driving_severity": "major"},
            ],
            "verdict_counts": _counts(
                must_fix={"FULLY_ADDRESSED": 2},
                should_fix={"FULLY_ADDRESSED": 1, "MADE_WORSE": 1},
                consider={"FULLY_ADDRESSED": 1},
            ),
            "residual_obligation_class_counts": _magnitudes(),
            "should_fix_addressed_rate": {"numerator": 1, "denominator": 2},
            "regressions": [{"new_issue_id": "NEW-1", "severity": "minor"}],
            "non_regression_new_issue_ids": ["NEW-2", "NEW-3"],
            "escalations": [
                {
                    "exception_id": "ESC-1",
                    "effective_approval_state": "rejected",
                    "escalation_class": "fatal_validity",
                    "mechanical_decision_impact": "Major Revision",
                }
            ],
            "reject_recommended": False,
            "apply_chain_witness": "pass",
        },
        "decision_state": "Minor Revision",
    }
    return {
        "cross_model_active": True,
        "roadmap": roadmap,
        "letter": letter,
        "reports": [
            {
                "report_format_version": "1.3",
                "base_draft_hash": ORIGINAL_SHA[:12],
                "output_draft_hash": REVISED_SHA[:12],
            }
        ],
        "precommitment": precommitment,
        "verdict_record": verdict_record,
        "traceability": traceability,
        "manifest_overrides": {},
    }


# --- golden scenario 3: G2(d) fail-closed (deferred and accepted forms) --------


def scenario_g2d(accepted: bool):
    roadmap = {
        "items": [
            {
                "id": "REV-001",
                "description": "Anonymization claim unsupported",
                "reviewer": "R1",
                "type": "Major",
                "obligation_class": "must_fix",
                "severity": "critical",
                "target_section": "Ethics",
                "suggested_action": "Document the de-identification procedure",
                "consensus_level": "CONSENSUS-4",
                "verification_criteria": "The de-identification procedure is documented and matches the data release.",
            },
            {
                "id": "REV-002",
                "description": "Figure captions too terse",
                "reviewer": "R2",
                "type": "Minor",
                "obligation_class": "should_fix",
                "severity": "minor",
                "target_section": "Figures",
                "suggested_action": "Expand captions",
                "consensus_level": "CONSENSUS-3",
                "verification_criteria": "Every figure caption states what the figure shows.",
            },
        ],
        "total_items": 2,
        "must_fix_count": 1,
        "editorial_decision": "Major Revision",
        "consensus_summary": "Ethics documentation dominates.",
        "dissenting_opinions": [],
    }
    letter = (
        "# Editorial Decision\n\n"
        "## Required Revisions * (Must Fix)\n\n"
        "### Required Item Details\n\n"
        "**R1: Anonymization claim unsupported**\n"
        "- **Problem**: The claim is asserted without procedure.\n"
        "- **Requirement**: Document the de-identification steps.\n"
        "- **Acceptance criteria**: The de-identification procedure is documented step by step.\n\n"
        "## Closing\n"
    )
    pre_rev001 = {
        "item_id": "REV-001",
        "obligation_class": "must_fix",
        "inherited_criterion": {
            "roadmap_text": "The de-identification procedure is documented and matches the data release.",
            "letter_text": "The de-identification procedure is documented step by step.",
            "letter_item_ref": "R1",
        },
        "operationalization": {
            "fully_addressed": "Ethics section documents each de-identification step against the release.",
            "partially_addressed": "Steps are documented but not matched to the release.",
            "made_worse_discriminator": "The revision removes the existing ethics statement.",
        },
        "expected_change_surface": "Ethics §6",
        "equivalence_policy": "allowed",
        "source_reviewer": "R1",
        "source_reviewer_labels": ["R1"],
    }
    precommitment = {
        "contract_version": "1.1",
        "round_id": "round-3",
        "input_manifest_hash": "0" * 64,
        "items": [
            pre_rev001,
            {
                "item_id": "REV-002",
                "obligation_class": "should_fix",
                "inherited_criterion": {"roadmap_text": "Every figure caption states what the figure shows."},
                "operationalization": {"fully_addressed": "Each caption names the variable and the takeaway."},
                "expected_change_surface": "Figures",
                "equivalence_policy": "allowed",
                "source_reviewer": "R2",
                "source_reviewer_labels": ["R2"],
            },
        ],
        "new_standards": [],
    }
    dissent = {
        "dissent_id": "DIS-1",
        "item_id": "REV-001",
        "criterion_hash": "0" * 64,  # recomputed at emit
        "reason_code": "criterion_infeasible_as_written",
        "original_operationalization": "Ethics section documents each de-identification step against the release.",
        "replacement_operationalization": "Ethics section documents the steps; release matching deferred to the data appendix.",
        "evidence": 'text: §6 "procedure"',
        "decision_impact_note": "Release matching moves to the appendix surface.",
    }
    verdict_record = {
        "contract_version": "1.1",
        "round_id": "round-3",
        "precommitment_hash": "0" * 64,
        "items": [
            {
                "item_id": "REV-001",
                "verdict": "FULLY_ADDRESSED",
                "evidence_anchor": ['text: §6 "de-identification steps"'],
                "change_summary": "Ethics section now documents the procedure.",
                "verified_by": "R1",
                "applied_criterion": "dissented:DIS-1",
            },
            {
                "item_id": "REV-002",
                "verdict": "FULLY_ADDRESSED",
                "evidence_anchor": ['figure: Figure 1'],
                "change_summary": "Captions expanded.",
                "verified_by": "R2",
                "applied_criterion": "precommitted",
            },
        ],
        "new_issues": [],
        "dissents": [dissent],
        "escalation_exceptions": [],
    }
    reapplication = {
        "reapplication_id": "RAP-1",
        "item_id": "REV-001",
        "answer_refs": ["adjudication:DIS-1"],
        "pre_reapplication_verdict": "FULLY_ADDRESSED",
        "reapplied_verdict": "CANNOT_VERIFY",
        "cannot_verify_reason": "dispatch_failed: transport timeout",
        "rationale": "The scoped 2B' call could not be dispatched.",
        "criterion_ref": "phase1:REV-001",
    }
    traceability = {
        "contract_version": "1.1",
        "round_id": "round-3",
        "revision": 2 if accepted else 1,
        "verdict_record_hash": "0" * 64,
        "rows": [
            {
                "item_id": "REV-001",
                "concern_id": "R1",
                "obligation_class": "MUST_FIX",
                "original_comment": "The claim is asserted without procedure.",
                "authors_claim": "Procedure documented in §6.",
                "revision_location": "Ethics §6",
                "verified": "CANNOT_VERIFY" if accepted else "YES",
                "status": "CANNOT_VERIFY" if accepted else "FULLY_ADDRESSED",
                "quality_assessment": "Fail-closed under the rejected replacement criterion." if accepted else "Meets the dissented criterion.",
                "final_verdict": "CANNOT_VERIFY" if accepted else "FULLY_ADDRESSED",
                "phase2a_verdict": "FULLY_ADDRESSED",
                "verified_by": "R1",
                "cross_model_status": "unavailable",
            },
            {
                "item_id": "REV-002",
                "concern_id": "S1",
                "obligation_class": "SHOULD_FIX",
                "original_comment": "Captions too terse.",
                "authors_claim": "Expanded.",
                "revision_location": "Figures",
                "verified": "YES",
                "status": "FULLY_ADDRESSED",
                "quality_assessment": "Adequate.",
                "final_verdict": "FULLY_ADDRESSED",
                "phase2a_verdict": "FULLY_ADDRESSED",
                "verified_by": "R2",
            },
        ],
        "adjustments": [],
        "new_issues": [],
        "post_letter_observations": [],
        "dissent_adjudications": [
            {
                "dissent_id": "DIS-1",
                "adjudicator": "cross_model",
                "outcome": "original_upheld",
                "rationale": "The original criterion is applicable as written.",
            }
        ],
        "resolution_intents": [],
        "cross_model_resolutions": [],
        "rebuttal_adjudications": [],
        "g2d_acceptances": [],
        "pending_rebuttal_upgrades": [],
        "escalation_approvals": [],
        "reapplications": [reapplication],
        "decision_inputs": {
            "per_item": [
                {
                    "item_id": "REV-001",
                    "final_verdict": "CANNOT_VERIFY" if accepted else "FULLY_ADDRESSED",
                    "driving_severity": "critical",
                }
            ],
            "verdict_counts": _counts(
                must_fix={"CANNOT_VERIFY": 1} if accepted else {"FULLY_ADDRESSED": 1},
                should_fix={"FULLY_ADDRESSED": 1},
            ),
            "residual_obligation_class_counts": _magnitudes(),
            "should_fix_addressed_rate": {"numerator": 1, "denominator": 1},
            "regressions": [],
            "non_regression_new_issue_ids": [],
            "escalations": [],
            "apply_chain_witness": "pass",
        },
        "decision_state": "Major Revision" if accepted else "user_review_required",
    }
    if accepted:
        traceability["supersedes_hash"] = "cd" * 32
        traceability["g2d_acceptances"] = [
            {"acceptance_id": "ACC-1", "item_id": "REV-001", "reapplication_id": "RAP-1", "accepted_by": "user"}
        ]
        traceability["adjustments"] = [
            {
                "adjustment_id": "ADJ-1",
                "item_id": "REV-001",
                "from_verdict": "FULLY_ADDRESSED",
                "to_verdict": "CANNOT_VERIFY",
                "basis": "user_accepted_fail_closed",
                "cannot_verify_reason": "dispatch_failed: transport timeout",
                "rationale": "User accepted the fail-closed outcome at the Stage 3' checkpoint.",
                "source_ref": "acceptance:ACC-1",
            }
        ]
        traceability["rows"][0]["adjustment_id"] = "ADJ-1"
        traceability["decision_inputs"]["reject_recommended"] = False
    return {
        "cross_model_active": True,
        "roadmap": roadmap,
        "letter": letter,
        "reports": [
            {
                "report_format_version": "1.3",
                "base_draft_hash": ORIGINAL_SHA[:12],
                "output_draft_hash": REVISED_SHA[:12],
            }
        ],
        "precommitment": precommitment,
        "verdict_record": verdict_record,
        "traceability": traceability,
        "manifest_overrides": {},
    }


def scenario_g2d_retry():
    """G2(d) guided re-examination retry that SUCCEEDS: RAP-1 (CANNOT_VERIFY,
    dispatch_failed) superseded by RAP-2 with CUMULATIVE answer_refs, whose
    derived adjustment moves the row FULLY -> PARTIALLY (§6 deferral loop)."""
    s = scenario_g2d(accepted=False)
    t = s["traceability"]
    t["revision"] = 2
    t["supersedes_hash"] = "ef" * 32
    t["resolution_intents"] = [
        {
            "intent_id": "INT-1",
            "item_id": "REV-001",
            "answered_by": "user",
            "guidance_note": "re-examine against the data appendix",
        }
    ]
    rap2_anchors = [_anchor('text: §6 "procedure vs release table"')]
    residual = {"text": "Release matching still undocumented for one dataset.", "residual_obligation_class": "should_fix"}
    rationale = "Re-application under the original criterion finds partial satisfaction."
    t["reapplications"].append(
        {
            "reapplication_id": "RAP-2",
            "item_id": "REV-001",
            "answer_refs": ["adjudication:DIS-1", "intent:INT-1"],
            "supersedes_reapplication_id": "RAP-1",
            "pre_reapplication_verdict": "FULLY_ADDRESSED",
            "reapplied_verdict": "PARTIALLY_ADDRESSED",
            "evidence_anchor": copy.deepcopy(rap2_anchors),
            "residual_gap": dict(residual),
            "rationale": rationale,
            "criterion_ref": "phase1:REV-001",
        }
    )
    t["adjustments"] = [
        {
            "adjustment_id": "ADJ-1",
            "item_id": "REV-001",
            "from_verdict": "FULLY_ADDRESSED",
            "to_verdict": "PARTIALLY_ADDRESSED",
            "basis": "cross_model_adjudication",
            "evidence_anchor": copy.deepcopy(rap2_anchors),
            "residual_gap": dict(residual),
            "rationale": rationale,
            "source_ref": "reapplication:RAP-2",
        }
    ]
    t["cross_model_resolutions"] = [
        {
            "resolution_id": "RES-1",
            "item_id": "REV-001",
            "intent_id": "INT-1",
            "reapplication_id": "RAP-2",
            "state": "primary_revised",
            "resolved_by": "system",
            "rationale": "Derived mechanically from the retry re-application.",
        }
    ]
    row = t["rows"][0]
    row["final_verdict"] = "PARTIALLY_ADDRESSED"
    row["status"] = "PARTIALLY_ADDRESSED"
    row["verified"] = "PARTIAL"
    row["adjustment_id"] = "ADJ-1"
    di = t["decision_inputs"]
    di["per_item"] = [
        {
            "item_id": "REV-001",
            "final_verdict": "PARTIALLY_ADDRESSED",
            "driving_severity": "critical",
            "residual_obligation_class": "should_fix",
        }
    ]
    di["verdict_counts"] = _counts(
        must_fix={"PARTIALLY_ADDRESSED": 1}, should_fix={"FULLY_ADDRESSED": 1}
    )
    di["residual_obligation_class_counts"] = _magnitudes(must_fix={"should_fix": 1})
    di["reject_recommended"] = False
    t["decision_state"] = "Minor Revision"
    return s


# --- emit + run ----------------------------------------------------------------


def emit(tmp_path: Path, scenario: dict, *, resync: bool = True):
    """Write every fixture file, resync hashes, and return the checker argv."""
    scenario = copy.deepcopy(scenario)

    original_path = tmp_path / "manuscript.v1.md"
    revised_path = tmp_path / "manuscript.v2.md"
    original_path.write_bytes(ORIGINAL_BYTES)
    parsed_original = parse_document(ORIGINAL_BYTES.decode("utf-8"))
    block_manifest = build_manifest(ORIGINAL_BYTES, parsed_original)
    block_manifest_path = tmp_path / "block-manifest.json"
    block_manifest_path.write_text(
        json.dumps(block_manifest, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    block_manifest_sha = hashlib.sha256(block_manifest_path.read_bytes()).hexdigest()

    # Scenario builders focus on #576 arithmetic. Upgrade their roadmap rows
    # to the closed #670 core before writing the exact artifact consumed by
    # current re-review and its replayed evidence bundle.
    roadmap_payload = scenario["roadmap"]
    roadmap_payload.pop("must_fix_count", None)
    roadmap_payload.update(
        {
            "schema_version": "revision-roadmap/1.0",
            "revision_round": 1,
            "base_draft_sha256": ORIGINAL_SHA,
            "block_manifest_sha256": block_manifest_sha,
        }
    )
    counts = {"must_fix": 0, "should_fix": 0, "consider": 0}
    for ordinal, item in enumerate(roadmap_payload["items"], start=1):
        item.pop("type", None)
        counts[item["obligation_class"]] += 1
        item["source_refs"] = [
            {
                "seat": "R1",
                "channel": "finding" if "severity" in item else item.get("source_kind", "editorial"),
                "ordinal": ordinal,
                "subclaim_ordinal": 0,
            }
        ]
        if "severity" in item:
            item.pop("source_kind", None)
            item.setdefault(
                "evidence_anchor",
                {
                    "anchor_type": "text",
                    "locator": "B0001",
                    "quote": "Original body.",
                },
            )
            item.setdefault("confidence", 4)
            item.setdefault("competence_basis", "Current re-review fixture basis.")
        else:
            item.setdefault("source_kind", "editorial")
        item.setdefault("cost_scope", {"kind": "sentence", "locator": "B0001"})
        item.setdefault(
            "consequence_if_unaddressed",
            {
                "code": "acceptance_criterion_unmet",
                "target": {"kind": "manuscript", "locator": "B0001"},
            },
        )
        item["proposed_targets"] = [
            {"block_id": "B0001", "allowed_operations": ["replace_block"]}
        ]
    roadmap_payload["obligation_counts"] = counts
    roadmap_path = tmp_path / "roadmap.json"
    roadmap_path.write_text(
        json.dumps(roadmap_payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    roadmap_sha = hashlib.sha256(roadmap_path.read_bytes()).hexdigest()

    claim_surface = {
        "schema_version": "claim-surface-manifest/1.0",
        "revision_round": 1,
        "roadmap_sha256": roadmap_sha,
        "base_draft_sha256": ORIGINAL_SHA,
        "claim_intent_sources": [],
        "surfaces": [],
    }
    claim_surface_path = tmp_path / "claim-surfaces.json"
    claim_surface_path.write_text(
        json.dumps(claim_surface, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    claim_surface_sha = hashlib.sha256(claim_surface_path.read_bytes()).hexdigest()

    event_id = "AUTHOR-EVENT-re-review-fixture"
    author_records = []
    author_overrides = scenario.get("author_triage_overrides", {})
    for item in roadmap_payload["items"]:
        record = {
            "item_id": item["id"],
            "author_event_id": event_id,
            "author_triage": "will_address",
            "authorized_targets": [
                {
                    "block_id": "B0001",
                    "allowed_operations": ["replace_block"],
                }
            ],
            "claim_strength_authorizations": [],
        }
        record.update(copy.deepcopy(author_overrides.get(item["id"], {})))
        author_records.append(record)
    author_adjudication = {
        "schema_version": "author-adjudication/1.0",
        "revision_round": 1,
        "roadmap_sha256": roadmap_sha,
        "base_draft_sha256": ORIGINAL_SHA,
        "claim_surface_manifest_sha256": claim_surface_sha,
        "adjudication_status": "complete",
        "author_events": [
            {
                "event_id": event_id,
                "source": "explicit_session_user_message",
                "actor_role": "author",
                "input_sha256": hashlib.sha256(b"explicit fixture author triage").hexdigest(),
            }
        ],
        "display_order": {
            "mode": "source_traceability",
            "item_ids": [item["id"] for item in roadmap_payload["items"]],
            "author_event_id": event_id,
        },
        "author_adjudications": author_records,
        "collateral_authorizations": [],
    }
    accepted_ids = [
        record["item_id"]
        for record in author_records
        if record["author_triage"] == "will_address"
    ]
    if accepted_ids:
        for index, record in enumerate(author_records, start=1):
            if record["author_triage"] in ("wont_address", "not_on_point"):
                author_adjudication["collateral_authorizations"].append(
                    {
                        "authorization_id": f"COLLATERAL-AUTH-fixture-{index}",
                        "author_event_id": event_id,
                        "authorizing_item_id": accepted_ids[0],
                        "constrained_item_id": record["item_id"],
                        "block_id": "B0001",
                        "operation": "replace_block",
                        "reason": "Explicit fixture authority for the shared test block.",
                    }
                )
    author_adjudication["display_order"].update(
        copy.deepcopy(scenario.get("author_display_override", {}))
    )
    author_path = tmp_path / "author-adjudication.json"
    author_path.write_text(
        json.dumps(author_adjudication, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    author_by_item = {record["item_id"]: record for record in author_records}
    for row in scenario["traceability"]["rows"]:
        author = author_by_item[row["item_id"]]
        for field in (
            "author_triage",
            "authorized_targets",
            "claim_strength_authorizations",
        ):
            row.setdefault(field, copy.deepcopy(author[field]))
        if "author_reason" in author:
            row.setdefault("author_reason", author["author_reason"])

    argv = []
    letter_sha = None
    if scenario["letter"] is not None:
        letter_path = tmp_path / "letter.md"
        letter_path.write_text(scenario["letter"], encoding="utf-8")
        letter_sha = hashlib.sha256(letter_path.read_bytes()).hexdigest()
        argv += ["--letter", str(letter_path)]

    patch_path = tmp_path / "patch.json"
    canonical_report_path = tmp_path / "canonical-apply-report.json"
    will_address_ids = [
        record["item_id"]
        for record in author_records
        if record["author_triage"] == "will_address"
    ]
    canonical_report = None
    patch_sha = None
    if scenario["reports"]:
        assert will_address_ids, "write-round fixture needs at least one will_address item"
        patch = {
            "patch_format_version": "1.1",
            "authorization_context": "review_roadmap",
            "revision_round": 1,
            "base_draft_hash": base_draft_hash(ORIGINAL_BYTES),
            "roadmap_sha256": roadmap_sha,
            "author_adjudication_sha256": hashlib.sha256(author_path.read_bytes()).hexdigest(),
            "author_decision_digest": author_decision_digest(author_adjudication),
            "claim_surface_manifest_sha256": claim_surface_sha,
            "ops": [
                {
                    "op": "replace_block",
                    "block_id": "B0001",
                    "old_hash": parsed_original.block_by_id()["B0001"].norm_hash,
                    "new_text": "Revised body.",
                    "roadmap_item_ids": will_address_ids,
                    "claim_strength_changes": [],
                    "collateral_authorization_ids": [
                        row["authorization_id"]
                        for row in author_adjudication["collateral_authorizations"]
                    ],
                }
            ],
            "emitted_by": "draft_writer_agent",
        }
        patch_path.write_text(
            json.dumps(patch, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )
        patch_sha = hashlib.sha256(patch_path.read_bytes()).hexdigest()
        canonical_report = apply_revision_patch(
            original_path,
            patch_path,
            revised_path,
            canonical_report_path,
            acknowledge_structural=False,
            touched_ratio_threshold=None,
            block_manifest_path=block_manifest_path,
            roadmap_path=roadmap_path,
            author_adjudication_path=author_path,
            claim_surface_manifest_path=claim_surface_path,
            artifact_root=tmp_path,
        )
        assert revised_path.read_bytes() == REVISED_BYTES
    else:
        revised_path.write_bytes(ORIGINAL_BYTES)

    report_paths = []
    report_shas = []
    for i, payload in enumerate(scenario["reports"]):
        payload = {**(canonical_report or {}), **dict(payload)}
        try:
            format_12_plus = tuple(int(p) for p in payload["report_format_version"].split(".")) >= (1, 2)
        except ValueError:
            format_12_plus = False
        if format_12_plus:
            payload.setdefault("patch_digest", patch_sha)
        payload.setdefault(
            "authorization_witness",
            {
                "status": "pass",
                "unregistered_claim_drift_review_required": True,
            },
        )
        path = tmp_path / f"apply-report-{i}.json"
        path.write_text(json.dumps(payload, indent=2), encoding="utf-8")
        report_paths.append(path)
        report_shas.append(hashlib.sha256(path.read_bytes()).hexdigest())
        argv += ["--apply-report", str(path)]

    receipt_path = tmp_path / "integrity-pass.json"
    receipt_path.write_text(
        json.dumps(
            {
                "schema_version": "integrity-pass-receipt/1.0",
                "receipt_id": "INTEGRITY-PASS-re-review-fixture",
                "checked_draft_sha256": ORIGINAL_SHA,
                "verdict": "PASS",
                "open_issue_count": 0,
                "issued_by": "integrity_verification_agent",
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )

    def artifact(path: Path) -> dict:
        return {
            "path": path.relative_to(tmp_path).as_posix(),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }

    if scenario["reports"]:
        bundle_round = {
            "kind": "review_roadmap",
            "revision_round": 1,
            "pre_round_draft": artifact(original_path),
            "pre_round_block_manifest": artifact(block_manifest_path),
            "revision_roadmap": artifact(roadmap_path),
            "claim_surface_manifest": artifact(claim_surface_path),
            "author_adjudication": artifact(author_path),
            "revision_patch": artifact(patch_path),
            "apply_report": artifact(report_paths[0]),
            "post_round_draft": artifact(revised_path),
        }
    else:
        bundle_round = {
            "kind": "review_noop",
            "revision_round": 1,
            "pre_round_draft": artifact(original_path),
            "pre_round_block_manifest": artifact(block_manifest_path),
            "revision_roadmap": artifact(roadmap_path),
            "claim_surface_manifest": artifact(claim_surface_path),
            "author_adjudication": artifact(author_path),
            "post_round_draft": artifact(revised_path),
        }
    bundle = {
        "schema_version": "revision-evidence-bundle/1.0",
        "chain_start": {
            "first_revision_round": 1,
            "draft": artifact(original_path),
            "block_manifest": artifact(block_manifest_path),
            "integrity_pass_receipt": artifact(receipt_path),
        },
        "rounds": [bundle_round],
        "final_draft": artifact(revised_path),
    }
    bundle_path = tmp_path / "revision-evidence-bundle.json"
    bundle_path.write_text(
        json.dumps(bundle, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    # Invalid top-level sidecar mutations are written only after the valid
    # apply/bundle fixture exists, so the checker—not fixture construction—
    # owns the expected failure.
    author_adjudication.update(copy.deepcopy(scenario.get("author_top_overrides", {})))
    author_path.write_text(
        json.dumps(author_adjudication, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    author_sha = hashlib.sha256(author_path.read_bytes()).hexdigest()
    bundle_sha = hashlib.sha256(bundle_path.read_bytes()).hexdigest()
    revised_sha = hashlib.sha256(revised_path.read_bytes()).hexdigest()

    manifest = {
        "contract_version": "1.1",
        "round_id": scenario["precommitment"]["round_id"],
        "cross_model_active": scenario["cross_model_active"],
        "artifacts": {
            "original_manuscript": _entry("path:manuscript.v1.md", ORIGINAL_SHA),
            "revised_manuscript": _entry("path:manuscript.v2.md", revised_sha),
            "revision_roadmap": _entry("path:roadmap.json", roadmap_sha),
            "author_adjudication": _entry(
                "path:author-adjudication.json", author_sha
            ),
            "revision_evidence_bundle": _entry(
                "path:revision-evidence-bundle.json", bundle_sha
            ),
            "editorial_decision_letter": (
                _entry("path:letter.md", letter_sha) if letter_sha else {"present": False}
            ),
            "response_to_reviewers": _entry("path:response.md", SYNTH_SHA),
            "revision_patches": {
                "present": True,
                "items": [
                    {"path_or_passport_ref": "path:patch.json", "sha256": patch_sha,
                     "version_label": None, "origin_date": None}
                ],
            } if scenario["reports"] else {"present": False},
            "apply_reports": {
                "present": True,
                "items": [
                    {"path_or_passport_ref": f"path:apply-report-{i}.json", "sha256": sha,
                     "version_label": None, "origin_date": None}
                    for i, sha in enumerate(report_shas)
                ],
            } if scenario["reports"] else {"present": False},
            "round1_findings": _entry("path:findings.md", SYNTH_SHA),
            "round1_config_cards": _entry("path:cards.md", SYNTH_SHA),
        },
    }
    for key, value in scenario["manifest_overrides"].items():
        manifest["artifacts"][key] = value
    if manifest["artifacts"]["revision_patches"]["present"]:
        for item in manifest["artifacts"]["revision_patches"]["items"]:
            if item["sha256"] == PATCH_SHA:
                item["sha256"] = patch_sha

    if resync:
        pre_by_item = {rec["item_id"]: rec for rec in scenario["precommitment"]["items"]}
        for dissent in scenario["verdict_record"]["dissents"]:
            target = pre_by_item.get(dissent["item_id"])
            if target is not None and dissent["criterion_hash"] == "0" * 64:
                dissent["criterion_hash"] = crs.canonical_hash(target)
        scenario["precommitment"]["input_manifest_hash"] = crs.canonical_hash(manifest)
        scenario["verdict_record"]["precommitment_hash"] = crs.canonical_hash(scenario["precommitment"])
        scenario["traceability"]["verdict_record_hash"] = crs.canonical_hash(scenario["verdict_record"])

    manifest_path = tmp_path / "manifest.json"
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    for name, artifact in (
        ("precommitment", scenario["precommitment"]),
        ("verdict_record", scenario["verdict_record"]),
        ("traceability", scenario["traceability"]),
    ):
        (tmp_path / f"{name}.json").write_text(json.dumps(artifact, ensure_ascii=False, indent=2), encoding="utf-8")

    argv = [
        "--manifest", str(manifest_path),
        "--precommitment", str(tmp_path / "precommitment.json"),
        "--verdict-record", str(tmp_path / "verdict_record.json"),
        "--traceability", str(tmp_path / "traceability.json"),
        "--roadmap", str(roadmap_path),
        "--author-adjudication", str(author_path),
        "--revision-evidence-bundle", str(bundle_path),
        "--revision-evidence-root", str(tmp_path),
    ] + argv
    return argv, manifest


def run_checker(tmp_path, scenario, capsys, *, resync=True):
    argv, _manifest = emit(tmp_path, scenario, resync=resync)
    code = crs.run(argv)
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def assert_exit2(tmp_path, scenario, capsys, reason, needle=None):
    code, out, _err = run_checker(tmp_path, scenario, capsys)
    assert code == crs.EXIT_INVALID, out
    assert f"[RE-REVIEW-ABORT: {reason}]" in out
    if needle:
        assert needle in out


def assert_mismatch(tmp_path, scenario, capsys, needle):
    code, out, _err = run_checker(tmp_path, scenario, capsys)
    assert code == crs.EXIT_SYNTHESIS, out
    assert "[RE-REVIEW-ABORT: synthesis_mismatch]" in out
    assert needle in out, out


# --- golden scenarios pass -----------------------------------------------------


def test_golden_accept_passes(tmp_path, capsys):
    code, out, err = run_checker(tmp_path, scenario_accept(), capsys)
    assert code == crs.EXIT_PASS, out
    assert "re-review synthesis ok" in out
    assert "'Accept'" in out
    assert err == ""


def test_golden_complex_minor_passes(tmp_path, capsys):
    code, out, err = run_checker(tmp_path, scenario_complex(), capsys)
    assert code == crs.EXIT_PASS, out
    assert "'Minor Revision'" in out
    # the regression advisory names NEW-1's nearest item only when non-null;
    # NEW-1 carries null here, so no advisory fires
    assert "ADVISORY" not in err


def test_golden_g2d_deferred_passes(tmp_path, capsys):
    code, out, _err = run_checker(tmp_path, scenario_g2d(accepted=False), capsys)
    assert code == crs.EXIT_PASS, out
    assert "'user_review_required'" in out


def test_golden_g2d_accepted_passes(tmp_path, capsys):
    code, out, _err = run_checker(tmp_path, scenario_g2d(accepted=True), capsys)
    assert code == crs.EXIT_PASS, out
    assert "'Major Revision'" in out


def test_golden_artifacts_validate_against_shipped_schemas(tmp_path, capsys):
    for i, scenario in enumerate(
        (scenario_accept(), scenario_complex(), scenario_g2d(True), scenario_g2d(False), scenario_g2d_retry())
    ):
        subdir = tmp_path / f"s{i}"
        subdir.mkdir()
        argv, manifest = emit(subdir, scenario)
        files = dict(zip(argv[::2], argv[1::2]))
        for schema_name, path_key in (
            ("precommitment", "--precommitment"),
            ("verdict_record", "--verdict-record"),
            ("traceability", "--traceability"),
        ):
            schema = json.loads((SCHEMA_DIR / f"{schema_name}.schema.json").read_text(encoding="utf-8"))
            payload = json.loads(Path(files[path_key]).read_text(encoding="utf-8"))
            jsonschema.Draft202012Validator(schema).validate(payload)
        manifest_schema = json.loads((SCHEMA_DIR / "input_manifest.schema.json").read_text(encoding="utf-8"))
        jsonschema.Draft202012Validator(manifest_schema).validate(manifest)


# --- exit-2 class: manifest layer ---------------------------------------------


def test_missing_hard_required_artifact_is_manifest_incomplete(tmp_path, capsys):
    s = scenario_accept()
    s["manifest_overrides"]["revised_manuscript"] = {"present": False}
    assert_exit2(tmp_path, s, capsys, "manifest_incomplete", "hard-required artifact revised_manuscript")


def test_apply_reports_without_patches_is_manifest_incomplete(tmp_path, capsys):
    s = scenario_accept()
    s["manifest_overrides"]["revision_patches"] = {"present": False}
    assert_exit2(tmp_path, s, capsys, "manifest_incomplete", "must travel together")


def test_patches_without_reports_is_manifest_incomplete_even_for_noop_bundle(
    tmp_path, capsys
):
    s = scenario_accept()
    s["reports"] = []
    s["author_triage_overrides"] = {
        item["id"]: {
            "author_triage": "wont_address",
            "author_reason": "The author explicitly declines this fixture item.",
            "authorized_targets": [],
            "claim_strength_authorizations": [],
        }
        for item in s["roadmap"]["items"]
    }
    s["traceability"]["decision_inputs"][
        "apply_chain_witness"
    ] = "not_run_no_reports"
    s["manifest_overrides"]["revision_patches"] = {
        "present": True,
        "items": [
            {
                "path_or_passport_ref": "path:patch.json",
                "sha256": SYNTH_SHA,
                "version_label": None,
                "origin_date": None,
            }
        ],
    }
    assert_exit2(tmp_path, s, capsys, "manifest_incomplete", "must travel together")


def test_array_length_mismatch_is_manifest_incomplete(tmp_path, capsys):
    s = scenario_accept()
    s["manifest_overrides"]["revision_patches"] = {
        "present": True,
        "items": [
            {"path_or_passport_ref": "path:patch.json", "sha256": PATCH_SHA, "version_label": None, "origin_date": None},
            {"path_or_passport_ref": "path:patch2.json", "sha256": SYNTH_SHA, "version_label": None, "origin_date": None},
        ],
    }
    assert_exit2(tmp_path, s, capsys, "manifest_incomplete", "length mismatch")


def test_passport_ref_with_null_freshness_is_manifest_incomplete(tmp_path, capsys):
    s = scenario_accept()
    s["manifest_overrides"]["round1_findings"] = _entry("passport:findings-ref", SYNTH_SHA)
    assert_exit2(tmp_path, s, capsys, "manifest_incomplete", "passport:-tagged")


def test_absent_artifact_with_fields_is_manifest_incomplete(tmp_path, capsys):
    s = scenario_accept()
    s["manifest_overrides"]["round1_findings"] = {"present": False, "sha256": SYNTH_SHA}
    assert_exit2(tmp_path, s, capsys, "manifest_incomplete", "NO ref, hash, or freshness fields")


def test_roadmap_older_than_letter_fails_closed(tmp_path, capsys):
    s = scenario_accept()
    seed = tmp_path / "seed"
    seed.mkdir()
    emit(seed, s)
    # rebuild with passport-tagged freshness on roadmap + letter
    roadmap_sha = hashlib.sha256((seed / "roadmap.json").read_bytes()).hexdigest()
    letter_sha = hashlib.sha256((seed / "letter.md").read_bytes()).hexdigest()
    s["manifest_overrides"]["revision_roadmap"] = _entry("passport:roadmap", roadmap_sha, "v1", "2026-07-01")
    s["manifest_overrides"]["editorial_decision_letter"] = _entry("passport:letter", letter_sha, "v1", "2026-07-15")
    assert_exit2(tmp_path, s, capsys, "manifest_hash_mismatch", "freshness")


def test_roadmap_file_hash_mismatch(tmp_path, capsys):
    s = scenario_accept()
    s["manifest_overrides"]["revision_roadmap"] = _entry("path:roadmap.json", SYNTH_SHA)
    assert_exit2(tmp_path, s, capsys, "manifest_hash_mismatch", "revision_roadmap file")


def test_patch_digest_mismatch_is_content_binding_failure(tmp_path, capsys):
    s = scenario_accept()
    s["reports"][0]["patch_digest"] = SYNTH_SHA
    assert_exit2(tmp_path, s, capsys, "manifest_hash_mismatch", "patch_digest")


def test_broken_apply_chain_last_link(tmp_path, capsys):
    s = scenario_accept()
    s["reports"][0]["output_draft_hash"] = "deadbeef0123"
    assert_exit2(tmp_path, s, capsys, "manifest_hash_mismatch", "revised_manuscript hash prefix")


def test_broken_apply_chain_first_link(tmp_path, capsys):
    s = scenario_accept()
    s["reports"][0]["base_draft_hash"] = "deadbeef0123"
    assert_exit2(tmp_path, s, capsys, "manifest_hash_mismatch", "original_manuscript hash prefix")


def test_broken_apply_chain_inner_link(tmp_path, capsys):
    s = scenario_accept()
    s["reports"] = [
        {"report_format_version": "1.3", "base_draft_hash": ORIGINAL_SHA[:12], "output_draft_hash": "aaaaaaaaaaaa"},
        {"report_format_version": "1.3", "base_draft_hash": "bbbbbbbbbbbb", "output_draft_hash": REVISED_SHA[:12]},
    ]
    s["manifest_overrides"]["revision_patches"] = {
        "present": True,
        "items": [
            {"path_or_passport_ref": "path:patch.json", "sha256": PATCH_SHA, "version_label": None, "origin_date": None},
            {"path_or_passport_ref": "path:patch2.json", "sha256": PATCH_SHA, "version_label": None, "origin_date": None},
        ],
    }
    assert_exit2(tmp_path, s, capsys, "manifest_hash_mismatch", "output_draft_hash")


def test_bundle_binding_requires_exact_ordered_write_pair_projection():
    roadmap_sha = "1" * 64
    author_sha = "2" * 64
    original_sha = "3" * 64
    final_sha = "4" * 64
    first_patch = "5" * 64
    first_report = "6" * 64
    second_patch = "7" * 64
    second_report = "8" * 64
    bundle = {
        "final_draft": {"sha256": final_sha},
        "rounds": [
            {
                "kind": "review_roadmap",
                "pre_round_draft": {"sha256": original_sha},
                "revision_roadmap": {"sha256": roadmap_sha},
                "author_adjudication": {"sha256": author_sha},
                "revision_patch": {"sha256": first_patch},
                "apply_report": {"sha256": first_report},
            },
            {
                "kind": "integrity_correction",
                "revision_patch": {"sha256": second_patch},
                "apply_report": {"sha256": second_report},
            },
        ],
    }
    manifest = {
        "artifacts": {
            "revised_manuscript": {"sha256": final_sha},
            "revision_roadmap": {"sha256": roadmap_sha},
            "author_adjudication": {"sha256": author_sha},
            "original_manuscript": {"present": True, "sha256": original_sha},
            "revision_patches": {
                "present": True,
                "items": [{"sha256": first_patch}, {"sha256": second_patch}],
            },
            "apply_reports": {
                "present": True,
                "items": [{"sha256": first_report}, {"sha256": second_report}],
            },
        }
    }
    crs.validate_revision_bundle_binding(bundle, manifest)

    for name, mutated in (
        (
            "omitted",
            [
                {"sha256": first_patch},
            ],
        ),
        (
            "reordered",
            [
                {"sha256": second_patch},
                {"sha256": first_patch},
            ],
        ),
        (
            "substituted",
            [
                {"sha256": first_patch},
                {"sha256": "9" * 64},
            ],
        ),
    ):
        with pytest.raises(crs.ManifestError, match="ordered write patch/report pairs"):
            changed = copy.deepcopy(manifest)
            changed["artifacts"]["revision_patches"]["items"] = mutated
            if name == "omitted":
                changed["artifacts"]["apply_reports"]["items"] = [
                    {"sha256": first_report}
                ]
            crs.validate_revision_bundle_binding(bundle, changed)


def test_format_12_report_without_patch_digest_is_incomplete(tmp_path, capsys):
    s = scenario_accept()
    s["reports"][0]["patch_digest"] = None  # blocks the setdefault fill
    argv, _m = emit(tmp_path, s)
    payload = json.loads((tmp_path / "apply-report-0.json").read_text())
    del payload["patch_digest"]
    (tmp_path / "apply-report-0.json").write_text(json.dumps(payload, indent=2))
    # re-sync the manifest hash for the rewritten report so ONLY the missing
    # digest fires (not the file-hash binding)
    manifest = json.loads((tmp_path / "manifest.json").read_text())
    manifest["artifacts"]["apply_reports"]["items"][0]["sha256"] = hashlib.sha256(
        (tmp_path / "apply-report-0.json").read_bytes()
    ).hexdigest()
    (tmp_path / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2))
    pre = json.loads((tmp_path / "precommitment.json").read_text())
    pre["input_manifest_hash"] = crs.canonical_hash(manifest)
    (tmp_path / "precommitment.json").write_text(json.dumps(pre, ensure_ascii=False, indent=2))
    vr = json.loads((tmp_path / "verdict_record.json").read_text())
    vr["precommitment_hash"] = crs.canonical_hash(pre)
    (tmp_path / "verdict_record.json").write_text(json.dumps(vr, ensure_ascii=False, indent=2))
    tr = json.loads((tmp_path / "traceability.json").read_text())
    tr["verdict_record_hash"] = crs.canonical_hash(vr)
    (tmp_path / "traceability.json").write_text(json.dumps(tr, ensure_ascii=False, indent=2))
    code = crs.run(argv)
    out = capsys.readouterr().out
    assert code == crs.EXIT_INVALID
    assert "[RE-REVIEW-ABORT: manifest_incomplete]" in out
    assert "requires patch_digest" in out


def test_legacy_report_is_rejected_by_current_contract(tmp_path, capsys):
    s = scenario_accept()
    s["reports"][0] = {
        "report_format_version": "1.1",
        "base_draft_hash": ORIGINAL_SHA[:12],
        "output_draft_hash": REVISED_SHA[:12],
    }
    code, out, _err = run_checker(tmp_path, s, capsys)
    assert code == crs.EXIT_INVALID, out
    assert "current contract requires report format 1.3" in out
    assert "archived loader" in out


@pytest.mark.parametrize(
    "artifact_name",
    ("manifest", "precommitment", "verdict_record", "traceability"),
)
def test_current_checker_rejects_every_mixed_legacy_contract_version(
    tmp_path, capsys, artifact_name
):
    argv, _manifest = emit(tmp_path, scenario_accept())
    path = tmp_path / f"{artifact_name}.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    payload["contract_version"] = "1.0"
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    code = crs.run(argv)
    out = capsys.readouterr().out
    assert code == crs.EXIT_INVALID, out
    assert "1.1" in out


@pytest.mark.parametrize("artifact_name", ("author_adjudication", "revision_evidence_bundle"))
def test_current_manifest_hard_requires_author_and_bundle_artifacts(
    tmp_path, capsys, artifact_name
):
    scenario = scenario_accept()
    scenario["manifest_overrides"][artifact_name] = {"present": False}
    assert_exit2(
        tmp_path,
        scenario,
        capsys,
        "manifest_incomplete",
        f"hard-required artifact {artifact_name} absent",
    )


def test_current_checker_requires_existing_bundle_file(tmp_path, capsys):
    argv, _manifest = emit(tmp_path, scenario_accept())
    (tmp_path / "revision-evidence-bundle.json").unlink()
    code = crs.run(argv)
    out = capsys.readouterr().out
    assert code == crs.EXIT_INVALID, out
    assert "[RE-REVIEW-ABORT: manifest_incomplete]" in out
    assert "revision_evidence_bundle file" in out


def test_current_checker_rejects_bundle_file_hash_drift(tmp_path, capsys):
    argv, _manifest = emit(tmp_path, scenario_accept())
    bundle_path = tmp_path / "revision-evidence-bundle.json"
    bundle_path.write_bytes(bundle_path.read_bytes() + b"\n")
    code = crs.run(argv)
    out = capsys.readouterr().out
    assert code == crs.EXIT_INVALID, out
    assert "[RE-REVIEW-ABORT: manifest_hash_mismatch]" in out
    assert "revision_evidence_bundle file" in out


def test_author_sidecar_raw_roadmap_binding_rejects_substitution(tmp_path, capsys):
    scenario = scenario_accept()
    scenario["author_top_overrides"] = {"roadmap_sha256": "f" * 64}
    assert_exit2(
        tmp_path,
        scenario,
        capsys,
        "manifest_hash_mismatch",
        "does not match the exact roadmap bytes",
    )


def test_traceability_author_triage_must_equal_bound_sidecar(tmp_path, capsys):
    scenario = scenario_accept()
    scenario["traceability"]["rows"][0].update(
        {
            "author_triage": "wont_address",
            "author_reason": "A forged downstream decline.",
            "authorized_targets": [],
            "claim_strength_authorizations": [],
        }
    )
    assert_mismatch(
        tmp_path,
        scenario,
        capsys,
        "author_triage is not an exact copy",
    )


def test_declined_author_reason_roundtrips_into_traceability(tmp_path, capsys):
    scenario = scenario_accept()
    scenario["author_triage_overrides"] = {
        "REV-002": {
            "author_triage": "not_on_point",
            "author_reason": "The author explicitly states that this request is out of scope.",
            "authorized_targets": [],
            "claim_strength_authorizations": [],
        }
    }
    code, out, _err = run_checker(tmp_path, scenario, capsys)
    assert code == crs.EXIT_PASS, out


def test_user_display_order_cannot_change_roadmap_or_letter_transport_order(
    tmp_path, capsys
):
    scenario = scenario_accept()
    scenario["author_display_override"] = {
        "mode": "user_selected",
        "item_ids": ["REV-002", "REV-001"],
    }
    code, out, _err = run_checker(tmp_path, scenario, capsys)
    assert code == crs.EXIT_PASS, out
    # The letter still joins R1 to the first must_fix item in immutable
    # roadmap order; the author's view permutation is presentation-only.
    assert "'Accept'" in out


def test_no_reports_is_not_run_no_reports_witness(tmp_path, capsys):
    s = scenario_accept()
    s["reports"] = []
    s["author_triage_overrides"] = {
        item["id"]: {
            "author_triage": "wont_address",
            "author_reason": "The author explicitly declines this fixture item.",
            "authorized_targets": [],
            "claim_strength_authorizations": [],
        }
        for item in s["roadmap"]["items"]
    }
    s["traceability"]["decision_inputs"]["apply_chain_witness"] = "not_run_no_reports"
    code, out, _err = run_checker(tmp_path, s, capsys)
    assert code == crs.EXIT_PASS, out
    assert "'not_run_no_reports'" in out


def test_absent_original_is_manifest_incomplete_in_current_contract(tmp_path, capsys):
    s = scenario_accept()
    s["manifest_overrides"]["original_manuscript"] = {"present": False}
    assert_exit2(
        tmp_path,
        s,
        capsys,
        "manifest_incomplete",
        "hard-required artifact original_manuscript",
    )


def test_letter_declared_but_not_provided_is_incomplete(tmp_path, capsys):
    s = scenario_accept()
    argv, _m = emit(tmp_path, s)
    idx = argv.index("--letter")
    del argv[idx:idx + 2]
    code = crs.run(argv)
    out = capsys.readouterr().out
    assert code == crs.EXIT_INVALID
    assert "--letter is required" in out


# --- exit-2 class: hash chain --------------------------------------------------


def test_stale_input_manifest_hash(tmp_path, capsys):
    s = scenario_accept()
    argv, _m = emit(tmp_path, s)
    pre = json.loads((tmp_path / "precommitment.json").read_text())
    pre["input_manifest_hash"] = "f" * 64
    (tmp_path / "precommitment.json").write_text(json.dumps(pre, ensure_ascii=False))
    code = crs.run(argv)
    out = capsys.readouterr().out
    assert code == crs.EXIT_INVALID
    assert "input_manifest_hash does not recompute" in out


def test_stale_precommitment_hash(tmp_path, capsys):
    s = scenario_accept()
    argv, _m = emit(tmp_path, s)
    vr = json.loads((tmp_path / "verdict_record.json").read_text())
    vr["precommitment_hash"] = "f" * 64
    (tmp_path / "verdict_record.json").write_text(json.dumps(vr, ensure_ascii=False))
    code = crs.run(argv)
    out = capsys.readouterr().out
    assert code == crs.EXIT_INVALID
    assert "precommitment_hash does not recompute" in out


def test_stale_verdict_record_hash(tmp_path, capsys):
    s = scenario_accept()
    argv, _m = emit(tmp_path, s)
    tr = json.loads((tmp_path / "traceability.json").read_text())
    tr["verdict_record_hash"] = "f" * 64
    (tmp_path / "traceability.json").write_text(json.dumps(tr, ensure_ascii=False))
    code = crs.run(argv)
    out = capsys.readouterr().out
    assert code == crs.EXIT_INVALID
    assert "verdict_record_hash does not recompute" in out


# --- exit-2 class: phase-artifact schemas -------------------------------------


def test_invalid_precommitment_is_phase1_lint(tmp_path, capsys):
    s = scenario_accept()
    s["precommitment"]["items"][1]["operationalization"]["made_worse_discriminator"] = "forbidden on P2"
    assert_exit2(tmp_path, s, capsys, "phase1_lint_failed", "should_fix lighter form")


def test_invalid_verdict_record_is_phase2a_lint(tmp_path, capsys):
    s = scenario_accept()
    s["verdict_record"]["items"][0]["verdict"] = "PARTIALLY_ADDRESSED"  # no residual_gap
    assert_exit2(tmp_path, s, capsys, "phase2a_lint_failed", "requires residual_gap")


def test_invalid_traceability_is_phase2b_lint(tmp_path, capsys):
    s = scenario_accept()
    s["traceability"]["decision_state"] = "aborted"  # abort_reason missing
    assert_exit2(tmp_path, s, capsys, "phase2b_lint_failed", "requires abort_reason")


def test_letter_fields_on_p2_item_is_phase1_lint(tmp_path, capsys):
    s = scenario_accept()
    s["precommitment"]["items"][1]["inherited_criterion"]["letter_text"] = "no"
    s["precommitment"]["items"][1]["inherited_criterion"]["letter_item_ref"] = "R2"
    assert_exit2(tmp_path, s, capsys, "phase1_lint_failed", "ONLY on must_fix")


def test_letter_field_biconditional_is_phase1_lint(tmp_path, capsys):
    s = scenario_accept()
    del s["precommitment"]["items"][0]["inherited_criterion"]["letter_item_ref"]
    assert_exit2(tmp_path, s, capsys, "phase1_lint_failed", "biconditional")


def test_supersedes_hash_biconditional_is_phase2b_lint(tmp_path, capsys):
    s = scenario_accept()
    s["traceability"]["supersedes_hash"] = "ab" * 32  # revision 1
    assert_exit2(tmp_path, s, capsys, "phase2b_lint_failed", "revision 1")


def test_cannot_verify_adjustment_off_basis_is_phase2b_lint(tmp_path, capsys):
    s = scenario_g2d(accepted=True)
    s["traceability"]["adjustments"][0]["basis"] = "scope_correction"
    assert_exit2(tmp_path, s, capsys, "phase2b_lint_failed", "ONLY basis")


def test_source_ref_forbidden_off_basis_is_phase2b_lint(tmp_path, capsys):
    s = scenario_complex()
    s["traceability"]["adjustments"][0]["source_ref"] = "reapplication:RAP-1"
    assert_exit2(tmp_path, s, capsys, "phase2b_lint_failed", "FORBIDDEN")


def test_manuscript_only_anchor_rule_is_phase2b_lint(tmp_path, capsys):
    s = scenario_complex()
    adj = s["traceability"]["adjustments"][1]
    adj["basis"] = "scope_correction"
    adj.pop("source_ref")
    adj["evidence_anchor"] = [_anchor('text: letter "claim"', "letter")]
    assert_exit2(tmp_path, s, capsys, "phase2b_lint_failed", "manuscript-side anchors")


def test_p1_row_without_cross_model_status_is_phase2b_lint(tmp_path, capsys):
    s = scenario_accept()
    del s["traceability"]["rows"][0]["cross_model_status"]
    assert_exit2(tmp_path, s, capsys, "phase2b_lint_failed", "MUST_FIX rows always carry")


def test_p2_row_with_cross_model_field_is_phase2b_lint(tmp_path, capsys):
    s = scenario_accept()
    s["traceability"]["rows"][1]["cross_model_status"] = "not_configured"
    assert_exit2(tmp_path, s, capsys, "phase2b_lint_failed", "neither cross-model field")


def test_system_intent_with_guidance_note_is_phase2b_lint(tmp_path, capsys):
    s = scenario_complex()
    s["traceability"]["resolution_intents"][0]["guidance_note"] = "look in the appendix"
    assert_exit2(tmp_path, s, capsys, "phase2b_lint_failed", "guidance_note exists only on user intents")


def test_user_resolution_hand_set_state_is_phase2b_lint(tmp_path, capsys):
    s = scenario_complex()
    s["traceability"]["cross_model_resolutions"][0]["resolved_by"] = "user"
    s["traceability"]["cross_model_resolutions"][0]["state"] = "primary_revised"
    assert_exit2(tmp_path, s, capsys, "phase2b_lint_failed", "never hand-sets a verdict")


# --- exit-1 class: criterion inheritance binding (§4/§5.1) ---------------------


def test_roadmap_text_must_match_verbatim(tmp_path, capsys):
    s = scenario_accept()
    s["precommitment"]["items"][0]["inherited_criterion"]["roadmap_text"] = "A softer paraphrase."
    assert_mismatch(tmp_path, s, capsys, "roadmap_text does not match the roadmap verbatim")


def test_letter_text_must_match_byte_for_byte(tmp_path, capsys):
    s = scenario_accept()
    s["precommitment"]["items"][0]["inherited_criterion"]["letter_text"] = "A formal power analysis appears somewhere."
    assert_mismatch(tmp_path, s, capsys, "letter_text does not match")


def test_letter_item_ref_is_derived_never_chosen(tmp_path, capsys):
    s = scenario_complex()
    item0 = s["precommitment"]["items"][0]["inherited_criterion"]
    item0["letter_item_ref"] = "R2"
    item0["letter_text"] = "A robustness table covers both alternative specifications."
    assert_mismatch(tmp_path, s, capsys, "derived ordinal")


def test_letter_ordinal_gap_degrades_whole_letter_layer(tmp_path, capsys):
    s = scenario_complex()
    s["letter"] = s["letter"].replace("**R2: Missing robustness checks**", "**R3: Missing robustness checks**")
    code, out, err = run_checker(tmp_path, s, capsys)
    assert code == crs.EXIT_SYNTHESIS
    assert "[CRITERIA-LAYER-ABSENT: letter/roadmap ordinal mismatch]" in err
    assert "letter fields must be absent" in out


def test_letter_fields_absent_when_layer_degraded_passes(tmp_path, capsys):
    s = scenario_complex()
    s["letter"] = s["letter"].replace("**R2: Missing robustness checks**", "**R3: Missing robustness checks**")
    for rec in s["precommitment"]["items"]:
        rec["inherited_criterion"].pop("letter_text", None)
        rec["inherited_criterion"].pop("letter_item_ref", None)
    code, out, err = run_checker(tmp_path, s, capsys)
    assert code == crs.EXIT_PASS, out
    assert "[CRITERIA-LAYER-ABSENT: letter/roadmap ordinal mismatch]" in err


def test_letter_block_present_requires_letter_fields(tmp_path, capsys):
    s = scenario_accept()
    crit = s["precommitment"]["items"][0]["inherited_criterion"]
    del crit["letter_text"]
    del crit["letter_item_ref"]
    assert_mismatch(tmp_path, s, capsys, "letter_text/letter_item_ref REQUIRED")


def test_precommitment_coverage_missing_p2(tmp_path, capsys):
    s = scenario_accept()
    del s["precommitment"]["items"][1]
    assert_mismatch(tmp_path, s, capsys, "precommitment coverage")


def test_precommitment_record_for_p3_item_is_extra(tmp_path, capsys):
    s = scenario_complex()
    s["precommitment"]["items"].append({
        "item_id": "REV-004",
        "obligation_class": "should_fix",
        "inherited_criterion": {"roadmap_text": "A pipeline figure exists or the omission is reasonable."},
        "operationalization": {"fully_addressed": "A pipeline figure exists."},
        "expected_change_surface": "Methods",
        "equivalence_policy": "allowed",
        "source_reviewer": "EIC",
        "source_reviewer_labels": ["EIC"],
    })
    assert_mismatch(tmp_path, s, capsys, "precommitment coverage")


def test_source_reviewer_labels_must_recompute(tmp_path, capsys):
    s = scenario_accept()
    s["precommitment"]["items"][0]["source_reviewer_labels"] = ["R2"]
    assert_mismatch(tmp_path, s, capsys, "§10 normalization")


def test_round_id_equality(tmp_path, capsys):
    s = scenario_accept()
    s["verdict_record"]["round_id"] = "round-999"
    assert_mismatch(tmp_path, s, capsys, "round_id != manifest.round_id")


# --- exit-1 class: Phase 2A invariants ----------------------------------------


def test_verdict_record_coverage_all_priorities(tmp_path, capsys):
    s = scenario_complex()
    del s["verdict_record"]["items"][3]  # REV-004 (consider)
    assert_mismatch(tmp_path, s, capsys, "verdict_record coverage")


def test_p3_item_must_be_not_precommitted(tmp_path, capsys):
    s = scenario_complex()
    s["verdict_record"]["items"][3]["applied_criterion"] = "precommitted"
    assert_mismatch(tmp_path, s, capsys, "consider items carry applied_criterion not_precommitted")


def test_p1_item_must_not_be_not_precommitted(tmp_path, capsys):
    s = scenario_accept()
    s["verdict_record"]["items"][0]["applied_criterion"] = "not_precommitted"
    assert_mismatch(tmp_path, s, capsys, "valid ONLY for consider items")


def test_dissent_ref_must_resolve_on_same_item(tmp_path, capsys):
    s = scenario_accept()
    s["verdict_record"]["items"][0]["applied_criterion"] = "dissented:DIS-9"
    assert_mismatch(tmp_path, s, capsys, "does not resolve to a dissent on this item")


def test_dissent_criterion_hash_recomputes(tmp_path, capsys):
    s = scenario_complex()
    s["verdict_record"]["dissents"][0]["criterion_hash"] = "e" * 64
    assert_mismatch(tmp_path, s, capsys, "criterion_hash does not recompute")


def test_new_standard_ref_must_resolve(tmp_path, capsys):
    s = scenario_complex()
    s["verdict_record"]["escalation_exceptions"][0]["new_standard_ref"] = "NS-9"
    assert_mismatch(tmp_path, s, capsys, "new_standard_ref 'NS-9' does not resolve")


def test_new_standard_ref_target_must_be_escalation_requested(tmp_path, capsys):
    s = scenario_complex()
    s["precommitment"]["new_standards"][0]["classification"] = "advisory"
    assert_mismatch(tmp_path, s, capsys, "not escalation_requested")


# --- exit-1 class: freeze witness + rows ---------------------------------------


def test_no_original_manuscript_is_rejected_at_manifest_gate(tmp_path, capsys):
    s = scenario_complex()
    s["manifest_overrides"]["original_manuscript"] = {"present": False}
    assert_exit2(
        tmp_path,
        s,
        capsys,
        "manifest_incomplete",
        "hard-required artifact original_manuscript",
    )


def test_new_issue_freeze_is_whole_record(tmp_path, capsys):
    s = scenario_complex()
    s["traceability"]["new_issues"][0]["found_by"] = "R2"  # edit one frozen field
    assert_mismatch(tmp_path, s, capsys, "WHOLE-RECORD byte-identical")


def test_new_issue_reclassification_breaks_freeze(tmp_path, capsys):
    s = scenario_complex()
    s["traceability"]["new_issues"][1]["attribution"] = "regression"
    assert_mismatch(tmp_path, s, capsys, "WHOLE-RECORD byte-identical")


def test_row_coverage_every_item(tmp_path, capsys):
    s = scenario_complex()
    del s["traceability"]["rows"][3]
    assert_mismatch(tmp_path, s, capsys, "row coverage")


def test_row_phase2a_verdict_binds_to_committed_record(tmp_path, capsys):
    s = scenario_accept()
    s["traceability"]["rows"][1]["phase2a_verdict"] = "NOT_ADDRESSED"
    assert_mismatch(tmp_path, s, capsys, "phase2a_verdict != committed")


def test_row_verified_by_copied_from_2a(tmp_path, capsys):
    s = scenario_accept()
    s["traceability"]["rows"][0]["verified_by"] = "EIC"
    assert_mismatch(tmp_path, s, capsys, "verified_by not copied")


def test_status_maps_1_to_1_from_final_verdict(tmp_path, capsys):
    s = scenario_accept()
    s["traceability"]["rows"][0]["status"] = "PARTIALLY_ADDRESSED"
    assert_mismatch(tmp_path, s, capsys, "status must map 1:1")


def test_verified_follows_mechanical_map(tmp_path, capsys):
    s = scenario_accept()
    s["traceability"]["rows"][0]["verified"] = "PARTIAL"
    assert_mismatch(tmp_path, s, capsys, "mechanical 5->4 map")


def test_cross_model_status_rederives_per_emission(tmp_path, capsys):
    s = scenario_complex()
    s["traceability"]["rows"][0]["cross_model_status"] = "diverges"  # cmv == final => agree
    assert_mismatch(tmp_path, s, capsys, "per-emission derivation")


def test_row_obligation_class_binds_to_roadmap(tmp_path, capsys):
    s = scenario_accept()
    s["traceability"]["rows"][1]["obligation_class"] = "CONSIDER"
    assert_mismatch(tmp_path, s, capsys, "does not match the roadmap")


# --- exit-1 class: adjustment chains -------------------------------------------


def test_g1_silent_verdict_change_is_criteria_drift(tmp_path, capsys):
    s = scenario_accept()
    row = s["traceability"]["rows"][1]
    row["final_verdict"] = "NOT_ADDRESSED"
    row["status"] = "NOT_ADDRESSED"
    row["verified"] = "NO"
    # keep DecisionInputs consistent so the G1 message is the load-bearing one
    di = s["traceability"]["decision_inputs"]
    di["verdict_counts"]["should_fix"] = {v: 0 for v in crs.VERDICTS}
    di["verdict_counts"]["should_fix"]["NOT_ADDRESSED"] = 1
    di["should_fix_addressed_rate"] = {"numerator": 0, "denominator": 1}
    assert_mismatch(tmp_path, s, capsys, "[RE-REVIEW-ABORT: criteria_drift]")


def test_chain_head_starts_at_phase2a(tmp_path, capsys):
    s = scenario_complex()
    s["traceability"]["adjustments"][0]["from_verdict"] = "NOT_ADDRESSED"
    assert_mismatch(tmp_path, s, capsys, "head from_verdict != phase2a_verdict")


def test_chain_tail_ends_at_final(tmp_path, capsys):
    s = scenario_g2d(accepted=True)
    s["traceability"]["rows"][0]["final_verdict"] = "NOT_ADDRESSED"
    s["traceability"]["rows"][0]["status"] = "NOT_ADDRESSED"
    s["traceability"]["rows"][0]["verified"] = "NO"
    assert_mismatch(tmp_path, s, capsys, "tail to_verdict != final_verdict")


def test_adjustment_id_names_latest_record(tmp_path, capsys):
    s = scenario_complex()
    s["traceability"]["rows"][0]["adjustment_id"] = "ADJ-2"
    assert_mismatch(tmp_path, s, capsys, "adjustment_id must name the chain's LATEST record")


def test_adjustment_id_present_iff_chain_exists(tmp_path, capsys):
    s = scenario_accept()
    s["traceability"]["rows"][0]["adjustment_id"] = "ADJ-1"
    assert_mismatch(tmp_path, s, capsys, "adjustment_id present with no adjustment chain")


def test_head_to_tail_join(tmp_path, capsys):
    s = scenario_complex()
    adj3 = {
        "adjustment_id": "ADJ-3",
        "item_id": "REV-001",
        "from_verdict": "NOT_ADDRESSED",  # breaks the join (predecessor to = FULLY)
        "to_verdict": "FULLY_ADDRESSED",
        "basis": "scope_correction",
        "evidence_anchor": [_anchor()],
        "rationale": "The letter reveals the 2A reading misread the target.",
        "supersedes_adjustment_id": "ADJ-1",
    }
    s["traceability"]["adjustments"].append(adj3)
    s["traceability"]["rows"][0]["adjustment_id"] = "ADJ-3"
    assert_mismatch(tmp_path, s, capsys, "head-to-tail join")


def test_addressed_by_rebuttal_marker_tracks_chain_tail(tmp_path, capsys):
    s = scenario_complex()
    del s["traceability"]["rows"][0]["addressed_by_rebuttal"]
    assert_mismatch(tmp_path, s, capsys, "addressed_by_rebuttal")


# --- exit-1 class: critical-rebuttal machinery ---------------------------------


def test_critical_rebuttal_check_presence_biconditional(tmp_path, capsys):
    s = scenario_complex()
    del s["traceability"]["adjustments"][0]["critical_rebuttal_check"]
    assert_mismatch(tmp_path, s, capsys, "critical_rebuttal_check present iff")


def test_single_family_disclosed_invalid_when_active(tmp_path, capsys):
    s = scenario_complex()
    s["traceability"]["adjustments"][0]["critical_rebuttal_check"] = "single_family_disclosed"
    s["traceability"]["pending_rebuttal_upgrades"][0]["disposition"] = "booked_single_family:ADJ-1"
    assert_mismatch(tmp_path, s, capsys, "single_family_disclosed is invalid")


def test_adjudicated_ref_must_resolve_upheld(tmp_path, capsys):
    s = scenario_complex()
    s["traceability"]["rebuttal_adjudications"][0]["verdict"] = "challenged"
    assert_mismatch(tmp_path, s, capsys, "upheld RebuttalAdjudication")


def test_booked_proposal_content_equality(tmp_path, capsys):
    s = scenario_complex()
    s["traceability"]["pending_rebuttal_upgrades"][0]["drafted_adjustment"]["rationale"] = "A different drafted rationale."
    assert_mismatch(tmp_path, s, capsys, "content-equal the drafted body")


def test_critical_rebuttal_adjustment_requires_booked_proposal(tmp_path, capsys):
    s = scenario_complex()
    s["traceability"]["pending_rebuttal_upgrades"] = []
    assert_mismatch(tmp_path, s, capsys, "traces to exactly one booked* PendingRebuttalUpgrade")


def test_challenged_disposition_requires_challenged_adjudication(tmp_path, capsys):
    s = scenario_complex()
    # keep RADJ-1 upheld (referenced by ADJ-1) and add a challenged proposal
    # pointing at it: the disposition/verdict cross-check must fire
    s["traceability"]["pending_rebuttal_upgrades"].append({
        "proposal_id": "PRB-2",
        "item_id": "REV-001",
        "drafted_adjustment": copy.deepcopy(s["traceability"]["pending_rebuttal_upgrades"][0]["drafted_adjustment"]),
        "disposition": "challenged:RADJ-1",
    })
    assert_mismatch(tmp_path, s, capsys, "must reference a challenged adjudication")


def test_rebuttal_adjudication_requires_active_cross_model(tmp_path, capsys):
    s = scenario_complex()
    s["cross_model_active"] = False
    # strip the other active-implying surfaces so THIS invariant is the target
    for row in s["traceability"]["rows"]:
        if "cross_model_status" in row and row["cross_model_status"] != "not_configured":
            row["cross_model_status"] = "not_configured"
            row.pop("cross_model_verdict", None)
    assert_mismatch(tmp_path, s, capsys, "exists only under active cross-model")


def test_agree_status_requires_active_cross_model(tmp_path, capsys):
    s = scenario_accept()
    s["traceability"]["rows"][0]["cross_model_status"] = "agree"
    s["traceability"]["rows"][0]["cross_model_verdict"] = "FULLY_ADDRESSED"
    assert_mismatch(tmp_path, s, capsys, "implies an active configuration")


# --- exit-1 class: deferral-loop referential integrity -------------------------


def test_answer_ref_must_resolve(tmp_path, capsys):
    s = scenario_complex()
    s["traceability"]["reapplications"][0]["answer_refs"] = ["intent:INT-9"]
    assert_mismatch(tmp_path, s, capsys, "does not resolve")


def test_intent_appears_in_exactly_one_current_record(tmp_path, capsys):
    s = scenario_complex()
    s["traceability"]["reapplications"] = []
    s["traceability"]["cross_model_resolutions"] = []
    s["traceability"]["adjustments"] = [s["traceability"]["adjustments"][0]]  # drop ADJ-2
    row = s["traceability"]["rows"][1]
    row["final_verdict"] = "NOT_ADDRESSED"
    row["status"] = "NOT_ADDRESSED"
    row["verified"] = "NO"
    row.pop("adjustment_id")
    row["cross_model_status"] = "diverges"
    di = s["traceability"]["decision_inputs"]
    di["per_item"][1]["final_verdict"] = "NOT_ADDRESSED"
    di["verdict_counts"]["must_fix"] = {v: 0 for v in crs.VERDICTS}
    di["verdict_counts"]["must_fix"].update({"FULLY_ADDRESSED": 1, "NOT_ADDRESSED": 1})
    di.pop("reject_recommended")
    s["traceability"]["decision_state"] = "user_review_required"
    assert_mismatch(tmp_path, s, capsys, "exactly one CURRENT reapplication's answer_refs")


def test_original_upheld_adjudication_must_be_discharged(tmp_path, capsys):
    s = scenario_g2d(accepted=False)
    s["traceability"]["reapplications"] = []
    assert_mismatch(tmp_path, s, capsys, "original_upheld must appear in exactly one CURRENT")


def test_criterion_ref_effective_rule_adjudication_mandated(tmp_path, capsys):
    s = scenario_g2d(accepted=False)
    s["traceability"]["reapplications"][0]["criterion_ref"] = "dissent:DIS-1"
    assert_mismatch(tmp_path, s, capsys, "effective-criterion rule")


def test_verdict_changing_reapplication_requires_derived_adjustment(tmp_path, capsys):
    s = scenario_complex()
    s["traceability"]["adjustments"] = [s["traceability"]["adjustments"][0]]  # drop ADJ-2
    row = s["traceability"]["rows"][1]
    row.pop("adjustment_id")
    assert_mismatch(tmp_path, s, capsys, "requires exactly one derived adjustment")


def test_derived_adjustment_binds_to_recorded_pre_value(tmp_path, capsys):
    s = scenario_complex()
    s["traceability"]["reapplications"][0]["pre_reapplication_verdict"] = "PARTIALLY_ADDRESSED"
    assert_mismatch(tmp_path, s, capsys, "RECORDED pre-value")


def test_derived_adjustment_copies_mechanically(tmp_path, capsys):
    s = scenario_complex()
    s["traceability"]["adjustments"][1]["rationale"] = "An embellished rationale."
    assert_mismatch(tmp_path, s, capsys, "MECHANICALLY COPIED")


def test_cannot_verify_reapplication_appends_nothing(tmp_path, capsys):
    s = scenario_complex()
    rap = s["traceability"]["reapplications"][0]
    rap["reapplied_verdict"] = "CANNOT_VERIFY"
    rap["cannot_verify_reason"] = "evidence surface inaccessible"
    rap.pop("evidence_anchor")
    # ADJ-2 still claims to derive from RAP-1: the CANNOT_VERIFY append fires
    assert_mismatch(tmp_path, s, capsys, "CANNOT_VERIFY appends NOTHING mechanically")


def test_intent_answered_derived_state_requires_system_resolution(tmp_path, capsys):
    s = scenario_complex()
    s["traceability"]["cross_model_resolutions"] = []
    assert_mismatch(tmp_path, s, capsys, "mandates a mechanically-created")


def test_system_resolution_state_follows_derivation(tmp_path, capsys):
    s = scenario_complex()
    s["traceability"]["cross_model_resolutions"][0]["state"] = "primary_upheld"
    assert_mismatch(tmp_path, s, capsys, "§9 derivation")


def test_user_resolution_requires_cannot_verify_reapplication(tmp_path, capsys):
    s = scenario_complex()
    s["traceability"]["cross_model_resolutions"][0]["resolved_by"] = "user"
    s["traceability"]["cross_model_resolutions"][0]["state"] = "primary_upheld"
    assert_mismatch(tmp_path, s, capsys, "requires a CANNOT_VERIFY reapplication")


# --- exit-1 class: G2(d) acceptances -------------------------------------------


def test_acceptance_reapplication_must_be_cannot_verify(tmp_path, capsys):
    s = scenario_g2d(accepted=True)
    rap = s["traceability"]["reapplications"][0]
    rap["reapplied_verdict"] = "FULLY_ADDRESSED"
    rap.pop("cannot_verify_reason")
    rap["evidence_anchor"] = [_anchor()]
    assert_mismatch(tmp_path, s, capsys, "must be CANNOT_VERIFY")


def test_accepted_item_final_verdict_is_cannot_verify(tmp_path, capsys):
    s = scenario_g2d(accepted=True)
    row = s["traceability"]["rows"][0]
    row["final_verdict"] = "FULLY_ADDRESSED"
    row["status"] = "FULLY_ADDRESSED"
    row["verified"] = "YES"
    assert_mismatch(tmp_path, s, capsys, "final_verdict must be CANNOT_VERIFY")


def test_fail_closed_adjustment_copies_reason(tmp_path, capsys):
    s = scenario_g2d(accepted=True)
    s["traceability"]["adjustments"][0]["cannot_verify_reason"] = "a different reason"
    assert_mismatch(tmp_path, s, capsys, "copied from the accepted reapplication")


# --- exit-1 class: escalation approvals ----------------------------------------


def test_approval_must_reference_existing_exception(tmp_path, capsys):
    s = scenario_complex()
    s["traceability"]["escalation_approvals"].append(
        {"exception_id": "ESC-9", "approval_state": "approved", "approved_by": "user"}
    )
    assert_mismatch(tmp_path, s, capsys, "no such exception record")


# --- exit-1 class: DecisionInputs equality -------------------------------------


def test_per_item_operands_recompute(tmp_path, capsys):
    s = scenario_accept()
    s["traceability"]["decision_inputs"]["per_item"][0]["driving_severity"] = None
    assert_mismatch(tmp_path, s, capsys, "per_item does not equal")


def test_verdict_counts_recompute(tmp_path, capsys):
    s = scenario_accept()
    s["traceability"]["decision_inputs"]["verdict_counts"]["must_fix"]["FULLY_ADDRESSED"] = 2
    assert_mismatch(tmp_path, s, capsys, "verdict_counts does not recompute")


def test_residual_obligation_class_counts_recompute(tmp_path, capsys):
    s = scenario_accept()
    s["traceability"]["decision_inputs"]["residual_obligation_class_counts"]["must_fix"]["must_fix"] = 1
    assert_mismatch(tmp_path, s, capsys, "residual_obligation_class_counts does not recompute")


def test_p2_rate_recomputes_over_final_verdicts(tmp_path, capsys):
    s = scenario_complex()
    s["traceability"]["decision_inputs"]["should_fix_addressed_rate"]["numerator"] = 2
    assert_mismatch(tmp_path, s, capsys, "should_fix_addressed_rate does not recompute")


def test_regression_list_recomputes(tmp_path, capsys):
    s = scenario_complex()
    s["traceability"]["decision_inputs"]["regressions"] = []
    assert_mismatch(tmp_path, s, capsys, "regression-attributed frozen new issues")


def test_non_regression_ids_recompute(tmp_path, capsys):
    s = scenario_complex()
    s["traceability"]["decision_inputs"]["non_regression_new_issue_ids"] = ["NEW-2"]
    assert_mismatch(tmp_path, s, capsys, "previously_missed/indeterminate ids")


def test_escalation_summary_joins_from_approvals(tmp_path, capsys):
    s = scenario_complex()
    s["traceability"]["decision_inputs"]["escalations"][0]["effective_approval_state"] = "approved"
    assert_mismatch(tmp_path, s, capsys, "joined exception/approval summary")


def test_recorded_witness_must_match_recomputed(tmp_path, capsys):
    s = scenario_accept()
    s["traceability"]["decision_inputs"]["apply_chain_witness"] = "fail"
    assert_mismatch(tmp_path, s, capsys, "apply_chain_witness")


# --- exit-1 class: gates + decision equality -----------------------------------


def test_g2b_diverges_without_covering_resolution_defers(tmp_path, capsys):
    s = scenario_complex()
    # the mandated re-application concluded CANNOT_VERIFY: row stays NOT_ADDRESSED,
    # no adjustment, no resolution -> G2(b) pending; emitting Major anyway must fail
    rap = s["traceability"]["reapplications"][0]
    rap["reapplied_verdict"] = "CANNOT_VERIFY"
    rap["cannot_verify_reason"] = "evidence surface inaccessible"
    rap.pop("evidence_anchor")
    s["traceability"]["cross_model_resolutions"] = []
    s["traceability"]["adjustments"] = [s["traceability"]["adjustments"][0]]
    row = s["traceability"]["rows"][1]
    row["final_verdict"] = "NOT_ADDRESSED"
    row["status"] = "NOT_ADDRESSED"
    row["verified"] = "NO"
    row.pop("adjustment_id")
    row["cross_model_status"] = "diverges"
    di = s["traceability"]["decision_inputs"]
    di["per_item"][1]["final_verdict"] = "NOT_ADDRESSED"
    di["verdict_counts"]["must_fix"] = {v: 0 for v in crs.VERDICTS}
    di["verdict_counts"]["must_fix"].update({"FULLY_ADDRESSED": 1, "NOT_ADDRESSED": 1})
    di.pop("reject_recommended")
    s["traceability"]["decision_state"] = "Major Revision"
    assert_mismatch(tmp_path, s, capsys, "G2(b)")


def test_g2c_pending_exception_defers(tmp_path, capsys):
    s = scenario_complex()
    s["traceability"]["escalation_approvals"] = []
    s["traceability"]["decision_inputs"]["escalations"][0]["effective_approval_state"] = "pending"
    assert_mismatch(tmp_path, s, capsys, "G2(c)")


def test_g2d_fail_closed_without_acceptance_defers(tmp_path, capsys):
    s = scenario_g2d(accepted=False)
    s["traceability"]["decision_state"] = "Major Revision"
    assert_mismatch(tmp_path, s, capsys, "G2(d)")


def test_deferred_state_without_pending_is_biconditional_violation(tmp_path, capsys):
    s = scenario_accept()
    s["traceability"]["decision_state"] = "user_review_required"
    s["traceability"]["decision_inputs"].pop("reject_recommended")
    assert_mismatch(tmp_path, s, capsys, "the G2 biconditional runs both directions")


def test_reject_recommended_absent_on_gated_emission(tmp_path, capsys):
    s = scenario_complex()
    s["traceability"]["escalation_approvals"] = []
    s["traceability"]["decision_inputs"]["escalations"][0]["effective_approval_state"] = "pending"
    s["traceability"]["decision_state"] = "user_review_required"
    assert_mismatch(tmp_path, s, capsys, "must be ABSENT on a gated emission")


def test_reject_recommended_present_on_non_gated_emission(tmp_path, capsys):
    s = scenario_accept()
    s["traceability"]["decision_inputs"].pop("reject_recommended")
    assert_mismatch(tmp_path, s, capsys, "must be PRESENT on a non-gated emission")


def test_decision_state_equals_recomputed_derivation(tmp_path, capsys):
    s = scenario_complex()
    s["traceability"]["decision_state"] = "Accept"
    assert_mismatch(tmp_path, s, capsys, "Steps 2-3 recomputed from the raw records")


def test_reject_recommended_equals_recomputed(tmp_path, capsys):
    s = scenario_accept()
    s["traceability"]["decision_inputs"]["reject_recommended"] = True
    assert_mismatch(tmp_path, s, capsys, "reject_recommended True != recomputed False")


def test_goalpost_previously_missed_cannot_enter_decision(tmp_path, capsys):
    # moving NEW-2 (previously_missed, major) into the regression operands
    # would escalate B3; the checker recomputes both lists from the frozen
    # attribution and rejects the promoted copy
    s = scenario_complex()
    di = s["traceability"]["decision_inputs"]
    di["regressions"].append({"new_issue_id": "NEW-2", "severity": "major"})
    di["non_regression_new_issue_ids"] = ["NEW-3"]
    assert_mismatch(tmp_path, s, capsys, "regression-attributed frozen new issues")


# --- round-1 review closures (three-track exact-head findings) -----------------


def test_golden_g2d_retry_passes(tmp_path, capsys):
    # general P1-2 / codex #8 regression pin: a spec-legal successful retry
    # (superseded CANNOT_VERIFY attempt preserved) must PASS
    code, out, _err = run_checker(tmp_path, scenario_g2d_retry(), capsys)
    assert code == crs.EXIT_PASS, out
    assert "'Minor Revision'" in out


def test_two_current_reapplications_for_one_answer(tmp_path, capsys):
    s = scenario_g2d_retry()
    del s["traceability"]["reapplications"][1]["supersedes_reapplication_id"]
    assert_mismatch(tmp_path, s, capsys, "exactly one CURRENT reapplication's answer_refs")


def test_valid_rebuttal_upgrades_to_fully_only(tmp_path, capsys):
    # general P1-1 / codex #2: a letter-anchored sideways move must fail
    s = scenario_complex()
    adj = s["traceability"]["adjustments"][0]
    adj["to_verdict"] = "PARTIALLY_ADDRESSED"
    adj["residual_gap"] = {"text": "residual", "residual_obligation_class": "should_fix"}
    assert_exit2(tmp_path, s, capsys, "phase2b_lint_failed", "upgrade to FULLY_ADDRESSED")


def test_valid_rebuttal_from_fully_is_not_an_upgrade(tmp_path, capsys):
    s = scenario_complex()
    s["traceability"]["adjustments"][0]["from_verdict"] = "FULLY_ADDRESSED"
    assert_exit2(tmp_path, s, capsys, "phase2b_lint_failed", "upgrade to FULLY_ADDRESSED")


def test_author_pointer_must_upgrade_to_partially_or_fully(tmp_path, capsys):
    s = scenario_accept()
    s["traceability"]["adjustments"].append({
        "adjustment_id": "ADJ-9",
        "item_id": "REV-002",
        "from_verdict": "PARTIALLY_ADDRESSED",
        "to_verdict": "NOT_ADDRESSED",
        "basis": "author_pointer_located_evidence",
        "evidence_anchor": [_anchor()],
        "rationale": "not an upgrade",
    })
    assert_exit2(tmp_path, s, capsys, "phase2b_lint_failed", "upgrades to PARTIALLY/FULLY_ADDRESSED")


def test_author_pointer_downgrade_rejected(tmp_path, capsys):
    s = scenario_accept()
    s["traceability"]["adjustments"].append({
        "adjustment_id": "ADJ-9",
        "item_id": "REV-002",
        "from_verdict": "FULLY_ADDRESSED",
        "to_verdict": "PARTIALLY_ADDRESSED",
        "basis": "author_pointer_located_evidence",
        "evidence_anchor": [_anchor()],
        "residual_gap": {"text": "residual", "residual_obligation_class": "consider"},
        "rationale": "a downgrade",
    })
    assert_exit2(tmp_path, s, capsys, "phase2b_lint_failed", "upgrades to PARTIALLY/FULLY_ADDRESSED")


def test_malformed_report_version_is_manifest_incomplete(tmp_path, capsys):
    # A malformed value cannot cross the exact current report-1.3 boundary.
    s = scenario_accept()
    s["reports"][0]["report_format_version"] = "not-a-version"
    assert_exit2(tmp_path, s, capsys, "manifest_incomplete", "not a numeric dotted version")


def test_report_draft_hashes_must_be_12_hex(tmp_path, capsys):
    s = scenario_accept()
    s["reports"][0]["base_draft_hash"] = "XYZ"
    assert_exit2(tmp_path, s, capsys, "manifest_incomplete", "12-hex")


def test_orphan_g2d_acceptance_cannot_clear_deferral(tmp_path, capsys):
    # codex #3: acceptance with no backing adjustment must fail even when
    # phase2a_verdict == final_verdict == CANNOT_VERIFY
    s = scenario_g2d(accepted=True)
    vrec = s["verdict_record"]["items"][0]
    vrec["verdict"] = "CANNOT_VERIFY"
    vrec["cannot_verify_reason"] = "evidence surface inaccessible"
    vrec.pop("evidence_anchor")
    row = s["traceability"]["rows"][0]
    row["phase2a_verdict"] = "CANNOT_VERIFY"
    row.pop("adjustment_id")
    s["traceability"]["adjustments"] = []
    s["traceability"]["reapplications"][0]["pre_reapplication_verdict"] = "CANNOT_VERIFY"
    assert_mismatch(tmp_path, s, capsys, "backs exactly ONE user_accepted_fail_closed")


def test_resolution_reapplication_must_answer_its_intent(tmp_path, capsys):
    # codex #4: cross-wired CrossModelResolution must fail
    s = scenario_complex()
    s["traceability"]["resolution_intents"].append(
        {"intent_id": "INT-2", "item_id": "REV-002", "answered_by": "user", "guidance_note": "recheck"}
    )
    s["traceability"]["reapplications"].append({
        "reapplication_id": "RAP-2",
        "item_id": "REV-002",
        "answer_refs": ["intent:INT-2"],
        "pre_reapplication_verdict": "FULLY_ADDRESSED",
        "reapplied_verdict": "FULLY_ADDRESSED",
        "evidence_anchor": [_anchor('table: Table 4 [robustness]')],
        "rationale": "re-examination upholds the located evidence",
        "criterion_ref": "phase1:REV-002",
    })
    s["traceability"]["cross_model_resolutions"].append({
        "resolution_id": "RES-2",
        "item_id": "REV-002",
        "intent_id": "INT-1",  # cross-wired: RAP-2 answered INT-2, not INT-1
        "reapplication_id": "RAP-2",
        "state": "primary_upheld",
        "resolved_by": "system",
        "rationale": "cross-wired resolution",
    })
    assert_mismatch(tmp_path, s, capsys, "did not answer")


def test_challenged_drafted_body_is_never_booked(tmp_path, capsys):
    # codex #6: a booked adjustment content-equal to a CHALLENGED proposal
    s = scenario_complex()
    s["traceability"]["rebuttal_adjudications"].append({
        "rebuttal_adjudication_id": "RADJ-2",
        "item_id": "REV-001",
        "verdict": "challenged",
        "rationale": "The counter-evidence does not rebut the finding.",
    })
    s["traceability"]["pending_rebuttal_upgrades"].append({
        "proposal_id": "PRB-2",
        "item_id": "REV-001",
        "drafted_adjustment": copy.deepcopy(s["traceability"]["pending_rebuttal_upgrades"][0]["drafted_adjustment"]),
        "disposition": "challenged:RADJ-2",
    })
    assert_mismatch(tmp_path, s, capsys, "NEVER booked")


def test_duplicate_drafted_body_rejected(tmp_path, capsys):
    s = scenario_complex()
    s["traceability"]["pending_rebuttal_upgrades"].append({
        "proposal_id": "PRB-3",
        "item_id": "REV-001",
        "drafted_adjustment": copy.deepcopy(s["traceability"]["pending_rebuttal_upgrades"][0]["drafted_adjustment"]),
        "disposition": "booked:ADJ-1",
    })
    assert_mismatch(tmp_path, s, capsys, "duplicate PendingRebuttalUpgrade drafted body")


def test_escalation_with_absent_original_is_rejected_at_manifest_gate(tmp_path, capsys):
    s = scenario_accept()
    s["manifest_overrides"]["original_manuscript"] = {"present": False}
    s["verdict_record"]["escalation_exceptions"] = [
        {
            "exception_id": "ESC-1",
            "escalation_class": "research_integrity",
            "reason_code": "fabricated-consent",
            "evidence_anchor": 'text: §2 "consent"',
            "why_round1_missed_it": "Round 1 focused elsewhere.",
            "mechanical_decision_impact": "Major Revision",
            "approval_state": "pending",
        }
    ]
    di = s["traceability"]["decision_inputs"]
    di["escalations"] = [
        {
            "exception_id": "ESC-1",
            "effective_approval_state": "pending",
            "escalation_class": "research_integrity",
            "mechanical_decision_impact": "Major Revision",
        }
    ]
    di["apply_chain_witness"] = "pass"
    di.pop("reject_recommended")
    s["traceability"]["decision_state"] = "user_review_required"
    assert_exit2(
        tmp_path,
        s,
        capsys,
        "manifest_incomplete",
        "hard-required artifact original_manuscript",
    )


def test_source_reviewer_is_verbatim_roadmap_copy(tmp_path, capsys):
    # codex #9
    s = scenario_accept()
    s["precommitment"]["items"][0]["source_reviewer"] = "R2"
    s["precommitment"]["items"][0]["source_reviewer_labels"] = ["R2"]
    assert_mismatch(tmp_path, s, capsys, "VERBATIM copy of the Schema 7 reviewer field")


def test_half_transported_item_cannot_carry_null_severity():
    # general P2-1 / codex #5
    s = scenario_accept()
    item = s["roadmap"]["items"][0]
    del item["severity"]
    item["confidence"] = 4
    with pytest.raises(crs.ManifestError, match="requires transported severity"):
        crs.load_roadmap({"items": [item]})


def test_aborted_emission_with_lint_reason_is_exempt(tmp_path, capsys):
    # general P2-2: abort precedence over deferral — a lint-failure abort is
    # accepted as recorded (the checker cannot re-derive a fenced call's lint)
    s = scenario_accept()
    s["traceability"]["decision_state"] = "aborted"
    s["traceability"]["abort_reason"] = "phase2b_lint_failed"
    s["traceability"]["decision_inputs"].pop("reject_recommended")
    code, out, _err = run_checker(tmp_path, s, capsys)
    assert code == crs.EXIT_PASS, out
    assert "'aborted'" in out


def test_aborted_criteria_drift_claim_must_recompute(tmp_path, capsys):
    s = scenario_accept()
    s["traceability"]["decision_state"] = "aborted"
    s["traceability"]["abort_reason"] = "criteria_drift"
    s["traceability"]["decision_inputs"].pop("reject_recommended")
    assert_mismatch(tmp_path, s, capsys, "no silent verdict change recomputes")


def test_path_ref_must_be_relative(tmp_path, capsys):
    # codex #10
    s = scenario_accept()
    s["manifest_overrides"]["round1_findings"] = _entry("path:../secrets.md", SYNTH_SHA)
    assert_exit2(tmp_path, s, capsys, "manifest_incomplete", "RELATIVE")


def test_letter_without_required_item_details_notes_empty_layer(tmp_path, capsys):
    s = scenario_accept()
    s["letter"] = "# Editorial Decision\n\n## Closing\n"
    crit = s["precommitment"]["items"][0]["inherited_criterion"]
    del crit["letter_text"]
    del crit["letter_item_ref"]
    code, out, err = run_checker(tmp_path, s, capsys)
    assert code == crs.EXIT_PASS, out
    assert "no Required Item Details blocks parsed" in err


def test_superseded_attempt_must_be_failed(tmp_path, capsys):
    # codex round-2 #1: supersession is defined for FAILED attempts only (§6)
    s = scenario_g2d_retry()
    rap1 = s["traceability"]["reapplications"][0]
    rap1["reapplied_verdict"] = "FULLY_ADDRESSED"
    rap1.pop("cannot_verify_reason")
    rap1["evidence_anchor"] = [_anchor('text: §6 "procedure"')]
    assert_mismatch(tmp_path, s, capsys, "only FAILED (CANNOT_VERIFY) attempts are superseded")


def test_superseded_pre_value_binds_to_direct_retry(tmp_path, capsys):
    # codex round-2 #1: a failed attempt appends nothing, so its dispatch
    # tail equals its direct retry's recorded pre-value
    s = scenario_g2d_retry()
    s["traceability"]["reapplications"][0]["pre_reapplication_verdict"] = "NOT_ADDRESSED"
    assert_mismatch(tmp_path, s, capsys, "dispatch tail equals its direct retry's")


def test_aborted_emission_cannot_fake_manifest_root_cause(tmp_path, capsys):
    # codex round-2 #2: the checker reached recomputation, so the §11
    # manifest layer validated — a claimed G0/checker abort is a false root cause
    s = scenario_accept()
    s["traceability"]["decision_state"] = "aborted"
    s["traceability"]["abort_reason"] = "manifest_incomplete"
    s["traceability"]["decision_inputs"].pop("reject_recommended")
    assert_mismatch(tmp_path, s, capsys, "cannot be the true root cause")


def test_reapplication_letter_tag_requires_booked_rebuttal_in_chain(tmp_path, capsys):
    # general round-2 P2-1: a NOT_ADDRESSED -> FULLY upgrade cannot ride
    # letter-side anchors when the re-examined chain never booked a
    # valid_rebuttal record (§5.3 letter-tag condition, §3.4 closing rule)
    s = scenario_complex()
    letter_anchors = [_anchor('text: letter §3 "assertion"', "letter")]
    s["traceability"]["reapplications"][0]["evidence_anchor"] = copy.deepcopy(letter_anchors)
    s["traceability"]["adjustments"][1]["evidence_anchor"] = copy.deepcopy(letter_anchors)
    assert_mismatch(tmp_path, s, capsys, "letter-tagged anchors are valid exactly when")


def test_superseded_record_with_derived_adjustment_still_checked(tmp_path, capsys):
    # codex round-3: a verdict-changing successful reapplication carrying its
    # derived adjustment must NOT bypass the failed-only supersession guard
    s = scenario_g2d_retry()
    t = s["traceability"]
    rap1 = t["reapplications"][0]
    rap1["reapplied_verdict"] = "NOT_ADDRESSED"
    rap1.pop("cannot_verify_reason")
    rap1_anchors = [_anchor('text: §6 "procedure"')]
    rap1["evidence_anchor"] = copy.deepcopy(rap1_anchors)
    adj0 = {
        "adjustment_id": "ADJ-2",
        "item_id": "REV-001",
        "from_verdict": "FULLY_ADDRESSED",
        "to_verdict": "NOT_ADDRESSED",
        "basis": "cross_model_adjudication",
        "evidence_anchor": copy.deepcopy(rap1_anchors),
        "rationale": rap1["rationale"],
        "source_ref": "reapplication:RAP-1",
    }
    adj1 = t["adjustments"][0]
    adj1["from_verdict"] = "NOT_ADDRESSED"
    adj1["supersedes_adjustment_id"] = "ADJ-2"
    t["adjustments"].insert(0, adj0)
    t["reapplications"][1]["pre_reapplication_verdict"] = "NOT_ADDRESSED"
    assert_mismatch(tmp_path, s, capsys, "only FAILED (CANNOT_VERIFY) attempts are superseded")


def test_p2_dissent_must_take_the_user_path(tmp_path, capsys):
    # general round-3 P2: §7 — the judge's adjudication scope equals the §9
    # pass's P1 coverage; a judge-cleared P2 dissent cannot clear G2(a)
    s = scenario_complex()
    pre_rev002 = next(rec for rec in s["precommitment"]["items"] if rec["item_id"] == "REV-002")
    s["verdict_record"]["dissents"].append({
        "dissent_id": "DIS-2",
        "item_id": "REV-002",
        "criterion_hash": "0" * 64,  # recomputed at emit
        "reason_code": "criterion_ambiguous",
        "original_operationalization": pre_rev002["operationalization"]["fully_addressed"],
        "replacement_operationalization": "Results carries a robustness table with at least one alternative specification.",
        "evidence": 'text: §4 "specifications"',
        "decision_impact_note": "Narrows the robustness surface.",
    })
    rev002 = next(rec for rec in s["verdict_record"]["items"] if rec["item_id"] == "REV-002")
    rev002["applied_criterion"] = "dissented:DIS-2"
    s["traceability"]["dissent_adjudications"] = [
        {"dissent_id": "DIS-1", "adjudicator": "cross_model", "outcome": "replacement_approved",
         "rationale": "Replacement approved by the judge."},
        {"dissent_id": "DIS-2", "adjudicator": "cross_model", "outcome": "replacement_approved",
         "rationale": "Replacement approved by the judge."},
    ]
    assert_mismatch(tmp_path, s, capsys, "always take the G2(a) user path")


def test_user_adjudication_on_active_p1_dissent_stays_legal(tmp_path, capsys):
    # adjudicated AGAINST the one-way §7 reading (codex round-4 #1a): the §6
    # deferral loop records a user-adjudicated DissentAdjudication DIRECTLY,
    # and the §9 pass can be per-row unavailable — the user path must remain
    # a legal fallback on an active-setup P1 dissent
    s = scenario_g2d(accepted=False)
    s["traceability"]["dissent_adjudications"][0]["adjudicator"] = "user"
    code, out, _err = run_checker(tmp_path, s, capsys)
    assert code == crs.EXIT_PASS, out


def test_system_intent_requires_evaluated_p1_row(tmp_path, capsys):
    # general round-4 P1: a system intent forged onto a not_configured row
    s = scenario_accept()
    s["traceability"]["resolution_intents"].append(
        {"intent_id": "INT-1", "item_id": "REV-001", "answered_by": "system"}
    )
    assert_mismatch(tmp_path, s, capsys, "system intents exist only for evaluated must_fix diverges rows")


def test_divergence_reapplication_requires_evaluated_p1_row(tmp_path, capsys):
    # general round-4 P1: the intent→reapplication→resolution chain cannot
    # exist for a row the judge never evaluated (not_configured / P2)
    s = scenario_accept()
    s["traceability"]["resolution_intents"].append(
        {"intent_id": "INT-1", "item_id": "REV-001", "answered_by": "user", "guidance_note": "forged"}
    )
    s["traceability"]["reapplications"].append({
        "reapplication_id": "RAP-1",
        "item_id": "REV-001",
        "answer_refs": ["intent:INT-1"],
        "pre_reapplication_verdict": "FULLY_ADDRESSED",
        "reapplied_verdict": "FULLY_ADDRESSED",
        "evidence_anchor": [_anchor()],
        "rationale": "forged divergence re-verification",
        "criterion_ref": "phase1:REV-001",
    })
    s["traceability"]["cross_model_resolutions"].append({
        "resolution_id": "RES-1",
        "item_id": "REV-001",
        "intent_id": "INT-1",
        "reapplication_id": "RAP-1",
        "state": "primary_upheld",
        "resolved_by": "system",
        "rationale": "forged resolution",
    })
    assert_mismatch(tmp_path, s, capsys, "divergence-only re-application exists only for an evaluated must_fix row")


def test_forged_divergence_on_agree_row_rejected(tmp_path, capsys):
    # codex round-5 P1: an originally-agree row (judge verdict == committed
    # verdict) cannot manufacture its own divergence by forging a
    # downgrading intent→reapplication→adjustment→resolution chain — §6
    # identifies diverges BEFORE the system intent is emitted
    s = scenario_complex()
    vrec = next(rec for rec in s["verdict_record"]["items"] if rec["item_id"] == "REV-002")
    vrec["verdict"] = "FULLY_ADDRESSED"
    vrec["evidence_anchor"] = ['table: Table 4 [robustness]']
    row = s["traceability"]["rows"][1]
    row["phase2a_verdict"] = "FULLY_ADDRESSED"
    row["final_verdict"] = "NOT_ADDRESSED"
    row["status"] = "NOT_ADDRESSED"
    row["verified"] = "NO"
    row["cross_model_status"] = "diverges"  # manufactured after the change
    adj2 = s["traceability"]["adjustments"][1]
    adj2["from_verdict"] = "FULLY_ADDRESSED"
    adj2["to_verdict"] = "NOT_ADDRESSED"
    rap = s["traceability"]["reapplications"][0]
    rap["pre_reapplication_verdict"] = "FULLY_ADDRESSED"
    rap["reapplied_verdict"] = "NOT_ADDRESSED"
    di = s["traceability"]["decision_inputs"]
    di["per_item"][1]["final_verdict"] = "NOT_ADDRESSED"
    di["verdict_counts"]["must_fix"] = {v: 0 for v in crs.VERDICTS}
    di["verdict_counts"]["must_fix"].update({"FULLY_ADDRESSED": 1, "NOT_ADDRESSED": 1})
    di["reject_recommended"] = True
    s["traceability"]["decision_state"] = "Major Revision"
    assert_mismatch(tmp_path, s, capsys, "no divergence existed at dispatch")


def test_divergence_chain_carries_original_system_intent(tmp_path, capsys):
    # codex round-5 P1 (companion rule): a user-only intent chain on an
    # evaluated diverging row lacks the §6 mandating system intent
    s = scenario_complex()
    s["traceability"]["resolution_intents"] = [
        {"intent_id": "INT-2", "item_id": "REV-002", "answered_by": "user", "guidance_note": "recheck"}
    ]
    s["traceability"]["reapplications"][0]["answer_refs"] = ["intent:INT-2"]
    s["traceability"]["cross_model_resolutions"][0]["intent_id"] = "INT-2"
    assert_mismatch(tmp_path, s, capsys, "ORIGINAL mandating system intent")


def test_ghost_dissent_must_be_applied(tmp_path, capsys):
    # general round-5 P1: a DissentRecord never referenced by its item's
    # verdict record (applied_criterion stays precommitted) is a ghost — it
    # cannot trip the §7 bound or authorize a re-application second chance
    s = scenario_accept()
    s["verdict_record"]["dissents"].append({
        "dissent_id": "DIS-1",
        "item_id": "REV-001",
        "criterion_hash": "0" * 64,  # recomputed at emit
        "reason_code": "criterion_ambiguous",
        "original_operationalization": "Methods carries a power analysis naming effect size, alpha, and power.",
        "replacement_operationalization": "Methods carries a power analysis naming effect size.",
        "evidence": 'text: §3.2 "power analysis"',
        "decision_impact_note": "Narrows the committed pattern.",
    })
    s["traceability"]["dissent_adjudications"] = [
        {"dissent_id": "DIS-1", "adjudicator": "user", "outcome": "replacement_approved",
         "rationale": "Approved at the checkpoint."}
    ]
    assert_mismatch(tmp_path, s, capsys, "is a ghost")


def test_below_bound_adjudication_rejected(tmp_path, capsys):
    # codex round-4 #1: dissents below the §7 bound stand unadjudicated by design
    s = scenario_complex()
    s["traceability"]["dissent_adjudications"] = [
        {"dissent_id": "DIS-1", "adjudicator": "user", "outcome": "replacement_approved",
         "rationale": "Adjudicated despite no bound tripping."}
    ]
    assert_mismatch(tmp_path, s, capsys, "unadjudicated by design")


def test_acceptance_must_reference_current_reapplication(tmp_path, capsys):
    # codex round-4 #2: a stale acceptance of a superseded attempt cannot
    # override the successful current retry
    s = scenario_g2d_retry()
    s["traceability"]["g2d_acceptances"] = [
        {"acceptance_id": "ACC-1", "item_id": "REV-001", "reapplication_id": "RAP-1", "accepted_by": "user"}
    ]
    assert_mismatch(tmp_path, s, capsys, "SUPERSEDED reapplication")


# --- §6 derivation unit table --------------------------------------------------


@pytest.mark.parametrize(
    "p1_items, p2_partials, p2_made_worse, rate, regressions, expected",
    (
        ([("MADE_WORSE", "critical", None)], [], False, (1, 1), set(), ("Major Revision", True, "B1")),
        ([("FULLY_ADDRESSED", "major", None)], [], False, (1, 1), {"critical"}, ("Major Revision", True, "B1")),
        ([("NOT_ADDRESSED", "major", None), ("FULLY_ADDRESSED", "major", None)], [], False, (1, 1), set(),
         ("Major Revision", True, "B2")),
        ([("MADE_WORSE", "major", None)], [], False, (1, 1), set(), ("Major Revision", True, "B2")),
        ([("CANNOT_VERIFY", "major", None), ("FULLY_ADDRESSED", "major", None), ("FULLY_ADDRESSED", None, None)],
         [], False, (1, 1), set(), ("Major Revision", False, "B3")),
        ([("FULLY_ADDRESSED", "major", None)], [], False, (1, 1), {"major"}, ("Major Revision", False, "B3")),
        ([("PARTIALLY_ADDRESSED", "major", "must_fix")], [], False, (1, 1), set(), ("Major Revision", False, "B4")),
        ([("FULLY_ADDRESSED", "major", None)], ["must_fix"], False, (1, 2), set(), ("Major Revision", False, "B4")),
        ([("PARTIALLY_ADDRESSED", "major", "should_fix")], [], False, (1, 1), set(), ("Minor Revision", False, "B5")),
        ([("FULLY_ADDRESSED", "major", None)], [], False, (3, 4), set(), ("Minor Revision", False, "B5")),
        ([("FULLY_ADDRESSED", "major", None)], [], True, (1, 1), set(), ("Minor Revision", False, "B5")),
        ([("FULLY_ADDRESSED", "major", None)], [], False, (1, 1), {"minor"}, ("Minor Revision", False, "B5")),
        ([("FULLY_ADDRESSED", "major", None)], [], False, (4, 5), set(), ("Accept", False, "B6")),
        ([], [], False, (0, 0), set(), ("Accept", False, "B6")),
    ),
)
def test_derive_decision_base_table(p1_items, p2_partials, p2_made_worse, rate, regressions, expected):
    assert crs.derive_decision(p1_items, p2_partials, p2_made_worse, rate[0], rate[1], regressions, []) == expected


def test_derive_decision_floor_and_reject_semantics():
    approved_major = {"effective_approval_state": "approved", "escalation_class": "ethics",
                      "mechanical_decision_impact": "Major Revision"}
    pending_major = dict(approved_major, effective_approval_state="pending")
    rejected_major = dict(approved_major, effective_approval_state="rejected")
    integrity_minor = {"effective_approval_state": "approved", "escalation_class": "research_integrity",
                       "mechanical_decision_impact": "Minor Revision"}
    base_accept = ([("FULLY_ADDRESSED", "major", None)], [], False, 1, 1, set())
    assert crs.derive_decision(*base_accept, [approved_major]) == ("Major Revision", False, "B6")
    assert crs.derive_decision(*base_accept, [pending_major]) == ("Accept", False, "B6")
    assert crs.derive_decision(*base_accept, [rejected_major]) == ("Accept", False, "B6")
    assert crs.derive_decision(*base_accept, [integrity_minor]) == ("Minor Revision", True, "B6")


def test_zero_p1_run_reaches_non_p1_disjuncts():
    # zero P1 items: B2 vacuously unsatisfied, but B1's critical-regression
    # disjunct still fires (§6 B2 note)
    assert crs.derive_decision([], [], False, 1, 1, {"critical"}, []) == ("Major Revision", True, "B1")


# --- §11 witness unit tests ----------------------------------------------------


def _witness_manifest(original_present=True):
    return {
        "artifacts": {
            "original_manuscript": _entry("path:m1", ORIGINAL_SHA) if original_present else {"present": False},
            "revised_manuscript": _entry("path:m2", REVISED_SHA),
            "revision_patches": {"present": True, "items": [
                {"path_or_passport_ref": "path:p", "sha256": PATCH_SHA, "version_label": None, "origin_date": None}
            ]},
        }
    }


def _authorization_witness():
    return {
        "status": "pass",
        "unregistered_claim_drift_review_required": True,
    }


def test_witness_pass_and_prefix_format():
    report = {"report_format_version": "1.3", "base_draft_hash": ORIGINAL_SHA[:12],
              "output_draft_hash": REVISED_SHA[:12], "patch_digest": PATCH_SHA,
              "authorization_witness": _authorization_witness()}
    witness, notes = crs.compute_apply_chain_witness(_witness_manifest(), [report])
    assert witness == "pass" and notes == []


def test_witness_rejects_absent_original_in_current_contract():
    report = {"report_format_version": "1.3", "base_draft_hash": "aaaaaaaaaaaa",
              "output_draft_hash": REVISED_SHA[:12], "patch_digest": PATCH_SHA,
              "authorization_witness": _authorization_witness()}
    with pytest.raises(crs.ManifestError, match="hard-requires original_manuscript"):
        crs.compute_apply_chain_witness(
            _witness_manifest(original_present=False), [report]
        )


def test_witness_no_reports():
    witness, notes = crs.compute_apply_chain_witness(_witness_manifest(), [])
    assert witness == "not_run_no_reports" and notes == []


# --- canonical hash vector -----------------------------------------------------


def test_canonical_hash_is_jcs_sha256():
    expected = hashlib.sha256('{"a":"中","b":1}'.encode("utf-8")).hexdigest()
    assert crs.canonical_hash({"b": 1, "a": "中"}) == expected


# --- §10 card-normalization fixtures -------------------------------------------

HEI_PINNED = (
    ("EIC", ["EIC"]),
    ("Peer Reviewer 1 (Methodology)", ["R1"]),
    ("Peer Reviewer 2 (Domain)", ["R2"]),
    ("Peer Reviewer 3 (Cross-disciplinary/Practical)", ["R3"]),
)
INTERDISCIPLINARY_PINNED = (
    ("EIC", ["EIC"]),
    ("Peer Reviewer 1 (Methodology — ML Technical Expert)", ["R1"]),
    ("Peer Reviewer 2 (Domain — Institutional Research Expert)", ["R2"]),
    ("Peer Reviewer 3 (Cross-disciplinary — Public Policy / AI Ethics)", ["R3"]),
)


def _role_lines(path: Path):
    lines = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("**Role**: "):
            lines.append(line[len("**Role**: "):])
    return lines


@pytest.mark.parametrize(
    "filename, pinned",
    (
        ("hei_paper_review_example.md", HEI_PINNED),
        ("interdisciplinary_review_example.md", INTERDISCIPLINARY_PINNED),
    ),
)
def test_example_card_role_lines_pinned_verbatim(filename, pinned):
    lines = _role_lines(EXAMPLES / filename)
    assert lines == [raw for raw, _expected in pinned], "example file Role lines changed — re-pin §10 fixtures"
    for raw, expected in pinned:
        labels, parse_failure = crs.normalize_reviewer_labels(raw)
        assert labels == expected, (raw, labels)
        assert parse_failure is False


@pytest.mark.parametrize(
    "raw, expected",
    (
        ("DA", ["DA"]),
        ("Devil's Advocate", ["DA"]),
        ("Devil’s Advocate", ["DA"]),
        ("DA (Adversarial)", ["DA"]),
    ),
)
def test_synthetic_da_fixtures(raw, expected):
    labels, parse_failure = crs.normalize_reviewer_labels(raw)
    assert labels == expected and parse_failure is False


@pytest.mark.parametrize(
    "raw, expected, parse_failure",
    (
        ("R1, R3", ["R1", "R3"], False),
        ("R1 and R2", ["R1", "R2"], False),
        ("R1/R2;R3", ["R1", "R2", "R3"], False),
        ("Editor-in-Chief", ["EIC"], False),
        ("Reviewer 2", ["R2"], False),
        ("EIC & R1", ["EIC", "R1"], False),
        ("R1, R1", ["R1"], False),
        ("Editorial Office", [], True),
        ("", [], False),
        ("Methodology Board (R1)", [], True),  # parenthetical stripped FIRST — no substring extraction
    ),
)
def test_normalization_grammar_edges(raw, expected, parse_failure):
    labels, failure = crs.normalize_reviewer_labels(raw)
    assert labels == expected
    assert failure is parse_failure


def test_paren_strip_precedes_dash_strip():
    # an em-dash inside a parenthetical is removed by step 1a; running 1b
    # first would leave an unbalanced fragment (§10 order is normative)
    labels, failure = crs.normalize_reviewer_labels("Peer Reviewer 1 (Methodology — ML) — lead")
    assert labels == ["R1"] and failure is False


# --- #576 §8 routing fixtures (PR-B2): frozen records reach AND are ingested at 4.5


REPO_ROOT = Path(__file__).resolve().parent.parent
_INTEGRITY_AGENT = REPO_ROOT / "academic-pipeline/agents/integrity_verification_agent.md"
_ORCHESTRATOR = REPO_ROOT / "academic-pipeline/agents/pipeline_orchestrator_agent.md"


def _add_frozen_non_regression_records(scenario):
    """Insert an identical previously_missed + indeterminate pair into BOTH the
    2A set and the 2B frozen copy (whole-record byte equality), and mirror the
    ids into decision_inputs — the §8 goalpost guard keeps them decision-inert."""
    records = [
        _new_issue(8, "previously_missed", "major"),
        _new_issue(9, "indeterminate", "minor"),
    ]
    scenario["verdict_record"]["new_issues"].extend(json.loads(json.dumps(records)))
    scenario["traceability"]["new_issues"].extend(json.loads(json.dumps(records)))
    di = scenario["traceability"]["decision_inputs"]
    di["non_regression_new_issue_ids"] = sorted(
        set(di["non_regression_new_issue_ids"]) | {"NEW-8", "NEW-9"}
    )
    return scenario


def _assert_4_5_ingestion_pinned(path_marker: str):
    """The INGESTION half of the §8 fixture: the Stage 4.5 gate's input list
    consumes BOTH attributions (not just arrival), and the orchestrator's
    handoff row for this path carries the sidecar's frozen records."""
    integrity = _INTEGRITY_AGENT.read_text(encoding="utf-8")
    assert (
        "the Stage 3' traceability sidecar's frozen `previously_missed` AND "
        "`indeterminate` new-issue records" in integrity
    ), "integrity_verification_agent must consume BOTH attributions (#576 §8)"
    assert "Current #576 1.1 hard-requires the original manuscript" in integrity
    assert "Consume both attributions as integrity-check input" in integrity
    assert "disposition appears in the report" in integrity, (
        "ingestion means per-record assessment, not just arrival"
    )
    orch = _ORCHESTRATOR.read_text(encoding="utf-8")
    assert path_marker in orch, f"orchestrator handoff row missing: {path_marker!r}"


def test_routing_fixture_accept_direct_records_reach_and_are_ingested(tmp_path, capsys):
    # Accept-direct path (Stage 3' -> 4.5, no Stage 4' between): the frozen
    # records survive a checker-validated emission at decision Accept...
    s = _add_frozen_non_regression_records(scenario_accept())
    code, out, _err = run_checker(tmp_path, s, capsys)
    assert code == crs.EXIT_PASS, out
    assert "'Accept'" in out
    # ...and the 4.5 gate INGESTS them on this path (prose contract pinned).
    _assert_4_5_ingestion_pinned(
        "| Stage 3' -> 4.5 | (Accept/Minor direct path — no Stage 4' between)"
    )
    orch = _ORCHESTRATOR.read_text(encoding="utf-8")
    assert "the frozen records are gate INPUT, not just cargo" in orch


def test_routing_fixture_major_via_4prime_records_reach_and_are_ingested(tmp_path, capsys):
    # Major-via-4' path: same frozen records on a Major Revision emission...
    s = _add_frozen_non_regression_records(scenario_g2d(accepted=True))
    code, out, _err = run_checker(tmp_path, s, capsys)
    assert code == crs.EXIT_PASS, out
    assert "'Major Revision'" in out
    # ...ride through 4' with the roadmap on the extended Stage 4/4' -> 4.5 row.
    _assert_4_5_ingestion_pinned(
        "(Major-via-4' path) the Stage 3' traceability sidecar with its frozen "
        "`previously_missed`/`indeterminate` new-issue records"
    )


_RE_REVIEW_PROTOCOL = REPO_ROOT / "academic-paper-reviewer/references/re_review_mode_protocol.md"


def test_rev_pm_closed_mapping_all_fields_pinned():
    """#576 §8: the previously_missed forward-seed mapping is CLOSED — every
    required RoadmapItem field plus all four transported optional fields must
    have a stated derivation on the operative protocol surface, so a Stage 3'
    synthesizer can build a legal REV-PM item from the living docs alone."""
    text = _RE_REVIEW_PROTOCOL.read_text(encoding="utf-8")
    start = text.index("- `previously_missed`")
    block = text[start:text.index("- `indeterminate`", start)]
    for needle in (
        "`id = REV-PM-<n>`",
        "`source_refs = [{seat: found_by, channel: finding, ordinal: <n>, subclaim_ordinal: 0}]`",
        "`obligation_class = consider`",
        "`cost_scope = {kind: section, locator: <location_anchor section>}`",
        "`consequence_if_unaddressed = {code: reader_traceability_reduced",
        "target section derives from `location_anchor`",
        'suggested action is "assess; address or record as a limitation"',
        "consensus is `SINGLE-VERIFIER`",
        "verification criteria require resolution or explicit limitation",
        "severity/evidence/confidence/competence copy the frozen record",
        "`proposed_targets` is the unique exact current block",
        "Legacy `type` is not emitted",
    ):
        assert needle in block, f"REV-PM closed mapping missing field derivation: {needle!r}"
