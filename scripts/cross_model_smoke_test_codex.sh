#!/bin/bash
# Manual LIVE smoke test. CI must never invoke this file.
# Uses public citation metadata only and the exact production detect/verify paths.
set -u

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd) || exit 1
RUNTIME="$SCRIPT_DIR/cross_model_codex_transport.py"

detect_output=$(python3 "$RUNTIME" detect) || {
  status=$?
  printf '%s\n' "$detect_output"
  exit "$status"
}
printf '%s\n' "$detect_output"

request='{"schema_version":"ars-codex-citation-request/1.0","request_id":"smoke-vaswani-2017","reference_text":"Vaswani, A., Shazeer, N., Parmar, N., Uszkoreit, J., Jones, L., Gomez, A. N., Kaiser, L., and Polosukhin, I. (2017). Attention Is All You Need. Advances in Neural Information Processing Systems 30.","citation_context":"Cited as the source introducing the Transformer architecture."}'

receipt=$(printf '%s' "$request" | "$SCRIPT_DIR/cross_model_codex_verify.sh") || {
  status=$?
  printf 'RESULT: FAIL (transport exit %s)\n' "$status"
  exit "$status"
}
printf '%s\n' "$receipt"

verdict=$(printf '%s' "$receipt" | python3 -c 'import json,sys; print(json.load(sys.stdin)["verdict"])') || exit 1
searched=$(printf '%s' "$receipt" | python3 -c 'import json,sys; print(str(json.load(sys.stdin)["searched"]).lower())') || exit 1
sources=$(printf '%s' "$receipt" | python3 -c 'import json,sys; print(len(json.load(sys.stdin)["sources"]))') || exit 1

if [ "$verdict" = "VERIFIED" ] && [ "$searched" = "true" ] && [ "$sources" -ge 1 ]; then
  printf 'RESULT: PASS\n'
  exit 0
fi

printf 'RESULT: FAIL (verdict=%s searched=%s sources=%s)\n' "$verdict" "$searched" "$sources"
exit 1
