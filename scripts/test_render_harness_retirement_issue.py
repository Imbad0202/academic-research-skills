"""Tests for the manifest-backed harness-retirement issue renderer (#617)."""
from __future__ import annotations

import copy
import json
import subprocess
import sys
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "render_harness_retirement_issue.py"
MANIFEST_PATH = REPO_ROOT / "scripts" / "ars_phase_scope_manifest.json"
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "harness-retirement-monthly.yml"

sys.path.insert(0, str(REPO_ROOT / "scripts"))
from render_harness_retirement_issue import render_issue  # noqa: E402


@pytest.fixture
def manifest() -> dict:
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def test_current_manifest_renders_complete_bucket_a_inventory(manifest: dict) -> None:
    body = render_issue("2026-08", manifest)

    assert "All 23 Bucket A agents" in body
    assert "`deep-research` (×10):" in body
    assert "`academic-paper` (×7):" in body
    assert "`academic-paper-reviewer` (×6):" in body
    assert "`timeline_extraction_agent`" in body

    bucket_a_names = {
        name for name, row in manifest["agents"].items() if row["bucket"] == "A"
    }
    assert len(bucket_a_names) == 23
    for name in bucket_a_names:
        assert body.count(f"`{name}`") == 1


def test_added_bucket_a_agent_updates_total_and_group_without_code_change(
    manifest: dict,
) -> None:
    mutated = copy.deepcopy(manifest)
    mutated["agents"]["future_research_agent"] = {
        "bucket": "A",
        "skill": "deep-research",
        "phase": "9",
        "allowed_write_globs": ["phase9_*/**"],
    }

    body = render_issue("2026-08", mutated)

    assert "All 24 Bucket A agents" in body
    assert "`deep-research` (×11):" in body
    assert body.count("`future_research_agent`") == 1


def test_debt_categories_are_model_agnostic(manifest: dict) -> None:
    body = render_issue("2026-08", manifest).casefold()

    assert "capability-era workarounds" in body
    assert "verbose reasoning scaffolds" in body
    assert "sonnet" not in body
    assert "opus" not in body
    assert "claude-" not in body


@pytest.mark.parametrize("month", ["2026-00", "2026-13", "2026-8", "x\n## injected"])
def test_invalid_month_is_rejected(manifest: dict, month: str) -> None:
    with pytest.raises(ValueError, match="YYYY-MM"):
        render_issue(month, manifest)


def test_cli_writes_deterministic_body(tmp_path: Path, manifest: dict) -> None:
    output = tmp_path / "issue-body.md"
    result = subprocess.run(
        [
            sys.executable,
            str(SCRIPT),
            "--month",
            "2026-08",
            "--manifest",
            str(MANIFEST_PATH),
            "--output",
            str(output),
        ],
        text=True,
        capture_output=True,
        check=False,
    )

    assert result.returncode == 0, result.stderr
    assert output.read_text(encoding="utf-8") == render_issue("2026-08", manifest)


def test_workflow_delegates_scope_rendering_to_script(manifest: dict) -> None:
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

    assert "uses: actions/checkout@v4" in workflow
    assert "python3 scripts/render_harness_retirement_issue.py" in workflow
    assert "--output issue-body.md" in workflow
    assert "All 22 Bucket A" not in workflow
    assert "Sonnet 3" not in workflow
    assert "opus 4" not in workflow
    for name in manifest["agents"]:
        assert name not in workflow
