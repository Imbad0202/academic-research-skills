"""Hermetic conformance and mutation tests for issue #660."""
from __future__ import annotations

import copy
import hashlib
import json
import subprocess
import sys
import unicodedata
from collections import Counter
from pathlib import Path

import pytest
import yaml
from jsonschema import Draft202012Validator


SCRIPTS = Path(__file__).resolve().parent
REPO_ROOT = SCRIPTS.parent
FIXTURES = SCRIPTS / "fixtures/tortured_phrase_screening"
sys.path.insert(0, str(SCRIPTS))

import tortured_phrase_screening as screening  # noqa: E402


CHECKED_AT = "2026-08-10T01:00:00Z"
RECORDED_AT = "2026-08-10T01:00:01Z"


def _bundle() -> screening.SnapshotBundle:
    return screening.load_snapshot(
        FIXTURES / "snapshot.json", FIXTURES / "snapshot_manifest.json"
    )


def _state() -> screening.SnapshotState:
    bundle = _bundle()
    return screening.SnapshotState(
        status="loaded",
        reason_code="CHECK_COMPLETED",
        bundle=bundle,
        snapshot_sha256=bundle.snapshot_sha256,
        manifest_sha256=bundle.manifest_sha256,
        detail=None,
    )


def _draft(name: str) -> str:
    return (FIXTURES / name).read_text(encoding="utf-8")


def _report(name: str = "own_draft.md") -> dict:
    return screening.build_own_draft_report(
        _draft(name),
        artifact_id=name,
        artifact_format="latex" if name.endswith(".tex") else "markdown",
        state=_state(),
        checked_at=CHECKED_AT,
        recorded_at=RECORDED_AT,
    )


def _passport() -> dict:
    return yaml.safe_load((FIXTURES / "corpus_input.yaml").read_text(encoding="utf-8"))


def _enriched(state: screening.SnapshotState | None = None) -> dict:
    return screening.enrich_passport(
        _passport(),
        state=state or _state(),
        checked_at=CHECKED_AT,
        recorded_at=RECORDED_AT,
    )


def _seed_expectations() -> dict:
    value, _raw = screening._strict_json_path(
        FIXTURES / "seed_expectations.json",
        label="synthetic seed expectations",
        maximum=512 * 1024,
    )
    if not isinstance(value, dict):
        raise AssertionError("seed expectations root must be an object")
    return value


def _expect_exact_keys(
    value: object,
    *,
    required: set[str],
    optional: set[str] | None = None,
    label: str,
) -> dict:
    if not isinstance(value, dict):
        raise AssertionError(f"{label} must be an object")
    optional = optional or set()
    keys = set(value)
    if keys != required | (keys & optional):
        missing = required - keys
        unknown = keys - required - optional
        raise AssertionError(
            f"{label} keys drifted; missing={sorted(missing)!r}, "
            f"unknown={sorted(unknown)!r}"
        )
    return value


def _compiled_rules() -> dict[str, screening.CompiledRule]:
    return {rule.rule_id: rule for rule in _bundle().rules}


def _actual_suppressions(
    text: str,
    segments: list[screening.Segment],
    rules: dict[str, screening.CompiledRule],
) -> Counter[tuple[str, str]]:
    suppressed: Counter[tuple[str, str]] = Counter()
    for segment in segments:
        tokens = screening.tokenize(text[segment.start : segment.end])
        for rule in rules.values():
            included = set(screening.evaluate_expression(rule.expression, tokens))
            retained = set(screening.evaluate_rule(rule, tokens))
            suppressed[(rule.rule_id, segment.kind)] += len(included - retained)
    return +suppressed


def _has_token_boundary_negative(
    rule: screening.CompiledRule,
    text: str,
    segments: list[screening.Segment],
) -> bool:
    expression = rule.expression
    if expression.get("op") != "literal":
        return False
    literal_tokens = screening.tokenize(expression["value"])
    if len(literal_tokens) != 1:
        return False
    literal = literal_tokens[0].normalized
    return any(
        literal in token.normalized and literal != token.normalized
        for segment in segments
        for token in screening.tokenize(text[segment.start : segment.end])
    )


def _has_same_segment_exclusion(
    rule: screening.CompiledRule,
    text: str,
    segments: list[screening.Segment],
) -> bool:
    if not rule.exclude_if:
        return False
    for segment in segments:
        tokens = screening.tokenize(text[segment.start : segment.end])
        included = set(screening.evaluate_expression(rule.expression, tokens))
        if included and included - set(screening.evaluate_rule(rule, tokens)):
            return True
    return False


def _non_match_reason_holds(
    reason: str,
    rule: screening.CompiledRule,
    text: str,
    segments: list[screening.Segment],
) -> bool:
    if reason == "token_boundary":
        return _has_token_boundary_negative(rule, text, segments)
    if reason == "exclude_if_in_same_segment":
        return _has_same_segment_exclusion(rule, text, segments)
    raise AssertionError(f"unsupported synthetic non-match reason {reason!r}")


def _normalization_case_holds(
    case: str,
    match: dict,
    rule: screening.CompiledRule,
) -> bool:
    expression = rule.expression
    if expression.get("op") != "literal":
        return False
    raw = match["matched_text"]
    actual_tokens = tuple(token.normalized for token in screening.tokenize(raw))
    literal_tokens = tuple(
        token.normalized for token in screening.tokenize(expression["value"])
    )
    if actual_tokens != literal_tokens:
        return False
    if case == "nfkc_casefold":
        folded = unicodedata.normalize("NFKC", raw).casefold()
        return folded == expression["value"].casefold() and raw.casefold() != folded
    if case == "same_line_dash_separator":
        return "\n" not in raw and any(char in screening._DASHES for char in raw)
    if case == "soft_hyphen_join":
        return "\u00ad" in raw and "\n" not in raw
    if case == "line_break_hyphen_join":
        return any(
            char in screening._DASHES and index + 1 < len(raw) and raw[index + 1] == "\n"
            for index, char in enumerate(raw)
        )
    raise AssertionError(f"unsupported normalization case {case!r}")


def _alternative_matches_record(
    alternative: dict,
    match: dict,
    *,
    text: str,
    segments: dict[str, screening.Segment],
) -> bool:
    segment = segments[match["segment_id"]]
    tokens = screening.tokenize(text[segment.start : segment.end])
    span = match["source_span"]
    return any(
        segment.start + witness.codepoint_start == span["codepoint_start"]
        and segment.start + witness.codepoint_end == span["codepoint_end"]
        for witness in screening.evaluate_expression(alternative, tokens)
    )


def _spans_overlap(left: dict, right: dict) -> bool:
    if left["segment_id"] != right["segment_id"]:
        return False
    left_span = left["source_span"]
    right_span = right["source_span"]
    return max(left_span["codepoint_start"], right_span["codepoint_start"]) < min(
        left_span["codepoint_end"], right_span["codepoint_end"]
    )


def _replay_draft_expectation(
    expectation: dict,
    rules: dict[str, screening.CompiledRule],
) -> set[str]:
    expectation = _expect_exact_keys(
        expectation,
        required={
            "path",
            "expected_counts",
            "expected_matches",
            "expected_suppressions",
            "expected_non_matches",
        },
        label="draft expectation",
    )
    path = expectation["path"]
    if path not in {"own_draft.md", "own_draft.tex"}:
        raise AssertionError(f"unsupported draft expectation path {path!r}")
    text = _draft(path)
    artifact_format = "latex" if path.endswith(".tex") else "markdown"
    segments = screening.segment_document(text, artifact_format)
    segments_by_id = {segment.segment_id: segment for segment in segments}
    report = _report(path)
    if report["evaluation_status"] != "UNMEASURED":
        raise AssertionError(f"{path}: synthetic results must remain UNMEASURED")

    expected_counts = _expect_exact_keys(
        expectation["expected_counts"],
        required={
            "matched_rule_count",
            "rule_match_count",
            "unique_instance_count",
        },
        label=f"{path}.expected_counts",
    )
    for key, expected in expected_counts.items():
        if type(expected) is not int or expected < 0:
            raise AssertionError(f"{path}.expected_counts.{key} must be nonnegative int")
        if report["counts"][key] != expected:
            raise AssertionError(
                f"{path}.{key}: expected {expected}, got {report['counts'][key]}"
            )

    expected_match_counts: Counter[tuple[str, str]] = Counter()
    seen_match_keys: set[tuple[str, str]] = set()
    match_groups: dict[str, list[dict]] = {}
    group_by_match_id: dict[str, str | None] = {}
    normalization_cases: set[str] = set()
    for index, raw_expected in enumerate(expectation["expected_matches"]):
        expected = _expect_exact_keys(
            raw_expected,
            required={"rule_id", "count", "context"},
            optional={
                "matched_alternative_index",
                "overlap_group",
                "normalization_case",
            },
            label=f"{path}.expected_matches[{index}]",
        )
        rule_id = expected["rule_id"]
        context = expected["context"]
        count = expected["count"]
        if rule_id not in rules:
            raise AssertionError(f"{path}: unknown expected rule {rule_id!r}")
        if context not in screening.CONTEXTS:
            raise AssertionError(f"{path}: unknown expected context {context!r}")
        if type(count) is not int or count < 1:
            raise AssertionError(f"{path}: expected match count must be positive int")
        match_key = (rule_id, context)
        if match_key in seen_match_keys:
            raise AssertionError(f"{path}: duplicate expected match key {match_key!r}")
        seen_match_keys.add(match_key)
        expected_match_counts[match_key] = count
        actual_matches = [
            match
            for match in report["matches"]
            if (match["pattern_id"], match["context"]) == match_key
        ]

        expression = rules[rule_id].expression
        alternative_index = expected.get("matched_alternative_index")
        if expression.get("op") == "any":
            if type(alternative_index) is not int:
                raise AssertionError(f"{path}: any rule {rule_id!r} needs an alternative index")
            alternatives = expression["alternatives"]
            if not 0 <= alternative_index < len(alternatives):
                raise AssertionError(f"{path}: alternative index out of range")
            for match in actual_matches:
                matching_indexes = {
                    child_index
                    for child_index, alternative in enumerate(alternatives)
                    if _alternative_matches_record(
                        alternative,
                        match,
                        text=text,
                        segments=segments_by_id,
                    )
                }
                if matching_indexes != {alternative_index}:
                    raise AssertionError(
                        f"{path}: any alternative mismatch for {rule_id!r}: "
                        f"{sorted(matching_indexes)!r}"
                    )
        elif alternative_index is not None:
            raise AssertionError(f"{path}: non-any rule carries alternative index")

        overlap_group = expected.get("overlap_group")
        if overlap_group is not None and (
            not isinstance(overlap_group, str) or not overlap_group
        ):
            raise AssertionError(f"{path}: overlap_group must be a nonempty string")
        for match in actual_matches:
            group_by_match_id[match["match_id"]] = overlap_group
            if overlap_group is not None:
                match_groups.setdefault(overlap_group, []).append(match)

        normalization_case = expected.get("normalization_case")
        if normalization_case is not None:
            if not isinstance(normalization_case, str):
                raise AssertionError(f"{path}: normalization_case must be a string")
            normalization_cases.add(normalization_case)
            if not actual_matches or not all(
                _normalization_case_holds(normalization_case, match, rules[rule_id])
                for match in actual_matches
            ):
                raise AssertionError(
                    f"{path}: normalization case {normalization_case!r} did not replay"
                )

    actual_match_counts = Counter(
        (match["pattern_id"], match["context"]) for match in report["matches"]
    )
    if actual_match_counts != expected_match_counts:
        raise AssertionError(
            f"{path}: expected rule/context counts do not match runtime output"
        )

    for group, matches in match_groups.items():
        if len(matches) < 2 or screening._unique_instance_count(matches) != 1:
            raise AssertionError(f"{path}: overlap group {group!r} is not one component")
    for left_index, left in enumerate(report["matches"]):
        for right in report["matches"][left_index + 1 :]:
            if _spans_overlap(left, right) and (
                group_by_match_id.get(left["match_id"]) is None
                or group_by_match_id.get(left["match_id"])
                != group_by_match_id.get(right["match_id"])
            ):
                raise AssertionError(f"{path}: overlapping matches lack one shared group")

    expected_suppressions: Counter[tuple[str, str]] = Counter()
    for index, raw_expected in enumerate(expectation["expected_suppressions"]):
        expected = _expect_exact_keys(
            raw_expected,
            required={"rule_id", "count", "context", "reason"},
            label=f"{path}.expected_suppressions[{index}]",
        )
        rule_id = expected["rule_id"]
        count = expected["count"]
        context = expected["context"]
        if rule_id not in rules or not rules[rule_id].exclude_if:
            raise AssertionError(f"{path}: suppression names a non-excluding rule")
        if context not in screening.CONTEXTS:
            raise AssertionError(f"{path}: suppression context is unknown")
        if type(count) is not int or count < 1:
            raise AssertionError(f"{path}: suppression count must be positive int")
        if expected["reason"] != "exclude_if_within_token_window":
            raise AssertionError(f"{path}: unsupported suppression reason")
        key = (rule_id, context)
        if key in expected_suppressions:
            raise AssertionError(f"{path}: duplicate expected suppression {key!r}")
        expected_suppressions[key] = count
    if _actual_suppressions(text, segments, rules) != expected_suppressions:
        raise AssertionError(f"{path}: suppression oracle does not replay")

    non_match_reasons: set[str] = set()
    seen_non_matches: set[str] = set()
    for index, raw_expected in enumerate(expectation["expected_non_matches"]):
        expected = _expect_exact_keys(
            raw_expected,
            required={"rule_id", "reason"},
            label=f"{path}.expected_non_matches[{index}]",
        )
        rule_id = expected["rule_id"]
        reason = expected["reason"]
        if rule_id not in rules:
            raise AssertionError(f"{path}: non-match names unknown rule {rule_id!r}")
        if rule_id in seen_non_matches:
            raise AssertionError(f"{path}: duplicate non-match rule {rule_id!r}")
        seen_non_matches.add(rule_id)
        if any(match["pattern_id"] == rule_id for match in report["matches"]):
            raise AssertionError(f"{path}: expected non-match {rule_id!r} matched")
        if not _non_match_reason_holds(reason, rules[rule_id], text, segments):
            raise AssertionError(f"{path}: non-match reason {reason!r} did not replay")
        non_match_reasons.add(reason)
    return normalization_cases | {f"nonmatch:{reason}" for reason in non_match_reasons}


def _corpus_surface_text(entry: dict, surface: str) -> str | None:
    return entry["title"] if surface == "title" else entry.get("abstract")


def _replay_corpus_expectation(
    expectation: dict,
    rules: dict[str, screening.CompiledRule],
) -> set[str]:
    expectation = _expect_exact_keys(
        expectation,
        required={"path", "records"},
        label="corpus expectation",
    )
    if expectation["path"] != "corpus_input.yaml":
        raise AssertionError("corpus expectation path drifted")
    source_entries = {
        entry["citation_key"]: entry for entry in _passport()["literature_corpus"]
    }
    output_entries = {
        entry["citation_key"]: entry for entry in _enriched()["literature_corpus"]
    }
    records = expectation["records"]
    if not isinstance(records, list):
        raise AssertionError("corpus records must be an array")
    citation_keys = [
        record.get("citation_key") if isinstance(record, dict) else None
        for record in records
    ]
    if (
        any(not isinstance(key, str) or not key for key in citation_keys)
        or len(citation_keys) != len(set(citation_keys))
        or set(citation_keys) != set(source_entries)
        or set(citation_keys) != set(output_entries)
    ):
        raise AssertionError("corpus expectation citation inventory drifted")

    replayed_reasons: set[str] = set()
    surface_contexts = {"title": "cited_title", "abstract": "cited_abstract"}
    for record_index, raw_record in enumerate(records):
        record = _expect_exact_keys(
            raw_record,
            required={"citation_key", "surfaces"},
            label=f"corpus.records[{record_index}]",
        )
        citation_key = record["citation_key"]
        surfaces = _expect_exact_keys(
            record["surfaces"],
            required={"title", "abstract"},
            label=f"corpus.records[{citation_key}].surfaces",
        )
        source_entry = source_entries[citation_key]
        output_entry = output_entries[citation_key]
        signals = [
            signal
            for signal in output_entry["bibliographic_integrity_signals"]
            if signal.get("schema_version") == screening.SIGNAL_VERSION
            and signal.get("signal_type") == "tortured_phrase_match"
        ]
        if len(signals) != 2:
            raise AssertionError(
                f"{citation_key}: expected exactly the title and abstract signals"
            )
        for surface, context in surface_contexts.items():
            expected = _expect_exact_keys(
                surfaces[surface],
                required={"check_status", "reason", "expected_rule_ids"},
                optional={"non_match_reasons"},
                label=f"corpus.records[{citation_key}].{surface}",
            )
            matching_signals = [
                signal
                for signal in signals
                if signal["tortured_phrase_context"]["surface"] == context
            ]
            if len(matching_signals) != 1:
                raise AssertionError(
                    f"{citation_key}.{surface}: expected exactly one current signal"
                )
            signal = matching_signals[0]
            signal_context = signal["tortured_phrase_context"]
            if signal["check_status"] != expected["check_status"]:
                raise AssertionError(f"{citation_key}.{surface}: status drifted")
            if signal_context["reason_code"] != expected["reason"]:
                raise AssertionError(f"{citation_key}.{surface}: reason drifted")

            expected_rule_ids = expected["expected_rule_ids"]
            if (
                not isinstance(expected_rule_ids, list)
                or any(not isinstance(rule_id, str) for rule_id in expected_rule_ids)
                or len(expected_rule_ids) != len(set(expected_rule_ids))
                or any(rule_id not in rules for rule_id in expected_rule_ids)
            ):
                raise AssertionError(
                    f"{citation_key}.{surface}: expected_rule_ids are invalid"
                )
            actual_rule_ids = {
                match["pattern_id"] for match in signal_context["matches"]
            }
            if actual_rule_ids != set(expected_rule_ids):
                raise AssertionError(f"{citation_key}.{surface}: rule ids drifted")
            expected_finding = (
                "unresolved"
                if expected["check_status"] != "checked"
                else "detected" if expected_rule_ids else "not_detected"
            )
            if signal["finding"] != expected_finding:
                raise AssertionError(f"{citation_key}.{surface}: finding drifted")

            raw_non_matches = expected.get("non_match_reasons", [])
            if expected["check_status"] == "checked" and not expected_rule_ids:
                if not raw_non_matches:
                    raise AssertionError(
                        f"{citation_key}.{surface}: zero result lacks a rule-bound reason"
                    )
            text = _corpus_surface_text(source_entry, surface)
            seen_non_match_rules: set[str] = set()
            for reason_index, raw_reason in enumerate(raw_non_matches):
                reason_record = _expect_exact_keys(
                    raw_reason,
                    required={"rule_id", "reason"},
                    label=(
                        f"corpus.records[{citation_key}].{surface}."
                        f"non_match_reasons[{reason_index}]"
                    ),
                )
                rule_id = reason_record["rule_id"]
                reason = reason_record["reason"]
                if rule_id not in rules or rule_id in seen_non_match_rules:
                    raise AssertionError(
                        f"{citation_key}.{surface}: invalid non-match rule {rule_id!r}"
                    )
                seen_non_match_rules.add(rule_id)
                if rule_id in actual_rule_ids or text is None:
                    raise AssertionError(
                        f"{citation_key}.{surface}: non-match rule is not absent"
                    )
                one_segment = [screening.Segment("SEG-000001", context, 0, len(text))]
                if not _non_match_reason_holds(
                    reason,
                    rules[rule_id],
                    text,
                    one_segment,
                ):
                    raise AssertionError(
                        f"{citation_key}.{surface}: non-match reason did not replay"
                    )
                replayed_reasons.add(reason)
    return replayed_reasons


def _replay_seed_expectations(expectations: dict) -> None:
    expectations = _expect_exact_keys(
        expectations,
        required={
            "schema_version",
            "snapshot_id",
            "snapshot_sha256",
            "label_scope",
            "empirical_accuracy_claimed",
            "contextual_false_positive_labels_provided",
            "contextual_false_negative_labels_provided",
            "inputs",
        },
        label="seed expectations",
    )
    if expectations["schema_version"] != "tortured-phrase-seed-expectations/1.0":
        raise AssertionError("seed expectations schema_version drifted")
    bundle = _bundle()
    if (
        expectations["snapshot_id"] != bundle.snapshot["snapshot_id"]
        or expectations["snapshot_id"] != bundle.manifest["snapshot_id"]
        or expectations["snapshot_sha256"] != bundle.snapshot_sha256
    ):
        raise AssertionError("seed expectations snapshot identity drifted")
    if expectations["label_scope"] != "mechanical_matcher_conformance_only":
        raise AssertionError("seed expectations label scope drifted")
    for flag in (
        "empirical_accuracy_claimed",
        "contextual_false_positive_labels_provided",
        "contextual_false_negative_labels_provided",
    ):
        if expectations[flag] is not False:
            raise AssertionError(f"seed expectations {flag} must remain false")

    inputs = expectations["inputs"]
    if not isinstance(inputs, list):
        raise AssertionError("seed expectations inputs must be an array")
    paths = [item.get("path") if isinstance(item, dict) else None for item in inputs]
    required_paths = {"own_draft.md", "own_draft.tex", "corpus_input.yaml"}
    if (
        any(not isinstance(path, str) for path in paths)
        or len(paths) != len(set(paths))
        or set(paths) != required_paths
    ):
        raise AssertionError("seed expectations input inventory drifted")

    rules = _compiled_rules()
    draft_coverage: set[str] = set()
    corpus_non_match_reasons: set[str] = set()
    for expectation in inputs:
        if expectation["path"] == "corpus_input.yaml":
            corpus_non_match_reasons |= _replay_corpus_expectation(expectation, rules)
        else:
            draft_coverage |= _replay_draft_expectation(expectation, rules)
    required_normalization = {
        "nfkc_casefold",
        "same_line_dash_separator",
        "soft_hyphen_join",
        "line_break_hyphen_join",
    }
    if not required_normalization.issubset(draft_coverage):
        raise AssertionError("seed expectations normalization coverage drifted")
    if "nonmatch:token_boundary" not in draft_coverage:
        raise AssertionError("seed expectations draft token-boundary negative is missing")
    if corpus_non_match_reasons != {
        "token_boundary",
        "exclude_if_in_same_segment",
    }:
        raise AssertionError("seed expectations corpus non-match coverage drifted")


def _strict_dump(path: Path, value: dict) -> None:
    path.write_text(
        json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
        encoding="utf-8",
    )


def _snapshot_pair(tmp_path: Path) -> tuple[Path, Path, dict, dict]:
    snapshot = json.loads((FIXTURES / "snapshot.json").read_text(encoding="utf-8"))
    manifest = json.loads(
        (FIXTURES / "snapshot_manifest.json").read_text(encoding="utf-8")
    )
    snapshot_path = tmp_path / "snapshot.json"
    manifest_path = tmp_path / "manifest.json"
    _strict_dump(snapshot_path, snapshot)
    manifest["snapshot_sha256"] = hashlib.sha256(snapshot_path.read_bytes()).hexdigest()
    _strict_dump(manifest_path, manifest)
    return snapshot_path, manifest_path, snapshot, manifest


def _rewrite_pair(
    snapshot_path: Path,
    manifest_path: Path,
    snapshot: dict,
    manifest: dict,
) -> None:
    _strict_dump(snapshot_path, snapshot)
    manifest["snapshot_sha256"] = hashlib.sha256(snapshot_path.read_bytes()).hexdigest()
    manifest["rule_count"] = len(snapshot.get("rules", []))
    _strict_dump(manifest_path, manifest)


def test_snapshot_and_manifest_exact_hash_bind() -> None:
    bundle = _bundle()
    assert bundle.snapshot_sha256 == "962879909bfdd338047dc4569ff42188c4200fcd56a0a459b0e0f9169f2446c4"
    assert len(bundle.rules) == 17
    assert bundle.manifest["unsupported_rule_count"] == 0
    assert bundle.manifest["rights"]["basis"] == "synthetic_fixture"


def test_seed_expectations_are_fully_replayed_as_the_mechanical_oracle() -> None:
    _replay_seed_expectations(_seed_expectations())


def _expectation_input(expectations: dict, path: str) -> dict:
    return next(item for item in expectations["inputs"] if item["path"] == path)


def _corpus_surface(expectations: dict, citation_key: str, surface: str) -> dict:
    corpus = _expectation_input(expectations, "corpus_input.yaml")
    record = next(
        item for item in corpus["records"] if item["citation_key"] == citation_key
    )
    return record["surfaces"][surface]


def _mutate_seed_expectations(expectations: dict, mutation: str) -> None:
    markdown = _expectation_input(expectations, "own_draft.md")
    if mutation == "wrong_count":
        markdown["expected_counts"]["rule_match_count"] += 1
    elif mutation == "wrong_rule":
        markdown["expected_matches"][0]["rule_id"] = "syn_corpus_abstract"
    elif mutation == "wrong_context":
        markdown["expected_matches"][0]["context"] = "quote"
    elif mutation == "wrong_alternative":
        expected = next(
            item
            for item in markdown["expected_matches"]
            if "matched_alternative_index" in item
        )
        expected["matched_alternative_index"] += 1
    elif mutation == "wrong_overlap":
        expected = next(
            item for item in markdown["expected_matches"] if "overlap_group" in item
        )
        expected["overlap_group"] += "-mutated"
    elif mutation == "wrong_normalization":
        expected = next(
            item
            for item in markdown["expected_matches"]
            if item.get("normalization_case") == "nfkc_casefold"
        )
        expected["normalization_case"] = "same_line_dash_separator"
    elif mutation == "wrong_suppression":
        markdown["expected_suppressions"][0]["count"] += 1
    elif mutation == "wrong_nonmatch":
        markdown["expected_non_matches"][0]["reason"] = "exclude_if_in_same_segment"
    elif mutation == "wrong_corpus_status":
        _corpus_surface(expectations, "fixture_complete_2026", "title")[
            "check_status"
        ] = "not_checked"
    elif mutation == "wrong_corpus_reason":
        _corpus_surface(expectations, "fixture_missing_2026", "abstract")[
            "reason"
        ] = "ABSTRACT_EMPTY"
    elif mutation == "wrong_corpus_rule_id":
        _corpus_surface(expectations, "fixture_complete_2026", "title")[
            "expected_rule_ids"
        ] = ["syn_corpus_abstract"]
    elif mutation == "wrong_corpus_nonmatch":
        _corpus_surface(expectations, "fixture_negative_2026", "title")[
            "non_match_reasons"
        ][0]["rule_id"] = "syn_literal_author"
    elif mutation == "wrong_corpus_nonmatch_reason":
        _corpus_surface(expectations, "fixture_negative_2026", "title")[
            "non_match_reasons"
        ][0]["reason"] = "exclude_if_in_same_segment"
    elif mutation == "wrong_snapshot_identity":
        expectations["snapshot_sha256"] = "0" * 64
    elif mutation == "wrong_claim_flag":
        expectations["empirical_accuracy_claimed"] = True
    elif mutation == "unknown_root_key":
        expectations["unexpected"] = True
    elif mutation == "missing_root_key":
        expectations.pop("schema_version")
    elif mutation == "unknown_input":
        expectations["inputs"].append({"path": "unknown.txt"})
    elif mutation == "missing_input":
        expectations["inputs"].pop()
    elif mutation == "duplicate_input":
        expectations["inputs"].append(copy.deepcopy(markdown))
    else:  # pragma: no cover - test parameter list is closed below
        raise AssertionError(f"unknown test mutation {mutation!r}")


@pytest.mark.parametrize(
    "mutation",
    [
        "wrong_count",
        "wrong_rule",
        "wrong_context",
        "wrong_alternative",
        "wrong_overlap",
        "wrong_normalization",
        "wrong_suppression",
        "wrong_nonmatch",
        "wrong_corpus_status",
        "wrong_corpus_reason",
        "wrong_corpus_rule_id",
        "wrong_corpus_nonmatch",
        "wrong_corpus_nonmatch_reason",
        "wrong_snapshot_identity",
        "wrong_claim_flag",
        "unknown_root_key",
        "missing_root_key",
        "unknown_input",
        "missing_input",
        "duplicate_input",
    ],
)
def test_seed_expectation_mutations_fail_closed(mutation: str) -> None:
    expectations = copy.deepcopy(_seed_expectations())
    _mutate_seed_expectations(expectations, mutation)
    with pytest.raises(AssertionError):
        _replay_seed_expectations(expectations)


def test_context_detection_is_never_suppressed() -> None:
    report = _report()
    assert report["check_status"] == "checked"
    assert report["finding"] == "detected"
    assert report["counts"]["unknown_segments"] == 0
    by_rule: dict[str, list[dict]] = {}
    for match in report["matches"]:
        by_rule.setdefault(match["pattern_id"], []).append(match)
    assert by_rule["syn_context_quote"][0]["context"] == "quote"
    assert {item["context"] for item in by_rule["syn_context_code"]} == {
        "code_or_verbatim"
    }
    assert by_rule["syn_context_reference"][0]["context"] == "reference_entry"
    assert all(
        item["disposition"] == "preserve_verbatim_review_context"
        for rule_id in ("syn_context_quote", "syn_context_code", "syn_context_reference")
        for item in by_rule[rule_id]
    )


def test_exclude_if_is_segment_scoped() -> None:
    matches = [
        item for item in _report()["matches"] if item["pattern_id"] == "syn_exclude_segment"
    ]
    assert len(matches) == 1
    assert matches[0]["context"] == "quote"


@pytest.mark.parametrize(
    ("text", "artifact_format"),
    [
        ("moonlit pickle\n\nrecipe glossary", "markdown"),
        (
            "# References\nmoonlit pickle\nrecipe glossary\n",
            "markdown",
        ),
        (
            "\\begin{thebibliography}{9}\n"
            "\\bibitem{a} moonlit pickle\n"
            "\\bibitem{b} recipe glossary\n"
            "\\end{thebibliography}\n",
            "latex",
        ),
    ],
)
def test_exclude_if_never_crosses_paragraph_or_reference_entry(
    text: str, artifact_format: str
) -> None:
    rule = _compiled_rules()["syn_exclude_segment"]
    segments = screening.segment_document(text, artifact_format)
    retained = [
        witness
        for segment in segments
        for witness in screening.evaluate_rule(
            rule, screening.tokenize(text[segment.start : segment.end])
        )
    ]
    assert len(retained) == 1


def test_overlaps_preserve_rule_hits_and_cluster_unique_instances() -> None:
    matches = [
        item
        for item in _report()["matches"]
        if item["pattern_id"] in {"syn_overlap_long", "syn_overlap_short"}
    ]
    assert len(matches) == 2
    assert screening._unique_instance_count(matches) == 1


@pytest.mark.parametrize(
    "rule_id",
    ["syn_nfkc_casefold", "syn_dash_same_line", "syn_soft_hyphen", "syn_hyphen_line_break"],
)
def test_frozen_normalization_cases_match(rule_id: str) -> None:
    assert any(item["pattern_id"] == rule_id for item in _report()["matches"])


@pytest.mark.parametrize(
    ("raw", "expected", "expected_start"),
    [
        ("a-\nb", ["ab"], 0),
        ("silver- \nleaf", ["silver", "leaf"], 0),
        ("silver—\nleaf", ["silver", "leaf"], 0),
        ("1-\na", ["1", "a"], 0),
        ("a-\n2", ["a", "2"], 0),
        ("a1-\nb", ["a1", "b"], 0),
        ("a\u0301-\nb", ["á", "b"], 0),
        ("\u0301alpha", ["alpha"], 1),
    ],
)
def test_only_exact_ascii_immediate_line_hyphen_joins_and_marks_cannot_start(
    raw: str, expected: list[str], expected_start: int
) -> None:
    tokens = screening.tokenize(raw)
    assert [token.normalized for token in tokens] == expected
    assert tokens[0].start == expected_start


def test_token_boundary_prevents_substring_match() -> None:
    assert all(item["pattern_id"] != "syn_boundary_orb" for item in _report()["matches"])


def test_repeated_literal_hits_fail_closed_at_the_witness_cap() -> None:
    tokens = screening.tokenize(" ".join(["orb"] * (screening.MAX_NODE_WITNESSES + 1)))
    with pytest.raises(screening.MatchLimitError, match="literal produced more"):
        screening.evaluate_expression({"op": "literal", "value": "orb"}, tokens)


def test_witness_reducer_deduplicates_only_exact_spans() -> None:
    inner = screening.Witness(2, 3, 2, 3)
    same = screening.Witness(2, 3, 2, 3)
    outer = screening.Witness(1, 4, 1, 4)
    separate = screening.Witness(5, 6, 5, 6)
    assert screening._minimal_witnesses([outer, inner, same, separate]) == [
        outer,
        inner,
        separate,
    ]


def test_any_and_all_preserve_distinct_nested_witnesses() -> None:
    tokens = screening.tokenize("amber reed reed")
    any_values = screening.evaluate_expression(
        {
            "op": "any",
            "alternatives": [
                {"op": "literal", "value": "amber"},
                {"op": "literal", "value": "amber reed"},
            ],
        },
        tokens,
    )
    assert [(item.token_start, item.token_end) for item in any_values] == [
        (0, 1),
        (0, 2),
    ]
    all_values = screening.evaluate_expression(
        {
            "op": "all",
            "terms": [
                {"op": "literal", "value": "amber"},
                {"op": "literal", "value": "reed"},
            ],
            "max_span_tokens": 3,
        },
        tokens,
    )
    assert [(item.token_start, item.token_end) for item in all_values] == [
        (0, 2),
        (0, 3),
    ]


def test_full_scan_counts_nested_same_rule_witnesses_as_one_overlap_instance() -> None:
    expression = {
        "op": "any",
        "alternatives": [
            {"op": "literal", "value": "amber"},
            {"op": "literal", "value": "amber reed"},
        ],
    }
    base = _bundle()
    rule = screening.CompiledRule(
        rule_id="nested_union",
        expression=expression,
        exclude_if=(),
        rule_sha256=screening._sha256_text(screening._canonical_json(expression)),
        semantic_key=screening._canonical_json(expression),
    )
    bundle = screening.SnapshotBundle(
        snapshot=base.snapshot,
        manifest=base.manifest,
        snapshot_sha256=base.snapshot_sha256,
        manifest_sha256=base.manifest_sha256,
        rules=(rule,),
        unicode_data_version=base.unicode_data_version,
    )
    text = "amber reed"
    matches, counts = screening.scan_segments(
        text,
        [screening.Segment("SEG-000001", "author_prose", 0, len(text))],
        bundle,
        artifact_sha256=hashlib.sha256(text.encode()).hexdigest(),
        surface="own_draft",
    )
    assert len(matches) == 2
    assert counts["rule_match_count"] == 2
    assert counts["matched_rule_count"] == 1
    assert counts["unique_instance_count"] == 1


def test_utf8_and_codepoint_spans_replay_multibyte_text() -> None:
    report = screening.build_own_draft_report(
        "前文 luminous turnip 後文",
        artifact_id="unicode.md",
        artifact_format="markdown",
        state=_state(),
        checked_at=CHECKED_AT,
        recorded_at=RECORDED_AT,
    )
    match = next(item for item in report["matches"] if item["pattern_id"] == "syn_literal_author")
    span = match["source_span"]
    text = "前文 luminous turnip 後文"
    assert text[span["codepoint_start"] : span["codepoint_end"]] == match["matched_text"]
    raw = text.encode("utf-8")
    assert raw[span["utf8_start"] : span["utf8_end"]].decode() == match["matched_text"]


@pytest.mark.parametrize("name", ["own_draft.md", "own_draft.tex"])
def test_segment_partition_covers_source_exactly(name: str) -> None:
    text = _draft(name)
    segments = screening.segment_document(text, "latex" if name.endswith(".tex") else "markdown")
    assert segments[0].start == 0
    assert segments[-1].end == len(text)
    assert all(left.end == right.start for left, right in zip(segments, segments[1:]))


def test_reference_heading_inside_fence_does_not_reclassify_following_prose() -> None:
    text = "```text\n# References\n```\nFollowing luminous turnip."
    segments = screening.segment_document(text, "markdown")
    following = next(item for item in segments if item.start <= text.index("Following") < item.end)
    assert following.kind == "author_prose"


def test_reference_heading_inside_html_comment_does_not_reclassify_prose() -> None:
    text = "<!--\n# References\n-->\nordinary luminous turnip\n"
    segments = screening.segment_document(text, "markdown")
    following = next(
        item for item in segments if item.start <= text.index("ordinary") < item.end
    )
    assert following.kind == "author_prose"
    report = screening.build_own_draft_report(
        text,
        artifact_id="comment-heading.md",
        artifact_format="markdown",
        state=_state(),
        checked_at=CHECKED_AT,
        recorded_at=RECORDED_AT,
    )
    prose_match = next(
        item for item in report["matches"] if item["matched_text"] == "luminous turnip"
    )
    assert prose_match["context"] == "author_prose"


@pytest.mark.parametrize("marker", ["```python", "~~~text"])
def test_fence_opener_inside_html_comment_cannot_leak_unknown_context(
    marker: str,
) -> None:
    text = f"<!--\n{marker}\n-->\nordinary luminous turnip\n"
    segments = screening.segment_document(text, "markdown")
    following = next(
        item for item in segments if item.start <= text.index("ordinary") < item.end
    )
    assert following.kind == "author_prose"
    assert all(item.kind != "unknown" for item in segments)


def test_latex_environment_opener_inside_comment_cannot_leak_context() -> None:
    text = (
        "% \\begin{thebibliography}{9}\n"
        "ordinary luminous turnip\n"
        "\\end{thebibliography}\n"
    )
    segments = screening.segment_document(text, "latex")
    following = next(
        item for item in segments if item.start <= text.index("ordinary") < item.end
    )
    assert following.kind == "author_prose"
    report = screening.build_own_draft_report(
        text,
        artifact_id="comment-environment.tex",
        artifact_format="latex",
        state=_state(),
        checked_at=CHECKED_AT,
        recorded_at=RECORDED_AT,
    )
    prose_match = next(
        item for item in report["matches"] if item["matched_text"] == "luminous turnip"
    )
    assert prose_match["context"] == "author_prose"


@pytest.mark.parametrize(
    ("environment", "expected_kind"),
    [
        ("thebibliography", "reference_entry"),
        ("quote", "quote"),
        ("verbatim", "code_or_verbatim"),
    ],
)
def test_latex_environment_escape_parity(
    environment: str, expected_kind: str
) -> None:
    even = (
        "\\" * 2
        + f"begin{{{environment}}}\nordinary\n"
        + "\\" * 2
        + f"end{{{environment}}}\n"
    )
    assert all(
        item.kind == "author_prose"
        for item in screening.segment_document(even, "latex")
    )
    odd = (
        "\\" * 3
        + f"begin{{{environment}}}\nordinary\n"
        + "\\" * 3
        + f"end{{{environment}}}\n"
    )
    assert any(
        item.kind == expected_kind
        for item in screening.segment_document(odd, "latex")
    )


def test_latex_verb_escape_parity_and_opaque_opener_precedence() -> None:
    even = r"\\verb|ordinary luminous turnip|"
    assert all(
        item.kind == "author_prose"
        for item in screening.segment_document(even, "latex")
    )
    active = r"\verb|\begin{verbatim}| ordinary luminous turnip"
    segments = screening.segment_document(active, "latex")
    following = next(
        item for item in segments if item.start <= active.index("ordinary") < item.end
    )
    assert following.kind == "author_prose"
    assert all(item.kind != "unknown" for item in segments)


def test_source_order_opaque_lexer_does_not_let_inner_opener_consume_later_close() -> None:
    text = (
        r"\verb|\begin{verbatim}| "
        r"\begin{verbatim} recipe glossary \end{verbatim} moonlit pickle"
    )
    segments = screening.segment_document(text, "latex")
    real_environment = text.index(r"\begin{verbatim}", len(r"\verb|"))
    later_prose = text.index("moonlit pickle")
    assert next(
        item for item in segments if item.start <= real_environment < item.end
    ).kind == "code_or_verbatim"
    assert next(
        item for item in segments if item.start <= later_prose < item.end
    ).kind == "author_prose"
    report = screening.build_own_draft_report(
        text,
        artifact_id="source-order.tex",
        artifact_format="latex",
        state=_state(),
        checked_at=CHECKED_AT,
        recorded_at=RECORDED_AT,
    )
    assert any(
        item["pattern_id"] == "syn_exclude_segment"
        and item["matched_text"] == "moonlit pickle"
        for item in report["matches"]
    )


def test_source_order_markdown_comment_does_not_consume_later_inline_code() -> None:
    text = "<!-- ` --> `luminous turnip`"
    segments = screening.segment_document(text, "markdown")
    later = text.index("`luminous")
    assert next(item for item in segments if item.start <= later < item.end).kind == (
        "code_or_verbatim"
    )
    assert all(item.kind != "unknown" for item in segments)


def test_blockquote_marker_inside_comment_cannot_capture_later_prose() -> None:
    text = '<!--\n> --> "recipe glossary" moonlit pickle\n'
    segments = screening.segment_document(text, "markdown")
    target = text.index("moonlit pickle")
    assert next(item for item in segments if item.start <= target < item.end).kind == (
        "author_prose"
    )
    report = screening.build_own_draft_report(
        text,
        artifact_id="comment-blockquote.md",
        artifact_format="markdown",
        state=_state(),
        checked_at=CHECKED_AT,
        recorded_at=RECORDED_AT,
    )
    assert any(
        item["pattern_id"] == "syn_exclude_segment"
        and item["matched_text"] == "moonlit pickle"
        for item in report["matches"]
    )


def test_context_openers_inside_opaque_bytes_do_not_consume_later_context() -> None:
    text = '`"` "recipe glossary" moonlit pickle '
    text += '`[` [Visible title](https://doi.org/10.1/example)'
    segments = screening.segment_document(text, "markdown")
    glossary = text.index('"recipe glossary"')
    title = text.index("Visible title")
    assert next(item for item in segments if item.start <= glossary < item.end).kind == (
        "quote"
    )
    assert next(item for item in segments if item.start <= title < item.end).kind == (
        "cited_title"
    )
    report = screening.build_own_draft_report(
        text,
        artifact_id="opaque-context.md",
        artifact_format="markdown",
        state=_state(),
        checked_at=CHECKED_AT,
        recorded_at=RECORDED_AT,
    )
    assert any(
        item["pattern_id"] == "syn_exclude_segment"
        and item["matched_text"] == "moonlit pickle"
        for item in report["matches"]
    )


@pytest.mark.parametrize(
    "text",
    [
        r"\verbose ordinary luminous turnip",
        r"\verbatim ordinary luminous turnip",
    ],
)
def test_latex_verb_control_word_prefixes_remain_prose(text: str) -> None:
    assert all(
        item.kind == "author_prose"
        for item in screening.segment_document(text, "latex")
    )


def test_latex_starred_verb_and_nested_quote_are_recognized() -> None:
    starred = r"\verb*|ordinary luminous turnip|"
    assert any(
        item.kind == "code_or_verbatim"
        and starred[item.start : item.end] == starred
        for item in screening.segment_document(starred, "latex")
    )
    nested = (
        r"\begin{quote} outer \begin{quote} inner \end{quote} "
        r"tail \end{quote}"
    )
    tail = nested.index("tail")
    assert next(
        item
        for item in screening.segment_document(nested, "latex")
        if item.start <= tail < item.end
    ).kind == "quote"


@pytest.mark.parametrize("text", [r"\verb ", "\\verb\n", r"\verb* "])
def test_malformed_bare_latex_verb_is_unknown(text: str) -> None:
    assert any(
        item.kind == "unknown"
        for item in screening.segment_document(text, "latex")
    )


def test_starred_latex_verb_cannot_backtrack_into_unstarred_delimiter() -> None:
    text = r"\verb* foo * ordinary luminous turnip"
    segments = screening.segment_document(text, "latex")
    assert len(segments) == 1
    assert segments[0].kind == "unknown"


def test_latex_accent_macro_quotes_remain_author_prose() -> None:
    text = r'\"o ordinary luminous turnip \"u'
    assert all(
        item.kind == "author_prose"
        for item in screening.segment_document(text, "latex")
    )


@pytest.mark.parametrize(
    "target",
    [
        "HTTPS://DOI.ORG/10.1/example",
        "HTTP://DX.DOI.ORG/10.1/example",
        "DOI:10.1/example",
    ],
)
def test_doi_title_prefix_is_ascii_case_insensitive(target: str) -> None:
    text = f"[Cited Turnip]({target})"
    title = text.index("Cited Turnip")
    assert next(
        item
        for item in screening.segment_document(text, "markdown")
        if item.start <= title < item.end
    ).kind == "cited_title"


def test_opaque_opener_cap_precedes_unclosed_verb_pairing(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(screening, "MAX_PARSE_INTERVALS", 3)
    with pytest.raises(screening.MatchLimitError, match="opaque parse candidates"):
        screening.segment_document(r"\verb!" * 4, "latex")


def test_unclosed_context_scanners_advance_monotonically() -> None:
    text = "[" * 20_000 + "\n" + "“" * 10_000
    segments = screening.segment_document(text, "markdown")
    assert len(segments) == 1
    assert segments[0].kind == "author_prose"


def test_escaped_latex_environment_closer_does_not_close_early() -> None:
    text = (
        "\\begin{thebibliography}{9}\n"
        "\\\\end{thebibliography}\n"
        "ordinary luminous turnip\n"
        "\\end{thebibliography}\n"
    )
    following = next(
        item
        for item in screening.segment_document(text, "latex")
        if item.start <= text.index("ordinary") < item.end
    )
    assert following.kind == "reference_entry"


@pytest.mark.parametrize(
    "text",
    [
        r"\(\begin{quote}\) ordinary luminous turnip",
        r"$\begin{thebibliography}$ ordinary luminous turnip",
        r"\[\begin{verbatim}\] ordinary luminous turnip",
    ],
)
def test_latex_environment_openers_inside_math_are_opaque(text: str) -> None:
    segments = screening.segment_document(text, "latex")
    following = next(
        item for item in segments if item.start <= text.index("ordinary") < item.end
    )
    assert following.kind == "author_prose"
    assert all(item.kind != "unknown" for item in segments)


@pytest.mark.parametrize("artifact_format", ["markdown", "latex"])
def test_odd_backslash_escaped_dollar_is_literal_prose(
    artifact_format: str,
) -> None:
    text = r"Cost is \$5."
    segments = screening.segment_document(text, artifact_format)
    assert all(segment.kind == "author_prose" for segment in segments)


def test_markdown_backtick_escape_parity_is_respected() -> None:
    escaped = r"Literal \` tick."
    assert all(
        segment.kind == "author_prose"
        for segment in screening.segment_document(escaped, "markdown")
    )
    active = r"Literal \\`code` tick."
    assert any(
        segment.kind == "code_or_verbatim"
        for segment in screening.segment_document(active, "markdown")
    )


def test_latex_percent_escape_parity_is_respected() -> None:
    escaped = r"Literal \% text."
    assert all(
        segment.kind == "author_prose"
        for segment in screening.segment_document(escaped, "latex")
    )
    active = r"Literal \\% comment"
    assert any(
        segment.kind == "code_or_verbatim"
        for segment in screening.segment_document(active, "latex")
    )


def test_unclosed_construct_is_unknown_and_degrades_not_clean() -> None:
    report = screening.build_own_draft_report(
        "Ordinary prose `luminous turnip",
        artifact_id="broken.md",
        artifact_format="markdown",
        state=_state(),
        checked_at=CHECKED_AT,
        recorded_at=RECORDED_AT,
    )
    assert report["check_status"] == "degraded"
    assert report["finding"] == "unresolved"
    assert report["reason_code"] == "DOCUMENT_PARSE_DEGRADED"
    assert report["counts"]["unknown_segments"] > 0
    assert report["matches"]
    assert report["matches"][0]["disposition"] == "review_unknown_no_automatic_rewrite"


def test_segment_resource_cap_degrades_without_partial_matches(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(screening, "MAX_SEGMENTS", 1)
    report = screening.build_own_draft_report(
        "prose `code` prose",
        artifact_id="many-segments.md",
        artifact_format="markdown",
        state=_state(),
        checked_at=CHECKED_AT,
        recorded_at=RECORDED_AT,
    )
    assert report["check_status"] == "degraded"
    assert report["reason_code"] == "MATCH_RESOURCE_LIMIT"
    assert report["matches"] == []
    assert report["counts"]["rules_evaluated"] == 0


@pytest.mark.parametrize(
    "text",
    [
        "a\n\nb\n\nc\n\n",
        "# References\none\ntwo\nthree\n",
    ],
)
def test_partition_boundaries_fail_while_collecting(
    monkeypatch: pytest.MonkeyPatch, text: str
) -> None:
    monkeypatch.setattr(screening, "MAX_SEGMENTS", 2)
    with pytest.raises(screening.MatchLimitError, match="document partition exceeds 2"):
        screening.segment_document(text, "markdown")


def test_over_token_input_fails_before_utf8_endpoint_projection(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bundle = _bundle()
    monkeypatch.setattr(screening, "MAX_TOKENS", 1)

    def unexpected_offsets(_text, _indices):
        raise AssertionError("UTF-8 endpoint projection must follow token admission")

    monkeypatch.setattr(screening, "_selected_byte_offsets", unexpected_offsets)
    with pytest.raises(screening.MatchLimitError, match="token count exceeds 1"):
        screening.scan_segments(
            "alpha beta",
            [screening.Segment("SEG-000001", "author_prose", 0, 10)],
            bundle,
            artifact_sha256=hashlib.sha256(b"alpha beta").hexdigest(),
            surface="own_draft",
        )


def test_raw_token_expansion_is_bounded_before_normalization(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(screening, "MAX_RAW_TOKEN_CODEPOINTS", 2)

    def unexpected_normalization(_value: str):
        raise AssertionError("overlong raw token must fail before NFKC expansion")

    monkeypatch.setattr(screening, "_normalized_token_parts", unexpected_normalization)
    with pytest.raises(screening.MatchLimitError, match="raw token exceeds 2"):
        screening.tokenize("\ufdfa" * 3)


def test_raw_token_cap_accepts_n_and_rejects_n_plus_one(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(screening, "MAX_RAW_TOKEN_CODEPOINTS", 2)
    assert [item.normalized for item in screening.tokenize("ab")] == ["ab"]
    with pytest.raises(screening.MatchLimitError, match="raw token exceeds 2"):
        screening.tokenize("abc")


def test_parser_work_budget_accepts_n_and_rejects_n_plus_one(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(screening, "MAX_PARSE_WORK_UNITS", 2)
    budget = screening.ParseWorkBudget()
    budget.spend()
    budget.spend()
    with pytest.raises(screening.MatchLimitError, match="parser work exceeds 2"):
        budget.spend()


def test_escaped_and_doi_closer_candidates_spend_parser_budget(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(screening, "MAX_PARSE_WORK_UNITS", 2)
    accepted = screening.ParseWorkBudget()
    assert screening._find_unescaped(r"\$$", "$", 0, budget=accepted) == 2
    exhausted = screening.ParseWorkBudget()
    with pytest.raises(screening.MatchLimitError, match="parser work exceeds 2"):
        screening._find_unescaped(r"\$\$$", "$", 0, budget=exhausted)
    doi_budget = screening.ParseWorkBudget()
    with pytest.raises(screening.MatchLimitError, match="parser work exceeds 2"):
        screening._doi_title_intervals(
            "[title](doi:10.1/example)",
            excluded=(),
            budget=doi_budget,
        )


@pytest.mark.parametrize(
    ("text", "artifact_format"),
    [
        ("<!--\n> one\n> two\n> three\n-->", "markdown"),
        (r"\end{quote}\end{quote}\end{quote}\end{quote}", "latex"),
    ],
)
def test_excluded_and_unmatched_context_candidates_spend_parser_budget(
    monkeypatch: pytest.MonkeyPatch,
    text: str,
    artifact_format: str,
) -> None:
    monkeypatch.setattr(screening, "MAX_PARSE_WORK_UNITS", 3)
    with pytest.raises(screening.MatchLimitError, match="parser work exceeds 3"):
        screening.segment_document(text, artifact_format)


def test_selected_utf8_offsets_are_exact_and_endpoint_bounded() -> None:
    text = "A台灣B"
    assert screening._selected_byte_offsets(text, {0, 1, 3, 4}) == {
        0: 0,
        1: 1,
        3: 7,
        4: 8,
    }


def test_delimiter_parser_enforces_interval_cap_before_return(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(screening, "MAX_PARSE_INTERVALS", 2)
    with pytest.raises(screening.MatchLimitError, match="parse interval count exceeds 2"):
        screening._paired_delimiter_intervals(
            "$one$ $two$ $three$", "$", "$", "code_or_verbatim"
        )


def test_rule_by_segment_work_is_globally_bounded(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(screening, "MAX_RULE_SEGMENT_EVALUATIONS", 1)
    with pytest.raises(
        screening.MatchLimitError, match="rule-by-segment evaluations exceed 1"
    ):
        screening.scan_segments(
            "luminous turnip",
            [screening.Segment("SEG-000001", "author_prose", 0, 16)],
            _bundle(),
            artifact_sha256=hashlib.sha256(b"luminous turnip").hexdigest(),
            surface="own_draft",
        )


def test_literal_and_composition_work_budget_is_shared_across_corpus(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(screening, "MAX_MATCH_WORK_UNITS", 300)
    output = _enriched()
    first, second = output["literature_corpus"][:2]
    assert all(
        signal["check_status"] == "checked"
        for signal in first["bibliographic_integrity_signals"]
    )
    second_title = next(
        signal
        for signal in second["bibliographic_integrity_signals"]
        if signal["tortured_phrase_context"]["surface"] == "cited_title"
    )
    assert second_title["check_status"] == "degraded"
    assert (
        second_title["tortured_phrase_context"]["reason_code"]
        == "MATCH_RESOURCE_LIMIT"
    )
    assert second_title["tortured_phrase_context"]["matches"] == []


def test_report_digest_and_full_replay() -> None:
    report = _report()
    screening.validate_own_draft_report(report, _draft("own_draft.md"), state=_state())
    report["counts"]["rule_match_count"] += 1
    with pytest.raises(screening.ScreeningError, match="report_sha256"):
        screening.validate_own_draft_report(report, _draft("own_draft.md"), state=_state())


def test_rehashed_report_still_fails_source_replay() -> None:
    report = _report()
    report["matches"][0]["matched_text"] = "forged"
    report["matches"][0]["matched_text_sha256"] = screening._sha256_text("forged")
    report["report_sha256"] = screening._report_digest(report)
    with pytest.raises(screening.ScreeningError, match="replay"):
        screening.validate_own_draft_report(report, _draft("own_draft.md"), state=_state())


def test_oversized_full_report_collapses_to_a_self_readable_degraded_artifact(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    text = " ".join(["luminous turnip"] * 100)
    monkeypatch.setattr(screening, "MAX_ADVISORY_BYTES", 5000)
    report = screening.build_own_draft_report(
        text,
        artifact_id="bounded.md",
        artifact_format="markdown",
        state=_state(),
        checked_at=CHECKED_AT,
        recorded_at=RECORDED_AT,
    )
    assert report["check_status"] == "degraded"
    assert report["reason_code"] == "MATCH_RESOURCE_LIMIT"
    assert report["matches"] == []
    assert len(screening._pretty_json_bytes(report)) <= screening.MAX_ADVISORY_BYTES
    path = tmp_path / "report.json"
    screening._atomic_write_json(
        path, report, maximum=screening.MAX_ADVISORY_BYTES
    )
    assert screening._load_report(path) == report
    screening.validate_own_draft_report(report, text, state=_state())


def test_bounded_reader_rejects_before_consuming_beyond_limit(tmp_path: Path) -> None:
    path = tmp_path / "oversized.bin"
    path.write_bytes(b"x" * 9)
    with pytest.raises(screening.MatchLimitError, match="exceeds 8 bytes"):
        screening._read_bounded_bytes(path, maximum=8)


def test_no_snapshot_is_explicit_not_checked() -> None:
    state = screening.snapshot_state(None, None)
    report = screening.build_own_draft_report(
        "luminous turnip",
        artifact_id="draft.md",
        artifact_format="markdown",
        state=state,
        checked_at=CHECKED_AT,
        recorded_at=RECORDED_AT,
    )
    assert report["check_status"] == "not_checked"
    assert report["finding"] == "unresolved"
    assert report["reason_code"] == "SNAPSHOT_NOT_PROVIDED"
    assert report["matches"] == []


@pytest.mark.parametrize(
    "state",
    [
        screening.snapshot_state(None, None),
        screening.snapshot_state(FIXTURES / "snapshot.json", None),
    ],
)
def test_empty_draft_preserves_missing_or_degraded_snapshot_authority(
    state: screening.SnapshotState,
) -> None:
    report = screening.build_own_draft_report(
        "",
        artifact_id="empty.md",
        artifact_format="markdown",
        state=state,
        checked_at=CHECKED_AT,
        recorded_at=RECORDED_AT,
    )
    assert report["check_status"] == (
        "not_checked" if state.status == "not_checked" else "degraded"
    )
    assert report["reason_code"] == state.reason_code
    assert report["finding"] == "unresolved"
    screening.validate_own_draft_report(report, "", state=state)


def test_empty_draft_is_degraded_never_a_zero_match() -> None:
    report = screening.build_own_draft_report(
        " \t\n",
        artifact_id="empty.md",
        artifact_format="markdown",
        state=_state(),
        checked_at=CHECKED_AT,
        recorded_at=RECORDED_AT,
    )
    assert report["check_status"] == "degraded"
    assert report["finding"] == "unresolved"
    assert report["reason_code"] == "DOCUMENT_EMPTY"
    assert report["matches"] == []
    assert report["counts"]["rules_evaluated"] == 0


def test_snapshot_byte_tamper_fails_hash_before_content_access() -> None:
    manifest = FIXTURES / "snapshot_manifest.json"
    state = screening.snapshot_state(FIXTURES / "own_draft.md", manifest)
    assert state.status == "degraded"
    assert state.reason_code == "SNAPSHOT_HASH_MISMATCH"


@pytest.mark.parametrize(
    ("raw", "reason"),
    [
        (b"\xef\xbb\xbf{}", "SNAPSHOT_BYTES_INVALID"),
        (b"\xff", "SNAPSHOT_BYTES_INVALID"),
        (b'{"schema_version":"a","schema_version":"b"}', "SNAPSHOT_BYTES_INVALID"),
        (b'{"x":NaN}', "SNAPSHOT_BYTES_INVALID"),
    ],
)
def test_strict_snapshot_loader_rejects_unsafe_bytes(
    tmp_path: Path, raw: bytes, reason: str
) -> None:
    snapshot_path = tmp_path / "bad.json"
    snapshot_path.write_bytes(raw)
    manifest = json.loads(
        (FIXTURES / "snapshot_manifest.json").read_text(encoding="utf-8")
    )
    manifest["snapshot_sha256"] = hashlib.sha256(raw).hexdigest()
    manifest_path = tmp_path / "manifest.json"
    _strict_dump(manifest_path, manifest)
    state = screening.snapshot_state(snapshot_path, manifest_path)
    assert state.status == "degraded"
    assert state.reason_code == reason


def test_draft_reader_rejects_isolated_carriage_return(tmp_path: Path) -> None:
    draft = tmp_path / "draft.md"
    draft.write_bytes(b"alpha\rbeta")
    with pytest.raises(screening.ScreeningError, match="isolated carriage return"):
        screening._read_strict_text(
            draft, maximum=screening.MAX_DOCUMENT_BYTES, label="draft"
        )


def test_direct_builder_allows_crlf_but_rejects_isolated_carriage_return() -> None:
    screening.build_own_draft_report(
        "alpha\r\nbeta",
        artifact_id="draft.md",
        artifact_format="markdown",
        state=_state(),
        checked_at=CHECKED_AT,
        recorded_at=RECORDED_AT,
    )
    with pytest.raises(screening.ScreeningError, match="isolated carriage return"):
        screening.build_own_draft_report(
            "alpha\rbeta",
            artifact_id="draft.md",
            artifact_format="markdown",
            state=_state(),
            checked_at=CHECKED_AT,
            recorded_at=RECORDED_AT,
        )


def test_manifest_hash_mismatch_never_checks_remaining_rules(tmp_path: Path) -> None:
    snapshot_path, manifest_path, snapshot, manifest = _snapshot_pair(tmp_path)
    snapshot["rules"][0]["expression"]["value"] = "changed phrase"
    _strict_dump(snapshot_path, snapshot)
    state = screening.snapshot_state(snapshot_path, manifest_path)
    assert state.reason_code == "SNAPSHOT_HASH_MISMATCH"


def test_manifest_snapshot_identity_must_match_hash_bound_snapshot(
    tmp_path: Path,
) -> None:
    snapshot_path, manifest_path, _snapshot, manifest = _snapshot_pair(tmp_path)
    manifest["snapshot_id"] = "forged-snapshot-id"
    _strict_dump(manifest_path, manifest)
    state = screening.snapshot_state(snapshot_path, manifest_path)
    assert state.status == "degraded"
    assert state.reason_code == "SNAPSHOT_HASH_MISMATCH"


@pytest.mark.parametrize(
    "mutation",
    [
        "synthetic_reference",
        "user_without_declaration",
        "permission_without_reference",
        "unresolved_but_permitted",
        "null_source_locator",
    ],
)
def test_manifest_rights_and_source_projection_fail_closed(
    tmp_path: Path, mutation: str
) -> None:
    snapshot_path, manifest_path, _snapshot, manifest = _snapshot_pair(tmp_path)
    if mutation == "synthetic_reference":
        manifest["rights"]["reference"] = "unexpected reference"
    elif mutation == "user_without_declaration":
        manifest["supply_mode"] = "user_supplied"
        manifest["rights"] = {
            "basis": "user_declared_authorized",
            "redistribution_status": "permitted",
            "reference": None,
            "user_declaration": None,
        }
    elif mutation == "permission_without_reference":
        manifest["supply_mode"] = "user_supplied"
        manifest["rights"] = {
            "basis": "written_permission",
            "redistribution_status": "permitted",
            "reference": None,
            "user_declaration": None,
        }
    elif mutation == "unresolved_but_permitted":
        manifest["supply_mode"] = "user_supplied"
        manifest["rights"] = {
            "basis": "unresolved",
            "redistribution_status": "permitted",
            "reference": None,
            "user_declaration": None,
        }
    else:
        manifest["source"]["locator"] = None
    _strict_dump(manifest_path, manifest)
    state = screening.snapshot_state(snapshot_path, manifest_path)
    assert state.status == "degraded"
    assert state.reason_code == "SNAPSHOT_MANIFEST_INVALID"


def test_advisory_schema_mirrors_manifest_rights_conditionals() -> None:
    report = _report()
    validator = Draft202012Validator(
        screening._load_schema(screening.ADVISORY_SCHEMA_PATH),
        format_checker=Draft202012Validator.FORMAT_CHECKER,
    )
    rights = report["input_binding"]["snapshot"]["rights"]
    rights["basis"] = "user_declared_authorized"
    rights["user_declaration"] = None
    assert list(validator.iter_errors(report))


def test_explicit_but_unreadable_snapshot_is_degraded_not_absent(
    tmp_path: Path,
) -> None:
    missing = tmp_path / "missing-snapshot.json"
    state = screening.snapshot_state(missing, FIXTURES / "snapshot_manifest.json")
    assert state.status == "degraded"
    assert state.reason_code == "SNAPSHOT_BYTES_INVALID"
    signal = screening.build_cited_signal(
        _passport()["literature_corpus"][0],
        surface="cited_title",
        state=state,
        checked_at=CHECKED_AT,
        recorded_at=RECORDED_AT,
    )
    assert signal["check_status"] == "degraded"
    assert signal["tortured_phrase_context"]["reason_code"] == "SNAPSHOT_BYTES_INVALID"


@pytest.mark.parametrize(
    ("mutation", "expected_reason"),
    [
        (lambda snap, man: snap.update({"grammar_profile": "unknown/9"}), "SNAPSHOT_PROFILE_UNSUPPORTED"),
        (lambda snap, man: snap.update({"rules": []}), "SNAPSHOT_MANIFEST_INVALID"),
        (
            lambda snap, man: snap["rules"][0].update(
                {"expression": {"op": "regex", "value": ".*"}}
            ),
            "SNAPSHOT_RULES_UNSUPPORTED",
        ),
        (
            lambda snap, man: snap["rules"].append(copy.deepcopy(snap["rules"][0])),
            "SNAPSHOT_RULES_UNSUPPORTED",
        ),
        (
            lambda snap, man: man.update({"unsupported_rule_count": 1}),
            "SNAPSHOT_RULES_UNSUPPORTED",
        ),
    ],
)
def test_invalid_or_partial_grammar_is_never_clean(
    tmp_path: Path, mutation, expected_reason: str
) -> None:
    snapshot_path, manifest_path, snapshot, manifest = _snapshot_pair(tmp_path)
    mutation(snapshot, manifest)
    _rewrite_pair(snapshot_path, manifest_path, snapshot, manifest)
    state = screening.snapshot_state(snapshot_path, manifest_path)
    assert state.status == "degraded"
    assert state.reason_code == expected_reason


@pytest.mark.parametrize(
    "injected_value",
    ["grammar_profile", "normalizer_profile", "schema_version"],
)
def test_invalid_rule_text_cannot_inject_profile_failure_reason(
    tmp_path: Path, injected_value: str
) -> None:
    snapshot_path, manifest_path, snapshot, manifest = _snapshot_pair(tmp_path)
    snapshot["rules"][0]["expression"] = {
        "op": "regex",
        "value": injected_value,
    }
    _rewrite_pair(snapshot_path, manifest_path, snapshot, manifest)
    state = screening.snapshot_state(snapshot_path, manifest_path)
    assert state.status == "degraded"
    assert state.reason_code == "SNAPSHOT_RULES_UNSUPPORTED"


def test_semantically_duplicate_rule_is_rejected(tmp_path: Path) -> None:
    snapshot_path, manifest_path, snapshot, manifest = _snapshot_pair(tmp_path)
    duplicate = copy.deepcopy(snapshot["rules"][0])
    duplicate["rule_id"] = "different_id_same_semantics"
    snapshot["rules"].append(duplicate)
    _rewrite_pair(snapshot_path, manifest_path, snapshot, manifest)
    state = screening.snapshot_state(snapshot_path, manifest_path)
    assert state.reason_code == "SNAPSHOT_RULES_UNSUPPORTED"


def test_near_gap_is_intervening_token_count_and_ordered() -> None:
    rule = next(item for item in _bundle().rules if item.rule_id == "syn_near_ordered")
    assert screening.evaluate_rule(rule, screening.tokenize("nebula x cabbage"))
    assert not screening.evaluate_rule(rule, screening.tokenize("nebula x y cabbage"))
    assert not screening.evaluate_rule(rule, screening.tokenize("cabbage x nebula"))


def test_near_never_crosses_context_segments() -> None:
    report = screening.build_own_draft_report(
        "nebula `x` cabbage",
        artifact_id="segments.md",
        artifact_format="markdown",
        state=_state(),
        checked_at=CHECKED_AT,
        recorded_at=RECORDED_AT,
    )
    assert all(item["pattern_id"] != "syn_near_ordered" for item in report["matches"])


def test_explicit_timestamps_only_no_ambient_clock_source() -> None:
    source = (SCRIPTS / "tortured_phrase_screening.py").read_text(encoding="utf-8")
    assert ".now(" not in source
    with pytest.raises(screening.ScreeningError, match="explicit RFC 3339"):
        screening.build_own_draft_report(
            "luminous turnip",
            artifact_id="draft.md",
            artifact_format="markdown",
            state=_state(),
            checked_at="today",
            recorded_at=RECORDED_AT,
        )


def test_recorded_at_cannot_precede_checked_at() -> None:
    with pytest.raises(screening.ScreeningError, match="must not precede"):
        screening.build_own_draft_report(
            "luminous turnip",
            artifact_id="draft.md",
            artifact_format="markdown",
            state=_state(),
            checked_at="2026-08-10T01:00:01Z",
            recorded_at="2026-08-10T01:00:00Z",
        )
    entry = _passport()["literature_corpus"][0]
    with pytest.raises(screening.ScreeningError, match="must not precede"):
        screening.build_cited_signal(
            entry,
            surface="cited_title",
            state=_state(),
            checked_at="2026-08-10T01:00:01Z",
            recorded_at="2026-08-10T01:00:00Z",
        )


def test_submicrosecond_timestamp_order_cannot_be_truncated() -> None:
    checked_at = "2026-08-10T01:00:00.0000009Z"
    recorded_at = "2026-08-10T01:00:00.0000001Z"
    with pytest.raises(screening.ScreeningError, match="explicit RFC 3339"):
        screening.build_own_draft_report(
            "luminous turnip",
            artifact_id="draft.md",
            artifact_format="markdown",
            state=_state(),
            checked_at=checked_at,
            recorded_at=recorded_at,
        )
    with pytest.raises(screening.ScreeningError, match="explicit RFC 3339"):
        screening.build_cited_signal(
            _passport()["literature_corpus"][0],
            surface="cited_title",
            state=_state(),
            checked_at=checked_at,
            recorded_at=recorded_at,
        )


def test_renderer_is_one_page_bounded_and_has_claim_ceiling() -> None:
    report = _report()
    rendered = screening.render_own_draft_report(
        report, _draft("own_draft.md"), state=_state()
    )
    assert screening.SUMMARY_LABEL in rendered
    assert "does not establish papermill, AI, or author origin" in rendered
    assert "not a clean-text certificate" in rendered
    assert "one fixed page capped at 25" in rendered
    assert "--all" not in rendered


def test_renderer_reports_omitted_count_and_machine_replay_key() -> None:
    text = " ".join(["luminous turnip"] * 30)
    report = screening.build_own_draft_report(
        text,
        artifact_id="many-matches.md",
        artifact_format="markdown",
        state=_state(),
        checked_at=CHECKED_AT,
        recorded_at=RECORDED_AT,
    )
    assert len(report["matches"]) > screening.MAX_RENDER_PAGE_SIZE
    rendered = screening.render_own_draft_report(report, text, state=_state())
    omitted = len(report["matches"]) - screening.MAX_RENDER_PAGE_SIZE
    assert f"omitted {omitted}" in rendered
    assert "Complete machine JSON replay key" in rendered
    assert "artifact_id=many-matches.md" in rendered
    assert report["report_sha256"] in rendered


def test_renderer_uses_outcome_specific_zero_and_unresolved_wording() -> None:
    zero = screening.build_own_draft_report(
        "ordinary unmatched prose",
        artifact_id="zero.md",
        artifact_format="markdown",
        state=_state(),
        checked_at=CHECKED_AT,
        recorded_at=RECORDED_AT,
    )
    rendered_zero = screening.render_own_draft_report(
        zero, "ordinary unmatched prose", state=_state()
    )
    assert screening.SUMMARY_LABEL not in rendered_zero
    assert "No phrase-list match observed on the checked surface" in rendered_zero
    assert "not a clean-text certificate" in rendered_zero

    unresolved_state = screening.snapshot_state(None, None)
    unresolved = screening.build_own_draft_report(
        "ordinary unmatched prose",
        artifact_id="unresolved.md",
        artifact_format="markdown",
        state=unresolved_state,
        checked_at=CHECKED_AT,
        recorded_at=RECORDED_AT,
    )
    rendered_unresolved = screening.render_own_draft_report(
        unresolved, "ordinary unmatched prose", state=unresolved_state
    )
    assert screening.SUMMARY_LABEL not in rendered_unresolved
    assert "screening is unresolved" in rendered_unresolved


def test_renderer_escapes_markdown_and_html_injection() -> None:
    assert "<img" not in screening._markdown_cell("<img src=x>")
    assert "\\[click\\]" in screening._markdown_cell("[click](https://example.invalid)")


def test_corpus_rows_are_per_surface_and_missing_abstract_is_explicit() -> None:
    output = _enriched()
    by_key = {item["citation_key"]: item for item in output["literature_corpus"]}
    complete = by_key["fixture_complete_2026"]["bibliographic_integrity_signals"]
    assert {item["tortured_phrase_context"]["surface"] for item in complete} == {
        "cited_title",
        "cited_abstract",
    }
    missing = by_key["fixture_missing_2026"]["bibliographic_integrity_signals"]
    abstract = next(
        item for item in missing if item["tortured_phrase_context"]["surface"] == "cited_abstract"
    )
    title = next(
        item for item in missing if item["tortured_phrase_context"]["surface"] == "cited_title"
    )
    assert title["finding"] == "detected"
    assert abstract["check_status"] == "not_checked"
    assert abstract["finding"] == "unresolved"
    assert abstract["tortured_phrase_context"]["reason_code"] == "ABSTRACT_MISSING"
    assert abstract["tortured_phrase_context"]["counts"]["rules_evaluated"] == 0


def test_whitespace_abstract_is_explicitly_empty_not_checked() -> None:
    document = _passport()
    document["literature_corpus"][0]["abstract"] = " \t\n"
    output = screening.enrich_passport(
        document,
        state=_state(),
        checked_at=CHECKED_AT,
        recorded_at=RECORDED_AT,
    )
    abstract = next(
        item
        for item in output["literature_corpus"][0]["bibliographic_integrity_signals"]
        if item["tortured_phrase_context"]["surface"] == "cited_abstract"
    )
    assert abstract["check_status"] == "not_checked"
    assert abstract["finding"] == "unresolved"
    assert abstract["tortured_phrase_context"]["reason_code"] == "ABSTRACT_EMPTY"
    assert abstract["tortured_phrase_context"]["surface_binding"] == {
        "content_sha256": None,
        "content_utf8_bytes": None,
    }
    assert abstract["tortured_phrase_context"]["counts"]["rules_evaluated"] == 0


def test_legitimate_negative_only_means_no_configured_match() -> None:
    output = _enriched()
    entry = next(
        item for item in output["literature_corpus"] if item["citation_key"] == "fixture_negative_2026"
    )
    assert all(
        signal["finding"] == "not_detected"
        for signal in entry["bibliographic_integrity_signals"]
    )
    assert all(
        signal["tortured_phrase_context"]["boundary"]["absence_is_clean_certificate"]
        is False
        for signal in entry["bibliographic_integrity_signals"]
    )


def test_manual_entries_are_not_exempt_and_pointer_is_not_dereferenced() -> None:
    output = _enriched()
    entry = output["literature_corpus"][0]
    assert entry["obtained_via"] == "manual"
    assert entry["source_pointer"].startswith("fixture://")
    assert len(entry["bibliographic_integrity_signals"]) == 2


def test_enrichment_is_semantically_idempotent_and_supersedes_current_row() -> None:
    first = _enriched()
    second = screening.enrich_passport(
        first,
        state=_state(),
        checked_at=CHECKED_AT,
        recorded_at=RECORDED_AT,
    )
    assert second == first
    first["literature_corpus"][0]["title"] += " changed"
    third = screening.enrich_passport(
        first,
        state=_state(),
        checked_at=CHECKED_AT,
        recorded_at=RECORDED_AT,
    )
    signals = third["literature_corpus"][0]["bibliographic_integrity_signals"]
    assert len([item for item in signals if item["schema_version"] == screening.SIGNAL_VERSION]) == 2


def test_enrichment_rejects_foreign_current_row_before_supersession() -> None:
    document = _enriched()
    row = document["literature_corpus"][0]["bibliographic_integrity_signals"][0]
    row["subject"]["source_pointer"] = "fixture://foreign-source"
    with pytest.raises(screening.ScreeningError, match="source_pointer does not belong"):
        screening.enrich_passport(
            document,
            state=_state(),
            checked_at=CHECKED_AT,
            recorded_at=RECORDED_AT,
        )


def test_legacy_and_unrelated_signals_are_preserved() -> None:
    document = _passport()
    legacy = json.loads(
        (SCRIPTS / "fixtures/bibliographic_integrity_signals/tortured_phrase.json").read_text(
            encoding="utf-8"
        )
    )
    legacy["subject"]["citation_key"] = document["literature_corpus"][0]["citation_key"]
    legacy["subject"]["source_pointer"] = document["literature_corpus"][0]["source_pointer"]
    document["literature_corpus"][0]["bibliographic_integrity_signals"] = [legacy]
    output = screening.enrich_passport(
        document,
        state=_state(),
        checked_at=CHECKED_AT,
        recorded_at=RECORDED_AT,
    )
    signals = output["literature_corpus"][0]["bibliographic_integrity_signals"]
    assert signals[0] == legacy
    assert len(signals) == 3


def test_multiple_current_rows_are_rejected() -> None:
    document = _enriched()
    entry = document["literature_corpus"][0]
    duplicate = copy.deepcopy(entry["bibliographic_integrity_signals"][0])
    context = duplicate["tortured_phrase_context"]
    context["snapshot"]["snapshot_sha256"] = "0" * 64
    context["snapshot"]["manifest_sha256"] = "1" * 64
    duplicate["provenance"]["source_sha256"] = "0" * 64
    duplicate["signal_id"] = screening._signal_id(
        entry["citation_key"],
        context["surface"],
        context["snapshot"]["snapshot_sha256"],
        context["surface_binding"]["content_sha256"],
    )
    for match in context["matches"]:
        span = match["source_span"]
        match["match_id"] = "tpm-" + screening._sha256_text(
            screening._canonical_json(
                {
                    "artifact_sha256": context["surface_binding"]["content_sha256"],
                    "snapshot_sha256": context["snapshot"]["snapshot_sha256"],
                    "surface": context["surface"],
                    "segment_id": match["segment_id"],
                    "context": match["context"],
                    "rule_id": match["pattern_id"],
                    "codepoint_start": span["codepoint_start"],
                    "codepoint_end": span["codepoint_end"],
                }
            )
        )[:24]
    entry["bibliographic_integrity_signals"].append(duplicate)
    with pytest.raises(screening.ScreeningError, match="multiple current"):
        screening.enrich_passport(
            document,
            state=_state(),
            checked_at=CHECKED_AT,
            recorded_at=RECORDED_AT,
        )


def test_internally_invalid_current_row_is_not_silently_superseded() -> None:
    document = _enriched()
    row = document["literature_corpus"][0]["bibliographic_integrity_signals"][0]
    row["signal_id"] = row["signal_id"][:-1] + (
        "0" if row["signal_id"][-1] != "0" else "1"
    )
    with pytest.raises(screening.ScreeningError, match="internally inconsistent"):
        screening.enrich_passport(
            document,
            state=_state(),
            checked_at=CHECKED_AT,
            recorded_at=RECORDED_AT,
        )


def test_generated_id_collision_with_preserved_legacy_row_is_rejected() -> None:
    document = _passport()
    generated = screening.build_cited_signal(
        document["literature_corpus"][0],
        surface="cited_title",
        state=_state(),
        checked_at=CHECKED_AT,
        recorded_at=RECORDED_AT,
    )
    legacy = json.loads(
        (SCRIPTS / "fixtures/bibliographic_integrity_signals/tortured_phrase.json").read_text(
            encoding="utf-8"
        )
    )
    legacy["signal_id"] = generated["signal_id"]
    legacy["subject"]["citation_key"] = document["literature_corpus"][0]["citation_key"]
    legacy["subject"]["source_pointer"] = document["literature_corpus"][0]["source_pointer"]
    document["literature_corpus"][0]["bibliographic_integrity_signals"] = [legacy]
    with pytest.raises(screening.ScreeningError, match="collides with preserved"):
        screening.enrich_passport(
            document,
            state=_state(),
            checked_at=CHECKED_AT,
            recorded_at=RECORDED_AT,
        )


@pytest.mark.parametrize(
    "mutation",
    [
        "title",
        "source_pointer",
        "signal_id",
        "span",
        "count",
        "match_id",
        "evidence",
    ],
)
def test_cited_binding_mutations_fail(mutation: str) -> None:
    output = _enriched()
    entry = output["literature_corpus"][0]
    target_surface = "cited_abstract" if mutation == "span" else "cited_title"
    signal = next(
        item
        for item in entry["bibliographic_integrity_signals"]
        if item["tortured_phrase_context"]["surface"] == target_surface
    )
    if mutation == "title":
        entry["title"] += " mutation"
    elif mutation == "source_pointer":
        entry["source_pointer"] += "/mutation"
    elif mutation == "signal_id":
        signal["signal_id"] = signal["signal_id"][:-1] + "0"
    elif mutation == "span":
        signal["tortured_phrase_context"]["matches"][0]["source_span"]["utf8_end"] -= 1
    elif mutation == "count":
        signal["tortured_phrase_context"]["counts"]["rule_match_count"] += 1
    elif mutation == "match_id":
        signal["tortured_phrase_context"]["matches"][0]["match_id"] = "tpm-" + "0" * 24
    else:
        signal["evidence"][0]["observed_value"] = "forged"
    with pytest.raises(screening.ScreeningError):
        screening.validate_cited_signal_binding(signal, entry)


@pytest.mark.parametrize(
    "mutation",
    [
        "missing_abstract_as_checked",
        "checked_with_zero_rules",
        "checked_with_unknown_segment",
        "match_context_crosses_surface",
        "outer_not_checked_with_loaded_snapshot",
        "not_checked_snapshot_keeps_hashes",
        "match_limit_with_not_checked_snapshot",
    ],
)
def test_cited_state_and_surface_laundering_mutations_fail(mutation: str) -> None:
    output = _enriched()
    if mutation == "missing_abstract_as_checked":
        entry = next(
            item
            for item in output["literature_corpus"]
            if item["citation_key"] == "fixture_missing_2026"
        )
        signal = next(
            item
            for item in entry["bibliographic_integrity_signals"]
            if item["tortured_phrase_context"]["surface"] == "cited_abstract"
        )
        signal["check_status"] = "checked"
        signal["finding"] = "not_detected"
        signal["provenance"]["checked_at"] = CHECKED_AT
        signal["evidence"][0]["evidence_type"] = "list_record"
        signal["evidence"][0]["observed_value"] = 0
        signal["tortured_phrase_context"]["reason_code"] = "CHECK_COMPLETED"
    else:
        entry = output["literature_corpus"][0]
        signal = next(
            item
            for item in entry["bibliographic_integrity_signals"]
            if item["tortured_phrase_context"]["surface"] == "cited_title"
        )
        context = signal["tortured_phrase_context"]
        if mutation == "checked_with_zero_rules":
            context["counts"]["rules_evaluated"] = 0
        elif mutation == "checked_with_unknown_segment":
            context["counts"]["unknown_segments"] = 1
        elif mutation == "match_context_crosses_surface":
            match = context["matches"][0]
            match["context"] = "cited_abstract"
            payload = {
                "artifact_sha256": context["surface_binding"]["content_sha256"],
                "snapshot_sha256": context["snapshot"]["snapshot_sha256"],
                "surface": context["surface"],
                "segment_id": match["segment_id"],
                "context": match["context"],
                "rule_id": match["pattern_id"],
                "codepoint_start": match["source_span"]["codepoint_start"],
                "codepoint_end": match["source_span"]["codepoint_end"],
            }
            match["match_id"] = "tpm-" + screening._sha256_text(
                screening._canonical_json(payload)
            )[:24]
            context["counts"]["matches_by_context"]["cited_title"] -= 1
            context["counts"]["matches_by_context"]["cited_abstract"] += 1
        elif mutation in {
            "outer_not_checked_with_loaded_snapshot",
            "not_checked_snapshot_keeps_hashes",
        }:
            signal["check_status"] = "not_checked"
            signal["finding"] = "unresolved"
            signal["provenance"]["checked_at"] = None
            signal["evidence"][0]["evidence_type"] = "degradation_record"
            signal["evidence"][0]["observed_value"] = "SNAPSHOT_NOT_PROVIDED"
            context["reason_code"] = "SNAPSHOT_NOT_PROVIDED"
            context["counts"] = screening._empty_counts()
            context["matches"] = []
            if mutation == "not_checked_snapshot_keeps_hashes":
                context["snapshot"] = screening._snapshot_binding(
                    screening.snapshot_state(None, None)
                )
                context["snapshot"]["snapshot_sha256"] = "0" * 64
                context["snapshot"]["manifest_sha256"] = "1" * 64
                signal["signal_id"] = screening._signal_id(
                    entry["citation_key"],
                    context["surface"],
                    context["snapshot"]["snapshot_sha256"],
                    context["surface_binding"]["content_sha256"],
                )
                signal["provenance"]["source_name"] = (
                    "tortured-phrase snapshot unavailable"
                )
                signal["provenance"]["source_version"] = None
                signal["provenance"]["source_sha256"] = "0" * 64
        else:
            signal["check_status"] = "degraded"
            signal["finding"] = "unresolved"
            signal["evidence"][0]["evidence_type"] = "degradation_record"
            signal["evidence"][0]["observed_value"] = "MATCH_RESOURCE_LIMIT"
            context["reason_code"] = "MATCH_RESOURCE_LIMIT"
            context["counts"] = screening._empty_counts()
            context["matches"] = []
            context["snapshot"] = screening._snapshot_binding(
                screening.snapshot_state(None, None)
            )
            signal["provenance"]["source_name"] = (
                "tortured-phrase snapshot unavailable"
            )
            signal["provenance"]["source_version"] = None
            signal["provenance"]["source_sha256"] = None
    with pytest.raises(screening.ScreeningError):
        screening.validate_cited_signal_binding(signal, entry)


@pytest.mark.parametrize(
    "rights",
    [
        {
            "basis": "user_declared_authorized",
            "redistribution_status": "permitted",
            "reference": None,
            "user_declaration": None,
        },
        {
            "basis": "written_permission",
            "redistribution_status": "permitted",
            "reference": None,
            "user_declaration": None,
        },
        {
            "basis": "unresolved",
            "redistribution_status": "permitted",
            "reference": None,
            "user_declaration": None,
        },
    ],
)
def test_cited_carrier_rejects_impossible_rights_projection(rights: dict) -> None:
    output = _enriched()
    entry = output["literature_corpus"][0]
    signal = entry["bibliographic_integrity_signals"][0]
    signal["tortured_phrase_context"]["snapshot"]["rights"] = rights
    with pytest.raises(screening.ScreeningError):
        screening.validate_cited_signal_binding(signal, entry)


def test_cited_carrier_rejects_missing_loaded_source_locator() -> None:
    output = _enriched()
    entry = output["literature_corpus"][0]
    signal = entry["bibliographic_integrity_signals"][0]
    signal["tortured_phrase_context"]["snapshot"]["source"]["locator"] = None
    with pytest.raises(screening.ScreeningError):
        screening.validate_cited_signal_binding(signal, entry)


def test_tortured_phrase_cannot_be_deterministic_or_terminal() -> None:
    schema = screening._load_schema(screening.SIGNAL_SCHEMA_PATH)
    validator = Draft202012Validator(
        schema, format_checker=Draft202012Validator.FORMAT_CHECKER
    )
    signal = _enriched()["literature_corpus"][0]["bibliographic_integrity_signals"][0]
    assert not list(validator.iter_errors(signal))
    signal["epistemic_class"] = "deterministic_fact"
    signal["epistemic_label"] = "RESOLVER-OR-LIST-OBSERVATION"
    assert list(validator.iter_errors(signal))
    signal = _enriched()["literature_corpus"][0]["bibliographic_integrity_signals"][0]
    signal["terminal_policy"] = {
        "eligible": True,
        "owner": "citation_finalizer",
        "policy_key": "tortured_phrase",
        "current_effect": "policy_gated",
    }
    assert list(validator.iter_errors(signal))


def test_report_never_copies_raw_pattern_bodies() -> None:
    report_bytes = json.dumps(_report(), ensure_ascii=False)
    snapshot = json.loads((FIXTURES / "snapshot.json").read_text(encoding="utf-8"))
    for rule in snapshot["rules"]:
        expression = json.dumps(rule["expression"], ensure_ascii=False, sort_keys=True)
        assert expression not in report_bytes


def test_cli_rejects_in_place_passport_output() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "tortured_phrase_screening.py"),
            "enrich-passport",
            "--input",
            str(FIXTURES / "corpus_input.yaml"),
            "--output",
            str(FIXTURES / "corpus_input.yaml"),
            "--snapshot",
            str(FIXTURES / "snapshot.json"),
            "--snapshot-manifest",
            str(FIXTURES / "snapshot_manifest.json"),
            "--checked-at",
            CHECKED_AT,
            "--recorded-at",
            RECORDED_AT,
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 1
    assert "refuses in-place" in result.stderr


@pytest.mark.parametrize("alias", ["snapshot", "manifest", "snapshot_hardlink"])
def test_scan_output_cannot_alias_any_named_input(
    tmp_path: Path, alias: str
) -> None:
    draft = tmp_path / "draft.md"
    snapshot = tmp_path / "snapshot.json"
    manifest = tmp_path / "manifest.json"
    draft.write_bytes((FIXTURES / "own_draft.md").read_bytes())
    snapshot.write_bytes((FIXTURES / "snapshot.json").read_bytes())
    manifest.write_bytes((FIXTURES / "snapshot_manifest.json").read_bytes())
    if alias == "snapshot":
        output = snapshot
    elif alias == "manifest":
        output = manifest
    else:
        output = tmp_path / "snapshot-hardlink.json"
        output.hardlink_to(snapshot)
    snapshot_before = snapshot.read_bytes()
    manifest_before = manifest.read_bytes()
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "tortured_phrase_screening.py"),
            "scan-draft",
            "--input",
            str(draft),
            "--artifact-id",
            "draft.md",
            "--format",
            "markdown",
            "--snapshot",
            str(snapshot),
            "--snapshot-manifest",
            str(manifest),
            "--checked-at",
            CHECKED_AT,
            "--recorded-at",
            RECORDED_AT,
            "--output",
            str(output),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 1
    assert "named-input alias" in result.stderr
    assert snapshot.read_bytes() == snapshot_before
    assert manifest.read_bytes() == manifest_before


def test_corpus_output_match_cap_rejects_before_write(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setattr(screening, "MAX_CORPUS_OUTPUT_MATCHES", 0)
    with pytest.raises(screening.MatchLimitError, match="corpus output match count"):
        _enriched()


@pytest.mark.parametrize(
    ("limit_name", "document", "message"),
    [
        (
            "MAX_CORPUS_ENTRIES",
            {"literature_corpus": [{}, {}]},
            "more than 1 entries",
        ),
        (
            "MAX_CORPUS_EXISTING_SIGNALS",
            {"literature_corpus": [{"bibliographic_integrity_signals": [{}]}]},
            "exceed 0 rows",
        ),
    ],
)
def test_corpus_cardinality_caps_fail_before_copy_or_row_construction(
    monkeypatch: pytest.MonkeyPatch,
    limit_name: str,
    document: dict,
    message: str,
) -> None:
    monkeypatch.setattr(screening, limit_name, 1 if limit_name.endswith("ENTRIES") else 0)

    def unexpected_copy(_value):
        raise AssertionError("copy must not run after an over-limit input")

    monkeypatch.setattr(screening.copy, "deepcopy", unexpected_copy)
    with pytest.raises(screening.MatchLimitError, match=message):
        screening.enrich_passport(
            document,
            state=screening.snapshot_state(None, None),
            checked_at=CHECKED_AT,
            recorded_at=RECORDED_AT,
        )


def test_deep_json_passport_fails_closed_without_traceback_or_output_mutation(
    tmp_path: Path,
) -> None:
    passport = tmp_path / "deep-passport.json"
    passport.write_text(
        '{"literature_corpus":[],"extension":'
        + "[" * 1000
        + "0"
        + "]" * 1000
        + "}\n",
        encoding="utf-8",
    )
    output = tmp_path / "output.json"
    output.write_bytes(b"sentinel\n")
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "tortured_phrase_screening.py"),
            "enrich-passport",
            "--input",
            str(passport),
            "--output",
            str(output),
            "--checked-at",
            CHECKED_AT,
            "--recorded-at",
            RECORDED_AT,
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 1
    assert "Traceback" not in result.stderr
    assert "strict JSON" in result.stderr or "structure exceeds" in result.stderr
    assert output.read_bytes() == b"sentinel\n"


def test_deep_advisory_report_fails_closed_without_traceback(tmp_path: Path) -> None:
    report = tmp_path / "deep-report.json"
    report.write_text(
        '{"extension":' + "[" * 1000 + "0" + "]" * 1000 + "}\n",
        encoding="utf-8",
    )
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "tortured_phrase_screening.py"),
            "validate-draft",
            "--input",
            str(FIXTURES / "own_draft.md"),
            "--artifact-id",
            "own_draft.md",
            "--format",
            "markdown",
            "--snapshot",
            str(FIXTURES / "snapshot.json"),
            "--snapshot-manifest",
            str(FIXTURES / "snapshot_manifest.json"),
            "--report",
            str(report),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 1
    assert "Traceback" not in result.stderr
    assert "strict JSON" in result.stderr or "structure exceeds" in result.stderr


@pytest.mark.parametrize("cwd", [REPO_ROOT, SCRIPTS])
def test_runtime_imports_in_package_and_direct_script_modes(cwd: Path) -> None:
    module = "scripts.tortured_phrase_screening" if cwd == REPO_ROOT else "tortured_phrase_screening"
    result = subprocess.run(
        [sys.executable, "-c", f"import {module}"],
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr


def test_package_import_cannot_bind_shadow_bibliographic_module(
    tmp_path: Path,
) -> None:
    (tmp_path / "bibliographic_integrity_signals.py").write_text(
        "raise RuntimeError('shadow module imported')\n", encoding="utf-8"
    )
    code = (
        "import sys; "
        f"sys.path.insert(0, {str(tmp_path)!r}); "
        "import scripts.tortured_phrase_screening as module; "
        "print(module._validate_existing_phrase_projection.__module__); "
        "print(module._validate_existing_phrase_projection.__code__.co_filename)"
    )
    result = subprocess.run(
        [sys.executable, "-c", code],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    lines = result.stdout.splitlines()
    assert lines[0] == "scripts.bibliographic_integrity_signals"
    assert Path(lines[1]).resolve() == (
        SCRIPTS / "bibliographic_integrity_signals.py"
    ).resolve()


def test_yaml_aliases_fail_closed_without_output(tmp_path: Path) -> None:
    passport = tmp_path / "aliased.yaml"
    passport.write_text(
        "shared: &rows []\nliterature_corpus: *rows\n",
        encoding="utf-8",
    )
    output = tmp_path / "output.yaml"
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "tortured_phrase_screening.py"),
            "enrich-passport",
            "--input",
            str(passport),
            "--output",
            str(output),
            "--snapshot",
            str(FIXTURES / "snapshot.json"),
            "--snapshot-manifest",
            str(FIXTURES / "snapshot_manifest.json"),
            "--checked-at",
            CHECKED_AT,
            "--recorded-at",
            RECORDED_AT,
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 1
    assert "YAML aliases are forbidden" in result.stderr
    assert not output.exists()


def test_cli_has_no_all_or_page_traversal() -> None:
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "tortured_phrase_screening.py"),
            "render-draft",
            "--help",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 0
    assert "--all" not in result.stdout
    assert "--page" not in result.stdout


def test_invalid_snapshot_cli_writes_degraded_artifact_and_returns_one(tmp_path: Path) -> None:
    bad = tmp_path / "bad.json"
    bad.write_text("{}\n", encoding="utf-8")
    output = tmp_path / "report.json"
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "tortured_phrase_screening.py"),
            "scan-draft",
            "--input",
            str(FIXTURES / "own_draft.md"),
            "--artifact-id",
            "own_draft.md",
            "--format",
            "markdown",
            "--snapshot",
            str(bad),
            "--snapshot-manifest",
            str(FIXTURES / "snapshot_manifest.json"),
            "--checked-at",
            CHECKED_AT,
            "--recorded-at",
            RECORDED_AT,
            "--output",
            str(output),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 1
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["check_status"] == "degraded"
    assert report["finding"] == "unresolved"


@pytest.mark.parametrize(
    ("text", "reason"),
    [
        ("", "DOCUMENT_EMPTY"),
        ("`unclosed luminous turnip", "DOCUMENT_PARSE_DEGRADED"),
    ],
)
def test_loaded_snapshot_scan_returns_one_for_degraded_artifact(
    tmp_path: Path, text: str, reason: str
) -> None:
    draft = tmp_path / "draft.md"
    draft.write_text(text, encoding="utf-8")
    output = tmp_path / "report.json"
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "tortured_phrase_screening.py"),
            "scan-draft",
            "--input",
            str(draft),
            "--artifact-id",
            "draft.md",
            "--format",
            "markdown",
            "--snapshot",
            str(FIXTURES / "snapshot.json"),
            "--snapshot-manifest",
            str(FIXTURES / "snapshot_manifest.json"),
            "--checked-at",
            CHECKED_AT,
            "--recorded-at",
            RECORDED_AT,
            "--output",
            str(output),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 1
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["check_status"] == "degraded"
    assert report["reason_code"] == reason


def test_loaded_snapshot_resource_degradation_returns_one_after_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    draft = tmp_path / "draft.md"
    draft.write_text("alpha\n\nbeta", encoding="utf-8")
    output = tmp_path / "report.json"
    monkeypatch.setattr(screening, "MAX_SEGMENTS", 1)
    result = screening.main(
        [
            "scan-draft",
            "--input",
            str(draft),
            "--artifact-id",
            "draft.md",
            "--format",
            "markdown",
            "--snapshot",
            str(FIXTURES / "snapshot.json"),
            "--snapshot-manifest",
            str(FIXTURES / "snapshot_manifest.json"),
            "--checked-at",
            CHECKED_AT,
            "--recorded-at",
            RECORDED_AT,
            "--output",
            str(output),
        ]
    )
    assert result == 1
    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["check_status"] == "degraded"
    assert report["reason_code"] == "MATCH_RESOURCE_LIMIT"


def test_loaded_snapshot_corpus_degradation_returns_one_after_write(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    passport = tmp_path / "corpus.yaml"
    passport.write_bytes((FIXTURES / "corpus_input.yaml").read_bytes())
    output = tmp_path / "output.yaml"
    monkeypatch.setattr(screening, "MAX_MATCH_WORK_UNITS", 0)
    result = screening.main(
        [
            "enrich-passport",
            "--input",
            str(passport),
            "--output",
            str(output),
            "--snapshot",
            str(FIXTURES / "snapshot.json"),
            "--snapshot-manifest",
            str(FIXTURES / "snapshot_manifest.json"),
            "--checked-at",
            CHECKED_AT,
            "--recorded-at",
            RECORDED_AT,
        ]
    )
    assert result == 1
    enriched, _kind = screening._load_passport(output)
    assert any(
        signal.get("check_status") == "degraded"
        for entry in enriched["literature_corpus"]
        for signal in entry["bibliographic_integrity_signals"]
        if signal.get("schema_version") == screening.SIGNAL_VERSION
    )


def test_explicit_not_checked_scan_remains_successful(tmp_path: Path) -> None:
    output = tmp_path / "report.json"
    result = screening.main(
        [
            "scan-draft",
            "--input",
            str(FIXTURES / "own_draft.md"),
            "--artifact-id",
            "own_draft.md",
            "--format",
            "markdown",
            "--checked-at",
            CHECKED_AT,
            "--recorded-at",
            RECORDED_AT,
            "--output",
            str(output),
        ]
    )
    assert result == 0
    assert json.loads(output.read_text(encoding="utf-8"))["check_status"] == (
        "not_checked"
    )


def test_failed_scan_does_not_overwrite_input_or_partial_output(tmp_path: Path) -> None:
    draft = tmp_path / "draft.md"
    draft.write_text("luminous turnip", encoding="utf-8")
    before = draft.read_bytes()
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPTS / "tortured_phrase_screening.py"),
            "scan-draft",
            "--input",
            str(draft),
            "--artifact-id",
            "draft.md",
            "--format",
            "markdown",
            "--checked-at",
            "bad-time",
            "--recorded-at",
            RECORDED_AT,
            "--output",
            str(tmp_path / "report.json"),
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    assert result.returncode == 1
    assert draft.read_bytes() == before
    assert not (tmp_path / "report.json").exists()
