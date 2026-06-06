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
# (→ NOT_SEARCHED) rather than a fabricated or crashing result. Used with `jq -r`.
(.candidates[0].groundingMetadata.groundingChunks // []) as $chunks
| [ .candidates[0].groundingMetadata.groundingSupports[]?.groundingChunkIndices[]?
    | select(type == "number" and . >= 0 and . < ($chunks | length)) ]
| unique
| [ .[] | $chunks[.].web.uri // empty ]
| unique
| join(", ")
