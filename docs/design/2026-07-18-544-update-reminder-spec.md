# #544 — SessionStart update-available reminder for plugin installs

**Status:** spec for the feature branch `feat/544-update-reminder`
**Affects:** `scripts/announce-ars-loaded.sh` (SessionStart announce), new `scripts/ars_update_check.sh`, new `scripts/test_ars_update_check.py`, `docs/SETUP.md` (+ zh-TW twin), CHANGELOG.
**Eval impact:** none (no scoring / generation / gold-set change).

## Problem

Issue #543's reporter hit a bug on suite v3.11.1 that had been fixed since v3.12.2 /
v3.13.0 (#449 / #459) — six minor versions behind at report time. This is a recurring
class, not a one-off, because of two platform facts (first-party verified against
code.claude.com docs, 2026-07-18):

1. Third-party marketplaces have auto-update **disabled by default**. Only a manual
   `/plugin update` or an explicit per-marketplace auto-update toggle pulls new
   versions. Official Anthropic marketplaces default ON; ours defaults OFF.
2. Update detection compares the `version` string in `.claude-plugin/plugin.json`.
   A user who is behind sees no signal anywhere that they are behind.

ARS releases roughly every 1–2 weeks (`docs/SETUP.md` already says so and "strongly
recommends" enabling auto-update — advice an installed-and-forgotten user never
re-reads). A user who installed once and never toggled auto-update silently
accumulates months of drift, then reports already-fixed bugs.

## Scope decision (settled with maintainer, 2026-07-18)

**Plugin installs only.** The reminder rides the existing SessionStart announce hook,
which only exists under a plugin install (`hooks/hooks.json` + `CLAUDE_PLUGIN_ROOT`).
Clone/symlink installs (SETUP Methods 1–3) are out of scope by design: those users
update via `git pull`, chose a manual layout deliberately, and run no plugin hooks. A
gstack-style per-SKILL.md preamble check (which would cover every install layout) was
considered and rejected: it touches all four SKILL.md files, needs per-layout wording,
and doubles the maintenance surface for the population least likely to be stuck.

## Design

### New script: `scripts/ars_update_check.sh`

A self-contained version checker. Called by the announce script; also runnable
standalone. Same portability discipline as `announce-ars-loaded.sh`: Bash 3.2
compatible, no jq, no Bash 4+ features.

**Output contract (stdout, single line or nothing):**

| Output | Meaning |
|---|---|
| `UPDATE_AVAILABLE <installed> <latest>` | remote version differs from installed |
| *(nothing)* | up to date, disabled, not a plugin install, or any failure |

Exit code is always 0. The checker never prints to stderr on the happy path and the
caller discards stderr regardless.

**Steps:**

1. **Kill switch.** `ARS_UPDATE_CHECK=0` → exit silently. Documented user-facing
   toggle. (Any other value, including unset, means enabled.)
2. **Plugin gate.** `CLAUDE_PLUGIN_ROOT` unset or `${CLAUDE_PLUGIN_ROOT}/.claude-plugin/plugin.json`
   unreadable → exit silently. This is the mechanism that scopes the feature to
   plugin installs.
3. **Local version.** First `"version": "<value>"` match in the local `plugin.json`,
   extracted with the same `[[ =~ ]]` regex style the announce script uses for
   `source`. Parse miss → exit silently.
4. **Cache consult.** Cache file `${ARS_UPDATE_CHECK_STATE_DIR:-$HOME/.cache/ars}/update-check`,
   format `<STATE> <installed-at-check> <latest>` (STATE ∈ `UP_TO_DATE` /
   `UPDATE_AVAILABLE`). If the file exists, is well-formed, its mtime is younger than
   24 h, **and** its `<installed-at-check>` equals the current local version: render
   from cache (emit the token for `UPDATE_AVAILABLE`, emit nothing for `UP_TO_DATE`)
   and exit — no network. A recorded local version that differs from the current one
   means the user updated since the check; fall through to refetch. Malformed cache →
   fall through to refetch.
5. **Remote fetch.** `curl -fsSL --max-time 3` on
   `${ARS_UPDATE_CHECK_REMOTE_URL:-https://raw.githubusercontent.com/Imbad0202/academic-research-skills/main/.claude-plugin/plugin.json}`,
   parse `version` with the same regex. curl missing, fetch failure, or parse miss →
   exit silently **without touching the cache** (a stale good cache beats a poisoned
   one; the next session retries).
6. **Compare + write cache.** Plain string inequality (no semver ordering — the only
   question is "does `/plugin update` deliver something different"). Write the cache
   line atomically (temp file + `mv`), then emit the token if versions differ.

Remote choice rationale: `main`'s `plugin.json` is exactly what `/plugin update`
delivers (the marketplace tracks the repo; the version string is the update key —
see #459's release-gap postmortem), so comparing against `main` matches the
platform's own update semantics. Release tags would drift from what an update
actually installs during the merge→tag window.

**Env overrides** (testing + user control):

| Variable | Default | Role |
|---|---|---|
| `ARS_UPDATE_CHECK` | unset (enabled) | `0` disables everything |
| `ARS_UPDATE_CHECK_STATE_DIR` | `~/.cache/ars` | cache directory (tests point it at a tmpdir) |
| `ARS_UPDATE_CHECK_REMOTE_URL` | raw `main` plugin.json | remote source (tests use `file://` fixtures) |

Local version needs no override: tests set `CLAUDE_PLUGIN_ROOT` to a fixture
directory.

### Announce integration: `scripts/announce-ars-loaded.sh`

Only the `startup|clear` branch changes (compact/resume stays minimal — no network,
no reminder mid-session). The checker is invoked **inside the `startup|clear` case
arm** — not before the `case` — so `compact`/`resume` never runs it, keeping the
no-network promise for those paths structural rather than incidental:

```bash
UPDATE_LINE=""
if [[ -n "${CLAUDE_PLUGIN_ROOT:-}" ]]; then
  _UPD=$(bash "${CLAUDE_PLUGIN_ROOT}/scripts/ars_update_check.sh" 2>/dev/null || true)
  if [[ "${_UPD}" =~ ^UPDATE_AVAILABLE[[:space:]]([^[:space:]]+)[[:space:]]([^[:space:]]+)$ ]]; then
    UPDATE_LINE="ARS update available: v${BASH_REMATCH[2]} (installed: v${BASH_REMATCH[1]}). Run /plugin update academic-research-skills, or enable auto-update in /plugin -> Marketplaces.

"
  fi
fi
```

and the `startup|clear` case prepends `${UPDATE_LINE}` to the existing `ANNOUNCE`
text. The reminder is one line of `additionalContext`; Claude relays it to the user
at session start. It re-renders every new session until the user updates — no
snooze/backoff ladder (that machinery exists in gstack for interactive upgrade
prompts; one context line does not warrant it; revisit only on user noise reports).

The `|| true` + regex-gate means any checker misbehavior degrades to "no reminder",
never a broken announce. The checker's token-only output contract keeps all
human-facing wording in the announce script (single wording surface, and the ASCII
`->` keeps the JSON-escaping path trivial).

### Error handling summary

| Failure | Behavior |
|---|---|
| `ARS_UPDATE_CHECK=0` | fully off — no network, no output |
| not a plugin install | silent skip |
| offline / timeout / GitHub down | silent skip, cache untouched, retry next session after TTL |
| curl absent (unusual even on Windows Git Bash) | silent skip |
| local or remote version parse miss | silent skip |
| corrupt cache | ignored, refetched |
| checker crashes entirely | announce unaffected (`|| true`) |

Privacy: the check fetches one public file from this repository over HTTPS and
transmits no user data beyond that HTTP request. Stated in SETUP.md next to the
kill switch.

### Tests: `scripts/test_ars_update_check.py`

Pytest, subprocess-driving the bash script — hermetic, no network: remote is a
`file://` URL to fixture `plugin.json` files in a tmpdir, state dir is a tmpdir,
`CLAUDE_PLUGIN_ROOT` is a fixture directory. TTL cases manipulate cache mtime via
`os.utime`. Cases:

1. `ARS_UPDATE_CHECK=0` → no output, no cache write, no fetch.
2. `CLAUDE_PLUGIN_ROOT` unset → no output.
3. local == remote → no output; cache written `UP_TO_DATE`.
4. local != remote → `UPDATE_AVAILABLE <local> <remote>`; cache written.
5. Fresh `UPDATE_AVAILABLE` cache → token emitted with **no** fetch (proved by
   pointing the remote URL at a fixture with a third version and asserting the
   cached value is what renders).
6. Fresh `UP_TO_DATE` cache → silent, no fetch (remote points at a newer fixture;
   still silent until TTL expiry).
7. Expired cache (mtime > 24 h) → refetch, output and cache reflect the new remote.
8. Expired cache + remote unreachable (`file://` to a nonexistent path) → silent;
   the stale cache file is left in place untouched (next session retries the fetch).
9. Malformed remote JSON → silent, cache untouched.
10. Corrupt cache → refetch succeeds, cache rewritten.
11. User updated (current local == cached `<latest>`, cache fresh) → cache local
    mismatch forces refetch → now `UP_TO_DATE`, silent.
12. Announce integration, behind: run `announce-ars-loaded.sh` with
    `{"source":"startup"}` on stdin and checker env pointing at fixtures → emitted
    `additionalContext` starts with the reminder line.
13. Announce integration, current: same but versions equal → announce byte-identical
    to pre-change output.
14. Announce integration, checker absent/broken: `CLAUDE_PLUGIN_ROOT` fixture without
    the checker script → announce byte-identical to pre-change output.

The test file joins the local pytest manifest in the same commit (local/CI parity
discipline per #492).

### Docs

- `docs/SETUP.md` Method 0: after the auto-update recommendation, add that from the
  release shipping #544 onward the plugin announces at session start when a newer
  version exists, the `ARS_UPDATE_CHECK=0` kill switch, and the privacy note (exact
  version number is filled in at release time, not hardcoded ahead of the tag). Mirror the sentence in
  `docs/SETUP.zh-TW.md` (en/zh parity: no H2 change, prose only).
- `CHANGELOG.md` `[Unreleased]` entry citing #543 → #544.

### Explicitly out of scope

- Clone/symlink install coverage (see Scope decision).
- Snooze/backoff ladder, "just upgraded" banner, interactive upgrade prompt.
- Semver ordering (string inequality is the correct question here).
- Auto-running the update (Claude cannot invoke `/plugin update`; the platform owns it).
- Adding the checker to `INFRA_PROTECTED_GLOBS` — it is advisory announce plumbing,
  not load-bearing enforcement; protecting it would repeat the #459 category error.

## Invariants

1. With `ARS_UPDATE_CHECK=0`, or outside a plugin install, or on any failure path,
   the announce output is byte-identical to pre-#544 behavior.
2. The checker performs at most one network request per session start with a 3 s
   ceiling — and in steady state (no local version change, healthy cache) at most
   one per 24 h per machine. It never blocks or breaks session start.
3. All human-facing reminder wording lives in `announce-ars-loaded.sh`; the checker
   emits only the machine token.
4. The check transmits no user data; the only network access is an HTTPS GET of one
   public repo file.
