#!/usr/bin/env python3
"""Offline-only execution envelope for #659.

The command set creates and validates files. It has no provider transport,
dispatch, probe, actor, subject, judge, or adjudicator execution path.
Externally recorded transcripts may be ingested only after a separately held
fresh authorization; this envelope never grants that authorization.
"""
from __future__ import annotations

import argparse
import base64
import copy
from datetime import datetime
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import stat
import sys
import unicodedata
from typing import Any, NoReturn

from jsonschema import Draft202012Validator, FormatChecker

import validate_ideation_diversity_assets as phase1


REPO_ROOT = Path(__file__).resolve().parents[1]
SUITE = "within_session_ideation_diversity"
SUITE_ROOT = REPO_ROOT / "evals" / "heldout" / SUITE
RUN_PLAN_SCHEMA = SUITE_ROOT / "run_plan.schema.json"
AUTHORIZATION_SCHEMA = SUITE_ROOT / "authorization_record.schema.json"
TRANSCRIPT_SCHEMA = SUITE_ROOT / "transcript.schema.json"
INGESTION_SCHEMA = SUITE_ROOT / "ingestion_manifest.schema.json"
STOP_INTENT_SCHEMA = SUITE_ROOT / "stop_intent.schema.json"
BLIND_PACKET_SCHEMA = SUITE_ROOT / "blind_packet.schema.json"
BLIND_INVENTORY_SCHEMA = SUITE_ROOT / "blind_inventory.schema.json"
BLIND_MANIFEST_SCHEMA = SUITE_ROOT / "blind_manifest.schema.json"
PRIVATE_ARM_MAP_SCHEMA = SUITE_ROOT / "private_arm_map.schema.json"
PRODUCTION_PROMPT = REPO_ROOT / "deep-research" / "agents" / "socratic_mentor_agent.md"
CODEBOOK = SUITE_ROOT / "codebook.md"
MAX_INPUT_BYTES = 4 * 1024 * 1024
MAX_STOP_INTENT_BYTES = 8 * 1024 * 1024
STOP_INTENT_REF = "stop-intent.json"
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
RUN_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]{2,79}$")
EXTERNAL_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{7,255}$")
STOP_RULES = [
    "prompt_or_role_card_hash_mismatch",
    "arm_leakage",
    "ineligible_session",
    "authorization_record_missing_or_mismatch",
    "unplanned_tool_action",
    "unplanned_network_action",
    "evidence_write_failure",
    "partial_subject_output",
    "actor_protocol_deviation",
    "out_of_order_ingestion",
    "transcript_contract_failure",
]
BLINDED_TO = [
    "mechanism",
    "arm",
    "pair_mapping",
    "replicate",
    "expected_direction",
    "other_transcripts",
    "aggregate",
    "prior_labels",
]
ARM_LEAK_TOKENS = (
    "adjacent_probe",
    "exploratory_guardrails",
    "ars_socratic_adjacent_probe",
    "paired transcript",
    "expected metric direction",
)
MESSAGE_EVENT_KINDS = {"actor_message", "subject_message"}
TERMINAL_EVENT_KINDS = {
    "session_started",
    "session_completed",
    "session_blocked",
    "session_partial",
    "tool_action",
    "network_action",
    "evidence_write_failure",
}
RAW_EVENT_KINDS = MESSAGE_EVENT_KINDS | TERMINAL_EVENT_KINDS
HUMAN_EVIDENCE_PATTERNS = (
    re.compile(
        r"\b(?:prior|human|judge|annotator|reviewer)\s+"
        r"(?:label|rating|decision|evidence)s?\b",
        re.IGNORECASE,
    ),
    re.compile(r"\badjudicat(?:e|ed|es|ing|ion|or|ors)\b", re.IGNORECASE),
    re.compile(
        r"\b(?:A[12]|M[1-5])\s*(?:=|:)?\s*"
        r"(?:yes|no|not_applicable)\b",
        re.IGNORECASE,
    ),
    re.compile(r"(?:真人|人類)(?:專家|評審|標註|裁決|證據)"),
    re.compile(r"(?:先前|既有|前輪)(?:標註|評分|裁決)"),
    re.compile(r"\b(?:gold[- ]standard\s+)?(?:coder|annotator|rater)\b", re.IGNORECASE),
    re.compile(r"\btie[- ]breaker\b", re.IGNORECASE),
    re.compile(r"(?:黃金標準|標註者|編碼者|評分者|裁決者)"),
)
MAPPING_LEAK_PATTERNS = (
    re.compile(r"\breplicate(?:\s+id)?\s*(?:=|:|#)?\s*[12]\b", re.IGNORECASE),
    re.compile(r"\b(?:cell|pair|arm|scenario|experiment)\s+id\s*(?:=|:)", re.IGNORECASE),
    re.compile(r"\bother transcripts?\b", re.IGNORECASE),
    re.compile(r"\b(?:adjacent[- ]probe|exploratory[- ]guardrails?)\b", re.IGNORECASE),
    re.compile(
        r"\b(?:treatment|control|experimental)\s+"
        r"(?:arm|condition|group)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:mechanism|feature|probe|guardrails?)\b.{0,24}"
        r"\b(?:enabled|disabled|ablated|on|off)\b",
        re.IGNORECASE,
    ),
    re.compile(
        r"\b(?:preceding|previous|prior|other|paired)\s+"
        r"(?:session|transcript|response)\b",
        re.IGNORECASE,
    ),
    re.compile(r"(?:處置|控制|實驗)(?:組|條件|臂)"),
    re.compile(r"(?:前一|先前|其他|配對)(?:場次|對話|逐字稿|回應)"),
)
EXPERIMENTS = (
    (
        "adjacent_probe",
        ("adjacent_probe_off", "adjacent_probe_on"),
    ),
    (
        "exploratory_guardrails",
        ("exploratory_guardrails_on", "exploratory_guardrails_ablated"),
    ),
)
ASSET_PATHS = (
    "docs/design/2026-08-13-659-within-session-ideation-diversity-design.md",
    "evals/heldout/within_session_ideation_diversity/README.md",
    "evals/heldout/within_session_ideation_diversity/heldout_set.json",
    "evals/heldout/within_session_ideation_diversity/heldout_set.schema.json",
    "evals/heldout/within_session_ideation_diversity/codebook.md",
    "evals/heldout/within_session_ideation_diversity/nonproduction_variant.json",
    "evals/heldout/within_session_ideation_diversity/run_plan.schema.json",
    "evals/heldout/within_session_ideation_diversity/authorization_record.schema.json",
    "evals/heldout/within_session_ideation_diversity/transcript.schema.json",
    "evals/heldout/within_session_ideation_diversity/ingestion_manifest.schema.json",
    "evals/heldout/within_session_ideation_diversity/stop_intent.schema.json",
    "evals/heldout/within_session_ideation_diversity/blind_packet.schema.json",
    "evals/heldout/within_session_ideation_diversity/blind_inventory.schema.json",
    "evals/heldout/within_session_ideation_diversity/blind_manifest.schema.json",
    "evals/heldout/within_session_ideation_diversity/private_arm_map.schema.json",
    "deep-research/agents/socratic_mentor_agent.md",
    "scripts/run_ideation_diversity_no_call.py",
)


class EnvelopeError(RuntimeError):
    """Closed no-call envelope failure."""


class StopViolation(EnvelopeError):
    """A transcript event that permanently stops the run."""

    def __init__(self, code: str, detail: str):
        super().__init__(detail)
        self.code = code
        self.detail = detail


def _fail(message: str) -> NoReturn:
    raise EnvelopeError(message)


def _reject_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ValueError(f"duplicate JSON key {key!r}")
        value[key] = item
    return value


def _strict_loads(raw: bytes) -> dict[str, Any]:
    try:
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_reject_pairs,
            parse_constant=lambda token: (_ for _ in ()).throw(
                ValueError(f"non-finite JSON value {token!r}")
            ),
        )
    except (UnicodeError, ValueError, json.JSONDecodeError) as exc:
        raise EnvelopeError(f"invalid strict JSON: {exc}") from exc
    if not isinstance(value, dict):
        _fail("JSON root must be an object")
    return value


def _canonical(value: Any) -> bytes:
    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, ValueError, UnicodeError) as exc:
        raise EnvelopeError(f"value is not canonical JSON: {exc}") from exc


def _json_bytes(value: Any) -> bytes:
    return _canonical(value) + b"\n"


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _read_file(path: Path, *, limit: int = MAX_INPUT_BYTES) -> bytes:
    try:
        if path.is_symlink() or not path.is_file():
            _fail(f"input must be a regular non-symlink file: {path}")
        before = path.stat()
        if before.st_size > limit:
            _fail(f"input exceeds {limit} bytes: {path}")
        raw = path.read_bytes()
        after = path.stat()
    except OSError as exc:
        raise EnvelopeError(f"cannot read {path}: {exc}") from exc
    if len(raw) != after.st_size or (
        before.st_dev,
        before.st_ino,
        before.st_size,
        before.st_mtime_ns,
    ) != (
        after.st_dev,
        after.st_ino,
        after.st_size,
        after.st_mtime_ns,
    ):
        _fail(f"input changed while being read: {path}")
    return raw


def _write_new(path: Path, raw: bytes, *, mode: int = 0o644) -> None:
    """Publish complete bytes exclusively without ever exposing a partial target."""
    temporary: Path | None = None
    descriptor: int | None = None
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary = path.with_name(
            f".{path.name}.atomic-write-{secrets.token_hex(12)}.tmp"
        )
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        descriptor = os.open(temporary, flags, mode)
        view = memoryview(raw)
        written = 0
        while written < len(view):
            count = os.write(descriptor, view[written:])
            if count <= 0:
                raise OSError("atomic staging write made no progress")
            written += count
        os.fsync(descriptor)
        os.close(descriptor)
        descriptor = None
        # A hard link is an atomic, exclusive publication: an existing target
        # is never replaced and readers can only observe complete staged bytes.
        os.link(temporary, path, follow_symlinks=False)
        _fsync_directory(path.parent)
    except FileExistsError as exc:
        raise EnvelopeError(f"refusing to overwrite {path}") from exc
    except OSError as exc:
        raise EnvelopeError(f"cannot create {path}: {exc}") from exc
    finally:
        if descriptor is not None:
            try:
                os.close(descriptor)
            except OSError:
                pass
        if temporary is not None and temporary.exists():
            try:
                temporary.unlink()
                _fsync_directory(temporary.parent)
            except OSError as exc:
                # A complete target may already be published, but an orphaned
                # staging name would violate the exact inventory contract.
                raise EnvelopeError(
                    f"cannot remove unpublished atomic staging file {temporary}: {exc}"
                ) from exc


def _fsync_directory(path: Path) -> None:
    flags = os.O_RDONLY
    if hasattr(os, "O_DIRECTORY"):
        flags |= os.O_DIRECTORY
    descriptor = os.open(path, flags)
    try:
        os.fsync(descriptor)
    finally:
        os.close(descriptor)


def _validate_run_tree(run_dir: Path) -> None:
    if run_dir.is_symlink() or not run_dir.is_dir():
        _fail(f"run directory must be a real non-symlink directory: {run_dir}")
    try:
        links = [path for path in run_dir.rglob("*") if path.is_symlink()]
    except OSError as exc:
        raise EnvelopeError(f"cannot inspect run directory {run_dir}: {exc}") from exc
    if links:
        _fail(f"run directory must not contain symlinks: {links[0]}")


def _replace_json(path: Path, value: dict[str, Any]) -> None:
    raw = _json_bytes(value)
    temporary = path.with_name(
        f".{path.name}.replace-{_sha(raw)[:24]}.json"
    )
    _ensure_exact_new(temporary, raw)
    try:
        os.replace(temporary, path)
        _fsync_directory(path.parent)
    except OSError as exc:
        # Keep the complete content-addressed staging bytes. A stopped-state
        # marker can replay this exact replacement; normal ingestion registers
        # the surviving file as pre-stop evidence.
        raise EnvelopeError(
            f"cannot atomically replace {path}; complete staging preserved at "
            f"{temporary}: {exc}"
        ) from exc


def _relative_files_and_directories(run_dir: Path) -> tuple[set[str], set[str]]:
    files: set[str] = set()
    directories: set[str] = set()
    try:
        for path in run_dir.rglob("*"):
            relative = str(path.relative_to(run_dir))
            if path.is_symlink():
                _fail(f"run directory must not contain symlinks: {path}")
            if path.is_file():
                files.add(relative)
            elif path.is_dir():
                directories.add(relative)
            else:
                _fail(f"run directory contains a non-file entry: {path}")
    except OSError as exc:
        raise EnvelopeError(f"cannot inventory run directory {run_dir}: {exc}") from exc
    return files, directories


def _parent_directories(refs: set[str]) -> set[str]:
    directories: set[str] = set()
    for ref in refs:
        parent = Path(ref).parent
        while str(parent) != ".":
            directories.add(str(parent))
            parent = parent.parent
    return directories


def _schema(path: Path) -> dict[str, Any]:
    schema = _strict_loads(_read_file(path))
    try:
        Draft202012Validator.check_schema(schema)
    except Exception as exc:
        raise EnvelopeError(f"invalid Draft 2020-12 schema {path}: {exc}") from exc
    return schema


def _validate_schema(path: Path, value: dict[str, Any], label: str) -> None:
    errors = sorted(
        Draft202012Validator(
            _schema(path), format_checker=FormatChecker()
        ).iter_errors(value),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        first = errors[0]
        location = "$" + "".join(f"[{part!r}]" for part in first.absolute_path)
        _fail(f"{label} schema failure at {location}: {first.message}")


def _timestamp(value: str, label: str) -> datetime:
    if not isinstance(value, str):
        _fail(f"invalid {label} date-time")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise EnvelopeError(f"invalid {label} date-time") from exc
    if parsed.tzinfo is None:
        _fail(f"{label} must include a UTC offset")
    return parsed


def _repo_path(ref: str) -> Path:
    path = Path(ref)
    if path.is_absolute() or ".." in path.parts or not ref:
        _fail(f"unsafe repository asset reference {ref!r}")
    return REPO_ROOT / path


def _asset_bindings() -> list[dict[str, str]]:
    return [
        {"path": ref, "sha256": _sha(_read_file(_repo_path(ref)))}
        for ref in ASSET_PATHS
    ]


def _scenario_index(heldout: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {row["scenario_id"]: row for row in heldout["scenarios"]}


def _actor_packet(cell_id: str, scenario: dict[str, Any], blind_fields: list[str]) -> dict[str, Any]:
    return {
        "schema_version": "ideation-diversity-actor-packet/1.0",
        "suite": SUITE,
        "actor_session_id": cell_id,
        "content_class": "repository-owned synthetic scholar role card",
        "blind_fields": blind_fields,
        "role_card": {
            key: scenario[key]
            for key in (
                "language",
                "domain",
                "role_brief",
                "initial_message",
                "owned_framings",
                "response_policy",
                "forbidden_out_of_role",
            )
        },
        "model_generated_actor": False,
    }


def _session_envelope(cell: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "ideation-diversity-session-envelope/1.0",
        "suite": SUITE,
        "cell_id": cell["cell_id"],
        "sequence_index": cell["sequence_index"],
        "prompt_path": cell["prompt"]["path"],
        "prompt_sha256": cell["prompt"]["sha256"],
        "environment": cell["prompt"]["environment"],
        "actor_packet_path": cell["actor_packet_path"],
        "actor_packet_sha256": cell["actor_packet_sha256"],
        "fresh_context_required": True,
        "tools": [],
        "web_enabled": False,
        "runner_transport": "none",
        "dispatch_available": False,
        "api_spend_ceiling_usd": 0,
        "api_fallback": False,
        "envelope_grants_consent": False,
        "fresh_external_authorization_required": True,
    }


def _prompt_binding(arm_id: str, production_sha: str, variant_sha: str) -> dict[str, Any]:
    if arm_id == "adjacent_probe_on":
        return {
            "kind": "production",
            "path": "materials/prompts/production-socratic-mentor.md",
            "sha256": production_sha,
            "environment": {"ARS_SOCRATIC_ADJACENT_PROBE": "1"},
        }
    if arm_id == "exploratory_guardrails_ablated":
        return {
            "kind": "nonproduction_ablation",
            "path": "materials/prompts/exploratory-guardrails-ablated.md",
            "sha256": variant_sha,
            "environment": {},
        }
    return {
        "kind": "production",
        "path": "materials/prompts/production-socratic-mentor.md",
        "sha256": production_sha,
        "environment": {},
    }


def _ordered_assignments(seed: str, scenarios: list[dict[str, Any]]) -> list[tuple[str, str, dict[str, Any], int, int]]:
    blocks: list[tuple[str, tuple[str, str], dict[str, Any]]] = []
    for experiment_id, arms in EXPERIMENTS:
        for scenario in scenarios:
            blocks.append((experiment_id, arms, scenario))
    blocks.sort(
        key=lambda block: _sha(
            f"{seed}\0{block[0]}\0{block[2]['scenario_id']}".encode("utf-8")
        )
    )
    assignments: list[tuple[str, str, dict[str, Any], int, int]] = []
    for block_index, (experiment_id, arms, scenario) in enumerate(blocks, 1):
        orientation = int(
            _sha(f"{seed}\0orientation\0{experiment_id}\0{scenario['scenario_id']}".encode()),
            16,
        ) % 2
        first = arms if orientation == 0 else tuple(reversed(arms))
        for replicate, arm_order in ((1, first), (2, tuple(reversed(first)))):
            for arm_id in arm_order:
                assignments.append(
                    (experiment_id, arm_id, scenario, replicate, block_index)
                )
    return assignments


def _build_plan(config: dict[str, Any]) -> dict[str, Any]:
    heldout, variant = phase1.load_assets()
    production_raw = _read_file(PRODUCTION_PROMPT)
    rendered_raw = phase1.render_variant(variant).encode("utf-8")
    production_sha = _sha(production_raw)
    variant_sha = _sha(rendered_raw)
    cells: list[dict[str, Any]] = []
    for sequence_index, assignment in enumerate(
        _ordered_assignments(config["order_seed"], heldout["scenarios"]), 1
    ):
        experiment_id, arm_id, scenario, replicate, block_index = assignment
        cell_id = f"cell-{sequence_index:03d}"
        scenario_sha = _sha(_canonical(scenario))
        actor_packet_path = f"materials/actor-packets/{cell_id}.json"
        actor_packet = _actor_packet(
            cell_id, scenario, heldout["actor_blind_fields"]
        )
        cell: dict[str, Any] = {
            "cell_id": cell_id,
            "sequence_index": sequence_index,
            "experiment_id": experiment_id,
            "arm_id": arm_id,
            "scenario_id": scenario["scenario_id"],
            "pair_id": scenario["pair_id"],
            "language": scenario["language"],
            "replicate": replicate,
            "actor_block_id": f"actor-block-{block_index:02d}-r{replicate}",
            "prompt": _prompt_binding(arm_id, production_sha, variant_sha),
            "scenario_sha256": scenario_sha,
            "initial_message_sha256": _sha(scenario["initial_message"].encode("utf-8")),
            "actor_packet_path": actor_packet_path,
            "actor_packet_sha256": _sha(_json_bytes(actor_packet)),
            "session_envelope_path": f"materials/session-envelopes/{cell_id}.json",
            "session_envelope_sha256": "0" * 64,
            "fresh_context_required": True,
        }
        cell["session_envelope_sha256"] = _sha(_json_bytes(_session_envelope(cell)))
        cells.append(cell)
    cell_ids = [cell["cell_id"] for cell in cells]
    order_projection = [
        {
            "cell_id": cell["cell_id"],
            "sequence_index": cell["sequence_index"],
            "experiment_id": cell["experiment_id"],
            "scenario_id": cell["scenario_id"],
            "arm_id": cell["arm_id"],
            "replicate": cell["replicate"],
            "actor_block_id": cell["actor_block_id"],
        }
        for cell in cells
    ]
    return {
        "schema_version": "ideation-diversity-run-plan/1.0",
        "suite": SUITE,
        "phase": "phase_2_no_call_execution_envelope",
        "status": "frozen_no_call",
        "run_id": config["run_id"],
        "suite_commit": config["suite_commit"],
        "suite_commit_provenance": {
            "status": "operator_declared_unverified",
            "verified_by_no_call_runner": False,
            "verifiable_authority": "run_plan_sha256_and_asset_bindings",
        },
        "content_class": "repository-owned synthetic scholar role cards",
        "created_without_dispatch": True,
        "asset_bindings": _asset_bindings(),
        "rendered_variant_sha256": variant_sha,
        "execution": {
            "subject_provider": config["subject_provider"],
            "subject_model": config["subject_model"],
            "subject_runtime": config["subject_runtime"],
            "subject_runtime_version": config["subject_runtime_version"],
            "auth_mode": config["auth_mode"],
            "reasoning_effort": config["reasoning_effort"],
            "input_token_cap": config["input_token_cap"],
            "output_token_cap": config["output_token_cap"],
            "token_cap_verification": {
                "status": "operator_declared_unverified",
                "enforced_by_no_call_runner": False,
                "observed_usage_recorded": False,
                "provider_tokenizer_verified": False,
            },
            "tools": [],
            "web_enabled": False,
            "runner_transport": "none",
            "dispatch_available": False,
            "api_spend_ceiling_usd": 0,
            "api_fallback": False,
            "envelope_grants_consent": False,
            "fresh_external_authorization_required": True,
        },
        "design": {
            "experiments": 2,
            "scenarios": 6,
            "arms_per_experiment": 2,
            "replicates_per_scenario_arm": 2,
            "subject_session_cells": 48,
            "fresh_context_per_cell": True,
            "adaptive_actor_forbidden": True,
            "model_generated_actor_forbidden": True,
        },
        "order": {
            "algorithm": "sha256-balanced-block-v1",
            "seed": config["order_seed"],
            "block_count": 12,
            "cell_ids": cell_ids,
            "order_sha256": _sha(_canonical(order_projection)),
        },
        "cells": cells,
        "stop_rules": STOP_RULES,
        "judge_requirements": {
            "minimum_independent_judges": 2,
            "separate_arm_blind_adjudicator_required": True,
            "raw_labels_must_be_retained": True,
            "human_evidence_may_not_be_fabricated": True,
            "packet_contains_no_labels": True,
            "first_round_assignment_ledger_required_before_delivery": True,
            "same_role_card_cross_arm_or_replicate_exposure_forbidden": True,
            "bundle_alone_proves_judge_exposure_blindness": False,
        },
    }


def _config_from_plan(plan: dict[str, Any]) -> dict[str, Any]:
    execution = plan["execution"]
    return {
        "run_id": plan["run_id"],
        "suite_commit": plan["suite_commit"],
        "order_seed": plan["order"]["seed"],
        "subject_provider": execution["subject_provider"],
        "subject_model": execution["subject_model"],
        "subject_runtime": execution["subject_runtime"],
        "subject_runtime_version": execution["subject_runtime_version"],
        "auth_mode": execution["auth_mode"],
        "reasoning_effort": execution["reasoning_effort"],
        "input_token_cap": execution["input_token_cap"],
        "output_token_cap": execution["output_token_cap"],
    }


def _validate_authorization_record(
    record: dict[str, Any],
    plan: dict[str, Any],
    plan_sha: str,
) -> None:
    _validate_schema(AUTHORIZATION_SCHEMA, record, "authorization record")
    expected = {
        "run_plan_sha256": plan_sha,
        "run_id": plan["run_id"],
        "suite_commit": plan["suite_commit"],
        "suite_commit_provenance": plan["suite_commit_provenance"],
        "execution": plan["execution"],
    }
    for key, value in expected.items():
        if record[key] != value:
            _fail(f"authorization record {key} differs from frozen run plan")
    scope = record["scope"]
    if scope["cell_ids"] != plan["order"]["cell_ids"]:
        _fail("authorization record is not scoped to the exact ordered 48 cells")
    if scope["order_sha256"] != plan["order"]["order_sha256"]:
        _fail("authorization record order hash differs from frozen run plan")
    if record["decision"]["status"] != "authorized":
        _fail("authorization record decision is not authorized")
    _timestamp(record["decision"]["decided_at"], "authorization decided_at")


def _validate_plan(plan: dict[str, Any]) -> None:
    _validate_schema(RUN_PLAN_SCHEMA, plan, "run plan")
    expected = _build_plan(_config_from_plan(plan))
    if _canonical(plan) != _canonical(expected):
        _fail("run plan differs from the exact current asset/order/hash expansion")
    cells = plan["cells"]
    if len({cell["cell_id"] for cell in cells}) != 48:
        _fail("run plan cell ids must be unique")
    observed = {
        (
            cell["experiment_id"],
            cell["scenario_id"],
            cell["arm_id"],
            cell["replicate"],
        )
        for cell in cells
    }
    expected_cross_product = {
        (experiment, scenario["scenario_id"], arm, replicate)
        for experiment, arms in EXPERIMENTS
        for scenario in phase1.load_assets()[0]["scenarios"]
        for arm in arms
        for replicate in (1, 2)
    }
    if observed != expected_cross_product:
        _fail("run plan is not the exact 2 x 6 x 2 x 2 cross-product")
    for experiment, arms in EXPERIMENTS:
        for scenario in phase1.load_assets()[0]["scenarios"]:
            rows = [
                cell
                for cell in cells
                if cell["experiment_id"] == experiment
                and cell["scenario_id"] == scenario["scenario_id"]
            ]
            orders = [
                [cell["arm_id"] for cell in rows if cell["replicate"] == replicate]
                for replicate in (1, 2)
            ]
            if len(orders[0]) != 2 or orders[1] != list(reversed(orders[0])):
                _fail(f"arm order is not counterbalanced for {experiment}/{scenario['scenario_id']}")


def _initial_manifest(plan: dict[str, Any], plan_sha: str) -> dict[str, Any]:
    return {
        "schema_version": "ideation-diversity-ingestion-manifest/1.0",
        "suite": SUITE,
        "run_plan_sha256": plan_sha,
        "authorization_record_path": None,
        "authorization_record_sha256": None,
        "blind_manifest_ref": None,
        "blind_manifest_sha256": None,
        "status": "initialized",
        "next_sequence_index": 1,
        "stopped": False,
        "stop_receipt": None,
        "cells": [
            {
                "cell_id": cell["cell_id"],
                "sequence_index": cell["sequence_index"],
                "status": "pending",
                "transcript_ref": None,
                "transcript_sha256": None,
                "ingestion_receipt_ref": None,
            }
            for cell in plan["cells"]
        ],
    }


def _validate_manifest(manifest: dict[str, Any], plan: dict[str, Any], plan_sha: str) -> None:
    _validate_schema(INGESTION_SCHEMA, manifest, "ingestion manifest")
    if manifest["run_plan_sha256"] != plan_sha:
        _fail("ingestion manifest is bound to a different run plan")
    authorization_bound = (
        manifest["authorization_record_path"] is not None,
        manifest["authorization_record_sha256"] is not None,
    )
    if authorization_bound not in {(False, False), (True, True)}:
        _fail("authorization-record manifest fields must be both null or both bound")
    blind_bound = (
        manifest["blind_manifest_ref"] is not None,
        manifest["blind_manifest_sha256"] is not None,
    )
    if blind_bound not in {(False, False), (True, True)}:
        _fail("blind-manifest fields must be both null or both bound")
    pairs = [(row["cell_id"], row["sequence_index"]) for row in manifest["cells"]]
    expected = [(row["cell_id"], row["sequence_index"]) for row in plan["cells"]]
    if pairs != expected:
        _fail("ingestion manifest cell order differs from run plan")
    rows = manifest["cells"]
    ingested = sum(row["status"] == "ingested" for row in rows)
    if ingested and authorization_bound != (True, True):
        _fail("ingested transcripts require a preserved authorization record")
    if manifest["next_sequence_index"] != ingested + 1:
        _fail("ingestion manifest next_sequence_index is inconsistent")
    if manifest["stopped"] != (manifest["status"] == "stopped"):
        _fail("ingestion stopped/status fields disagree")
    for index, row in enumerate(rows):
        if index < ingested:
            expected_status = "ingested"
        elif manifest["stopped"] and index == ingested:
            expected_status = "blocked"
        else:
            expected_status = "pending"
        if row["status"] != expected_status:
            _fail("ingestion manifest states must form an exact append-only prefix")
        populated = (
            row["transcript_ref"] is not None,
            row["transcript_sha256"] is not None,
            row["ingestion_receipt_ref"] is not None,
        )
        expected_populated = {
            "pending": (False, False, False),
            "ingested": (True, True, True),
            "blocked": (True, True, False),
        }[row["status"]]
        if populated != expected_populated:
            _fail(f"ingestion manifest references disagree for {row['cell_id']}")
        if row["status"] == "ingested" and (
            row["transcript_ref"], row["ingestion_receipt_ref"]
        ) != (
            f"transcripts/{row['cell_id']}.json",
            f"receipts/{row['cell_id']}.json",
        ):
            _fail(f"ingested artifact paths drifted for {row['cell_id']}")
        if row["status"] == "blocked":
            base_ref = (
                f"blocked/{row['cell_id']}.transcript."
                f"{row['transcript_sha256']}.raw"
            )
            if row["transcript_ref"] != base_ref and not row[
                "transcript_ref"
            ].startswith(base_ref + ".collision-"):
                _fail(f"blocked evidence path drifted for {row['cell_id']}")
    state = manifest["status"]
    if state in {"initialized", "materialized"} and ingested != 0:
        _fail(f"{state} manifest cannot contain ingested cells")
    if state == "ingesting" and not 1 <= ingested <= 47:
        _fail("ingesting manifest must contain 1 through 47 ingested cells")
    if state in {"complete", "blind_finalized"} and ingested != 48:
        _fail(f"{state} manifest must contain 48 ingested cells")
    if state == "stopped":
        if ingested >= 48:
            _fail("stopped manifest requires one remaining blocked cell")
        if manifest["stop_receipt"] is None:
            _fail("stopped manifest requires one stop receipt")
        blocked = rows[ingested]
        receipt = manifest["stop_receipt"]
        if (
            receipt["cell_id"],
            receipt["sequence_index"],
            receipt["raw_ref"],
            receipt["raw_sha256"],
        ) != (
            blocked["cell_id"],
            blocked["sequence_index"],
            blocked["transcript_ref"],
            blocked["transcript_sha256"],
        ):
            _fail("stop receipt is not bound to the single blocked cell")
        if receipt["stop_intent_ref"] != STOP_INTENT_REF:
            _fail("stopped manifest is not bound to the durable stop intent")
    elif manifest["stop_receipt"] is not None:
        _fail("unstopped manifest must not contain a stop receipt")
    if state == "blind_finalized":
        if blind_bound != (True, True):
            _fail("blind_finalized manifest requires a bound blind manifest")
        if manifest["blind_manifest_ref"] != "blind/manifest.json":
            _fail("blind manifest path drifted")
    elif blind_bound != (False, False):
        _fail("only blind_finalized state may bind blind artifacts")


def _expected_run_inventory(
    run_dir: Path, plan: dict[str, Any], manifest: dict[str, Any]
) -> tuple[set[str], set[str]]:
    files = {"run-plan.json", "ingestion-manifest.json"}
    if manifest["status"] != "initialized":
        files.update(_material_map(plan))
    if manifest["authorization_record_path"] is not None:
        files.add(manifest["authorization_record_path"])
    for row in manifest["cells"]:
        if row["transcript_ref"] is not None:
            files.add(row["transcript_ref"])
        if row["ingestion_receipt_ref"] is not None:
            files.add(row["ingestion_receipt_ref"])
    if manifest["stop_receipt"] is not None:
        files.add(STOP_INTENT_REF)
        files.update(
            row["ref"]
            for row in manifest["stop_receipt"]["preserved_auxiliary_artifacts"]
        )
    if manifest["status"] == "blind_finalized":
        blind_manifest_raw = _read_file(run_dir / "blind/manifest.json")
        blind_manifest = _strict_loads(blind_manifest_raw)
        files.update(
            {
                "blind/manifest.json",
                blind_manifest["inventory_ref"],
                blind_manifest["private_map_ref"],
            }
        )
        files.update(row["packet_ref"] for row in blind_manifest["packets"])
    return files, _parent_directories(files)


def _validate_run_inventory(
    run_dir: Path,
    plan: dict[str, Any],
    manifest: dict[str, Any],
) -> None:
    expected_files, expected_directories = _expected_run_inventory(
        run_dir, plan, manifest
    )
    observed_files, observed_directories = _relative_files_and_directories(run_dir)
    if observed_files != expected_files:
        unexpected = sorted(observed_files - expected_files)
        missing = sorted(expected_files - observed_files)
        _fail(
            "run file inventory drifted; "
            f"unexpected={unexpected[:3]!r}, missing={missing[:3]!r}"
        )
    if observed_directories != expected_directories:
        unexpected = sorted(observed_directories - expected_directories)
        missing = sorted(expected_directories - observed_directories)
        _fail(
            "run directory inventory drifted; "
            f"unexpected={unexpected[:3]!r}, missing={missing[:3]!r}"
        )


def _decode_base64(value: str, label: str) -> bytes:
    try:
        decoded = base64.b64decode(value.encode("ascii"), validate=True)
    except (UnicodeError, ValueError) as exc:
        raise EnvelopeError(f"invalid {label} base64") from exc
    if base64.b64encode(decoded).decode("ascii") != value:
        _fail(f"non-canonical {label} base64")
    return decoded


def _validate_stop_intent(
    raw: bytes,
    plan: dict[str, Any],
    plan_sha: str,
) -> tuple[dict[str, Any], dict[str, Any], bytes, bytes]:
    marker = _strict_loads(raw)
    if raw != _json_bytes(marker):
        _fail("stop intent is not canonical write-once replay bytes")
    _validate_schema(STOP_INTENT_SCHEMA, marker, "stop intent")
    if marker["run_plan_sha256"] != plan_sha:
        _fail("stop intent is bound to a different run plan")
    stopped_raw = _decode_base64(
        marker["stopped_manifest_base64"], "stopped manifest"
    )
    if _sha(stopped_raw) != marker["stopped_manifest_sha256"]:
        _fail("stop intent stopped-manifest hash drift")
    stopped = _strict_loads(stopped_raw)
    if stopped_raw != _json_bytes(stopped):
        _fail("stop intent stopped manifest is not canonical replay bytes")
    _validate_manifest(stopped, plan, plan_sha)
    raw_evidence = _decode_base64(marker["raw_base64"], "blocked raw evidence")
    if _sha(raw_evidence) != marker["raw_sha256"]:
        _fail("stop intent blocked-raw hash drift")
    receipt = stopped["stop_receipt"]
    bound = (
        marker["cell_id"],
        marker["sequence_index"],
        marker["reason_code"],
        marker["detail"],
        marker["raw_ref"],
        marker["raw_sha256"],
    )
    replayed = (
        receipt["cell_id"],
        receipt["sequence_index"],
        receipt["reason_code"],
        receipt["detail"],
        receipt["raw_ref"],
        receipt["raw_sha256"],
    )
    if bound != replayed:
        _fail("stop intent fields drifted from the stopped-manifest replay")
    return marker, stopped, stopped_raw, raw_evidence


def _ensure_exact_new(path: Path, raw: bytes) -> None:
    if path.exists():
        if _read_file(path, limit=max(MAX_INPUT_BYTES, len(raw))) != raw:
            _fail(f"write-once evidence collision at {path}")
        return
    _write_new(path, raw)


def _recover_stop_intent(
    run_dir: Path,
    plan: dict[str, Any],
    plan_sha: str,
    current_manifest_raw: bytes,
) -> tuple[dict[str, Any], bytes]:
    marker_raw = _read_file(
        run_dir / STOP_INTENT_REF, limit=MAX_STOP_INTENT_BYTES
    )
    marker, stopped, stopped_raw, raw_evidence = _validate_stop_intent(
        marker_raw, plan, plan_sha
    )
    current_sha = _sha(current_manifest_raw)
    if current_manifest_raw == stopped_raw:
        pass
    elif current_sha == marker["prior_manifest_sha256"]:
        try:
            _ensure_exact_new(run_dir / marker["raw_ref"], raw_evidence)
            _replace_json(run_dir / "ingestion-manifest.json", stopped)
        except EnvelopeError as exc:
            raise EnvelopeError(
                "durable stop intent forbids retry; stopped-state recovery is "
                f"still pending: {exc}"
            ) from exc
        current_manifest_raw = _read_file(run_dir / "ingestion-manifest.json")
        if current_manifest_raw != stopped_raw:
            _fail("durable stop recovery did not publish exact stopped state")
    else:
        _fail("manifest drifted from both pre-stop and durable stopped state")
    try:
        _ensure_exact_new(run_dir / marker["raw_ref"], raw_evidence)
    except EnvelopeError as exc:
        raise EnvelopeError(
            "durable stop intent forbids retry; blocked transcript hash drift or "
            f"evidence recovery failure: {exc}"
        ) from exc
    return stopped, stopped_raw


def _load_run(run_dir: Path, expected_sha: str | None = None) -> tuple[dict[str, Any], bytes, str, dict[str, Any]]:
    _validate_run_tree(run_dir)
    plan_raw = _read_file(run_dir / "run-plan.json")
    plan_sha = _sha(plan_raw)
    if expected_sha is not None and expected_sha != plan_sha:
        _fail("--plan-sha256 does not match frozen run-plan bytes")
    plan = _strict_loads(plan_raw)
    _validate_plan(plan)
    manifest_raw = _read_file(run_dir / "ingestion-manifest.json")
    if (run_dir / STOP_INTENT_REF).exists():
        manifest, manifest_raw = _recover_stop_intent(
            run_dir, plan, plan_sha, manifest_raw
        )
    else:
        manifest = _strict_loads(manifest_raw)
    _validate_manifest(manifest, plan, plan_sha)
    if manifest["stopped"] and not (run_dir / STOP_INTENT_REF).exists():
        _fail("stopped state is missing its durable write-once stop intent")
    return plan, plan_raw, plan_sha, manifest


def init_run(args: argparse.Namespace) -> dict[str, Any]:
    if args.run_dir.exists():
        _fail(f"run directory already exists: {args.run_dir}")
    config = {
        "run_id": args.run_id,
        "suite_commit": args.suite_commit,
        "order_seed": args.order_seed,
        "subject_provider": args.subject_provider,
        "subject_model": args.subject_model,
        "subject_runtime": args.subject_runtime,
        "subject_runtime_version": args.subject_runtime_version,
        "auth_mode": args.auth_mode,
        "reasoning_effort": args.reasoning_effort,
        "input_token_cap": args.input_token_cap,
        "output_token_cap": args.output_token_cap,
    }
    if RUN_ID_RE.fullmatch(args.run_id) is None:
        _fail("--run-id has invalid syntax")
    if COMMIT_RE.fullmatch(args.suite_commit) is None:
        _fail("--suite-commit must be 40 lowercase hex characters")
    plan = _build_plan(config)
    _validate_plan(plan)
    plan_raw = _json_bytes(plan)
    plan_sha = _sha(plan_raw)
    args.run_dir.mkdir(parents=True)
    _validate_run_tree(args.run_dir)
    _write_new(args.run_dir / "run-plan.json", plan_raw)
    manifest = _initial_manifest(plan, plan_sha)
    _validate_manifest(manifest, plan, plan_sha)
    _write_new(args.run_dir / "ingestion-manifest.json", _json_bytes(manifest))
    return {"run_plan_sha256": plan_sha, "cells": 48, "dispatch_available": False}


def _material_map(plan: dict[str, Any]) -> dict[str, bytes]:
    heldout, variant = phase1.load_assets()
    scenarios = _scenario_index(heldout)
    values: dict[str, bytes] = {
        "materials/prompts/production-socratic-mentor.md": _read_file(PRODUCTION_PROMPT),
        "materials/prompts/exploratory-guardrails-ablated.md": phase1.render_variant(variant).encode("utf-8"),
    }
    for cell in plan["cells"]:
        scenario = scenarios[cell["scenario_id"]]
        actor_packet = _actor_packet(
            cell["cell_id"], scenario, heldout["actor_blind_fields"]
        )
        values[cell["actor_packet_path"]] = _json_bytes(actor_packet)
        values[cell["session_envelope_path"]] = _json_bytes(_session_envelope(cell))
    return values


def _validate_materials(run_dir: Path, plan: dict[str, Any], required: bool) -> None:
    expected = _material_map(plan)
    material_root = run_dir / "materials"
    if not material_root.exists():
        if required:
            _fail("materials have not been materialized")
        return
    for ref, raw in expected.items():
        actual = _read_file(run_dir / ref)
        if actual != raw:
            _fail(f"material bytes drifted: {ref}")
    expected_refs = set(expected)
    observed_refs = {
        str(path.relative_to(run_dir))
        for path in material_root.rglob("*")
        if path.is_file()
    }
    if observed_refs != expected_refs:
        _fail("material file inventory is not the exact frozen set")


def materialize(args: argparse.Namespace) -> dict[str, Any]:
    plan, _, plan_sha, manifest = _load_run(args.run_dir, args.plan_sha256)
    _validate_run_inventory(args.run_dir, plan, manifest)
    if manifest["status"] != "initialized":
        _fail("materialize is allowed exactly once from initialized state")
    if (args.run_dir / "materials").exists():
        _fail("refusing to overwrite existing materials")
    for ref, raw in _material_map(plan).items():
        _write_new(args.run_dir / ref, raw)
    _validate_materials(args.run_dir, plan, required=True)
    manifest["status"] = "materialized"
    _validate_manifest(manifest, plan, plan_sha)
    _replace_json(args.run_dir / "ingestion-manifest.json", manifest)
    return {"materialized_files": 98, "cells": 48, "dispatch_available": False}


def _closed_embedded_object(
    raw_utf8: str,
    declared_sha256: str,
    label: str,
) -> dict[str, Any]:
    raw = raw_utf8.encode("utf-8")
    if _sha(raw) != declared_sha256:
        _fail(f"{label} hash mismatch")
    value = _strict_loads(raw)
    if raw != _canonical(value):
        _fail(f"{label} must use exact canonical JSON bytes")
    return value


def _normalize_raw_event(event: dict[str, Any]) -> dict[str, Any]:
    try:
        normalized = _closed_embedded_object(
            event["raw_event_utf8"],
            event["raw_event_sha256"],
            f"raw event {event['event_index']}",
        )
    except EnvelopeError as exc:
        raise StopViolation("transcript_contract_failure", str(exc)) from exc
    event_kind = normalized.get("event_kind")
    if not isinstance(event_kind, str) or event_kind not in RAW_EVENT_KINDS:
        raise StopViolation(
            "transcript_contract_failure",
            f"raw event {event['event_index']} has an unknown action classification",
        )
    expected_keys = (
        {"event_kind", "turn_index", "text"}
        if event_kind in MESSAGE_EVENT_KINDS
        else {"event_kind", "turn_index"}
    )
    if set(normalized) != expected_keys:
        raise StopViolation(
            "transcript_contract_failure",
            f"raw event {event['event_index']} is not a closed normalized event",
        )
    turn_index = normalized["turn_index"]
    if turn_index is not None and type(turn_index) is not int:
        raise StopViolation(
            "transcript_contract_failure",
            f"raw event {event['event_index']} has an invalid turn index type",
        )
    raw_stop_codes = {
        "tool_action": "unplanned_tool_action",
        "network_action": "unplanned_network_action",
        "evidence_write_failure": "evidence_write_failure",
        "session_blocked": "partial_subject_output",
        "session_partial": "partial_subject_output",
    }
    if event_kind in raw_stop_codes:
        raise StopViolation(
            raw_stop_codes[event_kind],
            f"raw event stream reports stop condition {event_kind}",
        )
    if normalized["event_kind"] != event["event_kind"] or normalized[
        "turn_index"
    ] != event["turn_index"]:
        raise StopViolation(
            "transcript_contract_failure",
            f"raw event {event['event_index']} disagrees with normalized fields",
        )
    if event_kind in MESSAGE_EVENT_KINDS:
        if not isinstance(normalized["text"], str) or not normalized["text"]:
            raise StopViolation(
                "transcript_contract_failure",
                f"raw message event {event['event_index']} has no exact text bytes",
            )
    elif normalized["turn_index"] is not None:
        raise StopViolation(
            "transcript_contract_failure",
            f"non-message raw event {event['event_index']} claims a turn",
        )
    return normalized


def _external_session_receipt(
    transcript: dict[str, Any], expected: dict[str, Any]
) -> dict[str, Any]:
    source = transcript["source"]
    try:
        receipt = _closed_embedded_object(
            source["external_session_receipt_utf8"],
            source["external_session_receipt_sha256"],
            "external session receipt",
        )
    except EnvelopeError as exc:
        raise StopViolation("transcript_contract_failure", str(exc)) from exc
    required = {
        "receipt_id",
        "external_session_id",
        "cell_id",
        "sequence_index",
        "started_at",
        "completed_at",
        "fresh_context",
    }
    if set(receipt) != required:
        raise StopViolation(
            "transcript_contract_failure",
            "external session receipt is not a closed exact record",
        )
    if not (
        isinstance(receipt["cell_id"], str)
        and type(receipt["sequence_index"]) is int
        and type(receipt["fresh_context"]) is bool
        and isinstance(receipt["started_at"], str)
        and isinstance(receipt["completed_at"], str)
    ):
        raise StopViolation(
            "transcript_contract_failure",
            "external session receipt field types are invalid",
        )
    if (
        receipt["cell_id"],
        receipt["sequence_index"],
        receipt["fresh_context"],
    ) != (expected["cell_id"], expected["sequence_index"], True):
        raise StopViolation(
            "out_of_order_ingestion",
            "external session receipt is not bound to the next fresh-context cell",
        )
    if not all(
        isinstance(receipt[key], str)
        and EXTERNAL_ID_RE.fullmatch(receipt[key]) is not None
        for key in ("receipt_id", "external_session_id")
    ):
        raise StopViolation(
            "transcript_contract_failure",
            "external session receipt identifiers are invalid",
        )
    started = _timestamp(receipt["started_at"], "external session started_at")
    completed = _timestamp(receipt["completed_at"], "external session completed_at")
    if started > completed:
        raise StopViolation(
            "transcript_contract_failure",
            "external session receipt starts after it completes",
        )
    if transcript["session"]["fresh_context"] is not True:
        raise StopViolation(
            "partial_subject_output",
            "transcript and external receipt do not attest a fresh context",
        )
    return receipt


def _receipt_value(
    plan_sha: str,
    cell: dict[str, Any],
    transcript_ref: str,
    transcript_raw: bytes,
    transcript: dict[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": "ideation-diversity-ingestion-receipt/1.0",
        "suite": SUITE,
        "run_plan_sha256": plan_sha,
        "cell_id": cell["cell_id"],
        "sequence_index": cell["sequence_index"],
        "transcript_ref": transcript_ref,
        "transcript_sha256": _sha(transcript_raw),
        "authorization_record_ref": transcript["source"]["authorization_record_ref"],
        "authorization_record_sha256": transcript["source"][
            "authorization_record_sha256"
        ],
        "source_artifact_id": transcript["source"]["source_artifact_id"],
        "external_session_receipt_sha256": transcript["source"][
            "external_session_receipt_sha256"
        ],
        "accepted": True,
        "generated_evidence": False,
    }


def _validate_ingested_artifacts(
    run_dir: Path,
    plan: dict[str, Any],
    plan_sha: str,
    manifest: dict[str, Any],
    *,
    semantic: bool = True,
) -> dict[str, Any]:
    scenarios = _scenario_index(phase1.load_assets()[0]) if semantic else {}
    authorization: dict[str, Any] | None = None
    if manifest["authorization_record_path"] is not None:
        authorization_raw = _read_file(
            run_dir / manifest["authorization_record_path"]
        )
        if _sha(authorization_raw) != manifest["authorization_record_sha256"]:
            _fail("preserved authorization record hash drift")
        authorization = _strict_loads(authorization_raw)
        _validate_authorization_record(authorization, plan, plan_sha)
    seen_source_artifact_ids: set[str] = set()
    seen_external_receipt_ids: set[str] = set()
    seen_external_session_ids: set[str] = set()
    last_completed_at: datetime | None = None
    for cell, row in zip(plan["cells"], manifest["cells"]):
        if row["status"] == "blocked":
            raw = _read_file(run_dir / row["transcript_ref"])
            if _sha(raw) != row["transcript_sha256"]:
                _fail(f"blocked transcript hash drift: {row['cell_id']}")
            receipt = manifest["stop_receipt"]
            if receipt is None or (
                receipt["raw_ref"], receipt["raw_sha256"]
            ) != (row["transcript_ref"], _sha(raw)):
                _fail(f"blocked evidence receipt drift: {row['cell_id']}")
            for artifact in receipt["preserved_auxiliary_artifacts"]:
                auxiliary_raw = _read_file(run_dir / artifact["ref"])
                if _sha(auxiliary_raw) != artifact["sha256"]:
                    _fail(
                        "preserved pre-stop artifact hash drift: "
                        f"{artifact['ref']}"
                    )
                if artifact["role"] == "authorization_record":
                    _validate_authorization_record(
                        _strict_loads(auxiliary_raw), plan, plan_sha
                    )
            continue
        if row["status"] != "ingested":
            continue
        raw = _read_file(run_dir / row["transcript_ref"])
        if _sha(raw) != row["transcript_sha256"]:
            _fail(f"ingested transcript hash drift: {row['cell_id']}")
        transcript = _strict_loads(raw)
        if authorization is None or manifest["authorization_record_sha256"] != transcript["source"][
            "authorization_record_sha256"
        ]:
            _fail(f"transcript authorization binding drift: {row['cell_id']}")
        external_receipt = _external_session_receipt(transcript, cell)
        started_at = _timestamp(
            external_receipt["started_at"], "external session started_at"
        )
        completed_at = _timestamp(
            external_receipt["completed_at"], "external session completed_at"
        )
        if started_at < _timestamp(
            authorization["decision"]["decided_at"],
            "authorization decided_at",
        ):
            _fail(f"transcript predates authorization: {row['cell_id']}")
        identifiers = (
            (transcript["source"]["source_artifact_id"], seen_source_artifact_ids),
            (external_receipt["receipt_id"], seen_external_receipt_ids),
            (external_receipt["external_session_id"], seen_external_session_ids),
        )
        for identifier, seen in identifiers:
            if identifier in seen:
                _fail(f"external session identity was reused: {identifier}")
            seen.add(identifier)
        if last_completed_at is not None and started_at < last_completed_at:
            _fail(f"external session time/order regressed: {row['cell_id']}")
        last_completed_at = completed_at
        if semantic:
            _validate_transcript(
                transcript,
                cell,
                plan_sha,
                scenarios[cell["scenario_id"]],
            )
        expected_receipt = _json_bytes(
            _receipt_value(
                plan_sha,
                cell,
                row["transcript_ref"],
                raw,
                transcript,
            )
        )
        actual_receipt = _read_file(run_dir / row["ingestion_receipt_ref"])
        if actual_receipt != expected_receipt:
            _fail(f"ingestion receipt drift: {row['cell_id']}")
    return {
        "source_artifact_ids": seen_source_artifact_ids,
        "external_receipt_ids": seen_external_receipt_ids,
        "external_session_ids": seen_external_session_ids,
        "last_completed_at": last_completed_at,
    }


def validate_run(args: argparse.Namespace) -> dict[str, Any]:
    plan, _, plan_sha, manifest = _load_run(args.run_dir, args.plan_sha256)
    _validate_materials(
        args.run_dir, plan, required=manifest["status"] != "initialized"
    )
    _validate_ingested_artifacts(args.run_dir, plan, plan_sha, manifest)
    if manifest["status"] == "blind_finalized":
        _validate_blind_bundle(args.run_dir, plan, plan_sha, manifest)
    _validate_run_inventory(args.run_dir, plan, manifest)
    return {
        "run_plan_sha256": plan_sha,
        "status": manifest["status"],
        "ingested": sum(row["status"] == "ingested" for row in manifest["cells"]),
        "cells": 48,
    }


def _validate_transcript(value: dict[str, Any], expected: dict[str, Any], plan_sha: str, scenario: dict[str, Any]) -> None:
    try:
        _validate_schema(TRANSCRIPT_SCHEMA, value, "transcript")
    except EnvelopeError as exc:
        raise StopViolation("transcript_contract_failure", str(exc)) from exc
    if value["cell_id"] != expected["cell_id"] or value["sequence_index"] != expected["sequence_index"]:
        raise StopViolation("out_of_order_ingestion", "transcript is not the next frozen cell")
    if value["run_plan_sha256"] != plan_sha:
        raise StopViolation("prompt_or_role_card_hash_mismatch", "transcript run-plan binding mismatch")
    binding_pairs = {
        "prompt_sha256": expected["prompt"]["sha256"],
        "scenario_sha256": expected["scenario_sha256"],
        "initial_message_sha256": expected["initial_message_sha256"],
        "actor_packet_sha256": expected["actor_packet_sha256"],
        "session_envelope_sha256": expected["session_envelope_sha256"],
    }
    if value["bindings"] != binding_pairs:
        raise StopViolation("prompt_or_role_card_hash_mismatch", "transcript prompt/role/envelope binding mismatch")
    _external_session_receipt(value, expected)
    observations = value["observations"]
    turns = value["turns"]
    events = value["events"]
    normalized_events = [_normalize_raw_event(event) for event in events]
    event_kinds = [event["event_kind"] for event in normalized_events]
    try:
        _assert_blindable_transcript(
            {"cells": [expected]}, value
        )
    except EnvelopeError as exc:
        raise StopViolation(
            "arm_leakage",
            f"transcript semantic blinding gate failed: {exc}",
        ) from exc
    transcript_text = "\n".join(turn["text"] for turn in turns).casefold()
    checks = (
        (
            not observations["prompt_hash_match"]
            or not observations["role_card_hash_match"],
            "prompt_or_role_card_hash_mismatch",
        ),
        (
            observations["arm_leakage"]
            or any(token in transcript_text for token in ARM_LEAK_TOKENS),
            "arm_leakage",
        ),
        (not observations["eligible"], "ineligible_session"),
        (
            bool(observations["unplanned_tool_actions"])
            or "tool_action" in event_kinds,
            "unplanned_tool_action",
        ),
        (
            bool(observations["unplanned_network_actions"])
            or "network_action" in event_kinds,
            "unplanned_network_action",
        ),
        (
            observations["evidence_write_failure"]
            or "evidence_write_failure" in event_kinds,
            "evidence_write_failure",
        ),
        (
            observations["partial_subject_output"]
            or "session_blocked" in event_kinds
            or "session_partial" in event_kinds,
            "partial_subject_output",
        ),
        (observations["actor_protocol_deviation"], "actor_protocol_deviation"),
    )
    for failed, code in checks:
        if failed:
            raise StopViolation(code, f"transcript reports stop condition {code}")
    session = value["session"]
    if not session["fresh_context"] or not session["complete"] or session["blocked"] or session["partial"]:
        raise StopViolation("partial_subject_output", "session is not a complete fresh-context record")
    if session["stop_reason"] not in {"freeze_point_reached", "actor_decided_early"}:
        raise StopViolation("actor_protocol_deviation", "session has a non-eligible stop reason")
    if [turn["turn_index"] for turn in turns] != list(range(1, len(turns) + 1)):
        raise StopViolation("transcript_contract_failure", "turn indices are not contiguous")
    if any(turn["role"] != ("actor" if index % 2 == 0 else "subject") for index, turn in enumerate(turns)):
        raise StopViolation("actor_protocol_deviation", "turn roles do not strictly alternate from actor")
    if turns[-1]["role"] != "actor" or turns[0]["text"] != scenario["initial_message"]:
        raise StopViolation("actor_protocol_deviation", "transcript first/final actor-turn contract failed")
    actor_turns = sum(turn["role"] == "actor" for turn in turns)
    subject_turns = len(turns) - actor_turns
    if (actor_turns, subject_turns) != (session["actor_turns"], session["subject_turns"]):
        raise StopViolation("transcript_contract_failure", "declared turn counts do not match transcript")
    if session["stop_reason"] == "freeze_point_reached" and actor_turns != 6:
        raise StopViolation("actor_protocol_deviation", "freeze-point session must end on actor turn 6")
    if [event["event_index"] for event in events] != list(range(1, len(events) + 1)):
        raise StopViolation("transcript_contract_failure", "event indices are not contiguous")
    if (
        event_kinds[0] != "session_started"
        or event_kinds[-1] != "session_completed"
        or event_kinds.count("session_started") != 1
        or event_kinds.count("session_completed") != 1
    ):
        raise StopViolation(
            "transcript_contract_failure",
            "eligible event stream requires exactly one first start and one last completion",
        )
    message_events = [
        event
        for event in normalized_events
        if event["event_kind"] in MESSAGE_EVENT_KINDS
    ]
    expected_messages = [
        {
            "event_kind": f"{turn['role']}_message",
            "turn_index": turn["turn_index"],
            "text": turn["text"],
        }
        for turn in turns
    ]
    if message_events != expected_messages:
        raise StopViolation(
            "transcript_contract_failure",
            "transcript turns are not derived byte-exactly from raw message events",
        )


def _record_stop(
    run_dir: Path,
    plan: dict[str, Any],
    plan_sha: str,
    manifest: dict[str, Any],
    raw: bytes,
    violation: StopViolation,
    preserved_auxiliary_artifacts: list[dict[str, str]] | None = None,
) -> None:
    index = manifest["next_sequence_index"] - 1
    expected = plan["cells"][index]
    raw_sha = _sha(raw)
    raw_ref = f"blocked/{expected['cell_id']}.transcript.{raw_sha}.raw"
    raw_path = run_dir / raw_ref
    if raw_path.exists():
        try:
            collision = _read_file(raw_path, limit=max(MAX_INPUT_BYTES, len(raw)))
        except EnvelopeError:
            collision = None
        if collision != raw:
            while True:
                candidate = raw_ref + f".collision-{secrets.token_hex(8)}"
                if not (run_dir / candidate).exists():
                    raw_ref = candidate
                    raw_path = run_dir / raw_ref
                    break
    # Attempt complete-byte publication before freezing the marker so any
    # surviving atomic staging evidence can be hash-registered in its replay.
    raw_write_error: EnvelopeError | None = None
    try:
        _ensure_exact_new(raw_path, raw)
    except EnvelopeError as exc:
        raw_write_error = exc
    supplied = list(preserved_auxiliary_artifacts or [])
    expected_before, _ = _expected_run_inventory(run_dir, plan, manifest)
    observed_before, _ = _relative_files_and_directories(run_dir)
    supplied_refs = {row["ref"] for row in supplied}
    for ref in sorted(observed_before - expected_before - supplied_refs):
        if ref in {STOP_INTENT_REF, raw_ref}:
            continue
        artifact_raw = _read_file(run_dir / ref)
        supplied.append(
            {
                "role": "pre_stop_unregistered_artifact",
                "ref": ref,
                "sha256": _sha(artifact_raw),
            }
        )
    if len(supplied) > 64:
        _fail("too many pre-stop artifacts to register in the closed stop receipt")
    stopped_manifest = copy.deepcopy(manifest)
    stopped_manifest["cells"][index].update(
        status="blocked",
        transcript_ref=raw_ref,
        transcript_sha256=raw_sha,
        ingestion_receipt_ref=None,
    )
    stopped_manifest["status"] = "stopped"
    stopped_manifest["stopped"] = True
    stopped_manifest["stop_receipt"] = {
        "cell_id": expected["cell_id"],
        "sequence_index": expected["sequence_index"],
        "reason_code": violation.code,
        "detail": violation.detail[:2000],
        "raw_ref": raw_ref,
        "raw_sha256": raw_sha,
        "retry_forbidden": True,
        "stop_intent_ref": STOP_INTENT_REF,
        "stop_intent_committed_before_state_replacement": True,
        "preserved_auxiliary_artifacts": supplied,
    }
    _validate_manifest(stopped_manifest, plan, plan_sha)
    prior_manifest_raw = _read_file(run_dir / "ingestion-manifest.json")
    if _strict_loads(prior_manifest_raw) != manifest:
        _fail("ingestion manifest changed while preparing durable stop intent")
    stopped_raw = _json_bytes(stopped_manifest)
    marker = {
        "schema_version": "ideation-diversity-stop-intent/1.0",
        "suite": SUITE,
        "run_plan_sha256": plan_sha,
        "prior_manifest_sha256": _sha(prior_manifest_raw),
        "cell_id": expected["cell_id"],
        "sequence_index": expected["sequence_index"],
        "reason_code": violation.code,
        "detail": violation.detail[:2000],
        "raw_ref": raw_ref,
        "raw_sha256": raw_sha,
        "raw_base64": base64.b64encode(raw).decode("ascii"),
        "stopped_manifest_sha256": _sha(stopped_raw),
        "stopped_manifest_base64": base64.b64encode(stopped_raw).decode("ascii"),
        "retry_forbidden": True,
    }
    marker_raw = _json_bytes(marker)
    _validate_stop_intent(marker_raw, plan, plan_sha)
    _ensure_exact_new(run_dir / STOP_INTENT_REF, marker_raw)
    try:
        _ensure_exact_new(raw_path, raw)
        raw_write_error = None
    except EnvelopeError as exc:
        raw_write_error = exc
    # The marker is the irreversible boundary. If this replacement fails,
    # every later load rejects retry and can replay the exact stopped state.
    _replace_json(run_dir / "ingestion-manifest.json", stopped_manifest)
    if raw_write_error is not None:
        raise EnvelopeError(
            "run is permanently stopped; blocked raw recovery remains pending: "
            f"{raw_write_error}"
        ) from raw_write_error


def _preserved_ingestion_artifacts(
    run_dir: Path,
    manifest_before: dict[str, Any],
    authorization_raw: bytes,
    transcript_ref: str,
    transcript_raw: bytes,
    receipt_ref: str,
    receipt_raw: bytes,
) -> list[dict[str, str]]:
    candidates: list[tuple[str, str, bytes]] = []
    if manifest_before["authorization_record_sha256"] is None:
        candidates.append(
            ("authorization_record", "authorization/record.json", authorization_raw)
        )
    candidates.extend(
        (
            (
                "accepted_transcript_before_state_commit",
                transcript_ref,
                transcript_raw,
            ),
            (
                "ingestion_receipt_before_state_commit",
                receipt_ref,
                receipt_raw,
            ),
        )
    )
    preserved: list[dict[str, str]] = []
    for role, ref, expected_raw in candidates:
        try:
            actual_raw = _read_file(run_dir / ref)
        except EnvelopeError:
            continue
        if actual_raw == expected_raw:
            preserved.append({"role": role, "ref": ref, "sha256": _sha(actual_raw)})
    return preserved


def ingest(args: argparse.Namespace) -> dict[str, Any]:
    plan, _, plan_sha, manifest = _load_run(args.run_dir, args.plan_sha256)
    if manifest["stopped"]:
        _fail("run is stopped; the frozen protocol forbids retry")
    if manifest["status"] in {"complete", "blind_finalized"}:
        _fail("all 48 transcripts are already ingested")
    if manifest["status"] not in {"materialized", "ingesting"}:
        _fail("transcripts may be ingested only after materialization")
    raw = _read_file(args.transcript)
    expected = plan["cells"][manifest["next_sequence_index"] - 1]
    scenario = _scenario_index(phase1.load_assets()[0])[expected["scenario_id"]]
    try:
        _validate_materials(args.run_dir, plan, required=True)
        sequence_state = _validate_ingested_artifacts(
            args.run_dir,
            plan,
            plan_sha,
            manifest,
            semantic=False,
        )
        _validate_run_inventory(args.run_dir, plan, manifest)
    except EnvelopeError as exc:
        violation = StopViolation(
            "evidence_write_failure",
            f"pre-ingestion run evidence/inventory validation failed: {exc}",
        )
        _record_stop(args.run_dir, plan, plan_sha, manifest, raw, violation)
        raise violation from exc
    try:
        value = _strict_loads(raw)
        _validate_transcript(value, expected, plan_sha, scenario)
        try:
            authorization_raw = _read_file(args.authorization_record)
            authorization = _strict_loads(authorization_raw)
            _validate_authorization_record(authorization, plan, plan_sha)
        except EnvelopeError as exc:
            raise StopViolation(
                "authorization_record_missing_or_mismatch",
                f"cannot verify external authorization record: {exc}",
            ) from exc
        authorization_sha = _sha(authorization_raw)
        if authorization_sha != value["source"]["authorization_record_sha256"]:
            raise StopViolation(
                "authorization_record_missing_or_mismatch",
                "external authorization record hash does not match transcript binding",
            )
        if value["source"]["authorization_record_ref"] != authorization["record_id"]:
            raise StopViolation(
                "authorization_record_missing_or_mismatch",
                "transcript authorization reference differs from record id",
            )
        external_receipt = _external_session_receipt(value, expected)
        started_at = _timestamp(
            external_receipt["started_at"], "external session started_at"
        )
        if started_at < _timestamp(
            authorization["decision"]["decided_at"],
            "authorization decided_at",
        ):
            raise StopViolation(
                "authorization_record_missing_or_mismatch",
                "external session starts before the authorization decision",
            )
        uniqueness = (
            (
                value["source"]["source_artifact_id"],
                sequence_state["source_artifact_ids"],
            ),
            (
                external_receipt["receipt_id"],
                sequence_state["external_receipt_ids"],
            ),
            (
                external_receipt["external_session_id"],
                sequence_state["external_session_ids"],
            ),
        )
        if any(identifier in seen for identifier, seen in uniqueness):
            raise StopViolation(
                "out_of_order_ingestion",
                "external artifact, receipt, or fresh-context session id was reused",
            )
        last_completed_at = sequence_state["last_completed_at"]
        if last_completed_at is not None and started_at < last_completed_at:
            raise StopViolation(
                "out_of_order_ingestion",
                "external session time/order regressed across frozen cells",
            )
        if manifest["authorization_record_sha256"] not in {None, authorization_sha}:
            raise StopViolation(
                "authorization_record_missing_or_mismatch",
                "run is already bound to a different authorization record",
            )
    except StopViolation as violation:
        _record_stop(args.run_dir, plan, plan_sha, manifest, raw, violation)
        raise
    except EnvelopeError as exc:
        violation = StopViolation("transcript_contract_failure", str(exc))
        _record_stop(args.run_dir, plan, plan_sha, manifest, raw, violation)
        raise violation from exc
    cell_id = expected["cell_id"]
    transcript_ref = f"transcripts/{cell_id}.json"
    receipt_ref = f"receipts/{cell_id}.json"
    receipt = _receipt_value(plan_sha, expected, transcript_ref, raw, value)
    receipt_raw = _json_bytes(receipt)
    manifest_before_ingestion = copy.deepcopy(manifest)
    try:
        if manifest["authorization_record_sha256"] is None:
            _write_new(
                args.run_dir / "authorization/record.json",
                authorization_raw,
            )
            manifest["authorization_record_path"] = "authorization/record.json"
            manifest["authorization_record_sha256"] = authorization_sha
        _write_new(args.run_dir / transcript_ref, raw)
        _write_new(args.run_dir / receipt_ref, receipt_raw)
    except EnvelopeError as exc:
        violation = StopViolation(
            "evidence_write_failure",
            f"cannot preserve accepted transcript/receipt: {exc}",
        )
        try:
            _record_stop(
                args.run_dir,
                plan,
                plan_sha,
                manifest_before_ingestion,
                raw,
                violation,
                _preserved_ingestion_artifacts(
                    args.run_dir,
                    manifest_before_ingestion,
                    authorization_raw,
                    transcript_ref,
                    raw,
                    receipt_ref,
                    receipt_raw,
                ),
            )
        except EnvelopeError as stop_exc:
            raise EnvelopeError(
                "evidence write failed and the stop receipt could not be persisted; "
                "do not retry this run"
            ) from stop_exc
        raise violation from exc
    manifest["cells"][expected["sequence_index"] - 1].update(
        status="ingested",
        transcript_ref=transcript_ref,
        transcript_sha256=_sha(raw),
        ingestion_receipt_ref=receipt_ref,
    )
    manifest["next_sequence_index"] += 1
    ingested = manifest["next_sequence_index"] - 1
    manifest["status"] = "complete" if ingested == 48 else "ingesting"
    _validate_manifest(manifest, plan, plan_sha)
    try:
        _replace_json(args.run_dir / "ingestion-manifest.json", manifest)
    except EnvelopeError as exc:
        violation = StopViolation(
            "evidence_write_failure",
            f"cannot persist ingestion manifest: {exc}",
        )
        try:
            _record_stop(
                args.run_dir,
                plan,
                plan_sha,
                manifest_before_ingestion,
                raw,
                violation,
                _preserved_ingestion_artifacts(
                    args.run_dir,
                    manifest_before_ingestion,
                    authorization_raw,
                    transcript_ref,
                    raw,
                    receipt_ref,
                    receipt_raw,
                ),
            )
        except EnvelopeError as stop_exc:
            raise EnvelopeError(
                "ingestion manifest write failed and the stop receipt could not be "
                "persisted; do not retry this run"
            ) from stop_exc
        raise violation from exc
    return {"ingested": ingested, "next_sequence_index": manifest["next_sequence_index"]}


def _artifact_presence() -> dict[str, bool]:
    return {
        "structured_judge_labels_attached": False,
        "adjudication_artifact_attached": False,
        "human_evidence_artifact_attached": False,
    }


def _assignment_boundary() -> dict[str, bool]:
    return {
        "future_closed_assignment_ledger_gate_required": True,
        "assignment_ledger_implemented_by_no_call_runner": False,
        "same_judge_equivalent_scholar_context_cross_condition_exposure_forbidden": True,
        "bundle_alone_proves_judge_exposure_blindness": False,
    }


def _blind_identifiers(plan: dict[str, Any]) -> set[str]:
    identifiers: set[str] = set()
    for cell in plan["cells"]:
        identifiers.update(
            _normalized_blind_text(str(cell[key]))
            for key in (
                "cell_id",
                "experiment_id",
                "arm_id",
                "scenario_id",
                "pair_id",
                "actor_block_id",
            )
        )
    return identifiers


def _normalized_blind_text(text: str) -> str:
    """Normalize compatibility forms and punctuation separators before matching."""
    normalized = unicodedata.normalize("NFKC", text).casefold()
    separated = "".join(
        " " if unicodedata.category(character)[0] in {"C", "P", "Z"} else character
        for character in normalized
    )
    return " ".join(separated.split())


def _assert_blindable_transcript(
    plan: dict[str, Any], transcript: dict[str, Any]
) -> None:
    _assert_blind_texts(plan, [turn["text"] for turn in transcript["turns"]])


def _assert_blind_texts(plan: dict[str, Any], texts: list[str]) -> None:
    blind_identifiers = _blind_identifiers(plan)
    for text in texts:
        folded = _normalized_blind_text(text)
        leaked = next(
            (identifier for identifier in blind_identifiers if identifier in folded),
            None,
        )
        if leaked is not None:
            _fail(f"transcript free text leaks frozen blind identifier {leaked!r}")
        if any(pattern.search(folded) for pattern in MAPPING_LEAK_PATTERNS):
            _fail("transcript free text leaks pair/arm/replicate mapping")
        if any(pattern.search(folded) for pattern in HUMAN_EVIDENCE_PATTERNS):
            _fail("transcript free text contains prior label/adjudication/human evidence")


def _assert_blind_packet_structure(
    plan: dict[str, Any], packet: dict[str, Any]
) -> None:
    forbidden_keys = {
        "cell_id",
        "sequence_index",
        "experiment_id",
        "arm_id",
        "scenario_id",
        "pair_id",
        "replicate",
        "actor_block_id",
        "source",
        "events",
        "observations",
    }

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            leaked_keys = forbidden_keys.intersection(value)
            if leaked_keys:
                _fail(f"blind packet contains assignment/source keys {sorted(leaked_keys)!r}")
            for child in value.values():
                visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(packet)
    role_card = packet["role_card"]
    role_texts = [
        role_card["role_brief"],
        role_card["initial_message"],
        *[row["statement"] for row in role_card["owned_framings"]],
        *role_card["forbidden_out_of_role"],
        packet["domain"],
    ]
    _assert_blind_texts(plan, role_texts)


def _blind_packet_value(
    blind_id: str,
    scenario: dict[str, Any],
    transcript: dict[str, Any],
    codebook_raw: bytes,
) -> dict[str, Any]:
    return {
        "schema_version": "ideation-diversity-isolated-blind-session/1.0",
        "suite": SUITE,
        "blind_session_id": blind_id,
        "content_class": "repository-owned synthetic scholar role cards",
        "blinded_to": BLINDED_TO,
        "delivery": {
            "isolated_single_session": True,
            "deliver_other_sessions_together": False,
            "assignment_ledger_gate_required_before_delivery": True,
        },
        "assignment_boundary": _assignment_boundary(),
        "artifact_presence": _artifact_presence(),
        "free_text_screening": {
            "frozen_identifiers_rejected": True,
            "mapping_markers_rejected": True,
            "prior_label_adjudication_human_markers_rejected": True,
        },
        "codebook": {
            "sha256": _sha(codebook_raw),
            "text": codebook_raw.decode("utf-8"),
        },
        "language": scenario["language"],
        "domain": scenario["domain"],
        "role_card": {
            key: scenario[key]
            for key in (
                "role_brief",
                "initial_message",
                "owned_framings",
                "response_policy",
                "forbidden_out_of_role",
            )
        },
        "transcript": {
            "stop_reason": transcript["session"]["stop_reason"],
            "turns": transcript["turns"],
        },
    }


def _blind_inventory_value(
    plan_sha: str, inventory_rows: list[dict[str, str]]
) -> dict[str, Any]:
    return {
        "schema_version": "ideation-diversity-blind-inventory/1.0",
        "suite": SUITE,
        "run_plan_sha256": plan_sha,
        "packet_count": 48,
        "delivery_rule": (
            "deliver_exactly_one_isolated_packet_per_first_round_judge_assignment"
        ),
        "assignment_boundary": _assignment_boundary(),
        "artifact_presence": _artifact_presence(),
        "packets": inventory_rows,
    }


def _private_map_value(
    plan_sha: str,
    inventory_raw: bytes,
    mapping: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "schema_version": "ideation-diversity-private-arm-map/1.0",
        "suite": SUITE,
        "run_plan_sha256": plan_sha,
        "inventory_sha256": _sha(inventory_raw),
        "private": True,
        "protection": {
            "kind": "procedural_nondisclosure_only",
            "encrypted": False,
            "directory_mode": "0700",
            "file_mode": "0600",
            "unblind_only_after_raw_labels_and_adjudication_sealed": True,
        },
        "mapping": mapping,
    }


def _blind_manifest_value(
    plan_sha: str,
    source_ingestion_manifest_sha: str,
    inventory_raw: bytes,
    packets: list[tuple[str, bytes]],
    private_map_raw: bytes,
) -> dict[str, Any]:
    return {
        "schema_version": "ideation-diversity-blind-manifest/1.0",
        "suite": SUITE,
        "run_plan_sha256": plan_sha,
        "source_ingestion_manifest_sha256": source_ingestion_manifest_sha,
        "inventory_ref": "blind/inventory.json",
        "inventory_sha256": _sha(inventory_raw),
        "private_map_ref": "blind/private/arm-map.json",
        "private_map_sha256": _sha(private_map_raw),
        "packet_count": 48,
        "packets": [
            {
                "blind_session_id": blind_id,
                "packet_ref": f"blind/sessions/{blind_id}.json",
                "packet_sha256": _sha(packet_raw),
            }
            for blind_id, packet_raw in packets
        ],
        "finalized_artifacts": True,
        "exact_inventory_required": True,
    }


def _source_ingestion_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    source = copy.deepcopy(manifest)
    source["status"] = "complete"
    source["blind_manifest_ref"] = None
    source["blind_manifest_sha256"] = None
    return source


def _validate_blind_bundle(
    run_dir: Path,
    plan: dict[str, Any],
    plan_sha: str,
    manifest: dict[str, Any],
) -> tuple[str, str]:
    blind_manifest_raw = _read_file(run_dir / "blind/manifest.json")
    blind_manifest_sha = _sha(blind_manifest_raw)
    blind_manifest = _strict_loads(blind_manifest_raw)
    _validate_schema(BLIND_MANIFEST_SCHEMA, blind_manifest, "blind manifest")
    if blind_manifest["run_plan_sha256"] != plan_sha:
        _fail("blind manifest is bound to a different run plan")
    source_sha = _sha(_json_bytes(_source_ingestion_manifest(manifest)))
    if blind_manifest["source_ingestion_manifest_sha256"] != source_sha:
        _fail("blind manifest source ingestion state drifted")
    if manifest["status"] == "blind_finalized" and (
        manifest["blind_manifest_ref"], manifest["blind_manifest_sha256"]
    ) != ("blind/manifest.json", blind_manifest_sha):
        _fail("finalized ingestion state disagrees with blind manifest bytes")

    expected_bundle_files = {
        "manifest.json",
        str(Path(blind_manifest["inventory_ref"]).relative_to("blind")),
        str(Path(blind_manifest["private_map_ref"]).relative_to("blind")),
    }
    expected_bundle_files.update(
        str(Path(row["packet_ref"]).relative_to("blind"))
        for row in blind_manifest["packets"]
    )
    observed_files, observed_directories = _relative_files_and_directories(
        run_dir / "blind"
    )
    if observed_files != expected_bundle_files or observed_directories != _parent_directories(
        expected_bundle_files
    ):
        _fail("blind bundle file/directory inventory is not exact")

    inventory_raw = _read_file(run_dir / blind_manifest["inventory_ref"])
    if _sha(inventory_raw) != blind_manifest["inventory_sha256"]:
        _fail("blind inventory hash drift")
    inventory = _strict_loads(inventory_raw)
    _validate_schema(BLIND_INVENTORY_SCHEMA, inventory, "blind inventory")

    private_map_path = run_dir / blind_manifest["private_map_ref"]
    private_map_raw = _read_file(private_map_path)
    if _sha(private_map_raw) != blind_manifest["private_map_sha256"]:
        _fail("private arm-map hash drift")
    if stat.S_IMODE(private_map_path.parent.stat().st_mode) != 0o700:
        _fail("private arm-map directory mode must remain 0700")
    if stat.S_IMODE(private_map_path.stat().st_mode) != 0o600:
        _fail("private arm-map file mode must remain 0600")
    private_map = _strict_loads(private_map_raw)
    _validate_schema(PRIVATE_ARM_MAP_SCHEMA, private_map, "private arm map")
    mapping = private_map.get("mapping")
    if not isinstance(mapping, list) or len(mapping) != 48:
        _fail("private arm map must contain exactly 48 mappings")
    mapping_by_id = {row.get("blind_session_id"): row for row in mapping}
    if None in mapping_by_id or len(mapping_by_id) != 48:
        _fail("private arm map blind ids must be unique")

    scenarios = _scenario_index(phase1.load_assets()[0])
    codebook_raw = _read_file(CODEBOOK)
    packet_pairs: list[tuple[str, bytes]] = []
    inventory_rows: list[dict[str, str]] = []
    expected_mapping: list[dict[str, Any]] = []
    plan_by_cell = {cell["cell_id"]: cell for cell in plan["cells"]}
    state_by_cell = {row["cell_id"]: row for row in manifest["cells"]}
    for packet_row in blind_manifest["packets"]:
        blind_id = packet_row["blind_session_id"]
        mapped = mapping_by_id.get(blind_id)
        if mapped is None or mapped.get("cell_id") not in plan_by_cell:
            _fail(f"blind mapping is missing or invalid for {blind_id}")
        cell = plan_by_cell[mapped["cell_id"]]
        expected_map_row = {
            "blind_session_id": blind_id,
            "cell_id": cell["cell_id"],
            "experiment_id": cell["experiment_id"],
            "arm_id": cell["arm_id"],
            "scenario_id": cell["scenario_id"],
            "pair_id": cell["pair_id"],
            "replicate": cell["replicate"],
        }
        if mapped != expected_map_row:
            _fail(f"private arm mapping drift for {blind_id}")
        transcript_raw = _read_file(
            run_dir / state_by_cell[cell["cell_id"]]["transcript_ref"]
        )
        transcript = _strict_loads(transcript_raw)
        _assert_blindable_transcript(plan, transcript)
        expected_packet = _blind_packet_value(
            blind_id,
            scenarios[cell["scenario_id"]],
            transcript,
            codebook_raw,
        )
        _assert_blind_packet_structure(plan, expected_packet)
        expected_packet_raw = _json_bytes(expected_packet)
        packet_raw = _read_file(run_dir / packet_row["packet_ref"])
        if packet_raw != expected_packet_raw or _sha(packet_raw) != packet_row[
            "packet_sha256"
        ]:
            _fail(f"blind packet replay/hash drift for {blind_id}")
        packet_pairs.append((blind_id, packet_raw))
        inventory_rows.append(
            {"blind_session_id": blind_id, "packet_sha256": _sha(packet_raw)}
        )
        expected_mapping.append(expected_map_row)

    packet_pairs.sort(key=lambda row: row[0])
    inventory_rows.sort(key=lambda row: row["blind_session_id"])
    expected_mapping.sort(key=lambda row: row["blind_session_id"])
    if inventory != _blind_inventory_value(plan_sha, inventory_rows):
        _fail("blind inventory replay drift")
    expected_private_map = _private_map_value(
        plan_sha, inventory_raw, expected_mapping
    )
    if private_map != expected_private_map:
        _fail("private arm-map replay drift")
    expected_blind_manifest = _blind_manifest_value(
        plan_sha,
        source_sha,
        inventory_raw,
        packet_pairs,
        private_map_raw,
    )
    if blind_manifest != expected_blind_manifest:
        _fail("blind manifest replay drift")
    return blind_manifest_sha, _sha(inventory_raw)


def _finalize_blind_state(
    run_dir: Path,
    plan: dict[str, Any],
    plan_sha: str,
    manifest: dict[str, Any],
    blind_manifest_sha: str,
) -> dict[str, Any]:
    finalized = copy.deepcopy(manifest)
    finalized["status"] = "blind_finalized"
    finalized["blind_manifest_ref"] = "blind/manifest.json"
    finalized["blind_manifest_sha256"] = blind_manifest_sha
    _validate_manifest(finalized, plan, plan_sha)
    _replace_json(run_dir / "ingestion-manifest.json", finalized)
    return finalized


def prepare_blind_packet(args: argparse.Namespace) -> dict[str, Any]:
    plan, _, plan_sha, manifest = _load_run(args.run_dir, args.plan_sha256)
    _validate_materials(args.run_dir, plan, required=True)
    _validate_ingested_artifacts(args.run_dir, plan, plan_sha, manifest)
    if manifest["status"] == "blind_finalized":
        _fail("blind packet is already finalized and write-once")
    if manifest["status"] != "complete" or manifest["stopped"]:
        _fail("blind packet requires 48 complete, unstopped transcript ingestions")

    blind_root = args.run_dir / "blind"
    if blind_root.exists():
        blind_manifest_sha, inventory_sha = _validate_blind_bundle(
            args.run_dir, plan, plan_sha, manifest
        )
        finalized = _finalize_blind_state(
            args.run_dir, plan, plan_sha, manifest, blind_manifest_sha
        )
        _validate_run_inventory(args.run_dir, plan, finalized)
        return {
            "inventory_sha256": inventory_sha,
            "sessions": 48,
            "artifact_presence": _artifact_presence(),
            "state": "blind_finalized",
            "recovered_existing_atomic_bundle": True,
        }

    _validate_run_inventory(args.run_dir, plan, manifest)
    scenarios = _scenario_index(phase1.load_assets()[0])
    codebook_raw = _read_file(CODEBOOK)
    packets: list[tuple[str, bytes]] = []
    inventory_rows: list[dict[str, str]] = []
    mapping: list[dict[str, Any]] = []
    used: set[str] = set()
    for cell, state in zip(plan["cells"], manifest["cells"]):
        raw = _read_file(args.run_dir / state["transcript_ref"])
        if _sha(raw) != state["transcript_sha256"]:
            _fail(f"transcript drift before blinding: {cell['cell_id']}")
        transcript = _strict_loads(raw)
        _assert_blindable_transcript(plan, transcript)
        while True:
            blind_id = f"blind-{secrets.token_hex(12)}"
            if blind_id not in used:
                used.add(blind_id)
                break
        isolated_packet = _blind_packet_value(
            blind_id, scenarios[cell["scenario_id"]], transcript, codebook_raw
        )
        _assert_blind_packet_structure(plan, isolated_packet)
        _validate_schema(BLIND_PACKET_SCHEMA, isolated_packet, "isolated blind packet")
        packet_raw = _json_bytes(isolated_packet)
        packets.append((blind_id, packet_raw))
        inventory_rows.append(
            {"blind_session_id": blind_id, "packet_sha256": _sha(packet_raw)}
        )
        mapping.append(
            {
                "blind_session_id": blind_id,
                "cell_id": cell["cell_id"],
                "experiment_id": cell["experiment_id"],
                "arm_id": cell["arm_id"],
                "scenario_id": cell["scenario_id"],
                "pair_id": cell["pair_id"],
                "replicate": cell["replicate"],
            }
        )
    packets.sort(key=lambda row: row[0])
    inventory_rows.sort(key=lambda row: row["blind_session_id"])
    mapping.sort(key=lambda row: row["blind_session_id"])
    inventory = _blind_inventory_value(plan_sha, inventory_rows)
    _validate_schema(BLIND_INVENTORY_SCHEMA, inventory, "blind inventory")
    inventory_raw = _json_bytes(inventory)
    private_map = _private_map_value(plan_sha, inventory_raw, mapping)
    _validate_schema(PRIVATE_ARM_MAP_SCHEMA, private_map, "private arm map")
    private_map_raw = _json_bytes(private_map)
    source_ingestion_manifest_sha = _sha(_json_bytes(manifest))
    blind_manifest = _blind_manifest_value(
        plan_sha,
        source_ingestion_manifest_sha,
        inventory_raw,
        packets,
        private_map_raw,
    )
    _validate_schema(BLIND_MANIFEST_SCHEMA, blind_manifest, "blind manifest")
    blind_manifest_raw = _json_bytes(blind_manifest)

    staging = args.run_dir.parent / (
        f".{args.run_dir.name}.blind-next-{secrets.token_hex(12)}"
    )
    try:
        staging.mkdir(mode=0o755)
        for blind_id, packet_raw in packets:
            _write_new(staging / "sessions" / f"{blind_id}.json", packet_raw)
        _write_new(staging / "inventory.json", inventory_raw)
        private_directory = staging / "private"
        private_directory.mkdir(mode=0o700)
        os.chmod(private_directory, 0o700)
        _write_new(private_directory / "arm-map.json", private_map_raw, mode=0o600)
        os.chmod(private_directory / "arm-map.json", 0o600)
        _write_new(staging / "manifest.json", blind_manifest_raw)
        os.rename(staging, blind_root)
        _fsync_directory(args.run_dir)
        _fsync_directory(args.run_dir.parent)
    except OSError as exc:
        raise EnvelopeError(f"cannot atomically finalize blind bundle: {exc}") from exc

    blind_manifest_sha, inventory_sha = _validate_blind_bundle(
        args.run_dir, plan, plan_sha, manifest
    )
    finalized = _finalize_blind_state(
        args.run_dir, plan, plan_sha, manifest, blind_manifest_sha
    )
    _validate_run_inventory(args.run_dir, plan, finalized)
    return {
        "inventory_sha256": inventory_sha,
        "sessions": 48,
        "artifact_presence": _artifact_presence(),
        "state": "blind_finalized",
        "recovered_existing_atomic_bundle": False,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    init = sub.add_parser("init-run", help="freeze a 48-cell no-call run plan")
    init.add_argument("--run-dir", type=Path, required=True)
    init.add_argument("--run-id", required=True)
    init.add_argument(
        "--suite-commit",
        required=True,
        help="operator-declared 40-hex provenance; existence is not verified",
    )
    init.add_argument("--order-seed", required=True)
    init.add_argument("--subject-provider", required=True)
    init.add_argument("--subject-model", required=True)
    init.add_argument("--subject-runtime", required=True)
    init.add_argument("--subject-runtime-version", required=True)
    init.add_argument("--auth-mode", required=True)
    init.add_argument("--reasoning-effort", required=True)
    init.add_argument(
        "--input-token-cap",
        type=int,
        required=True,
        help="operator-declared cap; this no-call runner does not verify usage",
    )
    init.add_argument(
        "--output-token-cap",
        type=int,
        required=True,
        help="operator-declared cap; this no-call runner does not verify usage",
    )
    materialize_parser = sub.add_parser(
        "materialize",
        help="materialize prompt, actor, and operator packets only",
    )
    validate_parser = sub.add_parser(
        "validate",
        help="validate frozen plan, materials, and ingested hashes",
    )
    blind_parser = sub.add_parser(
        "prepare-blind-packet",
        help="prepare isolated unlabeled arm-blind packets",
    )
    for command_parser in (materialize_parser, validate_parser, blind_parser):
        command_parser.add_argument("--run-dir", type=Path, required=True)
        command_parser.add_argument("--plan-sha256", required=True)
    ingest_parser = sub.add_parser("ingest", help="ingest one external transcript in frozen order")
    ingest_parser.add_argument("--run-dir", type=Path, required=True)
    ingest_parser.add_argument("--plan-sha256", required=True)
    ingest_parser.add_argument("--transcript", type=Path, required=True)
    ingest_parser.add_argument("--authorization-record", type=Path, required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "init-run":
            result = init_run(args)
        elif args.command == "materialize":
            result = materialize(args)
        elif args.command == "validate":
            result = validate_run(args)
        elif args.command == "ingest":
            result = ingest(args)
        elif args.command == "prepare-blind-packet":
            result = prepare_blind_packet(args)
        else:
            raise AssertionError(f"unhandled command {args.command!r}")
    except EnvelopeError as exc:
        print(f"{SUITE}: FAIL: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
