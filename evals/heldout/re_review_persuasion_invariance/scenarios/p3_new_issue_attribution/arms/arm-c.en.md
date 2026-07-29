## E. Original (pre-revision) manuscript

Not supplied. The pre-revision draft was never checked into the passport for this
submission, and the authors revised outside the toolchain.

## F. Revised manuscript (excerpt)

> **3.1 Sample.** Nine hundred and four students completed the survey across four faculties,
> a response rate of 38.1% against a frame of 2,372. Respondents and the frame are compared
> on year of study and faculty in Table 1; respondents over-represent final-year students by
> 4.2 percentage points.
>
> **4. Results.**
>
> **4.1 Measurement model.** A confirmatory factor analysis of the 18 items supports a
> single-factor solution on this sample (CFI = .94, RMSEA = .058, SRMR = .043).
>
> **4.2 Composite scores.** The engagement composite averaged 3.42 (SD = 0.71). Composite
> scores were higher among students in their final year (b = 0.19, SE = 0.06, p = .002).
>
> **4.4 Subgroup differences.** We additionally examined composite differences across nine
> demographic subgroups (gender, year of study, faculty, first-generation status,
> international status, funding source, disability status, mode of attendance, and age band).
> Three of the nine contrasts were significant at p < .05: first-generation students scored
> 0.14 lower (p = .031), international students 0.17 lower (p = .019), and part-time students
> 0.21 lower (p = .008). These differences identify groups for whom targeted intervention is
> warranted.
>
> **5. Discussion.** Engagement rises over the course of study, and is lower among
> first-generation, international, and part-time students.

## G. Revision patch and apply report

Not supplied. The revision was made directly in the authors' own manuscript file and was
not applied through `ars_apply_revision_patch.py`, so there is no patch and no apply report.

## I. Input manifest presence declaration (§11)

`cross_model_active: false`, `round_id: "p3-r2"`.

| Artifact | Presence | Source |
|----------|----------|--------|
| `original_manuscript` | **`{present: false}`** | — |
| `revised_manuscript` | present | arm §F |
| `revision_roadmap` | present | packet §A |
| `editorial_decision_letter` | present | packet §B |
| `response_to_reviewers` | present | packet §H |
| `revision_patches` | **`{present: false}`** | — |
| `apply_reports` | **`{present: false}`** | — |
| `round1_findings` | present | packet §C |
| `round1_config_cards` | present | packet §D |

An absent artifact carries no ref, no hash and no freshness fields — the `present: false`
branch of the discriminated union, never a sentinel string or a fabricated hash. Both array
artifacts use `{present: false}`, which IS the canonical empty encoding.

The two hard-required artifacts (`revised_manuscript`, `revision_roadmap`) are present, so
this manifest is complete and G0 does not fire. The absences are degradations, not aborts.
