---
type: regex
target: last_message
match: not_contains
flags: im
arm: with-only
---
^[ \t]*#{1,6}[^\n]*(concern[ -]tracker|preserved source|source preservation)|concern_tracker\.json|source_letter\.txt|committee-correspondence/1\.0
