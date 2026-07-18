"""Tests for scripts/ars_update_check.sh (#544) and its announce integration.

Hermetic: the remote is a file:// URL fixture, the state dir is a tmpdir,
CLAUDE_PLUGIN_ROOT is a fixture directory. No network access anywhere.
Spec: docs/design/2026-07-18-544-update-reminder-spec.md
"""
import json
import os
import shutil
import subprocess
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
CHECKER = REPO_ROOT / "scripts" / "ars_update_check.sh"
ANNOUNCE = REPO_ROOT / "scripts" / "announce-ars-loaded.sh"

STRIP_VARS = (
    "ARS_UPDATE_CHECK",
    "ARS_UPDATE_CHECK_STATE_DIR",
    "ARS_UPDATE_CHECK_REMOTE_URL",
    "CLAUDE_PLUGIN_ROOT",
)


def base_env():
    """Ambient environment minus every #544 variable, so tests fully control them."""
    return {k: v for k, v in os.environ.items() if k not in STRIP_VARS}


def make_plugin_root(tmp_path, version, name="plugin_root", with_checker=True):
    root = tmp_path / name
    (root / ".claude-plugin").mkdir(parents=True)
    (root / ".claude-plugin" / "plugin.json").write_text(
        json.dumps({"name": "academic-research-skills", "version": version}) + "\n"
    )
    if with_checker:
        (root / "scripts").mkdir()
        shutil.copy2(CHECKER, root / "scripts" / "ars_update_check.sh")
    return root


def make_remote(tmp_path, version, name="remote_plugin.json"):
    remote = tmp_path / name
    remote.write_text(
        json.dumps({"name": "academic-research-skills", "version": version}) + "\n"
    )
    return "file://" + str(remote)


def run_checker(plugin_root=None, remote_url=None, state_dir=None, extra_env=None):
    env = base_env()
    if plugin_root is not None:
        env["CLAUDE_PLUGIN_ROOT"] = str(plugin_root)
    if remote_url is not None:
        env["ARS_UPDATE_CHECK_REMOTE_URL"] = remote_url
    if state_dir is not None:
        env["ARS_UPDATE_CHECK_STATE_DIR"] = str(state_dir)
    if extra_env:
        env.update(extra_env)
    return subprocess.run(
        ["bash", str(CHECKER)], capture_output=True, text=True, env=env, timeout=30
    )


def _write_cache(state_dir, line, age_seconds=0):
    state_dir.mkdir(parents=True, exist_ok=True)
    cache = state_dir / "update-check"
    cache.write_text(line + "\n")
    if age_seconds:
        past = time.time() - age_seconds
        os.utime(cache, (past, past))
    return cache


# ---------------------------------------------------------------- core paths


def test_kill_switch_disables_everything(tmp_path):
    root = make_plugin_root(tmp_path, "3.17.0")
    state = tmp_path / "state"
    r = run_checker(
        plugin_root=root,
        remote_url=make_remote(tmp_path, "9.9.9"),
        state_dir=state,
        extra_env={"ARS_UPDATE_CHECK": "0"},
    )
    assert r.returncode == 0
    assert r.stdout == ""
    assert not (state / "update-check").exists()


def test_no_plugin_root_is_silent(tmp_path):
    state = tmp_path / "state"
    r = run_checker(remote_url=make_remote(tmp_path, "9.9.9"), state_dir=state)
    assert r.returncode == 0
    assert r.stdout == ""
    assert not (state / "update-check").exists()


def test_home_unset_no_state_dir_is_silent(tmp_path):
    # [I-1] HOME unset + no ARS_UPDATE_CHECK_STATE_DIR: exit 0, silent, no fetch.
    root = make_plugin_root(tmp_path, "3.17.0")
    env = base_env()
    env.pop("HOME", None)
    env["CLAUDE_PLUGIN_ROOT"] = str(root)
    env["ARS_UPDATE_CHECK_REMOTE_URL"] = make_remote(tmp_path, "9.9.9")
    r = subprocess.run(
        ["bash", str(CHECKER)], capture_output=True, text=True, env=env, timeout=30
    )
    assert r.returncode == 0
    assert r.stdout == ""
    assert r.stderr == ""


def test_up_to_date_silent_and_caches(tmp_path):
    root = make_plugin_root(tmp_path, "3.17.0")
    state = tmp_path / "state"
    r = run_checker(
        plugin_root=root,
        remote_url=make_remote(tmp_path, "3.17.0"),
        state_dir=state,
    )
    assert r.returncode == 0
    assert r.stdout == ""
    assert r.stderr == ""
    assert (state / "update-check").read_text().strip() == "UP_TO_DATE 3.17.0 3.17.0"


def test_update_available_token_and_cache(tmp_path):
    root = make_plugin_root(tmp_path, "3.17.0")
    state = tmp_path / "state"
    r = run_checker(
        plugin_root=root,
        remote_url=make_remote(tmp_path, "3.18.0"),
        state_dir=state,
    )
    assert r.returncode == 0
    assert r.stdout.strip() == "UPDATE_AVAILABLE 3.17.0 3.18.0"
    assert r.stderr == ""
    assert (
        state / "update-check"
    ).read_text().strip() == "UPDATE_AVAILABLE 3.17.0 3.18.0"


# ------------------------------------------------- cache + failure semantics


def test_fresh_update_available_cache_renders_without_fetch(tmp_path):
    root = make_plugin_root(tmp_path, "3.17.0")
    state = tmp_path / "state"
    _write_cache(state, "UPDATE_AVAILABLE 3.17.0 3.18.0")
    # The remote holds a THIRD version: if the checker fetched, both the
    # token and the cache would say 3.19.0. They must not.
    r = run_checker(
        plugin_root=root,
        remote_url=make_remote(tmp_path, "3.19.0"),
        state_dir=state,
    )
    assert r.stdout.strip() == "UPDATE_AVAILABLE 3.17.0 3.18.0"
    assert (
        state / "update-check"
    ).read_text().strip() == "UPDATE_AVAILABLE 3.17.0 3.18.0"


def test_fresh_up_to_date_cache_suppresses_fetch(tmp_path):
    root = make_plugin_root(tmp_path, "3.17.0")
    state = tmp_path / "state"
    _write_cache(state, "UP_TO_DATE 3.17.0 3.17.0")
    r = run_checker(
        plugin_root=root,
        remote_url=make_remote(tmp_path, "3.18.0"),
        state_dir=state,
    )
    assert r.stdout == ""
    assert (state / "update-check").read_text().strip() == "UP_TO_DATE 3.17.0 3.17.0"


def test_expired_cache_refetches(tmp_path):
    root = make_plugin_root(tmp_path, "3.17.0")
    state = tmp_path / "state"
    _write_cache(state, "UP_TO_DATE 3.17.0 3.17.0", age_seconds=25 * 3600)
    r = run_checker(
        plugin_root=root,
        remote_url=make_remote(tmp_path, "3.18.0"),
        state_dir=state,
    )
    assert r.stdout.strip() == "UPDATE_AVAILABLE 3.17.0 3.18.0"
    assert (
        state / "update-check"
    ).read_text().strip() == "UPDATE_AVAILABLE 3.17.0 3.18.0"


def test_expired_cache_unreachable_remote_is_silent_and_preserved(tmp_path):
    root = make_plugin_root(tmp_path, "3.17.0")
    state = tmp_path / "state"
    _write_cache(state, "UPDATE_AVAILABLE 3.17.0 3.18.0", age_seconds=25 * 3600)
    r = run_checker(
        plugin_root=root,
        remote_url="file://" + str(tmp_path / "nonexistent.json"),
        state_dir=state,
    )
    assert r.returncode == 0
    assert r.stdout == ""
    assert (
        state / "update-check"
    ).read_text().strip() == "UPDATE_AVAILABLE 3.17.0 3.18.0"


def test_malformed_remote_is_silent_cache_untouched(tmp_path):
    root = make_plugin_root(tmp_path, "3.17.0")
    state = tmp_path / "state"
    bad = tmp_path / "bad.json"
    bad.write_text("<html>rate limited</html>\n")
    r = run_checker(plugin_root=root, remote_url="file://" + str(bad), state_dir=state)
    assert r.returncode == 0
    assert r.stdout == ""
    assert not (state / "update-check").exists()


def test_corrupt_cache_refetches(tmp_path):
    root = make_plugin_root(tmp_path, "3.17.0")
    state = tmp_path / "state"
    _write_cache(state, "GARBAGE")
    r = run_checker(
        plugin_root=root,
        remote_url=make_remote(tmp_path, "3.18.0"),
        state_dir=state,
    )
    assert r.stdout.strip() == "UPDATE_AVAILABLE 3.17.0 3.18.0"
    assert (
        state / "update-check"
    ).read_text().strip() == "UPDATE_AVAILABLE 3.17.0 3.18.0"


def test_local_version_changed_invalidates_fresh_cache(tmp_path):
    # The user updated: current local equals the cached <latest>. The fresh
    # cache must NOT render a reminder; the checker refetches and goes quiet.
    root = make_plugin_root(tmp_path, "3.18.0")
    state = tmp_path / "state"
    _write_cache(state, "UPDATE_AVAILABLE 3.17.0 3.18.0")
    r = run_checker(
        plugin_root=root,
        remote_url=make_remote(tmp_path, "3.18.0"),
        state_dir=state,
    )
    assert r.stdout == ""
    assert (state / "update-check").read_text().strip() == "UP_TO_DATE 3.18.0 3.18.0"


# -------------------------------------------------------- announce integration


def run_announce(source_json, env_overrides):
    env = base_env()
    env.update(env_overrides)
    return subprocess.run(
        ["bash", str(ANNOUNCE)],
        input=source_json,
        capture_output=True,
        text=True,
        env=env,
        timeout=30,
    )


def _additional_context(stdout):
    return json.loads(stdout)["hookSpecificOutput"]["additionalContext"]


def test_announce_prepends_reminder_when_behind(tmp_path):
    root = make_plugin_root(tmp_path, "3.17.0")
    state = tmp_path / "state"
    env = {
        "CLAUDE_PLUGIN_ROOT": str(root),
        "ARS_UPDATE_CHECK_STATE_DIR": str(state),
        "ARS_UPDATE_CHECK_REMOTE_URL": make_remote(tmp_path, "3.18.0"),
    }
    r = run_announce('{"source":"startup"}', env)
    ctx = _additional_context(r.stdout)
    assert ctx.startswith(
        "ARS update available: v3.18.0 (installed: v3.17.0). "
        "Run /plugin update academic-research-skills, "
        "or enable auto-update in /plugin -> Marketplaces."
    )
    assert "ARS (academic-research-skills) plugin loaded." in ctx


def test_announce_unchanged_when_current(tmp_path):
    root = make_plugin_root(tmp_path, "3.17.0")
    state = tmp_path / "state"
    # Baseline: no CLAUDE_PLUGIN_ROOT at all == pre-#544 output.
    baseline = run_announce('{"source":"startup"}', {})
    env = {
        "CLAUDE_PLUGIN_ROOT": str(root),
        "ARS_UPDATE_CHECK_STATE_DIR": str(state),
        "ARS_UPDATE_CHECK_REMOTE_URL": make_remote(tmp_path, "3.17.0"),
    }
    r = run_announce('{"source":"startup"}', env)
    assert r.stdout == baseline.stdout


def test_announce_unchanged_when_checker_missing(tmp_path):
    root = make_plugin_root(tmp_path, "3.17.0", with_checker=False)
    baseline = run_announce('{"source":"startup"}', {})
    r = run_announce('{"source":"startup"}', {"CLAUDE_PLUGIN_ROOT": str(root)})
    assert r.stdout == baseline.stdout


def test_announce_resume_never_runs_checker(tmp_path):
    # Structural pin for "checker lives inside the startup|clear arm": on
    # resume the checker must not run at all, so no cache file may appear.
    root = make_plugin_root(tmp_path, "3.17.0")
    state = tmp_path / "state"
    env = {
        "CLAUDE_PLUGIN_ROOT": str(root),
        "ARS_UPDATE_CHECK_STATE_DIR": str(state),
        "ARS_UPDATE_CHECK_REMOTE_URL": make_remote(tmp_path, "3.18.0"),
    }
    r = run_announce('{"source":"resume"}', env)
    assert "update available" not in r.stdout
    assert not (state / "update-check").exists()
