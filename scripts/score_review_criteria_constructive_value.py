#!/usr/bin/env python3
"""Reduce a completed #684 paired expert-adjudication record.

This stdlib-only scorer reads one explicit local file.  It performs no subject
or judge dispatch, network/API/model call, clock read, directory scan, or
editorial decision.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import sys
import tempfile
from pathlib import Path
from typing import Any, NoReturn


MAX_BYTES = 8 * 1024 * 1024
SHA = set("0123456789abcdef")
ARMS = ("baseline", "treatment")
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
CRITERION_ID_RE = re.compile(r"^[a-z0-9][a-z0-9._-]*$")


class ScoreError(ValueError):
    """Raised for a malformed or incomparable adjudication record."""


def _fail(path: str, message: str) -> NoReturn:
    raise ScoreError(f"{path}: {message}")


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ScoreError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _constant(value: str) -> NoReturn:
    raise ScoreError(f"non-finite JSON number: {value}")


def _open_nofollow(path: Path) -> int:
    directory_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    parts = path.parts
    if path.is_absolute():
        directory_fd = os.open(os.sep, directory_flags)
        components = parts[1:]
    else:
        directory_fd = os.open(".", directory_flags)
        components = parts
    if not components:
        os.close(directory_fd)
        raise ScoreError(f"explicit input must name a file: {path}")
    try:
        for component in components[:-1]:
            next_fd = os.open(
                component,
                directory_flags | nofollow,
                dir_fd=directory_fd,
            )
            os.close(directory_fd)
            directory_fd = next_fd
        return os.open(
            components[-1], os.O_RDONLY | nofollow, dir_fd=directory_fd
        )
    except OSError as exc:
        raise ScoreError(
            f"cannot traverse explicit input without symlinks {path}: {exc}"
        ) from exc
    finally:
        os.close(directory_fd)


def _read(path: Path) -> tuple[dict[str, Any], bytes]:
    fd = _open_nofollow(path)
    try:
        before = os.fstat(fd)
        if not stat.S_ISREG(before.st_mode) or before.st_size > MAX_BYTES:
            raise ScoreError("input must be a regular file within the byte cap")
        chunks: list[bytes] = []
        total = 0
        while True:
            chunk = os.read(fd, min(65536, MAX_BYTES + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > MAX_BYTES:
                raise ScoreError("input exceeds byte cap")
        after = os.fstat(fd)
        if (before.st_dev, before.st_ino, before.st_size, before.st_mtime_ns, before.st_ctime_ns) != (
            after.st_dev,
            after.st_ino,
            after.st_size,
            after.st_mtime_ns,
            after.st_ctime_ns,
        ):
            raise ScoreError("input changed while being read")
        raw = b"".join(chunks)
        if len(raw) != after.st_size:
            raise ScoreError("short read")
    finally:
        os.close(fd)
    try:
        value = json.loads(
            raw.decode("utf-8"),
            object_pairs_hook=_pairs,
            parse_constant=_constant,
        )
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ScoreError(f"strict JSON parse failed: {exc}") from exc
    if not isinstance(value, dict):
        raise ScoreError("top-level value must be an object")
    return value, raw


def _object(value: Any, path: str, keys: set[str]) -> dict[str, Any]:
    if not isinstance(value, dict):
        _fail(path, "must be an object")
    if set(value) != keys:
        _fail(path, f"closed fields mismatch: {sorted(set(value) ^ keys)}")
    return value


def _text(value: Any, path: str) -> str:
    if not isinstance(value, str) or not value:
        _fail(path, "must be a non-empty string")
    try:
        value.encode("utf-8")
    except UnicodeEncodeError as exc:
        _fail(path, f"must be valid Unicode: {exc}")
    return value


def _sha(value: Any, path: str) -> str:
    text = _text(value, path)
    if len(text) != 64 or any(char not in SHA for char in text):
        _fail(path, "must be lowercase SHA-256")
    return text


def _id(value: Any, path: str) -> str:
    text = _text(value, path)
    if ID_RE.fullmatch(text) is None:
        _fail(path, "must be a 1..128-character ASCII identifier")
    return text


def _criterion_id(value: Any, path: str) -> str:
    text = _text(value, path)
    if CRITERION_ID_RE.fullmatch(text) is None:
        _fail(path, "must be a canonical criterion id")
    return text


def _portable_ref(value: Any, path: str) -> str:
    text = _text(value, path)
    if (
        len(text) > 512
        or text.startswith("/")
        or "\\" in text
        or any(part in ("", ".", "..") for part in text.split("/"))
    ):
        _fail(path, "must be a portable relative POSIX reference")
    return text


def _array(value: Any, path: str, *, minimum: int = 0) -> list[Any]:
    if not isinstance(value, list) or len(value) < minimum:
        _fail(path, f"must be an array with at least {minimum} item(s)")
    return value


def _unique_texts(value: Any, path: str, *, minimum: int = 0) -> list[str]:
    rows = [_text(item, f"{path}[{index}]") for index, item in enumerate(_array(value, path, minimum=minimum))]
    if len(set(rows)) != len(rows):
        _fail(path, "must contain unique strings")
    return rows


def _enum(value: Any, path: str, allowed: set[str]) -> str:
    text = _text(value, path)
    if text not in allowed:
        _fail(path, f"must be one of {sorted(allowed)}")
    return text


def _integer(value: Any, path: str, minimum: int, maximum: int | None = None) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        _fail(path, f"must be an integer >= {minimum}")
    if maximum is not None and value > maximum:
        _fail(path, f"must be an integer <= {maximum}")
    return value


def _canonical(value: Any) -> bytes:
    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ).encode("utf-8")
    except (TypeError, ValueError, UnicodeEncodeError) as exc:
        raise ScoreError(f"value is not canonical JSON: {exc}") from exc


def _context(value: Any, path: str) -> dict[str, Any]:
    obj = _object(
        value,
        path,
        {"context_ref", "context_sha256", "resolved_digest", "selected_criterion_ids"},
    )
    _portable_ref(obj["context_ref"], f"{path}.context_ref")
    _sha(obj["context_sha256"], f"{path}.context_sha256")
    _sha(obj["resolved_digest"], f"{path}.resolved_digest")
    ids = _unique_texts(
        obj["selected_criterion_ids"],
        f"{path}.selected_criterion_ids",
        minimum=1,
    )
    for index, criterion_id in enumerate(ids):
        _criterion_id(criterion_id, f"{path}.selected_criterion_ids[{index}]")
    return obj


def _budget(value: Any, path: str) -> dict[str, Any]:
    obj = _object(
        value,
        path,
        {"model_id", "model_family", "tools", "sampling", "input_token_cap", "output_token_cap"},
    )
    _text(obj["model_id"], f"{path}.model_id")
    _text(obj["model_family"], f"{path}.model_family")
    _unique_texts(obj["tools"], f"{path}.tools")
    _text(obj["sampling"], f"{path}.sampling")
    _integer(obj["input_token_cap"], f"{path}.input_token_cap", 1)
    _integer(obj["output_token_cap"], f"{path}.output_token_cap", 1)
    return obj


def _blank_counts() -> dict[str, Any]:
    return {
        "profile": [0, 0],
        "applicability": [0, 0],
        "unsupported": [0, 0, 0],
        "severity": [0, 0],
        "venue": [0, 0],
        "usefulness": [0, 0, {str(i): 0 for i in range(1, 6)}],
        "agreement": {
            metric: [0, 0]
            for metric in ("applicability", "support", "severity", "venue", "usefulness")
        },
    }


def _require_expert_ids(value: Any, path: str, expert_ids: list[str],
                        keys: set[str]) -> list[dict[str, Any]]:
    rows = _array(value, path)
    if len(rows) != len(expert_ids):
        _fail(path, "must contain exactly one row for every declared expert")
    result: list[dict[str, Any]] = []
    actual_ids: list[str] = []
    for index, row in enumerate(rows):
        row_path = f"{path}[{index}]"
        obj = _object(row, row_path, {"expert_id", *keys})
        actual_ids.append(_id(obj["expert_id"], f"{row_path}.expert_id"))
        result.append(obj)
    if actual_ids != expert_ids:
        _fail(path, "must cover declared expert ids exactly in declaration order")
    return result


def _require_unanimous_consistency(values: list[Any], adjudicated: Any,
                                   path: str) -> None:
    if len(set(values)) == 1 and adjudicated != values[0]:
        _fail(path, "cannot overturn a unanimous expert label")


def _validate_and_count(record: dict[str, Any]) -> dict[str, dict[str, Any]]:
    _object(record, "$", {"schema_version", "suite", "subject", "experts", "adjudication", "items"})
    if record["schema_version"] != "review-criteria-paired-adjudication/1.0":
        _fail("$.schema_version", "unsupported version")
    if record["suite"] != "review_criteria_constructive_value":
        _fail("$.suite", "wrong suite")

    subject = _object(
        record["subject"],
        "$.subject",
        {"suite_commit", "model_id", "model_family", "tools", "sampling", "input_token_cap", "output_token_cap", "replicates_per_item"},
    )
    commit = _text(subject["suite_commit"], "$.subject.suite_commit")
    if len(commit) != 40 or any(char not in SHA for char in commit):
        _fail("$.subject.suite_commit", "must be 40 lowercase hex")
    subject_budget = _budget(
        {key: subject[key] for key in ("model_id", "model_family", "tools", "sampling", "input_token_cap", "output_token_cap")},
        "$.subject",
    )
    replicate_count = _integer(subject["replicates_per_item"], "$.subject.replicates_per_item", 2)

    experts = _array(record["experts"], "$.experts", minimum=2)
    expert_ids: list[str] = []
    for index, row in enumerate(experts):
        path = f"$.experts[{index}]"
        obj = _object(
            row,
            path,
            {"expert_id", "expert_type", "expertise", "independent", "blinded_to"},
        )
        expert_ids.append(_id(obj["expert_id"], f"{path}.expert_id"))
        if obj["expert_type"] != "human":
            _fail(f"{path}.expert_type", "must be human")
        _text(obj["expertise"], f"{path}.expertise")
        if obj["independent"] is not True:
            _fail(f"{path}.independent", "must be true")
        blinded = set(_unique_texts(obj["blinded_to"], f"{path}.blinded_to", minimum=1))
        required_blinding = {
            "arm_identity",
            "mechanism_state",
            "other_experts",
            "raw_aggregate",
            "expected_direction",
        }
        if blinded != required_blinding:
            _fail(f"{path}.blinded_to", "must contain the exact five blind dimensions")
    if len(set(expert_ids)) != len(expert_ids):
        _fail("$.experts", "duplicate expert_id")

    adjudication = _object(
        record["adjudication"],
        "$.adjudication",
        {
            "adjudicator_id",
            "adjudicator_type",
            "method",
            "arm_blind",
            "disagreements_retained",
        },
    )
    _id(adjudication["adjudicator_id"], "$.adjudication.adjudicator_id")
    if adjudication["adjudicator_type"] != "human":
        _fail("$.adjudication.adjudicator_type", "must be human")
    _text(adjudication["method"], "$.adjudication.method")
    if adjudication["arm_blind"] is not True or adjudication["disagreements_retained"] is not True:
        _fail("$.adjudication", "arm_blind and disagreements_retained must be true")

    counts = {arm: _blank_counts() for arm in ARMS}
    item_ids: list[str] = []
    for item_index, row in enumerate(_array(record["items"], "$.items", minimum=1)):
        path = f"$.items[{item_index}]"
        item = _object(row, path, {"item_id", "target_context", "arms"})
        item_ids.append(_id(item["item_id"], f"{path}.item_id"))
        authority = _context(item["target_context"], f"{path}.target_context")
        selected = authority["selected_criterion_ids"]
        arms = _array(item["arms"], f"{path}.arms", minimum=2)
        if len(arms) != 2:
            _fail(f"{path}.arms", "must contain exactly baseline and treatment")
        arm_map: dict[str, dict[str, Any]] = {}
        for arm_index, arm_value in enumerate(arms):
            arm_path = f"{path}.arms[{arm_index}]"
            arm = _object(arm_value, arm_path, {"arm_id", "mechanism", "target_context", "budget", "replicates"})
            arm_id = _enum(arm["arm_id"], f"{arm_path}.arm_id", set(ARMS))
            if arm_id in arm_map:
                _fail(f"{path}.arms", f"duplicate arm {arm_id}")
            expected_mechanism = "pre_684" if arm_id == "baseline" else "criteria_binding_v1"
            if arm["mechanism"] != expected_mechanism:
                _fail(f"{arm_path}.mechanism", f"must be {expected_mechanism}")
            if _canonical(_context(arm["target_context"], f"{arm_path}.target_context")) != _canonical(authority):
                _fail(f"{arm_path}.target_context", "must equal the sealed item context")
            budget = _budget(arm["budget"], f"{arm_path}.budget")
            if _canonical(budget) != _canonical(subject_budget):
                _fail(f"{arm_path}.budget", "must equal the frozen subject budget")
            arm_map[arm_id] = arm
        if set(arm_map) != set(ARMS):
            _fail(f"{path}.arms", "must contain baseline and treatment")
        if _canonical(arm_map["baseline"]["budget"]) != _canonical(arm_map["treatment"]["budget"]):
            _fail(f"{path}.arms", "baseline and treatment budgets differ")

        for arm_id in ARMS:
            replicates = _array(arm_map[arm_id]["replicates"], f"{path}.{arm_id}.replicates", minimum=2)
            if len(replicates) != replicate_count:
                _fail(f"{path}.{arm_id}.replicates", "must equal subject.replicates_per_item")
            replicate_ids: list[str] = []
            for rep_index, rep_value in enumerate(replicates):
                rep_path = f"{path}.{arm_id}.replicates[{rep_index}]"
                rep = _object(rep_value, rep_path, {"replicate_id", "profile", "applicability", "findings"})
                replicate_ids.append(_id(rep["replicate_id"], f"{rep_path}.replicate_id"))
                profile = _object(rep["profile"], f"{rep_path}.profile", {"resolved_digest", "selected_criterion_ids"})
                _sha(profile["resolved_digest"], f"{rep_path}.profile.resolved_digest")
                _unique_texts(profile["selected_criterion_ids"], f"{rep_path}.profile.selected_criterion_ids", minimum=1)
                counts[arm_id]["profile"][1] += 1
                if profile["resolved_digest"] == authority["resolved_digest"] and profile["selected_criterion_ids"] == selected:
                    counts[arm_id]["profile"][0] += 1

                applications = _array(rep["applicability"], f"{rep_path}.applicability")
                app_ids: list[str] = []
                for app_index, app_value in enumerate(applications):
                    app_path = f"{rep_path}.applicability[{app_index}]"
                    app = _object(
                        app_value,
                        app_path,
                        {"criterion_id", "predicted", "expert_labels", "expert_label"},
                    )
                    app_ids.append(_criterion_id(app["criterion_id"], f"{app_path}.criterion_id"))
                    predicted = _enum(app["predicted"], f"{app_path}.predicted", {"applicable", "not_applicable", "unresolved"})
                    label = _enum(app["expert_label"], f"{app_path}.expert_label", {"applicable", "not_applicable", "unresolved"})
                    raw_labels = _require_expert_ids(
                        app["expert_labels"],
                        f"{app_path}.expert_labels",
                        expert_ids,
                        {"label"},
                    )
                    raw_applicability = [
                        _enum(
                            expert["label"],
                            f"{app_path}.expert_labels[{expert_index}].label",
                            {"applicable", "not_applicable", "unresolved"},
                        )
                        for expert_index, expert in enumerate(raw_labels)
                    ]
                    _require_unanimous_consistency(
                        raw_applicability, label, f"{app_path}.expert_label"
                    )
                    counts[arm_id]["agreement"]["applicability"][1] += 1
                    if len(set(raw_applicability)) == 1:
                        counts[arm_id]["agreement"]["applicability"][0] += 1
                    counts[arm_id]["applicability"][1] += 1
                    if predicted == label:
                        counts[arm_id]["applicability"][0] += 1
                if app_ids != selected:
                    _fail(f"{rep_path}.applicability", "must cover selected criterion ids in authority order")

                finding_ids: list[str] = []
                for finding_index, finding_value in enumerate(_array(rep["findings"], f"{rep_path}.findings")):
                    finding_path = f"{rep_path}.findings[{finding_index}]"
                    finding = _object(
                        finding_value,
                        finding_path,
                        {"finding_id", "expert_labels", "support_label", "predicted_severity", "expert_severity", "predicted_venue_alignment", "expert_venue_alignment", "usefulness"},
                    )
                    finding_ids.append(_id(finding["finding_id"], f"{finding_path}.finding_id"))
                    support = _enum(finding["support_label"], f"{finding_path}.support_label", {"supported", "unsupported", "unresolved"})
                    predicted_severity = _enum(finding["predicted_severity"], f"{finding_path}.predicted_severity", {"critical", "major", "minor", "none"})
                    expert_severity = _enum(finding["expert_severity"], f"{finding_path}.expert_severity", {"critical", "major", "minor", "none", "unresolved"})
                    predicted_venue = _enum(finding["predicted_venue_alignment"], f"{finding_path}.predicted_venue_alignment", {"aligned", "not_aligned", "not_claimed"})
                    expert_venue = _enum(finding["expert_venue_alignment"], f"{finding_path}.expert_venue_alignment", {"aligned", "not_aligned", "not_claimed", "unresolved"})
                    usefulness = _integer(finding["usefulness"], f"{finding_path}.usefulness", 1, 5)
                    raw_labels = _require_expert_ids(
                        finding["expert_labels"],
                        f"{finding_path}.expert_labels",
                        expert_ids,
                        {"support_label", "severity", "venue_alignment", "usefulness"},
                    )
                    raw_support: list[str] = []
                    raw_severity: list[str] = []
                    raw_venue: list[str] = []
                    raw_usefulness: list[int] = []
                    for expert_index, expert in enumerate(raw_labels):
                        raw_path = f"{finding_path}.expert_labels[{expert_index}]"
                        raw_support.append(_enum(expert["support_label"], f"{raw_path}.support_label", {"supported", "unsupported", "unresolved"}))
                        raw_severity.append(_enum(expert["severity"], f"{raw_path}.severity", {"critical", "major", "minor", "none", "unresolved"}))
                        raw_venue.append(_enum(expert["venue_alignment"], f"{raw_path}.venue_alignment", {"aligned", "not_aligned", "not_claimed", "unresolved"}))
                        raw_usefulness.append(_integer(expert["usefulness"], f"{raw_path}.usefulness", 1, 5))
                    _require_unanimous_consistency(raw_support, support, f"{finding_path}.support_label")
                    _require_unanimous_consistency(raw_severity, expert_severity, f"{finding_path}.expert_severity")
                    _require_unanimous_consistency(raw_venue, expert_venue, f"{finding_path}.expert_venue_alignment")
                    _require_unanimous_consistency(raw_usefulness, usefulness, f"{finding_path}.usefulness")
                    for metric, values in (
                        ("support", raw_support),
                        ("severity", raw_severity),
                        ("venue", raw_venue),
                        ("usefulness", raw_usefulness),
                    ):
                        counts[arm_id]["agreement"][metric][1] += 1
                        if len(set(values)) == 1:
                            counts[arm_id]["agreement"][metric][0] += 1
                    if support == "unresolved":
                        counts[arm_id]["unsupported"][2] += 1
                    else:
                        counts[arm_id]["unsupported"][1] += 1
                        if support == "unsupported":
                            counts[arm_id]["unsupported"][0] += 1
                    if support == "supported" and expert_severity in {"critical", "major"}:
                        counts[arm_id]["severity"][1] += 1
                        if predicted_severity == expert_severity:
                            counts[arm_id]["severity"][0] += 1
                    if expert_venue != "unresolved":
                        counts[arm_id]["venue"][1] += 1
                        if predicted_venue == expert_venue:
                            counts[arm_id]["venue"][0] += 1
                    counts[arm_id]["usefulness"][0] += usefulness
                    counts[arm_id]["usefulness"][1] += 1
                    counts[arm_id]["usefulness"][2][str(usefulness)] += 1
                if len(set(finding_ids)) != len(finding_ids):
                    _fail(f"{rep_path}.findings", "duplicate finding_id")
            if len(set(replicate_ids)) != len(replicate_ids):
                _fail(f"{path}.{arm_id}.replicates", "duplicate replicate_id")
    if len(set(item_ids)) != len(item_ids):
        _fail("$.items", "duplicate item_id")
    return counts


def _rate(numerator: int, denominator: int) -> dict[str, Any]:
    return {
        "numerator": numerator,
        "denominator": denominator,
        "rate": None if denominator == 0 else numerator / denominator,
    }


def _render_arm(counts: dict[str, Any]) -> dict[str, Any]:
    usefulness_total, usefulness_n, distribution = counts["usefulness"]
    return {
        "profile_resolution_rate": _rate(*counts["profile"]),
        "applicability_accuracy": _rate(*counts["applicability"]),
        "unsupported_finding_rate": {
            **_rate(counts["unsupported"][0], counts["unsupported"][1]),
            "unresolved_excluded": counts["unsupported"][2],
        },
        "severity_agreement_rate": _rate(*counts["severity"]),
        "venue_alignment_accuracy": _rate(*counts["venue"]),
        "mean_usefulness": {
            "sum": usefulness_total,
            "denominator": usefulness_n,
            "mean": None if usefulness_n == 0 else usefulness_total / usefulness_n,
            "distribution": distribution,
        },
        "raw_expert_unanimity": {
            metric: _rate(*value)
            for metric, value in counts["agreement"].items()
        },
    }


def score(record: dict[str, Any], raw: bytes) -> dict[str, Any]:
    counts = _validate_and_count(record)
    per_arm = {arm: _render_arm(counts[arm]) for arm in ARMS}
    metric_paths = {
        "profile_resolution_rate": "rate",
        "applicability_accuracy": "rate",
        "unsupported_finding_rate": "rate",
        "severity_agreement_rate": "rate",
        "venue_alignment_accuracy": "rate",
        "mean_usefulness": "mean",
    }
    deltas: dict[str, float | None] = {}
    for metric, leaf in metric_paths.items():
        baseline = per_arm["baseline"][metric][leaf]
        treatment = per_arm["treatment"][metric][leaf]
        deltas[f"{metric}_treatment_minus_baseline"] = (
            None if baseline is None or treatment is None else treatment - baseline
        )
    return {
        "schema_version": "review-criteria-constructive-value-score/1.0",
        "suite": "review_criteria_constructive_value",
        "source_sha256": hashlib.sha256(raw).hexdigest(),
        "suite_commit": record["subject"]["suite_commit"],
        "per_arm": per_arm,
        "deltas": deltas,
        "composite_score": None,
        "claim_status": "paired_expert_adjudication_scored",
    }


def _write(path: Path, raw: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        view = memoryview(raw)
        while view:
            written = os.write(fd, view)
            if written <= 0:
                raise ScoreError("zero-progress output write")
            view = view[written:]
        os.fsync(fd)
        os.close(fd)
        fd = -1
        os.replace(temp_name, path)
    finally:
        if fd >= 0:
            os.close(fd)
        try:
            os.unlink(temp_name)
        except FileNotFoundError:
            pass


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--adjudication", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        record, raw = _read(args.adjudication)
        rendered = _canonical(score(record, raw)) + b"\n"
        if args.output is None:
            sys.stdout.buffer.write(rendered)
        else:
            _write(args.output, rendered)
    except ScoreError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
