#!/usr/bin/env python3
"""Integrity lint for evals/heldout/re_review_persuasion_invariance/ (#576 Spec B §14).

Structure-only fixture gate (the #574 E4 `check_seeded_defect_fixtures.py` precedent): it
validates that the machine index, the material files, and the held-out ground truth agree,
so a drifted fixture cannot silently corrupt a paired-control measurement. It measures
nothing about model behavior; baseline runs are the manual protocol in the set's README.

Invariants:
  1. `heldout_set.json` parses, carries the required top-level keys, and declares the
     expected languages / issue / enums.
  2. The scenario inventory is EXACTLY the expected set, and each scenario's arm-id set is
     exactly the expected one (a deleted scenario or arm cannot silently shrink the set).
  3. Every declared path resolves: scenario dir, both packet files, every arm material file
     in both languages, and `ground_truth.md`.
  4. Referential integrity: arm ids unique per scenario; every pair names exactly two
     DECLARED arm ids; every pair carries at least one cell.
  5. Every cell's `observable` and `relation` come from the declared enums, its `expected`
     keys are exactly the pair's two arm ids, its `rule_anchor` is non-empty, and any
     `on_mismatch` comes from the closed set.
  6. Relation/value agreement: an `identical` cell's two expected values are equal and a
     `differs` cell's are unequal (a mislabelled cell cannot pass as either).
  7. Claim-set equality: a scenario with `claim_set_equality_required` true has a non-null,
     equal `claim_set` on every arm. This is the construct-validity commitment P-1 rests on
     — the arms may differ in rhetoric but not in what they assert.
  8. Hash placeholders: every material file carrying an apply report uses all three
     placeholder tokens and NO literal hex on the three hash keys.
  9. Pointer arms: a declared `material_pointer` has a pointer file naming an existing
     sibling in every language, and no undeclared pointer file exists.
 10. Held-out boundary: no packet or arm material file mentions the ground-truth file, and
     no scripted checkpoint answer appears in any material file of its scenario.
 11. Section split: each scenario's `arm_supplied_sections` are ABSENT from both packet
     files and PRESENT in every non-pointer arm material file, in both languages.

Run: python3 scripts/check_persuasion_invariance_fixtures.py
Exit 0 on pass; 1 with per-invariant messages on failure.
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ROOT = REPO / "evals" / "heldout" / "re_review_persuasion_invariance"
INDEX = ROOT / "heldout_set.json"

LANGUAGES = ["en", "zh-TW"]
ISSUE = 576

# Expected inventory — update deliberately when scenarios or arms are added/retired.
# Values are the EXACT arm-id sets, so a coordinated arm deletion must fail CI rather
# than silently shrink the denominator a measurement is reported over.
EXPECTED_ARMS = {
    "P-1": {"arm-a", "arm-b"},
    "P-2": {"arm-a", "arm-b"},
    "P-3": {"arm-a", "arm-b", "arm-c"},
    "P-4": {"arm-a", "arm-b"},
    "P-5": {"arm-a", "arm-b", "arm-c"},
    "P-6": {"arm-a", "arm-b", "arm-c"},
}

REQUIRED_TOP = {
    "set_version",
    "issue",
    "spec_authority",
    "spec_section",
    "harness",
    "languages",
    "hash_placeholders",
    "relation_enum",
    "observable_enum",
    "scenarios",
}
REQUIRED_SCENARIO = {
    "id",
    "dir",
    "title",
    "controlled_factor",
    "arm_supplied_sections",
    "packet",
    "claim_set_equality_required",
    "arms",
    "pairs",
}
REQUIRED_ARM = {"arm_id", "condition", "material", "claim_set", "scripted_checkpoint_answer"}
REQUIRED_CELL = {"observable", "relation", "expected", "rule_anchor"}

ON_MISMATCH_VALUES = {"dispatch_violation"}
PLACEHOLDERS = ("<<BASE_DRAFT_HASH>>", "<<OUTPUT_DRAFT_HASH>>", "<<PATCH_DIGEST>>")
HASH_KEYS = ("base_draft_hash", "output_draft_hash", "patch_digest")
POINTER_RE = re.compile(r"^ARM-MATERIAL-POINTER:\s*(\S+)\s*$")
SECTION_RE = re.compile(r"^##\s+([A-Z])\.\s", re.MULTILINE)
GROUND_TRUTH_NAME = "ground_truth.md"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _sections(text: str) -> set[str]:
    return set(SECTION_RE.findall(text))


def _pointer_target(text: str) -> str | None:
    first = text.splitlines()[0] if text.splitlines() else ""
    match = POINTER_RE.match(first)
    return match.group(1) if match else None


def check_index(errors: list[str]) -> dict | None:
    if not INDEX.is_file():
        errors.append(f"1. index missing: {INDEX.relative_to(REPO)}")
        return None
    try:
        data = json.loads(_read(INDEX))
    except json.JSONDecodeError as exc:
        errors.append(f"1. index does not parse: {exc}")
        return None

    missing = REQUIRED_TOP - set(data)
    if missing:
        errors.append(f"1. index missing top-level keys: {sorted(missing)}")
    if data.get("issue") != ISSUE:
        errors.append(f"1. index issue is {data.get('issue')!r}, expected {ISSUE}")
    if data.get("languages") != LANGUAGES:
        errors.append(f"1. index languages are {data.get('languages')!r}, expected {LANGUAGES}")
    if list(data.get("hash_placeholders", [])) != list(PLACEHOLDERS):
        errors.append(
            f"1. index hash_placeholders are {data.get('hash_placeholders')!r}, "
            f"expected {list(PLACEHOLDERS)}"
        )
    for key in ("relation_enum", "observable_enum"):
        if not isinstance(data.get(key), dict) or not data.get(key):
            errors.append(f"1. index {key} must be a non-empty object")
    return data


def check_inventory(data: dict, errors: list[str]) -> None:
    seen = [s.get("id") for s in data.get("scenarios", [])]
    if sorted(x for x in seen if x) != sorted(EXPECTED_ARMS):
        errors.append(
            f"2. scenario inventory is {sorted(x for x in seen if x)!r}, "
            f"expected {sorted(EXPECTED_ARMS)!r}"
        )
    if len(seen) != len(set(seen)):
        errors.append(f"2. duplicate scenario ids: {seen!r}")

    for scenario in data.get("scenarios", []):
        sid = scenario.get("id")
        if sid not in EXPECTED_ARMS:
            continue
        arm_ids = [a.get("arm_id") for a in scenario.get("arms", [])]
        if set(arm_ids) != EXPECTED_ARMS[sid]:
            errors.append(
                f"2. {sid} arm-id set is {sorted(x for x in arm_ids if x)!r}, "
                f"expected {sorted(EXPECTED_ARMS[sid])!r}"
            )
        if len(arm_ids) != len(set(arm_ids)):
            errors.append(f"4. {sid} has duplicate arm ids: {arm_ids!r}")


def check_scenario(scenario: dict, relations: set[str], observables: set[str],
                   errors: list[str]) -> None:
    sid = scenario.get("id", "<unknown>")
    missing = REQUIRED_SCENARIO - set(scenario)
    if missing:
        errors.append(f"3. {sid} missing keys: {sorted(missing)}")
        return

    sdir = ROOT / scenario["dir"]
    if not sdir.is_dir():
        errors.append(f"3. {sid} dir does not exist: {scenario['dir']}")
        return
    if not (sdir / GROUND_TRUTH_NAME).is_file():
        errors.append(f"3. {sid} missing {GROUND_TRUTH_NAME}")

    packet_paths: dict[str, Path] = {}
    for lang in LANGUAGES:
        rel = scenario["packet"].get(lang)
        if not rel:
            errors.append(f"3. {sid} packet missing language {lang}")
            continue
        path = sdir / rel
        if not path.is_file():
            errors.append(f"3. {sid} packet file does not exist: {scenario['dir']}/{rel}")
        else:
            packet_paths[lang] = path

    arm_ids = {a.get("arm_id") for a in scenario["arms"]}
    material_paths: dict[tuple[str, str], Path] = {}
    pointer_arms: set[str] = set()

    for arm in scenario["arms"]:
        aid = arm.get("arm_id", "<unknown>")
        arm_missing = REQUIRED_ARM - set(arm)
        if arm_missing:
            errors.append(f"3. {sid}/{aid} missing arm keys: {sorted(arm_missing)}")
            continue
        if arm.get("material_pointer") is not None:
            pointer_arms.add(aid)
            if arm["material_pointer"] not in arm_ids:
                errors.append(
                    f"9. {sid}/{aid} material_pointer {arm['material_pointer']!r} "
                    f"is not a declared arm id"
                )
        for lang in LANGUAGES:
            rel = arm["material"].get(lang)
            if not rel:
                errors.append(f"3. {sid}/{aid} material missing language {lang}")
                continue
            path = sdir / rel
            if not path.is_file():
                errors.append(
                    f"3. {sid}/{aid} material file does not exist: {scenario['dir']}/{rel}"
                )
            else:
                material_paths[(aid, lang)] = path

    check_pairs(scenario, arm_ids, relations, observables, errors)
    check_claim_sets(scenario, errors)
    check_placeholders(sid, packet_paths, material_paths, pointer_arms, errors)
    check_pointers(sid, scenario, material_paths, pointer_arms, errors)
    check_heldout_boundary(sid, scenario, packet_paths, material_paths, errors)
    check_section_split(sid, scenario, packet_paths, material_paths, pointer_arms, errors)


def check_pairs(scenario: dict, arm_ids: set[str], relations: set[str],
                observables: set[str], errors: list[str]) -> None:
    sid = scenario.get("id", "<unknown>")
    pair_ids = [p.get("pair_id") for p in scenario["pairs"]]
    if len(pair_ids) != len(set(pair_ids)):
        errors.append(f"4. {sid} has duplicate pair ids: {pair_ids!r}")

    for pair in scenario["pairs"]:
        pid = pair.get("pair_id", "<unknown>")
        arms = pair.get("arms") or []
        if len(arms) != 2:
            errors.append(f"4. {sid}/{pid} names {len(arms)} arms, expected exactly 2")
            continue
        unknown = [a for a in arms if a not in arm_ids]
        if unknown:
            errors.append(f"4. {sid}/{pid} names undeclared arm ids: {unknown!r}")
            continue
        if arms[0] == arms[1]:
            errors.append(f"4. {sid}/{pid} pairs an arm with itself: {arms[0]!r}")
            continue
        cells = pair.get("cells") or []
        if not cells:
            errors.append(f"4. {sid}/{pid} carries no cells")
        for idx, cell in enumerate(cells):
            check_cell(f"{sid}/{pid}#{idx}", cell, set(arms), relations, observables, errors)


def check_cell(label: str, cell: dict, arms: set[str], relations: set[str],
               observables: set[str], errors: list[str]) -> None:
    missing = REQUIRED_CELL - set(cell)
    if missing:
        errors.append(f"5. {label} missing cell keys: {sorted(missing)}")
        return
    if cell["observable"] not in observables:
        errors.append(f"5. {label} observable {cell['observable']!r} is not in observable_enum")
    if cell["relation"] not in relations:
        errors.append(f"5. {label} relation {cell['relation']!r} is not in relation_enum")
    if not str(cell["rule_anchor"]).strip():
        errors.append(f"5. {label} rule_anchor is empty")
    if "on_mismatch" in cell and cell["on_mismatch"] not in ON_MISMATCH_VALUES:
        errors.append(
            f"5. {label} on_mismatch {cell['on_mismatch']!r} is not in {sorted(ON_MISMATCH_VALUES)}"
        )

    expected = cell.get("expected")
    if not isinstance(expected, dict) or set(expected) != arms:
        errors.append(
            f"5. {label} expected keys are "
            f"{sorted(expected) if isinstance(expected, dict) else expected!r}, "
            f"expected exactly {sorted(arms)}"
        )
        return

    first, second = (expected[a] for a in sorted(arms))
    equal = first == second
    if cell["relation"] == "identical" and not equal:
        errors.append(f"6. {label} relation is 'identical' but expected values differ: {expected!r}")
    if cell["relation"] == "differs" and equal:
        errors.append(f"6. {label} relation is 'differs' but expected values are equal: {expected!r}")


def check_claim_sets(scenario: dict, errors: list[str]) -> None:
    sid = scenario.get("id", "<unknown>")
    if not scenario.get("claim_set_equality_required"):
        return
    sets = []
    for arm in scenario["arms"]:
        claim_set = arm.get("claim_set")
        if not claim_set:
            errors.append(
                f"7. {sid}/{arm.get('arm_id')} declares claim_set_equality_required "
                f"but carries no claim_set"
            )
            return
        sets.append((arm.get("arm_id"), list(claim_set)))
    reference = sets[0][1]
    for aid, claim_set in sets[1:]:
        if claim_set != reference:
            errors.append(
                f"7. {sid}/{aid} claim_set {claim_set!r} differs from "
                f"{sets[0][0]}'s {reference!r} — the arms must assert the same claims"
            )


def check_placeholders(sid: str, packet_paths: dict[str, Path],
                       material_paths: dict[tuple[str, str], Path],
                       pointer_arms: set[str], errors: list[str]) -> None:
    candidates: list[Path] = list(packet_paths.values())
    candidates += [p for (aid, _), p in material_paths.items() if aid not in pointer_arms]
    for path in candidates:
        text = _read(path)
        if "report_format_version" not in text:
            continue
        rel = path.relative_to(ROOT)
        for token in PLACEHOLDERS:
            if token not in text:
                errors.append(f"8. {sid} {rel} carries an apply report but lacks {token}")
        for key in HASH_KEYS:
            for value in re.findall(rf'"{key}"\s*:\s*"([^"]*)"', text):
                if value not in PLACEHOLDERS:
                    errors.append(
                        f"8. {sid} {rel} {key} is {value!r}, expected a placeholder token — "
                        f"a checked-in hash fails the §11 apply-chain witness"
                    )


def check_pointers(sid: str, scenario: dict, material_paths: dict[tuple[str, str], Path],
                   pointer_arms: set[str], errors: list[str]) -> None:
    materials_by_arm = {
        arm["arm_id"]: arm.get("material", {}) for arm in scenario["arms"] if "arm_id" in arm
    }
    for (aid, lang), path in sorted(material_paths.items()):
        rel = path.relative_to(ROOT)
        target = _pointer_target(_read(path))
        if aid in pointer_arms:
            if target is None:
                errors.append(
                    f"9. {sid}/{aid} declares material_pointer but {rel} is not a pointer file"
                )
                continue
            declared = materials_by_arm.get(
                next(a["material_pointer"] for a in scenario["arms"]
                     if a.get("arm_id") == aid), {}
            ).get(lang)
            if declared and Path(declared).name != target:
                errors.append(
                    f"9. {sid}/{aid} {rel} points at {target!r} but its material_pointer arm "
                    f"declares {Path(declared).name!r} for {lang}"
                )
            if not (path.parent / target).is_file():
                errors.append(f"9. {sid}/{aid} {rel} points at a missing file: {target}")
        elif target is not None:
            errors.append(
                f"9. {sid}/{aid} {rel} is a pointer file but the index declares no material_pointer"
            )


def check_heldout_boundary(sid: str, scenario: dict, packet_paths: dict[str, Path],
                           material_paths: dict[tuple[str, str], Path],
                           errors: list[str]) -> None:
    answers = [
        (arm["arm_id"], arm["scripted_checkpoint_answer"])
        for arm in scenario["arms"]
        if arm.get("scripted_checkpoint_answer")
    ]
    for path in list(packet_paths.values()) + list(material_paths.values()):
        text = _read(path)
        rel = path.relative_to(ROOT)
        if GROUND_TRUTH_NAME in text:
            errors.append(
                f"10. {sid} {rel} references {GROUND_TRUTH_NAME}; material files must not "
                f"point a run at the held-out key"
            )
        for aid, answer in answers:
            if answer in text:
                errors.append(
                    f"10. {sid} {rel} contains {aid}'s scripted checkpoint answer verbatim; "
                    f"the answer must stay held out until the checkpoint"
                )


def check_section_split(sid: str, scenario: dict, packet_paths: dict[str, Path],
                        material_paths: dict[tuple[str, str], Path],
                        pointer_arms: set[str], errors: list[str]) -> None:
    supplied = set(scenario.get("arm_supplied_sections") or [])
    if not supplied:
        errors.append(f"11. {sid} declares no arm_supplied_sections")
        return
    for lang, path in sorted(packet_paths.items()):
        leaked = supplied & _sections(_read(path))
        if leaked:
            errors.append(
                f"11. {sid} packet.{lang} contains arm-supplied section(s) {sorted(leaked)}; "
                f"the packet must omit every section the arm varies"
            )
    for (aid, lang), path in sorted(material_paths.items()):
        if aid in pointer_arms:
            continue
        absent = supplied - _sections(_read(path))
        if absent:
            errors.append(
                f"11. {sid}/{aid} material ({lang}) is missing arm-supplied section(s) "
                f"{sorted(absent)}"
            )


def main() -> int:
    errors: list[str] = []
    if not ROOT.is_dir():
        print(f"FAIL: fixture root missing: {ROOT.relative_to(REPO)}", file=sys.stderr)
        return 1

    data = check_index(errors)
    if data is None:
        for err in errors:
            print(f"FAIL: {err}", file=sys.stderr)
        return 1

    check_inventory(data, errors)
    relations = set(data.get("relation_enum") or {})
    observables = set(data.get("observable_enum") or {})
    for scenario in data.get("scenarios", []):
        check_scenario(scenario, relations, observables, errors)

    if errors:
        for err in errors:
            print(f"FAIL: {err}", file=sys.stderr)
        return 1

    scenarios = len(data["scenarios"])
    arms = sum(len(s["arms"]) for s in data["scenarios"])
    pairs = sum(len(s["pairs"]) for s in data["scenarios"])
    cells = sum(len(p["cells"]) for s in data["scenarios"] for p in s["pairs"])
    print(
        f"OK: #576 persuasion-invariance fixtures — {scenarios} scenarios, {arms} arms, "
        f"{pairs} pairs, {cells} cells per language ({len(LANGUAGES)} languages)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
