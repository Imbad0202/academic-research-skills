#!/usr/bin/env python3
"""Stance runner for the #655 claim-standing probe (Track B execution).

Consumes a finalized candidate ledger under a `retrieval_plus_stance`
query-plan-1.1 consent and produces one `claim-standing-stance-record/1.0`
plus its `evidence-row/1.3` rows. The stance provider is an injected
transport whose declared identity must equal the consented `stance_plan`;
no live provider adapter ships here, and every emitted surface carries the
mandatory `STANCE CLASSIFICATION UNMEASURED` banner.

Fail-closed discipline: a plan without stance authorization refuses before
any call; a malformed judge output (unknown stance token, missing line,
non-verbatim or overlong evidence quote) becomes that row's
`not_checked/parse_error` with the raw output retained verbatim; transport
failures map to `judge_timeout`/`judge_error`. The semantic validator
`validate_stance_record` re-verifies every identity hash, the all-selected
distribution sum, exact selected-family coverage, and each referenced
evidence row's recomputed hash.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from typing import Any

from jsonschema import Draft202012Validator

try:
    from scripts import build_claim_standing_candidate_ledger as substrate
except ImportError:  # direct script execution
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import build_claim_standing_candidate_ledger as substrate  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[1]
STANCE_RECORD_SCHEMA = (
    REPO_ROOT / "shared/contracts/claim_standing/stance_record.schema.json"
)
EVIDENCE_ROW_SCHEMA = (
    REPO_ROOT / "shared/contracts/evidence/evidence_row_v1_3.schema.json"
)
PROMPT_CONTRACT_VERSION = "claim-standing-stance-prompt-1.0"
STANCE_RECORD_SUFFIX = ".stance-record.json"
EVIDENCE_ROWS_SUFFIX = ".evidence-rows.json"
UNMEASURED_BANNER = "STANCE CLASSIFICATION UNMEASURED"
STANCES = (
    "support",
    "contradict",
    "mixed",
    "not_addressed",
    "INSUFFICIENT_EVIDENCE",
    "AMBIGUOUS",
)
MAX_EVIDENCE_WORDS = 25

PROMPT_TEMPLATE = """You assess the relation between one claim and one candidate source's inspected text. Judge only what THIS text says about THIS claim; never judge source quality, field consensus, or truth.

Respond with exactly four lines and nothing else:
STANCE: one of support | contradict | mixed | not_addressed | INSUFFICIENT_EVIDENCE | AMBIGUOUS
EVIDENCE: one quotation of at most 25 words copied verbatim from the inspected text
CONDITIONS: the population or condition difference driving mixed or AMBIGUOUS, or none
RATIONALE: one or two sentences.

Rules: support and contradict describe the direction of the inspected text relative to the claim at face value. mixed requires both directions explicit in the text. not_addressed means the text is relevant but silent on the proposition. INSUFFICIENT_EVIDENCE means the text touches the proposition without directional information. AMBIGUOUS means incompatible readings or an unresolvable condition difference. Never output a confidence, probability, or score.

CLAIM: {claim}
CANDIDATE TITLE: {title}
INSPECTED TEXT ({coverage}): {evidence}
"""


class StanceError(RuntimeError):
    pass


def _fail(message: str) -> None:
    raise StanceError(message)


def _now() -> str:
    return (
        datetime.now(timezone.utc)
        .replace(microsecond=0)
        .isoformat()
        .replace("+00:00", "Z")
    )


def _validate_schema(schema_path: Path, value: dict[str, Any], label: str) -> None:
    schema = json.loads(schema_path.read_bytes())
    errors = sorted(
        Draft202012Validator(schema).iter_errors(value), key=lambda e: str(e.path)
    )
    if errors:
        first = errors[0]
        _fail(f"{label} schema: {list(first.path)!r}: {first.message}")


def _require_stance_consent(plan: dict[str, Any]) -> None:
    substrate.validate_schema(
        plan, substrate.plan_schema_filename(plan), "query plan"
    )
    substrate.validate_plan(plan)
    consent = plan["consent"]
    if (
        plan.get("schema_version") != substrate.PLAN_VERSION_1_1
        or consent["decision"] != "retrieval_plus_stance"
    ):
        _fail(
            "stance classification requires a query-plan-1.1 consent whose "
            "decision is retrieval_plus_stance; this plan does not authorize it"
        )
    if plan["stance_plan"]["prompt_contract_version"] != PROMPT_CONTRACT_VERSION:
        _fail(
            "consented stance_plan.prompt_contract_version "
            f"{plan['stance_plan']['prompt_contract_version']!r} does not match "
            f"this runner's frozen {PROMPT_CONTRACT_VERSION!r}"
        )


def _require_transport_identity(plan: dict[str, Any], transport: Any) -> None:
    stance_plan = plan["stance_plan"]
    for field in ("provider_identity", "model_identity"):
        declared = getattr(transport, field, None)
        if declared != stance_plan[field]:
            _fail(
                f"transport {field} {declared!r} does not match the consented "
                f"stance_plan {field} {stance_plan[field]!r}"
            )
    if not getattr(transport, "runtime_identity", None):
        _fail("transport must declare a runtime_identity")


def _require_bound_ledger(plan: dict[str, Any], ledger_value: dict[str, Any]) -> None:
    substrate.validate_schema(
        ledger_value, "candidate_ledger.schema.json", "candidate ledger"
    )
    if ledger_value["candidate_ledger_sha256"] != substrate.bound_digest(
        ledger_value, "candidate_ledger_sha256"
    ):
        _fail("candidate_ledger_sha256 does not bind the ledger")
    if ledger_value["query_plan_sha256"] != plan["plan_sha256"]:
        _fail("candidate ledger is bound to a different query plan")
    if ledger_value["claim_sha256"] != plan["claim"]["claim_sha256"]:
        _fail("candidate ledger claim binding drifted")


def _selected_families(ledger_value: dict[str, Any]) -> list[dict[str, Any]]:
    return sorted(
        (
            family
            for family in ledger_value["work_families"]
            if family["selection_state"] == "selected"
        ),
        key=lambda family: family["work_family_id"],
    )


def _parse_judge_output(raw_output: str, evidence_text: str) -> dict[str, Any]:
    """Strict four-line grammar, in order, nothing else; deviations are parse
    errors, and the record schema's own bounds are enforced here so a verbose
    judge degrades one row instead of aborting the run."""
    body = raw_output[:-1] if raw_output.endswith("\n") else raw_output
    lines = body.split("\n")
    prefixes = ("STANCE: ", "EVIDENCE: ", "CONDITIONS: ", "RATIONALE: ")
    if len(lines) != len(prefixes) or any(not line.strip() for line in lines):
        raise ValueError("expected exactly four labeled lines and nothing else")
    fields: dict[str, str] = {}
    for line, prefix in zip(lines, prefixes):
        if not line.startswith(prefix):
            raise ValueError(f"expected the {prefix.strip()} line in order")
        fields[prefix.strip().rstrip(":")] = line[len(prefix) :].strip()
    if fields["STANCE"] not in STANCES:
        raise ValueError(f"unknown stance token {fields['STANCE']!r}")
    quote = fields["EVIDENCE"]
    if not quote or quote == "none":
        raise ValueError("EVIDENCE must quote the inspected text")
    if len(quote.split()) > MAX_EVIDENCE_WORDS or len(quote) > 1000:
        raise ValueError("EVIDENCE exceeds the bounded-excerpt ceiling")
    if quote not in evidence_text:
        raise ValueError("EVIDENCE is not a verbatim substring of the inspected text")
    rationale = fields["RATIONALE"]
    if not rationale or len(rationale) > 2000:
        raise ValueError("RATIONALE must be non-empty and at most 2000 characters")
    conditions = fields["CONDITIONS"]
    if not conditions or len(conditions) > 1000:
        raise ValueError("CONDITIONS must be 'none' or a non-empty description")
    return {
        "stance": fields["STANCE"],
        "quote": quote,
        "conditions": None if conditions == "none" else conditions,
        "rationale": rationale,
    }


def _evidence_row(
    plan: dict[str, Any],
    ledger_value: dict[str, Any],
    family: dict[str, Any],
    hit: dict[str, Any],
    quote: str,
    captured_at: str,
) -> dict[str, Any]:
    evidence_text = hit["abstract_text"]
    start = evidence_text.encode("utf-8").index(quote.encode("utf-8"))
    row = {
        "schema_version": "evidence-row/1.3",
        "surface": "claim_standing_advisory",
        "row_id": f"EVR-CS-{family['work_family_id']}",
        "claim": {
            "claim_id": plan["claim"]["claim_id"],
            "claim_sha256": plan["claim"]["claim_sha256"],
            "probe_id": plan["probe_id"],
        },
        "candidate": {
            "work_family_id": family["work_family_id"],
            "canonical_raw_hit_id": family["canonical_raw_hit_id"],
            "candidate_ledger_sha256": ledger_value["candidate_ledger_sha256"],
            "display_label": hit["title"],
            "doi": hit["doi"],
        },
        "coverage": family["coverage"],
        "source": {
            "source_content_sha256": family["content_sha256"],
            "source_content_utf8_bytes": len(evidence_text.encode("utf-8")),
        },
        "excerpt": {
            "state": "verified_exact_match",
            "text": quote,
            "excerpt_sha256": substrate.text_digest(quote),
            "source_span_utf8": {
                "start": start,
                "end": start + len(quote.encode("utf-8")),
            },
            "captured_at": captured_at,
        },
        # Fresh extraction, recorded as a cache miss per the family rule.
        "cache": {"status": "miss", "key_sha256": substrate.text_digest(quote)},
        "content_handling": {
            "contains_external_text": True,
            # Local persistence authority never confers sharing authority.
            "sharing_scope": "session_only",
            "rights_basis": "not_assessed",
        },
        "row_sha256": "0" * 64,
    }
    row["row_sha256"] = substrate.bound_digest(row, "row_sha256")
    _validate_schema(EVIDENCE_ROW_SCHEMA, row, "evidence row")
    return row


def _stance_prompt(
    plan: dict[str, Any], family: dict[str, Any], hit: dict[str, Any]
) -> str:
    return PROMPT_TEMPLATE.format(
        claim=plan["claim"]["claim_text"],
        title=hit["title"] or "(untitled)",
        coverage=family["coverage"],
        evidence=hit["abstract_text"],
    )


def _tally(rows: list[dict[str, Any]]) -> dict[str, int]:
    counted = {bucket: 0 for bucket in STANCES}
    counted["not_checked"] = 0
    for row in rows:
        bucket = row["stance"] if row["check_state"] == "performed" else "not_checked"
        counted[bucket] += 1
    return counted


def run_stance(
    plan: dict[str, Any],
    ledger_value: dict[str, Any],
    *,
    transport: Any,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    _require_stance_consent(plan)
    _require_transport_identity(plan, transport)
    _require_bound_ledger(plan, ledger_value)

    hits_by_id = {hit["raw_hit_id"]: hit for hit in ledger_value["raw_hits"]}
    rows: list[dict[str, Any]] = []
    evidence_rows: list[dict[str, Any]] = []
    transmissions: list[dict[str, Any]] = []
    for family in _selected_families(ledger_value):
        hit = hits_by_id[family["canonical_raw_hit_id"]]
        base_row = {
            "work_family_id": family["work_family_id"],
            "canonical_raw_hit_id": family["canonical_raw_hit_id"],
            "check_state": "not_checked",
            "stance": None,
            "failure_state": None,
            "conditions_noted": None,
            "evidence_scope": family["coverage"],
            "evidence_row_refs": [],
            "prompt_sha256": None,
            "assessment_input_sha256": None,
            "raw_output": None,
            "raw_output_sha256": None,
            "rationale": None,
            "assessed_at": None,
        }
        if family["content_state"] != "available" or hit["abstract_text"] is None:
            base_row["failure_state"] = "abstract_missing"
            rows.append(base_row)
            continue
        prompt = _stance_prompt(plan, family, hit)
        prompt_sha = substrate.text_digest(prompt)
        assessment_input_sha = substrate.digest(
            {
                "claim_sha256": plan["claim"]["claim_sha256"],
                "candidate_content_sha256": substrate.text_digest(
                    hit["abstract_text"]
                ),
                "prompt_contract_version": PROMPT_CONTRACT_VERSION,
                "prompt_sha256": prompt_sha,
            }
        )
        transmission = {
            "work_family_id": family["work_family_id"],
            "recipient_provider_identity": plan["stance_plan"]["provider_identity"],
            "recipient_model_identity": plan["stance_plan"]["model_identity"],
            "purpose": "stance_classification",
            "content_classes": ["claim_and_selected_evidence_to_stance_provider"],
            "prompt_sha256": prompt_sha,
            "prompt_utf8_bytes": len(prompt.encode("utf-8")),
            "consent_receipt_id": plan["consent"]["consent_receipt_id"],
            "retention_state": plan["stance_plan"]["retention_state"],
            "retention_reference": plan["stance_plan"]["retention_reference"],
            "sent_at": _now(),
            "result_state": None,
        }
        transmissions.append(transmission)
        # The prompt hashes bind BEFORE the transport call: a failed call
        # (timeout, judge error, oversized output) still retains exactly
        # what was sent, so the transmission ledger's cross-check can hold
        # every transport-reaching row to its recorded prompt hash.
        base_row.update(
            prompt_sha256=prompt_sha,
            assessment_input_sha256=assessment_input_sha,
        )
        try:
            raw_output = transport(prompt)
        except TimeoutError:
            base_row["failure_state"] = "judge_timeout"
            transmission["result_state"] = "judge_timeout"
            rows.append(base_row)
            continue
        except Exception:  # noqa: BLE001 — any provider failure is judge_error
            base_row["failure_state"] = "judge_error"
            transmission["result_state"] = "judge_error"
            rows.append(base_row)
            continue
        if not isinstance(raw_output, str):
            base_row["failure_state"] = "judge_error"
            transmission["result_state"] = "judge_error"
            rows.append(base_row)
            continue
        if len(raw_output) > 20000:
            # The contract's raw-output ceiling; an oversized output is not
            # retained (retaining a truncation would not be verbatim).
            base_row["failure_state"] = "parse_error"
            transmission["result_state"] = "oversized_output"
            rows.append(base_row)
            continue
        assessed_at = _now()
        base_row.update(
            raw_output=raw_output,
            raw_output_sha256=substrate.text_digest(raw_output),
            assessed_at=assessed_at,
        )
        try:
            parsed = _parse_judge_output(raw_output, hit["abstract_text"])
        except (ValueError, TypeError):
            base_row["failure_state"] = "parse_error"
            transmission["result_state"] = "parse_error"
            rows.append(base_row)
            continue
        evidence = _evidence_row(
            plan, ledger_value, family, hit, parsed["quote"], assessed_at
        )
        evidence_rows.append(evidence)
        transmission["result_state"] = "performed"
        base_row.update(
            check_state="performed",
            stance=parsed["stance"],
            conditions_noted=parsed["conditions"],
            rationale=parsed["rationale"],
            evidence_row_refs=[
                {"row_id": evidence["row_id"], "row_sha256": evidence["row_sha256"]}
            ],
        )
        rows.append(base_row)

    distribution = {
        "denominator": "all_selected_work_families",
        "selected_total": len(rows),
        **_tally(rows),
    }

    record = {
        "schema_version": "claim-standing-stance-record/1.0",
        "probe_id": plan["probe_id"],
        "unmeasured_banner": UNMEASURED_BANNER,
        "advisory_boundary": {
            "layer": "LLM-ADVISORY",
            "gate_effect": "none",
            "read_ledger_effect": "none",
            "manuscript_mutation": "none",
        },
        "identity": {
            "claim_sha256": plan["claim"]["claim_sha256"],
            "consent_receipt_sha256": plan["consent"]["receipt_sha256"],
            "query_plan_sha256": plan["plan_sha256"],
            "adapter_registry_sha256": substrate.digest(plan["provider_roster"]),
            "candidate_ledger_sha256": ledger_value["candidate_ledger_sha256"],
            "stance_plan_sha256": substrate.digest(plan["stance_plan"]),
        },
        "stance_runtime": {
            "provider_identity": plan["stance_plan"]["provider_identity"],
            "model_identity": plan["stance_plan"]["model_identity"],
            "prompt_contract_version": PROMPT_CONTRACT_VERSION,
            "runtime_identity": transport.runtime_identity,
        },
        "rows": rows,
        "distribution": distribution,
        "completed_at": _now(),
    }
    record["stance_record_sha256"] = substrate.bound_digest(
        record, "stance_record_sha256"
    )
    _validate_schema(STANCE_RECORD_SCHEMA, record, "stance record")
    validate_stance_record(plan, ledger_value, record, evidence_rows)
    return record, evidence_rows, transmissions


def expected_identity(
    plan: dict[str, Any], ledger_value: dict[str, Any]
) -> dict[str, str]:
    """The §7 probe-identity hash set one (plan, ledger) pair binds.

    Single authority for the identity comparison used by the semantic
    validator and the freshness checker; adding a binding here extends both.
    """
    return {
        "claim_sha256": plan["claim"]["claim_sha256"],
        "consent_receipt_sha256": plan["consent"]["receipt_sha256"],
        "query_plan_sha256": plan["plan_sha256"],
        "adapter_registry_sha256": substrate.digest(plan["provider_roster"]),
        "candidate_ledger_sha256": substrate.bound_digest(
            ledger_value, "candidate_ledger_sha256"
        ),
        "stance_plan_sha256": substrate.digest(plan.get("stance_plan")),
    }


def validate_stance_record(
    plan: dict[str, Any],
    ledger_value: dict[str, Any],
    record: dict[str, Any],
    evidence_rows: list[dict[str, Any]],
) -> None:
    """The semantic verifier the stance-record contract names as required."""
    _require_stance_consent(plan)
    _require_bound_ledger(plan, ledger_value)
    _validate_schema(STANCE_RECORD_SCHEMA, record, "stance record")
    if record["stance_record_sha256"] != substrate.bound_digest(
        record, "stance_record_sha256"
    ):
        _fail("stance_record_sha256 does not bind the record")

    identity = record["identity"]
    expected = expected_identity(plan, ledger_value)
    for field, value in expected.items():
        if identity[field] != value:
            _fail(f"identity.{field} drifted: the record is stale (candidate_ledger, plan, or consent changed)")
    runtime = record["stance_runtime"]
    stance_plan = plan["stance_plan"]
    for field in ("provider_identity", "model_identity", "prompt_contract_version"):
        if runtime[field] != stance_plan[field]:
            _fail(
                f"stance_runtime.{field} does not match the consented "
                "stance_plan"
            )

    selected_ids = [
        family["work_family_id"] for family in _selected_families(ledger_value)
    ]
    row_ids = [row["work_family_id"] for row in record["rows"]]
    if row_ids != selected_ids:
        _fail(
            "rows must cover exactly the ledger's selected work families, "
            "once each, in work_family_id order"
        )
    ledger_families = {
        family["work_family_id"]: family
        for family in ledger_value["work_families"]
    }
    for row in record["rows"]:
        family = ledger_families[row["work_family_id"]]
        if row["canonical_raw_hit_id"] != family["canonical_raw_hit_id"]:
            _fail(
                f"row {row['work_family_id']}: canonical_raw_hit_id disagrees "
                "with the ledger family"
            )
        if row["evidence_scope"] != family["coverage"]:
            _fail(
                f"row {row['work_family_id']}: evidence_scope disagrees with "
                "the ledger family's coverage"
            )

    distribution = record["distribution"]
    for bucket, value in _tally(record["rows"]).items():
        if distribution[bucket] != value:
            _fail(f"distribution.{bucket} does not match the rows")
    if distribution["selected_total"] != len(record["rows"]):
        _fail("distribution.selected_total does not match the rows")

    hits_by_id = {hit["raw_hit_id"]: hit for hit in ledger_value["raw_hits"]}
    families_by_id = {
        family["work_family_id"]: family
        for family in ledger_value["work_families"]
    }
    rows_by_id = {}
    for row in evidence_rows:
        _validate_schema(EVIDENCE_ROW_SCHEMA, row, "evidence row")
        if row["row_sha256"] != substrate.bound_digest(row, "row_sha256"):
            _fail(f"evidence row {row['row_id']}: row_sha256 does not bind the row")
        if row["row_id"] in rows_by_id:
            _fail(f"duplicate evidence row id {row['row_id']}")
        rows_by_id[row["row_id"]] = row
    referenced: set[str] = set()
    for row in record["rows"]:
        for ref in row["evidence_row_refs"]:
            evidence = rows_by_id.get(ref["row_id"])
            if evidence is None:
                _fail(f"evidence row {ref['row_id']} is referenced but absent")
            if evidence["row_sha256"] != ref["row_sha256"]:
                _fail(
                    f"evidence row {ref['row_id']}: row_sha256 does not bind "
                    "the referenced row"
                )
            referenced.add(ref["row_id"])
            # Replay the evidence against the exact ledger candidate: a row
            # forged for another claim, candidate, or source cannot back a
            # stance row.
            claim = evidence["claim"]
            if (
                claim["claim_id"] != plan["claim"]["claim_id"]
                or claim["claim_sha256"] != plan["claim"]["claim_sha256"]
                or claim["probe_id"] != plan["probe_id"]
            ):
                _fail(f"evidence row {ref['row_id']}: claim binding drifted")
            candidate = evidence["candidate"]
            if candidate["candidate_ledger_sha256"] != ledger_value[
                "candidate_ledger_sha256"
            ]:
                _fail(f"evidence row {ref['row_id']}: ledger binding drifted")
            if (
                candidate["work_family_id"] != row["work_family_id"]
                or candidate["canonical_raw_hit_id"] != row["canonical_raw_hit_id"]
            ):
                _fail(
                    f"evidence row {ref['row_id']}: bound to a different "
                    "candidate than the stance row it backs"
                )
            family = families_by_id.get(row["work_family_id"])
            hit = hits_by_id.get(row["canonical_raw_hit_id"])
            if family is None or hit is None:
                _fail(f"evidence row {ref['row_id']}: candidate is not in the ledger")
            if evidence["coverage"] != row["evidence_scope"]:
                _fail(f"evidence row {ref['row_id']}: coverage disagrees with the stance row")
            if evidence["source"]["source_content_sha256"] != family["content_sha256"]:
                _fail(f"evidence row {ref['row_id']}: source hash disagrees with the ledger")
            if hit["abstract_text"] is not None and family[
                "content_sha256"
            ] != substrate.text_digest(hit["abstract_text"]):
                _fail(
                    f"evidence row {ref['row_id']}: ledger content hash does "
                    "not replay from the inspected bytes"
                )
            excerpt = evidence["excerpt"]
            if excerpt["state"] in ("verified_exact_match", "agent_extracted"):
                evidence_text = hit["abstract_text"]
                if evidence_text is None:
                    _fail(f"evidence row {ref['row_id']}: no inspected text exists")
                span = excerpt["source_span_utf8"]
                source_bytes = evidence_text.encode("utf-8")
                if (
                    span["end"] > len(source_bytes)
                    or span["start"] >= span["end"]
                    or evidence["source"]["source_content_utf8_bytes"]
                    != len(source_bytes)
                ):
                    _fail(f"evidence row {ref['row_id']}: span is out of bounds")
                try:
                    replay = source_bytes[span["start"] : span["end"]].decode("utf-8")
                except (UnicodeError, ValueError):
                    _fail(f"evidence row {ref['row_id']}: span does not replay")
                if replay != excerpt["text"]:
                    _fail(f"evidence row {ref['row_id']}: span does not replay the excerpt")
                if excerpt["excerpt_sha256"] != substrate.text_digest(excerpt["text"]):
                    _fail(f"evidence row {ref['row_id']}: excerpt_sha256 does not bind")
    orphans = sorted(set(rows_by_id) - referenced)
    if orphans:
        _fail(f"unreferenced evidence rows present: {orphans!r}")

    # Performed rows must replay from their retained raw output: a resealed
    # stance/rationale/conditions that the judge never produced cannot pass.
    # Symmetrically, a parse_error row whose retained output parses cleanly
    # is a downgrade forgery.
    for row in record["rows"]:
        if row["raw_output"] is not None and row[
            "raw_output_sha256"
        ] != substrate.text_digest(row["raw_output"]):
            _fail(
                f"row {row['work_family_id']}: raw_output_sha256 does not "
                "bind the retained output"
            )
        if row["check_state"] != "performed":
            hit = hits_by_id[row["canonical_raw_hit_id"]]
            if row["raw_output"] is not None and hit["abstract_text"] is not None:
                try:
                    _parse_judge_output(row["raw_output"], hit["abstract_text"])
                except (ValueError, TypeError):
                    pass
                else:
                    _fail(
                        f"row {row['work_family_id']}: retained output parses "
                        "cleanly; a not_checked state cannot stand"
                    )
            family = families_by_id[row["work_family_id"]]
            if family["content_state"] == "available":
                if row["failure_state"] == "abstract_missing":
                    _fail(
                        f"row {row['work_family_id']}: abstract_missing "
                        "contradicts the ledger's available content state"
                    )
                # A transport-reaching failure row still binds exactly what
                # was sent: its prompt hashes must replay from the frozen
                # template (the transmission cross-check depends on this).
                expected_prompt_sha = substrate.text_digest(
                    _stance_prompt(plan, family, hit)
                )
                if row["prompt_sha256"] != expected_prompt_sha:
                    _fail(
                        f"row {row['work_family_id']}: prompt_sha256 does "
                        "not replay from the frozen prompt template"
                    )
                if row["assessment_input_sha256"] != substrate.digest(
                    {
                        "claim_sha256": plan["claim"]["claim_sha256"],
                        "candidate_content_sha256": substrate.text_digest(
                            hit["abstract_text"]
                        ),
                        "prompt_contract_version": PROMPT_CONTRACT_VERSION,
                        "prompt_sha256": expected_prompt_sha,
                    }
                ):
                    _fail(
                        f"row {row['work_family_id']}: "
                        "assessment_input_sha256 does not replay"
                    )
            else:
                if row["failure_state"] != "abstract_missing":
                    _fail(
                        f"row {row['work_family_id']}: content-unavailable "
                        "candidates are never dispatched, so only "
                        "abstract_missing can stand"
                    )
                if row["prompt_sha256"] is not None or (
                    row["assessment_input_sha256"] is not None
                ):
                    _fail(
                        f"row {row['work_family_id']}: an undispatched row "
                        "cannot carry prompt hashes"
                    )
            continue
        family = families_by_id[row["work_family_id"]]
        hit = hits_by_id[row["canonical_raw_hit_id"]]
        try:
            parsed = _parse_judge_output(row["raw_output"], hit["abstract_text"])
        except (ValueError, TypeError) as exc:
            _fail(
                f"row {row['work_family_id']}: retained raw output does not "
                f"parse as a performed row ({exc})"
            )
        if (
            parsed["stance"] != row["stance"]
            or parsed["conditions"] != row["conditions_noted"]
            or parsed["rationale"] != row["rationale"]
        ):
            _fail(
                f"row {row['work_family_id']}: stance fields do not replay "
                "from the retained raw output"
            )
        expected_prompt = _stance_prompt(plan, family, hit)
        expected_prompt_sha = substrate.text_digest(expected_prompt)
        if row["prompt_sha256"] != expected_prompt_sha:
            _fail(
                f"row {row['work_family_id']}: prompt_sha256 does not replay "
                "from the frozen prompt template"
            )
        if row["assessment_input_sha256"] != substrate.digest(
            {
                "claim_sha256": plan["claim"]["claim_sha256"],
                "candidate_content_sha256": substrate.text_digest(
                    hit["abstract_text"]
                ),
                "prompt_contract_version": PROMPT_CONTRACT_VERSION,
                "prompt_sha256": expected_prompt_sha,
            }
        ):
            _fail(
                f"row {row['work_family_id']}: assessment_input_sha256 does "
                "not replay"
            )
        quoted = {ref["row_id"] for ref in row["evidence_row_refs"]}
        for ref_id in quoted:
            if rows_by_id[ref_id]["excerpt"]["text"] != parsed["quote"]:
                _fail(
                    f"row {row['work_family_id']}: evidence excerpt does not "
                    "replay from the retained raw output"
                )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    run_parser = commands.add_parser(
        "run", help="classify stance for every selected work family"
    )
    run_parser.add_argument("--query-plan", type=Path, required=True)
    parser_note = (
        "outputs are derived from the consent's authorized_output_path: "
        f"'<path>{STANCE_RECORD_SUFFIX}' and '<path>{EVIDENCE_ROWS_SUFFIX}'"
    )
    run_parser.description = parser_note
    args = parser.parse_args(argv)
    try:
        plan = substrate.load_json(args.query_plan)
        _require_stance_consent(plan)
        _fail(
            "no live stance transport is wired: this CLI is a placeholder "
            "until a stance provider adapter ships with its own consent "
            "surface; use run_stance() with an injected transport"
        )
    except (StanceError, substrate.LedgerError, OSError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
