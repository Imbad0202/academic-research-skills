"""Hermetic runner, blinding, and human-label tests for #684."""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import sys

import pytest

import run_review_criteria_constructive_value as runner
import score_review_criteria_constructive_value as scorer


def _fake_codex(
    tmp_path: Path, *, status: str = "Logged in using ChatGPT",
    status_to_stderr: bool = False, forbidden_event: bool = False,
    invalid_output: bool = False, feature_names: tuple[str, ...] | None = None,
) -> tuple[Path, Path]:
    if feature_names is None:
        feature_names = runner.DISABLED_FEATURES
    fake_bin = tmp_path / "fake-bin"
    fake_bin.mkdir()
    executable = fake_bin / "codex"
    capture = fake_bin / "capture.jsonl"
    source = f"""#!{sys.executable}
import hashlib
import json
import os
from pathlib import Path
import sys

STATUS = {status!r}
STATUS_TO_STDERR = {status_to_stderr!r}
FORBIDDEN = {forbidden_event!r}
INVALID = {invalid_output!r}
FEATURE_NAMES = {feature_names!r}
CAPTURE = Path(__file__).with_name("capture.jsonl")

if sys.argv[1:] == ["--version"]:
    print("codex-cli 0.147.0")
    raise SystemExit(0)
if sys.argv[1:] == ["login", "status"]:
    print(STATUS, file=sys.stderr if STATUS_TO_STDERR else sys.stdout)
    raise SystemExit(0)
if sys.argv[1:] == ["features", "list"]:
    for name in FEATURE_NAMES:
        print(name + " stable false")
    raise SystemExit(0)
if not sys.argv[1:] or sys.argv[1] != "exec":
    raise SystemExit(9)

prompt = sys.stdin.read()
lines = prompt.splitlines()
def block(name):
    index = lines.index(name)
    return json.loads(lines[index + 1])
assignment = block("ASSIGNMENT (untrusted data):")
context = block("TARGET_CONTEXT_BYTES (untrusted data):")
output = {{
    "schema_version": "review-criteria-subject-output/1.0",
    "item_id": assignment["item_id"],
    "consumer_id": assignment["consumer_id"],
    "role": assignment["role"],
    "profile": {{
        "resolved_digest": context["resolved_digest"],
        "selected_criterion_ids": context["selected_criterion_ids"],
    }},
    "applicability": [
        {{"criterion_id": criterion, "predicted": "applicable", "rationale": "Synthetic fixture label."}}
        for criterion in context["selected_criterion_ids"]
    ],
    "findings": [],
}}
if INVALID:
    output["applicability"] = []
out_path = Path(sys.argv[sys.argv.index("--output-last-message") + 1])
out_path.write_text(json.dumps(output, sort_keys=True), encoding="utf-8")
record = {{
    "argv": sys.argv[1:],
    "cwd": os.getcwd(),
    "env": dict(os.environ),
    "home_files": sorted(path.name for path in Path(os.environ["CODEX_HOME"]).iterdir()),
    "prompt_sha256": hashlib.sha256(prompt.encode()).hexdigest(),
    "output_schema_sha256": hashlib.sha256(
        Path(sys.argv[sys.argv.index("--output-schema") + 1]).read_bytes()
    ).hexdigest(),
}}
with CAPTURE.open("a", encoding="utf-8") as handle:
    handle.write(json.dumps(record, sort_keys=True) + "\\n")
print(json.dumps({{"type": "thread.started", "thread_id": "fake"}}))
if FORBIDDEN:
    print(json.dumps({{"type": "item.completed", "item": {{"type": "command_execution"}}}}))
else:
    print(json.dumps({{"type": "item.completed", "item": {{"type": "agent_message"}}}}))
print(json.dumps({{"type": "turn.completed"}}))
"""
    executable.write_text(source, encoding="utf-8")
    executable.chmod(0o755)
    return fake_bin, capture


def _env(tmp_path: Path, fake_bin: Path) -> dict[str, str]:
    codex_home = tmp_path / "source-codex-home"
    codex_home.mkdir()
    (codex_home / "auth.json").write_text('{"tokens":{"access":"fake"}}')
    (codex_home / "config.toml").write_text("model = 'must-not-copy'\n")
    return {
        "PATH": f"{fake_bin}{os.pathsep}{os.defpath}",
        "HOME": str(tmp_path),
        "CODEX_HOME": str(codex_home),
        "OPENAI_API_KEY": "must-not-reach-child",
        "ANTHROPIC_API_KEY": "must-not-reach-child",
        "GEMINI_API_KEY": "must-not-reach-child",
    }


def _init_args(run_dir: Path) -> argparse.Namespace:
    return argparse.Namespace(
        run_dir=run_dir,
        suite_commit="a" * 40,
        model="gpt-5.6",
        codex_version="0.147.0",
        reasoning_effort="high",
        input_token_cap=12000,
        output_token_cap=3000,
    )


def _dispatch_args(run_dir: Path, *, consent: bool = True, digest: str | None = None):
    raw = (run_dir / "run-plan.json").read_bytes()
    return argparse.Namespace(
        run_dir=run_dir,
        plan_sha256=digest or hashlib.sha256(raw).hexdigest(),
        execute_24_subscription_calls=consent,
    )


def _prepare_run(tmp_path: Path, monkeypatch) -> tuple[Path, dict[str, str], Path]:
    fake_bin, capture = _fake_codex(tmp_path)
    environ = _env(tmp_path, fake_bin)
    monkeypatch.setattr(runner, "_verify_frozen_commit", lambda _commit, _assets: None)
    run_dir = tmp_path / "run"
    runner.init_run(_init_args(run_dir))
    return run_dir, environ, capture


def test_frozen_assets_and_exact_balanced_plan_validate() -> None:
    result = runner.validate_assets()
    assert result["items"] == 6
    assert result["calls"] == 24
    plan = json.loads(runner.CALL_PLAN_PATH.read_text())
    assert [row["arm"] for row in plan["calls"][:4]] == [
        "baseline", "treatment", "treatment", "baseline"
    ]
    assert [row["arm"] for row in plan["calls"][4:8]] == [
        "treatment", "baseline", "baseline", "treatment"
    ]


def test_lock_hash_mutation_fails(monkeypatch, tmp_path) -> None:
    lock = json.loads(runner.LOCK_PATH.read_text())
    first = next(iter(lock["assets"]))
    lock["assets"][first] = "0" * 64
    path = tmp_path / "bad-lock.json"
    path.write_text(json.dumps(lock))
    monkeypatch.setattr(runner, "LOCK_PATH", path)
    with pytest.raises(runner.MeasurementError, match="hash mismatch"):
        runner.validate_assets()


@pytest.mark.parametrize("keyword", ["const", "enum"])
def test_provider_response_schema_requires_explicit_types(keyword: str) -> None:
    schema = {
        "type": "object",
        "additionalProperties": False,
        "required": ["value"],
        "properties": {"value": {keyword: "x" if keyword == "const" else ["x"]}},
    }
    with pytest.raises(runner.MeasurementError, match="requires explicit type"):
        runner._validate_provider_response_schema(schema)


def test_provider_response_schema_requires_closed_fully_required_objects() -> None:
    schema = {
        "type": "object",
        "additionalProperties": False,
        "required": [],
        "properties": {"value": {"type": "string"}},
    }
    with pytest.raises(runner.MeasurementError, match="require every property"):
        runner._validate_provider_response_schema(schema)


def test_provider_response_schema_projection_keeps_local_validation_only_local() -> None:
    source = json.loads(runner.OUTPUT_SCHEMA_PATH.read_text())
    projected = runner._project_provider_response_schema(source)
    serialized = json.dumps(projected, sort_keys=True)
    for keyword in runner.PROVIDER_SCHEMA_STRIPPED_KEYWORDS:
        assert f'"{keyword}"' not in serialized
    assert '"pattern"' in serialized
    assert '"minItems"' in serialized
    assert '"maxItems"' in serialized
    runner._validate_provider_response_schema(projected)

    source_serialized = json.dumps(source, sort_keys=True)
    assert '"uniqueItems"' in source_serialized
    assert '"minLength"' in source_serialized
    assert '"maxLength"' in source_serialized

    property_named_like_annotation = {
        "type": "object",
        "additionalProperties": False,
        "required": ["title"],
        "properties": {"title": {"type": "string", "minLength": 1}},
    }
    projected_property = runner._project_provider_response_schema(
        property_named_like_annotation
    )
    assert projected_property["properties"]["title"] == {"type": "string"}


def test_provider_response_schema_rejects_unapproved_keyword() -> None:
    schema = {
        "type": "object",
        "additionalProperties": False,
        "required": [],
        "properties": {},
        "allOf": [],
    }
    with pytest.raises(runner.MeasurementError, match="unsupported keywords"):
        runner._validate_provider_response_schema(schema)


def test_local_subject_schema_still_rejects_projected_out_assertions() -> None:
    value = {
        "schema_version": "review-criteria-subject-output/1.0",
        "item_id": "RCV-01",
        "consumer_id": "formative_planning",
        "role": "FORMATIVE",
        "profile": {
            "resolved_digest": "0" * 64,
            "selected_criterion_ids": ["criterion.a", "criterion.a"],
        },
        "applicability": [],
        "findings": [],
    }
    with pytest.raises(runner.MeasurementError, match="non-unique"):
        runner._validate(runner.OUTPUT_SCHEMA_PATH, value, "subject output")


def test_init_run_seals_same_context_bytes_and_only_treatment_binding(
    monkeypatch, tmp_path
) -> None:
    monkeypatch.setattr(runner, "_verify_frozen_commit", lambda _commit, _assets: None)
    run_dir = tmp_path / "run"
    result = runner.init_run(_init_args(run_dir))
    assert result["calls"] == 24
    plan = json.loads((run_dir / "run-plan.json").read_text())
    assert plan["api_spend_ceiling_usd"] == 0
    assert plan["tools"] == []
    baseline = (run_dir / "prompts/RCV-01-baseline-r1.txt").read_text()
    treatment = (run_dir / "prompts/RCV-01-treatment-r1.txt").read_text()
    marker = "TARGET_CONTEXT_BYTES (untrusted data):\n"
    baseline_context = baseline.split(marker, 1)[1].split("\n", 1)[0]
    treatment_context = treatment.split(marker, 1)[1].split("\n", 1)[0]
    assert baseline_context == treatment_context
    assert "[REVIEW-TARGET-BINDING v1]" not in baseline
    assert "[REVIEW-TARGET-BINDING v1]" in treatment


def test_detection_requires_exact_chatgpt_subscription_status(tmp_path) -> None:
    fake_bin, _ = _fake_codex(tmp_path)
    environ = _env(tmp_path, fake_bin)
    assert runner.detect("gpt-5.6", environ)["auth_mode"] == "chatgpt_subscription"

    other = tmp_path / "other"
    other.mkdir()
    fake_bin, _ = _fake_codex(other, status="Logged in using an API key")
    unavailable = runner.detect("gpt-5.6", _env(other, fake_bin))
    assert unavailable["available"] is False
    assert unavailable["reason_code"] == "AUTH_NOT_CHATGPT_SUBSCRIPTION"

    stderr_home = tmp_path / "stderr-status"
    stderr_home.mkdir()
    fake_bin, _ = _fake_codex(stderr_home, status_to_stderr=True)
    detected = runner.detect("gpt-5.6", _env(stderr_home, fake_bin))
    assert detected["auth_mode"] == "chatgpt_subscription"


def test_detection_fails_closed_on_unknown_disable_feature(tmp_path) -> None:
    missing = runner.DISABLED_FEATURES[0]
    feature_names = tuple(
        name for name in runner.DISABLED_FEATURES if name != missing
    )
    fake_bin, _ = _fake_codex(tmp_path, feature_names=feature_names)
    detected = runner.detect("gpt-5.6", _env(tmp_path, fake_bin))
    assert detected["available"] is False
    assert detected["reason_code"] == "CODEX_FEATURE_FLAGS_INCOMPATIBLE"
    assert detected["unsupported_feature_flags"] == [missing]


def test_dispatch_requires_flag_and_exact_plan_hash(monkeypatch, tmp_path) -> None:
    run_dir, environ, capture = _prepare_run(tmp_path, monkeypatch)
    with pytest.raises(runner.MeasurementError, match="execute-24"):
        runner.dispatch(_dispatch_args(run_dir, consent=False), environ)
    with pytest.raises(runner.MeasurementError, match="plan-sha256"):
        runner.dispatch(_dispatch_args(run_dir, digest="0" * 64), environ)
    assert not capture.exists()


def test_fake_subscription_dispatch_is_contained_complete_and_idempotent(
    monkeypatch, tmp_path
) -> None:
    run_dir, environ, capture = _prepare_run(tmp_path, monkeypatch)
    result = runner.dispatch(_dispatch_args(run_dir), environ)
    assert result["completed_calls"] == 24
    assert result["api_spend_usd"] == 0
    manifest = json.loads((run_dir / "execution-manifest.json").read_text())
    assert len(manifest["calls"]) == 24
    rows = [json.loads(line) for line in capture.read_text().splitlines()]
    assert len(rows) == 24
    provider_schema = runner._project_provider_response_schema(
        json.loads(runner.OUTPUT_SCHEMA_PATH.read_text())
    )
    provider_schema_sha256 = hashlib.sha256(
        runner._json_bytes(provider_schema)
    ).hexdigest()
    for row in rows:
        assert row["home_files"] == ["auth.json"]
        assert "OPENAI_API_KEY" not in row["env"]
        assert "ANTHROPIC_API_KEY" not in row["env"]
        assert "GEMINI_API_KEY" not in row["env"]
        assert "--ephemeral" in row["argv"]
        assert "--ignore-user-config" in row["argv"]
        assert "read-only" in row["argv"]
        disabled = [
            row["argv"][index + 1]
            for index, value in enumerate(row["argv"][:-1])
            if value == "--disable"
        ]
        assert disabled == list(runner.DISABLED_FEATURES)
        assert "view_image" not in disabled
        assert row["output_schema_sha256"] == provider_schema_sha256
    before = capture.read_bytes()
    manifest_before = (run_dir / "execution-manifest.json").read_bytes()
    runner.dispatch(_dispatch_args(run_dir), environ)
    assert capture.read_bytes() == before
    assert (run_dir / "execution-manifest.json").read_bytes() == manifest_before


@pytest.mark.parametrize(
    ("forbidden", "invalid", "match"),
    [(True, False, "forbidden tool"), (False, True, "applicability")],
)
def test_dispatch_fails_closed_on_tool_event_or_semantic_output(
    monkeypatch, tmp_path, forbidden: bool, invalid: bool, match: str
) -> None:
    fake_bin, capture = _fake_codex(
        tmp_path, forbidden_event=forbidden, invalid_output=invalid
    )
    environ = _env(tmp_path, fake_bin)
    monkeypatch.setattr(runner, "_verify_frozen_commit", lambda _commit, _assets: None)
    run_dir = tmp_path / "run"
    runner.init_run(_init_args(run_dir))
    with pytest.raises(runner.MeasurementError, match=match):
        runner.dispatch(_dispatch_args(run_dir), environ)
    blocked = list((run_dir / "blocked").glob("*.json"))
    assert len(blocked) == 1
    assert json.loads(blocked[0].read_text())["api_spend_usd"] == 0
    before = capture.read_bytes()
    with pytest.raises(runner.MeasurementError, match="does not authorize a retry"):
        runner.dispatch(_dispatch_args(run_dir), environ)
    assert capture.read_bytes() == before


def _label_file(packet: dict, packet_sha: str, expert_id: str) -> dict:
    return {
        "schema_version": "review-criteria-expert-labels/1.0",
        "suite": runner.SUITE,
        "packet_sha256": packet_sha,
        "expert": {
            "expert_id": expert_id,
            "expert_type": "human",
            "expertise": "synthetic fixture expertise",
            "independent": True,
            "blinded_to": runner.BLINDING,
        },
        "labels": [
            {
                "blind_output_id": row["blind_output_id"],
                "applicability": [
                    {"criterion_id": value["criterion_id"], "label": "applicable"}
                    for value in row["subject_output"]["applicability"]
                ],
                "findings": [],
                "rationale": "Fixture labels the supplied synthetic output only.",
            }
            for row in packet["outputs"]
        ],
    }


def _decisions(packet: dict, packet_sha: str) -> dict:
    return {
        "schema_version": "review-criteria-adjudication-decisions/1.0",
        "suite": runner.SUITE,
        "packet_sha256": packet_sha,
        "adjudicator_id": "expert-c",
        "adjudicator_type": "human",
        "method": "Arm-blind fixture adjudication",
        "arm_blind": True,
        "disagreements_retained": True,
        "decisions": [
            {
                "blind_output_id": row["blind_output_id"],
                "applicability": [
                    {"criterion_id": value["criterion_id"], "expert_label": "applicable"}
                    for value in row["subject_output"]["applicability"]
                ],
                "findings": [],
                "rationale": "Fixture decision preserves unanimous labels.",
            }
            for row in packet["outputs"]
        ],
    }


def test_blind_packet_two_experts_finalize_and_score(monkeypatch, tmp_path) -> None:
    run_dir, environ, _capture = _prepare_run(tmp_path, monkeypatch)
    runner.dispatch(_dispatch_args(run_dir), environ)
    packet_path = tmp_path / "expert-packet.json"
    map_path = tmp_path / "arm-map.json"
    runner.prepare_expert_packet(
        argparse.Namespace(run_dir=run_dir, output=packet_path, arm_map=map_path)
    )
    packet_raw = packet_path.read_bytes()
    packet = json.loads(packet_raw)
    assert b'"arm":"baseline"' not in packet_raw
    assert b'"arm":"treatment"' not in packet_raw
    assert len(packet["outputs"]) == 24
    packet_sha = hashlib.sha256(packet_raw).hexdigest()
    expert_paths = []
    for expert_id in ("expert-a", "expert-b"):
        path = tmp_path / f"{expert_id}.json"
        path.write_text(json.dumps(_label_file(packet, packet_sha, expert_id)))
        runner.validate_labels(argparse.Namespace(packet=packet_path, labels=path))
        expert_paths.append(path)
    decisions_path = tmp_path / "decisions.json"
    decisions_path.write_text(json.dumps(_decisions(packet, packet_sha)))
    output = tmp_path / "paired-adjudication.json"
    result = runner.finalize(
        argparse.Namespace(
            run_dir=run_dir,
            packet=packet_path,
            arm_map=map_path,
            expert_labels=expert_paths,
            decisions=decisions_path,
            output=output,
        )
    )
    assert result["replicates"] == 24
    record = json.loads(output.read_text())
    score = scorer.score(record, output.read_bytes())
    assert score["per_arm"]["baseline"]["profile_resolution_rate"]["denominator"] == 12
    assert score["per_arm"]["treatment"]["profile_resolution_rate"]["denominator"] == 12
    assert score["composite_score"] is None
    plan = json.loads((run_dir / "run-plan.json").read_text())
    report = runner._measurement_report_value(
        plan=plan,
        measurement_date="2026-08-11",
        paired_ref=(
            "evals/heldout/review_criteria_constructive_value/runs/fixture/"
            "paired-adjudication.json"
        ),
        paired_sha256="a" * 64,
        execution_ref=(
            "evals/heldout/review_criteria_constructive_value/runs/fixture/"
            "execution-manifest.json"
        ),
        execution_sha256="b" * 64,
        raw_paths=["evals/heldout/review_criteria_constructive_value/runs/fixture"],
        score=score,
    )
    errors, _warnings = runner.validate_report(report)
    assert errors == []


def test_forged_arm_map_is_rejected(monkeypatch, tmp_path) -> None:
    run_dir, environ, _capture = _prepare_run(tmp_path, monkeypatch)
    runner.dispatch(_dispatch_args(run_dir), environ)
    packet_path = tmp_path / "expert-packet.json"
    map_path = tmp_path / "arm-map.json"
    runner.prepare_expert_packet(
        argparse.Namespace(run_dir=run_dir, output=packet_path, arm_map=map_path)
    )
    packet_raw = packet_path.read_bytes()
    packet = json.loads(packet_raw)
    packet_sha = hashlib.sha256(packet_raw).hexdigest()
    expert_paths = []
    for expert_id in ("expert-a", "expert-b"):
        path = tmp_path / f"{expert_id}.json"
        path.write_text(json.dumps(_label_file(packet, packet_sha, expert_id)))
        expert_paths.append(path)
    decisions_path = tmp_path / "decisions.json"
    decisions_path.write_text(json.dumps(_decisions(packet, packet_sha)))
    arm_map = json.loads(map_path.read_text())
    arm_map["mapping"][0]["arm"] = (
        "treatment" if arm_map["mapping"][0]["arm"] == "baseline" else "baseline"
    )
    map_path.write_text(json.dumps(arm_map))
    with pytest.raises(runner.MeasurementError, match="does not match"):
        runner.finalize(
            argparse.Namespace(
                run_dir=run_dir,
                packet=packet_path,
                arm_map=map_path,
                expert_labels=expert_paths,
                decisions=decisions_path,
                output=tmp_path / "never.json",
            )
        )


def test_forged_expert_packet_is_rejected(monkeypatch, tmp_path) -> None:
    run_dir, environ, _capture = _prepare_run(tmp_path, monkeypatch)
    runner.dispatch(_dispatch_args(run_dir), environ)
    packet_path = tmp_path / "expert-packet.json"
    map_path = tmp_path / "arm-map.json"
    runner.prepare_expert_packet(
        argparse.Namespace(run_dir=run_dir, output=packet_path, arm_map=map_path)
    )
    packet = json.loads(packet_path.read_text())
    packet["outputs"][0]["subject_output"]["profile"]["resolved_digest"] = "0" * 64
    packet_path.write_text(json.dumps(packet))
    packet_raw = packet_path.read_bytes()
    packet_sha = hashlib.sha256(packet_raw).hexdigest()
    arm_map = json.loads(map_path.read_text())
    arm_map["packet_sha256"] = packet_sha
    map_path.write_text(json.dumps(arm_map))
    expert_paths = []
    for expert_id in ("expert-a", "expert-b"):
        path = tmp_path / f"{expert_id}.json"
        path.write_text(json.dumps(_label_file(packet, packet_sha, expert_id)))
        expert_paths.append(path)
    decisions_path = tmp_path / "decisions.json"
    decisions_path.write_text(json.dumps(_decisions(packet, packet_sha)))
    with pytest.raises(runner.MeasurementError, match="subject-output drift"):
        runner.finalize(
            argparse.Namespace(
                run_dir=run_dir,
                packet=packet_path,
                arm_map=map_path,
                expert_labels=expert_paths,
                decisions=decisions_path,
                output=tmp_path / "never.json",
            )
        )


def test_post_dispatch_run_plan_drift_is_rejected(monkeypatch, tmp_path) -> None:
    run_dir, environ, _capture = _prepare_run(tmp_path, monkeypatch)
    runner.dispatch(_dispatch_args(run_dir), environ)
    plan_path = run_dir / "run-plan.json"
    plan = json.loads(plan_path.read_text())
    plan["calls"][0]["arm"] = "treatment"
    plan_path.write_text(json.dumps(plan))
    with pytest.raises(runner.MeasurementError, match="drifts from call_plan"):
        runner.prepare_expert_packet(
            argparse.Namespace(
                run_dir=run_dir,
                output=tmp_path / "never-packet.json",
                arm_map=tmp_path / "never-map.json",
            )
        )


def test_explicit_symlink_input_is_rejected(tmp_path) -> None:
    target = tmp_path / "target.json"
    target.write_text("{}")
    link = tmp_path / "link.json"
    link.symlink_to(target)
    with pytest.raises(runner.MeasurementError, match="without symlinks"):
        runner._safe_explicit_file(link)
