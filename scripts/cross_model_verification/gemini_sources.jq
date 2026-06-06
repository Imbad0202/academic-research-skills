# Canonical source-URL extraction — Gemini generateContent (google_search tool).
# CONTRACT: derive SOURCES ONLY from the chunks actually cited by groundingSupports (the
# supported chunk indices), NOT every groundingChunks entry — so a VERIFIED whose text cites no
# chunk leaves SOURCES blank and is downgraded to NOT_SEARCHED at step 5.
#
# FAIL-CLOSED on malformed indices: a model can emit junk groundingChunkIndices. Without a guard,
#   - a negative index (e.g. -1) silently selects a chunk from the END of the array, fabricating a
#     real-but-wrong source URL that would falsely satisfy the "VERIFIED must carry a source" rule
#     and defeat the downgrade;
#   - a string index raises a jq error ("Cannot index array with string").
# The `select(type=="number" and . >= 0 and . < ($chunks|length))` admits only valid in-range
# numeric indices; anything else is dropped, so a malformed support set yields blank SOURCES
# (→ NOT_SEARCHED) rather than a fabricated or crashing result.
#
# Every container is normalized to an array first (`arr/1`): `length` and `$chunks[.]` are only
# meaningful on arrays, and a malformed groundingChunks/groundingSupports arriving as a string or
# object would otherwise mis-count length or crash `$chunks[.]`. The top-level `candidates` is
# array-normalized too, so a malformed `candidates` arriving as an object does not crash the
# `[0]` access (`arr(.candidates)[0]` on a non-array yields null → no metadata → blank sources).
# Extracted URIs are filtered to non-empty strings so a malformed `uri` (a number/bool/object)
# never fabricates a source. Used with `jq -r`.
def arr($x): if ($x | type) == "array" then $x else [] end;
(arr(.candidates)[0].groundingMetadata) as $meta
| arr($meta.groundingChunks) as $chunks
| [ arr($meta.groundingSupports)[]
    | arr(.groundingChunkIndices)[]
    | select(type == "number" and . >= 0 and . < ($chunks | length)) ]
| unique
| [ .[] | $chunks[.].web.uri | select(type == "string" and length > 0) ]
| unique
| join(", ")
