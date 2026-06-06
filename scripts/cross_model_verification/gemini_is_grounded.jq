# Canonical grounding guard — Gemini generateContent (google_search tool).
# CONTRACT (cross_model_verification.md, Gemini block): accept the verdict text only when BOTH
#   - webSearchQueries  (length > 0) — the model actually issued a search, AND
#   - groundingSupports (length > 0) — the verdict TEXT is tied to retrieved chunks.
# webSearchQueries + groundingChunks alone is NOT enough: Gemini can run a search, return chunks,
# then emit an unsupported from-memory verdict whose text references none of them.
# groundingSupports[].groundingChunkIndices is what links answer spans to sources; without it a
# VERIFIED is not actually grounded. Used with `jq -e`: exit 0 = grounded; non-0 = NOT_SEARCHED.
#
# FAIL-CLOSED on malformed types AND on supports that link to nothing: it is not enough for
# webSearchQueries / groundingSupports to be non-empty arrays — a `groundingSupports: [{}]`,
# `[{groundingChunkIndices: []}]`, or one whose only indices are negative / string / out-of-range
# carries NO actual link to a retrieved chunk, so the verdict text is not grounded. The guard
# therefore requires (a) a non-empty webSearchQueries array AND (b) at least one VALID supported
# chunk index — the SAME in-range non-negative-integer predicate gemini_sources.jq uses — so
# guard-pass ⟺ at least one source is extractable. (Without (b) an unsupported NOT_FOUND/MISMATCH
# verdict, which the blank-source downgrade does not touch, would be trusted as grounded.)
# Every container is array-normalized (`arr`) so a malformed object container fails closed.
def arr($x): if ($x | type) == "array" then $x else [] end;
def nonempty_array($x): ($x | type) == "array" and ($x | length) > 0;
any(arr(.candidates)[];
  .groundingMetadata as $meta
  | (arr($meta.groundingChunks) | length) as $n
  | nonempty_array($meta.webSearchQueries)
  and (any(arr($meta.groundingSupports)[] | arr(.groundingChunkIndices)[];
           type == "number" and . >= 0 and . < $n)))
