#!/usr/bin/env python3
"""Focused mutation tests for the #789 sealed bakeoff lifecycle."""

from __future__ import annotations

import copy
import json
import subprocess
from pathlib import Path

import pytest
from jsonschema import Draft202012Validator

from scripts import check_promotion_bakeoff_preregistration as sealed


REPO = Path(__file__).resolve().parent.parent
COMMITMENT_SCHEMA = (
    REPO
    / "shared/contracts/cross_model/promotion_bakeoff_sealed_commitment.schema.json"
)
REVEAL_SCHEMA = (
    REPO / "shared/contracts/cross_model/promotion_bakeoff_sealed_reveal.schema.json"
)


def _run(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        capture_output=True,
        text=True,
    )


def _git(repo: Path, *args: str) -> None:
    result = _run(repo, *args)
    assert result.returncode == 0, result.stderr


def _init_repo(tmp_path: Path) -> Path:
    repo = tmp_path / "repo"
    repo.mkdir(parents=True)
    _git(repo, "init", "-q")
    _git(repo, "config", "user.name", "Sealed Test")
    _git(repo, "config", "user.email", "sealed@example.invalid")
    return repo


def _commit(repo: Path, message: str, *paths: str) -> None:
    _git(repo, "add", "--", *paths)
    _git(repo, "commit", "-q", "-m", message)


def _probe(seed: str = "fresh") -> dict:
    references = []
    for index in range(10):
        references.append(
            {
                "id": f"real-easy-{index:02d}",
                "label": "real",
                "difficulty": "easy",
                "reference_text": f"{seed} Easy Author {index}. Verified DOI article {index}.",
                "citation_context": f"Easy context {index}",
                "ground_truth": {
                    "doi": f"10.1234/{seed}.easy.{index}",
                    "verified_via": "resolver-test",
                },
            }
        )
    for index in range(10):
        references.append(
            {
                "id": f"real-hard-{index:02d}",
                "label": "real",
                "difficulty": "hard",
                "reference_text": f"{seed} Hard Author {index}. Verified preprint {index}.",
                "citation_context": f"Hard context {index}",
                "ground_truth": {
                    "arxiv": f"2608.{index:05d}",
                    "verified_via": "resolver-test",
                },
            }
        )
    for index in range(10):
        references.append(
            {
                "id": f"fab-{index:02d}",
                "label": "fabricated",
                "difficulty": "n/a",
                "reference_text": f"{seed} Synthetic Author {index}. Invented study {index}.",
                "citation_context": f"Fabricated context {index}",
                "ground_truth": {"negative_checked_via": "resolver-test"},
            }
        )
    return {
        "schema_version": sealed.PROBE_VERSION,
        "created": "2026-08-24",
        "references": references,
    }


def _bytes(value: dict) -> bytes:
    return sealed.render_json(value)


def _write(repo: Path, relpath: str, raw: bytes) -> Path:
    path = repo / relpath
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(raw)
    return path


def _campaign_rel(campaign: str, name: str) -> str:
    return f"evals/bakeoff/{campaign}/{name}"


def _commit_seal(repo: Path, campaign: str, probe_raw: bytes) -> tuple[str, bytes]:
    commitment = sealed.make_commitment(campaign, probe_raw)
    commitment_raw = _bytes(commitment)
    relpath = _campaign_rel(campaign, sealed.COMMITMENT_NAME)
    _write(repo, relpath, commitment_raw)
    _commit(repo, "sealed commitment", relpath)
    return relpath, commitment_raw


def _commit_reveal(
    repo: Path,
    campaign: str,
    probe_raw: bytes,
    commitment_rel: str,
    commitment_raw: bytes,
) -> str:
    probe_rel = _campaign_rel(campaign, sealed.PROBE_NAME)
    reveal_rel = _campaign_rel(campaign, sealed.REVEAL_NAME)
    _write(repo, probe_rel, probe_raw)
    reveal = sealed.make_reveal(
        campaign,
        commitment_rel,
        commitment_raw,
        probe_rel,
        probe_raw,
    )
    _write(repo, reveal_rel, _bytes(reveal))
    _commit(repo, "reveal after fleet", probe_rel, reveal_rel)
    return reveal_rel


def _valid_lifecycle(
    tmp_path: Path, *, campaign: str = "2026-08-24-candidate-api", seed: str = "fresh"
) -> tuple[Path, str, bytes]:
    repo = _init_repo(tmp_path)
    probe_raw = _bytes(_probe(seed))
    commitment_rel, commitment_raw = _commit_seal(repo, campaign, probe_raw)
    reveal_rel = _commit_reveal(
        repo, campaign, probe_raw, commitment_rel, commitment_raw
    )
    return repo, reveal_rel, probe_raw


def test_generated_contracts_match_the_closed_json_schemas() -> None:
    probe_raw = _bytes(_probe())
    commitment = sealed.make_commitment("2026-08-24-candidate-api", probe_raw)
    reveal = sealed.make_reveal(
        commitment["campaign_id"],
        _campaign_rel(commitment["campaign_id"], sealed.COMMITMENT_NAME),
        _bytes(commitment),
        _campaign_rel(commitment["campaign_id"], sealed.PROBE_NAME),
        probe_raw,
    )
    for path, instance in (
        (COMMITMENT_SCHEMA, commitment),
        (REVEAL_SCHEMA, reveal),
    ):
        schema = json.loads(path.read_text(encoding="utf-8"))
        Draft202012Validator.check_schema(schema)
        Draft202012Validator(schema).validate(instance)


def test_commitment_contains_no_probe_row_or_free_text_surface() -> None:
    probe = _probe()
    commitment = sealed.make_commitment("2026-08-24-candidate-api", _bytes(probe))
    assert set(commitment) == sealed._COMMITMENT_KEYS
    rendered = _bytes(commitment).decode("utf-8")
    assert probe["references"][0]["reference_text"] not in rendered
    assert "ground_truth" not in rendered
    assert "probe_set.json" not in rendered


def test_valid_pending_commitment_preflight_and_tree_pass(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    campaign = "2026-08-24-candidate-api"
    probe_raw = _bytes(_probe())
    commitment_rel, _commitment_raw = _commit_seal(repo, campaign, probe_raw)
    private_probe = tmp_path / "private-probe.json"
    private_probe.write_bytes(probe_raw)
    summary = sealed.preflight(repo, commitment_rel, private_probe)
    assert summary.row_count == 30
    assert sealed.verify_tree(repo) == []


def test_valid_reveal_verifies_git_order_hash_and_freshness(tmp_path: Path) -> None:
    repo, reveal_rel, probe_raw = _valid_lifecycle(tmp_path)
    receipt = sealed.verify_reveal(repo, reveal_rel)
    assert receipt.probe_set_sha256 == sealed.sha256_bytes(probe_raw)
    assert receipt.commitment_git_commit != receipt.reveal_git_commit
    assert receipt.reveal_copy_git_commits == (receipt.reveal_git_commit,)
    assert receipt.published_probe_versions_checked == 0
    assert [item.campaign_id for item in sealed.verify_tree(repo)] == [
        "2026-08-24-candidate-api"
    ]


def test_crlf_worktree_checkout_does_not_look_like_history_mutation(
    tmp_path: Path,
) -> None:
    repo, reveal_rel, _probe_raw = _valid_lifecycle(tmp_path)
    campaign = "2026-08-24-candidate-api"
    for name in (
        sealed.COMMITMENT_NAME,
        sealed.PROBE_NAME,
        sealed.REVEAL_NAME,
    ):
        path = repo / _campaign_rel(campaign, name)
        path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
    assert sealed.verify_reveal(repo, reveal_rel).campaign_id == campaign


def test_crlf_checkout_has_the_same_sealed_digest() -> None:
    lf = _bytes(_probe())
    crlf = lf.replace(b"\n", b"\r\n")
    assert sealed.sha256_bytes(lf) == sealed.sha256_bytes(crlf)
    commitment = sealed.make_commitment("2026-08-24-candidate-api", lf)
    sealed.verify_probe_against_commitment(commitment, crlf)


def test_duplicate_json_key_is_rejected() -> None:
    with pytest.raises(sealed.PreregistrationError) as failure:
        sealed.load_json_bytes(b'{"schema_version":"x","schema_version":"y"}', where="mutation")
    assert failure.value.code == "JSON_DUPLICATE_KEY"


def test_commitment_extra_field_cannot_smuggle_labels() -> None:
    commitment = sealed.make_commitment("2026-08-24-candidate-api", _bytes(_probe()))
    commitment["notes"] = "fab-01 is fabricated"
    with pytest.raises(sealed.PreregistrationError) as failure:
        sealed.validate_commitment(commitment)
    assert failure.value.code == "SCHEMA_INVALID"


@pytest.mark.parametrize(
    "mutation",
    [
        lambda probe: probe.update({"notes": "hidden free-text surface"}),
        lambda probe: probe["references"][0].pop("citation_context"),
        lambda probe: probe["references"][0]["ground_truth"].update(
            {"notes": "undeclared witness"}
        ),
    ],
)
def test_probe_contract_is_closed(mutation) -> None:
    probe = _probe()
    mutation(probe)
    with pytest.raises(sealed.PreregistrationError) as failure:
        sealed.make_commitment("2026-08-24-candidate-api", _bytes(probe))
    assert failure.value.code == "PROBE_INVALID"


def test_changed_probe_fails_the_sealed_hash() -> None:
    probe = _probe()
    commitment = sealed.make_commitment("2026-08-24-candidate-api", _bytes(probe))
    probe["references"][0]["citation_context"] = "observed-output edit"
    with pytest.raises(sealed.PreregistrationError) as failure:
        sealed.verify_probe_against_commitment(commitment, _bytes(probe))
    assert failure.value.code == "HASH_MISMATCH"


def test_rehashed_probe_with_wrong_composition_still_fails() -> None:
    probe = _probe()
    probe["references"][0]["difficulty"] = "hard"
    with pytest.raises(sealed.PreregistrationError) as failure:
        sealed.make_commitment("2026-08-24-candidate-api", _bytes(probe))
    assert failure.value.code == "COMPOSITION_MISMATCH"


def test_commitment_and_probe_in_same_commit_are_not_a_seal(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    campaign = "2026-08-24-candidate-api"
    probe_raw = _bytes(_probe())
    commitment_rel = _campaign_rel(campaign, sealed.COMMITMENT_NAME)
    probe_rel = _campaign_rel(campaign, sealed.PROBE_NAME)
    reveal_rel = _campaign_rel(campaign, sealed.REVEAL_NAME)
    commitment_raw = _bytes(sealed.make_commitment(campaign, probe_raw))
    reveal_raw = _bytes(
        sealed.make_reveal(
            campaign, commitment_rel, commitment_raw, probe_rel, probe_raw
        )
    )
    _write(repo, commitment_rel, commitment_raw)
    _write(repo, probe_rel, probe_raw)
    _write(repo, reveal_rel, reveal_raw)
    _commit(repo, "not actually sealed", commitment_rel, probe_rel, reveal_rel)
    with pytest.raises(sealed.PreregistrationError) as failure:
        sealed.verify_reveal(repo, reveal_rel)
    assert failure.value.code in {"LABEL_EXPOSURE", "ORDER_VIOLATION"}


def test_probe_and_reveal_must_be_introduced_together(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    campaign = "2026-08-24-candidate-api"
    probe_raw = _bytes(_probe())
    commitment_rel, commitment_raw = _commit_seal(repo, campaign, probe_raw)
    probe_rel = _campaign_rel(campaign, sealed.PROBE_NAME)
    reveal_rel = _campaign_rel(campaign, sealed.REVEAL_NAME)
    _write(repo, probe_rel, probe_raw)
    _commit(repo, "premature fixture-only reveal", probe_rel)
    reveal = sealed.make_reveal(
        campaign, commitment_rel, commitment_raw, probe_rel, probe_raw
    )
    _write(repo, reveal_rel, _bytes(reveal))
    _commit(repo, "late reveal carrier", reveal_rel)
    with pytest.raises(sealed.PreregistrationError) as failure:
        sealed.verify_reveal(repo, reveal_rel)
    assert failure.value.code == "ORDER_VIOLATION"


def test_commitment_cannot_be_rewritten_at_reveal(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    campaign = "2026-08-24-candidate-api"
    probe_raw = _bytes(_probe())
    commitment_rel, commitment_raw = _commit_seal(repo, campaign, probe_raw)
    mutated = commitment_raw.replace(b'  "campaign_id"', b'    "campaign_id"')
    assert mutated != commitment_raw
    _write(repo, commitment_rel, mutated)
    probe_rel = _campaign_rel(campaign, sealed.PROBE_NAME)
    reveal_rel = _campaign_rel(campaign, sealed.REVEAL_NAME)
    _write(repo, probe_rel, probe_raw)
    reveal = sealed.make_reveal(
        campaign, commitment_rel, mutated, probe_rel, probe_raw
    )
    _write(repo, reveal_rel, _bytes(reveal))
    _commit(repo, "rewrite seal while revealing", commitment_rel, probe_rel, reveal_rel)
    with pytest.raises(sealed.PreregistrationError) as failure:
        sealed.verify_reveal(repo, reveal_rel)
    assert failure.value.code == "ARTIFACT_MUTATED"


def test_revealed_probe_changed_then_reverted_is_still_invalid(tmp_path: Path) -> None:
    repo, reveal_rel, probe_raw = _valid_lifecycle(tmp_path)
    probe_rel = _campaign_rel("2026-08-24-candidate-api", sealed.PROBE_NAME)
    mutated = json.loads(probe_raw)
    mutated["references"][0]["citation_context"] = "temporary observed-output edit"
    _write(repo, probe_rel, _bytes(mutated))
    _commit(repo, "mutate revealed answer key", probe_rel)
    _write(repo, probe_rel, probe_raw)
    _commit(repo, "revert answer key", probe_rel)
    with pytest.raises(sealed.PreregistrationError) as failure:
        sealed.verify_reveal(repo, reveal_rel)
    assert failure.value.code == "ARTIFACT_MUTATED"


def test_merge_side_probe_mutation_cannot_be_hidden_by_ours_resolution(
    tmp_path: Path,
) -> None:
    repo, reveal_rel, probe_raw = _valid_lifecycle(tmp_path)
    main_branch = _run(repo, "branch", "--show-current").stdout.strip()
    _git(repo, "checkout", "-q", "-b", "mutation-side")
    probe_rel = _campaign_rel("2026-08-24-candidate-api", sealed.PROBE_NAME)
    mutated = json.loads(probe_raw)
    mutated["references"][0]["citation_context"] = "side-history mutation"
    _write(repo, probe_rel, _bytes(mutated))
    _commit(repo, "side mutation", probe_rel)
    _git(repo, "checkout", "-q", main_branch)
    _git(repo, "merge", "-q", "--no-ff", "-s", "ours", "mutation-side", "-m", "ours merge")

    with pytest.raises(sealed.PreregistrationError) as failure:
        sealed.verify_reveal(repo, reveal_rel)
    assert failure.value.code == "ARTIFACT_MUTATED"


def test_merge_side_mode_mutation_with_same_blob_is_rejected(tmp_path: Path) -> None:
    repo, reveal_rel, _probe_raw = _valid_lifecycle(tmp_path)
    main_branch = _run(repo, "branch", "--show-current").stdout.strip()
    commitment_rel = _campaign_rel(
        "2026-08-24-candidate-api", sealed.COMMITMENT_NAME
    )
    commitment_path = repo / commitment_rel
    target = commitment_path.read_text(encoding="utf-8")
    _git(repo, "checkout", "-q", "-b", "mode-side")
    commitment_path.unlink()
    commitment_path.symlink_to(target)
    _commit(repo, "side mode mutation with identical blob", commitment_rel)
    _git(repo, "checkout", "-q", main_branch)
    _git(repo, "merge", "-q", "--no-ff", "-s", "ours", "mode-side", "-m", "ours merge")
    _git(repo, "branch", "-D", "mode-side")

    with pytest.raises(sealed.PreregistrationError) as failure:
        sealed.verify_reveal(repo, reveal_rel)
    assert failure.value.code == "PATH_UNSAFE"


def test_symlink_substitution_fails_even_when_target_bytes_match(tmp_path: Path) -> None:
    repo, reveal_rel, _probe_raw = _valid_lifecycle(tmp_path)
    reveal_path = repo / reveal_rel
    copy_path = reveal_path.with_name("reveal-copy.json")
    copy_path.write_bytes(reveal_path.read_bytes())
    reveal_path.unlink()
    reveal_path.symlink_to(copy_path.name)
    with pytest.raises(sealed.PreregistrationError) as failure:
        sealed.verify_reveal(repo, reveal_rel)
    assert failure.value.code == "PATH_UNSAFE"


def _add_published_probe(repo: Path, probe_raw: bytes) -> str:
    relpath = "evals/bakeoff/2026-08-01-old/probe_set.json"
    _write(repo, relpath, probe_raw)
    _commit(repo, "publish old labels", relpath)
    return relpath


def test_reformatted_fabrication_reuse_is_rejected(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    old_probe = _probe("old")
    _add_published_probe(repo, _bytes(old_probe))
    candidate = _probe("new")
    reused = old_probe["references"][20]["reference_text"]
    candidate["references"][20]["reference_text"] = (
        "  " + reused.upper().replace(".", " . ") + "  "
    )
    probe_raw = _bytes(candidate)
    campaign = "2026-08-24-candidate-api"
    commitment_rel, commitment_raw = _commit_seal(repo, campaign, probe_raw)
    reveal_rel = _commit_reveal(
        repo, campaign, probe_raw, commitment_rel, commitment_raw
    )
    with pytest.raises(sealed.PreregistrationError) as failure:
        sealed.verify_reveal(repo, reveal_rel)
    assert failure.value.code == "PUBLISHED_FABRICATION_REUSE"


def test_published_probe_bytes_cannot_be_reused_under_a_new_campaign(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    probe_raw = _bytes(_probe("old"))
    _add_published_probe(repo, probe_raw)
    campaign = "2026-08-24-candidate-api"
    commitment_rel, commitment_raw = _commit_seal(repo, campaign, probe_raw)
    reveal_rel = _commit_reveal(
        repo, campaign, probe_raw, commitment_rel, commitment_raw
    )
    with pytest.raises(sealed.PreregistrationError) as failure:
        sealed.verify_reveal(repo, reveal_rel)
    assert failure.value.code == "PUBLISHED_SET_REUSE"


def test_real_rows_may_remain_while_fabrication_pool_is_fresh(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    old_probe = _probe("old")
    _add_published_probe(repo, _bytes(old_probe))
    candidate = _probe("new")
    candidate["references"][:20] = copy.deepcopy(old_probe["references"][:20])
    probe_raw = _bytes(candidate)
    campaign = "2026-08-24-candidate-api"
    commitment_rel, commitment_raw = _commit_seal(repo, campaign, probe_raw)
    reveal_rel = _commit_reveal(
        repo, campaign, probe_raw, commitment_rel, commitment_raw
    )
    receipt = sealed.verify_reveal(repo, reveal_rel)
    assert receipt.published_probe_versions_checked == 1


@pytest.mark.parametrize("merge_side", [False, True])
def test_freshness_scans_non_head_and_ours_merged_public_refs(
    tmp_path: Path, merge_side: bool
) -> None:
    repo = _init_repo(tmp_path)
    _write(repo, "README.md", b"base\n")
    _commit(repo, "base", "README.md")
    main_branch = _run(repo, "branch", "--show-current").stdout.strip()
    _git(repo, "checkout", "-q", "-b", "published-labels")
    old_probe = _probe("published")
    _add_published_probe(repo, _bytes(old_probe))
    leaked_commit = _run(repo, "rev-parse", "HEAD").stdout.strip()
    _git(repo, "checkout", "-q", main_branch)
    if merge_side:
        _git(
            repo,
            "merge",
            "-q",
            "--no-ff",
            "-s",
            "ours",
            "published-labels",
            "-m",
            "ours merge",
        )
        assert _run(repo, "merge-base", "--is-ancestor", leaked_commit, "HEAD").returncode == 0

    candidate = _probe("fresh")
    candidate["references"][20]["reference_text"] = old_probe["references"][20][
        "reference_text"
    ]
    summary = sealed.validate_probe_set(_bytes(candidate))
    with pytest.raises(sealed.PreregistrationError) as failure:
        sealed.verify_freshness(repo, summary)
    assert failure.value.code == "PUBLISHED_FABRICATION_REUSE"


def test_freshness_scans_unicode_and_merge_only_probe_paths(tmp_path: Path) -> None:
    unicode_repo = _init_repo(tmp_path / "unicode")
    unicode_probe = _probe("unicode-published")
    unicode_rel = "evals/bakeoff/2026-08-01-測試/probe_set.json"
    _write(unicode_repo, unicode_rel, _bytes(unicode_probe))
    _commit(unicode_repo, "publish labels under unicode path", unicode_rel)
    unicode_candidate = _probe("unicode-fresh")
    unicode_candidate["references"][20]["reference_text"] = unicode_probe[
        "references"
    ][20]["reference_text"]
    with pytest.raises(sealed.PreregistrationError) as unicode_failure:
        sealed.verify_freshness(
            unicode_repo, sealed.validate_probe_set(_bytes(unicode_candidate))
        )
    assert unicode_failure.value.code == "PUBLISHED_FABRICATION_REUSE"

    merge_repo = _init_repo(tmp_path / "merge-only")
    _write(merge_repo, "base.txt", b"base\n")
    _commit(merge_repo, "base", "base.txt")
    main_branch = _run(merge_repo, "branch", "--show-current").stdout.strip()
    _git(merge_repo, "checkout", "-q", "-b", "merge-parent")
    _write(merge_repo, "side.txt", b"side\n")
    _commit(merge_repo, "side parent", "side.txt")
    _git(merge_repo, "checkout", "-q", main_branch)
    _write(merge_repo, "main.txt", b"main\n")
    _commit(merge_repo, "main parent", "main.txt")
    _git(merge_repo, "merge", "-q", "--no-ff", "--no-commit", "merge-parent")
    merge_probe = _probe("merge-published")
    merge_rel = "evals/bakeoff/2026-08-02-merge-only/probe_set.json"
    _write(merge_repo, merge_rel, _bytes(merge_probe))
    _commit(merge_repo, "merge commit publishes labels", merge_rel)
    merge_candidate = _probe("merge-fresh")
    merge_candidate["references"][20]["reference_text"] = merge_probe[
        "references"
    ][20]["reference_text"]
    with pytest.raises(sealed.PreregistrationError) as merge_failure:
        sealed.verify_freshness(
            merge_repo, sealed.validate_probe_set(_bytes(merge_candidate))
        )
    assert merge_failure.value.code == "PUBLISHED_FABRICATION_REUSE"


def test_same_campaign_path_on_other_ref_is_not_excluded(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    _write(repo, "README.md", b"base\n")
    _commit(repo, "base", "README.md")
    main_branch = _run(repo, "branch", "--show-current").stdout.strip()
    campaign = "2026-08-24-candidate-api"
    probe_raw = _bytes(_probe("same-path"))
    probe_rel = _campaign_rel(campaign, sealed.PROBE_NAME)
    _git(repo, "checkout", "-q", "-b", "leaked-same-path")
    _write(repo, probe_rel, probe_raw)
    _commit(repo, "publish same campaign path", probe_rel)
    _git(repo, "checkout", "-q", main_branch)

    commitment_rel, commitment_raw = _commit_seal(repo, campaign, probe_raw)
    private_probe = tmp_path / "private-same-path.json"
    private_probe.write_bytes(probe_raw)
    with pytest.raises(sealed.PreregistrationError) as preflight_failure:
        sealed.preflight(repo, commitment_rel, private_probe)
    assert preflight_failure.value.code == "PUBLISHED_SET_REUSE"

    reveal_rel = _commit_reveal(
        repo, campaign, probe_raw, commitment_rel, commitment_raw
    )
    with pytest.raises(sealed.PreregistrationError) as reveal_failure:
        sealed.verify_reveal(repo, reveal_rel)
    assert reveal_failure.value.code == "PUBLISHED_SET_REUSE"


def test_squash_copied_reveal_with_source_ref_retained_is_one_lifecycle(
    tmp_path: Path,
) -> None:
    repo = _init_repo(tmp_path)
    _write(repo, "README.md", b"base\n")
    _commit(repo, "base", "README.md")
    campaign = "2026-08-24-candidate-api"
    probe_raw = _bytes(_probe("squash-copy"))
    commitment_rel, commitment_raw = _commit_seal(repo, campaign, probe_raw)
    main_branch = _run(repo, "branch", "--show-current").stdout.strip()
    _git(repo, "checkout", "-q", "-b", "reveal-feature")
    _commit_reveal(repo, campaign, probe_raw, commitment_rel, commitment_raw)
    feature_reveal_commit = _run(repo, "rev-parse", "HEAD").stdout.strip()
    _git(repo, "checkout", "-q", main_branch)
    _write(repo, "main.txt", b"main advanced\n")
    _commit(repo, "advance main before squash", "main.txt")
    _git(repo, "merge", "-q", "--squash", "reveal-feature")
    _git(repo, "commit", "-q", "-m", "squash reveal feature")

    reveal_rel = _campaign_rel(campaign, sealed.REVEAL_NAME)
    receipt = sealed.verify_reveal(repo, reveal_rel)
    assert receipt.published_probe_versions_checked == 0
    assert receipt.reveal_copy_git_commits == tuple(
        sorted((feature_reveal_commit, receipt.reveal_git_commit))
    )
    assert [item.campaign_id for item in sealed.verify_tree(repo)] == [campaign]


def test_post_seal_probe_only_ref_is_not_a_lifecycle_copy(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    campaign = "2026-08-24-candidate-api"
    probe_raw = _bytes(_probe("post-seal-leak"))
    commitment_rel, commitment_raw = _commit_seal(repo, campaign, probe_raw)
    main_branch = _run(repo, "branch", "--show-current").stdout.strip()
    probe_rel = _campaign_rel(campaign, sealed.PROBE_NAME)
    _git(repo, "checkout", "-q", "-b", "probe-only-leak")
    _write(repo, probe_rel, probe_raw)
    _commit(repo, "publish probe without bound reveal", probe_rel)
    _git(repo, "checkout", "-q", main_branch)
    reveal_rel = _commit_reveal(
        repo, campaign, probe_raw, commitment_rel, commitment_raw
    )

    with pytest.raises(sealed.PreregistrationError) as failure:
        sealed.verify_reveal(repo, reveal_rel)
    assert failure.value.code == "PUBLISHED_SET_REUSE"


def test_shallow_history_and_missing_historical_blob_fail_closed(tmp_path: Path) -> None:
    origin = _init_repo(tmp_path / "origin")
    probe_raw = _bytes(_probe("hidden-history"))
    old_rel = _add_published_probe(origin, probe_raw)
    (origin / old_rel).unlink()
    _commit(origin, "retire old fixture", old_rel)
    campaign = "2026-08-24-candidate-api"
    commitment_rel, _commitment_raw = _commit_seal(origin, campaign, probe_raw)
    shallow = tmp_path / "shallow"
    clone = subprocess.run(
        ["git", "clone", "-q", "--depth", "1", origin.as_uri(), str(shallow)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert clone.returncode == 0, clone.stderr
    private_probe = tmp_path / "private-shallow.json"
    private_probe.write_bytes(probe_raw)
    with pytest.raises(sealed.PreregistrationError) as shallow_failure:
        sealed.preflight(shallow, commitment_rel, private_probe)
    assert shallow_failure.value.code == "HISTORY_INCOMPLETE"

    missing_blob_repo = _init_repo(tmp_path / "missing-blob")
    missing_raw = _bytes(_probe("missing-blob"))
    missing_rel = _add_published_probe(missing_blob_repo, missing_raw)
    blob_oid = _run(
        missing_blob_repo, "rev-parse", f"HEAD:{missing_rel}"
    ).stdout.strip()
    object_path = missing_blob_repo / ".git/objects" / blob_oid[:2] / blob_oid[2:]
    assert object_path.is_file()
    object_path.unlink()
    candidate = sealed.validate_probe_set(_bytes(_probe("candidate")))
    with pytest.raises(sealed.PreregistrationError) as blob_failure:
        sealed.verify_freshness(missing_blob_repo, candidate)
    assert blob_failure.value.code == "GIT_ERROR"


@pytest.mark.parametrize(
    "relpath",
    [
        "evals/bakeoff/probe_set.json",
        "evals/bakeoff/noncanonical/nested/probe_set.json",
    ],
)
def test_tree_rejects_recursive_noncanonical_probe_paths(
    tmp_path: Path, relpath: str
) -> None:
    repo = _init_repo(tmp_path)
    _write(repo, relpath, _bytes(_probe()))
    _commit(repo, "noncanonical probe", relpath)
    with pytest.raises(sealed.PreregistrationError) as failure:
        sealed.verify_tree(repo)
    assert failure.value.code == "PATH_INVALID"


def test_tree_reconciles_missing_tracked_campaign_and_root_symlink(
    tmp_path: Path,
) -> None:
    repo, _reveal_rel, _probe_raw = _valid_lifecycle(tmp_path)
    campaign_dir = repo / "evals/bakeoff/2026-08-24-candidate-api"
    hidden = repo / "hidden-campaign"
    campaign_dir.rename(hidden)
    with pytest.raises(sealed.PreregistrationError) as missing:
        sealed.verify_tree(repo)
    assert missing.value.code == "WORKTREE_DRIFT"

    campaign_dir.parent.rename(repo / "bakeoff-real")
    empty = repo / "empty-bakeoff"
    empty.mkdir()
    (repo / "evals/bakeoff").symlink_to(empty, target_is_directory=True)
    with pytest.raises(sealed.PreregistrationError) as symlinked:
        sealed.verify_tree(repo)
    assert symlinked.value.code == "PATH_UNSAFE"


@pytest.mark.parametrize("staged_name", [sealed.PROBE_NAME, sealed.REVEAL_NAME])
def test_preflight_rejects_staged_probe_or_reveal(
    tmp_path: Path, staged_name: str
) -> None:
    repo = _init_repo(tmp_path)
    campaign = "2026-08-24-candidate-api"
    probe_raw = _bytes(_probe())
    commitment_rel, _commitment_raw = _commit_seal(repo, campaign, probe_raw)
    private_probe = tmp_path / "private-probe.json"
    private_probe.write_bytes(probe_raw)
    staged_rel = _campaign_rel(campaign, staged_name)
    _write(repo, staged_rel, probe_raw if staged_name == sealed.PROBE_NAME else b"{}\n")
    _git(repo, "add", "--", staged_rel)

    with pytest.raises(sealed.PreregistrationError) as failure:
        sealed.preflight(repo, commitment_rel, private_probe)
    assert failure.value.code == "LABEL_EXPOSURE"


def test_tree_rejects_new_unsealed_fixture_but_grandfathers_recorded_run(
    tmp_path: Path,
) -> None:
    repo = _init_repo(tmp_path)
    new_rel = "evals/bakeoff/2026-08-24-unsealed/probe_set.json"
    _write(repo, new_rel, _bytes(_probe()))
    _commit(repo, "unsealed future labels", new_rel)
    with pytest.raises(sealed.PreregistrationError) as failure:
        sealed.verify_tree(repo)
    assert failure.value.code == "UNSEALED_PROBE"

    # The sole pre-#789 run is an explicit path allowlist, not a broad date
    # exemption that a future campaign could imitate.
    repo2 = _init_repo(tmp_path / "legacy")
    legacy_rel = next(iter(sealed.LEGACY_PUBLIC_PROBE_PATHS))
    legacy_raw = (REPO / legacy_rel).read_bytes()
    assert sealed.sha256_bytes(legacy_raw) == sealed.LEGACY_PUBLIC_PROBE_SHA256[
        legacy_rel
    ]
    _write(repo2, legacy_rel, legacy_raw)
    _commit(repo2, "recorded pre-seal run", legacy_rel)
    assert sealed.verify_tree(repo2) == []

    mutated = json.loads(legacy_raw)
    mutated["references"][0]["citation_context"] = "post-run mutation"
    _write(repo2, legacy_rel, _bytes(mutated))
    _commit(repo2, "mutate grandfathered labels", legacy_rel)
    with pytest.raises(sealed.PreregistrationError) as legacy_failure:
        sealed.verify_tree(repo2)
    assert legacy_failure.value.code == "ARTIFACT_MUTATED"


def test_grandfather_path_rejects_unpinned_initial_bytes(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    legacy_rel = next(iter(sealed.LEGACY_PUBLIC_PROBE_PATHS))
    _write(repo, legacy_rel, _bytes(_probe("not-the-recorded-run")))
    _commit(repo, "wrong bytes at grandfather path", legacy_rel)
    with pytest.raises(sealed.PreregistrationError) as failure:
        sealed.verify_tree(repo)
    assert failure.value.code == "LEGACY_PROBE_MISMATCH"


def test_grandfather_path_cannot_disappear_after_publication(tmp_path: Path) -> None:
    repo = _init_repo(tmp_path)
    legacy_rel = next(iter(sealed.LEGACY_PUBLIC_PROBE_PATHS))
    _write(repo, legacy_rel, (REPO / legacy_rel).read_bytes())
    _commit(repo, "recorded pre-seal run", legacy_rel)
    assert sealed.verify_tree(repo) == []
    (repo / legacy_rel).unlink()
    _commit(repo, "delete grandfathered fixture", legacy_rel)
    with pytest.raises(sealed.PreregistrationError) as failure:
        sealed.verify_tree(repo)
    assert failure.value.code == "PATH_MISSING"


def test_cli_returns_closed_nonzero_failure(tmp_path: Path, capsys) -> None:
    repo = _init_repo(tmp_path)
    bad_rel = "evals/bakeoff/2026-08-24-unsealed/probe_set.json"
    _write(repo, bad_rel, _bytes(_probe()))
    _commit(repo, "unsealed", bad_rel)
    result = sealed.main(["verify-tree", "--repo-root", str(repo)])
    captured = capsys.readouterr()
    assert result == 1
    assert "FAIL [UNSEALED_PROBE]" in captured.err


def test_verification_receipt_discloses_local_evidence_limit(tmp_path: Path) -> None:
    repo, reveal_rel, _probe_raw = _valid_lifecycle(tmp_path)
    receipt = sealed.verify_reveal(repo, reveal_rel).as_dict()
    assert receipt["remote_publication_timing"] == "not_verifiable_locally"
    assert receipt["gate_eligibility"] == "requires_run_report_witness"
    assert receipt["reveal_copy_git_commits"] == [receipt["reveal_git_commit"]]


def test_protocol_requires_timing_witness_for_every_reveal_copy() -> None:
    protocol = (REPO / "shared/cross_model_verification.md").read_text(
        encoding="utf-8"
    )
    assert "`reveal_copy_git_commits`" in protocol
    assert "every listed reveal-copy commit" in protocol
