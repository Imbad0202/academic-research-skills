"""Mutation tests for check_data_flows.py (#758).

Two layers:
- the real tree must pass (baseline), and
- a synthetic fixture repo exercises each invariant's fire/no-fire edge
  without depending on the real script inventory.
"""
from __future__ import annotations

from pathlib import Path

import pytest

from check_data_flows import (
    DOC_RELPATH,
    run_all_checks,
)

REPO_ROOT = Path(__file__).resolve().parent.parent


def _write(root: Path, rel: str, content: str) -> None:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


@pytest.fixture()
def fixture_repo(tmp_path: Path) -> Path:
    """Minimal repo: one documented network script, one non-network script,
    one network-importing test file (exempt), one documented curl shell
    script, and the three inbound-link surfaces."""
    _write(
        tmp_path,
        "docs/DATA_FLOWS.md",
        "# Data Flows\n\n"
        "| Touchpoint |\n|---|\n"
        "| `scripts/net_client.py` row |\n"
        "| `scripts/fetch_thing.sh` row |\n",
    )
    _write(
        tmp_path,
        "scripts/net_client.py",
        "import urllib.request\n\n\ndef go(url):\n"
        "    return urllib.request.urlopen(url)\n",
    )
    _write(
        tmp_path,
        "scripts/pure_local.py",
        "import json\nimport urllib.parse\n\nVALUE = urllib.parse.quote('x')\n",
    )
    _write(
        tmp_path,
        "scripts/test_net_helper.py",
        "import urllib.request\n",
    )
    _write(
        tmp_path,
        "scripts/fetch_thing.sh",
        "#!/bin/sh\ncurl -fsSL https://example.invalid/x\n",
    )
    _write(
        tmp_path,
        "scripts/no_net.sh",
        "#!/bin/sh\n# curl is only mentioned in this comment\necho ok\n",
    )
    link = "[docs/DATA_FLOWS.md](docs/DATA_FLOWS.md)"
    _write(tmp_path, "README.md", f"# Fixture\n\nSee {link}.\n")
    _write(tmp_path, "SECURITY.md", f"# Security\n\nMap: {link}.\n")
    _write(tmp_path, "THIRD_PARTY.md", f"# Third party\n\nMap: {link}.\n")
    return tmp_path


def test_real_tree_passes() -> None:
    assert run_all_checks(REPO_ROOT) == []


def test_fixture_baseline_passes(fixture_repo: Path) -> None:
    assert run_all_checks(fixture_repo) == []


def test_missing_doc_is_single_fatal_error(fixture_repo: Path) -> None:
    (fixture_repo / DOC_RELPATH).unlink()
    errors = run_all_checks(fixture_repo)
    assert len(errors) == 1
    assert "missing" in errors[0]


def test_df1_unnamed_network_script_fires(fixture_repo: Path) -> None:
    _write(
        fixture_repo,
        "scripts/new_resolver.py",
        "from urllib import request\n\n\ndef go(url):\n"
        "    return request.urlopen(url)\n",
    )
    errors = run_all_checks(fixture_repo)
    assert any("DF-1" in e and "new_resolver.py" in e for e in errors)


def test_df1_string_mention_without_import_not_flagged(
    fixture_repo: Path,
) -> None:
    # A no-call guard that merely NAMES the module in a forbidden list must
    # not be treated as a network touchpoint (AST, not grep).
    _write(
        fixture_repo,
        "scripts/no_call_guard.py",
        'FORBIDDEN = {"urllib.request", "http.client"}\n',
    )
    assert run_all_checks(fixture_repo) == []


def test_df1_test_files_exempt(fixture_repo: Path) -> None:
    # test_net_helper.py in the fixture already imports urllib.request and
    # is not named in the doc; the baseline passing proves the exemption.
    assert run_all_checks(fixture_repo) == []


def test_df2_unnamed_curl_script_fires(fixture_repo: Path) -> None:
    _write(
        fixture_repo,
        "scripts/new_fetch.sh",
        "#!/bin/sh\ncurl -s https://example.invalid/y\n",
    )
    errors = run_all_checks(fixture_repo)
    assert any("DF-2" in e and "new_fetch.sh" in e for e in errors)


def test_df2_commented_curl_not_flagged(fixture_repo: Path) -> None:
    # no_net.sh in the fixture mentions curl only in a comment; baseline
    # passing proves comments don't count.
    assert run_all_checks(fixture_repo) == []


def test_df3_removed_readme_link_fires(fixture_repo: Path) -> None:
    _write(fixture_repo, "README.md", "# Fixture\n\nNo link here.\n")
    errors = run_all_checks(fixture_repo)
    assert any("DF-3" in e and "README.md" in e for e in errors)


def test_df3_label_keeps_name_but_target_moves_fires(
    fixture_repo: Path,
) -> None:
    _write(
        fixture_repo,
        "SECURITY.md",
        "# Security\n\n[docs/DATA_FLOWS.md](docs/OTHER.md)\n",
    )
    errors = run_all_checks(fixture_repo)
    assert any("DF-3" in e and "SECURITY.md" in e for e in errors)


def test_df3_link_inside_fence_fires(fixture_repo: Path) -> None:
    _write(
        fixture_repo,
        "THIRD_PARTY.md",
        "# Third party\n\n```text\n"
        "[docs/DATA_FLOWS.md](docs/DATA_FLOWS.md)\n```\n",
    )
    errors = run_all_checks(fixture_repo)
    assert any("DF-3" in e and "THIRD_PARTY.md" in e for e in errors)


def test_df3_commented_out_link_fires(fixture_repo: Path) -> None:
    _write(
        fixture_repo,
        "THIRD_PARTY.md",
        "# Third party\n\n"
        "<!-- [docs/DATA_FLOWS.md](docs/DATA_FLOWS.md) -->\n",
    )
    errors = run_all_checks(fixture_repo)
    assert any("DF-3" in e and "THIRD_PARTY.md" in e for e in errors)
