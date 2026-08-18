# Governance

**Scope.** This is a solo-maintained public project. This page states who decides,
what the cross-model review layer does and does not provide, what happens if
maintenance stops, and how the project's operating principles relate to
ISO/IEC 42001.

**Origin.** ISO/IEC 42001-spirit gap assessment
([`audits/iso42001-spirit-gap-assessment-2026-08-17.md`](audits/iso42001-spirit-gap-assessment-2026-08-17.md),
finding F-2, [#760](https://github.com/Imbad0202/academic-research-skills/issues/760)).
The principles below are distilled operating principles (with informative anchors to
ISO/IEC 42001), not the standard's own principle list and not a certification claim.

## Decision authority

- The maintainer (Cheng-I Wu, [@Imbad0202](https://github.com/Imbad0202)) is the
  final decision authority for scope, design, merges, releases, deprecations, and
  security response. There is no committee, no co-maintainer, and no organizational
  review body behind this repository.
- External contributions are welcome through issues and pull requests; the
  maintainer's review is the only human review gate. The CI gates
  ([docs/ARCHITECTURE.md §7.1](docs/ARCHITECTURE.md#71-ci-workflow-enforcement-classes-755))
  are deterministic checks enforcing at the strengths classified there — some
  blocking, some advisory or post-push only; none is a second reviewer.
- Community ports and sibling distributions follow the platform-ports policy in
  [CONTRIBUTING.md](CONTRIBUTING.md) (listings in [THIRD_PARTY.md](THIRD_PARTY.md));
  their ongoing maintenance, support, and platform-specific behavior are the port
  maintainer's responsibility, not the ARS maintainer's.

## What cross-model review provides, and what it does not

Several workflows consult a second model family: the consent-gated cross-model
verification layer ([`shared/cross_model_verification.md`](shared/cross_model_verification.md))
and the maintainer's pre-ship dual-track reviews. These are **error-detection
controls**: a model with a different training distribution may catch failures the
first model family misses. The suite makes no measured effectiveness claim for
this layer.

They are **not organizational independence**. A second model is not a second person.
In the user-facing verification layer, the researcher configures, consents to, and
adjudicates every cross-model result in their own run; in this repository's pre-ship
reviews, the maintainer does. In neither case is any output of that layer an
independent audit, an external review, or a sign-off by anyone other than the human
operating it. Surfaces that report cross-model results (panel provenance blocks,
review records) state execution facts for exactly this reason rather than claiming
independence — and where earlier repo records say "independent cross-model audit",
that names blind, separately executed runs (execution separation), not
organizational independence.

## Release authority and change control

Releases are tagged by the maintainer after the pre-tag gates pass
(version-consistency lint, changelog-covers-merges; see
[CONTRIBUTING.md](CONTRIBUTING.md)), with a post-tag re-check of the same lint
([docs/ARCHITECTURE.md §7.1](docs/ARCHITECTURE.md#71-ci-workflow-enforcement-classes-755)).
Between releases, changes land on `main` through pull requests, with CI workflows
enforcing at the strengths classified in §7.1.

## Continuity and end of life

There is no maintenance SLA. If maintenance stops, this repository stays public
under its license, which already permits non-commercial community forks (see
[LICENSE](LICENSE));
no handover procedure is promised. Users should treat prolonged maintainer
inactivity as end-of-life and either pin the last release or move to a fork they
trust; the [SECURITY.md](SECURITY.md) response promises lapse with the rest of
maintenance at that point.

## Security response

Security reports follow the private-reporting and triage procedure in
[SECURITY.md](SECURITY.md). The only hard time-bound promise there is the
acknowledgement window; fix timelines are severity-tiered best-effort targets,
stated as such, because a solo maintainer cannot honestly promise more.

## Operating principles and ISO/IEC 42001

ISO/IEC 42001 certifies an organization's AI management system. This repository has
no organization to certify and does not pursue certification (assessment §1). It
instead adopts three distilled operating principles, each with an informative anchor
into the standard:

| Principle | Meaning here | Informative 42001 anchor |
|---|---|---|
| **Transparency** | Outward claims match the evidence record; users can see what they get per install channel and where their data goes | Clause 7.4; Annex A.8 |
| **Verifiability** | Every enforcement claim is mechanically checked in CI or explicitly labeled advisory/aspirational; effectiveness claims carry evidence or say `NOT_RUN` | Clauses 8.1, 9.1; Annex A.6 |
| **Feasibility** | Governance artifacts sized to solo maintenance; nothing that needs an org chart to operate | Clause 4 (context), proportionality |

### How the 2026-08 remediation series covers the standard's core

The operative core of ISO/IEC 42001 is a risk-based management loop (clauses 4-10,
plan-do-check-act) with a control catalogue (Annex A) and an informative list of
organizational objectives and risk sources (Annex C). The eight findings issues from
the gap assessment map onto that core as follows — informative anchors, not clause
conformance claims:

| Issue | What it does | Principle served | Informative anchor |
|---|---|---|---|
| #754 version surfaces | Citation/version metadata matches the released suite | Transparency | Clause 7.4 |
| #753 claim-language alignment | Distribution surfaces stay within evidence ceilings | Transparency | Clause 7.4; Annex A.8 |
| #757 control availability | Per-channel map of which controls actually operate | Transparency | Annex A.8 |
| #758 data-flow map | Single map of network touchpoints and local stores | Transparency | Clause 7.4; Annex A.8 |
| #755 CI enforcement classes | Each workflow's real enforcement strength classified | Verifiability | Clause 9.1 |
| #756 data-access-level correction | Skill frontmatter `data_access_level` follows the dirtiest-input rule | Verifiability | Clause 8.1 |
| #759 risk register (PR #777) | Risk → control → evidence status → residual gap in one artifact | Verifiability | Clause 6; Clause 8.1 |
| #760 this page + SECURITY triage | Decision authority, cross-model scope, response procedure stated | Feasibility | Clause 5, sized to Clause 4 |

The check-act half of the loop is carried by the standing artifacts these issues
leave behind: the capability matrix and the risk register (#759, PR #777) record
what is unverified, the open issues the assessment §5 links (#746, #675, #676,
#653 at the time of writing) are the improvement queue, and a scheduled monthly
workflow opens a harness-retirement audit issue so prompt-debt review is scheduled
rather than forgotten. That is the whole loop, sized to one maintainer.

### Annex C objectives assessed as not applicable

Annex C's objective list assumes systems this project does not contain. Assessed
2026-08 against the informative list; re-assess if the project's shape changes:

- **Fairness.** ARS is a text-analysis and writing-support toolkit. It makes no
  consequential allocation decisions about people: no person is scored, and no
  output allocates admission, funding, publication, or access in the real world
  (the reviewer skill's manuscript scores and editorial decisions are advisory
  simulations for the author's own use). Behavioral signals do exist inside a
  session (the advisory Collaboration Depth Observer's collaboration-pattern
  reading; the Socratic Mentor's intent and readiness signals that adapt dialogue
  pacing), but they shape only the user's own session, are read only by that user,
  and produce no decision about anyone. Fairness obligations attach to systems
  that allocate treatment or access; none exists here.
- **Environmental impact.** The project trains no models and operates no training
  or inference infrastructure. Its footprint is local script execution, CI runs,
  and ordinary LLM API usage under each user's own account, which the user — not
  this repo — controls.
- **AI training-data quality.** The suite does not train or fine-tune any model, so
  there is no training corpus to govern. (Quality of *bibliographic* data is in
  scope and handled by the citation-verification layer — a different thing.)
