# Canonical source-URL extraction — OpenAI Responses API.
# CONTRACT: a VERIFIED verdict must carry at least one source the model actually cited. Sources
# come ONLY from `url_citation` annotations the model attached to its output_text — never
# fabricated. If this returns empty, the caller's SOURCES line is blank and step 5 downgrades a
# VERIFIED with no source to NOT_SEARCHED. Used with `jq -r`.
[.output[]? | select(.type=="message") | .content[]? | select(.type=="output_text")
  | .annotations[]? | select(.type=="url_citation") | .url] | unique | join(", ")
