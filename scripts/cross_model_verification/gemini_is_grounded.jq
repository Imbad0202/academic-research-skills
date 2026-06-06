# Canonical grounding guard — Gemini generateContent (google_search tool).
# CONTRACT (cross_model_verification.md, Gemini block): accept the verdict text only when BOTH
#   - webSearchQueries  (length > 0) — the model actually issued a search, AND
#   - groundingSupports (length > 0) — the verdict TEXT is tied to retrieved chunks.
# webSearchQueries + groundingChunks alone is NOT enough: Gemini can run a search, return chunks,
# then emit an unsupported from-memory verdict whose text references none of them.
# groundingSupports[].groundingChunkIndices is what links answer spans to sources; without it a
# VERIFIED is not actually grounded. Used with `jq -e`: exit 0 = grounded; non-0 = NOT_SEARCHED.
#
# GUARD DERIVES FROM THE EXTRACTOR — by construction, not by a re-implemented predicate. The guard
# embeds the EXACT extraction `gemini_sources.jq` performs (same `candidates[0]` selection, same
# valid-index predicate, same non-empty-string uri filter) and passes iff that extraction yields ≥1
# url AND the model actually issued a search (a non-empty webSearchQueries array on the SAME
# candidate). The safety invariant is **guard-pass ⟹ at least one source extractable**: deriving
# the guard from the extractor — rather than asserting two parallel jq programs agree — makes it
# hold for every input shape (a multi-candidate response where candidate 0 is unsupported, a
# fractional/negative/string/out-of-range index, a non-string uri, a malformed object container all
# leave the extraction empty → guard fails closed → an unsupported NOT_FOUND/MISMATCH, which the
# blank-source downgrade does not rescue since it only touches VERIFIED, is never trusted). The
# guard is strictly STRONGER than "has a source": a response carrying chunks but no webSearchQueries
# (sources non-blank, no real search signal) still fails — the converse is intentionally not
# required. Keep this extraction byte-identical to gemini_sources.jq's `$srcs` body. Used with
# `jq -e`: exit 0 = grounded; non-0 = NOT_SEARCHED.
def arr($x): if ($x | type) == "array" then $x else [] end;
(arr(.candidates)[0].groundingMetadata) as $meta
| arr($meta.groundingChunks) as $chunks
| ([ arr($meta.groundingSupports)[]
     | arr(.groundingChunkIndices)[]
     | select(type == "number" and . == floor and . >= 0 and . < ($chunks | length)) ]
   | unique
   | [ .[] | $chunks[.].web.uri | select(type == "string" and length > 0) ]) as $srcs
| ((arr($meta.webSearchQueries) | length) > 0) and (($srcs | length) > 0)
