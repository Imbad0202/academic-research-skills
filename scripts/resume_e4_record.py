#!/usr/bin/env python3
"""Re-emit an E4 record from a preserved post-dispatch evidence bundle.

This is recovery after record emission failed. It never constructs a model
transport, continues an interrupted panel, retries a call, or accepts closed
status fields from the operator.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import _e4_evidence as evidence  # noqa: E402
import dispatch_e4_panel as harness  # noqa: E402
import recompute_receipts as recompute  # noqa: E402


class RecoveryError(RuntimeError):
    pass


def _object(value, label: str) -> dict:
    if not isinstance(value, dict):
        raise RecoveryError(f"{label} must be an object")
    return value


def _exact_keys(value: dict, expected: set[str], label: str) -> None:
    actual = set(value)
    if actual != expected:
        raise RecoveryError(
            f"{label} fields differ; missing={sorted(expected - actual)}, "
            f"extra={sorted(actual - expected)}")


def _string(value, label: str, *, empty: bool = False) -> str:
    if not isinstance(value, str) or (not empty and not value.strip()):
        raise RecoveryError(f"{label} must be a string"
                            + ("" if empty else " and non-empty"))
    return value


def _artifact_name(value, label: str) -> str:
    name = _string(value, label)
    path = Path(name)
    if path.is_absolute() or len(path.parts) != 1 or path.parts[0] in {
            ".", ".."}:
        raise RecoveryError(
            f"{label} must name one record-bundle artifact, got {name!r}")
    return name


def _plain_file(bundle_root: Path, name: str, label: str) -> Path:
    path = bundle_root / _artifact_name(name, label)
    try:
        evidence.assert_plain_file(path, bundle_root)
    except evidence.EvidencePathError as failure:
        raise RecoveryError(f"{label} does not resolve: {failure}") from failure
    return path


def _read_plain_text(bundle_root: Path, name: str, label: str) -> str:
    path = _plain_file(bundle_root, name, label)
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as failure:
        raise RecoveryError(f"{label} is not readable text") from failure


def _load_state(bundle_root: Path) -> dict:
    state_path = bundle_root / harness.RECOVERY_STATE_FILE
    try:
        evidence.assert_plain_file(state_path, bundle_root)
        state = json.loads(state_path.read_text(encoding="utf-8"))
    except (evidence.EvidencePathError, OSError, UnicodeDecodeError,
            json.JSONDecodeError) as failure:
        raise RecoveryError(
            f"cannot load {harness.RECOVERY_STATE_FILE}: "
            f"{type(failure).__name__}: {failure}") from failure
    state = _object(state, "recovery state")
    _exact_keys(state, {
        "schema", "evidence_contract", "context", "result",
        "bundle_manifest",
    }, "recovery state")
    if state["schema"] != harness.RECOVERY_STATE_SCHEMA:
        raise RecoveryError(f"unsupported recovery schema {state['schema']!r}")
    if state["evidence_contract"] != harness.EVIDENCE_CONTRACT:
        raise RecoveryError(
            f"unsupported evidence contract {state['evidence_contract']!r}")
    manifest = state["bundle_manifest"]
    if not isinstance(manifest, list) or not all(
            isinstance(entry, dict) for entry in manifest):
        raise RecoveryError("bundle_manifest must be a list of objects")
    if any(entry.get("type") not in {"file", "directory"}
           for entry in manifest):
        raise RecoveryError(
            "bundle_manifest contains a redirected or non-plain artifact")
    current = evidence.tree_manifest(
        bundle_root, exclude={harness.RECOVERY_STATE_FILE})
    if current != manifest:
        raise RecoveryError(
            "preserved bundle manifest changed; refusing incomplete or "
            "inconsistent evidence")
    return state


def _result_from_state(state: dict, bundle_root: Path) \
        -> tuple[harness.PanelResult, dict]:
    context = _object(state["context"], "context")
    _exact_keys(context, {
        "model_id", "suite_commit", "date", "dispatch_note",
        "working_tree_dirty",
    }, "context")
    _string(context["model_id"], "context.model_id")
    _string(context["suite_commit"], "context.suite_commit")
    if not harness._valid_date(context["date"]):
        raise RecoveryError("context.date is not a real YYYY-MM-DD date")
    _string(context["dispatch_note"], "context.dispatch_note", empty=True)
    if not isinstance(context["working_tree_dirty"], bool):
        raise RecoveryError("context.working_tree_dirty must be boolean")

    saved = _object(state["result"], "result")
    _exact_keys(saved, {
        "fixture", "condition", "replicate", "completed_stages", "canary",
        "retries", "abort",
    }, "result")
    fixture = _string(saved["fixture"], "result.fixture")
    if fixture not in harness.MANUSCRIPTS:
        raise RecoveryError(f"unknown fixture in recovery state: {fixture!r}")
    condition = _string(saved["condition"], "result.condition")
    if condition not in {"baseline", "post", "script_adapter"}:
        raise RecoveryError(f"unknown condition in recovery state: {condition!r}")
    replicate = saved["replicate"]
    if isinstance(replicate, bool) or not isinstance(replicate, int) \
            or not 1 <= replicate <= 99:
        raise RecoveryError("result.replicate must be an integer from 1 to 99")

    completed = saved["completed_stages"]
    canary = saved["canary"]
    retries = saved["retries"]
    if not isinstance(completed, list) or not all(
            isinstance(item, str) and item for item in completed):
        raise RecoveryError("result.completed_stages must be a string list")
    if len(completed) != len(set(completed)):
        raise RecoveryError("result.completed_stages contains duplicates")
    if not isinstance(canary, list) or not all(
            isinstance(item, str) for item in canary):
        raise RecoveryError("result.canary must be a string list")
    if not isinstance(retries, list):
        raise RecoveryError("result.retries must be a list")

    result = harness.PanelResult(
        fixture, condition, replicate,
        completed_stages=list(completed), canary=list(canary))
    for index, item in enumerate(retries):
        item = _object(item, f"result.retries[{index}]")
        _exact_keys(item, {
            "role", "stage", "diagnostic", "rejected_response_location",
            "checker_output_location", "form",
        }, f"result.retries[{index}]")
        role = _string(item["role"], f"result.retries[{index}].role")
        stage = _string(item["stage"], f"result.retries[{index}].stage")
        if stage not in {"phase1", "extraction", "phase2_multi_dissent",
                         "synthesis"}:
            raise RecoveryError(f"unknown retry stage {stage!r}")
        diagnostic = _string(
            item["diagnostic"], f"result.retries[{index}].diagnostic",
            empty=True)
        rejected = _artifact_name(
            item["rejected_response_location"],
            f"result.retries[{index}].rejected_response_location")
        checker = _artifact_name(
            item["checker_output_location"],
            f"result.retries[{index}].checker_output_location")
        form = item["form"]
        if form not in {None, "verbatim", "normalized"}:
            raise RecoveryError(f"unknown retry diagnostic form {form!r}")
        _plain_file(bundle_root, rejected, "rejected response")
        checker_text = _read_plain_text(
            bundle_root, checker, "checker output")
        if diagnostic not in checker_text:
            raise RecoveryError(
                f"retry diagnostic is inconsistent with {checker}")
        result.retries.append(harness.RetryEvent(
            role=role, stage=stage, diagnostic=diagnostic,
            rejected_response_location=rejected,
            checker_output_location=checker, form=form,
        ))

    abort = saved["abort"]
    if abort is not None:
        abort = _object(abort, "result.abort")
        _exact_keys(abort, {
            "stage", "exit_code", "diagnostic", "log_name", "form",
        }, "result.abort")
        stage = _string(abort["stage"], "result.abort.stage")
        exit_code = abort["exit_code"]
        if isinstance(exit_code, bool) or not isinstance(exit_code, int):
            raise RecoveryError("result.abort.exit_code must be an integer")
        diagnostic = _string(
            abort["diagnostic"], "result.abort.diagnostic", empty=True)
        log_name = _artifact_name(abort["log_name"], "result.abort.log_name")
        form = abort["form"]
        if form not in {None, "verbatim", "normalized"}:
            raise RecoveryError(f"unknown abort diagnostic form {form!r}")
        log_text = _read_plain_text(
            bundle_root, log_name, "abort checker output")
        if diagnostic not in log_text:
            raise RecoveryError(
                f"abort diagnostic is inconsistent with {log_name}")
        result.abort = harness.PanelAborted(
            stage, exit_code, diagnostic, log_name, form=form)

    for required in ("contract.json", "metadata.json", harness.Bundle.JOURNAL):
        _plain_file(bundle_root, required, required)
    journal = _read_plain_text(
        bundle_root, harness.Bundle.JOURNAL, "dispatch journal")
    journal_lines = journal.splitlines()
    witnessed_stages = [
        line.removeprefix("COMPLETE ")
        for line in journal_lines
        if line.startswith("COMPLETE ")
    ]
    if witnessed_stages != completed:
        raise RecoveryError(
            "completed stages disagree with the append-only dispatch "
            "journal")
    try:
        contract = json.loads(
            (bundle_root / "contract.json").read_text(encoding="utf-8"))
        seats = harness.seats_for(contract)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError,
            harness.PreconditionFailure) as failure:
        raise RecoveryError(f"contract evidence is inconsistent: {failure}") \
            from failure

    expected_canary: list[str] = []
    for line in journal_lines:
        match = re.fullmatch(r"DONE ([^/]+\.md) chars=(\d+)", line)
        if match is None:
            continue
        artifact = _artifact_name(match.group(1), "completed response")
        response = _read_plain_text(
            bundle_root, artifact, "completed response")
        if len(response) != int(match.group(2)):
            raise RecoveryError(
                f"dispatch journal character count disagrees for {artifact}")
        for token in harness.canary_hits(response):
            entry = f"{artifact}:{token}"
            if entry not in expected_canary:
                expected_canary.append(entry)
    if canary != expected_canary:
        raise RecoveryError(
            "canary ledger disagrees with completed preserved responses")

    seen_retry_artifacts: set[tuple[str, str]] = set()
    witnessed_retry_lines: list[str] = []
    for event in result.retries:
        if event.stage == "synthesis":
            if event.role != "synthesis":
                raise RecoveryError(
                    "synthesis retry must be bound to the synthesis role")
            response_pattern = r"synthesis\.a([1-9][0-9]*)\.md"
            checker_patterns = (
                r"synthesis\.a([1-9][0-9]*)\.gate\.log",
                r"synthesis\.a([1-9][0-9]*)\.deliverable\.log",
            )
            journal_prefix = "RETRY synthesis diagnostic="
        else:
            if event.role not in seats:
                raise RecoveryError(
                    f"retry role is not a contract seat: {event.role!r}")
            if event.stage == "extraction" and event.role != "methodology":
                raise RecoveryError(
                    "extraction retry must be bound to the methodology seat")
            phase = {
                "phase1": "phase1",
                "extraction": "extraction",
            }.get(event.stage, "phase2")
            escaped = re.escape(event.role)
            response_pattern = (
                rf"{escaped}\.{phase}\.a([1-9][0-9]*)\.md")
            checker_patterns = (
                rf"{escaped}\.{phase}\.a([1-9][0-9]*)\.gate\.log",
            )
            journal_prefix = {
                "phase1": f"RETRY {event.role} phase1 diagnostic=",
                "extraction": f"RETRY {event.role} extraction diagnostic=",
            }.get(event.stage,
                  f"RETRY {event.role} phase2 multi-dissent diagnostic=")
        response_match = re.fullmatch(
            response_pattern, event.rejected_response_location)
        checker_match = next((
            match for pattern in checker_patterns
            if (match := re.fullmatch(
                pattern, event.checker_output_location)) is not None
        ), None)
        if response_match is None or checker_match is None \
                or response_match.group(1) != checker_match.group(1):
            raise RecoveryError(
                "retry role/stage disagrees with its preserved artifact names")
        pair = (event.rejected_response_location,
                event.checker_output_location)
        if pair in seen_retry_artifacts:
            raise RecoveryError("retry evidence is duplicated in the ledger")
        seen_retry_artifacts.add(pair)
        witnessed_retry_lines.append(journal_prefix + event.diagnostic)
    journal_retry_lines = [
        line for line in journal_lines if line.startswith("RETRY ")]
    if witnessed_retry_lines != journal_retry_lines:
        raise RecoveryError(
            "retry ledger disagrees with the append-only dispatch journal")

    if result.abort is not None:
        exact = f"ABORT {result.abort.stage} exit={result.abort.exit_code}"
        special = (
            result.abort.exit_code == harness.EXIT_PRECONDITION
            and result.abort.stage in {"setup", "precondition"}
            and any(line.startswith(f"ABORT {result.abort.stage} ")
                    for line in journal_lines)
        ) or (
            result.abort.exit_code == harness.EXIT_BLOCKED
            and (
                any(line.startswith(
                    f"ABORT transport {result.abort.stage} ")
                    for line in journal_lines)
                or result.abort.stage in {"preservation", "interrupt", "io"}
                and any(line.startswith(f"ABORT {result.abort.stage} ")
                        for line in journal_lines)
            )
        )
        if exact not in journal_lines and not special:
            raise RecoveryError(
                "terminal abort disagrees with the append-only dispatch "
                "journal")
    canonical = ["field_analysis"]
    for role in seats:
        canonical.append(f"{role}.phase1")
        if role == "methodology":
            # #610 step 5: the methodology seat's three-call shape.
            canonical.extend(
                ("methodology.extraction", "methodology.recompute"))
        canonical.append(f"{role}.phase2")
    canonical.append("synthesis")
    positions = [canonical.index(stage) if stage in canonical else -1
                 for stage in completed]
    if -1 in positions or positions != sorted(positions):
        raise RecoveryError("completed stages are unknown or out of order")
    if result.abort is None and completed != canonical:
        raise RecoveryError(
            "completed stages do not support a completed terminal record")

    for stage in completed:
        if stage == "field_analysis":
            _plain_file(bundle_root, "field_analysis.md", stage)
            continue
        if stage == "methodology.recompute":
            # #610 step 5: the calculator stage's evidence is its receipts
            # artifact plus its log — it is not a model call and has no
            # response/gate pair. Because the calculator is deterministic,
            # the receipts are additionally RE-DERIVED here from the
            # gate-passed extraction and compared byte-for-byte (security
            # round 1, P2-5): a tampered receipts artifact cannot resume.
            _plain_file(bundle_root, harness.RECEIPTS_ARTIFACT, stage)
            _plain_file(bundle_root, "methodology.recompute.log", stage)
            extraction_text = None
            for candidate in sorted(
                    bundle_root.glob("methodology.extraction.a*.md")):
                gate = candidate.with_name(
                    candidate.name.removesuffix(".md") + ".gate.log")
                try:
                    evidence.assert_plain_file(candidate, bundle_root)
                    evidence.assert_plain_file(gate, bundle_root)
                    gate_lines = gate.read_text(
                        encoding="utf-8").splitlines()
                except (evidence.EvidencePathError, OSError,
                        UnicodeDecodeError):
                    continue
                terminal = next(
                    (line for line in reversed(gate_lines)
                     if line.strip()), "")
                if terminal == "EXTRACTION-CONFORMANCE: PASS":
                    extraction_text = candidate.read_text(encoding="utf-8")
            if extraction_text is None:
                raise RecoveryError(
                    "methodology.recompute lacks a gate-passed extraction "
                    "artifact to re-derive the receipts from")
            try:
                expected_receipts = recompute.compute_receipts(
                    recompute.parse_extraction(extraction_text))
            except (recompute.ExtractionError, ArithmeticError) as failure:
                raise RecoveryError(
                    "the preserved extraction no longer computes: "
                    f"{failure}") from failure
            actual_receipts = _read_plain_text(
                bundle_root, harness.RECEIPTS_ARTIFACT, stage)
            if actual_receipts != expected_receipts:
                raise RecoveryError(
                    "the receipts artifact disagrees with the "
                    "deterministic re-derivation from the preserved "
                    "extraction")
            continue
        if stage == "synthesis":
            pattern = "synthesis.a*.md"
            pass_marker = "PANEL-SYNTHESIS: PASS"
        else:
            role, phase = stage.split(".", 1)
            pattern = f"{role}.{phase}.a*.md"
            pass_marker = {
                "phase1": "PHASE1-CONFORMANCE: PASS",
                "extraction": "EXTRACTION-CONFORMANCE: PASS",
            }.get(phase, "PHASE-CONFORMANCE: PASS")
        # #610 step 5 (security round 1, P2-5): the evidence contract names
        # the injected-receipt identity gate as contract content, so a
        # methodology Phase 2 in a panel that ran the calculator must show
        # the gate's distinct witness line, not just the generic pass.
        required_markers = (
            ("RECEIPT-IDENTITY: PASS",)
            if stage == "methodology.phase2"
            and "methodology.recompute" in completed
            else ()
        )
        candidates = sorted(bundle_root.glob(pattern))
        witnessed = False
        for candidate in candidates:
            gate = candidate.with_name(
                candidate.name.removesuffix(".md") + ".gate.log")
            try:
                evidence.assert_plain_file(candidate, bundle_root)
                evidence.assert_plain_file(gate, bundle_root)
            except evidence.EvidencePathError:
                continue
            try:
                gate_lines = gate.read_text(encoding="utf-8").splitlines()
            except (OSError, UnicodeDecodeError) as failure:
                raise RecoveryError(
                    f"checker evidence is not readable text: {gate.name}") \
                    from failure
            terminal = next(
                (line for line in reversed(gate_lines) if line.strip()), "")
            if terminal == pass_marker and all(
                    marker in gate_lines for marker in required_markers):
                witnessed = True
                break
        if not witnessed:
            raise RecoveryError(
                f"completed stages lack response/checker evidence for {stage}")
    return result, context


def resume(bundle_path: Path, work_dir: Path) -> tuple[Path, dict]:
    bundle_path = evidence.lexical_path(Path(bundle_path))
    work_dir = evidence.lexical_path(Path(work_dir))
    if work_dir == harness.REPO or harness.REPO in work_dir.parents:
        raise RecoveryError("work directory must remain outside the repository")
    try:
        evidence.assert_plain_directory(bundle_path, work_dir)
    except evidence.EvidencePathError as failure:
        raise RecoveryError(str(failure)) from failure
    state = _load_state(bundle_path)
    result, context = _result_from_state(state, bundle_path)
    bundle = harness.Bundle(bundle_path)
    stem = harness.stem_for(result, context["date"])
    blocked = result.abort is not None or result.provenance_status(
        bundle) != "valid"
    canonical_raw = (work_dir / "runs" / "raw" / "blocked" / stem
                     if blocked else work_dir / "runs" / "raw" / stem)
    supported = {work_dir / "bundle", canonical_raw}
    if bundle_path not in supported:
        raise RecoveryError(
            "bundle is not at a supported retained location; expected "
            f"{work_dir / 'bundle'} or {canonical_raw}")
    try:
        return harness.emit(
            result, bundle, work_dir,
            model_id=context["model_id"],
            suite_commit=context["suite_commit"],
            date=context["date"],
            dispatch_note=context["dispatch_note"],
            working_tree_dirty=context["working_tree_dirty"],
        )
    except (OSError, harness.PreconditionFailure,
            harness.PreservationError) as failure:
        raise RecoveryError(str(failure)) from failure


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--bundle", required=True, type=Path)
    parser.add_argument("--work-dir", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        path, record = resume(args.bundle, args.work_dir)
    except RecoveryError as failure:
        print(f"RECOVERY REFUSED: {failure}", file=sys.stderr)
        return harness.EXIT_PRECONDITION
    print(f"record: {path}")
    for key in ("measurement_status", "provenance_status",
                "panel_completion_status", "score_eligible"):
        print(f"{key}: {record[key]}")
    return harness.EXIT_OK if record["score_eligible"] else harness.EXIT_BLOCKED


if __name__ == "__main__":
    raise SystemExit(main())
