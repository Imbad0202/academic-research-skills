# Canonical grounding guard — OpenAI Responses API.
# CONTRACT (cross_model_verification.md, OpenAI block): accept the verdict text only when the
# response proves a hosted web search actually ran. A completed `web_search_call` item is that
# proof. Used with `jq -e`: exit 0 = a search ran (proceed to extract text+sources); exit non-0
# = no search happened → the caller emits NOT_SEARCHED and discards the verdict.
# This is the load-bearing fail-closed boundary: without a completed search the model answered
# from memory and its VERIFIED must never be trusted.
any(.output[]?; .type == "web_search_call" and .status == "completed")
