# Judge reasoning excerpts — 2026-07-11 measurement

Verbatim excerpts of the judge agents' prose reasoning, captured alongside the
boolean outcomes in `measurement-2026-07-11.json`. Not every agent produced prose
(several returned bare JSON); this file commits everything that was captured that
bears on a **miss** or a **notable pass**, so the mechanism reading in the audit
report is auditable. Judge: `claude-sonnet-5`, isolated per batch, given only the
advisory section variant + 6 items.

## Off-list title-shell misses — the exemption clause read broadly

- `ti-004` (post-#503 rep2, MISS): "'Beyond Awareness: Cybersecurity Training and
  Employee Security Behavior' — names specific mechanism (training → behavior) and
  domain (cybersecurity); doesn't reduce to a generic 'X and Y' shell despite
  superficial brevity. No match."
- `ti-002` (post-#503 rep2, MISS): "'The Weight of Care: Nurse Workload and the
  Quality of Patient Care' — names a specific mechanism/population (nurse workload
  → patient care quality); domain-native vocabulary, not a swappable shell."
- `ti-012` (post-#503 rep2, MISS): "names a specific mechanism/domain (vocabulary
  acquisition, L2 learners); doesn't survive noun-swap into an arbitrary field
  meaninglessly. No row match."
- `ti-013` (pre-#503, MISS): "'Aging Apart: Social Isolation Among Older Adults'
  is a title, not a frame pattern from the list — no match." (Pre-variant
  reasoning: judged against the table only, as instructed.)

## The same shape caught when the judge reads it as a bare pair

- `ti-004` / `ti-002` (pre-#503, FIRE): "bare 'X and Y' title shell, matches WP06
  (bare study-of frame)." (Same items, opposite call, adjacent runs — the
  decorated-title shape sits exactly on the exemption boundary.)
- `ti-007` (pre-#503, FIRE, cited "off-list shell"); (post-#503 rep1/rep2, FIRE,
  cited WP06).

## Family-variant behavior

- `nat-065` (pre-#503, FIRE): "'How does X affect Y' (SES → access to higher
  education) matches WP01 impact/effect frame." — interrogative rewording of a
  listed family, caught even pre-#503.
- `el-003` (post-#503 rep1, FIRE as off-list): "'What shapes X among Y' …
  matches the generic factors/determinants shell closely enough (off-list but
  clearly a shell: 'what shapes X among Y' swaps trivially)."
- `el-013` (post-#503 rep2, MISS): "'How does material choice bear on the
  durability of concrete structures' names a specific mechanism (material choice
  → durability) and site (concrete structures) — specific, not generic; doesn't
  survive swap." (Stable miss in all runs; same broad-exemption reading.)

## Hard negatives — the exemption working as intended

- `dn-006` (pre-#503, correct SILENT): "highly specific mediator construct, named
  scale, named population — domain-native operationalized wording, not a bare
  shell match despite containing 'mediate the effect.'"
- `dn-009` (pre-#503, correct SILENT): "precise mediation model with named
  instruments (IUS-12, GAD-7) — domain-native, high-confidence no match."
- `nat-077` (pre-#503, MISS): "close to WP16 … but not the canonical 'barriers
  and facilitators to X' pair shell … weak/ambiguous match, not high-confidence."
  (Post-#503: FIRE citing WP16 in both replicates.)
