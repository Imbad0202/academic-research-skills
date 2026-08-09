#!/usr/bin/env python3
"""Lint the bounded #680 human-subjects reference migration.

This checker reads only the named migration references/consumers and the local
#666 registry.  It is a hermetic prose/registry contract lint, not an authority
resolver, legal opinion, review-pathway classifier, or submission-readiness
checker.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable


IRB_REFERENCE = Path("deep-research/references/irb_decision_tree.md")
ETHICS_CHECKLIST = Path("deep-research/references/ethics_checklist.md")
TERMINOLOGY_GLOSSARY = Path("shared/references/irb_terminology_glossary.md")
DEEP_RESEARCH_SKILL = Path("deep-research/SKILL.md")
ETHICS_AGENT = Path("deep-research/agents/ethics_review_agent.md")
ARCHITECT_AGENT = Path("deep-research/agents/research_architect_agent.md")
ARCHITECT_MIRROR = Path("agents/research_architect_agent.md")
REGISTRY = Path("shared/human_subjects_authority_registry.json")

REFERENCE_FILES = (IRB_REFERENCE, ETHICS_CHECKLIST, TERMINOLOGY_GLOSSARY)
AGENT_FILES = (ETHICS_AGENT, ARCHITECT_AGENT, ARCHITECT_MIRROR)
TEXT_FILES = (
    *REFERENCE_FILES,
    DEEP_RESEARCH_SKILL,
    *AGENT_FILES,
)

PROTOCOL_POINTER = "shared/references/human_subjects_authority_protocol.md"
REGISTRY_POINTER = "shared/human_subjects_authority_registry.json"
RESOLVED_GATE = "profile_dependent_result_allowed"
RESOLVED_STATE = "resolution_state=resolved"
TRUE_GATE = "downstream_gate.profile_dependent_result_allowed=true"

ETHICS_GATE_CONTRACT = (
    "Only when `resolution_state=resolved` and "
    "`downstream_gate.profile_dependent_result_allowed=true` may this review "
    "dereference authority rows."
)
ARCHITECT_GATE_CONTRACT = (
    "Profile-dependent planning is allowed only when "
    "`resolution_state=resolved` and "
    "`downstream_gate.profile_dependent_result_allowed=true`."
)
ETHICS_CLOSED_GATE = (
    "If authority selection, a bound input, replay-validation evidence, or the "
    "gate is missing or unresolved, set `submission_readiness=unresolved`, keep "
    "`review_pathway=institutional determination required`, and emit no "
    "profile-dependent consent, pathway, or readiness result."
)
ARCHITECT_CLOSED_GATE = (
    "If the context, exact selection, replay-validation evidence, or gate is "
    "missing or unresolved, set `submission_readiness=unresolved`, keep the "
    "pathway at `institutional determination required`, and emit no "
    "profile-dependent consent-element, pathway, or readiness result."
)
ETHICS_REPLAY_CONTRACT = (
    "Authority-bound review may consume a serialized result only when the "
    "permitted dispatching layer supplies its exactly bound context and registry "
    "and confirms a successful `validate_resolved_context(result, context, "
    "registry)` replay from `scripts/resolve_human_subjects_authority.py`."
)
ETHICS_NO_SIMULATION = "This role must not simulate or claim that replay check."
ARCHITECT_REPLAY_CONTRACT = (
    "Accept a serialized authority result only with its exactly bound context and "
    "registry and evidence that the permitted dispatching layer successfully "
    "called `validate_resolved_context(result, context, registry)` from "
    "`scripts/resolve_human_subjects_authority.py`."
)
ARCHITECT_NO_SIMULATION = (
    "This role has no shell authority and must not claim to have run replay "
    "validation."
)
AGENT_GATE_CONTRACTS = {
    ETHICS_AGENT: (ETHICS_GATE_CONTRACT, ETHICS_CLOSED_GATE),
    ARCHITECT_AGENT: (ARCHITECT_GATE_CONTRACT, ARCHITECT_CLOSED_GATE),
    ARCHITECT_MIRROR: (ARCHITECT_GATE_CONTRACT, ARCHITECT_CLOSED_GATE),
}
AGENT_REPLAY_CONTRACTS = {
    ETHICS_AGENT: (ETHICS_REPLAY_CONTRACT, ETHICS_NO_SIMULATION),
    ARCHITECT_AGENT: (ARCHITECT_REPLAY_CONTRACT, ARCHITECT_NO_SIMULATION),
    ARCHITECT_MIRROR: (ARCHITECT_REPLAY_CONTRACT, ARCHITECT_NO_SIMULATION),
}

REQUIREMENT_TABLE_HEADER = (
    "| Exact requirement id | Exact provision | Obligated actor | Consumer scopes | "
    "Bounded subject | Primary-source anchor |"
)
REQUIREMENT_TABLE_SEPARATOR = "|---|---|---|---|---|---|"

# These namespaces are deliberately narrower than the general registry id
# grammar.  They identify only V1 requirement ids, not profile ids or ordinary
# dotted prose.
REQUIREMENT_ID = re.compile(
    r"(?<![A-Za-z0-9_.-])"
    r"(?:us\.45cfr46\.|tw\.hsra\.|eu\.gdpr\.article-)"
    r"[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?"
    r"(?![A-Za-z0-9_.-])"
)
HEADING = re.compile(r"^(#{1,6})\s+(.*)$")
PATHWAY = re.compile(r"\b(?:exempt|expedited|full[ -]board)\b", re.IGNORECASE)
SCENARIO = re.compile(
    r"\b(?:scenario|survey|interview|experiment|observation|public data|"
    r"data analysis|secondary analysis|student|teacher|faculty|classroom|"
    r"mental health|vulnerab|sensitive|portfolio|tracking)\w*\b",
    re.IGNORECASE,
)
EXPLANATORY_SECTION = re.compile(
    r"\b(?:historical|legacy|deprecated|removed|forbidden|banned|prohibited|"
    r"anti[- ]pattern)\b",
    re.IGNORECASE,
)
COMMITTEE_PROMOTION = re.compile(
    r"\b(?:submission[-_ ]packet|participant[-_ ]information|"
    r"consent[-_ ]element|consent[-_ ]item|"
    r"investigator[-_ ](?:packet|task|requirement))s?\b",
    re.IGNORECASE,
)
INLINE_CODE = re.compile(r"^`([^`]+)`$")
MARKDOWN_LINK = re.compile(r"^\[([^\]]+)\]\((https://[^\s()]+)\)$")
PARAGRAPH_SINGLE_LINE = re.compile(
    r"^\s*(?:#{1,6}\s|\||```|~~~|---\s*$)", re.IGNORECASE
)
NEW_LIST_ITEM = re.compile(r"^\s*(?:[-*+]\s|[0-9]+[.)]\s)")


@dataclass(frozen=True)
class RequirementMeta:
    obligated_actor: str
    consumer_scopes: tuple[str, ...]
    provision: str
    authority_url: str


@dataclass(frozen=True)
class RequirementTableRow:
    line_number: int
    provision: str
    obligated_actor: str
    consumer_scopes: tuple[str, ...]
    anchor_label: str
    authority_url: str


class MigrationInputError(RuntimeError):
    """The fixed migration inputs cannot be read or structurally trusted."""


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    value: dict[str, Any] = {}
    for key, item in pairs:
        if key in value:
            raise MigrationInputError(f"duplicate JSON key: {key}")
        value[key] = item
    return value


def _reject_nonfinite(token: str) -> Any:
    raise MigrationInputError(f"non-finite JSON value: {token}")


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise MigrationInputError(f"{path}: cannot read UTF-8 text: {exc}") from exc


def _load_registry(path: Path) -> tuple[dict[str, RequirementMeta], list[str]]:
    try:
        raw = path.read_text(encoding="utf-8")
        value = json.loads(
            raw,
            object_pairs_hook=_unique_object,
            parse_constant=_reject_nonfinite,
        )
    except (OSError, UnicodeError, json.JSONDecodeError, MigrationInputError) as exc:
        raise MigrationInputError(f"{path}: cannot load JSON: {exc}") from exc
    if not isinstance(value, dict) or not isinstance(value.get("profiles"), list):
        raise MigrationInputError(f"{path}: profiles must be an array")

    requirements: dict[str, RequirementMeta] = {}
    errors: list[str] = []
    for profile_index, profile in enumerate(value["profiles"]):
        if not isinstance(profile, dict) or not isinstance(
            profile.get("requirements"), list
        ):
            raise MigrationInputError(
                f"{path}: profiles[{profile_index}].requirements must be an array"
            )
        for requirement_index, requirement in enumerate(profile["requirements"]):
            location = f"profiles[{profile_index}].requirements[{requirement_index}]"
            if not isinstance(requirement, dict):
                raise MigrationInputError(f"{path}: {location} must be an object")
            requirement_id = requirement.get("requirement_id")
            actor = requirement.get("obligated_actor")
            scopes = requirement.get("consumer_scopes")
            anchor = requirement.get("authority_anchor")
            if (
                not isinstance(requirement_id, str)
                or not isinstance(actor, str)
                or not isinstance(scopes, list)
                or not all(isinstance(scope, str) for scope in scopes)
                or not isinstance(anchor, dict)
                or not isinstance(anchor.get("provision"), str)
                or not isinstance(anchor.get("authority_url"), str)
            ):
                raise MigrationInputError(
                    f"{path}: {location} needs id, actor, scopes, and a row-local "
                    "provision/authority URL"
                )
            if requirement_id in requirements:
                raise MigrationInputError(
                    f"{path}: duplicate requirement_id: {requirement_id}"
                )
            requirements[requirement_id] = RequirementMeta(
                obligated_actor=actor,
                consumer_scopes=tuple(scopes),
                provision=anchor["provision"],
                authority_url=anchor["authority_url"],
            )
            if "committee_governance" in scopes:
                if "submission_packet" in scopes:
                    errors.append(
                        f"{REGISTRY}: committee-governance requirement "
                        f"{requirement_id!r} cannot also claim submission_packet scope"
                    )
    if not requirements:
        raise MigrationInputError(f"{path}: registry has no requirements")
    return requirements, errors


def _normalized(line: str) -> str:
    return " ".join(line.casefold().split())


def _assertion_clauses(paragraph: str) -> tuple[str, ...]:
    """Split assertions after Markdown line wrapping has been joined."""

    return tuple(
        clause.strip()
        for clause in re.split(r"(?<=[.!?;])\s+", paragraph)
        if clause.strip()
    )


def _code_cell(cell: str) -> str | None:
    match = INLINE_CODE.fullmatch(cell.strip())
    return match.group(1) if match else None


def _parse_requirement_table(
    text: str, requirements: dict[str, RequirementMeta]
) -> list[str]:
    errors: list[str] = []
    if text.count(REQUIREMENT_TABLE_HEADER) != 2:
        errors.append(
            f"{IRB_REFERENCE}: exact six-column requirement header must appear twice"
        )
    if text.count(REQUIREMENT_TABLE_SEPARATOR) != 2:
        errors.append(
            f"{IRB_REFERENCE}: exact six-column requirement separator must appear twice"
        )

    rows: dict[str, RequirementTableRow] = {}
    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not (stripped.startswith("|") and stripped.endswith("|")):
            continue
        cells = [cell.strip() for cell in stripped[1:-1].split("|")]
        if not cells:
            continue
        requirement_id = _code_cell(cells[0])
        if requirement_id is None or REQUIREMENT_ID.fullmatch(requirement_id) is None:
            continue
        if len(cells) != 6:
            errors.append(
                f"{IRB_REFERENCE}:{line_number}: requirement row must have six columns"
            )
            continue
        if requirement_id in rows:
            errors.append(
                f"{IRB_REFERENCE}:{line_number}: duplicate requirement table row: "
                f"{requirement_id}"
            )
            continue

        provision = _code_cell(cells[1])
        actor = _code_cell(cells[2])
        scopes_json = _code_cell(cells[3])
        anchor = MARKDOWN_LINK.fullmatch(cells[5])
        if provision is None or actor is None or scopes_json is None or anchor is None:
            errors.append(
                f"{IRB_REFERENCE}:{line_number}: requirement row needs code-formatted "
                "provision/actor/scopes and one HTTPS anchor"
            )
            continue
        try:
            scopes_value = json.loads(scopes_json)
        except json.JSONDecodeError as exc:
            errors.append(
                f"{IRB_REFERENCE}:{line_number}: consumer scopes are not JSON: {exc.msg}"
            )
            continue
        if not isinstance(scopes_value, list) or not all(
            isinstance(scope, str) for scope in scopes_value
        ):
            errors.append(
                f"{IRB_REFERENCE}:{line_number}: consumer scopes must be a JSON "
                "string array"
            )
            continue
        rows[requirement_id] = RequirementTableRow(
            line_number=line_number,
            provision=provision,
            obligated_actor=actor,
            consumer_scopes=tuple(scopes_value),
            anchor_label=anchor.group(1),
            authority_url=anchor.group(2),
        )

    table_ids = set(rows)
    registry_ids = set(requirements)
    for missing in sorted(registry_ids - table_ids):
        errors.append(f"{IRB_REFERENCE}: missing exact requirement table row: {missing}")
    for unexpected in sorted(table_ids - registry_ids):
        errors.append(
            f"{IRB_REFERENCE}: table requirement is absent from {REGISTRY}: {unexpected}"
        )

    for requirement_id in sorted(table_ids & registry_ids):
        row = rows[requirement_id]
        meta = requirements[requirement_id]
        comparisons = (
            ("provision", row.provision, meta.provision),
            ("obligated_actor", row.obligated_actor, meta.obligated_actor),
            ("consumer_scopes", row.consumer_scopes, meta.consumer_scopes),
            ("authority_url", row.authority_url, meta.authority_url),
        )
        for field, actual, expected in comparisons:
            if actual != expected:
                errors.append(
                    f"{IRB_REFERENCE}:{row.line_number}: {requirement_id} {field} "
                    f"does not exactly match {REGISTRY}: {actual!r} != {expected!r}"
                )
        allowed_labels = {meta.provision}
        if meta.provision.startswith("人體研究法第"):
            allowed_labels.add(f"{meta.provision}（全國法規資料庫中文控制文本）")
        if row.anchor_label not in allowed_labels:
            errors.append(
                f"{IRB_REFERENCE}:{row.line_number}: {requirement_id} anchor label "
                "does not identify its exact provision"
            )
    return errors


def _paragraph_contexts(text: str) -> dict[int, tuple[int, str]]:
    """Map each line to (owner line, Markdown paragraph text)."""

    lines = text.splitlines()
    contexts: dict[int, tuple[int, str]] = {}
    index = 0
    while index < len(lines):
        line = lines[index]
        if not line.strip() or PARAGRAPH_SINGLE_LINE.match(line):
            contexts[index + 1] = (index + 1, line)
            index += 1
            continue
        start = index
        paragraph = [line.strip()]
        index += 1
        while index < len(lines):
            candidate = lines[index]
            if (
                not candidate.strip()
                or PARAGRAPH_SINGLE_LINE.match(candidate)
                or NEW_LIST_ITEM.match(candidate)
            ):
                break
            paragraph.append(candidate.strip())
            index += 1
        joined = " ".join(paragraph)
        for line_index in range(start, index):
            contexts[line_index + 1] = (start + 1, joined)
    return contexts


def _is_positive_profile_use(paragraph: str) -> bool:
    patterns = (
        r"profile-dependent.{0,96}?\b(?:is )?(?:allowed|permitted)\b",
        r"\bmay\s+(?:dereference|consume|emit|use|produce|return)\b"
        r".{0,96}profile-dependent",
        r"profile-dependent.{0,96}?\bmay\s+(?:be\s+)?"
        r"(?:dereferenced|consumed|emitted|used|produced|returned)\b",
        r"\bmay\b.{0,40}?\bdereference authority rows\b",
        r"\bauthority rows\s+may\s+(?:be\s+)?dereferenced\b",
    )
    for raw_clause in _assertion_clauses(paragraph):
        clause = _normalized(raw_clause.replace("`", ""))
        for pattern in patterns:
            for match in re.finditer(pattern, clause):
                if not re.search(r"\b(?:not|never|no)\b", match.group(0)):
                    return True
    return False


def _adverse_replay_reason(paragraph: str) -> str | None:
    checks = (
        (
            r"\bthis role\s+may\s+(?!not\b)(?:simulate|claim|run)\b"
            r".{0,64}\b(?:replay check|replay validation|"
            r"validate_resolved_context)\b",
            "role may simulate or claim replay",
        ),
        (
            r"\bauthority-bound review\s+may\s+consume\s+a serialized result\b"
            r".{0,64}\bwithout\s+(?:a successful\s+)?replay validation\b",
            "authority result may be consumed without replay validation",
        ),
        (
            r"\bdoes not require\s+a successful\s+validate_resolved_context\b",
            "successful validate_resolved_context replay is made optional",
        ),
        (
            r"\bno evidence\b[^.;!?]{0,160}\bsuccessfully called\b",
            "successful dispatcher-call evidence is denied",
        ),
        (
            r"\ba serialized authority result\s+may\s+be accepted\b"
            r".{0,64}\bwithout\s+replay validation\b",
            "serialized authority result may be accepted without replay validation",
        ),
    )
    for raw_clause in _assertion_clauses(paragraph):
        clause = _normalized(raw_clause.replace("`", ""))
        for pattern, reason in checks:
            if re.search(pattern, clause):
                return reason
    return None


def _committee_promotion_is_negated(line: str, requirement_id: str) -> bool:
    escaped = re.escape(requirement_id)
    scope = (
        r"(?:submission[-_ ]packet|participant[-_ ]information|"
        r"consent[-_ ]element|investigator[-_ ](?:packet|task|requirement))"
    )
    direct_command = re.search(
        rf"\b(?:do not|must not|never)\s+(?:promote|convert|treat|turn|map|"
        rf"assign|include)\b[^.;:]{{0,120}}{escaped}[^.;:]{{0,120}}{scope}",
        line,
        re.IGNORECASE,
    )
    direct_predicate = re.search(
        rf"{escaped}[^.;:]{{0,80}}\b(?:is|are)\s+not\b[^.;:]{{0,40}}"
        rf"{scope}|{escaped}[^.;:]{{0,80}}\bmust not be\s+"
        rf"(?:included|assigned|promoted)\b[^.;:]{{0,60}}{scope}",
        line,
        re.IGNORECASE,
    )
    return direct_command is not None or direct_predicate is not None


def _active_lines(text: str) -> Iterable[tuple[int, str, tuple[str, ...]]]:
    """Yield lines outside explicitly historical/forbidden Markdown sections."""

    headings: list[tuple[int, str]] = []
    explanatory_level: int | None = None
    for line_number, line in enumerate(text.splitlines(), start=1):
        match = HEADING.match(line)
        if match:
            level = len(match.group(1))
            title = match.group(2).strip()
            while headings and headings[-1][0] >= level:
                headings.pop()
            headings.append((level, title))
            if explanatory_level is not None and level <= explanatory_level:
                explanatory_level = None
            if EXPLANATORY_SECTION.search(title):
                explanatory_level = level
        section_is_explanatory = explanatory_level is not None
        if section_is_explanatory:
            continue
        yield line_number, line, tuple(title for _, title in headings)


def _is_scenario_mapping(line: str) -> bool:
    if not PATHWAY.search(line):
        return False
    normalized = _normalized(line)
    if re.search(
        r"\b(?:scenario|surveys?|interviews?|experiments?|observations?|students?|"
        r"teachers?|faculty|classrooms?|data analysis|secondary analysis|mental "
        r"health|vulnerab\w*|sensitiv\w*|portfolios?|tracking)\b"
        r"[^.!?;]{0,80}(?:→|=>|->)[^.!?;]{0,48}"
        r"\b(?:exempt|expedited|full[ -]board)\b",
        normalized,
    ):
        return True
    direct_mapping = re.search(
        r"\b(?:anonymous\s+)?(?:surveys?|interviews?|experiments?|observations?|"
        r"students?|teachers?|faculty|classrooms?|data analysis|secondary analysis|"
        r"mental health|vulnerab\w*|sensitiv\w*|portfolios?|tracking)\b"
        r"[^.!?;]{0,64}\b(?:qualif(?:y|ies) for|requires?|receives?|gets?|maps? to)\b"
        r"[^.!?;]{0,40}\b(?:exempt|expedited|full[ -]board)\b",
        normalized,
    )
    if direct_mapping is not None and not re.search(
        r"\b(?:do|does|must|may|is|are)\s+not(?:\s+\w+){0,3}\s+"
        r"(?:qualif\w*|require\w*|receive\w*|get\w*|map\w*)\b",
        direct_mapping.group(0),
    ):
        return True
    if re.search(r"\brecommended (?:review )?(?:level|pathway)\b", normalized):
        return True
    if re.search(
        r"\b(?:anonymous\s+)?(?:surveys?|interviews?|experiments?|observations?|"
        r"students?|teachers?|faculty|classrooms?|data analysis|secondary analysis|"
        r"mental health|vulnerab\w*|sensitiv\w*|portfolios?|tracking)\b"
        r"[^.!?;]{0,64}\b(?:is|are)\s+(?:typically\s+|automatically\s+)?"
        r"(?:exempt|expedited|full[ -]board)\b",
        normalized,
    ):
        return True
    if re.search(r"(?:^|[^=])=(?!=)", line) and SCENARIO.search(line):
        return True
    if line.lstrip().startswith("|") and line.count("|") >= 3 and SCENARIO.search(line):
        return True
    return False


def _automatic_mapping_is_negated(value: str) -> bool:
    return re.search(
        r"\b(?:do|does|did|is|are|was|were|must|may|can|will|shall)\s+"
        r"(?:not|never)\b(?:\s+\w+){0,4}\s+"
        r"(?:automatic\w*|always|requir\w*|impli\w*|map\w*|qualif\w*)\b|"
        r"\bnever\s+(?:automatic\w*|always|requir\w*|impli\w*|map\w*|"
        r"qualif\w*)\b|"
        r"\bno\s+(?:automatic\w*\s+)?full[ -]board\b",
        value,
    ) is not None


def _verified_artifacts(clause: str) -> set[str]:
    normalized = _normalized(clause)
    artifacts = {
        "configuration": r"configurations?",
        "settings": r"settings?",
        "export": r"exports?",
        "fact": r"facts?",
    }
    verified: set[str] = set()
    for name, noun in artifacts.items():
        matches = (
            re.search(
                rf"\b{noun}\b.{{0,64}}\b(?:is|are|was|were|has been|have been)\s+"
                r"verified\b",
                normalized,
            ),
            re.search(
                rf"\bverif(?:y|ies|ied)\b.{{0,64}}\b{noun}\b",
                normalized,
            ),
        )
        if any(
            match is not None
            and not re.search(r"\b(?:not|never|no)\b", match.group(0))
            for match in matches
        ):
            verified.add(name)
    return verified


def _uses_immediately_prior_verified_artifact(
    clause: str, immediately_prior_clause: str | None
) -> bool:
    if immediately_prior_clause is None:
        return False
    referenced: set[str] = set()
    aliases = {
        "configuration": "configuration",
        "configurations": "configuration",
        "setting": "settings",
        "settings": "settings",
        "export": "export",
        "exports": "export",
        "fact": "fact",
        "facts": "fact",
    }
    for match in re.finditer(
        r"\b(?:that|those|the verified)\s+"
        r"(configuration(?:s)?|settings?|exports?|facts?)\b",
        _normalized(clause),
    ):
        referenced.add(aliases[match.group(1)])
    return bool(referenced & _verified_artifacts(immediately_prior_clause))


def _forbidden_clause_reason(
    clause: str,
    headings: tuple[str, ...],
    immediately_prior_clause: str | None = None,
) -> str | None:
    normalized = _normalized(clause)
    if "recommended review level" in normalized:
        return "universal 'Recommended Review Level' mapping"
    if "irb will reject" in normalized:
        return "unsupported 'IRB will reject' prediction"
    fixed_ip_promise = re.search(
        r"\bip address(?:es)?\b.{0,48}\b(?:will|must|shall|are|is)\b.{0,16}"
        r"\bnot\b.{0,12}\b(?:recorded|collected|stored|logged)\b",
        normalized,
    )
    reverse_ip_promise = re.search(
        r"\b(?:we|(?:this|that|the|our) (?:survey|platform|system|team)|"
        r"the research team)\b.{0,32}\b(?:do|does|will|shall)\s+not\s+"
        r"(?:record|collect|store|log)\w*\b.{0,48}\bip address(?:es)?\b",
        normalized,
    )
    no_ip_promise = re.search(
        r"\bno ip address(?:es)?\b.{0,24}\b(?:are|is|will be)\b.{0,16}"
        r"\b(?:recorded|collected|stored|logged)\b",
        normalized,
    )
    verified_condition = re.search(
        r"\b(?:only (?:if|after|when)|after|when)\b.{0,80}\bverif\w*\b",
        normalized,
    )
    if (
        "ip address" in normalized
        and (fixed_ip_promise or reverse_ip_promise or no_ip_promise)
        and not verified_condition
        and not _uses_immediately_prior_verified_artifact(
            clause, immediately_prior_clause
        )
    ):
        return "fixed IP-address-not-recorded promise"
    if re.search(
        r"\b(?:comply with\s+)?local(?: irb)? requirements?\b.{0,40}"
        r"(?:\+|\band\b|\bplus\b).{0,24}\btaiwan(?: irb)? requirements?\b",
        normalized,
    ) or re.search(
        r"\btaiwan(?: irb)? requirements?\b.{0,40}"
        r"(?:\+|\band\b|\bplus\b).{0,24}\blocal(?: irb)? requirements?\b",
        normalized,
    ):
        return "unconditional local-plus-Taiwan additive rule"
    retained_key_effect = re.search(
        r"\b(?:any |data with (?:a )?)?retained (?:re-?link|link) key\b.{0,80}"
        r"\b(?:always|necessarily|constitutes?|means?|falls? under|is|are)\b"
        r".{0,40}\bpseudonymi[sz]",
        normalized,
    ) or re.search(
        r"\b(?:keeping|retaining) (?:a |the )?(?:re-?link|link) key\b.{0,80}"
        r"\b(?:makes?|renders?|means?)\b.{0,48}\bpseudonymi[sz]",
        normalized,
    )
    governing_scope = re.search(
        r"\b(?:under|within|according to)\b.{0,60}"
        r"\b(?:selected|named|applicable|governing|gdpr|convention|regime)\b",
        normalized,
    )
    effect_is_negated = retained_key_effect is not None and re.search(
        r"\b(?:not|never|does not|do not)\b", retained_key_effect.group(0)
    )
    if retained_key_effect and not effect_is_negated and not governing_scope:
        return "unconditional retained-relink-key legal effect"
    full_board_section = any("full board" in heading.casefold() for heading in headings)
    vulnerability = re.search(r"\b(?:vulnerab\w*|sensitiv\w*)\b", normalized)
    automatic_mapping = re.search(
        r"\b(?:vulnerab\w*|sensitiv\w*)\b.{0,80}"
        r"(?:(?:→|=>|->)|\b(?:automatic\w*|always|requires?|implies?|maps? to|"
        r"qualif\w* for)\b).{0,48}\bfull[ -]board\b|"
        r"\bfull[ -]board\b.{0,80}\b(?:automatic\w*|always|required|mapped)\b"
        r".{0,32}\b(?:for|by)\b.{0,48}\b(?:vulnerab\w*|sensitiv\w*)\b",
        normalized,
    )
    checklist = bool(re.match(r"^\s*[-*]\s*\[[ xX]\]", clause))
    if automatic_mapping and not _automatic_mapping_is_negated(normalized):
        return "vulnerability/sensitivity automatically mapped to Full Board"
    if vulnerability and full_board_section and checklist:
        return "vulnerability/sensitivity checklist promoted to Full Board"
    if _is_scenario_mapping(clause):
        return "scenario-to-pathway mapping"
    return None


def _forbidden_reason(paragraph: str, headings: tuple[str, ...]) -> str | None:
    clauses = _assertion_clauses(paragraph)
    for index, clause in enumerate(clauses):
        immediately_prior = clauses[index - 1] if index else None
        reason = _forbidden_clause_reason(clause, headings, immediately_prior)
        if reason is not None:
            return reason
    return None


def run_checks(root: Path) -> list[str]:
    """Return deterministic #680 contract errors; raise on unusable inputs."""

    root = root.resolve()
    texts = {rel: _read_text(root / rel) for rel in TEXT_FILES}
    requirements, errors = _load_registry(root / REGISTRY)
    errors.extend(_parse_requirement_table(texts[IRB_REFERENCE], requirements))

    for rel in REFERENCE_FILES:
        text = texts[rel]
        for pointer in (PROTOCOL_POINTER, REGISTRY_POINTER):
            if pointer not in text:
                errors.append(f"{rel}: missing required #666 pointer: {pointer}")

    for rel in (DEEP_RESEARCH_SKILL, *AGENT_FILES):
        text = texts[rel]
        for pointer in (PROTOCOL_POINTER, REGISTRY_POINTER):
            if pointer not in text:
                errors.append(f"{rel}: missing required #666 consumer pointer: {pointer}")

    for rel, (positive_gate, closed_gate) in AGENT_GATE_CONTRACTS.items():
        text = texts[rel]
        if positive_gate not in text:
            errors.append(
                f"{rel}: missing exact resolved+true dereference condition"
            )
        if closed_gate not in text:
            errors.append(f"{rel}: missing exact unresolved/closed-gate fallback")
        if text.count(f"`{TRUE_GATE}`") != 1 or text.count(f"`{RESOLVED_STATE}`") != 1:
            errors.append(
                f"{rel}: resolved+true gate expressions must each appear exactly once"
            )
        gate_contexts = _paragraph_contexts(text)
        positive_paragraphs: list[tuple[int, str]] = []
        for line_number, line in enumerate(text.splitlines(), start=1):
            owner_line, paragraph = gate_contexts.get(
                line_number, (line_number, line)
            )
            if owner_line != line_number:
                continue
            if _is_positive_profile_use(paragraph):
                positive_paragraphs.append((owner_line, paragraph))
            replay_adverse = _adverse_replay_reason(paragraph)
            if replay_adverse is not None:
                errors.append(
                    f"{rel}:{owner_line}: adverse replay contract: {replay_adverse}"
                )
        canonical_positive = [
            item for item in positive_paragraphs if positive_gate in item[1]
        ]
        if len(canonical_positive) != 1:
            errors.append(
                f"{rel}: exactly one canonical positive-use gate paragraph is required"
            )
        for owner_line, paragraph in positive_paragraphs:
            if positive_gate not in paragraph:
                errors.append(
                    f"{rel}:{owner_line}: non-canonical positive profile use is forbidden"
                )
            elif _is_positive_profile_use(paragraph.replace(positive_gate, "", 1)):
                errors.append(
                    f"{rel}:{owner_line}: canonical gate paragraph contains "
                    "additional positive profile use"
                )

    for rel, contracts in AGENT_REPLAY_CONTRACTS.items():
        for contract in contracts:
            if contract not in texts[rel]:
                errors.append(f"{rel}: missing exact replay-evidence/no-simulation contract")

    if texts[ARCHITECT_AGENT] != texts[ARCHITECT_MIRROR]:
        errors.append(
            f"{ARCHITECT_AGENT} and {ARCHITECT_MIRROR}: "
            "research-architect mirrors must be byte-identical"
        )

    committee_ids = sorted(
        requirement_id
        for requirement_id, meta in requirements.items()
        if "committee_governance" in meta.consumer_scopes
    )
    for rel, text in texts.items():
        for match in REQUIREMENT_ID.finditer(text):
            requirement_id = match.group(0)
            if requirement_id not in requirements:
                line_number = text.count("\n", 0, match.start()) + 1
                errors.append(
                    f"{rel}:{line_number}: referenced requirement id is absent "
                    f"from {REGISTRY}: {requirement_id}"
                )

        paragraph_contexts = _paragraph_contexts(text)
        for line_number, line, headings in _active_lines(text):
            owner_line, paragraph = paragraph_contexts.get(
                line_number, (line_number, line)
            )
            if owner_line != line_number:
                continue
            promoted_ids: set[str] = set()
            for clause in _assertion_clauses(paragraph):
                for requirement_id in committee_ids:
                    if (
                        requirement_id not in promoted_ids
                        and requirement_id in clause
                        and COMMITTEE_PROMOTION.search(clause)
                        and not _committee_promotion_is_negated(clause, requirement_id)
                    ):
                        errors.append(
                            f"{rel}:{owner_line}: committee-governance requirement "
                            f"{requirement_id!r} promoted to an investigator/participant "
                            "consumer scope"
                        )
                        promoted_ids.add(requirement_id)
            reason = _forbidden_reason(paragraph, headings)
            if reason is not None:
                errors.append(f"{rel}:{owner_line}: forbidden #680 regression: {reason}")

    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    args = parser.parse_args(argv)
    try:
        errors = run_checks(args.root)
    except MigrationInputError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print("Human-subjects reference migration lint passed (#680).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
