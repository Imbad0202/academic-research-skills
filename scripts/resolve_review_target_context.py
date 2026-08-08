#!/usr/bin/env python3
"""Resolve an author-confirmed review target against a versioned criteria registry.

The resolver is intentionally blind to manuscript content. It opens only the two
explicit input paths and any explicitly requested output paths.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from collections import defaultdict
from datetime import date, datetime
from pathlib import Path
from typing import Any, NoReturn


AUTHORITY_CLASSES = (
    "official_venue_type",
    "field_society_standard",
    "reporting_design_overlay",
    "broad_field_fallback",
)
DIMENSIONS = ("scientific_validity", "venue_fit", "submission_readiness")
FRESHNESS = ("current", "stale", "unverified")
SELECTION_MODES = ("all_applicable", "explicit")
ID_PATTERN = re.compile(r"^[a-z0-9][a-z0-9._-]*$")
DATE_PATTERN = re.compile(r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")


class ContractError(ValueError):
    """Raised when an input violates the closed V1 contract."""


def _reject_constant(value: str) -> NoReturn:
    raise ContractError(f"non-finite JSON number is not allowed: {value}")


def _reject_duplicate_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ContractError(f"duplicate JSON key is not allowed: {key}")
        result[key] = value
    return result


def load_json(path: Path) -> dict[str, Any]:
    try:
        with path.open("r", encoding="utf-8") as handle:
            value = json.load(
                handle,
                object_pairs_hook=_reject_duplicate_pairs,
                parse_constant=_reject_constant,
            )
    except (OSError, json.JSONDecodeError) as exc:
        raise ContractError(f"cannot read JSON input {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ContractError(f"top-level JSON value must be an object: {path}")
    return value


def _canonical_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False
    ).encode("utf-8")


def digest(value: Any) -> str:
    return hashlib.sha256(_canonical_bytes(value)).hexdigest()


def _fail(path: str, message: str) -> NoReturn:
    raise ContractError(f"{path}: {message}")


def _object(value: Any, path: str, required: set[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        _fail(path, "must be an object")
    actual = set(value)
    missing = required - actual
    extra = actual - required
    if missing:
        _fail(path, f"missing field(s): {', '.join(sorted(missing))}")
    if extra:
        _fail(path, f"undeclared field(s): {', '.join(sorted(extra))}")
    return value


def _string(value: Any, path: str, *, nullable: bool = False) -> str | None:
    if nullable and value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        _fail(path, "must be a non-empty string" + (" or null" if nullable else ""))
    return value


def _string_list(value: Any, path: str) -> list[str]:
    if not isinstance(value, list):
        _fail(path, "must be an array")
    result: list[str] = []
    seen: set[str] = set()
    for index, item in enumerate(value):
        text = _string(item, f"{path}[{index}]")
        assert text is not None
        if text in seen:
            _fail(path, f"duplicate value: {text}")
        seen.add(text)
        result.append(text)
    return result


def _enum(value: Any, path: str, allowed: tuple[str, ...]) -> str:
    if value not in allowed:
        _fail(path, f"must be one of: {', '.join(allowed)}")
    return value


def _date(value: Any, path: str) -> date:
    text = _string(value, path)
    try:
        assert text is not None
        if DATE_PATTERN.fullmatch(text) is None:
            raise ValueError
        return date.fromisoformat(text)
    except ValueError as exc:
        raise ContractError(f"{path}: must be an ISO 8601 date") from exc


def _datetime(value: Any, path: str) -> None:
    text = _string(value, path)
    try:
        assert text is not None
        if "T" not in text:
            raise ValueError
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
        if parsed.tzinfo is None:
            raise ValueError
    except ValueError as exc:
        raise ContractError(f"{path}: must be an ISO 8601 date-time") from exc


def _normalized(value: str) -> str:
    return " ".join(value.casefold().split())


def _identifier(value: Any, path: str) -> str:
    text = _string(value, path)
    assert text is not None
    if ID_PATTERN.fullmatch(text) is None:
        _fail(path, "must use lowercase letters, digits, dot, underscore, or hyphen")
    return text


def validate_declaration(value: dict[str, Any]) -> None:
    required = {
        "schema_version",
        "confirmed_by",
        "confirmed_at",
        "criteria_as_of",
        "discipline",
        "target",
        "reporting_design_overlays",
        "criterion_selection",
        "precedence",
    }
    obj = _object(value, "declaration", required)
    if obj["schema_version"] != "review-target-declaration/1.0":
        _fail("declaration.schema_version", "must equal review-target-declaration/1.0")
    if obj["confirmed_by"] != "author":
        _fail("declaration.confirmed_by", "must equal author")
    _datetime(obj["confirmed_at"], "declaration.confirmed_at")
    _date(obj["criteria_as_of"], "declaration.criteria_as_of")

    discipline = _object(
        obj["discipline"],
        "declaration.discipline",
        {"primary", "subfield", "additional_disciplines"},
    )
    primary = _string(discipline["primary"], "declaration.discipline.primary")
    subfield = _string(
        discipline["subfield"], "declaration.discipline.subfield", nullable=True
    )
    additional = _string_list(
        discipline["additional_disciplines"],
        "declaration.discipline.additional_disciplines",
    )
    discipline_values = [primary, *additional]
    if len({_normalized(item) for item in discipline_values if item is not None}) != len(
        discipline_values
    ):
        _fail("declaration.discipline", "discipline names must be unique")
    if subfield is not None and not subfield.strip():
        _fail("declaration.discipline.subfield", "must not be blank")

    target = _object(
        obj["target"], "declaration.target", {"venue", "track", "contribution_type"}
    )
    venue = _string(target["venue"], "declaration.target.venue", nullable=True)
    track = _string(target["track"], "declaration.target.track", nullable=True)
    _string(target["contribution_type"], "declaration.target.contribution_type")
    if venue is None and track is not None:
        _fail("declaration.target.track", "must be null when venue is null")
    if venue is not None and track is None:
        _fail("declaration.target.track", "must be declared when venue is declared")

    _string_list(
        obj["reporting_design_overlays"], "declaration.reporting_design_overlays"
    )
    selection = _object(
        obj["criterion_selection"],
        "declaration.criterion_selection",
        {"mode", "ids"},
    )
    mode = _enum(
        selection["mode"], "declaration.criterion_selection.mode", SELECTION_MODES
    )
    selected_ids = _string_list(selection["ids"], "declaration.criterion_selection.ids")
    for index, criterion_id in enumerate(selected_ids):
        _identifier(criterion_id, f"declaration.criterion_selection.ids[{index}]")
    if mode == "all_applicable" and selected_ids:
        _fail("declaration.criterion_selection.ids", "must be empty in all_applicable mode")
    if mode == "explicit" and not selected_ids:
        _fail("declaration.criterion_selection.ids", "must not be empty in explicit mode")

    precedence = obj["precedence"]
    if not isinstance(precedence, list) or len(precedence) != 4:
        _fail("declaration.precedence", "must contain exactly four entries")
    ranks: set[int] = set()
    classes: set[str] = set()
    for index, item in enumerate(precedence):
        entry = _object(
            item,
            f"declaration.precedence[{index}]",
            {"rank", "authority_class"},
        )
        rank = entry["rank"]
        if isinstance(rank, bool) or not isinstance(rank, int) or rank not in range(1, 5):
            _fail(f"declaration.precedence[{index}].rank", "must be an integer from 1 to 4")
        authority = _enum(
            entry["authority_class"],
            f"declaration.precedence[{index}].authority_class",
            AUTHORITY_CLASSES,
        )
        ranks.add(rank)
        classes.add(authority)
    if ranks != {1, 2, 3, 4}:
        _fail("declaration.precedence", "ranks must be unique and cover 1 through 4")
    if classes != set(AUTHORITY_CLASSES):
        _fail("declaration.precedence", "each authority class must occur exactly once")


def _validate_axes(value: Any, path: str) -> None:
    axes = _object(
        value,
        path,
        {"disciplines", "subfields", "venues", "tracks", "contribution_types", "overlays"},
    )
    for axis in axes:
        values = _string_list(axes[axis], f"{path}.{axis}")
        if any(item.strip() == "*" for item in values):
            _fail(f"{path}.{axis}", "wildcards are not allowed; use an empty list")


def validate_registry(value: dict[str, Any]) -> None:
    obj = _object(
        value,
        "registry",
        {"schema_version", "registry_id", "registry_version", "as_of", "authority_classes", "criteria"},
    )
    if obj["schema_version"] != "review-criteria-registry/1.0":
        _fail("registry.schema_version", "must equal review-criteria-registry/1.0")
    _identifier(obj["registry_id"], "registry.registry_id")
    _string(obj["registry_version"], "registry.registry_version")
    registry_as_of = _date(obj["as_of"], "registry.as_of")
    partitions = _object(
        obj["authority_classes"], "registry.authority_classes", set(AUTHORITY_CLASSES)
    )
    partition_ids: dict[str, list[str]] = {
        authority: _string_list(
            partitions[authority], f"registry.authority_classes.{authority}"
        )
        for authority in AUTHORITY_CLASSES
    }
    for authority, listed_ids in partition_ids.items():
        for index, criterion_id in enumerate(listed_ids):
            _identifier(
                criterion_id,
                f"registry.authority_classes.{authority}[{index}]",
            )
    criteria = obj["criteria"]
    if not isinstance(criteria, list):
        _fail("registry.criteria", "must be an array")
    ids: set[str] = set()
    row_authority: dict[str, str] = {}
    criterion_fields = {
        "criterion_id",
        "version",
        "authority_class",
        "dimension",
        "title",
        "statement",
        "source",
        "applicability",
        "exclusions",
        "blocking_policy",
        "conflict_group",
    }
    for index, item in enumerate(criteria):
        path = f"registry.criteria[{index}]"
        row = _object(item, path, criterion_fields)
        criterion_id = _identifier(row["criterion_id"], f"{path}.criterion_id")
        if criterion_id in ids:
            _fail(f"{path}.criterion_id", f"duplicate id: {criterion_id}")
        ids.add(criterion_id)
        _string(row["version"], f"{path}.version")
        authority = _enum(row["authority_class"], f"{path}.authority_class", AUTHORITY_CLASSES)
        row_authority[criterion_id] = authority
        _enum(row["dimension"], f"{path}.dimension", DIMENSIONS)
        _string(row["title"], f"{path}.title")
        _string(row["statement"], f"{path}.statement")
        source = _object(
            row["source"],
            f"{path}.source",
            {"title", "publisher", "uri", "effective_date", "verified_at", "freshness"},
        )
        for field in ("title", "publisher", "uri"):
            _string(source[field], f"{path}.source.{field}")
        _date(source["effective_date"], f"{path}.source.effective_date")
        verified = source["verified_at"]
        if verified is not None:
            verified_date = _date(verified, f"{path}.source.verified_at")
            if verified_date > registry_as_of:
                _fail(
                    f"{path}.source.verified_at",
                    "cannot be later than registry.as_of",
                )
        freshness = _enum(source["freshness"], f"{path}.source.freshness", FRESHNESS)
        if freshness == "current" and verified is None:
            _fail(f"{path}.source.verified_at", "is required for a current source")
        _validate_axes(row["applicability"], f"{path}.applicability")
        _validate_axes(row["exclusions"], f"{path}.exclusions")
        if row["blocking_policy"] not in ("blocking_allowed", "advisory_only"):
            _fail(f"{path}.blocking_policy", "must be blocking_allowed or advisory_only")
        if row["conflict_group"] is not None:
            _string(row["conflict_group"], f"{path}.conflict_group")

        axes = row["applicability"]
        if authority == "official_venue_type":
            for axis in ("venues", "tracks", "contribution_types"):
                if len(axes[axis]) != 1:
                    _fail(f"{path}.applicability.{axis}", "official rows require exactly one value")
        elif authority == "field_society_standard" and not axes["disciplines"]:
            _fail(f"{path}.applicability.disciplines", "field/society rows require a discipline")
        elif authority == "reporting_design_overlay" and not axes["overlays"]:
            _fail(f"{path}.applicability.overlays", "overlay rows require an overlay")
        elif authority == "broad_field_fallback":
            for axis in ("venues", "tracks", "contribution_types", "overlays"):
                if axes[axis]:
                    _fail(f"{path}.applicability.{axis}", "broad fallback rows cannot claim target or overlay authority")

    flattened: list[str] = []
    for authority, listed_ids in partition_ids.items():
        for criterion_id in listed_ids:
            if criterion_id in flattened:
                _fail("registry.authority_classes", f"id appears in more than one partition: {criterion_id}")
            flattened.append(criterion_id)
            if criterion_id not in ids:
                _fail(f"registry.authority_classes.{authority}", f"unknown criterion id: {criterion_id}")
            if row_authority[criterion_id] != authority:
                _fail(f"registry.authority_classes.{authority}", f"row authority mismatch: {criterion_id}")
    if set(flattened) != ids:
        missing = sorted(ids - set(flattened))
        _fail("registry.authority_classes", f"criterion absent from partition: {', '.join(missing)}")


def _context_axes(declaration: dict[str, Any]) -> dict[str, set[str]]:
    discipline = declaration["discipline"]
    target = declaration["target"]
    venue = [] if target["venue"] is None else [target["venue"]]
    track = [] if target["track"] is None else [target["track"]]
    subfield = [] if discipline["subfield"] is None else [discipline["subfield"]]
    return {
        "disciplines": {_normalized(item) for item in [discipline["primary"], *discipline["additional_disciplines"]]},
        "subfields": {_normalized(item) for item in subfield},
        "venues": {_normalized(item) for item in venue},
        "tracks": {_normalized(item) for item in track},
        "contribution_types": {_normalized(target["contribution_type"])},
        "overlays": {_normalized(item) for item in declaration["reporting_design_overlays"]},
    }


def _axis_intersects(values: list[str], actual: set[str]) -> bool:
    return bool({_normalized(item) for item in values} & actual)


def _applicable(row: dict[str, Any], declaration: dict[str, Any]) -> bool:
    if _date(row["source"]["effective_date"], "criterion.source.effective_date") > _date(
        declaration["criteria_as_of"], "declaration.criteria_as_of"
    ):
        return False
    actual = _context_axes(declaration)
    applicability = row["applicability"]
    for axis, values in applicability.items():
        if values and not _axis_intersects(values, actual[axis]):
            return False
    exclusions = row["exclusions"]
    for axis, values in exclusions.items():
        if values and _axis_intersects(values, actual[axis]):
            return False
    return True


def resolve(declaration: dict[str, Any], registry: dict[str, Any]) -> dict[str, Any]:
    validate_declaration(declaration)
    validate_registry(registry)
    if _date(declaration["criteria_as_of"], "declaration.criteria_as_of") > _date(
        registry["as_of"], "registry.as_of"
    ):
        _fail(
            "declaration.criteria_as_of",
            "cannot be later than registry.as_of; use a registry verified for the requested date",
        )
    rows = registry["criteria"]
    applicable = [row for row in rows if _applicable(row, declaration)]
    applicable_by_id = {row["criterion_id"]: row for row in applicable}
    all_by_id = {row["criterion_id"]: row for row in rows}

    selection = declaration["criterion_selection"]
    if selection["mode"] == "explicit":
        unknown = [item for item in selection["ids"] if item not in all_by_id]
        if unknown:
            _fail("declaration.criterion_selection.ids", f"unknown criterion id(s): {', '.join(unknown)}")
        inapplicable = [item for item in selection["ids"] if item not in applicable_by_id]
        if inapplicable:
            _fail("declaration.criterion_selection.ids", f"inapplicable criterion id(s): {', '.join(inapplicable)}")
        selected = [applicable_by_id[item] for item in selection["ids"]]
    else:
        selected = applicable

    rank_by_authority = {
        item["authority_class"]: item["rank"] for item in declaration["precedence"]
    }
    row_index = {row["criterion_id"]: index for index, row in enumerate(rows)}
    selected.sort(key=lambda row: (rank_by_authority[row["authority_class"]], row["criterion_id"]))

    pointers: list[dict[str, Any]] = []
    outcomes: dict[str, list[str]] = {dimension: [] for dimension in DIMENSIONS}
    conflicts: dict[str, list[str]] = defaultdict(list)
    for row in selected:
        freshness = row["source"]["freshness"]
        advisory_reasons: list[str] = []
        if freshness != "current":
            advisory_reasons.append(f"source_{freshness}")
        if row["blocking_policy"] == "advisory_only":
            advisory_reasons.append("registry_policy_advisory_only")
        pointer = {
            "criterion_id": row["criterion_id"],
            "criterion_version": row["version"],
            "criterion_digest": digest(row),
            "authority_class": row["authority_class"],
            "authority_rank": rank_by_authority[row["authority_class"]],
            "dimension": row["dimension"],
            "source_uri": row["source"]["uri"],
            "source_freshness": freshness,
            "blocking_eligible": freshness == "current" and row["blocking_policy"] == "blocking_allowed",
            "advisory_reasons": advisory_reasons,
            "registry_pointer": f"/criteria/{row_index[row['criterion_id']]}",
        }
        pointers.append(pointer)
        outcomes[row["dimension"]].append(row["criterion_id"])
        if row["conflict_group"] is not None:
            conflicts[row["conflict_group"]].append(row["criterion_id"])

    parallel_conflicts = [
        {
            "conflict_group": group,
            "criterion_ids": sorted(ids),
            "reason": "parallel_interdisciplinary_criteria_require_human_resolution",
        }
        for group, ids in sorted(conflicts.items())
        if len(ids) > 1
    ]

    venue = declaration["target"]["venue"]
    official = [row for row in applicable if row["authority_class"] == "official_venue_type"]
    unresolved: list[dict[str, str]] = []
    if venue is None:
        fallback_state = "field_general"
        resolution_state = "resolved"
    elif not official:
        fallback_state = "declared_target_unresolved"
        resolution_state = "partial"
        unresolved.append(
            {
                "code": "no_exact_venue_track_contribution_profile",
                "dimension": "venue_fit",
                "message": "No exact official criterion matches the author-declared venue, track, and contribution type.",
            }
        )
    elif all(row["source"]["freshness"] != "current" for row in official):
        fallback_state = "venue_exact_advisory"
        resolution_state = "advisory_only"
        unresolved.append(
            {
                "code": "exact_profile_not_current",
                "dimension": "venue_fit",
                "message": "The exact official profile is stale or unverified and cannot block.",
            }
        )
    else:
        fallback_state = "venue_exact"
        resolution_state = "resolved"

    context: dict[str, Any] = {
        "schema_version": "review-target-context/1.0",
        "declaration": declaration,
        "registry": {
            "registry_id": registry["registry_id"],
            "registry_version": registry["registry_version"],
            "as_of": registry["as_of"],
            "registry_digest": digest(registry),
        },
        "selected_criterion_ids": [item["criterion_id"] for item in pointers],
        "selected_criteria": pointers,
        "outcomes": outcomes,
        "parallel_conflicts": parallel_conflicts,
        "fallback_state": fallback_state,
        "resolution_state": resolution_state,
        "unresolved": unresolved,
        "resolved_digest": "",
        "phase1_safe": True,
        "numeric_weights_applied": False,
    }
    substantive_declaration = {
        key: declaration[key]
        for key in (
            "schema_version",
            "criteria_as_of",
            "discipline",
            "target",
            "reporting_design_overlays",
            "criterion_selection",
            "precedence",
        )
    }
    digest_payload = {
        "declaration": substantive_declaration,
        "registry_id": registry["registry_id"],
        "registry_version": registry["registry_version"],
        "selected_criteria": [
            {
                key: pointer[key]
                for key in (
                    "criterion_id",
                    "criterion_version",
                    "criterion_digest",
                    "authority_class",
                    "authority_rank",
                    "dimension",
                    "source_freshness",
                    "blocking_eligible",
                )
            }
            for pointer in pointers
        ],
        "parallel_conflicts": parallel_conflicts,
        "fallback_state": fallback_state,
        "resolution_state": resolution_state,
        "unresolved": unresolved,
    }
    context["resolved_digest"] = digest(digest_payload)
    return context


def render_brief(context: dict[str, Any], registry: dict[str, Any]) -> str:
    rows = {row["criterion_id"]: row for row in registry["criteria"]}
    target = context["declaration"]["target"]
    venue = target["venue"] if target["venue"] is not None else "none (field-general fallback)"
    track = target["track"] if target["track"] is not None else "none"
    lines = [
        "# Target Criteria Brief",
        "",
        f"- Resolved digest: `{context['resolved_digest']}`",
        f"- Venue: {venue}",
        f"- Track: {track}",
        f"- Contribution type: {target['contribution_type']}",
        f"- Fallback state: `{context['fallback_state']}`",
        f"- Resolution state: `{context['resolution_state']}`",
        "- Numeric weights: not applied",
        "",
    ]
    headings = {
        "scientific_validity": "Scientific validity",
        "venue_fit": "Venue fit",
        "submission_readiness": "Submission readiness",
    }
    pointer_by_id = {item["criterion_id"]: item for item in context["selected_criteria"]}
    for dimension in DIMENSIONS:
        lines.extend([f"## {headings[dimension]}", ""])
        ids = context["outcomes"][dimension]
        if not ids:
            lines.extend(["No applicable selected criterion.", ""])
            continue
        for criterion_id in ids:
            row = rows[criterion_id]
            pointer = pointer_by_id[criterion_id]
            status = "blocking-eligible" if pointer["blocking_eligible"] else "advisory"
            reasons = ""
            if pointer["advisory_reasons"]:
                reasons = f"; reasons: {', '.join(pointer['advisory_reasons'])}"
            lines.extend(
                [
                    f"- `{criterion_id}` ({row['authority_class']}, {status}{reasons}): {row['statement']}",
                    f"  Source: {row['source']['title']} — {row['source']['uri']}",
                ]
            )
        lines.append("")
    lines.extend(["## Parallel conflicts", ""])
    if not context["parallel_conflicts"]:
        lines.extend(["None.", ""])
    else:
        for conflict in context["parallel_conflicts"]:
            ids = ", ".join(f"`{item}`" for item in conflict["criterion_ids"])
            lines.append(
                f"- `{conflict['conflict_group']}`: {ids}. Keep these criteria parallel; human resolution is required."
            )
        lines.append("")
    if context["unresolved"]:
        lines.extend(["## Unresolved", ""])
        for item in context["unresolved"]:
            lines.append(f"- `{item['dimension']}` / `{item['code']}`: {item['message']}")
        lines.append("")
    lines.extend(
        [
            "This brief was resolved only from author-confirmed metadata and the named registry.",
            "It contains no manuscript-derived inference and does not average interdisciplinary criteria.",
            "",
        ]
    )
    return "\n".join(lines)


def _write_text(path: Path, value: str) -> None:
    try:
        path.write_text(value, encoding="utf-8")
    except OSError as exc:
        raise ContractError(f"cannot write output {path}: {exc}") from exc


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--context", type=Path, required=True, help="author declaration JSON")
    parser.add_argument(
        "--registry",
        type=Path,
        default=Path(__file__).resolve().parents[1] / "shared" / "review_criteria_registry.json",
        help="criteria registry JSON (defaults to the shipped field-general registry)",
    )
    parser.add_argument("--output", type=Path, help="resolved context JSON path; stdout if omitted")
    parser.add_argument("--brief", type=Path, help="optional Markdown Target Criteria Brief path")
    args = parser.parse_args(argv)
    try:
        declaration = load_json(args.context)
        registry = load_json(args.registry)
        context = resolve(declaration, registry)
        rendered = json.dumps(context, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
        if args.output is None:
            sys.stdout.write(rendered)
        else:
            _write_text(args.output, rendered)
        if args.brief is not None:
            _write_text(args.brief, render_brief(context, registry))
    except ContractError as exc:
        print(f"review-target resolution failed: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
