#!/usr/bin/env python3
"""Validate and apply the research-workflow-profile/1.0 contract (#742).

The runtime is deliberately manuscript-blind.  It reads only explicitly
supplied profile/receipt/inventory paths, never proposes a family from content,
and emits selection state to stdout.  Profile corrections are append-only:
every caller-declared stage output is represented by a visible stale mark and
no scholar-owned artifact is opened, rewritten, or deleted.
"""
from __future__ import annotations

import argparse
import copy
import hashlib
import json
import re
import sys
from datetime import date, datetime
from pathlib import Path
from typing import Any, Mapping, NoReturn, Sequence


REPO_ROOT = Path(__file__).resolve().parent.parent
DEFAULT_FIELD_GENERAL_PROFILE = (
    REPO_ROOT / "shared" / "research_workflow_profiles" / "field_general.json"
)

PROFILE_SCHEMA_VERSION = "research-workflow-profile/1.0"
RECEIPT_SCHEMA_VERSION = "research-workflow-profile-selection-receipt/1.0"
PROFILE_HASH_PLACEHOLDER = "0" * 64
JCS_SAFE_INTEGER_MAX = 9_007_199_254_740_991

# Frozen with docs/design/2026-08-17-742-... §2 and the #745 matrix.
TASK_FAMILIES = (
    "rq_formation",
    "retrieval",
    "methodology",
    "synthesis",
    "drafting",
    "integrity_check",
    "review",
    "revision",
    "finalization",
)
PIPELINE_STAGE_IDS: dict[str, tuple[str, ...]] = {
    "rq_formation": ("stage_0_socratic",),
    "retrieval": ("stage_1_corpus",),
    "methodology": ("stage_1_blueprint",),
    "synthesis": ("stage_1_synthesis",),
    "drafting": ("stage_2_draft",),
    "integrity_check": ("stage_2_5_gate", "stage_4_5_gate"),
    "review": ("stage_3_review", "stage_3p_re_review"),
    "revision": ("stage_4_revision",),
    "finalization": ("stage_5_final", "stage_6_record"),
}

RESEARCH_FAMILIES = (
    "quantitative_empirical",
    "qualitative",
    "theoretical_conceptual",
    "interpretive_humanities",
    "evidence_synthesis",
    "computational",
    "clinical_human_subjects",
    "field_general",
)
RESEARCH_FAMILY_DISPLAY_NAMES: dict[str, dict[str, str]] = {
    "quantitative_empirical": {
        "en": "Quantitative empirical",
        "zh_TW": "量化實證研究",
    },
    "qualitative": {"en": "Qualitative", "zh_TW": "質性研究"},
    "theoretical_conceptual": {
        "en": "Theoretical / conceptual",
        "zh_TW": "理論／概念研究",
    },
    "interpretive_humanities": {
        "en": "Interpretive / humanities",
        "zh_TW": "詮釋／人文研究",
    },
    "evidence_synthesis": {
        "en": "Evidence synthesis",
        "zh_TW": "證據綜整研究",
    },
    "computational": {"en": "Computational", "zh_TW": "計算研究"},
    "clinical_human_subjects": {
        "en": "Clinical / human-subjects",
        "zh_TW": "臨床／人類參與者研究",
    },
    "field_general": {
        "en": "Field-general fallback",
        "zh_TW": "領域通用後備設定",
    },
}

ALTERNATIVE_CATEGORIES = (
    "rival_theory",
    "alternative_design",
    "alternative_measurement",
    "alternative_model",
    "disconfirming_query",
    "boundary_condition",
)
SELECTION_SOURCES = (
    "user_explicit",
    "user_confirmed_proposal",
    "fallback_automatic",
)
PROFILE_SOURCES = ("shipped_default", "user_authored", "user_modified")
FRESHNESS_STATES = ("current", "stale", "unverified")
STAGE_STATES = ("applicable", "intentionally_absent", "unresolved_fit")

_SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9_-]*$")
_SEMVER_RE = re.compile(
    r"^(0|[1-9][0-9]*)\."
    r"(0|[1-9][0-9]*)\."
    r"(0|[1-9][0-9]*)"
    r"(?:-((?:0|[1-9][0-9]*|[0-9A-Za-z-]*[A-Za-z-][0-9A-Za-z-]*)"
    r"(?:\.(?:0|[1-9][0-9]*|[0-9A-Za-z-]*[A-Za-z-][0-9A-Za-z-]*))*))?"
    r"(?:\+([0-9A-Za-z-]+(?:\.[0-9A-Za-z-]+)*))?$"
)
_SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
_DATE_RE = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
_RFC3339_DATETIME_RE = re.compile(
    r"^[0-9]{4}-[0-9]{2}-[0-9]{2}[Tt]"
    r"(?:[01][0-9]|2[0-3]):[0-5][0-9]:[0-5][0-9]"
    r"(?:\.[0-9]{1,6})?(?:[Zz]|[+-](?:[01][0-9]|2[0-3]):[0-5][0-9])$"
)

_PROFILE_REQUIRED = {
    "schema_version",
    "profile_id",
    "profile_version",
    "research_family",
    "display_name",
    "stage_map",
    "alternative_categories",
    "branch_budget",
    "overflow_behavior",
    "authority_points",
    "known_exclusions",
    "unresolved_fit_note",
    "provenance",
    "content_sha256",
}
_PROFILE_OPTIONAL = {"declared_family_label", "evidence_overlays"}
_BINDING_FIELDS = {"profile_id", "profile_version", "content_sha256"}
_SELECTION_FIELDS = {
    "sequence",
    "profile_binding",
    "selected_by",
    "ars_suite_version",
    "selected_at",
    "supersedes_sequence",
}
_STALE_MARK_FIELDS = {
    "artifact_ref",
    "task_family",
    "produced_under_selection_sequence",
    "caused_by_selection_sequence",
    "state",
    "reason",
    "marked_at",
    "authority_requirements_introduced",
    "authority_sensitive_reuse_gate",
}
_AUTHORITY_FIELDS = {"task_family", "authority", "requirement"}


class ContractError(ValueError):
    """Raised when a profile, receipt, or correction input fails closed."""


def _fail(path: str, message: str) -> NoReturn:
    raise ContractError(f"{path}: {message}")


def _reject_constant(value: str) -> NoReturn:
    raise ContractError(f"non-finite JSON number is not allowed: {value}")


def _reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise ContractError(f"duplicate JSON key is not allowed: {key}")
        value[key] = item
    return value


def _reject_non_jcs_numbers(value: Any, path: str = "document") -> None:
    if isinstance(value, float):
        _fail(path, "floating-point values are outside this contract's JCS domain")
    if (
        isinstance(value, int)
        and not isinstance(value, bool)
        and abs(value) > JCS_SAFE_INTEGER_MAX
    ):
        _fail(path, "integer is outside the interoperable JCS safe range")
    if isinstance(value, dict):
        for key, item in value.items():
            _reject_non_jcs_numbers(item, f"{path}.{key}")
    elif isinstance(value, list):
        for index, item in enumerate(value):
            _reject_non_jcs_numbers(item, f"{path}[{index}]")


def canonical_bytes(value: Any) -> bytes:
    """Restricted JCS bytes for the closed, integer-only #742 value domain."""

    _reject_non_jcs_numbers(value)
    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, UnicodeEncodeError, ValueError) as exc:
        raise ContractError(f"value cannot be serialized as canonical JSON: {exc}") from exc


def load_json(path: Path, *, require_canonical: bool = False) -> dict[str, Any]:
    try:
        raw = path.read_bytes()
    except OSError as exc:
        raise ContractError(f"cannot read JSON input {path}: {exc}") from exc
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ContractError(f"JSON input is not UTF-8: {path}") from exc
    try:
        value = json.loads(
            text,
            object_pairs_hook=_reject_duplicate_pairs,
            parse_constant=_reject_constant,
        )
    except (json.JSONDecodeError, ContractError) as exc:
        raise ContractError(f"cannot parse JSON input {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"top-level JSON value must be an object: {path}")
    if require_canonical and raw != canonical_bytes(value):
        raise ContractError(
            f"profile file must be stored as exact JSON Canonical Form bytes: {path}"
        )
    return value


def _object(
    value: Any,
    path: str,
    required: set[str],
    optional: set[str] | None = None,
) -> dict[str, Any]:
    if not isinstance(value, dict):
        _fail(path, "must be an object")
    optional = optional or set()
    missing = required - set(value)
    extra = set(value) - required - optional
    if missing:
        _fail(path, f"missing field(s): {', '.join(sorted(missing))}")
    if extra:
        _fail(path, f"undeclared field(s): {', '.join(sorted(extra))}")
    return value


def _text(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value.strip():
        _fail(path, "must be a non-empty string")
    return value


def _enum(value: Any, path: str, allowed: Sequence[str]) -> str:
    if value not in allowed:
        _fail(path, f"must be one of: {', '.join(allowed)}")
    return value


def _slug(value: Any, path: str) -> str:
    text = _text(value, path)
    if _SLUG_RE.fullmatch(text) is None:
        _fail(path, "must be a lowercase slug using letters, digits, '_' or '-'")
    return text


def _semver(value: Any, path: str) -> str:
    text = _text(value, path)
    if _SEMVER_RE.fullmatch(text) is None:
        _fail(path, "must be a SemVer 2.0.0 version")
    return text


def _sha256(value: Any, path: str) -> str:
    text = _text(value, path)
    if _SHA256_RE.fullmatch(text) is None:
        _fail(path, "must be a lowercase 64-hex SHA-256 digest")
    return text


def _iso_date(value: Any, path: str) -> date:
    text = _text(value, path)
    try:
        if _DATE_RE.fullmatch(text) is None:
            raise ValueError
        return date.fromisoformat(text)
    except ValueError as exc:
        raise ContractError(f"{path}: must be an ISO 8601 date") from exc


def _iso_datetime(value: Any, path: str) -> datetime:
    text = _text(value, path)
    try:
        if _RFC3339_DATETIME_RE.fullmatch(text) is None:
            raise ValueError
        normalized = text[:10] + "T" + text[11:]
        if normalized.endswith(("Z", "z")):
            normalized = normalized[:-1] + "+00:00"
        parsed = datetime.fromisoformat(normalized)
        if parsed.tzinfo is None or parsed.utcoffset() is None:
            raise ValueError
        return parsed
    except ValueError as exc:
        raise ContractError(f"{path}: must be an ISO 8601 date-time with offset") from exc


def _unique_text_list(value: Any, path: str) -> list[str]:
    if not isinstance(value, list):
        _fail(path, "must be an array")
    result: list[str] = []
    for index, item in enumerate(value):
        result.append(_text(item, f"{path}[{index}]"))
    if len(set(result)) != len(result):
        _fail(path, "must not contain duplicate values")
    return result


def _positive_int(value: Any, path: str) -> int:
    if (
        isinstance(value, bool)
        or not isinstance(value, int)
        or value < 1
        or value > JCS_SAFE_INTEGER_MAX
    ):
        _fail(
            path,
            "must be an integer from 1 through the interoperable JCS safe maximum",
        )
    return value


def _validate_authority_point(value: Any, path: str) -> dict[str, Any]:
    point = _object(value, path, _AUTHORITY_FIELDS)
    _enum(point["task_family"], f"{path}.task_family", TASK_FAMILIES)
    _text(point["authority"], f"{path}.authority")
    _text(point["requirement"], f"{path}.requirement")
    return point


def profile_digest(profile: Mapping[str, Any]) -> str:
    """Compute the self-referential profile digest using the zero placeholder."""

    candidate = copy.deepcopy(dict(profile))
    candidate["content_sha256"] = PROFILE_HASH_PLACEHOLDER
    return hashlib.sha256(canonical_bytes(candidate)).hexdigest()


def validate_profile(profile: Mapping[str, Any], *, verify_digest: bool = True) -> None:
    value = _object(dict(profile), "profile", _PROFILE_REQUIRED, _PROFILE_OPTIONAL)
    if value["schema_version"] != PROFILE_SCHEMA_VERSION:
        _fail("profile.schema_version", f"must equal {PROFILE_SCHEMA_VERSION}")
    _slug(value["profile_id"], "profile.profile_id")
    _semver(value["profile_version"], "profile.profile_version")
    family = _enum(
        value["research_family"], "profile.research_family", RESEARCH_FAMILIES
    )

    display = _object(value["display_name"], "profile.display_name", {"en", "zh_TW"})
    _text(display["en"], "profile.display_name.en")
    _text(display["zh_TW"], "profile.display_name.zh_TW")

    stage_map = value["stage_map"]
    if not isinstance(stage_map, dict):
        _fail("profile.stage_map", "must be an object")
    unknown_stages = set(stage_map) - set(TASK_FAMILIES)
    if unknown_stages:
        _fail(
            "profile.stage_map",
            f"unknown task-family key(s): {', '.join(sorted(unknown_stages))}",
        )
    for task_family, raw_state in stage_map.items():
        state_obj = _object(
            raw_state,
            f"profile.stage_map.{task_family}",
            {"state"},
            {"reason"},
        )
        state = _enum(
            state_obj["state"],
            f"profile.stage_map.{task_family}.state",
            STAGE_STATES,
        )
        if state == "intentionally_absent":
            if "reason" not in state_obj:
                _fail(
                    f"profile.stage_map.{task_family}",
                    "intentionally_absent requires reason",
                )
            _text(state_obj["reason"], f"profile.stage_map.{task_family}.reason")
        elif "reason" in state_obj:
            _fail(
                f"profile.stage_map.{task_family}",
                "reason is lawful only for intentionally_absent",
            )

    alternatives = _object(
        value["alternative_categories"],
        "profile.alternative_categories",
        {"state", "categories"},
    )
    alternative_state = _enum(
        alternatives["state"],
        "profile.alternative_categories.state",
        ("declared", "unresolved"),
    )
    categories = alternatives["categories"]
    if not isinstance(categories, list):
        _fail("profile.alternative_categories.categories", "must be an array")
    for index, category in enumerate(categories):
        _enum(
            category,
            f"profile.alternative_categories.categories[{index}]",
            ALTERNATIVE_CATEGORIES,
        )
    if len(set(categories)) != len(categories):
        _fail("profile.alternative_categories.categories", "must not contain duplicates")
    if alternative_state == "unresolved" and categories:
        _fail(
            "profile.alternative_categories.categories",
            "must be empty when state is unresolved",
        )

    _positive_int(value["branch_budget"], "profile.branch_budget")
    if value["overflow_behavior"] != "ask_merge_park_archive":
        _fail(
            "profile.overflow_behavior", "must equal ask_merge_park_archive"
        )

    if "evidence_overlays" in value:
        overlays = value["evidence_overlays"]
        if not isinstance(overlays, list):
            _fail("profile.evidence_overlays", "must be an array")
        seen_overlays: set[tuple[str, str]] = set()
        for index, raw_overlay in enumerate(overlays):
            path = f"profile.evidence_overlays[{index}]"
            overlay = _object(raw_overlay, path, {"name", "pointer"})
            identity = (
                _text(overlay["name"], f"{path}.name"),
                _text(overlay["pointer"], f"{path}.pointer"),
            )
            if identity in seen_overlays:
                _fail("profile.evidence_overlays", "must not contain duplicates")
            seen_overlays.add(identity)

    authority_points = value["authority_points"]
    if not isinstance(authority_points, list):
        _fail("profile.authority_points", "must be an array")
    authority_identities: set[bytes] = set()
    for index, raw_point in enumerate(authority_points):
        point = _validate_authority_point(
            raw_point, f"profile.authority_points[{index}]"
        )
        identity = canonical_bytes(point)
        if identity in authority_identities:
            _fail("profile.authority_points", "must not contain duplicate entries")
        authority_identities.add(identity)
    if family == "field_general" and authority_points:
        _fail(
            "profile.authority_points",
            "must be empty for every field_general profile; empty means ask the user",
        )
    if family != "field_general" and not authority_points:
        _fail(
            "profile.authority_points",
            "may be empty only when research_family is field_general",
        )

    _unique_text_list(value["known_exclusions"], "profile.known_exclusions")
    _text(value["unresolved_fit_note"], "profile.unresolved_fit_note")

    provenance = _object(
        value["provenance"],
        "profile.provenance",
        {"source", "source_pointer", "last_reviewed_at", "freshness_state"},
    )
    source = _enum(
        provenance["source"], "profile.provenance.source", PROFILE_SOURCES
    )
    _text(provenance["source_pointer"], "profile.provenance.source_pointer")
    _iso_date(provenance["last_reviewed_at"], "profile.provenance.last_reviewed_at")
    _enum(
        provenance["freshness_state"],
        "profile.provenance.freshness_state",
        FRESHNESS_STATES,
    )

    if "declared_family_label" in value:
        _text(value["declared_family_label"], "profile.declared_family_label")
        if source != "user_authored":
            _fail(
                "profile.declared_family_label",
                "is lawful only when provenance.source is user_authored",
            )

    embedded_digest = _sha256(value["content_sha256"], "profile.content_sha256")
    if verify_digest:
        expected = profile_digest(value)
        if embedded_digest != expected:
            _fail(
                "profile.content_sha256",
                f"digest mismatch (embedded {embedded_digest}, recomputed {expected})",
            )


def seal_profile(profile: Mapping[str, Any]) -> dict[str, Any]:
    """Return a deep-copied profile with its canonical content digest finalized."""

    sealed = copy.deepcopy(dict(profile))
    sealed["content_sha256"] = PROFILE_HASH_PLACEHOLDER
    validate_profile(sealed, verify_digest=False)
    sealed["content_sha256"] = profile_digest(sealed)
    validate_profile(sealed)
    return sealed


def load_profile(path: Path) -> dict[str, Any]:
    """Load, canonical-storage check, close-shape check, and digest-check a profile."""

    profile = load_json(path, require_canonical=True)
    validate_profile(profile)
    return profile


def effective_stage_map(profile: Mapping[str, Any]) -> dict[str, dict[str, str]]:
    """Expand omitted task families to explicit unresolved_fit without mutation."""

    validate_profile(profile)
    declared = profile["stage_map"]
    return {
        task_family: copy.deepcopy(
            declared.get(task_family, {"state": "unresolved_fit"})
        )
        for task_family in TASK_FAMILIES
    }


def profile_binding(profile: Mapping[str, Any]) -> dict[str, str]:
    validate_profile(profile)
    return {
        "profile_id": str(profile["profile_id"]),
        "profile_version": str(profile["profile_version"]),
        "content_sha256": str(profile["content_sha256"]),
    }


def validate_profile_catalog(profiles: Sequence[Mapping[str, Any]]) -> None:
    """Refuse two different documents published under one id/version pair."""

    seen: dict[tuple[str, str], bytes] = {}
    for index, profile in enumerate(profiles):
        validate_profile(profile)
        key = (str(profile["profile_id"]), str(profile["profile_version"]))
        raw = canonical_bytes(profile)
        if key in seen and seen[key] != raw:
            _fail(
                f"profiles[{index}]",
                f"different canonical content reuses immutable version {key[0]}@{key[1]}",
            )
        seen[key] = raw


def validate_shipped_field_general(profile: Mapping[str, Any]) -> None:
    """Pin the mandatory shipped fallback values from design §4."""

    validate_profile(profile)
    if profile["profile_id"] != "field_general":
        _fail("profile.profile_id", "shipped fallback must equal field_general")
    if profile["research_family"] != "field_general":
        _fail("profile.research_family", "shipped fallback must equal field_general")
    if profile["display_name"] != RESEARCH_FAMILY_DISPLAY_NAMES["field_general"]:
        _fail("profile.display_name", "does not equal the shipped en/zh_TW names")
    if set(profile["stage_map"]) != set(TASK_FAMILIES):
        _fail("profile.stage_map", "shipped fallback must name every task family")
    for task_family in TASK_FAMILIES:
        expected = "applicable" if task_family == "integrity_check" else "unresolved_fit"
        if profile["stage_map"][task_family] != {"state": expected}:
            _fail(
                f"profile.stage_map.{task_family}",
                f"shipped fallback must be exactly state={expected}",
            )
    if profile["alternative_categories"] != {"state": "unresolved", "categories": []}:
        _fail("profile.alternative_categories", "shipped fallback must stay unresolved")
    if profile["branch_budget"] != 3:
        _fail("profile.branch_budget", "shipped fallback must equal 3")
    if profile["authority_points"] != []:
        _fail("profile.authority_points", "shipped fallback must be empty (ask user)")
    if profile["provenance"]["source"] != "shipped_default":
        _fail("profile.provenance.source", "shipped fallback must be shipped_default")
    if (
        profile["provenance"]["source_pointer"]
        != "shared/research_workflow_profiles/field_general.json"
    ):
        _fail("profile.provenance.source_pointer", "does not name the shipped file")
    if "declared_family_label" in profile:
        _fail("profile.declared_family_label", "shipped fallback must not carry one")
    if profile.get("evidence_overlays", []) != []:
        _fail("profile.evidence_overlays", "shipped fallback must not claim an overlay")


def _validate_binding(value: Any, path: str) -> dict[str, Any]:
    binding = _object(value, path, _BINDING_FIELDS)
    _slug(binding["profile_id"], f"{path}.profile_id")
    _semver(binding["profile_version"], f"{path}.profile_version")
    _sha256(binding["content_sha256"], f"{path}.content_sha256")
    return binding


def _validate_selection(value: Any, path: str) -> tuple[dict[str, Any], datetime]:
    selection = _object(value, path, _SELECTION_FIELDS)
    _positive_int(selection["sequence"], f"{path}.sequence")
    binding = _validate_binding(selection["profile_binding"], f"{path}.profile_binding")
    selected_by = _enum(
        selection["selected_by"], f"{path}.selected_by", SELECTION_SOURCES
    )
    if selected_by == "fallback_automatic" and binding["profile_id"] != "field_general":
        _fail(
            f"{path}.selected_by",
            "fallback_automatic may bind only the field_general fallback",
        )
    _text(selection["ars_suite_version"], f"{path}.ars_suite_version")
    selected_at = _iso_datetime(selection["selected_at"], f"{path}.selected_at")
    supersedes = selection["supersedes_sequence"]
    if supersedes is not None and (
        isinstance(supersedes, bool) or not isinstance(supersedes, int) or supersedes < 1
    ):
        _fail(f"{path}.supersedes_sequence", "must be null or a positive integer")
    return selection, selected_at


def validate_selection_receipt(receipt: Mapping[str, Any]) -> None:
    value = _object(
        dict(receipt),
        "receipt",
        {"schema_version", "selection_chain", "artifact_stale_marks"},
    )
    if value["schema_version"] != RECEIPT_SCHEMA_VERSION:
        _fail("receipt.schema_version", f"must equal {RECEIPT_SCHEMA_VERSION}")
    chain = value["selection_chain"]
    if not isinstance(chain, list) or not chain:
        _fail("receipt.selection_chain", "must be a non-empty array")
    prior_time: datetime | None = None
    for index, raw_selection in enumerate(chain):
        path = f"receipt.selection_chain[{index}]"
        selection, selected_at = _validate_selection(raw_selection, path)
        expected_sequence = index + 1
        if selection["sequence"] != expected_sequence:
            _fail(f"{path}.sequence", f"must equal dense sequence {expected_sequence}")
        expected_supersedes = None if index == 0 else index
        if selection["supersedes_sequence"] != expected_supersedes:
            _fail(
                f"{path}.supersedes_sequence",
                f"must equal {expected_supersedes!r}",
            )
        if prior_time is not None and selected_at <= prior_time:
            _fail(f"{path}.selected_at", "must be later than the prior selection")
        prior_time = selected_at

    stale_marks = value["artifact_stale_marks"]
    if not isinstance(stale_marks, list):
        _fail("receipt.artifact_stale_marks", "must be an array")
    seen_marks: set[tuple[str, int]] = set()
    for index, raw_mark in enumerate(stale_marks):
        path = f"receipt.artifact_stale_marks[{index}]"
        mark = _object(raw_mark, path, _STALE_MARK_FIELDS)
        artifact_ref = _text(mark["artifact_ref"], f"{path}.artifact_ref")
        _enum(mark["task_family"], f"{path}.task_family", TASK_FAMILIES)
        produced = _positive_int(
            mark["produced_under_selection_sequence"],
            f"{path}.produced_under_selection_sequence",
        )
        caused = _positive_int(
            mark["caused_by_selection_sequence"],
            f"{path}.caused_by_selection_sequence",
        )
        if caused > len(chain):
            _fail(f"{path}.caused_by_selection_sequence", "does not resolve in chain")
        if produced != caused - 1:
            _fail(
                path,
                "must bind an artifact produced under the immediately prior selection",
            )
        if mark["state"] != "stale":
            _fail(f"{path}.state", "must equal stale")
        if mark["reason"] != "profile_context_changed":
            _fail(f"{path}.reason", "must equal profile_context_changed")
        _iso_datetime(mark["marked_at"], f"{path}.marked_at")
        if mark["marked_at"] != chain[caused - 1]["selected_at"]:
            _fail(
                f"{path}.marked_at",
                "must equal the causing correction's selected_at timestamp",
            )
        requirements = mark["authority_requirements_introduced"]
        if not isinstance(requirements, list):
            _fail(f"{path}.authority_requirements_introduced", "must be an array")
        seen_requirements: set[bytes] = set()
        for req_index, raw_requirement in enumerate(requirements):
            requirement = _validate_authority_point(
                raw_requirement,
                f"{path}.authority_requirements_introduced[{req_index}]",
            )
            encoded = canonical_bytes(requirement)
            if encoded in seen_requirements:
                _fail(
                    f"{path}.authority_requirements_introduced",
                    "must not contain duplicate entries",
                )
            seen_requirements.add(encoded)
        expected_gate = "unmet" if requirements else "not_introduced"
        if mark["authority_sensitive_reuse_gate"] != expected_gate:
            _fail(
                f"{path}.authority_sensitive_reuse_gate",
                f"must equal {expected_gate} for the introduced-requirements list",
            )
        mark_identity = (artifact_ref, caused)
        if mark_identity in seen_marks:
            _fail(path, "duplicates an artifact stale mark for this correction")
        seen_marks.add(mark_identity)


def _validate_selection_source(
    profile: Mapping[str, Any],
    selected_by: str,
    *,
    require_current_shipped: bool = True,
) -> None:
    _enum(selected_by, "selected_by", SELECTION_SOURCES)
    if selected_by == "fallback_automatic":
        validate_shipped_field_general(profile)
        shipped = load_profile(DEFAULT_FIELD_GENERAL_PROFILE)
        if require_current_shipped and profile_binding(profile) != profile_binding(shipped):
            _fail(
                "selected_by",
                "fallback_automatic must bind the exact currently shipped field_general profile",
            )


def create_selection_receipt(
    profile: Mapping[str, Any],
    *,
    selected_by: str,
    ars_suite_version: str,
    selected_at: str,
) -> dict[str, Any]:
    """Create one explicit initial selection receipt; no manuscript inference."""

    validate_profile(profile)
    _validate_selection_source(profile, selected_by)
    _text(ars_suite_version, "ars_suite_version")
    _iso_datetime(selected_at, "selected_at")
    receipt = {
        "schema_version": RECEIPT_SCHEMA_VERSION,
        "selection_chain": [
            {
                "sequence": 1,
                "profile_binding": profile_binding(profile),
                "selected_by": selected_by,
                "ars_suite_version": ars_suite_version,
                "selected_at": selected_at,
                "supersedes_sequence": None,
            }
        ],
        "artifact_stale_marks": [],
    }
    validate_selection_receipt(receipt)
    return receipt


def create_fallback_receipt(
    *, ars_suite_version: str, selected_at: str
) -> dict[str, Any]:
    """Make the no-selection state an explicit, visible field-general receipt."""

    profile = load_profile(DEFAULT_FIELD_GENERAL_PROFILE)
    validate_shipped_field_general(profile)
    return create_selection_receipt(
        profile,
        selected_by="fallback_automatic",
        ars_suite_version=ars_suite_version,
        selected_at=selected_at,
    )


def _introduced_authority_points(
    previous_profile: Mapping[str, Any], replacement_profile: Mapping[str, Any]
) -> list[dict[str, str]]:
    previous = {
        canonical_bytes(point) for point in previous_profile["authority_points"]
    }
    return [
        copy.deepcopy(point)
        for point in replacement_profile["authority_points"]
        if canonical_bytes(point) not in previous
    ]


def _validate_stage_outputs(value: Any) -> list[dict[str, str]]:
    if not isinstance(value, list):
        _fail("stage_outputs", "must be an array")
    result: list[dict[str, str]] = []
    seen_refs: set[str] = set()
    for index, raw_output in enumerate(value):
        path = f"stage_outputs[{index}]"
        output = _object(raw_output, path, {"artifact_ref", "task_family"})
        artifact_ref = _text(output["artifact_ref"], f"{path}.artifact_ref")
        task_family = _enum(
            output["task_family"], f"{path}.task_family", TASK_FAMILIES
        )
        if artifact_ref in seen_refs:
            _fail(path, f"duplicate artifact_ref: {artifact_ref}")
        seen_refs.add(artifact_ref)
        result.append({"artifact_ref": artifact_ref, "task_family": task_family})
    return result


def correct_selection(
    receipt: Mapping[str, Any],
    previous_profile: Mapping[str, Any],
    replacement_profile: Mapping[str, Any],
    stage_outputs: Sequence[Mapping[str, Any]],
    *,
    selected_by: str,
    ars_suite_version: str,
    selected_at: str,
) -> dict[str, Any]:
    """Append a correction and non-destructive stale marks for prior outputs."""

    validate_selection_receipt(receipt)
    validate_profile(previous_profile)
    validate_profile(replacement_profile)
    _validate_selection_source(replacement_profile, selected_by)
    _text(ars_suite_version, "ars_suite_version")
    _iso_datetime(selected_at, "selected_at")
    outputs = _validate_stage_outputs(list(stage_outputs))

    current = receipt["selection_chain"][-1]
    previous_binding = profile_binding(previous_profile)
    replacement_binding = profile_binding(replacement_profile)
    if current["profile_binding"] != previous_binding:
        _fail(
            "previous_profile",
            "binding does not equal the current selection receipt binding",
        )
    _validate_selection_source(
        previous_profile,
        current["selected_by"],
        require_current_shipped=False,
    )
    if replacement_binding == previous_binding:
        _fail("replacement_profile", "correction must change the profile binding")

    prior_time = _iso_datetime(current["selected_at"], "current.selected_at")
    correction_time = _iso_datetime(selected_at, "selected_at")
    if correction_time <= prior_time:
        _fail("selected_at", "must be later than the current selection")

    updated = copy.deepcopy(dict(receipt))
    new_sequence = len(updated["selection_chain"]) + 1
    updated["selection_chain"].append(
        {
            "sequence": new_sequence,
            "profile_binding": replacement_binding,
            "selected_by": selected_by,
            "ars_suite_version": ars_suite_version,
            "selected_at": selected_at,
            "supersedes_sequence": new_sequence - 1,
        }
    )

    introduced = _introduced_authority_points(previous_profile, replacement_profile)
    for output in outputs:
        updated["artifact_stale_marks"].append(
            {
                "artifact_ref": output["artifact_ref"],
                "task_family": output["task_family"],
                "produced_under_selection_sequence": new_sequence - 1,
                "caused_by_selection_sequence": new_sequence,
                "state": "stale",
                "reason": "profile_context_changed",
                "marked_at": selected_at,
                # The list is intentionally attached to each stale mark.  A
                # downstream consumer gates only authority-sensitive reuse;
                # absence never means an authority is unnecessary in general.
                "authority_requirements_introduced": copy.deepcopy(introduced),
                "authority_sensitive_reuse_gate": (
                    "unmet" if introduced else "not_introduced"
                ),
            }
        )
    validate_selection_receipt(updated)
    return updated


def active_selection_summary(
    receipt: Mapping[str, Any], profile: Mapping[str, Any]
) -> dict[str, Any]:
    """Return a compact display model that never hides an active fallback."""

    validate_selection_receipt(receipt)
    validate_profile(profile)
    current = receipt["selection_chain"][-1]
    if current["profile_binding"] != profile_binding(profile):
        _fail("profile", "binding does not equal the receipt's active selection")
    _validate_selection_source(
        profile,
        current["selected_by"],
        require_current_shipped=False,
    )
    try:
        validate_shipped_field_general(profile)
    except ContractError:
        fallback_active = False
    else:
        fallback_active = True
    return {
        "profile_id": profile["profile_id"],
        "profile_version": profile["profile_version"],
        "research_family": profile["research_family"],
        "declared_family_label": profile.get("declared_family_label"),
        "display_name": copy.deepcopy(profile["display_name"]),
        "selected_by": current["selected_by"],
        "fallback_active": fallback_active,
        "fallback_notice": (
            "Field-specific fit and authority points remain unresolved; ask the user."
            if fallback_active
            else None
        ),
        "freshness_state": profile["provenance"]["freshness_state"],
        "correction_count": len(receipt["selection_chain"]) - 1,
    }


def _load_stage_outputs(path: Path) -> list[dict[str, Any]]:
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_pairs,
            parse_constant=_reject_constant,
        )
    except (OSError, json.JSONDecodeError, ContractError) as exc:
        raise ContractError(f"cannot read stage-output inventory {path}: {exc}") from exc
    return _validate_stage_outputs(value)


def _emit_json(value: Any) -> None:
    sys.stdout.buffer.write(canonical_bytes(value) + b"\n")


def _selected_profile(path: Path | None) -> tuple[dict[str, Any], bool]:
    if path is None:
        profile = load_profile(DEFAULT_FIELD_GENERAL_PROFILE)
        validate_shipped_field_general(profile)
        return profile, True
    return load_profile(path), False


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    validate_profile_parser = subparsers.add_parser("validate-profile")
    validate_profile_parser.add_argument("profile", type=Path)
    validate_profile_parser.add_argument("--shipped-field-general", action="store_true")

    validate_receipt_parser = subparsers.add_parser("validate-receipt")
    validate_receipt_parser.add_argument("receipt", type=Path)

    select_parser = subparsers.add_parser("select")
    select_parser.add_argument("--profile", type=Path)
    select_parser.add_argument("--selected-by", choices=SELECTION_SOURCES)
    select_parser.add_argument("--ars-suite-version", required=True)
    select_parser.add_argument("--selected-at", required=True)

    correct_parser = subparsers.add_parser("correct")
    correct_parser.add_argument("--receipt", required=True, type=Path)
    correct_parser.add_argument("--previous-profile", required=True, type=Path)
    correct_parser.add_argument("--profile", type=Path)
    correct_parser.add_argument("--selected-by", choices=SELECTION_SOURCES)
    correct_parser.add_argument("--ars-suite-version", required=True)
    correct_parser.add_argument("--selected-at", required=True)
    correct_parser.add_argument("--stage-outputs", required=True, type=Path)

    show_parser = subparsers.add_parser("show-selection")
    show_parser.add_argument("--receipt", required=True, type=Path)
    show_parser.add_argument("--profile", required=True, type=Path)

    args = parser.parse_args(argv)
    try:
        if args.command == "validate-profile":
            profile = load_profile(args.profile)
            if args.shipped_field_general:
                validate_shipped_field_general(profile)
            print(f"PASS: valid {PROFILE_SCHEMA_VERSION} profile")
            return 0
        if args.command == "validate-receipt":
            validate_selection_receipt(load_json(args.receipt))
            print(f"PASS: valid {RECEIPT_SCHEMA_VERSION} receipt")
            return 0
        if args.command == "select":
            profile, automatic = _selected_profile(args.profile)
            selected_by = args.selected_by
            if automatic:
                if selected_by not in (None, "fallback_automatic"):
                    _fail(
                        "selected_by",
                        "omitting --profile is the automatic fallback path",
                    )
                selected_by = "fallback_automatic"
            elif selected_by is None:
                _fail("selected_by", "is required when --profile is supplied")
            _emit_json(
                create_selection_receipt(
                    profile,
                    selected_by=selected_by,
                    ars_suite_version=args.ars_suite_version,
                    selected_at=args.selected_at,
                )
            )
            return 0
        if args.command == "correct":
            receipt = load_json(args.receipt)
            previous = load_profile(args.previous_profile)
            replacement, automatic = _selected_profile(args.profile)
            selected_by = args.selected_by
            if automatic:
                if selected_by not in (None, "fallback_automatic"):
                    _fail(
                        "selected_by",
                        "omitting --profile is the automatic fallback path",
                    )
                selected_by = "fallback_automatic"
            elif selected_by is None:
                _fail("selected_by", "is required when --profile is supplied")
            _emit_json(
                correct_selection(
                    receipt,
                    previous,
                    replacement,
                    _load_stage_outputs(args.stage_outputs),
                    selected_by=selected_by,
                    ars_suite_version=args.ars_suite_version,
                    selected_at=args.selected_at,
                )
            )
            return 0
        if args.command == "show-selection":
            _emit_json(
                active_selection_summary(
                    load_json(args.receipt), load_profile(args.profile)
                )
            )
            return 0
    except ContractError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    return 2


if __name__ == "__main__":
    sys.exit(main())
