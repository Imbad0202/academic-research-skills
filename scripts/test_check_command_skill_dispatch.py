"""Regressions for lost command dispatch and cwd-dependent references."""
from pathlib import Path
import shutil
import json
import os
import subprocess
import re

import pytest

from scripts.check_command_skill_dispatch import check

REPO = Path(__file__).resolve().parents[1]


@pytest.fixture
def root(tmp_path):
    shutil.copytree(REPO / "commands", tmp_path / "commands")
    for name in ("academic-paper", "academic-paper-reviewer", "academic-pipeline", "deep-research"):
        (tmp_path / name).mkdir()
        (tmp_path / name / "SKILL.md").write_text("skill")
    return tmp_path


def test_shipped_commands_pass_from_unrelated_cwd(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert check(REPO) == []


@pytest.mark.parametrize("name", ["ars-citation-check", "ars-full", "ars-reviewer", "ars-revision-coach"])
def test_lost_invocation_fails(root, name):
    path = root / "commands" / f"{name}.md"
    path.write_text(path.read_text().replace("First invoke the Skill tool", "Mention the skill"))
    assert any("missing explicit Skill call" in error for error in check(root))


@pytest.mark.parametrize("reference", ["MODE_REGISTRY.md", "academic-paper/SKILL.md"])
@pytest.mark.parametrize("quote", ["`", ""])
def test_bare_reference_fails_even_when_rooted_reference_remains(root, reference, quote):
    path = root / "commands/ars-citation-check.md"
    path.write_text(path.read_text() + f"\nRead {quote}{reference}{quote}.\n")
    assert any("unrooted plugin reference" in error for error in check(root))


def test_wrong_target_fails(root):
    path = root / "commands/ars-citation-check.md"
    path.write_text(path.read_text().replace("academic-research-skills:academic-paper", "academic-research-skills:deep-research"))
    assert any("missing explicit Skill call" in error for error in check(root))


@pytest.mark.parametrize("replacement", ["", "disable-model-invocation: false", "disable-model-invocation: true\ndisable-model-invocation: false"])
def test_command_cannot_compete_with_core_skill(root, replacement):
    path = root / "commands/ars-citation-check.md"
    path.write_text(path.read_text().replace("disable-model-invocation: true", replacement))
    assert any("user-invocable only" in error for error in check(root))


def test_missing_target_file_fails(root):
    (root / "academic-paper/SKILL.md").unlink()
    assert any("target skill file does not exist" in error for error in check(root))


def test_missing_command_does_not_pass_vacuously(root):
    (root / "commands/ars-citation-check.md").unlink()
    assert any("missing command" in error for error in check(root))


def test_new_command_requires_classification(root):
    (root / "commands/ars-new.md").write_text("Trigger a skill.")
    assert any("classify new command" in error for error in check(root))


@pytest.mark.parametrize("source", ["startup", "clear", "resume", "compact"])
def test_session_announce_routes_models_to_core_skills(source):
    env = {k: v for k, v in os.environ.items() if k != "CLAUDE_PLUGIN_ROOT"}
    result = subprocess.run(
        ["bash", str(REPO / "scripts/announce-ars-loaded.sh")],
        input=json.dumps({"source": source}), text=True, capture_output=True,
        env=env, check=True,
    )
    context = json.loads(result.stdout)["hookSpecificOutput"]["additionalContext"]
    assert "mode slash commands above are for the user to type" in context
    for target in ("academic-paper", "academic-paper-reviewer", "deep-research", "academic-pipeline"):
        assert f"academic-research-skills:{target}" in context
    assert "Requests outside academic research and writing do not invoke ARS" in context


def test_citation_grader_matches_only_core_skill_name():
    import yaml

    paths = sorted((REPO / "plugin-evals-citation-check").glob("*/graders/skill-fired.md"))
    assert len(paths) == 6
    for path in paths:
        grader = yaml.safe_load(path.read_text().split("---", 2)[1])
        pattern = grader["input_match"]
        assert re.search(pattern, json.dumps({"skill": "academic-research-skills:academic-paper"}))
        for name in ("ars-citation-check", "academic-paper-reviewer", "academic-pipeline"):
            assert not re.search(pattern, json.dumps({"skill": f"academic-research-skills:{name}"}))
