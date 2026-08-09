"""Hermetic mutation tests for the bounded #680 reference migration."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest

from scripts import check_human_subjects_reference_migration as migration


REPO_ROOT = Path(__file__).resolve().parents[1]


def mirror(tmp_path: Path) -> Path:
    for rel in (*migration.TEXT_FILES, migration.REGISTRY):
        target = tmp_path / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO_ROOT / rel, target)
    return tmp_path


def append(root: Path, rel: Path, text: str) -> None:
    path = root / rel
    path.write_text(path.read_text(encoding="utf-8") + text, encoding="utf-8")


def replace_once(root: Path, rel: Path, old: str, new: str) -> None:
    path = root / rel
    text = path.read_text(encoding="utf-8")
    assert old in text, f"mutation target missing: {old!r}"
    path.write_text(text.replace(old, new, 1), encoding="utf-8")


def remove_all(root: Path, rel: Path, value: str) -> None:
    path = root / rel
    text = path.read_text(encoding="utf-8")
    assert value in text, f"removal target missing: {value!r}"
    path.write_text(text.replace(value, "__REMOVED_CONTRACT_TOKEN__"), encoding="utf-8")


def test_closed_input_list_is_pinned() -> None:
    assert migration.TEXT_FILES == (
        Path("deep-research/references/irb_decision_tree.md"),
        Path("deep-research/references/ethics_checklist.md"),
        Path("shared/references/irb_terminology_glossary.md"),
        Path("deep-research/SKILL.md"),
        Path("deep-research/agents/ethics_review_agent.md"),
        Path("deep-research/agents/research_architect_agent.md"),
        Path("agents/research_architect_agent.md"),
    )


def test_real_repository_and_cli_pass() -> None:
    assert migration.run_checks(REPO_ROOT) == []
    assert migration.main(["--root", str(REPO_ROOT)]) == 0


@pytest.mark.parametrize("rel", migration.REFERENCE_FILES)
@pytest.mark.parametrize(
    "pointer",
    (migration.PROTOCOL_POINTER, migration.REGISTRY_POINTER),
)
def test_each_reference_requires_both_666_pointers(
    tmp_path: Path, rel: Path, pointer: str
) -> None:
    root = mirror(tmp_path)
    remove_all(root, rel, pointer)
    errors = migration.run_checks(root)
    assert any("missing required #666 pointer" in error for error in errors)


@pytest.mark.parametrize("rel", (migration.DEEP_RESEARCH_SKILL, *migration.AGENT_FILES))
@pytest.mark.parametrize(
    "pointer",
    (migration.PROTOCOL_POINTER, migration.REGISTRY_POINTER),
)
def test_each_consumer_requires_both_666_pointers(
    tmp_path: Path, rel: Path, pointer: str
) -> None:
    root = mirror(tmp_path)
    remove_all(root, rel, pointer)
    errors = migration.run_checks(root)
    assert any("missing required #666 consumer pointer" in error for error in errors)


@pytest.mark.parametrize("rel", migration.AGENT_FILES)
def test_each_agent_requires_resolved_gate(tmp_path: Path, rel: Path) -> None:
    root = mirror(tmp_path)
    remove_all(root, rel, migration.RESOLVED_GATE)
    errors = migration.run_checks(root)
    assert any("missing exact resolved+true" in error for error in errors)


@pytest.mark.parametrize("rel", migration.AGENT_FILES)
@pytest.mark.parametrize(
    ("old", "new"),
    (
        ("`downstream_gate.profile_dependent_result_allowed=true`",
         "`downstream_gate.profile_dependent_result_allowed=false`"),
        ("`downstream_gate.profile_dependent_result_allowed=true`",
         "`downstream_gate.profile_dependent_result_allowed=unknown`"),
        ("`resolution_state=resolved`", "`resolution_state=applicability_unresolved`"),
    ),
)
def test_agent_gate_adverse_values_fail(
    tmp_path: Path, rel: Path, old: str, new: str
) -> None:
    root = mirror(tmp_path)
    replace_once(root, rel, old, new)
    assert any("resolved+true" in error for error in migration.run_checks(root))


@pytest.mark.parametrize(
    ("rel", "old", "new"),
    (
        (migration.ETHICS_AGENT, "Only when `resolution_state", "Even when `resolution_state"),
        (migration.ARCHITECT_AGENT, "allowed only when", "allowed unless"),
        (migration.ARCHITECT_MIRROR, "allowed only when", "allowed unless"),
    ),
)
def test_reversed_gate_logic_fails(
    tmp_path: Path, rel: Path, old: str, new: str
) -> None:
    root = mirror(tmp_path)
    replace_once(root, rel, old, new)
    assert any("missing exact resolved+true" in error for error in migration.run_checks(root))


@pytest.mark.parametrize("rel", migration.AGENT_FILES)
def test_closed_gate_fallback_cannot_be_reversed(tmp_path: Path, rel: Path) -> None:
    root = mirror(tmp_path)
    replace_once(root, rel, "and emit no profile-dependent", "and emit profile-dependent")
    assert any("missing exact unresolved/closed-gate" in error for error in migration.run_checks(root))


@pytest.mark.parametrize(
    "clause",
    (
        "Profile-dependent planning is allowed when `profile_dependent_result_allowed=false`.",
        "Profile-dependent results may be emitted when `resolution_state=applicability_unresolved`.",
        "When the gate is missing, this review may emit profile-dependent consent results.",
        "Profile-dependent planning is allowed\nwhen the gate is missing or unresolved.",
        "Authority rows may be dereferenced unless the downstream gate is true.",
        "Profile-dependent planning is allowed without replay validation.",
        "Profile-dependent planning is allowed when the downstream gate is false.",
        "Profile-dependent planning is allowed without replay validation. "
        "Profile-dependent results are not allowed.",
    ),
)
def test_appended_gate_contradictions_fail(tmp_path: Path, clause: str) -> None:
    root = mirror(tmp_path)
    append(root, migration.ETHICS_AGENT, f"\n{clause}\n")
    assert any("non-canonical positive profile use" in error for error in migration.run_checks(root))


def test_canonical_gate_cannot_mask_same_paragraph_extra_permission(
    tmp_path: Path,
) -> None:
    root = mirror(tmp_path)
    extra = " Profile-dependent planning is allowed without replay validation."
    replace_once(
        root,
        migration.ETHICS_AGENT,
        migration.ETHICS_GATE_CONTRACT,
        migration.ETHICS_GATE_CONTRACT + extra,
    )
    errors = migration.run_checks(root)
    assert any("additional positive profile use" in error for error in errors)


@pytest.mark.parametrize(
    "clause",
    (
        "Profile-dependent planning is not allowed without replay validation.",
        "Profile-dependent results may not be emitted while the gate is closed.",
        "Profile-dependent planning is not allowed without replay validation. "
        "Profile-dependent results remain unresolved.",
    ),
)
def test_negative_profile_use_clause_is_not_a_false_positive(
    tmp_path: Path, clause: str
) -> None:
    root = mirror(tmp_path)
    append(root, migration.ETHICS_AGENT, f"\n{clause}\n")
    assert migration.run_checks(root) == []


@pytest.mark.parametrize(
    ("old", "new"),
    (
        ("confirms a successful `validate_resolved_context",
         "does not require a successful `validate_resolved_context"),
        ("This role must not simulate or claim that replay check.",
         "This role may simulate and claim that replay check."),
    ),
)
def test_ethics_replay_evidence_and_no_simulation_are_pinned(
    tmp_path: Path, old: str, new: str
) -> None:
    root = mirror(tmp_path)
    replace_once(root, migration.ETHICS_AGENT, old, new)
    assert any("replay-evidence/no-simulation" in error for error in migration.run_checks(root))


def test_architect_replay_evidence_is_pinned_across_both_mirrors(tmp_path: Path) -> None:
    root = mirror(tmp_path)
    old = "evidence that the permitted dispatching layer successfully called"
    new = "no evidence that the permitted dispatching layer called"
    for rel in (migration.ARCHITECT_AGENT, migration.ARCHITECT_MIRROR):
        replace_once(root, rel, old, new)
    errors = migration.run_checks(root)
    assert any("replay-evidence/no-simulation" in error for error in errors)
    assert not any("mirrors must be byte-identical" in error for error in errors)


@pytest.mark.parametrize(
    ("mode", "clause"),
    (
        ("same", "This role may simulate and claim that replay check."),
        ("new", "This role may simulate replay validation."),
        ("new", "This role may claim replay validation was run."),
        ("new", "Authority-bound review may consume a serialized result without replay validation."),
        ("split", "This role may simulate and\nclaim that replay check."),
        ("split", "This role does not require a successful\nvalidate_resolved_context replay."),
    ),
)
def test_appended_adverse_replay_claims_fail(
    tmp_path: Path, mode: str, clause: str
) -> None:
    root = mirror(tmp_path)
    if mode == "same":
        replace_once(
            root,
            migration.ETHICS_AGENT,
            migration.ETHICS_NO_SIMULATION,
            migration.ETHICS_NO_SIMULATION + " " + clause,
        )
    else:
        append(root, migration.ETHICS_AGENT, f"\n\n{clause}\n")
    assert any("adverse replay contract" in error for error in migration.run_checks(root))


def test_architect_appended_no_evidence_claim_fails_in_both_mirrors(
    tmp_path: Path,
) -> None:
    root = mirror(tmp_path)
    clause = (
        "There is no evidence that the permitted dispatching layer successfully "
        "called validate_resolved_context."
    )
    for rel in (migration.ARCHITECT_AGENT, migration.ARCHITECT_MIRROR):
        append(root, rel, f"\n\n{clause}\n")
    assert any("adverse replay contract" in error for error in migration.run_checks(root))


@pytest.mark.parametrize(
    "clause",
    (
        "This role may claim to have run replay validation.",
        "This role may run replay validation itself.",
        "A serialized authority result may be accepted without replay validation.",
    ),
)
def test_architect_appended_adverse_replay_claims_fail_in_both_mirrors(
    tmp_path: Path, clause: str
) -> None:
    root = mirror(tmp_path)
    for rel in (migration.ARCHITECT_AGENT, migration.ARCHITECT_MIRROR):
        append(root, rel, f"\n\n{clause}\n")
    assert any("adverse replay contract" in error for error in migration.run_checks(root))


def test_negative_replay_controls_are_allowed(tmp_path: Path) -> None:
    root = mirror(tmp_path)
    append(
        root,
        migration.ETHICS_AGENT,
        "\n\nThis role may not simulate or claim that replay check.\n"
        "This role may not simulate replay validation.\n"
        "Authority-bound review may consume a serialized result only after replay validation.\n"
        "Evidence confirms the dispatcher successfully called validate_resolved_context.\n",
    )
    assert migration.run_checks(root) == []


def test_unknown_requirement_id_is_rejected(tmp_path: Path) -> None:
    root = mirror(tmp_path)
    append(
        root,
        migration.IRB_REFERENCE,
        "\n- Requirement: `tw.hsra.article-999.invented-row`\n",
    )
    errors = migration.run_checks(root)
    assert any("referenced requirement id is absent" in error for error in errors)


@pytest.mark.parametrize(
    ("old", "new", "field"),
    (
        ("| `institution_or_irb` |", "| `principal_investigator` |", "obligated_actor"),
        ("`[\"committee_governance\", \"pathway_trace\"]`",
         "`[\"submission_packet\", \"pathway_trace\"]`", "consumer_scopes"),
        ("| `45 CFR 46.107` |", "| `45 CFR 46.108` |", "provision"),
        ("section-46.107)", "section-46.108)", "authority_url"),
    ),
)
def test_requirement_table_metadata_must_join_registry(
    tmp_path: Path, old: str, new: str, field: str
) -> None:
    root = mirror(tmp_path)
    replace_once(root, migration.IRB_REFERENCE, old, new)
    errors = migration.run_checks(root)
    assert any(field in error and "does not exactly match" in error for error in errors)


def test_requirement_table_requires_full_registry_coverage(tmp_path: Path) -> None:
    root = mirror(tmp_path)
    path = root / migration.IRB_REFERENCE
    lines = path.read_text(encoding="utf-8").splitlines()
    lines = [line for line in lines if "eu.gdpr.article-89.2.member-state-derogation" not in line]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    assert any("missing exact requirement table row" in error for error in migration.run_checks(root))


def test_requirement_anchor_label_must_name_exact_provision(tmp_path: Path) -> None:
    root = mirror(tmp_path)
    replace_once(root, migration.IRB_REFERENCE, "[45 CFR 46.107](https://", "[45 CFR 46.108](https://")
    assert any("anchor label" in error for error in migration.run_checks(root))


def test_committee_governance_row_cannot_be_promoted(tmp_path: Path) -> None:
    root = mirror(tmp_path)
    append(
        root,
        migration.IRB_REFERENCE,
        "\n| `us.45cfr46.107.irb-composition` | `submission_packet` |\n",
    )
    errors = migration.run_checks(root)
    assert any("promoted to an investigator/participant" in error for error in errors)


def test_committee_governance_row_cannot_become_consent_item(tmp_path: Path) -> None:
    root = mirror(tmp_path)
    append(
        root,
        migration.ETHICS_CHECKLIST,
        "\n`tw.hsra.article-7.committee-composition` is a consent element.\n",
    )
    errors = migration.run_checks(root)
    assert any("promoted to an investigator/participant" in error for error in errors)


def test_committee_promotion_cannot_hide_across_line_wrap(tmp_path: Path) -> None:
    root = mirror(tmp_path)
    append(
        root,
        migration.IRB_REFERENCE,
        "\n`us.45cfr46.107.irb-composition` is an investigator\n"
        "`submission_packet` requirement.\n",
    )
    assert any("promoted to an investigator/participant" in error for error in migration.run_checks(root))


@pytest.mark.parametrize(
    "clause",
    (
        "The investigator must include `us.45cfr46.107.irb-composition` in the submission packet.",
        "`tw.hsra.article-7.committee-composition` is participant information.",
        "The investigator assigns `tw.hsra.article-7.committee-composition` to a consent-element task.",
    ),
)
def test_natural_language_committee_promotions_fail(
    tmp_path: Path, clause: str
) -> None:
    root = mirror(tmp_path)
    append(root, migration.IRB_REFERENCE, f"\n{clause}\n")
    assert any("promoted to an investigator/participant" in error for error in migration.run_checks(root))


@pytest.mark.parametrize(
    "clause",
    (
        "The investigator must not include `us.45cfr46.107.irb-composition` in the submission packet.",
        "`tw.hsra.article-7.committee-composition` is not participant information.",
    ),
)
def test_explicit_committee_nonpromotion_is_allowed(
    tmp_path: Path, clause: str
) -> None:
    root = mirror(tmp_path)
    append(root, migration.IRB_REFERENCE, f"\n{clause}\n")
    assert migration.run_checks(root) == []


def test_safe_committee_clause_cannot_mask_unsafe_clause(tmp_path: Path) -> None:
    root = mirror(tmp_path)
    append(
        root,
        migration.IRB_REFERENCE,
        "\n`tw.hsra.article-7.committee-composition` is not participant information. "
        "The investigator must include `tw.hsra.article-7.committee-composition` "
        "in the submission packet.\n",
    )
    assert any(
        "promoted to an investigator/participant" in error
        for error in migration.run_checks(root)
    )


def test_registry_cannot_promote_committee_governance_scope(tmp_path: Path) -> None:
    root = mirror(tmp_path)
    path = root / migration.REGISTRY
    registry = json.loads(path.read_text(encoding="utf-8"))
    row = next(
        requirement
        for profile in registry["profiles"]
        for requirement in profile["requirements"]
        if requirement["requirement_id"] == "us.45cfr46.107.irb-composition"
    )
    row["consumer_scopes"].append("submission_packet")
    path.write_text(json.dumps(registry), encoding="utf-8")
    errors = migration.run_checks(root)
    assert any("cannot also claim submission_packet" in error for error in errors)


@pytest.mark.parametrize(
    ("line", "reason"),
    (
        (
            "| Research Scenario | Recommended Review Level |",
            "Recommended Review Level",
        ),
        ("Anonymous survey → Exempt", "scenario-to-pathway mapping"),
        ("Anonymous surveys are Exempt.", "scenario-to-pathway mapping"),
        ("Anonymous surveys qualify for Exempt review.", "scenario-to-pathway mapping"),
        ("Interviews require Expedited review.", "scenario-to-pathway mapping"),
        (
            "Vulnerability always requires Full Board review.",
            "vulnerability/sensitivity automatically mapped",
        ),
        (
            "Online survey: IP addresses will not be recorded.",
            "fixed IP-address-not-recorded promise",
        ),
        ("We do not collect IP addresses.", "fixed IP-address-not-recorded promise"),
        ("This platform does not collect IP addresses.", "fixed IP-address-not-recorded promise"),
        ("No IP addresses are collected.", "fixed IP-address-not-recorded promise"),
        ("IRB will reject an incomplete form.", "IRB will reject"),
        (
            "Comply with local IRB requirements + Taiwan IRB requirements.",
            "local-plus-Taiwan additive rule",
        ),
        (
            "Any retained re-link key falls under pseudonymization.",
            "retained-relink-key legal effect",
        ),
        (
            "Data with a retained re-link key are pseudonymized.",
            "retained-relink-key legal effect",
        ),
        (
            "Keeping a re-link key makes the data pseudonymized.",
            "retained-relink-key legal effect",
        ),
    ),
)
def test_active_universal_regressions_are_rejected(
    tmp_path: Path, line: str, reason: str
) -> None:
    root = mirror(tmp_path)
    append(root, migration.IRB_REFERENCE, f"\n{line}\n")
    errors = migration.run_checks(root)
    assert any(reason in error for error in errors)


def test_full_board_section_checklist_regression_is_rejected(tmp_path: Path) -> None:
    root = mirror(tmp_path)
    append(
        root,
        migration.IRB_REFERENCE,
        "\n## Full Board Review\n\n- [ ] Involves vulnerable populations\n",
    )
    errors = migration.run_checks(root)
    assert any("checklist promoted to Full Board" in error for error in errors)


def test_do_not_prefix_cannot_disguise_active_mapping(tmp_path: Path) -> None:
    root = mirror(tmp_path)
    append(
        root,
        migration.IRB_REFERENCE,
        "\nDo not overlook this assertion: Anonymous surveys are Exempt.\n",
    )
    assert any("scenario-to-pathway" in error for error in migration.run_checks(root))


def test_scenario_mapping_cannot_hide_across_line_wrap(tmp_path: Path) -> None:
    root = mirror(tmp_path)
    append(root, migration.IRB_REFERENCE, "\nAnonymous surveys\nare Exempt.\n")
    assert any("scenario-to-pathway" in error for error in migration.run_checks(root))


@pytest.mark.parametrize(
    "clause",
    (
        "Anonymous surveys do not automatically qualify for Exempt review.",
        "Interviews do not necessarily require Expedited review.",
    ),
)
def test_explicit_scenario_nonmapping_is_allowed(tmp_path: Path, clause: str) -> None:
    root = mirror(tmp_path)
    append(root, migration.IRB_REFERENCE, f"\n{clause}\n")
    assert migration.run_checks(root) == []


def test_safe_scenario_clause_cannot_mask_unsafe_clause(tmp_path: Path) -> None:
    root = mirror(tmp_path)
    append(
        root,
        migration.IRB_REFERENCE,
        "\nAnonymous surveys do not qualify for Exempt review. "
        "Interviews require Expedited review.\n",
    )
    assert any("scenario-to-pathway" in error for error in migration.run_checks(root))


@pytest.mark.parametrize(
    "clause",
    (
        "Vulnerability does not automatically require Full Board review.",
        "Sensitive topics do not always imply Full Board review.",
        "Full Board review is not automatically required for vulnerable populations.",
        "No automatic Full Board review is required for vulnerable populations.",
    ),
)
def test_negated_vulnerability_mapping_is_allowed(
    tmp_path: Path, clause: str
) -> None:
    root = mirror(tmp_path)
    append(root, migration.IRB_REFERENCE, f"\n{clause}\n")
    assert migration.run_checks(root) == []


def test_scenario_and_pathway_on_separate_lines_are_not_joined(tmp_path: Path) -> None:
    root = mirror(tmp_path)
    append(
        root,
        migration.IRB_REFERENCE,
        "\nAnonymous surveys require institutional assessment.\n"
        "Exempt is an authority-specific label, not a result here.\n",
    )
    assert migration.run_checks(root) == []


def test_explicit_historical_forbidden_section_is_not_a_false_positive(
    tmp_path: Path,
) -> None:
    root = mirror(tmp_path)
    append(
        root,
        migration.IRB_REFERENCE,
        """

## Historical forbidden wording

- `IRB will reject`
- `IP addresses will not be recorded`
- `Any retained re-link key falls under pseudonymization`
- `Anonymous survey → Exempt`
""",
    )
    assert migration.run_checks(root) == []


def test_verified_ip_statement_is_not_treated_as_a_fixed_promise(
    tmp_path: Path,
) -> None:
    root = mirror(tmp_path)
    append(
        root,
        migration.TERMINOLOGY_GLOSSARY,
        "\nIP addresses will not be recorded\n"
        "only after that fact and the actual export are verified.\n",
    )
    assert migration.run_checks(root) == []


def test_unverified_ip_promise_split_across_lines_fails(tmp_path: Path) -> None:
    root = mirror(tmp_path)
    append(
        root,
        migration.TERMINOLOGY_GLOSSARY,
        "\nIP addresses will not be\nrecorded by the platform.\n",
    )
    assert any("fixed IP-address" in error for error in migration.run_checks(root))


@pytest.mark.parametrize(
    "clause",
    (
        "This platform does not collect IP addresses only after that fact is verified.",
        "No IP addresses are collected only after the actual export is verified.",
    ),
)
def test_verified_reverse_ip_statement_is_allowed(tmp_path: Path, clause: str) -> None:
    root = mirror(tmp_path)
    append(root, migration.TERMINOLOGY_GLOSSARY, f"\n{clause}\n")
    assert migration.run_checks(root) == []


@pytest.mark.parametrize(
    "clauses",
    (
        "Platform settings and the actual export were verified before disclosure. "
        "IP addresses are not recorded in that export.",
        "The platform settings were verified before disclosure. "
        "IP addresses are not recorded under those settings.",
        "The actual export was verified before disclosure. "
        "IP addresses are not recorded in the verified export.",
    ),
)
def test_immediately_prior_verified_artifact_can_scope_ip_statement(
    tmp_path: Path, clauses: str
) -> None:
    root = mirror(tmp_path)
    append(root, migration.TERMINOLOGY_GLOSSARY, f"\n{clauses}\n")
    assert migration.run_checks(root) == []


@pytest.mark.parametrize(
    "clauses",
    (
        "Platform settings and the actual export were verified before disclosure. "
        "This platform does not collect IP addresses.",
        "Platform settings were verified before disclosure. "
        "IP addresses are not recorded in that export.",
        "The actual export was verified before disclosure. "
        "A disclosure note was prepared. IP addresses are not recorded in that export.",
        "IP addresses are not recorded in the verified export.",
    ),
)
def test_verified_context_without_immediate_matching_reference_does_not_scope_ip(
    tmp_path: Path, clauses: str
) -> None:
    root = mirror(tmp_path)
    append(root, migration.TERMINOLOGY_GLOSSARY, f"\n{clauses}\n")
    assert any("fixed IP-address" in error for error in migration.run_checks(root))


def test_verified_ip_clause_cannot_mask_unverified_clause(tmp_path: Path) -> None:
    root = mirror(tmp_path)
    append(
        root,
        migration.TERMINOLOGY_GLOSSARY,
        "\nIP addresses will not be recorded only after that fact is verified. "
        "This platform does not collect IP addresses.\n",
    )
    assert any("fixed IP-address" in error for error in migration.run_checks(root))


def test_governing_convention_can_scope_relink_key_terminology(
    tmp_path: Path,
) -> None:
    root = mirror(tmp_path)
    append(
        root,
        migration.TERMINOLOGY_GLOSSARY,
        "\nUnder the named governing convention, any retained re-link key means "
        "pseudonymized data.\n",
    )
    assert migration.run_checks(root) == []


def test_scoped_relink_clause_cannot_mask_unscoped_clause(tmp_path: Path) -> None:
    root = mirror(tmp_path)
    append(
        root,
        migration.TERMINOLOGY_GLOSSARY,
        "\nUnder the named governing convention, data with a retained re-link key "
        "are pseudonymized. Data with a retained re-link key are pseudonymized.\n",
    )
    assert any(
        "retained-relink-key legal effect" in error
        for error in migration.run_checks(root)
    )


@pytest.mark.parametrize(
    "clause",
    (
        "Data with a retained re-link key are not automatically pseudonymized.",
        "Keeping a re-link key does not by itself make the data pseudonymized.",
    ),
)
def test_negated_relink_effect_is_allowed(tmp_path: Path, clause: str) -> None:
    root = mirror(tmp_path)
    append(root, migration.TERMINOLOGY_GLOSSARY, f"\n{clause}\n")
    assert migration.run_checks(root) == []


def test_explicit_committee_scope_warning_is_not_a_false_positive(
    tmp_path: Path,
) -> None:
    root = mirror(tmp_path)
    append(
        root,
        migration.IRB_REFERENCE,
        "\nDo not promote `us.45cfr46.107.irb-composition` to `submission_packet`.\n",
    )
    assert migration.run_checks(root) == []


def test_research_architect_mirrors_cannot_drift(tmp_path: Path) -> None:
    root = mirror(tmp_path)
    append(root, migration.ARCHITECT_MIRROR, "\n<!-- mirror drift -->\n")
    errors = migration.run_checks(root)
    assert any("mirrors must be byte-identical" in error for error in errors)


def test_content_failure_returns_one(tmp_path: Path) -> None:
    root = mirror(tmp_path)
    append(root, migration.TERMINOLOGY_GLOSSARY, "\nIRB will reject this.\n")
    assert migration.main(["--root", str(root)]) == 1


def test_missing_input_returns_two(tmp_path: Path) -> None:
    root = mirror(tmp_path)
    (root / migration.IRB_REFERENCE).unlink()
    assert migration.main(["--root", str(root)]) == 2


def test_malformed_registry_returns_two(tmp_path: Path) -> None:
    root = mirror(tmp_path)
    (root / migration.REGISTRY).write_text("{", encoding="utf-8")
    assert migration.main(["--root", str(root)]) == 2


def test_duplicate_registry_key_returns_two(tmp_path: Path) -> None:
    root = mirror(tmp_path)
    path = root / migration.REGISTRY
    text = path.read_text(encoding="utf-8")
    assert '"profiles"' in text
    path.write_text(text.replace('"profiles"', '"profiles_copy": [], "profiles"', 1))
    path.write_text(
        path.read_text(encoding="utf-8").replace('"profiles_copy"', '"profiles"', 1),
        encoding="utf-8",
    )
    assert migration.main(["--root", str(root)]) == 2


def test_argparse_usage_error_is_two() -> None:
    with pytest.raises(SystemExit) as caught:
        migration.main(["--not-an-option"])
    assert caught.value.code == 2
