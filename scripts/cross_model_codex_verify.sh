#!/bin/bash
# Bash 3.2-compatible entry point for the #630 citation-only transport.
set -u

SCRIPT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd) || exit 1
exec python3 "$SCRIPT_DIR/cross_model_codex_transport.py" verify
