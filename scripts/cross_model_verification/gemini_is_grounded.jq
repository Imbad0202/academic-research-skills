# Canonical grounding guard — Gemini generateContent (google_search tool).
# CONTRACT (cross_model_verification.md, Gemini block): accept the verdict text only when BOTH
#   - webSearchQueries  (a non-empty array; its elements are not checked) — the response reports a
#     search, AND
#   - at least one groundingSupports entry whose chunk index leads to a retrieved chunk with a
#     non-empty string uri (the extraction rule below; a non-empty array alone is not enough).
# webSearchQueries + groundingChunks alone is NOT enough: Gemini can run a search, return chunks,
# then emit an unsupported from-memory verdict whose text references none of them.
# groundingSupports[].groundingChunkIndices is what links answer spans to sources; without such a
# link the guard cannot verify that a VERIFIED rests on a source. Used with `jq -e`: exit 0 = both
# conditions hold; non-0 = NOT_SEARCHED.
#
# GUARD DERIVES FROM THE EXTRACTOR — by construction, not by a re-implemented predicate. The guard
# embeds the EXACT extraction `gemini_sources.jq` performs (same `candidates[0]` selection, same
# valid-index predicate, same non-empty-string uri filter) and passes iff that extraction yields ≥1
# non-empty string uri (not trimmed or parsed, so a whitespace-only uri counts) AND the response
# reports a search (a non-empty webSearchQueries array on the SAME candidate; its elements are not
# checked, so `[null]` counts). The safety invariant is **guard-pass ⟹ at least one source extractable**: deriving
# the guard from the extractor — rather than asserting two parallel jq programs agree — makes it
# hold for every input shape. Only `candidates[0]` is read, so a source on another candidate never
# counts. A non-object `candidates[0]` or `groundingMetadata`, or a non-array `candidates`,
# `groundingSupports` or `groundingChunks`, empties the whole extraction. Each chunk index is
# checked on its own: a fractional/negative/string/out-of-range index, a cited `groundingChunks`
# element or `web` that is NOT AN OBJECT, or a uri that is not a non-empty string drops only that
# index; a non-object `groundingSupports` element or a non-array `groundingChunkIndices` drops only
# that support. The source condition fails only when no index yields a source. So a
# NOT_FOUND/MISMATCH with no source link at all is never trusted (the
# blank-source downgrade only touches VERIFIED, so it does not rescue one). The
# guard is strictly STRONGER than "has a source": a response carrying chunks but no webSearchQueries
# (sources non-blank, no real search signal) still fails — the converse is intentionally not
# required. Keep this extraction's LOGIC identical to gemini_sources.jq's `$srcs` body — same
# candidate-0 selection, same valid-index predicate, same `obj(obj(chunk).web).uri` non-empty-string
# filter, same order. (The two differ only in how the result is consumed: here it is bound to `$srcs`
# inside a `([ … ]) as $srcs` wrap; there it is piped to `unique | join`, so leading whitespace is
# not byte-for-byte equal — only the extraction operations must stay in lockstep.) Used with
# `jq -e`: exit 0 = grounded; non-0 = NOT_SEARCHED.
#
# `arr/1` array-normalizes every container; `obj/1` object-normalizes every value that is then
# field-dereferenced (`obj(candidates[0]).groundingMetadata`, `obj($meta)`, `obj(support).…Indices`,
# `obj(obj(chunk).web).uri`). Without `obj/1`, a non-object at any of those points (e.g.
# `groundingMetadata: 5`, a `web: 5`) can make jq fail ("Cannot index number with string …") instead
# of failing closed (a `null` does not, since `null | .uri` is `null`) — a crash is loud but still
# violates the crash-free fail-closed contract.
def arr($x): if ($x | type) == "array" then $x else [] end;
def obj($x): if ($x | type) == "object" then $x else {} end;
(obj(arr(obj(.).candidates)[0]).groundingMetadata | obj(.)) as $meta
| arr($meta.groundingChunks) as $chunks
| ([ arr($meta.groundingSupports)[]
     | arr(obj(.).groundingChunkIndices)[]
     | select(type == "number" and . == floor and . >= 0 and . < ($chunks | length)) ]
   | unique
   | [ .[] | obj(obj($chunks[.]).web).uri | select(type == "string" and length > 0) ]) as $srcs
| ((arr($meta.webSearchQueries) | length) > 0) and (($srcs | length) > 0)
