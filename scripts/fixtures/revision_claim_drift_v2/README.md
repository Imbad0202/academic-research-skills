# Revision-claim-drift v2 subject-context fixtures

These records are synthetic schema fixtures. They are not measurements, do not
contain model outputs, and do not imply that a held-out fleet was rerun.

- `subject_context_machine_supported.json` demonstrates machine-supported
  neutral-cwd execution after a failed bare-mode authentication attempt, using
  a completed standard-mode probe with no visible target mechanism.
- `subject_context_attested_only.json` demonstrates the explicitly weaker
  operator-attested state when the machine probe is unavailable.
- `subject_context_not_isolated.json` demonstrates visible mechanism text and
  the mandatory closed contamination acknowledgement.
- `subject_context_unknown.json` demonstrates an unresolved, non-claiming
  record when neither machine evidence nor an attestation is available.

Every digest, launcher-configuration hash, and timestamp is synthetic. Raw
physical paths, instruction text, probe prompts, probe outputs, and free-form
attestations are intentionally absent. Negative cases are generated as in-memory
mutations of these positive fixtures so malformed records cannot be mistaken for
reusable artifacts. The guard also derives truthful inside-repository and
repository-visible `not_isolated` records from these fixtures.
