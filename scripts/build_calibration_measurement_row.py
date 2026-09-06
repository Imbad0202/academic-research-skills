"""Build the `heldout-measurement/1.1` row for a reviewer-calibration run (#653).

The scorer (`score_calibration_run.py`) produces the mechanical metrics; the
dispatcher's `manifest` stage produces the write-once execution manifest. This
builder folds those two artifacts, the attempt's records, the Phase 3.5 judge
rows, and the pre-registered plan + rubric into ONE contract row and validates
it with the contract checker before writing anything. It never computes a
metric of its own and never fills a judge row: a run without judge output has
no row (llm_judged suites require >=2 judges from two model families, I2).

Pre-registration binding (contract § Version 1.1 pre-registration record):
`plan_ref` / `rubric_ref` are hashed from the working tree AND compared with
the same paths at `frozen_commit` (= the records' `suite_commit`); a drift
refuses — an amendment is the only sanctioned way to change a frozen plan.
A dirty `suite_commit` refuses for the same reason (no commit names the bytes).
The scorer output is bound to the attempt (every scored panel is a complete
panel record here with this attempt id, and vice versa), the manifest is
re-derived from the records — whose raw outputs are re-hashed — and every
declared timing claim is checked against the local manifest before the write.

Output goes wherever `--out` says (write-once). Filing the row under
`evals/heldout/reviewer_calibration/` together with the raw bundles and the
manifest at `--runs-ref` is a separate, deliberate step; `--resolve-refs`
re-runs the checker's R1-R5 once those paths exist in the checkout.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from _e4_evidence import sha256_file  # noqa: E402
import check_heldout_measurement_report as checker  # noqa: E402
from dispatch_calibration_panel import (  # noqa: E402
    MANIFEST_NAME,
    PreconditionFailure,
    build_execution_manifest,
    load_attempt,
    write_once,
)

REPO = Path(__file__).resolve().parent.parent
SUITE = "reviewer_calibration"
SUITE_REL = Path("evals") / "heldout" / SUITE
PLAN_REF = str(SUITE_REL / "RUN_PLAN.md")
RUBRIC_REF = str(SUITE_REL / "adjudication_rubric.md")
RESOLUTION_RULE_REF = RUBRIC_REF + " § Resolution direction"
REPLICATE_RULE_REF = PLAN_REF + " § Schedule and ensembling"
ATOMICITY = (
    "one attempt_id for the whole schedule; a panel abort blocks that replicate "
    "only; recovery is re-dispatch of that replicate under the same substrate plan; "
    "no completed panel is discarded silently and blocked records are committed "
    "(RUN_PLAN § Substrate plan)"
)
CONSTRUCTION_RULE = (
    "balanced accuracy = (TPR + TNR) / 2 over papers; per paper the decision is the "
    "majority vote across replicates of the binarized synthesizer decision "
    "(Accept/Minor Revision -> positive, Major Revision/Reject -> negative) extracted "
    "by the closed `### Decision:` grammar; class-A adjudication is bidirectional "
    "(every synthesis decision is transcribed blind by the adjudicator and compared "
    "with the grammar, adjudication_rubric.md § Resolution direction), so the value "
    "is a point estimate over the audited decisions"
)
SINGLE_FAMILY_CAVEAT = (
    "Single-family panel (substrate_plan primary_only): all five seats and the "
    "synthesizer share one model family; the correlated-error caveat and the "
    "same-family optimism note of the calibration protocol apply."
)
REHEARSAL_CAVEAT = (
    "HARNESS REHEARSAL on the SUPERSEDED 2026-09-06 corpus (#828: PDF layout "
    "leaks the label). Not a measurement. This row must not be filed under "
    "evals/heldout/ and its numbers must not be cited."
)


def sha256_at_commit(commit: str, rel: str, repo: Path = REPO) -> str | None:
    """SHA-256 of `rel` as committed at `commit` (None when absent there)."""
    probe = subprocess.run(
        ["git", "show", f"{commit}:{rel}"], cwd=repo, capture_output=True, check=False
    )
    if probe.returncode != 0:
        return None
    return hashlib.sha256(probe.stdout).hexdigest()


def attempt_identity(work: Path) -> tuple[dict, list[str]]:
    """(identity fields, blocked record names) for the attempt under `work`;
    a dirty `suite_commit` refuses (no commit names the dispatched bytes)."""
    identity, records, blocked = load_attempt(work)
    for stem, record in records:
        if record.get("suite_commit_dirty"):
            raise PreconditionFailure(
                f"{stem}: suite_commit_dirty — no commit names the dispatched bytes; "
                "a row cannot pin frozen_commit to a dirty tree"
            )
    identity["credential_preflight"] = sorted(
        {str(record.get("credential_preflight")) for _, record in records}
    )
    return identity, blocked


def verified_manifest(work: Path) -> Path:
    """The attempt's manifest, re-derived from the records and compared
    field-for-field (everything but `created_at`) with the file on disk."""
    path = work / MANIFEST_NAME
    if not path.is_file():
        raise PreconditionFailure(f"{path} missing; run the dispatcher's manifest stage first")
    on_disk = json.loads(path.read_text(encoding="utf-8"))
    expected = build_execution_manifest(work, on_disk.get("created_at", ""))
    if on_disk != expected:
        raise PreconditionFailure(
            "execution manifest does not match the records it claims to cover; "
            "the manifest is stale or foreign"
        )
    return path


def frozen_ref(rel: str, commit: str) -> tuple[str, str]:
    """(ref, sha256) for a pre-registered file, refusing drift since `commit`."""
    path = REPO / rel
    if not path.is_file():
        raise PreconditionFailure(f"{rel} missing from the checkout")
    now = sha256_file(path)
    then = sha256_at_commit(commit, rel)
    if then is None:
        raise PreconditionFailure(f"{rel} does not exist at frozen_commit {commit}")
    if then != now:
        raise PreconditionFailure(
            f"{rel} changed since frozen_commit {commit}; record an amendment "
            "(amendments are append-only) instead of editing the frozen plan/rubric"
        )
    return rel, now


def agreement_block(judges: list[dict]) -> dict:
    """Divergence by the checker's own definition (`judge_divergence`)."""
    comparable, divergent, _, _ = checker.judge_divergence(judges)
    rate = None if not comparable else round(1 - len(divergent) / len(comparable), 4)
    return {
        "rate": rate,
        "divergent_items": sorted(divergent),
        "note": (
            f"{len(comparable)} item(s) judged by >=2 judges; divergent items escalate "
            "to maintainer adjudication (rubric class B), never majority-of-two"
        ),
    }


def _load_json(path: str | None, default):
    """Strict JSON (duplicate keys and NaN/Infinity refused, like the checker)."""
    if not path:
        return default
    try:
        return checker._loads_strict(Path(path).read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise PreconditionFailure(f"{path}: not strict JSON ({exc})") from exc


def bind_metrics(metrics: dict, work: Path, identity: dict) -> None:
    """The scorer output must describe THIS attempt: every scored panel is a
    complete panel record under `work` with this attempt id, and vice versa."""
    if metrics.get("suite") != SUITE:
        raise PreconditionFailure("metrics file is not a reviewer_calibration scorer output")
    _, records, _ = load_attempt(work)
    panels_here = {
        f"{r['paper_id']}-r{r['replicate']}" for _, r in records if r.get("stage") == "panel"
    }
    scored = metrics.get("per_panel") or {}
    if set(scored) != panels_here:
        raise PreconditionFailure(
            f"metrics cover panels {sorted(scored)} but this attempt holds "
            f"{sorted(panels_here)}; foreign or partial scorer output"
        )
    for key, row in scored.items():
        if row.get("attempt_id") != identity["attempt_id"]:
            raise PreconditionFailure(f"metrics panel {key}: attempt_id is not {identity['attempt_id']!r}")
    papers = {r["paper_id"] for _, r in records if r.get("stage") == "panel"}
    if metrics.get("n_papers") != len(papers):
        raise PreconditionFailure(f"metrics n_papers {metrics.get('n_papers')} != {len(papers)} panel papers here")


def build_row(args) -> dict:
    work = Path(args.work_dir)
    identity, blocked = attempt_identity(work)
    metrics = _load_json(args.metrics, None)
    bind_metrics(metrics, work, identity)
    manifest_path = verified_manifest(work)
    claims = sorted(set(args.claim))
    manifest = _load_json(str(manifest_path), None)
    claim_errors = checker._execution_claim_errors(manifest, set(claims))
    if claim_errors:
        raise PreconditionFailure("declared claims unsupported by the manifest: " + "; ".join(claim_errors))
    judges = _load_json(args.judges, None)
    if not isinstance(judges, list) or not judges:
        raise PreconditionFailure("--judges must be a non-empty JSON list of judge rows (Phase 3.5 output)")

    commit = identity["suite_commit"]
    plan_ref, plan_sha = frozen_ref(PLAN_REF, commit)
    rubric_ref, rubric_sha = frozen_ref(RUBRIC_REF, commit)
    runs_ref = args.runs_ref.rstrip("/")
    blocked_runs = sorted(set(blocked) | set(metrics.get("blocked_runs", [])) | set(args.blocked_run))
    headline_value = metrics["metrics"].get("balanced_accuracy")
    caveats = [SINGLE_FAMILY_CAVEAT, *args.caveat]
    if args.rehearsal:
        caveats.insert(0, REHEARSAL_CAVEAT)

    return {
        "measurement_contract": "heldout-measurement/1.1",
        "suite": SUITE,
        "suite_class": "llm_judged",
        "measurement_date": args.measurement_date,
        "decision_relevant": True,
        "subject": {
            "model_id": identity["model_id"],
            "config": {
                "suite_commit": commit,
                "prompts_ref": (
                    "academic-paper-reviewer/agents/*.md — whole agent file as system prompt "
                    "(calibration single-call engine, pre-v3.6.2); frozen Reviewer "
                    "Configuration Cards per paper (dispatcher cards stage)"
                ),
                "settings": (
                    f"effort={identity['effort']}; substrate_plan={identity['substrate_plan']}; "
                    "headless `claude -p --bare`, tools whitelisted off, fresh process per call; "
                    f"credential_preflight={identity['credential_preflight']}"
                ),
                "sampling": (
                    f"runs_per_paper={metrics['runs_per_paper']}; attempt_id={identity['attempt_id']}; "
                    "one attempt for the whole schedule"
                ),
            },
        },
        "judge_plan": {"exception": "none"},
        "judges": judges,
        "aggregate": {
            "headline": {
                "metric_name": "balanced_accuracy",
                "value": headline_value if headline_value is not None else "NOT COMPUTABLE",
                "construction_rule": CONSTRUCTION_RULE,
                "estimand_status": "point_estimate",
            },
            "agreement": agreement_block(judges),
        },
        "replicates": {
            "per_item": metrics["runs_per_paper"],
            "rule_ref": REPLICATE_RULE_REF,
            "spread": metrics.get("replicate_stability"),
            "exception": args.replicate_exception,
        },
        "adjudication": {
            "applies": True,
            "rubric_ref": rubric_ref,
            "rubric_sha256": rubric_sha,
            "rubric_precommitted": True,
            "blinded_to": ["expected_label"],
            "resolution_direction": "bidirectional",
            "resolution_rule_ref": RESOLUTION_RULE_REF,
            "overrides": _load_json(args.overrides, []),
            "raw_published": True,
        },
        "preregistration": {
            "plan_ref": plan_ref,
            "plan_sha256": plan_sha,
            "rubric_ref": rubric_ref,
            "rubric_sha256": rubric_sha,
            "frozen_commit": commit,
            "frozen_before_dispatch": True,
            "rubric_and_plan_frozen_together": True,
            "judge_template_version": args.judge_template_version,
            "amendments_append_only": True,
            "amendments": _load_json(args.amendments, []),
        },
        "execution_manifest": {
            "ref": f"{runs_ref}/{MANIFEST_NAME}",
            "sha256": sha256_file(manifest_path),
            "write_once": True,
            "claims": claims,
        },
        "attempts": {
            "atomicity": ATOMICITY,
            "partial_published": True,
            "blocked_runs": blocked_runs,
        },
        "raw_outputs": {"retained": True, "paths": [runs_ref + "/"]},
        "results": {
            "design": "single-arm calibration of the panel decision against public venue decisions",
            "arm_roles": {"treatment_or_cohort_arms": [], "variant_packet_arms": []},
            "n_papers": metrics["n_papers"],
            "gold_composition": metrics["gold_composition"],
            "confusion_matrix": metrics["confusion_matrix"],
            "metrics": metrics["metrics"],
            "bootstrap_95ci": metrics.get("bootstrap_95ci"),
            "exact_label_agreement": metrics.get("exact_label_agreement"),
            "replicate_stability": metrics.get("replicate_stability"),
            "auc": metrics.get("auc"),
            "minor_major_boundary_submatrix": metrics.get("minor_major_boundary_submatrix"),
            "per_dimension_calibration_error": metrics.get("per_dimension_calibration_error"),
            "severity_miscalibration_histogram": metrics.get("severity_miscalibration_histogram"),
        },
        "verdict": args.verdict,
        "caveats": caveats,
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--work-dir", required=True, help="dispatcher work dir (records + manifest)")
    parser.add_argument("--metrics", required=True, help="score_calibration_run.py output")
    parser.add_argument("--judges", required=True, help="JSON list of contract-shaped judge rows")
    parser.add_argument("--judge-template-version", required=True)
    parser.add_argument("--measurement-date", required=True)
    parser.add_argument("--runs-ref", required=True, help="repo-relative dir the raw bundles + manifest are filed under")
    parser.add_argument("--verdict", required=True)
    parser.add_argument("--caveat", action="append", default=[])
    parser.add_argument("--claim", action="append", default=[], choices=("same_window", "ordering", "concurrency"))
    parser.add_argument("--overrides", help="JSON list of contract-shaped adjudication overrides")
    parser.add_argument("--amendments", help="JSON list of contract-shaped amendments")
    parser.add_argument("--replicate-exception", help="written sentence when runs_per_paper < 2")
    parser.add_argument(
        "--blocked-run", action="append", default=[],
        help="one attempts.blocked_runs entry, e.g. a judge failure naming its item id (I11)",
    )
    parser.add_argument("--rehearsal", action="store_true", help="stamp the rehearsal caveat first")
    parser.add_argument("--resolve-refs", action="store_true", help="also run checker R1-R5 (filed rows only)")
    parser.add_argument("--out", required=True)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    row = build_row(args)
    errors, warnings = checker.validate_report(row, resolve_refs=args.resolve_refs)
    for line in warnings:
        print(f"WARN: {line}", file=sys.stderr)
    if errors:
        for line in errors:
            print(f"ERROR: {line}", file=sys.stderr)
        print("row NOT written: contract validation failed", file=sys.stderr)
        return 1
    text = json.dumps(row, indent=2, ensure_ascii=False, allow_nan=False) + "\n"
    if checker._loads_strict(text) != row:
        raise PreconditionFailure("serialized row does not round-trip through the strict parser")
    write_once(Path(args.out), text, "a measurement row")
    print(f"measurement row: {args.out} (validated against heldout-measurement/1.1"
          f"{' incl. R1-R5' if args.resolve_refs else ', I-invariants only'})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
