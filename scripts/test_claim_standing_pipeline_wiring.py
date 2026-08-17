"""#655 PR-C: pipeline-wiring noninterference tests (design §9 gate 12).

Running the wiring layer changes no Phase E verdict, gate, manuscript,
citation, or read-ledger byte — proven here as (a) a static capability scan
of the three wiring modules (import allowlist, no network / subprocess /
Phase E / read-ledger reach, attribute-level containment of the discovery
module to its pure roster constant, no direct file-writing calls), and (b)
an end-to-end run of both the library seams and the CLI entry points that
creates no files and mutates no inputs. The prose-surface markers for the
wiring live in `scripts/check_claim_standing_candidate_ledger_integration.py`
(single doc-pin owner), not here.
"""
from __future__ import annotations

import ast
import copy
import json
from pathlib import Path

from scripts import build_claim_standing_candidate_ledger as substrate
from scripts import build_claim_standing_query_plan as plan_builder
from scripts import check_claim_standing_freshness as freshness
from scripts import check_claim_standing_transmissions as transmissions
from scripts import claim_standing_stance_runner as runner
from scripts.test_build_claim_standing_candidate_ledger import (
    _rehash_input,
    _rehash_plan,
    _retained,
)
from scripts.test_build_claim_standing_query_plan import (
    _bound_decisions,
    _decisions,
    _registry_row,
)
from scripts.test_claim_standing_stance_contracts import _plan_v1_1
from scripts.test_claim_standing_stance_runner import FakeTransport

ROOT = Path(__file__).resolve().parents[1]
WIRING_MODULES = (
    ROOT / "scripts/build_claim_standing_query_plan.py",
    ROOT / "scripts/check_claim_standing_freshness.py",
    ROOT / "scripts/check_claim_standing_transmissions.py",
)
ALLOWED_IMPORTS = {
    "__future__",
    "argparse",
    "copy",
    "json",
    "sys",
    "pathlib",
    "typing",
    "scripts",
    "build_claim_standing_candidate_ledger",
    "claim_standing_discovery",
    "claim_standing_stance_runner",
}
FORBIDDEN_CAPABILITY_MODULES = {
    "urllib",
    "http",
    "socket",
    "ssl",
    "subprocess",
    "ctypes",
    "importlib",
    "os",
}
PHASE_E_AND_READ_LEDGER_MODULES = {"evidence_rows", "retraction_status"}
# The discovery module holds live transports; the wiring layer may reach
# only its pure declared-roster constant through it.
ALLOWED_DISCOVERY_ATTRIBUTES = {"provider_roster_defaults"}
WRITE_CAPABLE_ATTRIBUTES = {
    "write_text",
    "write_bytes",
    "unlink",
    "rmdir",
    "chmod",
    "mkdir",
    "rename",
    "replace",
    "symlink_to",
    "touch",
}


def _module_ast(path: Path) -> ast.Module:
    return ast.parse(path.read_text(encoding="utf-8"))


def _imported_names(tree: ast.Module) -> set[str]:
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                names.update(alias.name.split("."))
        elif isinstance(node, ast.ImportFrom):
            if node.module is not None:
                names.update(node.module.split("."))
            names.update(
                alias.name.split(".")[0]
                for alias in node.names
                if node.module is not None
                and node.module.split(".")[0] == "scripts"
            )
    return names


def _discovery_aliases(tree: ast.Module) -> set[str]:
    aliases: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if alias.name.split(".")[-1] == "claim_standing_discovery":
                    aliases.add(alias.asname or alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom):
            for alias in node.names:
                if alias.name == "claim_standing_discovery":
                    aliases.add(alias.asname or alias.name)
    return aliases


# --- gate 12: static capability scan ----------------------------------------


def test_wiring_modules_import_only_the_declared_allowlist() -> None:
    assert not ALLOWED_IMPORTS & (
        FORBIDDEN_CAPABILITY_MODULES | PHASE_E_AND_READ_LEDGER_MODULES
    )
    for path in WIRING_MODULES:
        names = _imported_names(_module_ast(path))
        assert names <= ALLOWED_IMPORTS, (
            f"{path.name} imports outside the wiring allowlist: "
            f"{sorted(names - ALLOWED_IMPORTS)}"
        )


def test_discovery_reach_is_limited_to_the_pure_roster_constant() -> None:
    for path in WIRING_MODULES:
        tree = _module_ast(path)
        aliases = _discovery_aliases(tree)
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Attribute)
                and isinstance(node.value, ast.Name)
                and node.value.id in aliases
            ):
                assert node.attr in ALLOWED_DISCOVERY_ATTRIBUTES, (
                    f"{path.name} reaches discovery.{node.attr}; only "
                    f"{sorted(ALLOWED_DISCOVERY_ATTRIBUTES)} is allowed"
                )
            # An alias must not escape the attribute scan by rebinding or
            # dynamic lookup.
            if (
                isinstance(node, ast.Assign)
                and isinstance(node.value, ast.Name)
                and node.value.id in aliases
            ):
                raise AssertionError(
                    f"{path.name} rebinds a discovery alias"
                )
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "getattr"
            ):
                raise AssertionError(
                    f"{path.name} uses getattr(); the capability scan "
                    "requires static attribute access"
                )


def test_wiring_modules_perform_no_direct_writes_or_read_ledger_access() -> None:
    for path in WIRING_MODULES:
        tree = _module_ast(path)
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and isinstance(node.func, ast.Name)
                and node.func.id == "open"
            ):
                raise AssertionError(f"{path.name} calls open() directly")
            if (
                isinstance(node, ast.Attribute)
                and node.attr in WRITE_CAPABLE_ATTRIBUTES
            ):
                raise AssertionError(
                    f"{path.name} uses write-capable attribute {node.attr!r}; "
                    "all persistence must flow through the substrate writer"
                )
        source = path.read_text(encoding="utf-8")
        for marker in ("human_read_log", "human_read_source", "read_scope"):
            assert marker not in source, f"{path.name} touches {marker}"


# --- gate 12: end-to-end run leaves everything untouched --------------------


def _write_json(path: Path, value: object) -> Path:
    path.write_text(json.dumps(value, ensure_ascii=False), encoding="utf-8")
    return path


def test_end_to_end_wiring_creates_no_files_and_mutates_no_inputs(
    tmp_path, monkeypatch, capsys
) -> None:
    inputs = tmp_path / "inputs"
    inputs.mkdir()
    workdir = tmp_path / "work"
    workdir.mkdir()
    monkeypatch.chdir(workdir)

    row = _registry_row()
    decisions = _bound_decisions(row, _decisions())
    row_before = copy.deepcopy(row)
    decisions_before = copy.deepcopy(decisions)
    built_plan = plan_builder.bind_plan(row, decisions)
    substrate.validate_plan(built_plan)

    stance_plan = _plan_v1_1(stance=True)
    stance_plan["stance_plan"]["prompt_contract_version"] = (
        runner.PROMPT_CONTRACT_VERSION
    )
    _rehash_plan(stance_plan)
    retained = _retained()
    _rehash_input(retained, stance_plan)
    ledger_value = substrate.build_ledger(stance_plan, retained)
    record, _, events = runner.run_stance(
        stance_plan, ledger_value, transport=FakeTransport()
    )
    inputs_before = copy.deepcopy((stance_plan, retained, ledger_value, record))

    transmissions.build_transmission_ledger(
        stance_plan, retained, stance_transmissions=events, stance_record=record
    )
    freshness.assess_freshness(
        current_claim_text=stance_plan["claim"]["claim_text"],
        plan=stance_plan,
        candidate_ledger=ledger_value,
        stance_record=record,
    )

    row_file = _write_json(inputs / "row.json", row)
    decisions_file = _write_json(inputs / "decisions.json", decisions)
    plan_file = _write_json(inputs / "plan.json", stance_plan)
    input_file = _write_json(inputs / "input.json", retained)
    events_file = _write_json(inputs / "events.json", events)
    record_file = _write_json(inputs / "record.json", record)
    claim_file = inputs / "claim.txt"
    claim_file.write_text(
        stance_plan["claim"]["claim_text"], encoding="utf-8"
    )
    assert plan_builder.main(
        ["propose", "--registry-claim", str(row_file), "--decisions", str(decisions_file)]
    ) == 0
    assert plan_builder.main(
        ["bind", "--registry-claim", str(row_file), "--decisions", str(decisions_file)]
    ) == 0
    assert transmissions.main(
        [
            "build",
            "--query-plan", str(plan_file),
            "--retrieval-input", str(input_file),
            "--stance-transmissions", str(events_file),
            "--stance-record", str(record_file),
        ]
    ) == 0
    assert freshness.main(
        [
            "--current-claim-file", str(claim_file),
            "--query-plan", str(plan_file),
            "--candidate-ledger", str(_write_json(inputs / "ledger.json", ledger_value)),
            "--stance-record", str(record_file),
        ]
    ) == 0
    capsys.readouterr()

    assert row == row_before
    assert decisions == decisions_before
    assert (stance_plan, retained, ledger_value, record) == inputs_before
    assert list(workdir.iterdir()) == []


def test_declination_record_carries_no_verdict_or_gate_vocabulary() -> None:
    row = _registry_row()
    decisions = _bound_decisions(
        row, _decisions(decision="cancel", recorded_at="2026-08-14T01:05:00Z")
    )
    record = plan_builder.bind_plan(row, decisions)
    rendered = json.dumps(record).lower()
    for forbidden in ("verdict", "severity", "pass", "fail", "score"):
        assert forbidden not in rendered
