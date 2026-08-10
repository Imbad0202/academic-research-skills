from __future__ import annotations

import copy
import hashlib
import inspect
import json
import os
from pathlib import Path
from urllib.parse import quote

import pytest
from jsonschema import Draft202012Validator
from referencing import Registry, Resource

try:
    import build_cross_document_consistency_advisory as runtime
except ModuleNotFoundError:
    from scripts import build_cross_document_consistency_advisory as runtime


REPO = Path(__file__).resolve().parents[1]
FIXTURES = Path(__file__).with_name("fixtures") / "cross_document_consistency"
STAMP = "2026-08-10T00:00:00Z"
ACCEPTED_ID = "accepted-draft"
PREREG_ID = "completed-preregistration"


def canonical(value: object) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode()


def sha(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def span(raw: bytes, text: str) -> dict[str, int]:
    needle = text.encode()
    start = raw.index(needle)
    return {"start": start, "end": start + len(needle)}


def locator(role: str) -> dict[str, str]:
    return {
        "kind": "section",
        "value": role.replace("_", " "),
        "provenance": runtime.LOCATOR_PROVENANCE,
    }


def quote_slot(role: str, artifact_id: str, raw: bytes, text: str) -> dict[str, object]:
    return {
        "logical_role": role,
        "artifact_id": artifact_id,
        "document_locator": locator(role),
        "evidence_state": "agent_extracted",
        "anchor_value_encoded": quote(text, safe=""),
        "quote_source_span_utf8": span(raw, text),
        "checked_scope_input": None,
        "captured_at": STAMP,
        "sharing_scope": "session_only",
        "rights_basis": "not_assessed",
    }


def checked_slot(
    role: str, artifact_id: str, raw: bytes, text: str
) -> dict[str, object]:
    return {
        "logical_role": role,
        "artifact_id": artifact_id,
        "document_locator": locator(role),
        "evidence_state": "checked_no_match",
        "anchor_value_encoded": None,
        "quote_source_span_utf8": None,
        "checked_scope_input": {
            "source_span_utf8": span(raw, text),
            "checked_at": STAMP,
            "scope_completeness": runtime.SCOPE_COMPLETENESS,
        },
        "captured_at": None,
        "sharing_scope": "session_only",
        "rights_basis": "not_assessed",
    }


def failure_slot(
    role: str,
    artifact_id: str,
    state: str,
) -> dict[str, object]:
    return {
        "logical_role": role,
        "artifact_id": artifact_id,
        "document_locator": locator(role),
        "evidence_state": state,
        "anchor_value_encoded": None,
        "quote_source_span_utf8": None,
        "checked_scope_input": None,
        "captured_at": None,
        "sharing_scope": "session_only",
        "rights_basis": "not_assessed",
    }


def observation(
    *,
    key: str,
    pair: str,
    slots: list[dict[str, object]],
    finding: str | None = None,
    negative: str | None = None,
    check_state: str = "performed",
    reason: str | None = None,
    deviation_id: str | None = None,
    deviation_domain: str | None = None,
) -> dict[str, object]:
    outcome = None
    if check_state == "performed":
        outcome = (
            "POTENTIAL_INCONSISTENCY_LOCATED"
            if finding is not None
            else "NO_LISTED_INCONSISTENCY_LOCATED"
        )
    return {
        "observation_key": key,
        "pair_kind": pair,
        "check_state": check_state,
        "outcome": outcome,
        "finding_type": finding,
        "negative_basis": negative,
        "not_checked_reason": reason,
        "deviation_id": deviation_id,
        "deviation_domain": deviation_domain,
        "evidence_slots": slots,
    }


def build_observations(accepted: bytes, prereg: bytes) -> list[dict[str, object]]:
    cases = json.loads((FIXTURES / "cases.json").read_text())
    result: list[dict[str, object]] = []
    roles = runtime.PAIR_ROLES
    for case in cases["positive"]:
        pair = case["pair_kind"]
        if pair in {"abstract_results", "discussion_results"}:
            slots = [
                quote_slot(roles[pair][0], ACCEPTED_ID, accepted, case["quotes"][0]),
                quote_slot(roles[pair][1], ACCEPTED_ID, accepted, case["quotes"][1]),
            ]
        elif pair == "methods_reported_analyses":
            slots = [
                quote_slot("methods", ACCEPTED_ID, accepted, case["quotes"][0]),
                checked_slot(
                    "reported_analyses",
                    ACCEPTED_ID,
                    accepted,
                    case["checked_scope"],
                ),
            ]
        else:
            slots = [
                quote_slot(
                    "manuscript_report", ACCEPTED_ID, accepted, case["quotes"][0]
                ),
                quote_slot("preregistration", PREREG_ID, prereg, case["quotes"][1]),
                checked_slot(
                    "disclosure_scope",
                    ACCEPTED_ID,
                    accepted,
                    case["checked_scope"],
                ),
            ]
        result.append(
            observation(
                key=case["observation_key"],
                pair=pair,
                slots=slots,
                finding=case["finding_type"],
                deviation_id=case.get("deviation_id"),
                deviation_domain=case.get("deviation_domain"),
            )
        )
    for case in cases["negative"]:
        pair = case["pair_kind"]
        if pair == "manuscript_preregistration":
            slots = [
                quote_slot(
                    "manuscript_report", ACCEPTED_ID, accepted, case["quotes"][0]
                ),
                quote_slot("preregistration", PREREG_ID, prereg, case["quotes"][1]),
                quote_slot(
                    "disclosure_scope", ACCEPTED_ID, accepted, case["quotes"][2]
                ),
            ]
        else:
            slots = [
                quote_slot(roles[pair][0], ACCEPTED_ID, accepted, case["quotes"][0]),
                quote_slot(roles[pair][1], ACCEPTED_ID, accepted, case["quotes"][1]),
            ]
        result.append(
            observation(
                key=case["observation_key"],
                pair=pair,
                slots=slots,
                negative=case["negative_basis"],
                deviation_id=case.get("deviation_id"),
                deviation_domain=case.get("deviation_domain"),
            )
        )
    return result


def make_manifest(
    accepted: bytes,
    sidecar: dict[str, object],
) -> dict[str, object]:
    accepted_digest = sha(accepted)
    prereg_state = {
        "provided": "present",
        "not_provided": "source_missing",
        "access_failed": "access_failed",
        "retrieval_failed": "retrieval_failed",
    }[sidecar["status"]]
    artifacts = [
        {
            "artifact_id": ACCEPTED_ID,
            "document_kind": "manuscript",
            "relative_path": "accepted_draft.md",
            "artifact_state": "present",
            "artifact_provenance": "synthetic_fixture",
            "source_artifact_sha256": accepted_digest,
            "source_artifact_size_bytes": len(accepted),
            "source_content_sha256": accepted_digest,
            "source_content_utf8_bytes": len(accepted),
        },
        {
            "artifact_id": sidecar["artifact_id"],
            "document_kind": "preregistration",
            "relative_path": sidecar["relative_path"],
            "artifact_state": prereg_state,
            "artifact_provenance": sidecar["artifact_provenance"],
            "source_artifact_sha256": sidecar["source_artifact_sha256"],
            "source_artifact_size_bytes": sidecar["source_artifact_size_bytes"],
            "source_content_sha256": sidecar["source_content_sha256"],
            "source_content_utf8_bytes": sidecar["source_content_utf8_bytes"],
        },
    ]
    artifacts.sort(key=lambda item: item["artifact_id"])
    manifest: dict[str, object] = {
        "schema_version": runtime.MANIFEST_SCHEMA_VERSION,
        "manifest_id": "fixture-manifest",
        "accepted_draft_artifact_id": ACCEPTED_ID,
        "accepted_draft_sha256": accepted_digest,
        "artifacts": artifacts,
        "manifest_digest": "",
    }
    manifest["manifest_digest"] = runtime._digest_without(manifest, "manifest_digest")
    return manifest


def make_bundle() -> dict[str, object]:
    accepted = (FIXTURES / "accepted_draft.md").read_bytes()
    prereg = (FIXTURES / "preregistration.md").read_bytes()
    sidecar = runtime.build_preregistration_artifact(
        status="provided",
        artifact_id=PREREG_ID,
        declared_at=STAMP,
        companion_bytes=prereg,
        relative_path="preregistration.md",
        artifact_provenance="synthetic_fixture",
    )
    manifest = make_manifest(accepted, sidecar)
    draft = {
        "schema_version": runtime.DRAFT_SCHEMA_VERSION,
        "layer": runtime.LAYER,
        "recorded_at": STAMP,
        "observations": build_observations(accepted, prereg),
    }
    raw = {
        "draft": canonical(draft),
        "manifest": canonical(manifest),
        "sidecar": canonical(sidecar),
    }
    report = runtime.finalize_advisory(
        draft,
        manifest,
        sidecar,
        accepted_draft_bytes=accepted,
        preregistration_bytes=prereg,
        draft_raw=raw["draft"],
        manifest_raw=raw["manifest"],
        sidecar_raw=raw["sidecar"],
    )
    return {
        "accepted": accepted,
        "prereg": prereg,
        "sidecar": sidecar,
        "manifest": manifest,
        "draft": draft,
        "raw": raw,
        "report": report,
    }


def write_bundle(tmp_path: Path, bundle: dict[str, object]) -> dict[str, Path]:
    paths = {
        "accepted": tmp_path / "accepted.md",
        "prereg": tmp_path / "prereg.md",
        "sidecar": tmp_path / "sidecar.json",
        "manifest": tmp_path / "manifest.json",
        "draft": tmp_path / "draft.json",
        "report": tmp_path / "report.json",
    }
    paths["accepted"].write_bytes(bundle["accepted"])
    paths["prereg"].write_bytes(bundle["prereg"])
    paths["sidecar"].write_bytes(bundle["raw"]["sidecar"])
    paths["manifest"].write_bytes(bundle["raw"]["manifest"])
    paths["draft"].write_bytes(bundle["raw"]["draft"])
    paths["report"].write_bytes(canonical(bundle["report"]))
    return paths


@pytest.fixture
def bundle() -> dict[str, object]:
    return make_bundle()


def finalizer_args(paths: dict[str, Path]) -> list[str]:
    return [
        "--draft",
        str(paths["draft"]),
        "--manifest",
        str(paths["manifest"]),
        "--preregistration-record",
        str(paths["sidecar"]),
        "--preregistration-companion",
        str(paths["prereg"]),
        "--accepted-draft",
        str(paths["accepted"]),
    ]


def test_four_positives_and_three_negatives_finalize(bundle):
    report = bundle["report"]
    observations = [
        item for pair in report["pair_results"] for item in pair["observations"]
    ]
    assert len(observations) == 7
    assert (
        sum(
            item["outcome"] == "POTENTIAL_INCONSISTENCY_LOCATED"
            for item in observations
        )
        == 4
    )
    assert (
        sum(
            item["outcome"] == "NO_LISTED_INCONSISTENCY_LOCATED"
            for item in observations
        )
        == 3
    )
    assert [pair["pair_kind"] for pair in report["pair_results"]] == list(
        runtime.PAIR_ORDER
    )
    assert [item["advisory_id"] for item in observations] == [
        f"ADV-XDOC-{index:06d}" for index in range(1, 8)
    ]
    assert [item["evidence_row"]["row_id"] for item in observations] == [
        f"EVR-XDOC-{index:06d}" for index in range(1, 8)
    ]


def test_observation_level_rows_have_exact_two_or_three_slots(bundle):
    for pair in bundle["report"]["pair_results"]:
        expected = 3 if pair["pair_kind"] == "manuscript_preregistration" else 2
        for observation_item in pair["observations"]:
            row = observation_item["evidence_row"]
            assert len(row["evidence_slots"]) == expected
            assert row["row_sha256"] == runtime._digest_without(row, "row_sha256")
            assert row["deviation_id"] == observation_item["deviation_id"]


def test_report_and_input_digests_replay(bundle):
    report = bundle["report"]
    assert report["report_digest"] == runtime._digest_without(report, "report_digest")
    assert report["input_binding"]["accepted_draft_sha256"] == sha(bundle["accepted"])
    assert report["input_binding"]["accepted_draft_artifact_id"] == ACCEPTED_ID
    runtime.validate_advisory(
        report,
        bundle["draft"],
        bundle["manifest"],
        bundle["sidecar"],
        advisory_raw=canonical(report),
        accepted_draft_bytes=bundle["accepted"],
        preregistration_bytes=bundle["prereg"],
        draft_raw=bundle["raw"]["draft"],
        manifest_raw=bundle["raw"]["manifest"],
        sidecar_raw=bundle["raw"]["sidecar"],
    )


def test_all_five_schemas_accept_runtime_outputs(bundle):
    schema_paths = {
        "sidecar": REPO
        / "shared/contracts/passport/preregistration_artifact.schema.json",
        "manifest": REPO
        / "shared/contracts/audit/cross_document_source_manifest.schema.json",
        "draft": REPO
        / "shared/contracts/audit/cross_document_consistency_advisory_draft.schema.json",
        "row": REPO / "shared/contracts/evidence/evidence_row_v1_2.schema.json",
        "final": REPO
        / "shared/contracts/audit/cross_document_consistency_advisory.schema.json",
    }
    schemas = {
        name: json.loads(path.read_text()) for name, path in schema_paths.items()
    }
    for name in ("sidecar", "manifest", "draft", "row", "final"):
        Draft202012Validator.check_schema(schemas[name])
    Draft202012Validator(schemas["sidecar"]).validate(bundle["sidecar"])
    Draft202012Validator(schemas["manifest"]).validate(bundle["manifest"])
    Draft202012Validator(schemas["draft"]).validate(bundle["draft"])
    row_registry = Registry().with_resource(
        schemas["row"]["$id"], Resource.from_contents(schemas["row"])
    )
    for pair in bundle["report"]["pair_results"]:
        for item in pair["observations"]:
            Draft202012Validator(schemas["row"]).validate(item["evidence_row"])
    Draft202012Validator(schemas["final"], registry=row_registry).validate(
        bundle["report"]
    )


@pytest.mark.parametrize(
    "mutation",
    ["role_swap", "drop_third", "quote_text", "span", "reason", "deviation"],
)
def test_draft_kill_mutations_fail_closed(bundle, mutation):
    draft = copy.deepcopy(bundle["draft"])
    if mutation == "role_swap":
        draft["observations"][0]["evidence_slots"][0]["logical_role"] = "results"
    elif mutation == "drop_third":
        target = next(
            item
            for item in draft["observations"]
            if item["finding_type"] == "undisclosed_preregistration_deviation"
        )
        target["evidence_slots"].pop()
    elif mutation == "quote_text":
        draft["observations"][0]["evidence_slots"][0]["anchor_value_encoded"] = "forged"
    elif mutation == "span":
        draft["observations"][0]["evidence_slots"][0]["quote_source_span_utf8"][
            "start"
        ] += 1
    elif mutation == "reason":
        target = draft["observations"][0]
        target.update(
            check_state="not_checked",
            outcome=None,
            finding_type=None,
            negative_basis=None,
            not_checked_reason="SOURCE_ACCESS_FAILED",
        )
        target["evidence_slots"][0] = failure_slot(
            "abstract", ACCEPTED_ID, "not_checked"
        )
    else:
        target = next(item for item in draft["observations"] if item["deviation_id"])
        target["deviation_domain"] = "unknown"
    with pytest.raises(runtime.AdvisoryError):
        runtime.finalize_advisory(
            draft,
            bundle["manifest"],
            bundle["sidecar"],
            accepted_draft_bytes=bundle["accepted"],
            preregistration_bytes=bundle["prereg"],
        )


@pytest.mark.parametrize(
    "mutation", ["record", "projection", "accepted_sha", "companion"]
)
def test_binding_kill_mutations_fail_before_semantics(bundle, mutation):
    sidecar = copy.deepcopy(bundle["sidecar"])
    manifest = copy.deepcopy(bundle["manifest"])
    prereg = bundle["prereg"]
    if mutation == "record":
        sidecar["record_digest"] = "0" * 64
    elif mutation == "projection":
        manifest["artifacts"][1]["artifact_provenance"] = "not_provided"
        manifest["manifest_digest"] = runtime._digest_without(
            manifest, "manifest_digest"
        )
    elif mutation == "accepted_sha":
        manifest["accepted_draft_sha256"] = "0" * 64
        manifest["manifest_digest"] = runtime._digest_without(
            manifest, "manifest_digest"
        )
    else:
        prereg = prereg + b"drift"
    with pytest.raises(runtime.AdvisoryError):
        runtime.finalize_advisory(
            bundle["draft"],
            manifest,
            sidecar,
            accepted_draft_bytes=bundle["accepted"],
            preregistration_bytes=prereg,
        )


def test_missing_preregistration_is_not_checked_not_clean(bundle):
    sidecar = runtime.build_preregistration_artifact(
        status="not_provided",
        artifact_id=PREREG_ID,
        declared_at=STAMP,
    )
    manifest = make_manifest(bundle["accepted"], sidecar)
    draft = copy.deepcopy(bundle["draft"])
    draft["observations"] = [
        item
        for item in draft["observations"]
        if item["pair_kind"] != "manuscript_preregistration"
    ]
    draft["observations"].append(
        observation(
            key="prereg.missing",
            pair="manuscript_preregistration",
            check_state="not_checked",
            reason="COUNTERPART_DOCUMENT_MISSING",
            slots=[
                failure_slot("manuscript_report", ACCEPTED_ID, "not_checked"),
                failure_slot("preregistration", PREREG_ID, "source_missing"),
                failure_slot("disclosure_scope", ACCEPTED_ID, "not_checked"),
            ],
        )
    )
    report = runtime.finalize_advisory(
        draft,
        manifest,
        sidecar,
        accepted_draft_bytes=bundle["accepted"],
        preregistration_bytes=None,
    )
    row = report["pair_results"][3]["observations"][0]
    assert row["check_state"] == "not_checked"
    assert row["outcome"] is None
    assert row["not_checked_reason"] == "COUNTERPART_DOCUMENT_MISSING"


def test_missing_methods_scope_routes_to_scope_not_provided(bundle):
    draft = copy.deepcopy(bundle["draft"])
    draft["observations"] = [
        item
        for item in draft["observations"]
        if item["pair_kind"] != "methods_reported_analyses"
    ]
    text = "We preregistered a linear regression adjusted for baseline score."
    draft["observations"].append(
        observation(
            key="methods.scope-not-provided",
            pair="methods_reported_analyses",
            check_state="not_checked",
            reason="COUNTERPART_SCOPE_NOT_PROVIDED",
            slots=[
                quote_slot("methods", ACCEPTED_ID, bundle["accepted"], text),
                failure_slot("reported_analyses", ACCEPTED_ID, "not_checked"),
            ],
        )
    )
    report = runtime.finalize_advisory(
        draft,
        bundle["manifest"],
        bundle["sidecar"],
        accepted_draft_bytes=bundle["accepted"],
        preregistration_bytes=bundle["prereg"],
    )
    methods = report["pair_results"][2]["observations"][0]
    assert methods["not_checked_reason"] == "COUNTERPART_SCOPE_NOT_PROVIDED"


def test_cli_finalize_validate_render_and_atomic_failure(tmp_path, bundle, capsys):
    paths = write_bundle(tmp_path, bundle)
    output = tmp_path / "built.json"
    assert (
        runtime.main(["finalize", *finalizer_args(paths), "--output", str(output)]) == 0
    )
    assert output.read_bytes() == canonical(bundle["report"])
    assert (
        runtime.main(["validate", *finalizer_args(paths), "--advisory", str(output)])
        == 0
    )
    rendered = tmp_path / "page.md"
    assert (
        runtime.main(
            [
                "render",
                *finalizer_args(paths),
                "--advisory",
                str(output),
                "--output",
                str(rendered),
                "--page-size",
                "3",
                "--page",
                "2",
            ]
        )
        == 0
    )
    text = rendered.read_text()
    assert "Page 2/3" in text
    assert text.count("ADV&#45;XDOC&#45;") <= 3

    output.write_bytes(b"sentinel")
    paths["draft"].write_text("{}")
    assert (
        runtime.main(["finalize", *finalizer_args(paths), "--output", str(output)]) == 2
    )
    assert output.read_bytes() == b"sentinel"
    assert capsys.readouterr().err.strip().splitlines()[-1] == (
        "ADVISORY_UNAVAILABLE:DRAFT_CONTRACT_INVALID"
    )


def test_validate_rejects_noncanonical_final_bytes(tmp_path, bundle):
    paths = write_bundle(tmp_path, bundle)
    paths["report"].write_text(json.dumps(bundle["report"], indent=2) + "\n")
    assert (
        runtime.main(
            ["validate", *finalizer_args(paths), "--advisory", str(paths["report"])]
        )
        == 2
    )


def test_library_validate_rejects_noncanonical_final_bytes(bundle):
    pretty = (
        json.dumps(bundle["report"], indent=2, ensure_ascii=False) + "\n"
    ).encode()
    with pytest.raises(runtime.AdvisoryError) as failure:
        runtime.validate_advisory(
            bundle["report"],
            bundle["draft"],
            bundle["manifest"],
            bundle["sidecar"],
            advisory_raw=pretty,
            accepted_draft_bytes=bundle["accepted"],
            preregistration_bytes=bundle["prereg"],
        )
    assert failure.value.code == "FINAL_ARTIFACT_INVALID"


def test_raw_input_binding_cannot_name_a_different_object(bundle):
    different_draft = copy.deepcopy(bundle["draft"])
    different_draft["recorded_at"] = "2026-08-10T00:00:01Z"
    with pytest.raises(runtime.AdvisoryError) as failure:
        runtime.finalize_advisory(
            bundle["draft"],
            bundle["manifest"],
            bundle["sidecar"],
            accepted_draft_bytes=bundle["accepted"],
            preregistration_bytes=bundle["prereg"],
            draft_raw=canonical(different_draft),
        )
    assert failure.value.code == "DRAFT_CONTRACT_INVALID"


def test_malformed_list_field_fails_as_closed_contract_error(bundle):
    draft = copy.deepcopy(bundle["draft"])
    draft["observations"][0]["evidence_slots"][0]["sharing_scope"] = []
    with pytest.raises(runtime.AdvisoryError) as failure:
        runtime.finalize_advisory(
            draft,
            bundle["manifest"],
            bundle["sidecar"],
            accepted_draft_bytes=bundle["accepted"],
            preregistration_bytes=bundle["prereg"],
        )
    assert failure.value.code == "DRAFT_CONTRACT_INVALID"


def test_invalid_source_preflight_precedes_semantic_draft_read(
    tmp_path, bundle, capsys
):
    paths = write_bundle(tmp_path, bundle)
    paths["accepted"].write_bytes(b"\xff")
    paths["draft"].unlink()
    assert runtime.main(["finalize", *finalizer_args(paths)]) == 2
    assert capsys.readouterr().err.strip() == (
        "ADVISORY_UNAVAILABLE:SOURCE_BINDING_INVALID"
    )


@pytest.mark.parametrize("count", [0, 1, 25, 26, 1001])
def test_paginator_has_no_loss_duplication_or_reordering(count):
    items = list(range(count))
    recovered = []
    total_pages = max(1, (count + 24) // 25)
    for page in range(1, total_pages + 1):
        visible, observed_pages = runtime.paginate(items, page=page, page_size=25)
        assert observed_pages == total_pages
        assert len(visible) <= 25
        recovered.extend(visible)
    assert recovered == items


def test_parser_has_no_all_escape_hatch(capsys):
    assert runtime.main(["render", "--all"]) == 2
    assert capsys.readouterr().err.strip() == (
        "ADVISORY_UNAVAILABLE:FINAL_ARTIFACT_INVALID"
    )


def test_single_percent_decode_and_literal_plus():
    assert runtime.strict_percent_decode("a+b%2520c") == "a+b%20c"
    with pytest.raises(runtime.AdvisoryError):
        runtime.strict_percent_decode("bad%2")


def test_runtime_has_no_ambient_or_external_execution_surfaces():
    source = Path(runtime.__file__).read_text()
    forbidden = (
        "datetime.now(",
        "datetime.utcnow(",
        "time.time(",
        "requests.",
        "urllib.request",
        "subprocess.",
        "os.walk(",
    )
    assert not any(token in source for token in forbidden)


def test_builder_cli_writes_canonical_sidecar(tmp_path, bundle):
    companion = tmp_path / "prereg.md"
    companion.write_bytes(bundle["prereg"])
    output = tmp_path / "record.json"
    assert (
        runtime.main(
            [
                "build-preregistration-artifact",
                "--status",
                "provided",
                "--artifact-id",
                PREREG_ID,
                "--declared-at",
                STAMP,
                "--relative-path",
                "preregistration.md",
                "--artifact-provenance",
                "synthetic_fixture",
                "--companion",
                str(companion),
                "--output",
                str(output),
            ]
        )
        == 0
    )
    assert output.read_bytes() == canonical(json.loads(output.read_text()))
    assert json.loads(output.read_text()) == bundle["sidecar"]


def test_report_tampering_fails_replay(bundle):
    report = copy.deepcopy(bundle["report"])
    report["pair_results"][0]["observations"][0]["evidence_row"]["row_sha256"] = (
        "0" * 64
    )
    report["report_digest"] = runtime._digest_without(report, "report_digest")
    with pytest.raises(runtime.AdvisoryError):
        runtime.validate_advisory(
            report,
            bundle["draft"],
            bundle["manifest"],
            bundle["sidecar"],
            advisory_raw=canonical(report),
            accepted_draft_bytes=bundle["accepted"],
            preregistration_bytes=bundle["prereg"],
        )


def test_fifo_admission_is_nonblocking_and_regular_file_only(tmp_path):
    source = inspect.getsource(runtime._read_named_bytes)
    assert "os.O_NONBLOCK" in source
    assert "stat.S_ISREG" in source
    fifo = tmp_path / "named-input.fifo"
    os.mkfifo(fifo)
    with pytest.raises(runtime.AdvisoryError) as failure:
        runtime._read_named_bytes(fifo, 16, label="test FIFO")
    assert failure.value.code == "NAMED_INPUT_UNREADABLE"


def test_named_byte_limit_accepts_n_and_rejects_n_plus_one(tmp_path):
    source = tmp_path / "bounded.bin"
    source.write_bytes(b"x" * 32)
    assert runtime._read_named_bytes(source, 32, label="bounded") == b"x" * 32
    source.write_bytes(b"x" * 33)
    with pytest.raises(runtime.AdvisoryError) as failure:
        runtime._read_named_bytes(source, 32, label="bounded")
    assert failure.value.code == "RESOURCE_LIMIT"


def test_provided_companion_later_unreadable_is_source_binding_failure(
    tmp_path, bundle, capsys
):
    paths = write_bundle(tmp_path, bundle)
    paths["prereg"].unlink()
    assert runtime.main(["finalize", *finalizer_args(paths)]) == 2
    assert capsys.readouterr().err.strip() == (
        "ADVISORY_UNAVAILABLE:SOURCE_BINDING_INVALID"
    )


def test_cli_syntax_error_is_one_bounded_path_free_diagnostic(capsys):
    secret = "/Users/private/manuscript.md"
    assert (
        runtime.main(
            [
                "finalize",
                "--draft",
                "d",
                "--manifest",
                "m",
                "--preregistration-record",
                "s",
                "--accepted-draft",
                "a",
                "--secret",
                secret,
            ]
        )
        == 2
    )
    diagnostic = capsys.readouterr().err
    assert diagnostic == "ADVISORY_UNAVAILABLE:FINAL_ARTIFACT_INVALID\n"
    assert secret not in diagnostic


def test_complete_role_matrix_preflight_precedes_semantic_outcomes(bundle):
    draft = copy.deepcopy(bundle["draft"])
    draft["observations"][0]["outcome"] = "BOGUS"
    draft["observations"][-1]["evidence_slots"][0]["logical_role"] = (
        "consent_protocol"
    )
    with pytest.raises(runtime.AdvisoryError) as failure:
        runtime.finalize_advisory(
            draft,
            bundle["manifest"],
            bundle["sidecar"],
            accepted_draft_bytes=bundle["accepted"],
            preregistration_bytes=bundle["prereg"],
        )
    assert "evidence_slots[0].logical_role" in str(failure.value)
    assert ".outcome" not in str(failure.value)


def test_renderer_includes_inert_locator(bundle):
    draft = copy.deepcopy(bundle["draft"])
    locator_value = "LOCATOR <img src=x> | [link](file:///secret)"
    draft["observations"][0]["evidence_slots"][0]["document_locator"][
        "value"
    ] = locator_value
    report = runtime.finalize_advisory(
        draft,
        bundle["manifest"],
        bundle["sidecar"],
        accepted_draft_bytes=bundle["accepted"],
        preregistration_bytes=bundle["prereg"],
        draft_raw=canonical(draft),
        manifest_raw=bundle["raw"]["manifest"],
        sidecar_raw=bundle["raw"]["sidecar"],
    )
    rendered = runtime.render_advisory(report)
    assert "LOCATOR " in rendered
    assert "<img" not in rendered
    assert "file:///secret" not in rendered
    assert "&#60;img src&#61;x&#62;" in rendered


def test_renderer_has_exact_ceiling_and_visible_no_listed_outcomes(bundle):
    rendered = runtime.render_advisory(bundle["report"])
    ceiling = (
        "NO LISTED INCONSISTENCY LOCATED — not proof of agreement, completeness, "
        "or a clean document."
    )
    assert ceiling in rendered
    for negative_basis in (
        "legitimate_compression",
        "same_rung_rewording",
        "disclosed_deviation",
    ):
        visible_result = runtime._markdown_inert(
            f"NO_LISTED_INCONSISTENCY_LOCATED — {negative_basis}"
        )
        assert visible_result in rendered


def test_blank_accepted_draft_fails_before_semantic_slots(bundle):
    accepted = b" \n\t"
    manifest = make_manifest(accepted, bundle["sidecar"])
    with pytest.raises(runtime.AdvisoryError) as failure:
        runtime.finalize_advisory(
            bundle["draft"],
            manifest,
            bundle["sidecar"],
            accepted_draft_bytes=accepted,
            preregistration_bytes=bundle["prereg"],
        )
    assert failure.value.code == "SOURCE_BINDING_INVALID"
    assert "accepted draft" in str(failure.value)


@pytest.mark.parametrize(
    ("status", "state", "reason"),
    [
        ("not_provided", "source_missing", "COUNTERPART_DOCUMENT_MISSING"),
        ("access_failed", "access_failed", "SOURCE_ACCESS_FAILED"),
        ("retrieval_failed", "retrieval_failed", "SOURCE_RETRIEVAL_FAILED"),
    ],
)
def test_unavailable_sidecar_status_matrix_is_not_checked(
    bundle, status, state, reason
):
    sidecar = runtime.build_preregistration_artifact(
        status=status,
        artifact_id=PREREG_ID,
        declared_at=STAMP,
    )
    manifest = make_manifest(bundle["accepted"], sidecar)
    draft = copy.deepcopy(bundle["draft"])
    draft["observations"] = [
        item
        for item in draft["observations"]
        if item["pair_kind"] != "manuscript_preregistration"
    ]
    draft["observations"].append(
        observation(
            key=f"prereg.{status}",
            pair="manuscript_preregistration",
            check_state="not_checked",
            reason=reason,
            slots=[
                failure_slot("manuscript_report", ACCEPTED_ID, "not_checked"),
                failure_slot("preregistration", PREREG_ID, state),
                failure_slot("disclosure_scope", ACCEPTED_ID, "not_checked"),
            ],
        )
    )
    report = runtime.finalize_advisory(
        draft,
        manifest,
        sidecar,
        accepted_draft_bytes=bundle["accepted"],
        preregistration_bytes=None,
    )
    result = report["pair_results"][3]["observations"][0]
    assert result["check_state"] == "not_checked"
    assert result["outcome"] is None
    assert result["not_checked_reason"] == reason


def test_reported_analysis_without_declared_method_uses_reverse_scope(bundle):
    draft = copy.deepcopy(bundle["draft"])
    draft["observations"] = [
        item
        for item in draft["observations"]
        if item["pair_kind"] != "methods_reported_analyses"
    ]
    draft["observations"].append(
        observation(
            key="methods.reported-no-declaration",
            pair="methods_reported_analyses",
            finding="reported_analysis_no_declared_counterpart",
            slots=[
                checked_slot(
                    "methods",
                    ACCEPTED_ID,
                    bundle["accepted"],
                    "We preregistered a linear regression adjusted for baseline score.",
                ),
                quote_slot(
                    "reported_analyses",
                    ACCEPTED_ID,
                    bundle["accepted"],
                    "Reported analyses included descriptive statistics and a robustness check.",
                ),
            ],
        )
    )
    report = runtime.finalize_advisory(
        draft,
        bundle["manifest"],
        bundle["sidecar"],
        accepted_draft_bytes=bundle["accepted"],
        preregistration_bytes=bundle["prereg"],
    )
    result = report["pair_results"][2]["observations"][0]
    assert result["finding_type"] == "reported_analysis_no_declared_counterpart"
    assert [
        slot["evidence_state"] for slot in result["evidence_row"]["evidence_slots"]
    ] == ["checked_no_match", "agent_extracted"]


def test_blank_checked_scope_is_not_absence_evidence(bundle):
    draft = copy.deepcopy(bundle["draft"])
    target = next(
        item
        for item in draft["observations"]
        if item["finding_type"] == "declared_analysis_no_reported_counterpart"
    )
    blank_start = bundle["accepted"].index(b"\n\n")
    target["evidence_slots"][1]["checked_scope_input"]["source_span_utf8"] = {
        "start": blank_start,
        "end": blank_start + 2,
    }
    with pytest.raises(runtime.AdvisoryError) as failure:
        runtime.finalize_advisory(
            draft,
            bundle["manifest"],
            bundle["sidecar"],
            accepted_draft_bytes=bundle["accepted"],
            preregistration_bytes=bundle["prereg"],
        )
    assert failure.value.code == "EVIDENCE_REPLAY_INVALID"


@pytest.mark.parametrize("text", [" ".join(["word"] * 26), "x" * 1001])
def test_external_quote_word_and_codepoint_limit_plus_one_fail(bundle, text):
    accepted = bundle["accepted"] + b"\n" + text.encode()
    manifest = make_manifest(accepted, bundle["sidecar"])
    draft = copy.deepcopy(bundle["draft"])
    draft["observations"][0]["evidence_slots"][0] = quote_slot(
        "abstract", ACCEPTED_ID, accepted, text
    )
    with pytest.raises(runtime.AdvisoryError) as failure:
        runtime.finalize_advisory(
            draft,
            manifest,
            bundle["sidecar"],
            accepted_draft_bytes=accepted,
            preregistration_bytes=bundle["prereg"],
        )
    assert failure.value.code == "EVIDENCE_REPLAY_INVALID"


@pytest.mark.parametrize(
    "raw",
    [
        b"\xef\xbb\xbf{}",
        b'{"a":1,"a":2}',
        b'{"a":NaN}',
        b'{"a":"\\u0001"}',
        b'{"a":"\\ud800"}',
    ],
)
def test_strict_json_kill_inputs_fail_closed(raw):
    with pytest.raises(runtime.AdvisoryError) as failure:
        runtime._strict_json_bytes(raw, code="DRAFT_CONTRACT_INVALID", path="draft")
    assert failure.value.code == "DRAFT_CONTRACT_INVALID"


def test_json_depth_limit_accepts_n_and_rejects_n_plus_one(monkeypatch):
    monkeypatch.setattr(runtime, "MAX_JSON_DEPTH", 2)
    accepted = runtime._strict_json_bytes(
        b'{"items":[]}', code="DRAFT_CONTRACT_INVALID", path="draft"
    )
    assert accepted == {"items": []}
    with pytest.raises(runtime.AdvisoryError) as failure:
        runtime._strict_json_bytes(
            b'{"items":[[]]}', code="DRAFT_CONTRACT_INVALID", path="draft"
        )
    assert failure.value.code == "DRAFT_CONTRACT_INVALID"
    assert "nesting exceeds 2" in str(failure.value)


def test_json_node_limit_accepts_n_and_rejects_n_plus_one(monkeypatch):
    monkeypatch.setattr(runtime, "MAX_JSON_NODES", 3)
    assert runtime._strict_json_bytes(
        b"[null,null]", code="DRAFT_CONTRACT_INVALID", path="draft"
    ) == [None, None]
    with pytest.raises(runtime.AdvisoryError) as failure:
        runtime._strict_json_bytes(
            b"[null,null,null]", code="DRAFT_CONTRACT_INVALID", path="draft"
        )
    assert failure.value.code == "DRAFT_CONTRACT_INVALID"
    assert "aggregate nodes exceed 3" in str(failure.value)


def test_observation_array_limit_accepts_n_and_rejects_n_plus_one(monkeypatch):
    monkeypatch.setattr(runtime, "MAX_OBSERVATIONS", 2)
    assert runtime._array(
        ["left", "right"],
        "observations",
        code="DRAFT_CONTRACT_INVALID",
        maximum=runtime.MAX_OBSERVATIONS,
    ) == ["left", "right"]
    with pytest.raises(runtime.AdvisoryError) as failure:
        runtime._array(
            ["left", "right", "extra"],
            "observations",
            code="DRAFT_CONTRACT_INVALID",
            maximum=runtime.MAX_OBSERVATIONS,
        )
    assert failure.value.code == "DRAFT_CONTRACT_INVALID"


def test_page_size_limit_accepts_n_and_rejects_n_plus_one(monkeypatch):
    monkeypatch.setattr(runtime, "MAX_PAGE_SIZE", 2)
    visible, pages = runtime.paginate([1, 2, 3], page=1, page_size=2)
    assert visible == [1, 2]
    assert pages == 2
    with pytest.raises(runtime.AdvisoryError) as failure:
        runtime.paginate([1, 2, 3], page=1, page_size=3)
    assert failure.value.code == "FINAL_ARTIFACT_INVALID"


def test_aggregate_source_limit_accepts_n_and_rejects_n_plus_one(
    monkeypatch, bundle
):
    total = len(bundle["accepted"]) + len(bundle["prereg"])
    monkeypatch.setattr(runtime, "MAX_TOTAL_SOURCE_BYTES", total)
    runtime._prepare_inputs(
        bundle["draft"],
        bundle["manifest"],
        bundle["sidecar"],
        accepted_draft_bytes=bundle["accepted"],
        preregistration_bytes=bundle["prereg"],
    )
    with pytest.raises(runtime.AdvisoryError) as failure:
        runtime._prepare_inputs(
            bundle["draft"],
            bundle["manifest"],
            bundle["sidecar"],
            accepted_draft_bytes=bundle["accepted"],
            preregistration_bytes=bundle["prereg"] + b"x",
        )
    assert failure.value.code == "RESOURCE_LIMIT"


def test_final_output_limit_accepts_n_and_rejects_n_plus_one(monkeypatch, bundle):
    final_size = len(canonical(bundle["report"]))
    monkeypatch.setattr(runtime, "MAX_FINAL_BYTES", final_size)
    accepted = runtime.finalize_advisory(
        bundle["draft"],
        bundle["manifest"],
        bundle["sidecar"],
        accepted_draft_bytes=bundle["accepted"],
        preregistration_bytes=bundle["prereg"],
        draft_raw=bundle["raw"]["draft"],
        manifest_raw=bundle["raw"]["manifest"],
        sidecar_raw=bundle["raw"]["sidecar"],
    )
    assert len(canonical(accepted)) == final_size
    monkeypatch.setattr(runtime, "MAX_FINAL_BYTES", final_size - 1)
    with pytest.raises(runtime.AdvisoryError) as failure:
        runtime.finalize_advisory(
            bundle["draft"],
            bundle["manifest"],
            bundle["sidecar"],
            accepted_draft_bytes=bundle["accepted"],
            preregistration_bytes=bundle["prereg"],
            draft_raw=bundle["raw"]["draft"],
            manifest_raw=bundle["raw"]["manifest"],
            sidecar_raw=bundle["raw"]["sidecar"],
        )
    assert failure.value.code == "RESOURCE_LIMIT"


@pytest.mark.parametrize(
    "changes",
    [
        {"relative_path": "../preregistration.md"},
        {"artifact_provenance": "not_provided"},
        {"declared_at": "2026-02-30T00:00:00Z"},
    ],
)
def test_sidecar_path_provenance_and_timestamp_fail_closed(bundle, changes):
    arguments = {
        "status": "provided",
        "artifact_id": PREREG_ID,
        "declared_at": STAMP,
        "companion_bytes": bundle["prereg"],
        "relative_path": "preregistration.md",
        "artifact_provenance": "synthetic_fixture",
    }
    arguments.update(changes)
    with pytest.raises(runtime.AdvisoryError) as failure:
        runtime.build_preregistration_artifact(**arguments)
    assert failure.value.code == "SOURCE_BINDING_INVALID"


def test_shipped_preregistration_template_is_not_evidence():
    template = (REPO / "deep-research/templates/preregistration_template.md").read_bytes()
    assert sha(template) == runtime.TEMPLATE_SHA256
    with pytest.raises(runtime.AdvisoryError) as failure:
        runtime.build_preregistration_artifact(
            status="provided",
            artifact_id=PREREG_ID,
            declared_at=STAMP,
            companion_bytes=template,
            relative_path="preregistration.md",
        )
    assert failure.value.code == "SOURCE_BINDING_INVALID"


def test_whitespace_only_preregistration_companion_is_not_evidence():
    with pytest.raises(runtime.AdvisoryError) as failure:
        runtime.build_preregistration_artifact(
            status="provided",
            artifact_id=PREREG_ID,
            declared_at=STAMP,
            companion_bytes=b" \n\t\r",
            relative_path="preregistration.md",
        )
    assert failure.value.code == "SOURCE_BINDING_INVALID"
    assert "must not be blank" in str(failure.value)


def test_duplicate_observation_key_fails_in_role_preflight(bundle):
    draft = copy.deepcopy(bundle["draft"])
    draft["observations"][1]["observation_key"] = draft["observations"][0][
        "observation_key"
    ]
    with pytest.raises(runtime.AdvisoryError) as failure:
        runtime.finalize_advisory(
            draft,
            bundle["manifest"],
            bundle["sidecar"],
            accepted_draft_bytes=bundle["accepted"],
            preregistration_bytes=bundle["prereg"],
        )
    assert failure.value.code == "DRAFT_CONTRACT_INVALID"


@pytest.mark.parametrize("alias_kind", ["hardlink", "symlink"])
def test_finalize_output_alias_cannot_replace_named_input(
    tmp_path, bundle, capsys, alias_kind
):
    paths = write_bundle(tmp_path, bundle)
    output = tmp_path / "aliased-output.json"
    if alias_kind == "hardlink":
        os.link(paths["draft"], output)
    else:
        output.symlink_to(paths["draft"])
    original = paths["draft"].read_bytes()
    assert (
        runtime.main(
            ["finalize", *finalizer_args(paths), "--output", str(output)]
        )
        == 2
    )
    assert paths["draft"].read_bytes() == original
    assert capsys.readouterr().err.strip() == (
        "ADVISORY_UNAVAILABLE:NAMED_INPUT_UNREADABLE"
    )


def test_symlink_named_input_is_rejected(tmp_path):
    target = tmp_path / "target.json"
    target.write_text("{}")
    link = tmp_path / "input.json"
    link.symlink_to(target)
    with pytest.raises(runtime.AdvisoryError) as failure:
        runtime._read_named_bytes(link, 10, label="symlink")
    assert failure.value.code == "NAMED_INPUT_UNREADABLE"
