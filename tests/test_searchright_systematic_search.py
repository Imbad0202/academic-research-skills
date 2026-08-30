from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "systematic-search" / "SKILL.md"
EXAMPLE = ROOT / "examples" / "searchright" / "systematic-search-handoff.json"


def load_skill() -> tuple[dict[str, object], str]:
    text = SKILL.read_text(encoding="utf-8")
    match = re.match(r"\A---\n(.*?)\n---\n(.*)\Z", text, re.DOTALL)
    assert match is not None
    metadata = yaml.safe_load(match.group(1))
    assert isinstance(metadata, dict)
    return metadata, match.group(2)


def test_searchright_caller_is_exact_and_fail_closed() -> None:
    metadata, body = load_skill()
    skill_metadata = metadata["metadata"]
    assert isinstance(skill_metadata, dict)
    dependency = skill_metadata["external_dependency"]
    assert isinstance(dependency, dict)
    assert dependency["version"] == "0.1.0-alpha.1"
    assert re.fullmatch(r"[0-9a-f]{64}", str(dependency["package_sha256"]))
    assert re.fullmatch(r"[0-9a-f]{40}", str(dependency["source_revision"]))
    assert skill_metadata["data_access_level"] == "raw"
    assert skill_metadata["task_type"] == "open-ended"
    normalized = " ".join(body.lower().split())
    for phrase in (
        "stop automated tool invocation",
        "untrusted data",
        "live execution requires",
        "independent human press review",
        "final exclusion",
        "protocol amendment",
        "preserve searchright evidence levels",
    ):
        assert phrase in normalized


def test_searchright_caller_contains_no_provider_or_prisma_runtime() -> None:
    _, body = load_skill()
    assert not re.search(r"https?://[^\s`]+/(?:api|search|query)", body, re.IGNORECASE)
    assert "requests.get" not in body
    assert "fetch(" not in body
    assert "records_identified =" not in body


def test_synthetic_handoff_is_bounded_and_non_live() -> None:
    handoff = json.loads(EXAMPLE.read_text(encoding="utf-8"))
    assert handoff["schema_version"] == "org.searchright.agent-handoff.v1"
    assert handoff["from_role"] == "question-framer"
    assert handoff["to_role"] == "information-specialist"
    assert handoff["context_policy"] == "minimum_necessary"
    assert handoff["execution_mode"] is None
    assert [item["purpose"] for item in handoff["approval_references"]] == ["review_plan"]
    artifact = handoff["artifacts"][0]
    assert artifact["path"].startswith("synthetic/")
    assert len(bytes.fromhex(artifact["sha256"])) == hashlib.sha256().digest_size
