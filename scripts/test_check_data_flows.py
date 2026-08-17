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
    _write(
        tmp_path,
        "docs/SETUP.md",
        "# Setup\n\nSee [DATA_FLOWS.md](DATA_FLOWS.md).\n",
    )
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


def test_df1_exemption_is_name_based(fixture_repo: Path) -> None:
    # The same network-importing body fires under a non-test_ name and stays
    # quiet under the test_ name — proving the exemption is name-based, not
    # content-based.
    body = (fixture_repo / "scripts/test_net_helper.py").read_text(
        encoding="utf-8"
    )
    assert run_all_checks(fixture_repo) == []  # test_ name: exempt
    _write(fixture_repo, "scripts/net_helper.py", body)
    errors = run_all_checks(fixture_repo)
    assert any("DF-1" in e and "net_helper.py" in e for e in errors)


def test_df1_recursive_scan_reaches_subdirectories(fixture_repo: Path) -> None:
    _write(
        fixture_repo,
        "scripts/verification_gate/sub_resolver.py",
        "import urllib.request\n",
    )
    errors = run_all_checks(fixture_repo)
    assert any("DF-1" in e and "sub_resolver.py" in e for e in errors)


def test_df1_from_urllib_parse_only_not_flagged(fixture_repo: Path) -> None:
    # pure_local.py imports urllib.parse only; adding the same idiom via
    # `from urllib import parse` must also stay quiet.
    _write(
        fixture_repo,
        "scripts/parse_only.py",
        "from urllib import parse\nVALUE = parse.quote('x')\n",
    )
    assert run_all_checks(fixture_repo) == []


def test_df1_from_urllib_import_request_fires(fixture_repo: Path) -> None:
    _write(
        fixture_repo,
        "scripts/idiom_resolver.py",
        "from urllib import request\n\n\ndef go(url):\n"
        "    return request.urlopen(url)\n",
    )
    errors = run_all_checks(fixture_repo)
    assert any("DF-1" in e and "idiom_resolver.py" in e for e in errors)


def test_df2_unnamed_curl_script_fires(fixture_repo: Path) -> None:
    _write(
        fixture_repo,
        "scripts/new_fetch.sh",
        "#!/bin/sh\ncurl -s https://example.invalid/y\n",
    )
    errors = run_all_checks(fixture_repo)
    assert any("DF-2" in e and "new_fetch.sh" in e for e in errors)


def test_df2_commented_curl_not_flagged_until_uncommented(
    fixture_repo: Path,
) -> None:
    # no_net.sh mentions curl only in a comment (quiet); uncommenting the
    # same invocation fires — proving the comment-stripping is load-bearing.
    assert run_all_checks(fixture_repo) == []
    _write(
        fixture_repo,
        "scripts/no_net.sh",
        "#!/bin/sh\ncurl -s https://example.invalid/z\n",
    )
    errors = run_all_checks(fixture_repo)
    assert any("DF-2" in e and "no_net.sh" in e for e in errors)


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


def test_df1_basename_substring_collision_fires(fixture_repo: Path) -> None:
    # The doc names scripts/net_client.py; a NEW scripts/client.py must not
    # ride on that substring — coverage is full-relative-path based (codex
    # R1 finding).
    _write(
        fixture_repo,
        "scripts/client.py",
        "import urllib.request\n",
    )
    errors = run_all_checks(fixture_repo)
    assert any("DF-1" in e and "scripts/client.py" in e for e in errors)


def test_df2_nested_shell_script_fires(fixture_repo: Path) -> None:
    _write(
        fixture_repo,
        "scripts/tools/fetch_nested.sh",
        "#!/bin/sh\ncurl -s https://example.invalid/n\n",
    )
    errors = run_all_checks(fixture_repo)
    assert any("DF-2" in e and "fetch_nested.sh" in e for e in errors)


def test_df2_path_qualified_curl_fires(fixture_repo: Path) -> None:
    _write(
        fixture_repo,
        "scripts/abs_fetch.sh",
        "#!/bin/sh\n/usr/bin/curl -s https://example.invalid/a\n",
    )
    errors = run_all_checks(fixture_repo)
    assert any("DF-2" in e and "abs_fetch.sh" in e for e in errors)


def test_df2_quoted_instructional_curl_not_flagged(fixture_repo: Path) -> None:
    _write(
        fixture_repo,
        "scripts/instruct.sh",
        '#!/bin/sh\necho "to fetch manually, run curl -s URL"\n',
    )
    assert run_all_checks(fixture_repo) == []


def test_df2_curl_inside_command_substitution_fires(
    fixture_repo: Path,
) -> None:
    # `resp="$(curl ...)"` executes curl even though the whole expression
    # sits inside double quotes — quote masking must not hide it (codex R2
    # finding).
    _write(
        fixture_repo,
        "scripts/subst_fetch.sh",
        '#!/bin/sh\nresp="$(curl -fsSL https://example.invalid/s)"\n',
    )
    errors = run_all_checks(fixture_repo)
    assert any("DF-2" in e and "subst_fetch.sh" in e for e in errors)


def test_df2_commented_command_substitution_not_flagged(
    fixture_repo: Path,
) -> None:
    # A full comment line containing $(curl ...) executes nothing and must
    # not fire.
    _write(
        fixture_repo,
        "scripts/doc_example.sh",
        '#!/bin/sh\n# example: resp="$(curl -fsSL URL)"\necho ok\n',
    )
    assert run_all_checks(fixture_repo) == []


def test_df2_argument_position_curl_not_flagged(fixture_repo: Path) -> None:
    # `command -v curl` (a preflight) and `echo curl` mention curl only in
    # argument position — no curl process runs (codex R3 finding).
    _write(
        fixture_repo,
        "scripts/preflight.sh",
        "#!/bin/sh\nif ! command -v curl >/dev/null; then\n"
        "  echo curl missing\nfi\n",
    )
    assert run_all_checks(fixture_repo) == []


def test_df2_env_prefixed_curl_fires(fixture_repo: Path) -> None:
    # `VAR=x curl ...` is still a curl invocation in command position.
    _write(
        fixture_repo,
        "scripts/env_fetch.sh",
        "#!/bin/sh\nLC_ALL=C curl -s https://example.invalid/e\n",
    )
    errors = run_all_checks(fixture_repo)
    assert any("DF-2" in e and "env_fetch.sh" in e for e in errors)


def test_df2_curl_behind_control_keywords_fires(fixture_repo: Path) -> None:
    # `if curl …; then` / `while ! curl …; do` keep curl in command
    # position behind shell control words (codex R4 finding).
    _write(
        fixture_repo,
        "scripts/cond_fetch.sh",
        "#!/bin/sh\nif curl -s https://example.invalid/c; then\n"
        "  echo ok\nfi\n",
    )
    errors = run_all_checks(fixture_repo)
    assert any("DF-2" in e and "cond_fetch.sh" in e for e in errors)


def test_df2_option_bearing_control_word_fires(fixture_repo: Path) -> None:
    # `time -p curl …` — the option token must not shadow the command head
    # (codex R5 finding).
    _write(
        fixture_repo,
        "scripts/timed_fetch.sh",
        "#!/bin/sh\ntime -p curl -s https://example.invalid/t\n",
    )
    errors = run_all_checks(fixture_repo)
    assert any("DF-2" in e and "timed_fetch.sh" in e for e in errors)


def test_df2_control_keywords_alone_not_flagged(fixture_repo: Path) -> None:
    _write(
        fixture_repo,
        "scripts/plain_cond.sh",
        "#!/bin/sh\nif true; then\n  echo ok\nfi\n",
    )
    assert run_all_checks(fixture_repo) == []


def test_df3_image_syntax_does_not_satisfy(fixture_repo: Path) -> None:
    # `![map](docs/DATA_FLOWS.md)` renders an image, not an anchor — a
    # one-character typo must not keep DF-3 green (codex R3 finding).
    _write(
        fixture_repo,
        "THIRD_PARTY.md",
        "# Third party\n\n![map](docs/DATA_FLOWS.md)\n",
    )
    errors = run_all_checks(fixture_repo)
    assert any("DF-3" in e and "THIRD_PARTY.md" in e for e in errors)


def test_df3_link_inside_code_span_fires(fixture_repo: Path) -> None:
    # A link inside inline backticks renders literally, not as a link
    # (codex R1 finding).
    _write(
        fixture_repo,
        "SECURITY.md",
        "# Security\n\n`[map](docs/DATA_FLOWS.md)`\n",
    )
    errors = run_all_checks(fixture_repo)
    assert any("DF-3" in e and "SECURITY.md" in e for e in errors)


def test_df3_setup_link_removed_fires(fixture_repo: Path) -> None:
    _write(fixture_repo, "docs/SETUP.md", "# Setup\n\nNo link.\n")
    errors = run_all_checks(fixture_repo)
    assert any("DF-3" in e and "SETUP.md" in e for e in errors)


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
