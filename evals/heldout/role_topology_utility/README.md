# Role-topology utility seed (#582, v0.1)

Offline design and repository-owned synthetic seed for two independent classes:
decomposable reviewer evidence review and sequential writing/revision. Authority:
[`docs/design/2026-08-13-582-role-topology-utility-design.md`](../../../docs/design/2026-08-13-582-role-topology-utility-design.md).

The exact arms, role graphs, budgets, tools, three-replicate rule, stopping rule,
uncertainty disclosure, blinding, and UVV definition live in `study_plan.json` and
its closed schema. `heldout_set.json` contains two synthetic fixtures per task and
a closed schema. `codebook.md` keeps the two evaluators separate.
`invocation_adapter.md` makes the synthetic task envelope authoritative and
limits embedded production contracts to role perspective and boundaries. Each
role row also freezes a hash-bound study output contract, so intermediate seats
emit their own artifacts and only the declared final seat emits the evaluated
outcome; this prevents production phase/output grammar from contaminating the
matched task.

Run only the offline commands:

```bash
python scripts/run_role_topology_utility_dry_run.py validate-assets
python scripts/run_role_topology_utility_dry_run.py dry-run
python scripts/run_role_topology_utility_dry_run.py materialize --output-dir /new/empty/path
```

No subject, expert, adjudicator, model, API, tool, or measurement run exists.
Materialized manifests permanently declare no dispatch and no measurement. Before
future dispatch, select and hash one exact provider/model/CLI/auth plan, satisfy the
#653 interpretation dependency for reviewer results, obtain fresh consent, and
precommit separate blinded human-expert packets. #582 remains open.
