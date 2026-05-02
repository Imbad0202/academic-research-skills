# audit_artifact_consistency fixtures

Synthetic JSON / YAML / JSONL files for ARS v3.6.7 Phase 6.3 lint tests.

`positive/` — bundles that should produce zero findings.
`negative/` — bundles that should produce at least one finding (rule_id named in the directory).

These fixtures stay independent of the in-memory test fixtures in
test_check_audit_artifact_consistency.py so the lint script can be
spot-checked from the CLI without running pytest.
