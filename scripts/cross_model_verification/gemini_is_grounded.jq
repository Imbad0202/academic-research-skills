# Canonical grounding guard — Gemini generateContent (google_search tool).
# CONTRACT (cross_model_verification.md, Gemini block): accept the verdict text only when BOTH
#   - webSearchQueries  (length > 0) — the model actually issued a search, AND
#   - groundingSupports (length > 0) — the verdict TEXT is tied to retrieved chunks.
# webSearchQueries + groundingChunks alone is NOT enough: Gemini can run a search, return chunks,
# then emit an unsupported from-memory verdict whose text references none of them.
# groundingSupports[].groundingChunkIndices is what links answer spans to sources; without it a
# VERIFIED is not actually grounded. Used with `jq -e`: exit 0 = grounded; non-0 = NOT_SEARCHED.
#
# FAIL-CLOSED on malformed types: `length` is truthy for non-empty strings/objects too, so a
# malformed groundingMetadata (webSearchQueries or groundingSupports arriving as a string/object
# instead of an array) must NOT pass the guard. Require each field to be a non-empty ARRAY. The
# top-level `candidates` is array-normalized first (`arr`) so a malformed `candidates` arriving as
# an object — whose values `.candidates[]?` would otherwise still iterate — yields no candidate to
# match (guard → false), staying consistent with gemini_sources.jq's `.candidates[0]` access.
def arr($x): if ($x | type) == "array" then $x else [] end;
def nonempty_array($x): ($x | type) == "array" and ($x | length) > 0;
any(arr(.candidates)[];
  nonempty_array(.groundingMetadata.webSearchQueries // [])
  and nonempty_array(.groundingMetadata.groundingSupports // []))
