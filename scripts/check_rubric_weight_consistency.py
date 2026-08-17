#!/usr/bin/env python3
"""Compatibility entrypoint for the retired rubric-weight lint.

Reviewer weights and aggregate scores no longer exist. Keep this filename so
older CI invocations fail closed through the replacement honesty contract.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from check_reviewer_scoring_honesty import check


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--root", type=Path, default=Path(__file__).resolve().parents[1]
    )
    args = parser.parse_args(argv)
    errors, missing = check(args.root)
    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 2 if missing else 1
    print("rubric-weight compatibility check: retired; reviewer scoring honesty OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
