#!/usr/bin/env python3
"""Describe saved outputs at a frozen Git commit; never set quality thresholds."""
from __future__ import annotations
import argparse
import hashlib
import json
import re
import shutil
import statistics
import subprocess
from pathlib import Path
try:
    from .check_writing_surface import ROOT, VOCABULARY, METRICS, check
except ImportError:  # Direct script execution.
    from check_writing_surface import ROOT, VOCABULARY, METRICS, check


def git(root: Path, *args: str) -> bytes:
    executable = shutil.which('git')
    # macOS system Git can be unavailable before Xcode licence acceptance.
    if Path('/opt/homebrew/bin/git').is_file():
        executable = '/opt/homebrew/bin/git'
    return subprocess.run([executable or 'git', '-C', str(root), *args],
                          check=True, capture_output=True).stdout


def eligible(path: str) -> bool:
    return bool(re.fullmatch(
        r'evals/heldout/revision_claim_drift/runs/2026-08-07/subjects/(?!README\.md$)[^/]+\.md', path
    ) or ('/blocked/' not in path and re.fullmatch(
        r'evals/heldout/reviewer_seeded_defects/runs/raw/.+/(?:(?:eic|domain|methodology|perspective|da)\.phase2|synthesis)\.a\d+\.md', path
    )))


def build(root: Path, ref: str) -> dict:
    commit = git(root, 'rev-parse', '--verify', ref + '^{commit}').decode().strip()
    paths = sorted(p for p in git(root, 'ls-tree', '-r', '--name-only', commit).decode().splitlines() if eligible(p))
    if not paths:
        raise ValueError('no eligible saved outputs')
    records = []
    for path in paths:
        raw = git(root, 'show', f'{commit}:{path}')
        report = check(raw.decode('utf-8'))
        records.append({'path': path, 'sha256': hashlib.sha256(raw).hexdigest(),
                        'corpus': 'drafts' if '/subjects/' in path else 'reviewer_outputs',
                        **report['document']})
    distributions = {}
    for corpus in ('all', 'drafts', 'reviewer_outputs'):
        group = [r for r in records if corpus == 'all' or r['corpus'] == corpus]
        distributions[corpus] = {}
        for _, key in METRICS:
            values = sorted(r['metrics'][key] for r in group
                            if r['coverage'] == 'complete' and r['metrics'][key] is not None)
            distributions[corpus][key] = {'n': len(values), 'min': min(values) if values else None,
                'median': statistics.median(values) if values else None,
                'max': max(values) if values else None,
                'mean': statistics.mean(values) if values else None,
                'population_sd': statistics.pstdev(values) if values else None}
    return {'schema_version': 'writing-surface-baseline/1.0', 'input_commit': commit,
            'implementation_sha256': {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
                 for name in ('scripts/check_writing_surface.py', 'scripts/build_writing_surface_baseline.py')},
            'vocabulary_sha256': hashlib.sha256(VOCABULARY.read_bytes()).hexdigest(),
            'selection': 'All eligible paths at input_commit; see eligible() and README. Partial outputs excluded from distributions.',
            'coverage_counts': {kind: sum(r['coverage'] == kind for r in records)
                                for kind in ('complete', 'partial', 'not_checked')},
            'records': records, 'distributions': distributions}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-ref', required=True)
    args = parser.parse_args()
    print(json.dumps(build(ROOT, args.source_ref), ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == '__main__':
    main()
