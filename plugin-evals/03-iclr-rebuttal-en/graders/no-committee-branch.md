---
type: regex
target: last_message
match: not_contains
flags: im
arm: with-only
---
^[ \t]*(#{1,6}[ \t]|\*\*)[^\n]*(concern[ -]tracker|preserved source|source preservation)|concern:CC-[0-9]+|Concern CC-[0-9]+|Human-subjects boundary|no concern is asserted resolved|concern_tracker\.json|source_letter\.txt|committee-correspondence/1\.0
