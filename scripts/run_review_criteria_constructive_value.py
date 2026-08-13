#!/usr/bin/env python3
"""Contained subscription-CLI runner for the #684 paired measurement.

CI exercises asset validation, prompt sealing, fake-Codex dispatch, blinding,
and expert-record assembly.  No command selects an API transport.  The only
live path is ``dispatch`` and it requires the exact frozen run-plan SHA-256 plus
the explicit ``--execute-24-subscription-calls`` flag.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
from pathlib import Path
import re
import secrets
import shutil
import stat
import subprocess
import sys
import tempfile
from typing import Any, NoReturn

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

from check_heldout_measurement_report import location_errors, validate_report
from resolve_review_target_context import render_brief, resolve, validate_registry
from score_review_criteria_constructive_value import score as score_paired_record


REPO_ROOT = Path(__file__).resolve().parents[1]
SUITE = "review_criteria_constructive_value"
SUITE_ROOT = REPO_ROOT / "evals" / "heldout" / SUITE
LOCK_PATH = SUITE_ROOT / "suite_lock.json"
SCENARIOS_PATH = SUITE_ROOT / "scenarios.json"
SCENARIOS_SCHEMA_PATH = SUITE_ROOT / "scenarios.schema.json"
DECLARATION_SCHEMA_PATH = (
    REPO_ROOT / "shared/contracts/review_target/review_target_declaration.schema.json"
)
REGISTRY_PATH = REPO_ROOT / "scripts/fixtures/review_target_context/synthetic-registry.json"
HELDOUT_SET_PATH = SUITE_ROOT / "heldout_set.json"
CALL_PLAN_PATH = SUITE_ROOT / "call_plan.json"
BASELINE_PROMPT_PATH = SUITE_ROOT / "baseline_prompt.md"
TREATMENT_PROMPT_PATH = SUITE_ROOT / "treatment_prompt.md"
OUTPUT_SCHEMA_PATH = SUITE_ROOT / "subject_output.schema.json"
EXPERT_PACKET_SCHEMA_PATH = SUITE_ROOT / "expert_packet.schema.json"
EXPERT_LABELS_SCHEMA_PATH = SUITE_ROOT / "expert_labels.schema.json"
DECISIONS_SCHEMA_PATH = SUITE_ROOT / "adjudication_decisions.schema.json"
PAIRED_SCHEMA_PATH = SUITE_ROOT / "paired_adjudication.schema.json"
EXECUTION_SCHEMA_PATH = REPO_ROOT / "evals/heldout/execution_manifest.schema.json"
MEASUREMENT_PLAN_PATH = SUITE_ROOT / "measurement_plan.md"
EXPERT_GUIDE_PATH = SUITE_ROOT / "expert_label_guide.md"

RUN_PLAN_VERSION = "review-criteria-run-plan/1.0"
RECEIPT_VERSION = "review-criteria-subject-receipt/1.0"
MIN_CODEX_VERSION = (0, 147, 0)
MAX_ASSET_BYTES = 4 * 1024 * 1024
MAX_EVENT_BYTES = 8 * 1024 * 1024
MAX_OUTPUT_BYTES = 2 * 1024 * 1024
MODEL_RE = re.compile(r"^gpt-[a-z0-9][a-z0-9._-]{0,123}$")
SHA_RE = re.compile(r"^[0-9a-f]{64}$")
COMMIT_RE = re.compile(r"^[0-9a-f]{40}$")
VERSION_RE = re.compile(r"\bcodex-cli\s+(\d+)\.(\d+)\.(\d+)\b")
FEATURE_NAME_RE = re.compile(r"^[a-z][a-z0-9_]*$")
PROVIDER_SCHEMA_STRIPPED_KEYWORDS = frozenset(
    {"$schema", "$id", "title", "uniqueItems", "minLength", "maxLength"}
)
PROVIDER_SCHEMA_ALLOWED_KEYWORDS = frozenset(
    {
        "type",
        "const",
        "enum",
        "properties",
        "required",
        "additionalProperties",
        "items",
        "minItems",
        "maxItems",
        "pattern",
    }
)
BLINDING = [
    "arm_identity",
    "mechanism_state",
    "other_experts",
    "raw_aggregate",
    "expected_direction",
]
LOCKED_ASSET_REFS = {
    "evals/heldout/review_criteria_constructive_value/adjudication_decisions.schema.json",
    "evals/heldout/review_criteria_constructive_value/baseline_prompt.md",
    "evals/heldout/review_criteria_constructive_value/call_plan.json",
    "evals/heldout/review_criteria_constructive_value/expert_label_guide.md",
    "evals/heldout/review_criteria_constructive_value/expert_labels.schema.json",
    "evals/heldout/review_criteria_constructive_value/expert_packet.schema.json",
    "evals/heldout/review_criteria_constructive_value/heldout_set.json",
    "evals/heldout/review_criteria_constructive_value/measurement_plan.md",
    "evals/heldout/review_criteria_constructive_value/paired_adjudication.schema.json",
    "evals/heldout/review_criteria_constructive_value/scenarios.json",
    "evals/heldout/review_criteria_constructive_value/scenarios.schema.json",
    "evals/heldout/review_criteria_constructive_value/subject_output.schema.json",
    "evals/heldout/review_criteria_constructive_value/treatment_prompt.md",
    "scripts/fixtures/review_target_context/synthetic-registry.json",
    "scripts/run_review_criteria_constructive_value.py",
    "scripts/score_review_criteria_constructive_value.py",
}
DISABLED_FEATURES = (
    "shell_tool",
    "unified_exec",
    "apps",
    "plugins",
    "plugin_sharing",
    "skill_search",
    "multi_agent",
    "multi_agent_v2",
    "computer_use",
    "browser_use",
    "browser_use_external",
    "browser_use_full_cdp_access",
    "in_app_browser",
    "image_generation",
    "artifact",
    "code_mode",
    "code_mode_host",
    "hooks",
    "goals",
    "workspace_dependencies",
    "shell_snapshot",
)
FORBIDDEN_EVENT_ITEM_TOKENS = (
    "command",
    "tool",
    "file_change",
    "mcp",
    "web_search",
    "image",
    "computer",
    "collab",
    "subagent",
    "plan",
)


class MeasurementError(RuntimeError):
    """A closed asset, transport, output, or expert-record violation."""


def _fail(message: str) -> NoReturn:
    raise MeasurementError(message)


def _reject_pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _strict_loads(raw: bytes) -> Any:
    return json.loads(
        raw.decode("utf-8"),
        object_pairs_hook=_reject_pairs,
        parse_constant=lambda value: (_ for _ in ()).throw(
            ValueError(f"non-finite JSON number: {value}")
        ),
    )


def _canonical(value: Any) -> bytes:
    try:
        return json.dumps(
            value,
            ensure_ascii=False,
            allow_nan=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
    except (TypeError, ValueError, UnicodeEncodeError) as exc:
        raise MeasurementError(f"value is not canonical JSON: {exc}") from exc


def _sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _safe_explicit_file(path: Path, *, limit: int = MAX_ASSET_BYTES) -> bytes:
    absolute = path.absolute()
    parts = absolute.parts
    directory_flags = os.O_RDONLY | getattr(os, "O_DIRECTORY", 0)
    nofollow = getattr(os, "O_NOFOLLOW", 0)
    directory_fd = os.open(absolute.anchor, directory_flags)
    try:
        for component in parts[1:-1]:
            next_fd = os.open(
                component,
                directory_flags | nofollow,
                dir_fd=directory_fd,
            )
            os.close(directory_fd)
            directory_fd = next_fd
        fd = os.open(parts[-1], os.O_RDONLY | nofollow, dir_fd=directory_fd)
    except OSError as exc:
        raise MeasurementError(
            f"cannot open explicit path without symlinks {path}: {exc}"
        ) from exc
    finally:
        os.close(directory_fd)
    info = os.fstat(fd)
    if not stat.S_ISREG(info.st_mode):
        os.close(fd)
        _fail(f"explicit input is not a regular file: {path}")
    if info.st_size > limit:
        os.close(fd)
        _fail(f"explicit input exceeds {limit} bytes: {path}")
    chunks: list[bytes] = []
    total = 0
    try:
        while True:
            chunk = os.read(fd, min(65_536, limit + 1 - total))
            if not chunk:
                break
            chunks.append(chunk)
            total += len(chunk)
            if total > limit:
                _fail(f"explicit input exceeds {limit} bytes: {path}")
        final = os.fstat(fd)
        raw = b"".join(chunks)
        if len(raw) != final.st_size or (
            info.st_dev,
            info.st_ino,
            info.st_size,
            info.st_mtime_ns,
            info.st_ctime_ns,
        ) != (
            final.st_dev,
            final.st_ino,
            final.st_size,
            final.st_mtime_ns,
            final.st_ctime_ns,
        ):
            _fail(f"explicit input changed while being read: {path}")
        return raw
    finally:
        os.close(fd)


def _load_json(path: Path) -> tuple[dict[str, Any], bytes]:
    raw = _safe_explicit_file(path)
    try:
        value = _strict_loads(raw)
    except (UnicodeError, ValueError, json.JSONDecodeError) as exc:
        raise MeasurementError(f"invalid strict JSON {path}: {exc}") from exc
    if not isinstance(value, dict):
        _fail(f"JSON root must be an object: {path}")
    return value, raw


def _schema(path: Path) -> dict[str, Any]:
    value, _ = _load_json(path)
    Draft202012Validator.check_schema(value)
    return value


def _validate(schema_path: Path, value: Any, label: str) -> None:
    schema = _schema(schema_path)
    errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(value),
        key=lambda error: list(error.absolute_path),
    )
    if errors:
        first = errors[0]
        location = "$" + "".join(f"[{part!r}]" for part in first.absolute_path)
        _fail(f"{label} schema failure at {location}: {first.message}")


def _project_provider_response_schema(node: Any) -> Any:
    """Remove local-only assertions from the Codex/OpenAI response schema."""
    if not isinstance(node, dict):
        _fail("provider response schema source node must be an object")
    projected: dict[str, Any] = {}
    for key, value in node.items():
        if key in PROVIDER_SCHEMA_STRIPPED_KEYWORDS:
            continue
        if key == "properties":
            if not isinstance(value, dict):
                _fail("provider response schema properties must be an object")
            projected[key] = {
                name: _project_provider_response_schema(child)
                for name, child in value.items()
            }
        elif key == "items":
            projected[key] = _project_provider_response_schema(value)
        else:
            projected[key] = value
    return projected


def _validate_provider_response_schema(node: Any, path: str = "$") -> None:
    """Pin the strict response-schema subset required by Codex/OpenAI."""
    if not isinstance(node, dict):
        _fail(f"provider response schema node must be an object at {path}")
    unsupported = set(node) - PROVIDER_SCHEMA_ALLOWED_KEYWORDS
    if unsupported:
        _fail(
            f"provider response schema has unsupported keywords at {path}: "
            f"{sorted(unsupported)}"
        )
    if ("const" in node or "enum" in node) and "type" not in node:
        _fail(f"provider response schema requires explicit type at {path}")
    if node.get("type") == "object":
        properties = node.get("properties")
        required = node.get("required")
        if not isinstance(properties, dict) or node.get("additionalProperties") is not False:
            _fail(f"provider response object must be closed at {path}")
        if not isinstance(required, list) or set(required) != set(properties):
            _fail(f"provider response object must require every property at {path}")
        for key, value in properties.items():
            _validate_provider_response_schema(value, f"{path}.properties[{key!r}]")
    if "items" in node:
        _validate_provider_response_schema(node["items"], f"{path}.items")


def _repo_ref(ref: str) -> Path:
    if not isinstance(ref, str) or not ref or ref.startswith("/") or "\\" in ref:
        _fail(f"invalid repository reference: {ref!r}")
    if any(part in {"", ".", ".."} for part in ref.split("/")):
        _fail(f"invalid repository reference: {ref!r}")
    return REPO_ROOT / ref


def _validate_lock() -> dict[str, str]:
    lock, _ = _load_json(LOCK_PATH)
    if set(lock) != {"schema_version", "suite", "assets"}:
        _fail("suite_lock.json must be the closed three-field object")
    if lock["schema_version"] != "review-criteria-suite-lock/1.0" or lock["suite"] != SUITE:
        _fail("suite_lock.json identity mismatch")
    assets = lock["assets"]
    if not isinstance(assets, dict) or set(assets) != LOCKED_ASSET_REFS:
        _fail("suite_lock.json must contain the exact closed asset set")
    for ref, digest in assets.items():
        if not isinstance(digest, str) or SHA_RE.fullmatch(digest) is None:
            _fail(f"suite lock digest is invalid for {ref!r}")
        raw = _safe_explicit_file(_repo_ref(ref))
        if _sha(raw) != digest:
            _fail(f"suite lock hash mismatch for {ref}")
    return assets


def _scenario_contexts() -> tuple[list[dict[str, Any]], dict[str, dict[str, Any]], dict[str, Any]]:
    scenarios, _ = _load_json(SCENARIOS_PATH)
    scenario_schema = _schema(SCENARIOS_SCHEMA_PATH)
    declaration_schema = _schema(DECLARATION_SCHEMA_PATH)
    registry = Registry().with_resource(
        declaration_schema["$id"], Resource.from_contents(declaration_schema)
    )
    errors = list(Draft202012Validator(scenario_schema, registry=registry).iter_errors(scenarios))
    if errors:
        _fail(f"scenarios schema failure: {errors[0].message}")
    criteria_registry, _ = _load_json(REGISTRY_PATH)
    validate_registry(criteria_registry)
    contexts: dict[str, dict[str, Any]] = {}
    items = scenarios["items"]
    for item in items:
        contexts[item["item_id"]] = resolve(item["declaration"], criteria_registry)
    return items, contexts, criteria_registry


def validate_assets() -> dict[str, Any]:
    assets = _validate_lock()
    items, contexts, registry = _scenario_contexts()
    skeleton, _ = _load_json(HELDOUT_SET_PATH)
    expected = [
        (item["item_id"], item["consumer_id"], item["role"])
        for item in items
    ]
    declared = [
        (item["item_id"], item["consumer"], item["role"])
        for item in skeleton.get("items", [])
    ]
    if declared != expected:
        _fail("heldout_set.json identity/order does not match scenarios.json")

    plan, _ = _load_json(CALL_PLAN_PATH)
    if set(plan) != {
        "schema_version",
        "suite",
        "design",
        "content_class",
        "api_spend_ceiling_usd",
        "transport",
        "calls",
    }:
        _fail("call_plan.json has an open or incomplete root")
    if (
        plan["schema_version"] != "review-criteria-call-plan/1.0"
        or plan["suite"] != SUITE
        or plan["content_class"] != "repository_owned_synthetic"
        or plan["api_spend_ceiling_usd"] != 0
        or plan["transport"] != "codex_chatgpt_subscription"
    ):
        _fail("call_plan.json identity/transport/spend policy mismatch")
    calls = plan["calls"]
    if not isinstance(calls, list) or len(calls) != 24:
        _fail("call plan must contain exactly 24 calls")
    item_ids = [item[0] for item in expected]
    seen: set[tuple[str, str, int]] = set()
    for index, call in enumerate(calls, 1):
        if not isinstance(call, dict) or set(call) != {
            "sequence_index", "call_id", "item_id", "arm", "replicate"
        }:
            _fail(f"call_plan.calls[{index - 1}] is not closed")
        if call["sequence_index"] != index:
            _fail("call plan sequence indices must be contiguous from 1")
        key = (call["item_id"], call["arm"], call["replicate"])
        if (
            call["item_id"] not in item_ids
            or call["arm"] not in {"baseline", "treatment"}
            or type(call["replicate"]) is not int
            or call["replicate"] not in {1, 2}
            or key in seen
        ):
            _fail(f"call plan contains invalid/duplicate cell: {key!r}")
        expected_id = f"{call['item_id']}-{call['arm']}-r{call['replicate']}"
        if call["call_id"] != expected_id:
            _fail(f"call id does not bind its design cell: {call['call_id']!r}")
        seen.add(key)
    full = {(item, arm, rep) for item in item_ids for arm in ("baseline", "treatment") for rep in (1, 2)}
    if seen != full:
        _fail("call plan does not cover the exact 6 x 2 x 2 design")
    for offset, item_id in enumerate(item_ids):
        arms = [call["arm"] for call in calls[offset * 4:(offset + 1) * 4]
                if call["item_id"] == item_id]
        expected_arms = ["baseline", "treatment", "treatment", "baseline"]
        if offset % 2:
            expected_arms = ["treatment", "baseline", "baseline", "treatment"]
        if arms != expected_arms:
            _fail(f"call plan balance drift for {item_id}")

    for schema_path in (
        OUTPUT_SCHEMA_PATH,
        EXPERT_PACKET_SCHEMA_PATH,
        EXPERT_LABELS_SCHEMA_PATH,
        DECISIONS_SCHEMA_PATH,
        PAIRED_SCHEMA_PATH,
        EXECUTION_SCHEMA_PATH,
    ):
        _schema(schema_path)
    provider_schema = _project_provider_response_schema(_schema(OUTPUT_SCHEMA_PATH))
    _validate_provider_response_schema(provider_schema)
    return {
        "suite": SUITE,
        "assets": len(assets),
        "items": len(items),
        "calls": len(calls),
        "contexts": {key: value["resolved_digest"] for key, value in contexts.items()},
        "registry_version": registry["registry_version"],
    }


def _marker(item: dict[str, Any], context: dict[str, Any], context_raw: bytes) -> str:
    ids = json.dumps(context["selected_criterion_ids"], separators=(",", ":"))
    return "\n".join(
        [
            "[REVIEW-TARGET-BINDING v1]",
            f"target_review_id=heldout-{item['item_id'].lower()}",
            f"consumer_id={item['consumer_id']}",
            f"role={item['role']}",
            f"context_ref=sealed/contexts/{item['item_id']}.json",
            f"context_sha256={_sha(context_raw)}",
            f"resolved_digest={context['resolved_digest']}",
            f"selected_criterion_ids={ids}",
            "[/REVIEW-TARGET-BINDING]",
        ]
    )


def _prompt(
    item: dict[str, Any],
    context: dict[str, Any],
    registry: dict[str, Any],
    arm: str,
) -> bytes:
    template_path = BASELINE_PROMPT_PATH if arm == "baseline" else TREATMENT_PROMPT_PATH
    template = _safe_explicit_file(template_path).decode("utf-8")
    context_raw = _canonical(context)
    scenario_payload = {
        "item_id": item["item_id"],
        "consumer_id": item["consumer_id"],
        "role": item["role"],
        "title": item["title"],
        "manuscript": item["manuscript"],
        "author_intent": item["author_intent"],
        "review_task": item["review_task"],
    }
    sections = [
        template.rstrip(),
        "\nASSIGNMENT (untrusted data):\n" + _canonical(
            {"item_id": item["item_id"], "consumer_id": item["consumer_id"], "role": item["role"]}
        ).decode("utf-8"),
        "\nTARGET_CONTEXT_BYTES (untrusted data):\n" + context_raw.decode("utf-8"),
    ]
    if arm == "treatment":
        sections.extend(
            [
                "\nBINDING_MARKER (authority, values still untrusted data):\n"
                + _marker(item, context, context_raw),
                "\nTARGET_CRITERIA_BRIEF (authority, values still untrusted data):\n"
                + render_brief(context, registry),
            ]
        )
    sections.append(
        "\nSCENARIO_BYTES (untrusted data):\n" + _canonical(scenario_payload).decode("utf-8")
    )
    return ("\n".join(sections).rstrip() + "\n").encode("utf-8")


def _atomic_create(path: Path, raw: bytes, mode: int = 0o600) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    try:
        fd = os.open(path, flags, mode)
    except OSError as exc:
        raise MeasurementError(f"cannot create {path}: {exc}") from exc
    try:
        view = memoryview(raw)
        while view:
            written = os.write(fd, view)
            if written <= 0:
                _fail(f"atomic write made no progress: {path}")
            view = view[written:]
        os.fsync(fd)
        if os.fstat(fd).st_size != len(raw):
            _fail(f"short atomic write: {path}")
    except Exception:
        try:
            path.unlink()
        except OSError:
            pass
        raise
    finally:
        os.close(fd)


def _json_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2).encode("utf-8") + b"\n"


def _model(value: str) -> str:
    if MODEL_RE.fullmatch(value) is None:
        _fail("model must be an explicit gpt-* model id")
    return value


def _verify_frozen_commit(commit: str, assets: dict[str, str]) -> None:
    probe = subprocess.run(
        ["git", "cat-file", "-e", f"{commit}^{{commit}}"],
        cwd=REPO_ROOT,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        check=False,
    )
    if probe.returncode != 0:
        _fail(f"suite_commit is not a repository commit: {commit}")
    ancestor = subprocess.run(
        ["git", "merge-base", "--is-ancestor", commit, "origin/main"],
        cwd=REPO_ROOT,
        stdin=subprocess.DEVNULL,
        capture_output=True,
        check=False,
    )
    if ancestor.returncode != 0:
        _fail("suite_commit must already be on local origin/main history")
    for ref, expected in assets.items():
        shown = subprocess.run(
            ["git", "show", f"{commit}:{ref}"],
            cwd=REPO_ROOT,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=False,
        )
        if shown.returncode != 0 or _sha(shown.stdout) != expected:
            _fail(f"suite_commit does not contain the locked asset bytes: {ref}")


def init_run(args: argparse.Namespace) -> dict[str, Any]:
    validate_assets()
    assets = _validate_lock()
    model = _model(args.model)
    if COMMIT_RE.fullmatch(args.suite_commit) is None:
        _fail("suite_commit must be exactly 40 lowercase hexadecimal characters")
    _verify_frozen_commit(args.suite_commit, assets)
    if args.reasoning_effort not in {"low", "medium", "high", "xhigh"}:
        _fail("reasoning_effort must be low, medium, high, or xhigh")
    if args.input_token_cap < 1 or args.output_token_cap < 1:
        _fail("token caps must be positive integers")
    if not re.fullmatch(r"\d+\.\d+\.\d+", args.codex_version):
        _fail("codex_version must be an exact dotted version")
    run_dir = args.run_dir.resolve()
    if run_dir.exists():
        _fail(f"run directory already exists: {run_dir}")
    run_dir.mkdir(parents=True, mode=0o700)

    items, contexts, registry = _scenario_contexts()
    by_id = {item["item_id"]: item for item in items}
    call_plan, call_plan_raw = _load_json(CALL_PLAN_PATH)
    calls: list[dict[str, Any]] = []
    for call in call_plan["calls"]:
        prompt = _prompt(by_id[call["item_id"]], contexts[call["item_id"]], registry, call["arm"])
        if len(prompt) > args.input_token_cap * 4:
            _fail(
                f"prompt {call['call_id']} exceeds the conservative local input cap "
                f"({len(prompt)} bytes > {args.input_token_cap * 4})"
            )
        prompt_ref = f"prompts/{call['call_id']}.txt"
        _atomic_create(run_dir / prompt_ref, prompt)
        calls.append(
            {
                **call,
                "prompt_ref": prompt_ref,
                "prompt_sha256": _sha(prompt),
                "output_ref": f"outputs/{call['call_id']}.json",
                "events_ref": f"events/{call['call_id']}.jsonl",
                "receipt_ref": f"receipts/{call['call_id']}.json",
            }
        )
    lock_raw = _safe_explicit_file(LOCK_PATH)
    run_plan = {
        "schema_version": RUN_PLAN_VERSION,
        "suite": SUITE,
        "suite_commit": args.suite_commit,
        "content_class": "repository_owned_synthetic",
        "transport": "codex_chatgpt_subscription",
        "auth_mode": "chatgpt_subscription",
        "api_spend_ceiling_usd": 0,
        "codex_version": args.codex_version,
        "model_id": model,
        "reasoning_effort": args.reasoning_effort,
        "sampling": "provider_managed_not_exposed",
        "input_token_cap": args.input_token_cap,
        "output_token_cap": args.output_token_cap,
        "tools": [],
        "isolation": {
            "ephemeral_auth_home": True,
            "empty_working_root": True,
            "ignore_user_config": True,
            "local_tools_disabled": True,
            "web_disabled": True,
            "forbidden_event_scan": True,
        },
        "suite_lock_sha256": _sha(lock_raw),
        "call_plan_sha256": _sha(call_plan_raw),
        "calls": calls,
    }
    _validate_run_plan(run_plan)
    _atomic_create(run_dir / "run-plan.json", _json_bytes(run_plan))
    return {
        "run_plan": str(run_dir / "run-plan.json"),
        "run_plan_sha256": _sha(_safe_explicit_file(run_dir / "run-plan.json")),
        "calls": 24,
        "model_id": model,
        "api_spend_ceiling_usd": 0,
    }


def _codex_home(environ: dict[str, str]) -> Path:
    if environ.get("CODEX_HOME"):
        return Path(environ["CODEX_HOME"]).expanduser().resolve()
    if not environ.get("HOME"):
        _fail("HOME is unavailable")
    return (Path(environ["HOME"]).expanduser() / ".codex").resolve()


def _feature_names(raw: str) -> set[str]:
    names = {
        parts[0]
        for line in raw.splitlines()
        if (
            (parts := line.split())
            and len(parts) >= 3
            and FEATURE_NAME_RE.fullmatch(parts[0]) is not None
            and parts[-1] in {"true", "false"}
        )
    }
    if not names:
        raise ValueError("empty or malformed Codex feature registry")
    return names


def detect(model: str, environ: dict[str, str] | None = None) -> dict[str, Any]:
    _model(model)
    env = dict(os.environ if environ is None else environ)
    codex = shutil.which("codex", path=env.get("PATH"))
    result: dict[str, Any] = {
        "transport": "codex_chatgpt_subscription",
        "model_id": model,
        "available": False,
        "auth_mode": None,
        "reason_code": None,
    }
    if not codex:
        result["reason_code"] = "CODEX_CLI_MISSING"
        return result
    auth_path = _codex_home(env) / "auth.json"
    try:
        auth_raw = _safe_explicit_file(auth_path, limit=1024 * 1024)
        if not isinstance(_strict_loads(auth_raw), dict):
            raise ValueError("auth root is not an object")
    except (MeasurementError, UnicodeError, ValueError, json.JSONDecodeError):
        result["reason_code"] = "SUBSCRIPTION_AUTH_INVALID"
        return result
    status_env = {
        "PATH": env.get("PATH", os.defpath),
        "CODEX_HOME": str(_codex_home(env)),
        "HOME": env.get("HOME", str(_codex_home(env).parent)),
        "LANG": "C",
        "LC_ALL": "C",
        "NO_COLOR": "1",
    }
    try:
        version_run = subprocess.run(
            [codex, "--version"], env=status_env, stdin=subprocess.DEVNULL,
            capture_output=True, text=True, timeout=10, check=False,
        )
        status_run = subprocess.run(
            [codex, "login", "status"], env=status_env, stdin=subprocess.DEVNULL,
            capture_output=True, text=True, timeout=10, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        result["reason_code"] = "CODEX_STATUS_UNAVAILABLE"
        return result
    match = VERSION_RE.search(version_run.stdout)
    if version_run.returncode or match is None:
        result["reason_code"] = "CODEX_VERSION_UNAVAILABLE"
        return result
    version = tuple(int(value) for value in match.groups())
    if version < MIN_CODEX_VERSION:
        result["reason_code"] = "CODEX_VERSION_TOO_OLD"
        return result
    status_lines = {
        line.strip()
        for line in (status_run.stdout + "\n" + status_run.stderr).splitlines()
        if line.strip()
    }
    if status_run.returncode or "Logged in using ChatGPT" not in status_lines:
        result["reason_code"] = "AUTH_NOT_CHATGPT_SUBSCRIPTION"
        return result
    try:
        features_run = subprocess.run(
            [codex, "features", "list"], env=status_env, stdin=subprocess.DEVNULL,
            capture_output=True, text=True, timeout=10, check=False,
        )
    except (OSError, subprocess.TimeoutExpired):
        result["reason_code"] = "CODEX_FEATURES_UNAVAILABLE"
        return result
    if features_run.returncode:
        result["reason_code"] = "CODEX_FEATURES_UNAVAILABLE"
        return result
    try:
        feature_names = _feature_names(features_run.stdout)
    except ValueError:
        result["reason_code"] = "CODEX_FEATURES_UNAVAILABLE"
        return result
    unsupported = sorted(set(DISABLED_FEATURES) - feature_names)
    if unsupported:
        result["reason_code"] = "CODEX_FEATURE_FLAGS_INCOMPATIBLE"
        result["unsupported_feature_flags"] = unsupported
        return result
    result.update(
        available=True,
        auth_mode="chatgpt_subscription",
        codex_version=".".join(str(value) for value in version),
    )
    return result


def _child_command(codex: str, plan: dict[str, Any], output: Path, schema: Path, work: Path) -> list[str]:
    command = [
        codex,
        "exec",
        "--strict-config",
        "--ephemeral",
        "--ignore-user-config",
        "--ignore-rules",
        "--skip-git-repo-check",
        "--sandbox",
        "read-only",
        "--model",
        plan["model_id"],
        "--cd",
        str(work),
        "--output-schema",
        str(schema),
        "--output-last-message",
        str(output),
        "--json",
        "-c",
        f'model_reasoning_effort="{plan["reasoning_effort"]}"',
        "-c",
        'web_search="disabled"',
        "-c",
        "mcp_servers={}",
        "-c",
        "analytics.enabled=false",
    ]
    for feature in DISABLED_FEATURES:
        command.extend(("--disable", feature))
    command.append("-")
    return command


def _scan_events(raw: bytes) -> None:
    if len(raw) > MAX_EVENT_BYTES:
        _fail("Codex event stream exceeds the sealed limit")
    event_count = 0
    for index, line in enumerate(raw.splitlines()):
        if not line:
            continue
        event_count += 1
        try:
            event = _strict_loads(line)
        except (UnicodeError, ValueError, json.JSONDecodeError) as exc:
            raise MeasurementError(f"malformed Codex event line {index + 1}: {exc}") from exc
        if not isinstance(event, dict):
            _fail(f"Codex event line {index + 1} is not an object")
        event_type = event.get("type")
        if event_type in {"error", "turn.failed"}:
            _fail(f"Codex emitted failure event {event_type!r}")
        item = event.get("item")
        if isinstance(item, dict):
            item_type = item.get("type")
            folded = str(item_type).casefold().replace("-", "_")
            if any(token in folded for token in FORBIDDEN_EVENT_ITEM_TOKENS):
                _fail(f"Codex emitted forbidden tool event item {item_type!r}")
    if event_count == 0:
        _fail("Codex event stream is empty")


def _validate_subject_output(
    value: dict[str, Any], item: dict[str, Any], context: dict[str, Any]
) -> None:
    _validate(OUTPUT_SCHEMA_PATH, value, "subject output")
    for field, expected in (
        ("item_id", item["item_id"]),
        ("consumer_id", item["consumer_id"]),
        ("role", item["role"]),
    ):
        if value[field] != expected:
            _fail(f"subject output {field} does not match the sealed assignment")
    selected = context["selected_criterion_ids"]
    applicability_ids = [row["criterion_id"] for row in value["applicability"]]
    if applicability_ids != selected:
        _fail("subject output applicability must cover selected criterion ids in order")
    finding_ids: set[str] = set()
    for finding in value["findings"]:
        if finding["finding_id"] in finding_ids:
            _fail("subject output contains duplicate finding_id")
        finding_ids.add(finding["finding_id"])
        if not set(finding["criterion_ids"]).issubset(set(selected)):
            _fail("subject output finding names an unselected criterion")
        remedy = finding["remedy"]
        if remedy["status"] == "none":
            expected = {
                "minimum_action": None,
                "effort_scope": "none",
                "changes_research_intent": "not_applicable",
                "requires_new_data": False,
            }
            if any(remedy[key] != expected_value for key, expected_value in expected.items()):
                _fail("no-remedy subject output has contradictory action fields")
            if remedy["no_honest_reason"] is None:
                _fail("no-remedy subject output requires no_honest_reason")
        else:
            if remedy["minimum_action"] is None or remedy["effort_scope"] == "none":
                _fail("available remedy requires an action and non-none effort scope")
            if remedy["no_honest_reason"] is not None:
                _fail("available remedy cannot carry no_honest_reason")
        if remedy["effort_scope"] == "new_data" and remedy["requires_new_data"] is not True:
            _fail("new_data remedy must declare requires_new_data=true")


def _rfc3339_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat().replace("+00:00", "Z")


def _copy_auth(source: Path, target: Path) -> None:
    raw = _safe_explicit_file(source, limit=1024 * 1024)
    if not isinstance(_strict_loads(raw), dict):
        _fail("Codex subscription auth root must be an object")
    _atomic_create(target, raw)


def _retain_blocked_io(
    run_dir: Path,
    call_id: str,
    stdout: bytes | None,
    stderr: bytes | None,
    output_path: Path | None,
) -> None:
    blocked_root = run_dir / "blocked"
    for suffix, raw, limit in (
        ("stdout.jsonl", stdout, MAX_EVENT_BYTES),
        ("stderr.txt", stderr, 1024 * 1024),
    ):
        if not raw:
            continue
        if len(raw) <= limit:
            _atomic_create(blocked_root / f"{call_id}.{suffix}", raw)
        else:
            _atomic_create(
                blocked_root / f"{call_id}.{suffix}.oversize.json",
                _json_bytes(
                    {
                        "retained": False,
                        "size_bytes": len(raw),
                        "sha256": _sha(raw),
                        "reason": "exceeds sealed retention cap",
                    }
                ),
            )
    if output_path is None or not output_path.exists():
        return
    try:
        output_raw = _safe_explicit_file(output_path, limit=MAX_OUTPUT_BYTES)
    except MeasurementError as exc:
        _atomic_create(
            blocked_root / f"{call_id}.output-unavailable.json",
            _json_bytes({"retained": False, "reason": str(exc)}),
        )
    else:
        _atomic_create(blocked_root / f"{call_id}.output.raw", output_raw)


def _run_one(
    plan: dict[str, Any], call: dict[str, Any], run_dir: Path, environ: dict[str, str]
) -> dict[str, Any]:
    codex = shutil.which("codex", path=environ.get("PATH"))
    if not codex:
        _fail("Codex CLI disappeared after detection")
    prompt_path = run_dir / call["prompt_ref"]
    prompt = _safe_explicit_file(prompt_path)
    if _sha(prompt) != call["prompt_sha256"]:
        _fail(f"prompt hash drift for {call['call_id']}")
    if len(prompt) > plan["input_token_cap"] * 4:
        _fail(f"prompt exceeds local cap for {call['call_id']}")
    started = _rfc3339_now()
    with tempfile.TemporaryDirectory(prefix="ars-rcv-subject-") as temp_name:
        # macOS returns /var/... while /var is a platform symlink to /private/var.
        # Canonicalize this runner-created root once; caller paths remain no-follow.
        temp = Path(temp_name).resolve()
        os.chmod(temp, 0o700)
        child_home = temp / "codex-home"
        work = temp / "work"
        child_home.mkdir(mode=0o700)
        work.mkdir(mode=0o700)
        schema = temp / "subject-output.schema.json"
        provider_schema = _project_provider_response_schema(_schema(OUTPUT_SCHEMA_PATH))
        _validate_provider_response_schema(provider_schema)
        _atomic_create(schema, _json_bytes(provider_schema))
        _copy_auth(_codex_home(environ) / "auth.json", child_home / "auth.json")
        output = temp / "last-message.json"
        child_env = {
            "PATH": environ.get("PATH", os.defpath),
            "CODEX_HOME": str(child_home),
            "HOME": str(temp),
            "TMPDIR": str(temp),
            "LANG": "C",
            "LC_ALL": "C",
            "NO_COLOR": "1",
        }
        command = _child_command(codex, plan, output, schema, work)
        try:
            completed = subprocess.run(
                command,
                input=prompt,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                env=child_env,
                cwd=work,
                timeout=1800,
                check=False,
            )
        except subprocess.TimeoutExpired as exc:
            _retain_blocked_io(run_dir, call["call_id"], exc.stdout, exc.stderr, output)
            raise MeasurementError(
                f"subscription CLI timed out for {call['call_id']}"
            ) from exc
        except OSError as exc:
            raise MeasurementError(
                f"subscription CLI failed to start for {call['call_id']}: {exc}"
            ) from exc
        try:
            if completed.returncode != 0:
                _fail(
                    f"subscription CLI exited {completed.returncode} for {call['call_id']}"
                )
            _scan_events(completed.stdout)
            output_raw = _safe_explicit_file(
                output,
                limit=min(MAX_OUTPUT_BYTES, plan["output_token_cap"] * 8),
            )
            try:
                output_value = _strict_loads(output_raw)
            except (UnicodeError, ValueError, json.JSONDecodeError) as exc:
                raise MeasurementError(
                    f"invalid subject JSON for {call['call_id']}: {exc}"
                ) from exc
            if not isinstance(output_value, dict):
                _fail(f"subject output root is not an object for {call['call_id']}")
            items, contexts, _registry = _scenario_contexts()
            by_id = {item["item_id"]: item for item in items}
            _validate_subject_output(
                output_value,
                by_id[call["item_id"]],
                contexts[call["item_id"]],
            )
        except MeasurementError:
            _retain_blocked_io(
                run_dir,
                call["call_id"],
                completed.stdout,
                completed.stderr,
                output,
            )
            raise
        completed_at = _rfc3339_now()
        _atomic_create(run_dir / call["events_ref"], completed.stdout)
        normalized_output = _json_bytes(output_value)
        _atomic_create(run_dir / call["output_ref"], normalized_output)
        receipt = {
            "schema_version": RECEIPT_VERSION,
            "call_id": call["call_id"],
            "sequence_index": call["sequence_index"],
            "item_id": call["item_id"],
            "arm": call["arm"],
            "replicate": call["replicate"],
            "transport": "codex_chatgpt_subscription",
            "auth_mode": "chatgpt_subscription",
            "model_id": plan["model_id"],
            "codex_version": plan["codex_version"],
            "reasoning_effort": plan["reasoning_effort"],
            "started_at": started,
            "completed_at": completed_at,
            "prompt_sha256": call["prompt_sha256"],
            "output_sha256": _sha(normalized_output),
            "events_sha256": _sha(completed.stdout),
            "api_spend_usd": 0,
            "tools_observed": [],
        }
        _atomic_create(run_dir / call["receipt_ref"], _json_bytes(receipt))
        return receipt


def _load_receipt(plan: dict[str, Any], call: dict[str, Any], run_dir: Path) -> dict[str, Any]:
    receipt, _ = _load_json(run_dir / call["receipt_ref"])
    required = {
        "schema_version", "call_id", "sequence_index", "item_id", "arm", "replicate",
        "transport", "auth_mode", "model_id", "codex_version", "reasoning_effort",
        "started_at", "completed_at", "prompt_sha256", "output_sha256",
        "events_sha256", "api_spend_usd", "tools_observed",
    }
    if set(receipt) != required or receipt["schema_version"] != RECEIPT_VERSION:
        _fail(f"receipt is open or malformed: {call['call_id']}")
    for field in ("call_id", "sequence_index", "item_id", "arm", "replicate", "prompt_sha256"):
        if receipt[field] != call[field]:
            _fail(f"receipt {field} mismatch: {call['call_id']}")
    if (
        receipt["transport"] != "codex_chatgpt_subscription"
        or receipt["auth_mode"] != "chatgpt_subscription"
        or receipt["model_id"] != plan["model_id"]
        or receipt["codex_version"] != plan["codex_version"]
        or receipt["reasoning_effort"] != plan["reasoning_effort"]
        or receipt["api_spend_usd"] != 0
        or receipt["tools_observed"] != []
    ):
        _fail(f"receipt transport/config mismatch: {call['call_id']}")
    output_raw = _safe_explicit_file(run_dir / call["output_ref"])
    events_raw = _safe_explicit_file(run_dir / call["events_ref"])
    if _sha(output_raw) != receipt["output_sha256"] or _sha(events_raw) != receipt["events_sha256"]:
        _fail(f"receipt artifact hash mismatch: {call['call_id']}")
    _scan_events(events_raw)
    return receipt


def _validate_run_plan(plan: dict[str, Any]) -> None:
    required = {
        "schema_version", "suite", "suite_commit", "content_class", "transport",
        "auth_mode", "api_spend_ceiling_usd", "codex_version", "model_id",
        "reasoning_effort", "sampling", "input_token_cap", "output_token_cap",
        "tools", "isolation", "suite_lock_sha256", "call_plan_sha256", "calls",
    }
    if set(plan) != required:
        _fail("run plan is open or incomplete")
    if (
        plan["schema_version"] != RUN_PLAN_VERSION
        or plan["suite"] != SUITE
        or COMMIT_RE.fullmatch(plan["suite_commit"]) is None
        or plan["content_class"] != "repository_owned_synthetic"
        or plan["transport"] != "codex_chatgpt_subscription"
        or plan["auth_mode"] != "chatgpt_subscription"
        or plan["api_spend_ceiling_usd"] != 0
        or MODEL_RE.fullmatch(plan["model_id"]) is None
        or plan["reasoning_effort"] not in {"low", "medium", "high", "xhigh"}
        or plan["sampling"] != "provider_managed_not_exposed"
        or type(plan["input_token_cap"]) is not int
        or type(plan["output_token_cap"]) is not int
        or plan["input_token_cap"] < 1
        or plan["output_token_cap"] < 1
        or plan["tools"] != []
        or SHA_RE.fullmatch(plan["suite_lock_sha256"]) is None
        or SHA_RE.fullmatch(plan["call_plan_sha256"]) is None
    ):
        _fail("run plan identity/configuration is invalid")
    isolation = plan["isolation"]
    if not isinstance(isolation, dict) or set(isolation) != {
        "ephemeral_auth_home", "empty_working_root", "ignore_user_config",
        "local_tools_disabled", "web_disabled", "forbidden_event_scan",
    } or any(value is not True for value in isolation.values()):
        _fail("run plan isolation attestations must be the exact all-true set")
    calls = plan["calls"]
    if not isinstance(calls, list) or len(calls) != 24:
        _fail("run plan must contain exactly 24 calls")
    expected_call_keys = {
        "sequence_index", "call_id", "item_id", "arm", "replicate", "prompt_ref",
        "prompt_sha256", "output_ref", "events_ref", "receipt_ref",
    }
    frozen_plan, _ = _load_json(CALL_PLAN_PATH)
    for index, (call, frozen_call) in enumerate(zip(calls, frozen_plan["calls"]), 1):
        if not isinstance(call, dict) or set(call) != expected_call_keys:
            _fail(f"run plan call {index} is open or incomplete")
        if call["sequence_index"] != index or SHA_RE.fullmatch(call["prompt_sha256"]) is None:
            _fail(f"run plan call {index} sequence/hash is invalid")
        for field in ("sequence_index", "call_id", "item_id", "arm", "replicate"):
            if call[field] != frozen_call[field]:
                _fail(f"run plan call {index} drifts from call_plan.json at {field}")
        expected_refs = {
            "prompt_ref": f"prompts/{call['call_id']}.txt",
            "output_ref": f"outputs/{call['call_id']}.json",
            "events_ref": f"events/{call['call_id']}.jsonl",
            "receipt_ref": f"receipts/{call['call_id']}.json",
        }
        if any(call[field] != value for field, value in expected_refs.items()):
            _fail(f"run plan call {index} has a noncanonical artifact reference")


def _validate_plan_authority(plan: dict[str, Any]) -> None:
    """Bind a persisted run plan back to the exact locked main-history suite."""
    _validate_run_plan(plan)
    assets = _validate_lock()
    if _sha(_safe_explicit_file(LOCK_PATH)) != plan["suite_lock_sha256"]:
        _fail("run plan suite_lock_sha256 no longer matches the frozen assets")
    if _sha(_safe_explicit_file(CALL_PLAN_PATH)) != plan["call_plan_sha256"]:
        _fail("run plan call_plan_sha256 no longer matches the exact 24-call plan")
    _verify_frozen_commit(plan["suite_commit"], assets)


def dispatch(args: argparse.Namespace, environ: dict[str, str] | None = None) -> dict[str, Any]:
    if not args.execute_24_subscription_calls:
        _fail("dispatch requires --execute-24-subscription-calls")
    validate_assets()
    env = dict(os.environ if environ is None else environ)
    run_dir = args.run_dir.resolve()
    plan_path = run_dir / "run-plan.json"
    plan, plan_raw = _load_json(plan_path)
    if args.plan_sha256 != _sha(plan_raw) or SHA_RE.fullmatch(args.plan_sha256) is None:
        _fail("--plan-sha256 does not match the frozen run-plan bytes")
    _validate_plan_authority(plan)
    detection = detect(plan["model_id"], env)
    if not detection["available"]:
        _fail(f"subscription transport unavailable: {detection['reason_code']}")
    if detection["codex_version"] != plan["codex_version"]:
        _fail("detected Codex version differs from the frozen run plan")
    receipts: list[dict[str, Any]] = []
    for call in plan["calls"]:
        receipt_path = run_dir / call["receipt_ref"]
        blocked_path = run_dir / "blocked" / f"{call['call_id']}.json"
        if blocked_path.exists():
            _fail(
                f"call {call['call_id']} is already recorded blocked; this plan "
                "does not authorize a retry"
            )
        if receipt_path.exists():
            receipts.append(_load_receipt(plan, call, run_dir))
            continue
        orphaned = [
            ref for ref in (call["output_ref"], call["events_ref"])
            if (run_dir / ref).exists()
        ]
        if orphaned:
            _fail(
                f"call {call['call_id']} has artifacts without a closed receipt: "
                + ", ".join(orphaned)
            )
        try:
            receipts.append(_run_one(plan, call, run_dir, env))
        except MeasurementError as exc:
            if not blocked_path.exists():
                _atomic_create(
                    blocked_path,
                    _json_bytes(
                        {
                            "schema_version": "review-criteria-blocked-call/1.0",
                            "call_id": call["call_id"],
                            "sequence_index": call["sequence_index"],
                            "reason": str(exc),
                            "partial_published": True,
                            "api_spend_usd": 0,
                        }
                    ),
                )
            raise
    manifest = {
        "schema_version": "heldout-execution-manifest/1.0",
        "suite": SUITE,
        "created_at": receipts[0]["started_at"],
        "write_once": True,
        "execution_window": {
            "window_id": f"{SUITE}-subscription-window",
            "started_at": receipts[0]["started_at"],
            "completed_at": receipts[-1]["completed_at"],
        },
        "calls": [
            {
                "call_id": receipt["call_id"],
                "sequence_index": receipt["sequence_index"],
                "started_at": receipt["started_at"],
                "completed_at": receipt["completed_at"],
                "prompt_sha256": receipt["prompt_sha256"],
                "output_sha256": receipt["output_sha256"],
                "concurrency_group": None,
                "attempt": 1,
            }
            for receipt in receipts
        ],
    }
    _validate(EXECUTION_SCHEMA_PATH, manifest, "execution manifest")
    manifest_path = run_dir / "execution-manifest.json"
    if manifest_path.exists():
        existing, existing_raw = _load_json(manifest_path)
        if existing != manifest:
            _fail("write-once execution manifest conflicts with completed receipts")
        manifest_raw = existing_raw
    else:
        manifest_raw = _json_bytes(manifest)
        _atomic_create(manifest_path, manifest_raw)
    return {
        "completed_calls": len(receipts),
        "execution_manifest": str(manifest_path),
        "execution_manifest_sha256": _sha(manifest_raw),
        "api_spend_usd": 0,
    }


def _complete_outputs(run_dir: Path) -> tuple[dict[str, Any], list[dict[str, Any]], dict[str, dict[str, Any]]]:
    plan, _ = _load_json(run_dir / "run-plan.json")
    _validate_plan_authority(plan)
    items, contexts, _registry = _scenario_contexts()
    by_id = {item["item_id"]: item for item in items}
    outputs = []
    for call in plan["calls"]:
        _load_receipt(plan, call, run_dir)
        output, _ = _load_json(run_dir / call["output_ref"])
        _validate_subject_output(output, by_id[call["item_id"]], contexts[call["item_id"]])
        outputs.append({"call": call, "output": output})
    return plan, outputs, contexts


def prepare_expert_packet(args: argparse.Namespace) -> dict[str, Any]:
    validate_assets()
    run_dir = args.run_dir.resolve()
    plan, outputs, contexts = _complete_outputs(run_dir)
    items, _context_map, _registry = _scenario_contexts()
    by_id = {item["item_id"]: item for item in items}
    blinded: list[dict[str, Any]] = []
    mapping: list[dict[str, Any]] = []
    used: set[str] = set()
    for row in outputs:
        while True:
            blind_id = f"blind-{secrets.token_hex(8)}"
            if blind_id not in used:
                used.add(blind_id)
                break
        call = row["call"]
        item = by_id[call["item_id"]]
        blinded.append(
            {
                "blind_output_id": blind_id,
                "scenario": {
                    "title": item["title"],
                    "manuscript": item["manuscript"],
                    "author_intent": item["author_intent"],
                    "review_task": item["review_task"],
                },
                "target_context": contexts[call["item_id"]],
                "subject_output": row["output"],
            }
        )
        mapping.append(
            {
                "blind_output_id": blind_id,
                "call_id": call["call_id"],
                "item_id": call["item_id"],
                "arm": call["arm"],
                "replicate": call["replicate"],
            }
        )
    blinded.sort(key=lambda row: row["blind_output_id"])
    mapping.sort(key=lambda row: row["blind_output_id"])
    packet = {
        "schema_version": "review-criteria-expert-packet/1.0",
        "suite": SUITE,
        "content_class": "repository_owned_synthetic",
        "blinding": BLINDING,
        "outputs": blinded,
    }
    _validate(EXPERT_PACKET_SCHEMA_PATH, packet, "expert packet")
    packet_raw = _json_bytes(packet)
    packet_path = args.output.resolve()
    map_path = args.arm_map.resolve()
    _atomic_create(packet_path, packet_raw)
    _atomic_create(
        map_path,
        _json_bytes(
            {
                "schema_version": "review-criteria-arm-map/1.0",
                "suite": SUITE,
                "packet_sha256": _sha(packet_raw),
                "run_plan_sha256": _sha(_safe_explicit_file(run_dir / "run-plan.json")),
                "model_id": plan["model_id"],
                "mapping": mapping,
            }
        ),
    )
    return {
        "expert_packet": str(packet_path),
        "expert_packet_sha256": _sha(packet_raw),
        "arm_map": str(map_path),
        "outputs": 24,
    }


def _indexed(rows: list[dict[str, Any]], key: str, label: str) -> dict[str, dict[str, Any]]:
    result: dict[str, dict[str, Any]] = {}
    for row in rows:
        value = row[key]
        if value in result:
            _fail(f"duplicate {key} in {label}: {value}")
        result[value] = row
    return result


def _validate_arm_map(
    arm_map: dict[str, Any], packet_sha: str, plan: dict[str, Any], plan_raw: bytes
) -> dict[str, dict[str, Any]]:
    if set(arm_map) != {
        "schema_version", "suite", "packet_sha256", "run_plan_sha256",
        "model_id", "mapping",
    }:
        _fail("arm map is open or incomplete")
    if (
        arm_map["schema_version"] != "review-criteria-arm-map/1.0"
        or arm_map["suite"] != SUITE
        or arm_map["packet_sha256"] != packet_sha
        or arm_map["run_plan_sha256"] != _sha(plan_raw)
        or arm_map["model_id"] != plan["model_id"]
        or not isinstance(arm_map["mapping"], list)
        or len(arm_map["mapping"]) != 24
    ):
        _fail("arm map identity/hash/model mismatch")
    mapping_index = _indexed(arm_map["mapping"], "blind_output_id", "arm map")
    call_index = _indexed(plan["calls"], "call_id", "run plan")
    if {row.get("call_id") for row in arm_map["mapping"]} != set(call_index):
        _fail("arm map must cover every run-plan call exactly once")
    for blind_id, mapping in mapping_index.items():
        if set(mapping) != {"blind_output_id", "call_id", "item_id", "arm", "replicate"}:
            _fail(f"arm map row is open or incomplete: {blind_id}")
        call = call_index.get(mapping["call_id"])
        if call is None or any(
            mapping[field] != call[field] for field in ("item_id", "arm", "replicate")
        ):
            _fail(f"arm map row does not match the frozen call: {blind_id}")
    return mapping_index


def _validate_packet_binding(
    packet: dict[str, Any],
    mapping_index: dict[str, dict[str, Any]],
    outputs: list[dict[str, Any]],
    contexts: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    packet_index = _indexed(packet["outputs"], "blind_output_id", "expert packet")
    if set(packet_index) != set(mapping_index):
        _fail("expert packet and arm map must cover the same blind ids")
    call_outputs = {row["call"]["call_id"]: row["output"] for row in outputs}
    items, _contexts, _registry = _scenario_contexts()
    item_index = {item["item_id"]: item for item in items}
    for blind_id, mapping in mapping_index.items():
        item = item_index[mapping["item_id"]]
        expected_scenario = {
            "title": item["title"],
            "manuscript": item["manuscript"],
            "author_intent": item["author_intent"],
            "review_task": item["review_task"],
        }
        packet_row = packet_index[blind_id]
        if packet_row["scenario"] != expected_scenario:
            _fail(f"expert packet scenario drift for {blind_id}")
        if packet_row["target_context"] != contexts[mapping["item_id"]]:
            _fail(f"expert packet target-context drift for {blind_id}")
        if packet_row["subject_output"] != call_outputs[mapping["call_id"]]:
            _fail(f"expert packet subject-output drift for {blind_id}")
    return packet_index


def _validate_label_coverage(packet: dict[str, Any], labels: dict[str, Any]) -> None:
    _validate(EXPERT_LABELS_SCHEMA_PATH, labels, "expert labels")
    output_index = _indexed(packet["outputs"], "blind_output_id", "expert packet")
    label_index = _indexed(labels["labels"], "blind_output_id", "expert labels")
    if set(output_index) != set(label_index):
        _fail("expert labels must cover the exact blinded output ids")
    for blind_id, output_row in output_index.items():
        subject = output_row["subject_output"]
        label = label_index[blind_id]
        predicted_criteria = [row["criterion_id"] for row in subject["applicability"]]
        labelled_criteria = [row["criterion_id"] for row in label["applicability"]]
        if labelled_criteria != predicted_criteria:
            _fail(f"expert applicability coverage/order mismatch for {blind_id}")
        predicted_findings = [row["finding_id"] for row in subject["findings"]]
        labelled_findings = [row["finding_id"] for row in label["findings"]]
        if labelled_findings != predicted_findings:
            _fail(f"expert finding coverage/order mismatch for {blind_id}")


def validate_labels(args: argparse.Namespace) -> dict[str, Any]:
    packet, packet_raw = _load_json(args.packet.resolve())
    _validate(EXPERT_PACKET_SCHEMA_PATH, packet, "expert packet")
    labels, _ = _load_json(args.labels.resolve())
    if labels.get("packet_sha256") != _sha(packet_raw):
        _fail("expert labels packet_sha256 mismatch")
    _validate_label_coverage(packet, labels)
    return {
        "expert_id": labels["expert"]["expert_id"],
        "labels": len(labels["labels"]),
        "packet_sha256": labels["packet_sha256"],
    }


def finalize(args: argparse.Namespace) -> dict[str, Any]:
    validate_assets()
    if len(args.expert_labels) != 2:
        _fail("finalize requires exactly two independent expert-label files")
    run_dir = args.run_dir.resolve()
    plan, outputs, contexts = _complete_outputs(run_dir)
    plan_raw = _safe_explicit_file(run_dir / "run-plan.json")
    packet, packet_raw = _load_json(args.packet.resolve())
    _validate(EXPERT_PACKET_SCHEMA_PATH, packet, "expert packet")
    packet_sha = _sha(packet_raw)
    arm_map, _ = _load_json(args.arm_map.resolve())
    map_index = _validate_arm_map(arm_map, packet_sha, plan, plan_raw)
    packet_index = _validate_packet_binding(packet, map_index, outputs, contexts)

    labels: list[dict[str, Any]] = []
    for path in args.expert_labels:
        value, _ = _load_json(path.resolve())
        if value.get("packet_sha256") != packet_sha:
            _fail("expert labels packet_sha256 mismatch")
        _validate_label_coverage(packet, value)
        labels.append(value)
    expert_ids = [value["expert"]["expert_id"] for value in labels]
    if len({value.casefold() for value in expert_ids}) != 2:
        _fail("expert ids must be distinct")
    decisions, _ = _load_json(args.decisions.resolve())
    _validate(DECISIONS_SCHEMA_PATH, decisions, "adjudication decisions")
    if decisions["packet_sha256"] != packet_sha:
        _fail("adjudication decisions packet_sha256 mismatch")
    decision_index = _indexed(decisions["decisions"], "blind_output_id", "decisions")
    if set(decision_index) != set(packet_index):
        _fail("adjudication decisions must cover the exact expert packet")
    label_indices = [_indexed(value["labels"], "blind_output_id", "expert labels") for value in labels]
    call_outputs = {row["call"]["call_id"]: row["output"] for row in outputs}
    by_item: dict[str, dict[str, Any]] = {}
    for blind_id, mapping in map_index.items():
        item_id = mapping["item_id"]
        by_item.setdefault(
            item_id,
            {
                "item_id": item_id,
                "target_context": {
                    "context_ref": f"sealed/contexts/{item_id}.json",
                    "context_sha256": _sha(_canonical(contexts[item_id])),
                    "resolved_digest": contexts[item_id]["resolved_digest"],
                    "selected_criterion_ids": contexts[item_id]["selected_criterion_ids"],
                },
                "arms": {"baseline": [], "treatment": []},
            },
        )
        subject = call_outputs[mapping["call_id"]]
        raw_labels = [index[blind_id] for index in label_indices]
        decision = decision_index[blind_id]
        if [row["criterion_id"] for row in decision["applicability"]] != [
            row["criterion_id"] for row in subject["applicability"]
        ]:
            _fail(f"decision applicability coverage/order mismatch for {blind_id}")
        if [row["finding_id"] for row in decision["findings"]] != [
            row["finding_id"] for row in subject["findings"]
        ]:
            _fail(f"decision finding coverage/order mismatch for {blind_id}")
        applicability = []
        for index, predicted in enumerate(subject["applicability"]):
            values = [row["applicability"][index]["label"] for row in raw_labels]
            final = decision["applicability"][index]["expert_label"]
            if len(set(values)) == 1 and final != values[0]:
                _fail(f"adjudication overturns unanimous applicability for {blind_id}")
            applicability.append(
                {
                    "criterion_id": predicted["criterion_id"],
                    "predicted": predicted["predicted"],
                    "expert_labels": [
                        {"expert_id": expert_ids[label_index], "label": values[label_index]}
                        for label_index in range(2)
                    ],
                    "expert_label": final,
                }
            )
        findings = []
        for index, predicted in enumerate(subject["findings"]):
            raw_finding = [row["findings"][index] for row in raw_labels]
            final = decision["findings"][index]
            for raw_key, final_key in (
                ("support_label", "support_label"),
                ("severity", "expert_severity"),
                ("venue_alignment", "expert_venue_alignment"),
                ("usefulness", "usefulness"),
            ):
                values = [row[raw_key] for row in raw_finding]
                if len(set(values)) == 1 and final[final_key] != values[0]:
                    _fail(f"adjudication overturns unanimous {raw_key} for {blind_id}")
            findings.append(
                {
                    "finding_id": predicted["finding_id"],
                    "expert_labels": [
                        {
                            "expert_id": expert_ids[label_index],
                            "support_label": raw_finding[label_index]["support_label"],
                            "severity": raw_finding[label_index]["severity"],
                            "venue_alignment": raw_finding[label_index]["venue_alignment"],
                            "usefulness": raw_finding[label_index]["usefulness"],
                        }
                        for label_index in range(2)
                    ],
                    "support_label": final["support_label"],
                    "predicted_severity": predicted["predicted_severity"],
                    "expert_severity": final["expert_severity"],
                    "predicted_venue_alignment": predicted["predicted_venue_alignment"],
                    "expert_venue_alignment": final["expert_venue_alignment"],
                    "usefulness": final["usefulness"],
                }
            )
        by_item[item_id]["arms"][mapping["arm"]].append(
            {
                "replicate_id": mapping["call_id"],
                "profile": subject["profile"],
                "applicability": applicability,
                "findings": findings,
            }
        )
    item_rows = []
    budget = {
        "model_id": plan["model_id"],
        "model_family": "openai",
        "tools": [],
        "sampling": plan["sampling"],
        "input_token_cap": plan["input_token_cap"],
        "output_token_cap": plan["output_token_cap"],
    }
    for item_id in sorted(by_item):
        row = by_item[item_id]
        arms = []
        for arm, mechanism in (("baseline", "pre_684"), ("treatment", "criteria_binding_v1")):
            reps = sorted(row["arms"][arm], key=lambda value: value["replicate_id"])
            arms.append(
                {
                    "arm_id": arm,
                    "mechanism": mechanism,
                    "target_context": row["target_context"],
                    "budget": budget,
                    "replicates": reps,
                }
            )
        item_rows.append(
            {"item_id": item_id, "target_context": row["target_context"], "arms": arms}
        )
    record = {
        "schema_version": "review-criteria-paired-adjudication/1.0",
        "suite": SUITE,
        "subject": {"suite_commit": plan["suite_commit"], **budget, "replicates_per_item": 2},
        "experts": [value["expert"] for value in labels],
        "adjudication": {
            "adjudicator_id": decisions["adjudicator_id"],
            "adjudicator_type": decisions["adjudicator_type"],
            "method": decisions["method"],
            "arm_blind": True,
            "disagreements_retained": True,
        },
        "items": item_rows,
    }
    _validate(PAIRED_SCHEMA_PATH, record, "paired adjudication")
    output_raw = _json_bytes(record)
    _atomic_create(args.output.resolve(), output_raw)
    return {
        "paired_adjudication": str(args.output.resolve()),
        "paired_adjudication_sha256": _sha(output_raw),
        "experts": expert_ids,
        "items": 6,
        "replicates": 24,
    }


def _repo_relative(path: Path, *, under_suite: bool = False) -> str:
    resolved = path.resolve()
    if not resolved.is_relative_to(REPO_ROOT):
        _fail(f"publishable artifact must be inside the repository: {path}")
    if under_suite and not resolved.is_relative_to(SUITE_ROOT.resolve()):
        _fail(f"publishable artifact must be inside the held-out suite: {path}")
    return resolved.relative_to(REPO_ROOT).as_posix()


def _measurement_report_value(
    *,
    plan: dict[str, Any],
    measurement_date: str,
    paired_ref: str,
    paired_sha256: str,
    execution_ref: str,
    execution_sha256: str,
    raw_paths: list[str],
    score: dict[str, Any],
) -> dict[str, Any]:
    plan_ref = MEASUREMENT_PLAN_PATH.relative_to(REPO_ROOT).as_posix()
    rubric_ref = EXPERT_GUIDE_PATH.relative_to(REPO_ROOT).as_posix()
    rubric_sha = _sha(_safe_explicit_file(EXPERT_GUIDE_PATH))
    plan_sha = _sha(_safe_explicit_file(MEASUREMENT_PLAN_PATH))
    return {
        "measurement_contract": "heldout-measurement/1.1",
        "suite": SUITE,
        "suite_class": "paired_controls",
        "measurement_date": measurement_date,
        "decision_relevant": True,
        "subject": {
            "model_id": plan["model_id"],
            "config": {
                "suite_commit": plan["suite_commit"],
                "prompts_ref": (
                    "evals/heldout/review_criteria_constructive_value/"
                    "baseline_prompt.md + treatment_prompt.md + suite_lock.json"
                ),
                "settings": (
                    f"Codex CLI {plan['codex_version']}; reasoning={plan['reasoning_effort']}; "
                    "ephemeral auth home; empty read-only root; local/web tools disabled"
                ),
                "sampling": plan["sampling"],
            },
        },
        "judge_plan": {
            "exception": "human_expert_panel",
            "expert_panel_ref": paired_ref,
            "expert_panel_sha256": paired_sha256,
        },
        "judges": [],
        "aggregate": {
            "headline": {
                "metric_name": "separate_metric_vector_no_composite",
                "value": "see results.suite_specific; composite_score=null",
                "construction_rule": (
                    "All pre-registered metrics and treatment-minus-baseline deltas "
                    "remain separate; no composite or substituted efficacy headline."
                ),
                "estimand_status": "point_estimate",
            },
            "agreement": {
                "rate": None,
                "divergent_items": [],
                "note": (
                    "Model-judge agreement is not applicable. Raw human-expert labels "
                    "and blind resolutions are retained in expert_panel_ref."
                ),
            },
        },
        "replicates": {
            "per_item": 2,
            "rule_ref": f"{plan_ref}#paired-execution",
            "spread": {"treatment_minus_baseline": score["deltas"]},
            "exception": None,
        },
        "adjudication": {
            "applies": True,
            "rubric_ref": rubric_ref,
            "rubric_sha256": rubric_sha,
            "rubric_precommitted": True,
            "blinded_to": ["condition", "mechanism_state", "raw_aggregate"],
            "overrides": [],
            "raw_published": True,
            "resolution_direction": "bidirectional",
            "resolution_rule_ref": (
                f"{rubric_ref} and adjudication_decisions.schema.json"
            ),
        },
        "preregistration": {
            "plan_ref": plan_ref,
            "plan_sha256": plan_sha,
            "rubric_ref": rubric_ref,
            "rubric_sha256": rubric_sha,
            "frozen_commit": plan["suite_commit"],
            "frozen_before_dispatch": True,
            "rubric_and_plan_frozen_together": True,
            "judge_template_version": "review-criteria-human-expert-label/1.0",
            "amendments_append_only": True,
            "amendments": [],
        },
        "execution_manifest": {
            "ref": execution_ref,
            "sha256": execution_sha256,
            "write_once": True,
            "claims": ["ordering"],
        },
        "attempts": {
            "atomicity": (
                "one fresh isolated subscription call per pre-registered design cell; "
                "a blocked cell stops dispatch and this plan authorizes no retry"
            ),
            "partial_published": False,
            "blocked_runs": [],
        },
        "raw_outputs": {"retained": True, "paths": raw_paths},
        "results": {
            "design": "balanced paired-controls measurement",
            "arm_roles": {
                "treatment_or_cohort_arms": ["baseline", "treatment"],
                "variant_packet_arms": [],
            },
            "suite_specific": score,
        },
        "verdict": (
            "Observed synthetic-suite metrics are reported separately for the pinned "
            "subscription model; no general reviewer-superiority claim is made."
        ),
        "caveats": [
            "Repository-owned synthetic scenarios only; results do not establish real-world venue acceptance.",
            "One pinned subject model and two human experts; no cross-model efficacy claim.",
            "Subscription quota was consumed; incremental metered API spend was USD 0.",
        ],
    }


def build_report(args: argparse.Namespace) -> dict[str, Any]:
    validate_assets()
    try:
        dt.date.fromisoformat(args.measurement_date)
    except ValueError as exc:
        raise MeasurementError("measurement_date must be a real ISO date") from exc
    run_dir = args.run_dir.resolve()
    plan, _outputs, _contexts = _complete_outputs(run_dir)
    _validate_run_plan(plan)
    paired_path = args.paired_adjudication.resolve()
    paired, paired_raw = _load_json(paired_path)
    _validate(PAIRED_SCHEMA_PATH, paired, "paired adjudication")
    if (
        paired["subject"]["suite_commit"] != plan["suite_commit"]
        or paired["subject"]["model_id"] != plan["model_id"]
        or paired["subject"]["input_token_cap"] != plan["input_token_cap"]
        or paired["subject"]["output_token_cap"] != plan["output_token_cap"]
    ):
        _fail("paired adjudication subject does not match the frozen run plan")
    score = score_paired_record(paired, paired_raw)
    execution_path = run_dir / "execution-manifest.json"
    execution, execution_raw = _load_json(execution_path)
    _validate(EXECUTION_SCHEMA_PATH, execution, "execution manifest")
    if len(execution["calls"]) != 24:
        _fail("execution manifest must retain all 24 completed calls")
    run_ref = _repo_relative(run_dir, under_suite=True)
    paired_ref = _repo_relative(paired_path, under_suite=True)
    execution_ref = _repo_relative(execution_path, under_suite=True)
    raw_paths = [run_ref]
    if not paired_path.is_relative_to(run_dir):
        raw_paths.append(paired_ref)
    report = _measurement_report_value(
        plan=plan,
        measurement_date=args.measurement_date,
        paired_ref=paired_ref,
        paired_sha256=_sha(paired_raw),
        execution_ref=execution_ref,
        execution_sha256=_sha(execution_raw),
        raw_paths=raw_paths,
        score=score,
    )
    output = args.output.resolve()
    if not output.is_relative_to(SUITE_ROOT.resolve()):
        _fail("measurement report output must be inside the held-out suite")
    errors, _warnings = validate_report(report, resolve_refs=True)
    errors.extend(location_errors(output, report))
    if errors:
        _fail("measurement report validation failed: " + "; ".join(errors))
    report_raw = _json_bytes(report)
    _atomic_create(output, report_raw)
    return {
        "measurement_report": str(output),
        "measurement_report_sha256": _sha(report_raw),
        "expert_panel_sha256": _sha(paired_raw),
        "execution_manifest_sha256": _sha(execution_raw),
        "api_spend_usd": 0,
    }


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("validate-assets")

    detect_parser = sub.add_parser("detect")
    detect_parser.add_argument("--model", required=True)

    init_parser = sub.add_parser("init-run")
    init_parser.add_argument("--run-dir", required=True, type=Path)
    init_parser.add_argument("--suite-commit", required=True)
    init_parser.add_argument("--model", required=True)
    init_parser.add_argument("--codex-version", required=True)
    init_parser.add_argument("--reasoning-effort", default="high")
    init_parser.add_argument("--input-token-cap", type=int, default=12000)
    init_parser.add_argument("--output-token-cap", type=int, default=3000)

    dispatch_parser = sub.add_parser("dispatch")
    dispatch_parser.add_argument("--run-dir", required=True, type=Path)
    dispatch_parser.add_argument("--plan-sha256", required=True)
    dispatch_parser.add_argument("--execute-24-subscription-calls", action="store_true")

    packet_parser = sub.add_parser("prepare-expert-packet")
    packet_parser.add_argument("--run-dir", required=True, type=Path)
    packet_parser.add_argument("--output", required=True, type=Path)
    packet_parser.add_argument("--arm-map", required=True, type=Path)

    labels_parser = sub.add_parser("validate-labels")
    labels_parser.add_argument("--packet", required=True, type=Path)
    labels_parser.add_argument("--labels", required=True, type=Path)

    final_parser = sub.add_parser("finalize")
    final_parser.add_argument("--run-dir", required=True, type=Path)
    final_parser.add_argument("--packet", required=True, type=Path)
    final_parser.add_argument("--arm-map", required=True, type=Path)
    final_parser.add_argument("--expert-labels", action="append", required=True, type=Path)
    final_parser.add_argument("--decisions", required=True, type=Path)
    final_parser.add_argument("--output", required=True, type=Path)

    report_parser = sub.add_parser("build-report")
    report_parser.add_argument("--run-dir", required=True, type=Path)
    report_parser.add_argument("--paired-adjudication", required=True, type=Path)
    report_parser.add_argument("--measurement-date", required=True)
    report_parser.add_argument("--output", required=True, type=Path)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        if args.command == "validate-assets":
            result = validate_assets()
        elif args.command == "detect":
            result = detect(args.model)
        elif args.command == "init-run":
            result = init_run(args)
        elif args.command == "dispatch":
            result = dispatch(args)
        elif args.command == "prepare-expert-packet":
            result = prepare_expert_packet(args)
        elif args.command == "validate-labels":
            result = validate_labels(args)
        elif args.command == "finalize":
            result = finalize(args)
        elif args.command == "build-report":
            result = build_report(args)
        else:  # pragma: no cover
            raise AssertionError(args.command)
    except (MeasurementError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
