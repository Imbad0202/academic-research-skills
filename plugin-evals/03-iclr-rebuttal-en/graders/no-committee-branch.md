---
type: regex
target: last_message
match: not_contains
flags: im
arm: with-only
---
^[ \t]*#{1,6}[ \t]+(?![^\n]*\b(?:no|not|without)\b)[^\n]*(?:concern[ -]tracker|preserved source|source preservation)|^[ \t]*\*\*(?![^*\n]*\b(?:no|not|without)\b)[^*\n]*(?:concern[ -]tracker|preserved source|source preservation)[^*\n]*\*\*|concern:CC-[0-9]+|Concern CC-[0-9]+|\*\*Human-subjects boundary:?\*\*|no concern is asserted resolved|committee_correspondence/[0-9a-f]{12}
