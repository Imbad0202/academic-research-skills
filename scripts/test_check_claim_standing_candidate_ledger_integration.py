"""Mutation tests for the static #655 Track A integration guard."""
from __future__ import annotations

import shutil
from pathlib import Path

import pytest

from scripts import check_claim_standing_candidate_ledger_integration as guard


ROOT = Path(__file__).resolve().parents[1]
COPIED = tuple(
    dict.fromkeys(
        (
            *(guard.SCHEMA_DIR / name for name in guard.SCHEMAS),
            guard.RUNTIME,
            guard.PROTOCOL,
            guard.PHASE_E_PROTOCOL,
            guard.DESIGN,
            guard.CONTRACT_README,
            guard.MANIFEST,
            guard.WORKFLOW,
            guard.CHANGELOG,
            *guard.FIXTURES,
            *guard.RESOLVER_HASHES,
        )
    )
)


def _tree(tmp_path: Path) -> Path:
    root = tmp_path / "repo"
    for relative in COPIED:
        target = root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(ROOT / relative, target)
    return root


def _replace(root: Path, relative: Path, old: str, new: str) -> None:
    path = root / relative
    text = path.read_text(encoding="utf-8")
    assert old in text
    path.write_text(text.replace(old, new), encoding="utf-8")


def test_current_repository_passes() -> None:
    assert guard.run_checks(ROOT) == []


def test_schema_identity_and_closure_are_pinned(tmp_path: Path) -> None:
    root = _tree(tmp_path)
    schema = guard.SCHEMA_DIR / "query_plan.schema.json"
    _replace(root, schema, "claim-standing-query-plan/1.0", "claim-standing-query-plan/2.0")
    _replace(root, schema, '"additionalProperties": false', '"additionalProperties": true')
    errors = guard.run_checks(root)
    assert any("schema_version drifted" in error for error in errors)
    assert any("root must remain closed" in error for error in errors)


def test_shared_contract_definitions_and_track_boundary_are_pinned(tmp_path: Path) -> None:
    root = _tree(tmp_path)
    candidate = guard.SCHEMA_DIR / "candidate_ledger.schema.json"
    _replace(root, candidate, '"returned_count": { "type": "integer"', '"returned_count": { "type": "number"')
    errors = guard.run_checks(root)
    assert any("shared attempt/attempt definitions drifted" in error for error in errors)
    root = _tree(tmp_path / "boundary")
    query = guard.SCHEMA_DIR / "query_plan.schema.json"
    _replace(root, query, '"created_at": { "$ref":', '"stance": { "type": "string" },\n    "created_at": { "$ref":')
    assert any("Track B/live fields entered Track A" in error for error in guard.run_checks(root))


def test_network_or_dispatch_capability_is_rejected(tmp_path: Path) -> None:
    root = _tree(tmp_path)
    path = root / guard.RUNTIME
    path.write_text("import requests\n" + path.read_text(encoding="utf-8"), encoding="utf-8")
    errors = guard.run_checks(root)
    assert any("non-allowlisted transport/model/process-capable imports" in error for error in errors)
    _replace(root, guard.RUNTIME, 'add_parser("build"', 'add_parser("dispatch"')
    assert any("forbidden capability marker" in error for error in guard.run_checks(root))


def test_non_allowlisted_and_dynamic_imports_are_rejected(tmp_path: Path) -> None:
    root = _tree(tmp_path / "direct")
    path = root / guard.RUNTIME
    path.write_text("import httpx\n" + path.read_text(encoding="utf-8"), encoding="utf-8")
    errors = guard.run_checks(root)
    assert any("non-allowlisted" in error and "httpx" in error for error in errors)

    root = _tree(tmp_path / "dynamic")
    path = root / guard.RUNTIME
    path.write_text(
        "_process_module = __import__('subprocess')\n"
        + path.read_text(encoding="utf-8"),
        encoding="utf-8",
    )
    errors = guard.run_checks(root)
    assert any("dynamic import, introspection" in error for error in errors)


@pytest.mark.parametrize(
    ("payload", "symbol"),
    [
        (
            "from sys import modules as registry\n"
            "registry['os'].spawnl(0, '/bin/true', 'true')\n",
            "sys.modules",
        ),
        (
            "from sys import _getframe as frame\n"
            "_scope = frame().f_globals\n",
            "sys._getframe",
        ),
    ],
)
def test_from_import_requires_an_exact_per_module_symbol_allowlist(
    tmp_path: Path, payload: str, symbol: str
) -> None:
    root = _tree(tmp_path)
    path = root / guard.RUNTIME
    path.write_text(payload + path.read_text(encoding="utf-8"), encoding="utf-8")
    errors = guard.run_checks(root)
    assert any("non-allowlisted" in error and symbol in error for error in errors)


@pytest.mark.parametrize(
    "payload",
    [
        "_runner = eval\n_runner('1 + 1')\n",
        "sys.modules['os'].system('true')\n",
        (
            "getattr(globals()['__built' + 'ins__'], "
            "'__im' + 'port__')('socket')\n"
        ),
    ],
)
def test_alias_introspection_and_allowed_module_capability_bypasses_are_rejected(
    tmp_path: Path, payload: str
) -> None:
    root = _tree(tmp_path)
    path = root / guard.RUNTIME
    path.write_text(payload + path.read_text(encoding="utf-8"), encoding="utf-8")
    errors = guard.run_checks(root)
    assert any("dynamic import, introspection" in error for error in errors)


@pytest.mark.parametrize(
    "payload",
    [
        "argparse._os.spawnl(0, '/bin/true', 'true')\n",
        "hashlib.__spec__.loader.load_module('os')\n",
        (
            "import argparse as parser_alias\n"
            "parser_alias._os.spawnl(0, '/bin/true', 'true')\n"
        ),
        "_escaped_module = argparse\n",
        "import hashlib as hash_alias\n_escaped_module = hash_alias\n",
        "_escaped_attribute = hashlib.sha256\n",
        "_escaped_stream = sys.stderr\n",
        "os.system('true')\n",
        "os.O_EXCL = 0\n",
        "del os.O_NOFOLLOW\n",
    ],
)
def test_direct_module_uses_are_exact_and_cannot_escape(
    tmp_path: Path, payload: str
) -> None:
    root = _tree(tmp_path)
    path = root / guard.RUNTIME
    path.write_text(payload + path.read_text(encoding="utf-8"), encoding="utf-8")
    errors = guard.run_checks(root)
    assert any("exact current-use" in error for error in errors)


def test_safe_direct_module_alias_is_tracked_and_allowed(tmp_path: Path) -> None:
    root = _tree(tmp_path)
    _replace(root, guard.RUNTIME, "import hashlib", "import hashlib as hash_alias")
    path = root / guard.RUNTIME
    path.write_text(
        path.read_text(encoding="utf-8").replace(
            "hashlib.sha256", "hash_alias.sha256"
        ),
        encoding="utf-8",
    )
    assert guard.run_checks(root) == []


@pytest.mark.parametrize(
    "payload",
    [
        "hashlib = object()\n",
        "def escape(os):\n    return os.open('/tmp/x', 0)\n",
        "from pathlib import Path as json\n",
    ],
)
def test_direct_module_bindings_cannot_be_shadowed(
    tmp_path: Path, payload: str
) -> None:
    root = _tree(tmp_path)
    path = root / guard.RUNTIME
    path.write_text(payload + path.read_text(encoding="utf-8"), encoding="utf-8")
    errors = guard.run_checks(root)
    assert any("cannot be shadowed" in error for error in errors)


def test_existing_resolver_change_is_rejected(tmp_path: Path) -> None:
    root = _tree(tmp_path)
    path = root / next(iter(guard.RESOLVER_HASHES))
    path.write_text(path.read_text(encoding="utf-8") + "\n# drift\n", encoding="utf-8")
    assert any("existing resolver changed" in error for error in guard.run_checks(root))


def test_documentation_manifest_and_workflow_markers_are_required(tmp_path: Path) -> None:
    root = _tree(tmp_path)
    _replace(root, guard.PROTOCOL, "STANCE CLASSIFICATION UNMEASURED", "MEASURED")
    _replace(
        root,
        guard.MANIFEST,
        'id = "655-claim-standing-candidate-ledger"',
        'id = "removed"',
    )
    _replace(
        root,
        guard.WORKFLOW,
        "Check claim-standing candidate-ledger integration (#655)",
        "removed",
    )
    errors = guard.run_checks(root)
    assert any(str(guard.PROTOCOL) in error for error in errors)
    assert any(str(guard.MANIFEST) in error for error in errors)
    assert any(str(guard.WORKFLOW) in error for error in errors)


def test_phase_e_probe_offer_markers_are_required(tmp_path: Path) -> None:
    root = _tree(tmp_path)
    _replace(
        root,
        guard.PHASE_E_PROTOCOL,
        "`ALL` is not permission to probe every claim",
        "ALL rows may be probed",
    )
    errors = guard.run_checks(root)
    assert any(str(guard.PHASE_E_PROTOCOL) in error for error in errors)


def test_stale_deferred_wiring_sentence_is_forbidden(tmp_path: Path) -> None:
    root = _tree(tmp_path)
    path = root / guard.PROTOCOL
    path.write_text(
        path.read_text(encoding="utf-8")
        + "\nA dedicated contract is deferred to the pipeline-wiring slice.\n",
        encoding="utf-8",
    )
    errors = guard.run_checks(root)
    assert any("must not appear" in error for error in errors)
