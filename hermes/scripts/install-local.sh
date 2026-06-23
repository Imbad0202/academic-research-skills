#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"

if [[ -n "${HERMES_SKILLS_DIR:-}" ]]; then
  target="$HERMES_SKILLS_DIR"
elif [[ -d "$HOME/AppData/Local/hermes" ]]; then
  target="$HOME/AppData/Local/hermes/skills/research"
else
  target="$HOME/.hermes/skills/research"
fi

mkdir -p "$target"

if [[ $# -eq 0 ]]; then
  echo "Usage: $0 all|deep-research|paper|reviewer|pipeline|<skill-name> [...]" >&2
  exit 2
fi

install_one() {
  local name="$1"
  local src="$repo_root/hermes/skills/$name"
  if [[ ! -f "$src/SKILL.md" ]]; then
    echo "Missing skill: $name" >&2
    exit 1
  fi
  rm -rf "$target/$name"
  mkdir -p "$target/$name"
  cp -R "$src"/. "$target/$name/"
  echo "Installed $name -> $target/$name"
}

for arg in "$@"; do
  case "$arg" in
    all)
      install_one hermes-academic-deep-research
      install_one hermes-academic-paper
      install_one hermes-academic-reviewer
      install_one hermes-academic-pipeline
      ;;
    deep-research) install_one hermes-academic-deep-research ;;
    paper) install_one hermes-academic-paper ;;
    reviewer) install_one hermes-academic-reviewer ;;
    pipeline) install_one hermes-academic-pipeline ;;
    *) install_one "$arg" ;;
  esac
done

echo "Done. Start a fresh Hermes session or run /reload-skills."
