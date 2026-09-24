---
type: regex
target: last_message
match: not_contains
flags: im
arm: with-only
---
^[ \t]*#{1,6}[ \t]+(?![^\n\r]*\b(?:no|not|none|without|n/a)\b)[^\n\r]*(?:concern[ -]tracker|preserved source|source preservation)|^[ \t]*\*\*(?![^\n\r]*\b(?:no|not|none|without|n/a)\b)[^*\n\r]*(?:concern[ -]tracker|preserved source|source preservation)[^*\n\r]*\*\*|^[ \t]*<!--[ \t]*concern:CC-[0-9]+|^[ \t]*#{1,6}[ \t]+Concern CC-[0-9]+|^[ \t]*>[ \t]*\*\*Human-subjects boundary:?\*\*|^[ \t]*(?:\*\*)?Status\b[^\n\r]*no concern is asserted resolved
