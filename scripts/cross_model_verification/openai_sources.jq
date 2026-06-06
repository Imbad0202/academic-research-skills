# Canonical source-URL extraction — OpenAI Responses API.
# CONTRACT: a VERIFIED verdict must carry at least one source the model actually cited. Sources
# come ONLY from `url_citation` annotations the model attached to its output_text — never
# fabricated. If this returns empty, the caller's SOURCES line is blank and step 5 downgrades a
# VERIFIED with no source to NOT_SEARCHED. Used with `jq -r`.
#
# FAIL-CLOSED on a malformed `url`: filter to non-empty strings so a `url_citation` whose `url` is
# a bool/number/object never fabricates a SOURCES entry (defeating the downgrade) or crashes
# `join` (an object `url` is not addable to a string). `output` is array-normalized first so a
# malformed `output` arriving as an object is not iterated over its values (which could surface a
# url nested in an object) — a non-array `output` yields no sources.
def arr($x): if ($x | type) == "array" then $x else [] end;
[arr(.output)[] | select(.type=="message") | .content[]? | select(.type=="output_text")
  | .annotations[]? | select(.type=="url_citation") | .url
  | select(type == "string" and length > 0)] | unique | join(", ")
