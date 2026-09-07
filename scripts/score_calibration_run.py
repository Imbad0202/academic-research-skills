"""Deterministic scoring for the reviewer-calibration full-tier run (#653).

Joins gold labels to frozen panel outputs ONLY here — after every panel record
exists — implementing the protocol's gold-label isolation boundary from the
scoring side (`calibration_mode_protocol.md` § Inputs: "Join them to the
completed panel outputs only after the final verdict is frozen").

Inputs are the dispatcher's per-run records plus raw bundles; everything this
script derives is recomputable from those committed artifacts:

  * Verdict extraction: the synthesizer's standard-mode `### Decision:` line
    (closed four-value set). A panel whose synthesis text yields zero or
    multiple distinct decisions is NEVER guessed — it lands in
    `needs_adjudication` and the maintainer supplies the transcription in an
    overrides file (each row carries the verbatim raw excerpt), mirroring the
    #654 adjudication discipline.
  * No score extraction: the seat contract is categorical and no continuous
    score exists (protocol Phase 2: "Do not report AUC"), so no numeric seat
    field is extracted and nothing is averaged.
  * Decision aggregation: binarize (Accept/Minor -> positive,
    Major/Reject -> negative; Lu 2026 Table 1 convention), then majority vote
    across the 3 replicates (odd count: always defined). The exact-decision
    mode is also reported per paper; a three-way exact split is reported as
    `no_exact_mode` rather than resolved.
  * Metrics: balanced accuracy, FNR (over-harsh), FPR (lenient) with 95%
    bootstrap CIs (1000 resamples over papers, fixed seed); exact-label
    agreement (protocol Phase 2 table, against a binary gold set: only
    `Accept`/`Reject` can match exactly); replicate agreement as stability
    (share of papers whose replicates agree on side, and on exact label).
  * Honest gaps are emitted, not omitted: the Minor/Major boundary sub-matrix
    prints NOT ESTIMABLE (all-binary gold set), per-dimension calibration
    error prints NOT COMPUTABLE (no `per_dimension_gold_scores` supplied),
    and the Phase 3.5 severity histogram is aggregated from the judged
    classification rows when supplied (`--severity-classifications`), else
    marked pending.

Stdlib only. Fixed-seed `random.Random` for the bootstrap: reproducible from
the committed inputs alone.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import random
from collections import Counter
import re
import sys
from pathlib import Path

DECISIONS = ("Accept", "Minor Revision", "Major Revision", "Reject")
POSITIVE = {"Accept", "Minor Revision"}

DECISION_RE = re.compile(
    r"^#{2,4}\s*Decision:\s*\[?\s*(Accept|Minor Revision|Major Revision|Reject)\s*\]?\s*$",
    re.MULTILINE,
)
EXACT_LABEL_FOR_GOLD = {"accept": "Accept", "reject": "Reject"}

BOOTSTRAP_RESAMPLES = 1000
BOOTSTRAP_SEED = 653


def extract_decision(synthesis_text: str) -> tuple[str | None, str]:
    """(decision, status): unique hit -> value; else None + reason."""
    hits = {m.group(1) for m in DECISION_RE.finditer(synthesis_text)}
    if len(hits) == 1:
        return next(iter(hits)), "extracted"
    if not hits:
        return None, "no_decision_line"
    return None, f"multiple_distinct_decisions:{sorted(hits)}"


def binarize(decision: str) -> str:
    return "positive" if decision in POSITIVE else "negative"


def load_panels(runs_dir: Path) -> tuple[list[dict], list[str]]:
    records, blocked = [], []
    for path in sorted(runs_dir.glob("*.json")):
        if path.name.startswith("blocked-"):
            blocked.append(path.name)
            continue
        record = json.loads(path.read_text(encoding="utf-8"))
        if record.get("suite") != "reviewer_calibration" or record.get("stage") != "panel":
            continue
        records.append(record)
    return records, blocked


def panel_key(record: dict) -> str:
    return f"{record['paper_id']}-r{record['replicate']}"


def read_raw(runs_dir: Path, record: dict, name: str) -> str | None:
    path = runs_dir / Path(record["raw_bundle"]).relative_to("runs") / name
    if not path.is_file():
        return None
    return path.read_text(encoding="utf-8")


def input_bindings(runs_dir: Path, gold: Path, overrides: Path | None = None,
                   severity: Path | None = None) -> dict:
    """Bind the scorer to exact input bytes, including an explicit absent file."""
    def digest(path):
        return hashlib.sha256(path.read_bytes()).hexdigest() if path else None

    records, _ = load_panels(runs_dir)
    return {
        "gold_sha256": digest(gold),
        "decision_overrides_sha256": digest(overrides),
        "severity_classifications_sha256": digest(severity),
        "synthesis_sha256": {
            panel_key(r): digest(runs_dir / Path(r["raw_bundle"]).relative_to("runs") / "synthesis.md")
            for r in records
        },
    }


def collect(runs_dir: Path, overrides: dict) -> tuple[dict, list[dict]]:
    """Per-panel rows keyed by panel; unresolved extraction problems listed."""
    if not isinstance(overrides, dict):
        raise SystemExit("decision overrides must be a panel-keyed object")
    records, blocked = load_panels(runs_dir)
    panels: dict[str, dict] = {}
    needs_adjudication: list[dict] = []
    for record in records:
        key = panel_key(record)
        synthesis = read_raw(runs_dir, record, "synthesis.md")
        if synthesis is None:
            needs_adjudication.append({"panel": key, "problem": "missing synthesis raw"})
            continue
        if key in panels:
            raise SystemExit(
                f"duplicate panel record for {key} (attempts "
                f"{panels[key].get('attempt_id')!r} and {record.get('attempt_id')!r}); "
                "no completed panel is discarded silently — retire one explicitly"
            )
        raw_decision, raw_status = extract_decision(synthesis)
        decision, status = raw_decision, raw_status
        if key in overrides:
            override = overrides[key]
            if not isinstance(override, dict):
                needs_adjudication.append({"panel": key, "problem": "override must be an object"})
                continue
            excerpt = override.get("raw", "")
            if (override.get("decision") in DECISIONS and isinstance(excerpt, str)
                    and excerpt.strip() and excerpt in synthesis):
                decision, status = override["decision"], "adjudicated"
            else:
                # Rubric A1 requires the verbatim raw excerpt; A2 (no decision
                # statement) is a re-dispatch, never an override.
                needs_adjudication.append(
                    {"panel": key, "problem": f"{status}; override lacks a valid decision or verbatim `raw` excerpt found in synthesis.md"}
                )
                continue
        elif decision is None:
            needs_adjudication.append({"panel": key, "problem": status})
            continue
        panels[key] = {
            "paper_id": record["paper_id"],
            "replicate": record["replicate"],
            "attempt_id": record.get("attempt_id"),
            "decision": decision,
            "decision_status": status,
            "raw_decision": raw_decision,
            "raw_decision_status": raw_status,
        }
    unknown = set(overrides) - {panel_key(r) for r in records}
    if unknown:
        raise SystemExit(f"overrides name unknown panels: {sorted(unknown)}")
    return {"panels": panels, "blocked": blocked}, needs_adjudication


def aggregate_papers(panels: dict[str, dict], expected_replicates: int) -> dict[str, dict]:
    papers: dict[str, dict] = {}
    for row in panels.values():
        papers.setdefault(row["paper_id"], []).append(row)
    out = {}
    for paper_id, rows in sorted(papers.items()):
        if len(rows) != expected_replicates:
            raise SystemExit(
                f"{paper_id}: {len(rows)} scored replicates, expected {expected_replicates}; "
                "a partial ensemble must not enter the aggregate"
            )
        sides = [binarize(r["decision"]) for r in rows]
        majority = "positive" if sides.count("positive") > sides.count("negative") else "negative"
        ranked = Counter(r["decision"] for r in rows).most_common()
        modes = [d for d, c in ranked if c == ranked[0][1]]
        out[paper_id] = {
            "replicate_decisions": [r["decision"] for r in sorted(rows, key=lambda x: x["replicate"])],
            "majority_side": majority,
            "exact_mode": modes[0] if len(modes) == 1 else "no_exact_mode",
            "replicates_agree_on_side": len(set(sides)) == 1,
            "replicates_agree_exactly": len(set(r["decision"] for r in rows)) == 1,
        }
    return out


def outcome_pairs(papers: dict[str, dict], gold: dict[str, str]) -> list[tuple[str, str]]:
    """(predicted_side, gold_label) per paper, in sorted paper-id order."""
    return [(papers[i]["majority_side"], gold[i]) for i in sorted(papers)]


def confusion(pairs: list[tuple[str, str]]) -> dict:
    tp = fn = tn = fp = 0
    for predicted, actual in pairs:
        if actual == "accept":
            if predicted == "positive":
                tp += 1
            else:
                fn += 1
        else:
            if predicted == "negative":
                tn += 1
            else:
                fp += 1
    return {"TP": tp, "FN": fn, "TN": tn, "FP": fp}


def metrics_from_confusion(c: dict) -> dict:
    tpr = c["TP"] / (c["TP"] + c["FN"]) if (c["TP"] + c["FN"]) else None
    tnr = c["TN"] / (c["TN"] + c["FP"]) if (c["TN"] + c["FP"]) else None
    return {
        "balanced_accuracy": (tpr + tnr) / 2 if tpr is not None and tnr is not None else None,
        "FNR_over_harsh": 1 - tpr if tpr is not None else None,
        "FPR_lenient": 1 - tnr if tnr is not None else None,
    }


def bootstrap_ci(pairs: list[tuple[str, str]]) -> dict:
    rng = random.Random(BOOTSTRAP_SEED)
    samples: dict[str, list[float]] = {"balanced_accuracy": [], "FNR_over_harsh": [], "FPR_lenient": []}
    for _ in range(BOOTSTRAP_RESAMPLES):
        resample = [pairs[rng.randrange(len(pairs))] for _ in pairs]  # with replacement
        m = metrics_from_confusion(confusion(resample))
        for key, value in m.items():
            if value is not None:
                samples[key].append(value)
    out = {}
    for key, values in samples.items():
        if not values:
            out[key] = None
            continue
        values.sort()
        lo = values[int(0.025 * len(values))]
        hi = values[min(int(0.975 * len(values)), len(values) - 1)]
        out[key] = {"lo": round(lo, 4), "hi": round(hi, 4), "resamples": len(values)}
    return out


def severity_histogram(path: Path | None) -> dict:
    if path is None:
        return {"status": "pending", "note": "Phase 3.5 judged classifications not yet supplied"}
    rows = json.loads(path.read_text(encoding="utf-8"))
    counts = {"low": 0, "med": 0, "high": 0}
    for row in rows:
        counts[row["risk"]] += 1
    total = sum(counts.values())
    return {
        "status": "computed",
        "counts": counts,
        "shares": {k: round(v / total, 4) if total else None for k, v in counts.items()},
        "total_weaknesses": total,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--runs-dir", required=True)
    parser.add_argument("--gold", required=True, help="manifests/gold_labels.json")
    parser.add_argument("--replicates", type=int, default=3)
    parser.add_argument("--overrides", help="maintainer adjudication overrides JSON")
    parser.add_argument("--severity-classifications")
    parser.add_argument("--out", required=True)
    args = parser.parse_args(argv)

    overrides = (
        json.loads(Path(args.overrides).read_text(encoding="utf-8")) if args.overrides else {}
    )
    collected, needs_adjudication = collect(Path(args.runs_dir), overrides)
    if needs_adjudication:
        print("PANELS NEEDING ADJUDICATION (no metrics emitted):", file=sys.stderr)
        for row in needs_adjudication:
            print(f"  {row['panel']}: {row['problem']}", file=sys.stderr)
        return 1

    gold_rows = json.loads(Path(args.gold).read_text(encoding="utf-8"))["labels"]
    gold = {r["paper_id"]: r["label"] for r in gold_rows}
    papers = aggregate_papers(collected["panels"], args.replicates)
    missing_gold = sorted(set(papers) - set(gold))
    if missing_gold:
        raise SystemExit(f"papers without gold labels: {missing_gold}")
    missing_results = sorted(set(gold) - set(papers))
    if missing_results:
        raise SystemExit(
            f"gold papers without a complete scored ensemble: {missing_results}; "
            "the full tier publishes only when every gold paper is scored"
        )

    pairs = outcome_pairs(papers, gold)
    c = confusion(pairs)
    exact_hits = sum(
        1 for i, row in papers.items() if row["exact_mode"] == EXACT_LABEL_FOR_GOLD[gold[i]]
    )
    result = {
        "suite": "reviewer_calibration",
        "tier": "full",
        "input_bindings": input_bindings(
            Path(args.runs_dir), Path(args.gold),
            Path(args.overrides) if args.overrides else None,
            Path(args.severity_classifications) if args.severity_classifications else None,
        ),
        "n_papers": len(papers),
        "gold_composition": {
            "accept": sum(1 for i in papers if gold[i] == "accept"),
            "reject": sum(1 for i in papers if gold[i] == "reject"),
        },
        "runs_per_paper": args.replicates,
        "confusion_matrix": c,
        "metrics": metrics_from_confusion(c),
        "bootstrap_95ci": bootstrap_ci(pairs),
        "exact_label_agreement": {
            "count": exact_hits,
            "share": round(exact_hits / len(papers), 4),
            "target_set_size": len(papers),
            "note": "binary gold set: only Accept (gold accept) / Reject (gold reject) can match exactly",
        },
        "replicate_stability": {
            "side_agreement_share": round(
                sum(1 for r in papers.values() if r["replicates_agree_on_side"]) / len(papers), 4
            ),
            "exact_agreement_share": round(
                sum(1 for r in papers.values() if r["replicates_agree_exactly"]) / len(papers), 4
            ),
        },
        "auc": "NOT REPORTED — no continuous rubric score exists (calibration protocol Phase 2)",
        "minor_major_boundary_submatrix": (
            "NOT ESTIMABLE — gold set lacks both sides of the Minor/Major boundary "
            "(all-binary accept/reject corpus)"
        ),
        "per_dimension_calibration_error": (
            "NOT COMPUTABLE (annotated_n=0/{n}, missing={n}) — adjudicated "
            "per-dimension gold scores were not supplied".format(n=len(papers))
        ),
        "severity_miscalibration_histogram": severity_histogram(
            Path(args.severity_classifications) if args.severity_classifications else None
        ),
        "blocked_runs": collected["blocked"],
        "per_paper": papers,
        "per_panel": {
            k: {kk: vv for kk, vv in v.items() if kk != "paper_id"}
            for k, v in sorted(collected["panels"].items())
        },
    }
    Path(args.out).write_text(
        json.dumps(result, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
    )
    print(f"metrics written: {args.out}")
    for key, value in result["metrics"].items():
        print(f"  {key}: {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
