# ARS routing core

This file is the single source of the cross-skill routing core: the rules that decide, before any agent is dispatched, whether a request is routed directly or the user is asked which workflow they want. Issue #133 is the failure it prevents, #889 calibrated its wording, and #892 made it reach every install path.

A Claude Code session loads the repository's `.claude/CLAUDE.md` only when its working directory is inside the ARS checkout, and Claude Code does not load a plugin's `CLAUDE.md` as project context. So the block between the markers below reaches a session through three carriers:

- `.claude/CLAUDE.md` § Routing Discipline (v3.9.2), for sessions started inside a clone of this repository;
- `scripts/announce-ars-loaded.sh`, which reads the block from this file at every SessionStart (startup, clear, resume, compaction, fork), so plugin installs have it before any skill loads; after compaction, resume, or a fork its lead-in limits the block to a new request;
- the `SKILL.md` of every skill (four today), so every install path has it once a skill loads.

`scripts/check_routing_core_sync.py` fails CI when a copy differs from this block by a single byte or a skill's `SKILL.md` lacks it. Change the rules here and copy the block to the carriers in the same commit. The message template, the phase table, and worked examples are in `shared/references/intent_clarification_protocol.md`.

<!-- routing-core:begin -->
**Step 0 — Escape hatch check (before any classification):** If the user's first message begins with `[direct-mode]` (case-insensitive byte-0 token, optionally preceded by whitespace/newlines that are stripped on parse), record this fact, strip the prefix and surrounding whitespace from the message, and skip directly to **Step 1 explicit-intent handling** on the stripped content. The literal `[direct-mode]` is NOT passed through to the dispatched agent. If the stripped message itself has no clear skill named, Step 1 falls through to Step 3 clarification (the escape hatch bypasses cross-phase clarification (Step 2), not all routing). When the token is honored and the named agent or skill needs inputs the message does not supply, read that agent's or skill's file and ask for what it requires, in its terms. Without the byte-0 token, naming an agent is not explicit intent: such a message goes through Steps 1-3 like any other, so cross-phase materials still get Step 2 clarification.

Otherwise, classify the user's input:

1. **Explicit clear intent** — user invokes a specific skill via `/ars-*` slash command, or uses an unambiguous trigger keyword that maps to a single skill (e.g., "lit-review this", "review my paper", "draft an abstract"):
   → Route directly; no clarification, no orchestrator detour.
   → The request stays explicit when the mode's usual input is absent or a word in it has other everyday senses. A revision request with no reviewer comments is revision mode's "feel certain sections need improvement" case, and "revisar artículo" is the reviewer's trigger. Route to that mode and let the mode handle what is missing; do not reopen the choice of workflow.

2. **Cross-phase materials detected** — user provides artifacts spanning ≥ 2 pipeline phases without naming a specific skill (e.g., pre-written abstract + pre-collected literature; full draft + reviewer comments + bibliography):
   → **Clarify**. Do NOT auto-route to a single-phase agent. List candidate workflows as a-d options in markdown body (NOT via AskUserQuestion tool). See `shared/references/intent_clarification_protocol.md` for the message template.
   → Reason: clarification is the safest action when materials don't unambiguously identify intent. (v3.10 active conductor (#134) will handle this via structured intake; v3.9.2 asks.)

3. **Ambiguous intent, no materials** — user provides no artifacts and no clear request:
   → Clarify per `shared/references/intent_clarification_protocol.md`.

**Anti-pattern (caused #133):** Receiving ambiguous cross-phase materials and silently auto-routing to a single-phase agent based on which phase the materials "look closest to." This bypasses orchestrator-level reconciliation and lets the subagent inherit the full ambiguity without independent oversight.
<!-- routing-core:end -->
