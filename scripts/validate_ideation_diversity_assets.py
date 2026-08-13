#!/usr/bin/env python3
"""Offline validator for the #659 Phase-1 design and synthetic role seed.

This CLI has no subject, actor, judge, provider, or network transport. It may
materialize the frozen non-production prompt variant to a new file, but it never
changes the production Socratic Mentor prompt.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

import jsonschema


REPO_ROOT = Path(__file__).resolve().parent.parent
SUITE_ROOT = REPO_ROOT / "evals" / "heldout" / "within_session_ideation_diversity"
SET_PATH = SUITE_ROOT / "heldout_set.json"
SCHEMA_PATH = SUITE_ROOT / "heldout_set.schema.json"
VARIANT_PATH = SUITE_ROOT / "nonproduction_variant.json"
CODEBOOK_PATH = SUITE_ROOT / "codebook.md"
DESIGN_PATH = REPO_ROOT / "docs" / "design" / (
    "2026-08-13-659-within-session-ideation-diversity-design.md"
)
SUITE = "within_session_ideation_diversity"
PAIR_IDS = {"idi-edtech", "idi-quality-policy", "idi-public-health"}
LANGUAGES = {"en", "zh-TW"}
FRAMING_KEYS = ["F1", "F2", "F3"]
VARIANT_KEYS = {
    "schema_version",
    "variant_id",
    "source_path",
    "source_sha256",
    "nonproduction_only",
    "runtime_install_forbidden",
    "adjacent_probe_state",
    "replacements",
    "required_present_after",
    "required_absent_after",
}
REPLACEMENT_KEYS = {"replacement_id", "occurrences", "before", "after"}
DIRECTIONAL_FACET_RE = re.compile(
    r"\b(?:cause|causal|effect|impact|driver|mechanism|mediate|moderate|outcome|"
    r"improve|reduce|increase|decrease|harm|benefit)\b|"
    r"(?:因果|影響|效果|導致|驅動|機制|中介|調節|改善|降低|增加|傷害|結果)",
    re.IGNORECASE,
)


class AssetError(ValueError):
    """Closed validation or materialization failure."""


def _reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise AssetError(f"duplicate JSON key {key!r}")
        value[key] = item
    return value


def load_json_strict(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(
            path.read_text(encoding="utf-8"),
            object_pairs_hook=_reject_duplicate_keys,
            parse_constant=lambda name: (_ for _ in ()).throw(
                AssetError(f"non-finite JSON value {name!r}")
            ),
        )
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise AssetError(f"cannot read strict JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise AssetError(f"{path} must contain one JSON object")
    return value


def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_assets() -> tuple[dict[str, Any], dict[str, Any]]:
    heldout = load_json_strict(SET_PATH)
    schema = load_json_strict(SCHEMA_PATH)
    variant = load_json_strict(VARIANT_PATH)
    try:
        jsonschema.Draft202012Validator.check_schema(schema)
    except jsonschema.SchemaError as exc:
        raise AssetError(f"invalid held-out schema: {exc.message}") from exc
    errors = sorted(
        jsonschema.Draft202012Validator(schema).iter_errors(heldout),
        key=lambda err: list(err.absolute_path),
    )
    if errors:
        first = errors[0]
        location = ".".join(str(part) for part in first.absolute_path) or "$"
        raise AssetError(f"heldout_set schema error at {location}: {first.message}")
    validate_assets(heldout, variant)
    return heldout, variant


def validate_assets(heldout: dict[str, Any], variant: dict[str, Any]) -> None:
    if heldout.get("suite") != SUITE:
        raise AssetError(f"suite must be {SUITE!r}")
    scenarios = heldout.get("scenarios")
    if not isinstance(scenarios, list) or len(scenarios) != 6:
        raise AssetError("v0.1 must contain exactly six scenarios")

    scenario_ids = [row.get("scenario_id") for row in scenarios]
    if len(set(scenario_ids)) != len(scenario_ids):
        raise AssetError("scenario_id values must be unique")
    observed_pairs = {
        (row.get("pair_id"), row.get("language")) for row in scenarios
    }
    expected_pairs = {(pair_id, language) for pair_id in PAIR_IDS for language in LANGUAGES}
    if observed_pairs != expected_pairs:
        raise AssetError("each canonical pair must contain one en and one zh-TW role card")

    for pair_id in PAIR_IDS:
        pair = [row for row in scenarios if row["pair_id"] == pair_id]
        if len({row["equivalence_key"] for row in pair}) != 1:
            raise AssetError(f"{pair_id}: equivalence_key must match across languages")
        signatures = []
        for row in pair:
            framings = row["owned_framings"]
            keys = [framing["framing_key"] for framing in framings]
            if keys != FRAMING_KEYS:
                raise AssetError(f"{row['scenario_id']}: framing keys must be F1,F2,F3")
            initially_expressed = [
                framing["framing_key"]
                for framing in framings
                if framing["initially_expressed"]
            ]
            if initially_expressed != ["F1"]:
                raise AssetError(
                    f"{row['scenario_id']}: exactly F1 must be initially expressed"
                )
            signatures.append(
                [(framing["framing_key"], framing["facet_kind"]) for framing in framings]
            )
            _validate_directionless_phrases(row)
        if signatures[0] != signatures[1]:
            raise AssetError(f"{pair_id}: framing/facet structure differs by language")

    _validate_codebook_and_design()
    render_variant(variant)


def _validate_directionless_phrases(scenario: dict[str, Any]) -> None:
    seen: set[str] = set()
    for framing in scenario["owned_framings"]:
        for phrase in framing["matching_facet_phrases"]:
            folded = phrase.casefold().strip()
            if folded in seen:
                raise AssetError(
                    f"{scenario['scenario_id']}: matching facet phrases must be unique"
                )
            seen.add(folded)
            if "?" in phrase or "？" in phrase or DIRECTIONAL_FACET_RE.search(phrase):
                raise AssetError(
                    f"{scenario['scenario_id']}: facet phrase is directional or formed: {phrase!r}"
                )


def _validate_codebook_and_design() -> None:
    try:
        codebook = CODEBOOK_PATH.read_text(encoding="utf-8")
        design = DESIGN_PATH.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise AssetError(f"cannot read design/codebook: {exc}") from exc
    codebook_normalized = " ".join(codebook.split())
    design_normalized = " ".join(design.split())

    codebook_requirements = (
        "independent scholar-script-owned framing expression",
        "formed research framing or hypothesis proposal",
        "option inflation",
        "never contributes to A1",
        "Do not average metrics 1-6 into a score",
        "At least two judges label independently",
    )
    for text in codebook_requirements:
        if text not in codebook_normalized:
            raise AssetError(f"codebook missing required boundary {text!r}")

    design_requirements = (
        "No subject, actor, judge, or adjudicator session is authorized",
        "never merged into a scalar diversity score",
        "two independent paired-control experiments",
        "never replace or modify the production agent file",
        "Without that attestation, report languages separately",
        "Stop on the first prompt/role-card hash mismatch",
    )
    for text in design_requirements:
        if text not in design_normalized:
            raise AssetError(f"design missing required boundary {text!r}")


def render_variant(variant: dict[str, Any]) -> str:
    if set(variant) != VARIANT_KEYS:
        raise AssetError("nonproduction_variant has missing or extra top-level keys")
    if variant["schema_version"] != "ideation-diversity-nonproduction-variant/1.0":
        raise AssetError("unknown nonproduction variant schema_version")
    if variant["variant_id"] != "exploratory_guardrails_ablated":
        raise AssetError("unexpected nonproduction variant_id")
    if variant["nonproduction_only"] is not True:
        raise AssetError("variant must be marked nonproduction_only")
    if variant["runtime_install_forbidden"] is not True:
        raise AssetError("variant must forbid runtime installation")
    if variant["adjacent_probe_state"] != "off":
        raise AssetError("guardrails experiment must hold adjacent probe off")

    source_rel = Path(variant["source_path"])
    if source_rel.is_absolute() or ".." in source_rel.parts:
        raise AssetError("variant source_path must be repository-relative and safe")
    source_path = REPO_ROOT / source_rel
    try:
        source_bytes = source_path.read_bytes()
        rendered = source_bytes.decode("utf-8")
    except (OSError, UnicodeError) as exc:
        raise AssetError(f"cannot read variant source: {exc}") from exc
    if _sha256(source_bytes) != variant["source_sha256"]:
        raise AssetError("variant source_sha256 does not match production prompt")

    replacements = variant["replacements"]
    if not isinstance(replacements, list) or len(replacements) < 1:
        raise AssetError("variant replacements must be a non-empty list")
    replacement_ids: set[str] = set()
    for replacement in replacements:
        if not isinstance(replacement, dict) or set(replacement) != REPLACEMENT_KEYS:
            raise AssetError("variant replacement has missing or extra keys")
        replacement_id = replacement["replacement_id"]
        if replacement_id in replacement_ids:
            raise AssetError(f"duplicate replacement_id {replacement_id!r}")
        replacement_ids.add(replacement_id)
        if replacement["occurrences"] != 1:
            raise AssetError("v0.1 replacements must each declare one occurrence")
        before = replacement["before"]
        after = replacement["after"]
        if not isinstance(before, str) or not before or not isinstance(after, str) or not after:
            raise AssetError(f"{replacement_id}: before/after must be non-empty strings")
        count = rendered.count(before)
        if count != replacement["occurrences"]:
            raise AssetError(
                f"{replacement_id}: expected {replacement['occurrences']} occurrence, found {count}"
            )
        rendered = rendered.replace(before, after, 1)

    for text in variant["required_present_after"]:
        if text not in rendered:
            raise AssetError(f"rendered variant missing required text {text!r}")
    for text in variant["required_absent_after"]:
        if text in rendered:
            raise AssetError(f"rendered variant retains ablated text {text!r}")
    return rendered


def materialize_variant(output: Path) -> None:
    if output.exists():
        raise AssetError(f"refusing to overwrite existing output {output}")
    _, variant = load_assets()
    rendered = render_variant(variant)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(rendered)


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("validate-assets", help="validate all frozen Phase-1 assets")
    materialize = subparsers.add_parser(
        "materialize-variant", help="write the frozen non-production ablation prompt"
    )
    materialize.add_argument("--output", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "validate-assets":
            load_assets()
            print("within_session_ideation_diversity assets: OK")
            return 0
        if args.command == "materialize-variant":
            materialize_variant(args.output)
            print(f"wrote non-production variant: {args.output}")
            return 0
    except AssetError as exc:
        print(f"within_session_ideation_diversity assets: FAIL: {exc}", file=sys.stderr)
        return 2
    raise AssertionError(f"unhandled command {args.command!r}")


if __name__ == "__main__":
    raise SystemExit(main())
