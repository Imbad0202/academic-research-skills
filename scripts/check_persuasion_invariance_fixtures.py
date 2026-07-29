#!/usr/bin/env python3
"""Integrity lint for evals/heldout/re_review_persuasion_invariance/ (#576 Spec B §14).

Structure-only fixture gate (the #574 E4 `check_seeded_defect_fixtures.py` precedent): it
validates that the machine index, the material files on disk, and each ground-truth file's
declared pair/observable inventory agree, so a drifted fixture cannot silently corrupt a
paired-control measurement. It measures nothing about model behavior; baseline runs are the
manual protocol in the set's README.

Scope note, deliberately narrow: this lint does NOT read expected VALUES out of the
ground-truth prose and compare them with the index. It cross-checks which (pair, observable,
target) cells exist on both sides, never what each cell expects. A wrong expected value is
caught by review, not here.

Invariants:
  1. `heldout_set.json` parses, carries the required top-level keys, and declares the pinned
     spec authority, issue, languages and placeholder tokens.
  2. The scenario inventory, each scenario's arm-id set, each scenario's pair-id set, and
     each scenario's cell count are EXACTLY the pinned values (a deleted scenario, arm, pair
     or cell cannot silently shrink the denominator a measurement is reported over).
  3. Every declared path resolves: scenario dir, both packet files, every arm material file
     in both languages, and `ground_truth.md`.
  4. Referential integrity: arm and pair ids unique per scenario; every pair names exactly
     two DECLARED, distinct arm ids; every pair carries at least one cell.
  5. Every cell carries all required keys including `target`, its `observable` and `relation`
     come from the declared enums, its `expected` keys are exactly the pair's two arm ids,
     its `rule_anchor` is non-empty, and any `on_mismatch` comes from the closed set.
  6. Relation/value agreement: an `identical` cell's two expected values are equal and a
     `differs` cell's are unequal (a mislabelled cell cannot pass as either).
  7. Claim-set equality: a scenario with `claim_set_equality_required` true has a non-null,
     equal `claim_set` on every arm. This pins the DECLARED arrays, which is the maintainer's
     construct-validity commitment for P-1; no claim id is bound to letter prose, and the
     lint does not pretend to check the text.
  8. Hash placeholders: an apply report is detected independently of the hash keys (any of
     `report_format_version` / `hunks_applied` / `hunks_rejected` / a hash key), and a file
     carrying one declares `report_format_version` and ALL THREE hash keys exactly once each,
     each bound to ITS OWN placeholder token — so a swapped pair, a dropped key, a duplicated
     key and a literal hex all fail. The number of report-bearing files is pinned, so deleting
     a whole report block fails too.
  9. Pointer arms: a declared `material_pointer` has a pointer file in every language naming
     the pointed-to arm's file for that language; the target exists and is NOT itself a
     pointer; no undeclared pointer file exists.
 10. Held-out boundary: no packet or arm material file mentions the ground-truth file, and no
     scripted checkpoint answer appears in a material file of its scenario. A non-null
     scripted answer is an object carrying every declared language, and EVERY language's
     answer is checked against EVERY file (a cross-language paste is still contamination).
 11. Section split: each scenario's `arm_supplied_sections` are ABSENT from both packet files
     and are EXACTLY the section set of every non-pointer arm material file, in both
     languages — an arm may not carry an undeclared or duplicated section, which would let it
     vary an input the scenario declares constant.
 12. Ground-truth agreement: every `ground_truth.md` carries a `## Pair structure` table — read
     up to the next H2, not to end of file — whose
     (arm-pair, observable, target) rows are exactly the index's cells for that scenario, as a
     MULTISET — two cells sharing an observable but differing in target need two rows, so a
     collapsed row cannot hide a cell.

Run: python3 scripts/check_persuasion_invariance_fixtures.py
Exit 0 on pass; 1 with per-invariant messages on failure.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
ROOT = REPO / "evals" / "heldout" / "re_review_persuasion_invariance"
INDEX = ROOT / "heldout_set.json"

LANGUAGES = ["en", "zh-TW"]
ISSUE = 576
SPEC_AUTHORITY = (
    "docs/design/2026-07-27-576-spec-b-re-review-precommitment-contract-spec.md"
)

# Expected inventory — update deliberately when scenarios, arms, pairs or cells are
# added/retired. Pinning cell COUNTS as well as ids means a quietly deleted cell fails CI
# instead of shrinking the denominator a reported pass rate is computed over.
EXPECTED_ARMS = {
    "P-1": {"arm-a", "arm-b"},
    "P-2": {"arm-a", "arm-b"},
    "P-3": {"arm-a", "arm-b", "arm-c"},
    "P-4": {"arm-a", "arm-b"},
    "P-5": {"arm-a", "arm-b", "arm-c"},
    "P-6": {"arm-a", "arm-b", "arm-c"},
}
EXPECTED_PAIRS = {
    "P-1": {"P-1/a-b"},
    "P-2": {"P-2/a-b"},
    "P-3": {"P-3/a-b", "P-3/a-c", "P-3/b-c"},
    "P-4": {"P-4/a-b"},
    "P-5": {"P-5/a-b", "P-5/a-c", "P-5/b-c"},
    "P-6": {"P-6/a-c", "P-6/a-b", "P-6/b-c"},
}
EXPECTED_CELL_COUNTS = {"P-1": 6, "P-2": 4, "P-3": 11, "P-4": 6, "P-5": 7, "P-6": 9}
# Files (packets + non-pointer arm materials, both languages) that carry an apply report.
# Pinned so deleting a whole report block fails instead of quietly passing the per-key checks.
EXPECTED_APPLY_REPORT_FILES = 22

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
REQUIRED_CELL = {"observable", "relation", "expected", "rule_anchor", "target"}

ON_MISMATCH_VALUES = {"dispatch_violation"}
# key -> the ONLY placeholder token that key may carry (key-bound: a swap must fail)
HASH_KEY_TOKENS = {
    "base_draft_hash": "<<BASE_DRAFT_HASH>>",
    "output_draft_hash": "<<OUTPUT_DRAFT_HASH>>",
    "patch_digest": "<<PATCH_DIGEST>>",
}
PLACEHOLDERS = tuple(HASH_KEY_TOKENS[k] for k in
                     ("base_draft_hash", "output_draft_hash", "patch_digest"))
POINTER_RE = re.compile(r"^ARM-MATERIAL-POINTER:\s*(\S+)\s*$")
SECTION_RE = re.compile(r"^##\s+([A-Z])\.\s", re.MULTILINE)
# An apply report is detected independently of the hash keys, so removing all three cannot
# make the file look report-free.
APPLY_REPORT_MARKER_RE = re.compile(
    r'"(report_format_version|hunks_applied|hunks_rejected|base_draft_hash'
    r'|output_draft_hash|patch_digest)"\s*:'
)
PAIR_ROW_RE = re.compile(
    r"^\|\s*\**([a-z])↔([a-z])\**\s*\|\s*([^|]+)\|\s*[^|]*\|\s*([^|]*)\|", re.MULTILINE
)
GROUND_TRUTH_NAME = "ground_truth.md"
PAIR_STRUCTURE_HEADING = "## Pair structure"


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def _sections(text: str) -> set[str]:
    """Section letters, and a marker for any duplicate — duplicates must not pass."""
    found = SECTION_RE.findall(text)
    if len(found) != len(set(found)):
        return set(found) | {"<duplicate>"}
    return set(found)


def _pointer_target(text: str) -> str | None:
    lines = text.splitlines()
    match = POINTER_RE.match(lines[0]) if lines else None
    return match.group(1) if match else None


def _strip_cell(text: str) -> str:
    return text.replace("*", "").replace("`", "").strip()


def _target_key(target) -> str:
    """Normalise a cell target for comparison; None and the em-dash both mean 'run-level'."""
    if target is None:
        return "—"
    return _strip_cell(str(target))


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
    if data.get("spec_authority") != SPEC_AUTHORITY:
        errors.append(
            f"1. index spec_authority is {data.get('spec_authority')!r}, "
            f"expected {SPEC_AUTHORITY!r}"
        )
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

        pair_ids = [p.get("pair_id") for p in scenario.get("pairs", [])]
        if set(pair_ids) != EXPECTED_PAIRS[sid]:
            errors.append(
                f"2. {sid} pair-id set is {sorted(x for x in pair_ids if x)!r}, "
                f"expected {sorted(EXPECTED_PAIRS[sid])!r}"
            )
        cells = sum(len(p.get("cells") or []) for p in scenario.get("pairs", []))
        if cells != EXPECTED_CELL_COUNTS[sid]:
            errors.append(
                f"2. {sid} declares {cells} cells, expected {EXPECTED_CELL_COUNTS[sid]}"
            )


def check_scenario(scenario: dict, relations: set[str], observables: set[str],
                   errors: list[str], report_bearing: list[Path]) -> None:
    sid = scenario.get("id", "<unknown>")
    missing = REQUIRED_SCENARIO - set(scenario)
    if missing:
        errors.append(f"3. {sid} missing keys: {sorted(missing)}")
        return

    sdir = ROOT / scenario["dir"]
    if not sdir.is_dir():
        errors.append(f"3. {sid} dir does not exist: {scenario['dir']}")
        return
    gt_path = sdir / GROUND_TRUTH_NAME
    if not gt_path.is_file():
        errors.append(f"3. {sid} missing {GROUND_TRUTH_NAME}")
        gt_path = None

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
            elif arm["material_pointer"] == aid:
                errors.append(f"9. {sid}/{aid} material_pointer points at itself")
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
    check_placeholders(sid, packet_paths, material_paths, pointer_arms, errors,
                       report_bearing)
    check_pointers(sid, scenario, material_paths, pointer_arms, errors)
    check_heldout_boundary(sid, scenario, packet_paths, material_paths, errors)
    check_section_split(sid, scenario, packet_paths, material_paths, pointer_arms, errors)
    if gt_path is not None:
        check_ground_truth_pairs(sid, scenario, gt_path, errors)


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
    if "conditional_on" in cell and (
        not isinstance(cell["conditional_on"], str) or not cell["conditional_on"].strip()
    ):
        errors.append(
            f"5. {label} conditional_on must be a non-empty string, got "
            f"{type(cell['conditional_on']).__name__}"
        )
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
                       pointer_arms: set[str], errors: list[str],
                       report_bearing: list[Path]) -> None:
    candidates: list[Path] = list(packet_paths.values())
    candidates += [p for (aid, _), p in material_paths.items() if aid not in pointer_arms]
    for path in sorted(candidates):
        text = _read(path)
        rel = path.relative_to(ROOT)
        found = {
            key: re.findall(rf'"{key}"\s*:\s*"([^"]*)"', text)
            for key in HASH_KEY_TOKENS
        }
        if not APPLY_REPORT_MARKER_RE.search(text):
            # No apply report in this file. Legitimate for a no-reports arm (P-3 arm-c) or a
            # packet that supplies no §G; the set-level count below is what stops a report
            # from being deleted wholesale.
            continue
        report_bearing.append(path)
        versions = re.findall(r'"report_format_version"\s*:', text)
        if len(versions) != 1:
            errors.append(
                f"8. {sid} {rel} carries an apply report with {len(versions)} "
                f'"report_format_version" key(s), expected exactly 1'
            )
        for key, token in HASH_KEY_TOKENS.items():
            values = found[key]
            if len(values) != 1:
                errors.append(
                    f"8. {sid} {rel} carries an apply report with {len(values)} "
                    f'"{key}" key(s), expected exactly 1 — every apply report declares all '
                    f"three hash keys"
                )
                continue
            if values[0] != token:
                errors.append(
                    f"8. {sid} {rel} {key} is {values[0]!r}, expected {token!r} — the token is "
                    f"key-bound; a literal hash or a swapped token breaks materialisation"
                )


def check_pointers(sid: str, scenario: dict, material_paths: dict[tuple[str, str], Path],
                   pointer_arms: set[str], errors: list[str]) -> None:
    pointer_of = {
        arm["arm_id"]: arm.get("material_pointer")
        for arm in scenario["arms"] if "arm_id" in arm
    }
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
            declared = materials_by_arm.get(pointer_of.get(aid), {}).get(lang)
            if declared and Path(declared).name != target:
                errors.append(
                    f"9. {sid}/{aid} {rel} points at {target!r} but its material_pointer arm "
                    f"declares {Path(declared).name!r} for {lang}"
                )
            target_path = path.parent / target
            if not target_path.is_file():
                errors.append(f"9. {sid}/{aid} {rel} points at a missing file: {target}")
            elif _pointer_target(_read(target_path)) is not None:
                errors.append(
                    f"9. {sid}/{aid} {rel} points at {target}, which is itself a pointer — "
                    f"a pointer must resolve to real material in one hop"
                )
        elif target is not None:
            errors.append(
                f"9. {sid}/{aid} {rel} is a pointer file but the index declares no material_pointer"
            )


def check_heldout_boundary(sid: str, scenario: dict, packet_paths: dict[str, Path],
                           material_paths: dict[tuple[str, str], Path],
                           errors: list[str]) -> None:
    answers: list[tuple[str, dict]] = []
    for arm in scenario["arms"]:
        answer = arm.get("scripted_checkpoint_answer")
        if answer is None:
            continue
        if not isinstance(answer, dict) or set(answer) != set(LANGUAGES):
            errors.append(
                f"10. {sid}/{arm.get('arm_id')} scripted_checkpoint_answer must be an object "
                f"carrying exactly {LANGUAGES}, got "
                f"{sorted(answer) if isinstance(answer, dict) else type(answer).__name__}"
            )
            continue
        answers.append((arm.get("arm_id"), answer))

    files = sorted(set(packet_paths.values()) | set(material_paths.values()))
    for path in files:
        text = _read(path)
        rel = path.relative_to(ROOT)
        if GROUND_TRUTH_NAME in text:
            errors.append(
                f"10. {sid} {rel} references {GROUND_TRUTH_NAME}; material files must not "
                f"point a run at the held-out key"
            )
        # every language's answer is checked against every file: a cross-language paste is
        # still contamination, and pairing the scan to the file's own language would miss it
        for aid, answer in answers:
            for lang in LANGUAGES:
                if answer[lang] and answer[lang] in text:
                    errors.append(
                        f"10. {sid} {rel} contains {aid}'s scripted checkpoint answer ({lang}) "
                        f"verbatim; the answer must stay held out until the checkpoint"
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
        actual = _sections(_read(path))
        if actual != supplied:
            errors.append(
                f"11. {sid}/{aid} material ({lang}) section set is {sorted(actual)}, expected "
                f"exactly {sorted(supplied)} — an arm may not add, drop or duplicate a section"
            )


def check_ground_truth_pairs(sid: str, scenario: dict, gt_path: Path,
                             errors: list[str]) -> None:
    text = _read(gt_path)
    if PAIR_STRUCTURE_HEADING not in text:
        errors.append(f"12. {sid} {GROUND_TRUTH_NAME} has no '{PAIR_STRUCTURE_HEADING}' section")
        return
    # Bound the section at the next H2 rather than reading to EOF: a later table whose rows
    # happen to match PAIR_ROW_RE would otherwise be folded into this comparison.
    table = text.split(PAIR_STRUCTURE_HEADING, 1)[1]
    next_h2 = re.search(r"^## ", table, re.MULTILINE)
    if next_h2:
        table = table[: next_h2.start()]
    declared = Counter(
        (tuple(sorted({f"arm-{a}", f"arm-{b}"})), _strip_cell(obs), _strip_cell(target))
        for a, b, obs, target in PAIR_ROW_RE.findall(table)
    )
    indexed = Counter(
        (tuple(sorted(pair["arms"])), cell["observable"], _target_key(cell.get("target")))
        for pair in scenario["pairs"]
        for cell in (pair.get("cells") or [])
        if len(pair.get("arms") or []) == 2 and "observable" in cell
    )
    only_gt = declared - indexed
    only_index = indexed - declared

    def fmt(counter):
        return sorted(f"{list(arms)} {obs} [{target}] x{n}"
                      for (arms, obs, target), n in counter.items())

    if only_gt:
        errors.append(
            f"12. {sid} {GROUND_TRUTH_NAME} Pair structure declares cells the index does not: "
            f"{fmt(only_gt)}"
        )
    if only_index:
        errors.append(
            f"12. {sid} index declares cells {GROUND_TRUTH_NAME} Pair structure does not: "
            f"{fmt(only_index)}"
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
    report_bearing: list[Path] = []
    relations = set(data.get("relation_enum") or {})
    observables = set(data.get("observable_enum") or {})
    for scenario in data.get("scenarios", []):
        check_scenario(scenario, relations, observables, errors, report_bearing)

    if len(report_bearing) != EXPECTED_APPLY_REPORT_FILES:
        errors.append(
            f"8. {len(report_bearing)} material/packet file(s) carry an apply report, expected "
            f"{EXPECTED_APPLY_REPORT_FILES} — a wholesale deletion cannot shrink the set silently"
        )

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
