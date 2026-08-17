# ISO/IEC 42001-Spirit Gap Assessment — 2026-08-17

Tracking meta-issue: [#761](https://github.com/Imbad0202/academic-research-skills/issues/761)

## 1. Scope decision: spirit, not certification

ISO/IEC 42001:2023 certifies an **organization's AI management system (AIMS)**. This
repository is a solo-maintained public project: there is no organization to certify,
no second person to appoint as internal auditor, and no management to review anything.
Standing up certification-grade machinery here (AIMS scope statement, management-review
minutes, supplier contract programs, competency records) would produce paperwork that
no one operates and that rots within two releases — the exact failure mode this suite's
own defrift lints exist to prevent.

ARS therefore does **not** pursue certification. It adopts the standard's spirit as
three operating principles, each of which maps to things this repo already values:

| Principle | Meaning here | 42001 anchor (informative) |
|---|---|---|
| **Transparency** | Outward claims match the evidence record; users can see what they get per install channel and where their data goes | Clause 7.4; Annex A.8 |
| **Verifiability** | Every enforcement claim is mechanically checked in CI or explicitly labeled advisory/aspirational; effectiveness claims carry evidence or say `NOT_RUN` | Clauses 8.1, 9.1; Annex A.6 |
| **Feasibility** | Governance artifacts sized to solo maintenance; nothing that needs an org chart to operate | Clause 4 (context), proportionality |

## 2. Method and sources

Dual-track audit, findings merged and re-verified:

1. **In-session structural review** — repository structure, governance documents,
   CI workflows, `audits/` history, mapped against clauses 4–10 and the ISO/IEC 22989
   producer / provider / user roles.
2. **Independent cross-model audit** — GPT-5.6 (xhigh reasoning) with read-only
   repository access, instructed to read the repo end-to-end and to be adversarial
   toward the repo's self-description. No conclusions from track 1 were shared with
   track 2 (anchoring control).

**Verification rule:** no cross-model finding was filed without first-party
re-verification against the working tree. Two corrections came out of that pass:

- Track 2 attributed a literal "zero fail-open" claim to user-facing docs; no such
  phrase exists there. `hooks/run_guard.sh` in fact documents its pass-through
  degrade posture honestly. The residual gap is consolidation (#757), not concealment.
- Track 2 framed the eval-circularity and injection-probe-scope facts as hidden;
  both are disclosed in-repo (`evals/gold/citation_extraction/README.md` states the
  same-reducer ~1.0 score explicitly; `scripts/run_indirect_prompt_injection_probe.py`
  states it never dispatches a model). The gap is that distribution surfaces do not
  carry these ceilings — a surfacing problem, handled by #753 and the existing #745
  claim-anchor mechanism.

## 3. Role summary (producer / provider / user)

- **Producer.** Change control, mutation-tested lints, content locks, and the #745
  capability matrix are strong and unusually honest (8 task families openly `NOT_RUN`).
  The missing half is effectiveness evidence — already tracked (#746, #675, #653) —
  and a single artifact linking risks to controls (#759).
- **Provider.** Technical docs disclose degradations candidly (README Requirements,
  SETUP methods, Pi README), but the facts are scattered (#757) and the marketing
  surfaces (`plugin.json`, `marketplace.json`) outrun the licensed claims (#753).
  Data flows are consent-gated where they matter most (cross-model transport) but
  have no single user-facing map (#758). Security response has a promise without a
  procedure (#760).
- **User.** Human-in-the-loop mechanisms are the repo's strongest 42001-spirit asset:
  read attestation is explicitly a declaration rather than proof, overrides require
  recorded reasoning, disclosure mode helps users meet venue obligations. The honest
  framing to keep: these are **trust-based controls with audit trails**, not coercive
  controls — final integrity responsibility stays with the human researcher, and
  claim surfaces should say so rather than say "cannot be skipped" (#753).

## 4. Verified findings register

All evidence re-verified 2026-08-17 against the working tree at v3.20.1.

| ID | Principle | Finding | Evidence | Disposition |
|---|---|---|---|---|
| T-1 | Transparency | "Production-grade … 39-agent ensemble" outruns the evidence record (8 `NOT_RUN` families; 3 plugin-exposed agents, rest inline by default) | `.claude-plugin/plugin.json:4`, `.claude-plugin/marketplace.json:7`, `docs/PERFORMANCE.md` v3.7.0 section, `docs/STAGE_CAPABILITY_MATRIX.md` | [#753](https://github.com/Imbad0202/academic-research-skills/issues/753) |
| T-2 | Transparency | "No `--no-block` escape hatch" / "cannot be skipped" coexists with documented override-with-reasoning and partial-non-compliance continuation | `academic-pipeline/SKILL.md:344,538,551,568`, `shared/compliance_checkpoint_protocol.md:148` | #753 |
| T-3 | Transparency | "31% → ~5-10%" error-reduction estimate has no traceable derivation | `shared/cross_model_verification.md:36` | #753 |
| T-4 | Transparency | "Never bundle gold labels into the repository" contradicted by `evals/gold/`; intended rule is about unconditional context loading | `shared/ground_truth_isolation_pattern.md` | #753 |
| T-5 | Transparency | 14 workflows enforce at four different strengths; no classification exists | `.github/workflows/` (eval gate PR-only + ack passes; changelog gate release-PRs only; monthly audit opens an issue; tag check post-release) | [#755](https://github.com/Imbad0202/academic-research-skills/issues/755) |
| V-1 | Verifiability | `CITATION.cff` and `POSITIONING.md` citation prose at 3.14.0 vs suite 3.20.1; lint does not watch these surfaces; Zenodo v3.20.1 deposit exists (10.5281/zenodo.21960342) | `CITATION.cff:30`, `POSITIONING.md:98`, `scripts/check_version_consistency.py` | [#754](https://github.com/Imbad0202/academic-research-skills/issues/754) |
| V-2 | Verifiability | `data_access_level: verified_only` contradicts the dirtiest-input rule the suite itself defines | `academic-pipeline/SKILL.md:9,41,403`, `shared/ground_truth_isolation_pattern.md:159` | [#756](https://github.com/Imbad0202/academic-research-skills/issues/756) |
| T-6 | Transparency | Per-channel enforcement variance documented honestly but scattered across five files | README Requirements + Claude Science note, `docs/SETUP.md`, `pi/README.md`, `hooks/run_guard.sh` | [#757](https://github.com/Imbad0202/academic-research-skills/issues/757) |
| T-7 | Transparency | No single data-flow map (resolvers, cross-model transport, update check, 90-day cache) | `shared/cross_model_verification.md`, `docs/SETUP.md:163`, resolver clients in `scripts/` | [#758](https://github.com/Imbad0202/academic-research-skills/issues/758) |
| F-1 | Feasibility | Risks handled piecewise; no artifact links risk → control → evidence status → residual gap | (absence) | [#759](https://github.com/Imbad0202/academic-research-skills/issues/759) |
| F-2 | Feasibility | Governance authority and cross-model-review scope unstated; SECURITY 7-day promise has no procedure behind it | `NOTICE.md`, `SECURITY.md:22` | [#760](https://github.com/Imbad0202/academic-research-skills/issues/760) |

## 5. Findings already tracked before this audit

The effectiveness-evidence half of the audit is not new work; it was already open:

- [#746](https://github.com/Imbad0202/academic-research-skills/issues/746) — execute the frozen outcome-level study
- [#675](https://github.com/Imbad0202/academic-research-skills/issues/675) — live indirect-prompt-injection behavior measurement
- [#676](https://github.com/Imbad0202/academic-research-skills/issues/676) — structural instruction/data isolation
- [#653](https://github.com/Imbad0202/academic-research-skills/issues/653) — reviewer calibration first measured error profile

## 6. Explicitly not adopted

Assessed and rejected as disproportionate for a solo public repo (door stays open if
the project ever grows an organization):

- Formal AIMS document set (scope statement, AI policy, Statement of Applicability)
- Interested-party register; competency records
- Management review minutes; appointed internal auditor (a second model is an
  error-detection control, not organizational independence — and is honestly scoped
  as such in #760)
- Supplier DPA / contract review program; incident register bureaucracy
- Signed per-run execution records (valuable in principle; revisit only if a
  downstream consumer actually needs attestable run evidence)

## 7. Remediation order

1. **#754** — version-surface fix + lint invariant (quick win, this audit's first PR)
2. **#753** — claim-language alignment (highest outward-facing impact)
3. **#757 / #758** — control-availability matrix, data-flow map
4. **#755 / #756** — CI classification table, `data_access_level` correction
5. **#759 / #760** — risk register, governance statement
