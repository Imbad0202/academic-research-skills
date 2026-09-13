---
max_turns: 20
timeout_seconds: 600
allowed_tools: [Read, Glob, Grep, Skill]
model: sonnet
runs: 3
---
幫我檢查這支檔案的引用，哪些是沒用到的？

```python
import os
import json
import hashlib
from collections import defaultdict
from pathlib import Path


def load_records(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def group_by_venue(records: list[dict]) -> dict[str, list[dict]]:
    groups: dict[str, list[dict]] = defaultdict(list)
    for rec in records:
        groups[rec.get("venue", "unknown")].append(rec)
    return groups


def summarise(groups: dict[str, list[dict]]) -> list[tuple[str, int]]:
    return sorted(((venue, len(items)) for venue, items in groups.items()), key=lambda t: -t[1])


if __name__ == "__main__":
    data = load_records(Path("records.json"))
    for venue, count in summarise(group_by_venue(data)):
        print(f"{venue}: {count}")
```
