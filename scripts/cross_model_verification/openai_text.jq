# Canonical verdict-text extraction — OpenAI Responses API.
# Joins all output_text segments of the message into the verdict text. Not a safety boundary by
# itself (the search guard + the sources filter are); extracted here so the doc and the test
# share one definition. `output` is array-normalized for consistency with the guard/sources
# filters (a non-array `output` yields empty text). Used with `jq -r`.
def arr($x): if ($x | type) == "array" then $x else [] end;
[arr(.output)[] | select(.type=="message") | .content[]? | select(.type=="output_text") | .text] | join("\n")
