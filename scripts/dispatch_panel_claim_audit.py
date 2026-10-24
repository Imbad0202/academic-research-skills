#!/usr/bin/env python3
"""Dispatch and score the panel-claim factuality audit (#1002).

The suite lives in ``evals/heldout/panel_claim_factuality/``; its README gives
the order of the steps and ``plan.json`` holds the frozen numbers. Subcommands:

  generate      ask the generator model for contrast pairs on one manuscript
  check-pairs   mechanical checks on the generated pairs (no model): one
                sentence each, 8-50 whitespace-delimited words, one to four
                changed tokens, and a verbatim evidence quote
  verify-pairs  ask the verifier model the eight pair questions, one call per
                manuscript
  build         read the pairs back from the logged generator and verifier
                outputs, check them and the claim inventory against plan.json,
                then write the batches, the item key, snapshots of every input,
                and a build manifest into a new directory; the two sentences of
                a pair never share a batch
  run           send each batch to one judge for one replicate; stop at the
                first transport failure or unreadable output after one retry
  score         check coverage, apply the contrast gate, sort every claim into
                one agreement list, write the adjudication packet and the
                execution manifest, and, once the maintainer's decisions file
                is complete, the headline counts

Every model call runs in a new empty directory, with the prompt on stdin
(codex, and the Gemini API helper ``gemini-api-call``) or in ``-p`` (agy). The
generator, verifier, and judge transports are the ones ``plan.json`` names. The
CLIs print their event stream (codex ``--json``, agy ``--output-format
stream-json``, with slash commands and skills off) and the helper prints the API
response body; the script decides from those fields, never from searching the
text: a call fails on a nonzero exit, a failed turn or error event, a missing
completed turn or a finish reason other than STOP, an empty reply, or any step
other than the reply (a command, a file read, a tool, a skill, a subagent, a
function call). A call first reserves its
output name with an exclusive lock file and logs a ``started`` line; it then
writes its output once and logs ``completed`` or ``failed``. An output is used,
by a later call or by scoring, only when a completed log line has the same
call id, transport, prompt hash, and output hash; a lock without an output is
an interrupted call and stops the run.

No path under ``reviewer_seeded_defects/manifests/`` is read: every input path
is resolved and refused when it lies there.
"""
from __future__ import annotations

import argparse
import difflib
import hashlib
import json
import os
import re
import signal
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

REPO_ROOT = Path(__file__).resolve().parent.parent
SUITE = REPO_ROOT / "evals" / "heldout" / "panel_claim_factuality"
SEEDED = REPO_ROOT / "evals" / "heldout" / "reviewer_seeded_defects"
MANUSCRIPTS = SEEDED / "manuscripts"
PROTECTED = (SEEDED / "manifests").resolve()
FIXTURE_FILES = {
    "ms00_clean": "ms00_clean_control.md",
    "ms01_quant": "ms01_quant_defective.md",
    "ms02_qual": "ms02_qual_defective.md",
}
VERDICTS = ("true", "false", "not_verifiable")
SEVERITIES = ("cosmetic", "minor", "major", "fundamental")
EVIDENCE = ("contradiction", "absent_quotation")
CRITERIA = ("V1", "V2", "V3", "R1", "R2", "R3", "R4", "R5")
PAIR_QUESTIONS = ("accurate_supported", "false_contradicted", "false_unsupported", "same_topic",
                  "plain_description", "no_tell", "evidence_quote_verbatim", "single_sentences")
# agy takes the prompt as an argument and fails silently above about 30 KB.
# Every prompt sent, a retry included, stays at or under PROMPT_LIMIT; a first
# attempt stays at or under PROMPT_BUDGET, which leaves room for the retry note.
PROMPT_LIMIT = 28_000
PROMPT_BUDGET = 27_500
TIMEOUT_S = 1500
RETRY_NOTE = ("\n\nYour previous answer could not be read: {reason}. Answer again, in the "
              "format given above, with nothing else.\n")
# agy flags: no slash commands or skills, and a stream that shows every step.
AGY_FLAGS = ("--disable-slash-commands", "--output-format", "stream-json")
# The steps (agy) and items (codex) a plain reply has; any other one stops the run.
AGY_ANSWER_STEPS = frozenset({"user_input", "agent_response", "unknown"})
CODEX_ANSWER_ITEMS = frozenset({"agent_message", "reasoning"})
# Gemini API judge (plan v4): no tools, no system instruction, medium thinking
# (plan v7), and 32,768 output tokens, which count thinking: the most one
# non-streaming request returns, so a cut-off reply ends with MAX_TOKENS. The key comes from
# the environment and goes only into the request header.
GEMINI_API_MODEL = "gemini-4-argon"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
GEMINI_API_KEY_ENV = "GEMINI_API_KEY"
GEMINI_API_CONFIG = {"thinkingConfig": {"thinkingLevel": "medium"}, "maxOutputTokens": 32768}
# The part fields a plain reply has; any other one (a function call, code) stops the run.
GEMINI_ANSWER_PART_KEYS = frozenset({"text", "thought", "thoughtSignature"})
# USD per token, in and out (thinking counts as out), from Google's pricing page;
# the rates hold through GEMINI_PRICE_UNTIL and double after it.
GEMINI_PRICE_IN, GEMINI_PRICE_OUT = 2.0e-6, 10.0e-6
GEMINI_PRICE_UNTIL = "2026-11-30"
# The plan's ceiling on any Gemini cap (PREREGISTRATION, Stop rules).
GEMINI_CAP_MAX_USD = 100.0
# Above the model's input plus output limits; a larger count is unreadable usage.
USAGE_MAX_TOKENS = 10_000_000
# Plan v5: a Gemini call that ends with finish reason MAX_TOKENS (its whole
# output limit spent, thinking included, with or without partial text) is sent
# once more, unchanged, under the call id + "-r". Plan v8 adds
# MALFORMED_RESPONSE, a provider-side generation failure. Safety and other
# finish reasons still stop the run.
MAX_TOKENS_FAILURE = "finish reason MAX_TOKENS"
RESEND_REASONS = frozenset({"MAX_TOKENS", "MALFORMED_RESPONSE"})
RESEND_FAILURES = frozenset(f"finish reason {r}" for r in RESEND_REASONS)
# The label a call log records per transport. The Gemini API judge gets its own
# label, so a logged call of the earlier agy "gemini" transport is never reused.
LOG_LABELS = {"gemini": "gemini_api"}
# Plan v10 (#1002 part two): the two Claude session models judge the contrast
# batches only, to test the runtime claim check's judge. Each call is a fenced
# headless `claude -p`: no tools, no MCP, an empty config directory, an
# allowlisted environment, a working directory that `_claude_workdir_base`
# checks, and the operator's OAuth token from CLAUDE_TOKEN_FILE, which goes
# only into that environment. `--bare` is left out: it accepts only an API key.
CLAUDE_JUDGES = {"claude_opus": "claude-opus-5-5", "claude_fable": "claude-fable-5-1"}
CLAUDE_TOKEN_FILE = Path.home() / ".config" / "ars-889" / "oauth_token"
CLAUDE_ENV_KEEP = ("PATH", "HOME", "LANG", "LC_ALL", "TMPDIR", "TERM", "USER", "SHELL",
                   "HTTP_PROXY", "HTTPS_PROXY", "NO_PROXY", "http_proxy", "https_proxy", "no_proxy",
                   "NODE_EXTRA_CA_CERTS", "SSL_CERT_FILE", "SSL_CERT_DIR")
CLAUDE_TOOL_DENY = ("Bash,Read,Write,Edit,Glob,Grep,WebFetch,WebSearch,"
                    "NotebookEdit,Task,Agent,Skill,TodoWrite,SlashCommand")
# Size ceilings: the Gemini helper reads at most RESPONSE_MAX_BYTES of a
# response body, and a transport stream above STREAM_MAX_CHARS is a failure
# that saves nothing.
RESPONSE_MAX_BYTES = 8 * 1024 * 1024
STREAM_MAX_CHARS = 64 * 1024 * 1024
# Batch ids are file-name stems the build writes (b001, b002, ...).
BATCH_ID_RE = re.compile(r"b\d{3,4}")
# An API error status or finish reason is echoed only in this form (e.g.
# RESOURCE_EXHAUSTED); a reply part key only in KEY_RE form.
API_STATUS_RE = re.compile(r"[A-Z][A-Z_]{0,63}")
KEY_RE = re.compile(r"[A-Za-z][A-Za-z0-9_]{0,63}")
# Reported usage is trusted only above these floors: at most this many bytes of
# prompt per input token and of reply per output token. Real v8 calls ran at
# 4.4-4.8 prompt bytes and at most 4.3 reply bytes per token.
USAGE_MAX_BYTES_PER_TOKEN = 16


class Stop(Exception):
    """A stop rule fired; the message says which."""


# ---------------------------------------------------------------------------
# Paths, hashes, files.
# ---------------------------------------------------------------------------


def _inside(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
        return True
    except ValueError:
        return False


def guard(path: Path) -> Path:
    """Refuse a path that resolves under, or contains, the held-out manifests."""
    resolved = path.resolve()
    if _inside(resolved, PROTECTED) or _inside(PROTECTED, resolved):
        raise Stop(f"refused: {path} overlaps the held-out manifests directory")
    return path


def read_text(path: Path) -> str:
    return guard(path).read_text(encoding="utf-8")


def read_jsonl(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in read_text(path).split("\n") if line.strip()]


def write_jsonl(path: Path, rows: list[dict[str, Any]]) -> None:
    _write_aux(path, "".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows))


def _write_aux(path: Path, data: str | bytes) -> None:
    """Write an output file (a call's side files, a build, a score) without
    following a symlink at its name, and never under the held-out manifests.
    Text is written as UTF-8; bytes are written unchanged."""
    if not hasattr(os, "O_NOFOLLOW") and os.path.islink(guard(path)):
        raise Stop(f"refused: {path.name} is a symlink")
    fd = os.open(guard(path), os.O_WRONLY | os.O_CREAT | os.O_TRUNC | getattr(os, "O_NOFOLLOW", 0), 0o644)
    with os.fdopen(fd, "wb") as handle:
        handle.write(data.encode("utf-8") if isinstance(data, str) else data)


def _printable(text: str) -> str:
    """``text`` with every non-printable character escaped, for the terminal."""
    return "".join(ch if ch.isprintable() else ch.encode("unicode_escape").decode("ascii") for ch in text)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def _file_sha(path: Path) -> str:
    return hashlib.sha256(guard(path).read_bytes()).hexdigest()


def load_plan() -> dict[str, Any]:
    return json.loads(read_text(SUITE / "plan.json"))


def manuscript_text(fixture: str) -> str:
    return read_text(MANUSCRIPTS / FIXTURE_FILES[fixture])


def _template(name: str) -> str:
    return read_text(SUITE / "prompts" / name)


def _norm(text: str) -> str:
    return " ".join(str(text).replace("“", '"').replace("”", '"')
                    .replace("‘", "'").replace("’", "'").replace('"', "").split()).casefold()


# ---------------------------------------------------------------------------
# Transports and calls.
# ---------------------------------------------------------------------------


def _codex_cmd(prompt: str) -> tuple[list[str], str | None]:
    return (["codex", "exec", "-m", "gpt-6-astra", "-c", 'model_reasoning_effort="xhigh"',
             "-c", "skills.include_instructions=false", "-s", "read-only",
             "--skip-git-repo-check", "--json", "-"], prompt)


def _agy_cmd(model: str) -> Callable[[str], tuple[list[str], str | None]]:
    def build(prompt: str) -> tuple[list[str], str | None]:
        return (["agy", f"--model={model}", *AGY_FLAGS, "-p", prompt, "--print-timeout", f"{TIMEOUT_S}s"],
                None)
    return build


def _gemini_api_cmd(prompt: str) -> tuple[list[str], str | None]:
    return ([sys.executable, "-I", str(Path(__file__).resolve()), "gemini-api-call"], prompt)


def _claude_cmd(model: str) -> Callable[[str], tuple[list[str], str | None]]:
    def build(prompt: str) -> tuple[list[str], str | None]:
        return (["claude", "-p", "--model", model, "--effort", "high", "--no-session-persistence",
                 "--strict-mcp-config", "--tools", "", "--disallowedTools", CLAUDE_TOOL_DENY,
                 "--output-format", "stream-json", "--verbose"], prompt)
    return build


def _claude_token() -> str:
    try:
        token = CLAUDE_TOKEN_FILE.read_text(encoding="utf-8").strip()
    except OSError:
        token = ""
    if not token:
        raise Stop(f"no Claude OAuth token in {CLAUDE_TOKEN_FILE}")
    return token


def _claude_workdir_base() -> Path:
    """The folder that holds a Claude judge's working directory. Claude Code
    reads CLAUDE.md and .claude/ settings from the working directory and every
    folder above it, so no such folder may hold them or a git checkout, and none
    may be under $HOME (plan v10)."""
    base = Path(tempfile.gettempdir()).resolve()
    if base.is_relative_to(Path.home().resolve()):
        raise Stop(f"the temporary folder {base} is under $HOME; set TMPDIR outside it")
    for folder in (base, *base.parents):
        found = [n for n in ("CLAUDE.md", "CLAUDE.local.md", ".claude", ".git") if (folder / n).exists()]
        if found:
            raise Stop(f"{folder} holds {', '.join(found)}; set TMPDIR to a folder with none above it")
    return base


def _claude_env(config_dir: str, token: str) -> dict[str, str]:
    """The allowlisted environment of one fenced `claude -p` call."""
    env = {k: v for k, v in os.environ.items() if k in CLAUDE_ENV_KEEP}
    env.update(CLAUDE_CONFIG_DIR=config_dir, CLAUDE_CODE_OAUTH_TOKEN=token)
    return env


TRANSPORTS: dict[str, Callable[[str], tuple[list[str], str | None]]] = {
    "codex": _codex_cmd,
    "gemini": _gemini_api_cmd,
    "claude_agy": _agy_cmd("Claude Opus 5.5 (High)"),
    **{judge: _claude_cmd(model) for judge, model in CLAUDE_JUDGES.items()},
}


def gemini_api_request(prompt: str) -> dict[str, Any]:
    return {"contents": [{"role": "user", "parts": [{"text": prompt}]}], "generationConfig": GEMINI_API_CONFIG}


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """A redirect becomes an HTTPError, so the key never goes to another URL."""

    def redirect_request(self, *args, **kwargs):
        return None


def cmd_gemini_api_call(_args, opener=None) -> int:
    """Send stdin as one prompt and print the response body of an HTTP 200.
    ``call_model`` runs this as a subprocess. On any other outcome nothing is
    printed or saved from the response and stderr gets fixed text only (the
    status code or the exception type), so no error body or exception message,
    which could echo the key, reaches a file."""
    key = os.environ.get(GEMINI_API_KEY_ENV, "")
    if not key:
        print(f"{GEMINI_API_KEY_ENV} is not set", file=sys.stderr)
        return 3
    if not (key.isascii() and key.isprintable()) or " " in key:
        print(f"{GEMINI_API_KEY_ENV} holds a character a request header cannot carry", file=sys.stderr)
        return 3
    if _now()[:10] > GEMINI_PRICE_UNTIL:
        print(f"the Gemini price table holds through {GEMINI_PRICE_UNTIL}; update it before a paid call",
              file=sys.stderr)
        return 3
    opener = opener or urllib.request.build_opener(_NoRedirect)
    try:
        prompt = sys.stdin.buffer.read().decode("utf-8")
        request = urllib.request.Request(
            GEMINI_API_URL.format(model=GEMINI_API_MODEL), method="POST",
            data=json.dumps(gemini_api_request(prompt), ensure_ascii=False).encode("utf-8"),
            headers={"x-goog-api-key": key, "Content-Type": "application/json"})
        with opener.open(request, timeout=TIMEOUT_S) as response:
            body, status = response.read(RESPONSE_MAX_BYTES + 1), response.status
        if len(body) > RESPONSE_MAX_BYTES:
            print(f"response over {RESPONSE_MAX_BYTES} bytes", file=sys.stderr)
            return 1
        if status == 200:
            api_error = _api_error(body)
            if api_error:
                print(api_error, file=sys.stderr)
                return 1
            sys.stdout.buffer.write(body)
            return 0
        print(f"HTTP {status}", file=sys.stderr)
    except urllib.error.HTTPError as exc:
        print(f"HTTP {exc.code}", file=sys.stderr)
    except Exception as exc:  # noqa: BLE001 - any failure is a transport failure
        print(f"request failed ({type(exc).__name__})", file=sys.stderr)
    return 1


def _api_error(body: bytes) -> str | None:
    """``API error <status>`` when an HTTP 200 body is an API error object,
    else None. The helper prints only this text, never the body."""
    try:
        parsed = json.loads(body)
    except ValueError:
        return None
    if not (isinstance(parsed, dict) and "error" in parsed):
        return None
    error = parsed["error"]
    status = error.get("status") if isinstance(error, dict) else None
    return "API error " + (status if isinstance(status, str) and API_STATUS_RE.fullmatch(status)
                           else "(unrecognized status)")


def gemini_usage(body_text: str, prompt_bytes: int, reply_bytes: int) -> dict[str, Any]:
    """Token counts and cost of one API response. Output is the total minus
    the prompt, so thinking and any other output count. ``usd`` is None (the
    run then counts the call at its worst case) unless both counts are
    integers with 0 <= prompt < total <= USAGE_MAX_TOKENS and neither count is
    below its floor (USAGE_MAX_BYTES_PER_TOKEN)."""
    try:
        meta = json.loads(body_text).get("usageMetadata")
    except (ValueError, AttributeError):
        meta = None
    if not isinstance(meta, dict):
        return {"usd": None}
    prompt, total = meta.get("promptTokenCount"), meta.get("totalTokenCount")
    if not all(isinstance(v, int) and not isinstance(v, bool) for v in (prompt, total)) \
            or not 0 <= prompt <= total <= USAGE_MAX_TOKENS:
        return {"usd": None}
    tokens_out = total - prompt
    if (tokens_out == 0 or prompt * USAGE_MAX_BYTES_PER_TOKEN < prompt_bytes
            or tokens_out * USAGE_MAX_BYTES_PER_TOKEN < reply_bytes):
        # A count too small for the text sent or received is not trusted.
        return {"usd": None}
    return {"tokens_in": prompt, "tokens_out": tokens_out,
            "usd": round(prompt * GEMINI_PRICE_IN + tokens_out * GEMINI_PRICE_OUT, 6)}


def _resend(call_id: str, out_file: Path) -> tuple[str, Path]:
    return f"{call_id}-r", out_file.with_name(out_file.name.replace(".out", ".r.out"))


def failed_resendable(calls_log: Path, call_id: str, prompt: str) -> bool:
    """The last logged attempt of ``call_id`` is a Gemini API call with this
    prompt that failed with a resendable finish reason (RESEND_REASONS); only
    then is a resend the same call."""
    entries = _logged(calls_log, call_id)
    return (bool(entries) and entries[-1].get("status") == "failed" and entries[-1].get("error") in RESEND_FAILURES
            and entries[-1].get("transport") == LOG_LABELS["gemini"]
            and entries[-1].get("prompt_sha256") == _sha(prompt))


def attempt_output(calls_log: Path, call_id: str, out_file: Path, prompt: str, transport: str) -> str | None:
    """``completed_output`` for one attempt, or for its resend when the Gemini
    attempt failed with a resendable finish reason (plans v5, v8)."""
    text = completed_output(calls_log, call_id, out_file, prompt, transport)
    if text is None and transport == "gemini" and failed_resendable(calls_log, call_id, prompt):
        text = completed_output(calls_log, *_resend(call_id, out_file), prompt, transport)
    return text


def worst_case_usd(prompt: str) -> float:
    """An upper bound on one call: a token per prompt byte, and the full output limit."""
    return len(prompt.encode("utf-8")) * GEMINI_PRICE_IN + GEMINI_API_CONFIG["maxOutputTokens"] * GEMINI_PRICE_OUT


def gemini_spent(out_root: Path) -> float:
    """Every Gemini call logged under ``out_root``: its cost, or its worst case
    when the call has no usage (an interrupted or failed call)."""
    total = 0.0
    for log in sorted((out_root / "gemini").glob("r*/calls.jsonl")):
        entries = read_jsonl(log)
        ends = {(e["call_id"], e["sequence_index"]) for e in entries if e.get("status") != "started"}
        for e in entries:
            if e.get("status") == "started" and (e["call_id"], e["sequence_index"]) not in ends:
                total += e.get("worst_case_usd") or 0.0
            elif e.get("status") == "completed" and e.get("usd") is not None:
                total += e["usd"]
            elif e.get("status") in ("completed", "failed"):
                # A failed call counts at its worst case whatever usage it logged.
                total += e.get("worst_case_usd") or 0.0
    return total


def _events(stream: str) -> tuple[list[dict[str, Any]], int]:
    """(events, unreadable lines). Lines split on LF only: JSON strings can hold
    U+2028 and other characters that ``str.splitlines`` breaks on."""
    events, unreadable = [], 0
    for line in stream.split("\n"):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except ValueError:
            unreadable += 1
            continue
        if isinstance(event, dict):
            events.append(event)
        else:
            unreadable += 1
    return events, unreadable


def agy_answer(stream: str) -> tuple[str, str | None]:
    """(reply text, problem) from agy stream-json output. A missing or failed
    result, or any step that is not part of a plain reply, is a problem."""
    steps: set[str] = set()
    result: dict[str, Any] | None = None
    events, unreadable = _events(stream)
    if unreadable:
        return "", f"{unreadable} unreadable event lines"
    for event in events:
        if event.get("event") == "step_update":
            steps.add(str((event.get("step_update") or {}).get("step_type")))
        elif event.get("event") == "result":
            result = event.get("result") or {}
    other = sorted(steps - AGY_ANSWER_STEPS)
    if other:
        return "", "steps other than the reply: " + ", ".join(other)
    if not result or result.get("status") != "SUCCESS" or not isinstance(result.get("response"), str):
        return "", "no successful result event"
    return result["response"], None


def claude_answer(stream: str) -> tuple[str, str | None]:
    """(reply text, problem) from `claude -p --output-format stream-json`: the
    text of the surviving assistant messages, in order (a message another one
    supersedes or a refusal fallback retracts is dropped). A tool use, an
    unreadable line, or anything but exactly one result event that is a success
    is a problem."""
    events, unreadable = _events(stream)
    if unreadable:
        return "", f"{unreadable} unreadable event lines"
    messages: list[tuple[str | None, str]] = []
    evicted: set[str] = set()
    results: list[dict[str, Any]] = []
    for event in events:
        kind = event.get("type")
        if kind == "assistant":
            evicted.update(str(u) for u in event.get("supersedes") or [])
            blocks = [b for b in (event.get("message") or {}).get("content") or [] if isinstance(b, dict)]
            if any(b.get("type") == "tool_use" for b in blocks):
                return "", "a tool use"
            messages.append((event.get("uuid"), "".join(b.get("text") or "" for b in blocks
                                                        if b.get("type") == "text")))
        elif kind == "system" and event.get("subtype") == "model_refusal_fallback":
            evicted.update(str(u) for u in event.get("retracted_message_uuids") or [])
        elif kind == "result":
            results.append(event)
    if len(results) != 1 or results[0].get("is_error") or results[0].get("subtype") != "success":
        return "", "not exactly one successful result event"
    return "".join(text for uuid, text in messages if uuid is None or str(uuid) not in evicted), None


def codex_answer(stream: str) -> tuple[str, str | None]:
    """(reply text, problem) from ``codex exec --json`` output: the last agent
    message of a completed turn. A failed turn, an error event, or any item in
    the turn other than a message or reasoning is a problem. Items before the
    turn starts (configuration warnings) are not part of the reply."""
    started = completed = False
    failed: str | None = None
    other: set[str] = set()
    answer: str | None = None
    events, unreadable = _events(stream)
    if unreadable:
        return "", f"{unreadable} unreadable event lines"
    for event in events:
        kind = event.get("type")
        if kind == "turn.started":
            started = True
        elif kind == "turn.completed":
            completed = True
        elif kind in ("turn.failed", "error"):
            failed = str(kind)
        elif started and str(kind).startswith("item."):
            item = event.get("item") or {}
            if item.get("type") not in CODEX_ANSWER_ITEMS:
                other.add(str(item.get("type")))
            elif item.get("type") == "agent_message" and kind == "item.completed":
                answer = item.get("text")
    if failed:
        return "", f"a {failed} event"
    if other:
        return "", "items other than the reply: " + ", ".join(sorted(other))
    if not completed or not isinstance(answer, str):
        return "", "no completed turn with a reply"
    return answer, None


def gemini_api_answer(body_text: str) -> tuple[str, str | None]:
    """(reply text, problem) from a generateContent response body. An error
    body, another model version, a candidate count other than one, a finish
    reason other than STOP, or a part that is not text is a problem. Thought
    parts are not part of the reply."""
    try:
        body = json.loads(body_text)
    except ValueError:
        return "", "unreadable API response"
    if not isinstance(body, dict):
        return "", "unreadable API response"
    if "error" in body:
        return "", _api_error(body_text.encode("utf-8"))
    version = body.get("modelVersion")
    if version != GEMINI_API_MODEL:
        return "", f"model version {version!r}, not {GEMINI_API_MODEL}"
    candidates = body.get("candidates")
    if not isinstance(candidates, list) or len(candidates) != 1:
        return "", f"{len(candidates) if isinstance(candidates, list) else 'no'} candidates"
    candidate = candidates[0]
    if not isinstance(candidate, dict):
        return "", "unreadable candidate"
    # Parts first: a forbidden part stops the run whatever the finish reason,
    # so a MAX_TOKENS reply that holds one is never resent (plan v5).
    content = candidate.get("content")
    parts = content.get("parts") if isinstance(content, dict) else None
    if parts is None and candidate.get("finishReason") in RESEND_REASONS:
        parts = []  # an empty resendable reply may leave out its content
    if not isinstance(parts, list) or not all(isinstance(p, dict) for p in parts):
        return "", "unreadable reply parts"
    other = sorted({k for part in parts for k in part if k not in GEMINI_ANSWER_PART_KEYS})
    if other:
        return "", "parts other than the reply: " + ", ".join(
            k if KEY_RE.fullmatch(k) else "(unrecognized key)" for k in other)
    if any(not isinstance(p.get("text"), str) for p in parts):
        return "", "a reply part without text"
    reason = candidate.get("finishReason")
    if reason != "STOP":
        return "", "finish reason " + (reason if isinstance(reason, str) and API_STATUS_RE.fullmatch(reason)
                                       else "(unrecognized)")
    return "".join(p["text"] for p in parts if not p.get("thought")), None


ANSWER_PARSERS: dict[str, Callable[[str], tuple[str, str | None]]] = {
    "codex": codex_answer, "gemini": gemini_api_answer, "claude_agy": agy_answer,
    **{judge: claude_answer for judge in CLAUDE_JUDGES}}


def _log(calls_log: Path, entry: dict[str, Any]) -> None:
    fd = os.open(guard(calls_log), os.O_WRONLY | os.O_CREAT | os.O_APPEND | getattr(os, "O_NOFOLLOW", 0), 0o644)
    with os.fdopen(fd, "a", encoding="utf-8") as log:
        log.write(json.dumps(entry, ensure_ascii=False) + "\n")
        log.flush()
        os.fsync(log.fileno())


def _logged(calls_log: Path, call_id: str) -> list[dict[str, Any]]:
    if not calls_log.exists():
        return []
    return [e for e in read_jsonl(calls_log) if e.get("call_id") == call_id]


def completed_output(calls_log: Path, call_id: str, out_file: Path, prompt: str, transport: str) -> str | None:
    """The output of call ``call_id``, or None when it was never made or
    failed (a logged failure). An interrupted call stops, and so does an output
    whose last completed log line has another transport, prompt, or output
    hash: it belongs to another build or was changed."""
    if not guard(out_file).exists():
        entries = _logged(calls_log, call_id)
        lock = out_file.with_name(out_file.name + ".lock")
        if (entries and entries[-1].get("status") == "started") or (lock.exists() and not entries):
            raise Stop(f"{call_id}: an interrupted call (a started call or a lock without an output)")
        if any(e.get("status") == "completed" for e in entries):
            raise Stop(f"{call_id}: a completed call has lost its output; restore {out_file.name}")
        return None
    text = read_text(out_file)
    done = [e for e in _logged(calls_log, call_id) if e.get("status") == "completed"]
    if (not done or done[-1].get("prompt_sha256") != _sha(prompt)
            or done[-1].get("transport") != LOG_LABELS.get(transport, transport)
            or done[-1].get("output_sha256") != _sha(text)):
        raise Stop(f"{call_id}: an output exists but no completed call with this prompt, transport, "
                   "and output is logged")
    return text


class StreamOverflow(Exception):
    """A transport wrote more than STREAM_MAX_CHARS to stdout or stderr."""


def bounded_run(cmd: list[str], *, input: str | None, cwd: str, env: dict[str, str], timeout: float,
                limit: int = STREAM_MAX_CHARS, **_ignored) -> subprocess.CompletedProcess:
    """``subprocess.run(capture_output=True, text=True)`` without pipes. The
    process reads stdin from a file and writes stdout and stderr to files in a
    private directory, so nothing it does can block this process. It runs in
    its own process group, and the group is killed when it ends, at the
    deadline, when either file passes ``limit`` bytes (StreamOverflow; the
    files are checked every 50 ms, so a file can pass ``limit`` by what the
    process writes in that time), and on any exception here, Ctrl-C included.
    POSIX only: the kill reaches the transport's children through the group.
    No file-size rlimit: the CLIs write their own state files, which are
    larger than ``limit``."""
    if os.name != "posix":
        raise Stop("the claim-audit transports run on POSIX systems only")

    with tempfile.TemporaryDirectory(prefix="ars1002-io-") as io:
        paths = {name: Path(io) / name for name in ("stdin", "stdout", "stderr")}
        paths["stdin"].write_bytes((input or "").encode("utf-8"))
        deadline = time.monotonic() + timeout
        over = timed_out = False
        proc = mask = None
        interrupted = False
        # SIGINT stays blocked for the whole call, so Ctrl-C never cuts the start
        # or the cleanup short: the loop sees a pending Ctrl-C and stops, and the
        # interrupt is raised after the group is killed. The child unblocks
        # SIGINT before it runs.
        try:
            mask = signal.pthread_sigmask(signal.SIG_BLOCK, {signal.SIGINT})
            with open(paths["stdin"], "rb") as fin, open(paths["stdout"], "wb") as fout, \
                    open(paths["stderr"], "wb") as ferr:
                proc = subprocess.Popen(cmd, stdin=fin, stdout=fout, stderr=ferr, cwd=cwd, env=env,
                                        start_new_session=True,
                                        preexec_fn=lambda: signal.pthread_sigmask(signal.SIG_SETMASK, mask))
            while proc.poll() is None:
                if signal.SIGINT in signal.sigpending():
                    interrupted = True
                    break
                if any(paths[n].stat().st_size > limit for n in ("stdout", "stderr")):
                    over = True
                    break
                if time.monotonic() >= deadline:
                    timed_out = True
                    break
                time.sleep(0.05)
        finally:
            if proc is not None:
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except OSError:
                    pass
                proc.wait()
            if mask is not None:
                signal.pthread_sigmask(signal.SIG_SETMASK, mask)
            else:  # interrupted before the mask was saved; this CLI never blocks SIGINT otherwise
                signal.pthread_sigmask(signal.SIG_UNBLOCK, {signal.SIGINT})
        if interrupted:
            raise KeyboardInterrupt

        def head(name: str) -> bytes:  # at most limit + 1 bytes, whatever a stray writer adds later
            with open(paths[name], "rb") as handle:
                return handle.read(limit + 1)
        out, err = head("stdout"), head("stderr")
        if over or len(out) > limit or len(err) > limit:
            raise StreamOverflow
        if timed_out:
            raise subprocess.TimeoutExpired(cmd, timeout, output=out)
        return subprocess.CompletedProcess(cmd, proc.returncode, out.decode("utf-8", "replace"),
                                           err.decode("utf-8", "replace"))


def call_model(transport: str, prompt: str, out_file: Path, calls_log: Path, call_id: str,
               attempt: int = 1, runner=bounded_run) -> str:
    """Run one call and return its output text. Reuse a completed call only
    when its log line matches (``completed_output``); stop on an interrupted
    call, an oversized prompt, or a transport failure."""
    guard(out_file)
    size = len(prompt.encode("utf-8"))
    if size > PROMPT_LIMIT:
        raise Stop(f"{call_id}: prompt is {size} bytes, over the {PROMPT_LIMIT}-byte limit")
    lock = out_file.with_name(out_file.name + ".lock")
    reused = completed_output(calls_log, call_id, out_file, prompt, transport)
    if reused is not None:
        return reused
    token, workdir_base = (_claude_token(), _claude_workdir_base()) if transport in CLAUDE_JUDGES else ("", None)
    out_file.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY)
    except FileExistsError:
        raise Stop(f"{call_id}: an interrupted or concurrent call holds {lock.name}") from None
    os.close(fd)
    started = _now()
    seq = len(read_jsonl(calls_log)) + 1 if calls_log.exists() else 1
    base = {"call_id": call_id, "sequence_index": seq, "attempt": attempt,
            "transport": LOG_LABELS.get(transport, transport), "started_at": started, "prompt_sha256": _sha(prompt)}
    paid = transport == "gemini"
    _log(calls_log, {**base, "status": "started", **({"worst_case_usd": worst_case_usd(prompt)} if paid else {})})
    cmd, stdin = TRANSPORTS[transport](prompt)
    # Only the Gemini helper gets the API key; the CLIs never see it.
    env = dict(os.environ) if paid else {k: v for k, v in os.environ.items() if k != GEMINI_API_KEY_ENV}
    try:
        with tempfile.TemporaryDirectory(prefix="ars1002-", dir=workdir_base) as empty, \
                tempfile.TemporaryDirectory(prefix="ars1002-cfg-") as config_dir:
            if transport in CLAUDE_JUDGES:
                env = _claude_env(config_dir, token)
            proc = runner(cmd, input=stdin, capture_output=True, text=True, cwd=empty, env=env,
                          timeout=TIMEOUT_S + 60)
    except StreamOverflow:
        proc = None
    except (subprocess.TimeoutExpired, OSError) as exc:
        partial = getattr(exc, "stdout", None) or ""
        if isinstance(partial, bytes):
            partial = partial.decode("utf-8", "replace")
        _write_aux(out_file.with_name(out_file.name + ".partial"), partial[:STREAM_MAX_CHARS])
        _log(calls_log, {**base, "status": "failed", "completed_at": _now(), "error": type(exc).__name__,
                         **({"usd": None, "worst_case_usd": worst_case_usd(prompt)} if paid else {})})
        raise Stop(f"{call_id}: transport failed ({type(exc).__name__})") from None
    raw, err = (proc.stdout or "", proc.stderr or "") if proc else ("", "")
    if proc is None or len(raw) > STREAM_MAX_CHARS or len(err) > STREAM_MAX_CHARS:
        failure = f"stream over {STREAM_MAX_CHARS} characters"
        _log(calls_log, {**base, "status": "failed", "completed_at": _now(),
                         "exit_code": proc.returncode if proc else None, "error": failure,
                         **({"usd": None, "worst_case_usd": worst_case_usd(prompt)} if paid else {})})
        raise Stop(f"{call_id}: transport failed ({failure})")
    _write_aux(out_file.with_name(out_file.name + ".err"), err)
    _write_aux(out_file.with_name(out_file.name + ".stream"), raw)
    try:
        output, problem = ANSWER_PARSERS[transport](raw)
    except Exception as exc:  # noqa: BLE001 - a reply the parser cannot read is a transport failure
        output, problem = "", f"unreadable reply ({type(exc).__name__})"
    # One line-ending form, so the logged hash equals the hash of the text read back.
    output = output.replace("\r\n", "\n").replace("\r", "\n")
    usage = ({**gemini_usage(raw, len(prompt.encode("utf-8")), len(output.encode("utf-8"))),
              "worst_case_usd": worst_case_usd(prompt)} if paid else {})
    failure = ((f"exit {proc.returncode}" + (f": {problem}" if problem else "") if proc.returncode != 0 else None)
               or problem or (None if output.strip() else "empty reply"))
    if failure:
        _write_aux(out_file.with_name(out_file.name + ".partial"), raw)
        # A failed paid call counts at its worst case: its reported usage is not trusted.
        if paid:
            usage = {**usage, "reported_usd": usage.get("usd"), "usd": None}
        _log(calls_log, {**base, "status": "failed", "completed_at": _now(), "exit_code": proc.returncode,
                         "error": failure, **usage})
        raise Stop(f"{call_id}: transport failed ({failure})")
    tmp = out_file.with_name(out_file.name + ".tmp")
    _write_aux(tmp, output)
    os.replace(tmp, out_file)
    _log(calls_log, {**base, "status": "completed", "completed_at": _now(), "exit_code": proc.returncode,
                     "output_sha256": _sha(output), **usage})
    lock.unlink()
    return output


# ---------------------------------------------------------------------------
# Reading model output.
# ---------------------------------------------------------------------------


def json_lines(text: str) -> list[dict[str, Any]]:
    """Every line of ``text`` that is one JSON object; other lines are ignored."""
    rows = []
    for line in text.split("\n"):
        line = line.strip().strip("`")
        if line.startswith("{") and line.endswith("}"):
            try:
                value = json.loads(line)
            except ValueError:
                continue
            if isinstance(value, dict):
                rows.append(value)
    return rows


def _row_problem(row: dict[str, Any]) -> str | None:
    if row.get("verdict") not in VERDICTS:
        return "verdict"
    if row.get("severity") not in SEVERITIES:
        return "severity"
    if row["verdict"] == "false":
        if row.get("evidence") not in EVIDENCE:
            return "evidence"
        for field in ("quote", "locator"):
            if not isinstance(row.get(field), str) or not row[field].strip():
                return field
    return None


def read_verdicts(text: str, item_ids: list[str]) -> tuple[dict[str, dict[str, Any]], str | None]:
    """Return ({item_id: row}, problem). Every item needs exactly one line that
    passes the schema; a second line for an item, or a line that fails it, is a
    problem."""
    rows: dict[str, dict[str, Any]] = {}
    problems: list[str] = []
    wanted = set(item_ids)
    for row in json_lines(text):
        cid = row.get("claim_id")
        if not isinstance(cid, str) or cid not in wanted:
            continue
        if cid in rows:
            problems.append(f"{cid} answered twice")
            continue
        bad = _row_problem(row)
        if bad:
            problems.append(f"{cid} has an invalid {bad}")
            continue
        rows[cid] = row
    missing = [i for i in item_ids if i not in rows and not any(p.startswith(i + " ") for p in problems)]
    if missing:
        problems.append(f"{len(missing)} of {len(item_ids)} items have no verdict line")
    return rows, ("; ".join(problems[:5]) if problems else None)


def evidence_ok(row: dict[str, Any], claim_text: str, manuscript: str) -> bool:
    """The mechanical check on a ``false`` verdict's evidence (rubric V1)."""
    quote = _norm(row.get("quote") or "")
    if not quote:
        return False
    if row.get("evidence") == "contradiction":
        return quote in _norm(manuscript)
    if row.get("evidence") == "absent_quotation":
        return quote in _norm(claim_text) and quote not in _norm(manuscript)
    return False


# ---------------------------------------------------------------------------
# Contrast pairs.
# ---------------------------------------------------------------------------


def changed_tokens(a: str, b: str) -> int:
    """Tokens changed between two sentences: for each differing run, the longer side."""
    sm = difflib.SequenceMatcher(a=a.split(), b=b.split(), autojunk=False)
    return sum(max(i2 - i1, j2 - j1) for tag, i1, i2, j1, j2 in sm.get_opcodes() if tag != "equal")


# A sentence end inside the text: . ! or ?, maybe a closing quote or bracket,
# then space and a capital, a digit, or an opening quote or bracket (a second
# sentence can start with a digit). A period after a lone letter of any script
# (an initial such as "A. Smith" or "É. Durkheim", or "U.S.", "e.g.") or after
# "et al" is not counted as an end, so this check never rejects such a sentence; "group A. The" cannot be
# told from an initial by its characters, and the verifier's single_sentences
# question catches it.
_SENTENCE_BREAK = re.compile(r"(?<!\b[^\W\d_])(?<!\bal)[.!?][\"'”’)\]]*\s+[A-Z0-9\"'“‘(\[]")


def _one_sentence(text: str) -> bool:
    return text.endswith(".") and not _SENTENCE_BREAK.search(text[:-1])


def mechanical_checks(pair: dict[str, Any], manuscript: str) -> dict[str, bool]:
    acc, fal = str(pair.get("accurate_sentence", "")), str(pair.get("false_sentence", ""))
    quote = str(pair.get("evidence_quote", ""))
    return {
        "one_sentence_each": _one_sentence(acc) and _one_sentence(fal),
        "word_counts_8_to_50": all(8 <= len(s.split()) <= 50 for s in (acc, fal)),
        # Counted only when the word counts pass, so an over-long sentence costs no diff.
        "changed_tokens_1_to_4": (all(8 <= len(s.split()) <= 50 for s in (acc, fal))
                                  and 1 <= changed_tokens(acc, fal) <= 4),
        "evidence_quote_in_manuscript": bool(quote.strip()) and _norm(quote) in _norm(manuscript),
    }


def generate_prompt(fixture: str, plan: dict[str, Any]) -> str:
    return _template("contrast_generate.md").replace(
        "{n}", str(plan["contrast_pairs"]["per_fixture_requested"])).replace("{manuscript}", manuscript_text(fixture))


def verify_prompt(fixture: str, pairs: list[dict[str, Any]]) -> str:
    shown = "\n".join(json.dumps({k: p[k] for k in ("pair_id", "accurate_sentence", "false_sentence",
                                                    "evidence_quote")}, ensure_ascii=False) for p in pairs)
    return _template("contrast_verify.md").replace("{manuscript}", manuscript_text(fixture)).replace(
        "{pairs}", shown)


def _pair_log(pairs_dir: Path) -> Path:
    return guard(pairs_dir) / "calls.jsonl"


def generated_pairs(pairs_dir: Path, plan: dict[str, Any]) -> list[dict[str, Any]]:
    """The pairs read back from each logged generator output (plan transport)."""
    transport = plan["contrast_pairs"]["generator"]["transport"]
    rows = []
    for fixture in FIXTURE_FILES:
        text = completed_output(_pair_log(pairs_dir), f"generate-{fixture}", pairs_dir / f"{fixture}.generate.out",
                                generate_prompt(fixture, plan), transport)
        for pair in json_lines(text or ""):
            if isinstance(pair.get("pair_id"), str) and pair["pair_id"]:
                rows.append({**pair, "pair_id": f"{fixture}-{pair['pair_id']}", "fixture": fixture})
    return rows


def mechanically_valid(pairs: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for pair in pairs:
        checks = mechanical_checks(pair, manuscript_text(pair["fixture"]))
        if all(checks.values()):
            out.append({**pair, "mechanical": checks})
    return out


def accepted_pairs(pairs_dir: Path, plan: dict[str, Any]) -> tuple[list[dict[str, Any]], list[str], list[str]]:
    """(accepted, problems, rejected) from the logged verifier outputs (plan
    transport). A pair with no answer, a repeated answer, or any answer not
    true is rejected; a manuscript with no verifier output is a problem."""
    transport = plan["contrast_pairs"]["verifier"]["transport"]
    accepted, problems, rejected = [], [], []
    valid = _group(mechanically_valid(generated_pairs(pairs_dir, plan)), "fixture")
    for fixture in FIXTURE_FILES:
        pairs = valid.get(fixture, [])
        if not pairs:
            continue
        text = completed_output(_pair_log(pairs_dir), f"verify-{fixture}", pairs_dir / f"{fixture}.verify.out",
                                verify_prompt(fixture, pairs), transport)
        if text is None:
            problems.append(f"{fixture}: no verifier output")
            continue
        answers: dict[str, list[dict[str, Any]]] = defaultdict(list)
        for row in json_lines(text):
            if isinstance(row.get("pair_id"), str):
                answers[row["pair_id"]].append(row)
        for pair in pairs:
            got = answers.get(pair["pair_id"], [])
            if len(got) == 1 and all(got[0].get(q) is True for q in PAIR_QUESTIONS):
                accepted.append({**pair, "verify": got[0]})
            else:
                rejected.append(f"{pair['pair_id']}: {len(got)} answers" if len(got) != 1
                                else f"{pair['pair_id']}: an answer is not true")
    return accepted, problems, rejected


def _pair_transport(plan: dict[str, Any], role: str) -> str:
    """The pair generator and verifier never use the paid Gemini judge, which
    runs only through ``run`` with a cap."""
    transport = plan["contrast_pairs"][role]["transport"]
    if transport == "gemini":
        raise Stop(f"the {role} cannot use the paid Gemini API; it runs only through run --cap-usd")
    return transport


def cmd_generate(args) -> int:
    plan = load_plan()
    out = guard(args.out)
    text = call_model(_pair_transport(plan, "generator"), generate_prompt(args.fixture, plan),
                      out / f"{args.fixture}.generate.out", _pair_log(out), f"generate-{args.fixture}")
    pairs = sum(1 for p in json_lines(text) if isinstance(p.get("pair_id"), str) and p["pair_id"])
    print(json.dumps({"fixture": args.fixture, "pairs": pairs}))
    return 0 if pairs else 1


def cmd_check_pairs(args) -> int:
    generated = generated_pairs(args.pairs_dir, load_plan())
    valid = mechanically_valid(generated)
    write_jsonl(args.pairs_dir / "checked_pairs.jsonl", valid)
    print(json.dumps({"pairs": len(generated), "mechanical_pass": len(valid),
                      "by_fixture": dict(sorted(Counter(p["fixture"] for p in valid).items()))}))
    return 0


def cmd_verify_pairs(args) -> int:
    """One verifier call per manuscript, over its mechanically valid pairs."""
    plan = load_plan()
    transport = _pair_transport(plan, "verifier")
    valid = _group(mechanically_valid(generated_pairs(args.pairs_dir, plan)), "fixture")
    for fixture in FIXTURE_FILES:
        if valid.get(fixture):
            call_model(transport, verify_prompt(fixture, valid[fixture]),
                       guard(args.pairs_dir) / f"{fixture}.verify.out", _pair_log(args.pairs_dir), f"verify-{fixture}")
    accepted, problems, rejected = accepted_pairs(args.pairs_dir, plan)
    write_jsonl(args.pairs_dir / "accepted_pairs.jsonl", accepted)
    problems += pair_problems(accepted, plan)
    print(json.dumps({"checked": sum(len(v) for v in valid.values()), "accepted": len(accepted),
                      "accepted_by_fixture": dict(sorted(Counter(p["fixture"] for p in accepted).items())),
                      "rejected": rejected, "problems": problems}))
    return 1 if problems else 0


def pair_problems(pairs: list[dict[str, Any]], plan: dict[str, Any]) -> list[str]:
    """The stop rule on contrast pairs: per manuscript, between the minimum and
    the requested number of accepted pairs, each with all four mechanical
    checks true when run again here and all eight verifier answers ``true``,
    and no repeated pair id or sentence."""
    cfg = plan["contrast_pairs"]
    found = []
    by_fixture = Counter(p.get("fixture") for p in pairs)
    for fixture in FIXTURE_FILES:
        n = by_fixture.get(fixture, 0)
        if not cfg["min_accepted_per_fixture"] <= n <= cfg["per_fixture_requested"]:
            found.append(f"{fixture}: {n} accepted pairs, outside "
                         f"{cfg['min_accepted_per_fixture']}-{cfg['per_fixture_requested']}")
    ids = Counter(p.get("pair_id") for p in pairs)
    found += [f"pair id {i} repeated" for i, c in ids.items() if c > 1]
    sentences = Counter(_norm(p.get(k, "")) for p in pairs for k in ("accurate_sentence", "false_sentence"))
    found += [f"a sentence is repeated {c} times" for c in sentences.values() if c > 1]
    for p in pairs:
        if p.get("fixture") not in FIXTURE_FILES:
            found.append(f"{p.get('pair_id')}: unknown fixture")
            continue
        checks = mechanical_checks(p, manuscript_text(p["fixture"]))
        if not all(checks.values()) or p.get("mechanical") != checks:
            found.append(f"{p.get('pair_id')}: a mechanical check is not true")
        if not all(p.get("verify", {}).get(q) is True for q in PAIR_QUESTIONS):
            found.append(f"{p.get('pair_id')}: a verifier answer is not true")
    return found


# ---------------------------------------------------------------------------
# Batches.
# ---------------------------------------------------------------------------


def _item_line(item_id: str, text: str) -> str:
    return json.dumps({"claim_id": item_id, "text": text}, ensure_ascii=False)


def _group(rows, field):
    out = defaultdict(list)
    for r in rows:
        out[r[field]].append(r)
    return out


def inventory_problems(claims: list[dict[str, Any]], summary: dict[str, Any], plan: dict[str, Any]) -> list[str]:
    expected = plan["claims"]["expected_counts"]
    found = list(summary.get("problems", []))
    bundles = {c.get("bundle") for c in claims}
    if summary.get("bundles") != expected["bundles"] or len(bundles) != expected["bundles"]:
        found.append(f"bundles: {len(bundles)} in the claims, {summary.get('bundles')} in the summary, "
                     f"!= {expected['bundles']}")
    fixtures = defaultdict(set)
    for c in claims:
        fixtures[c.get("bundle")].add(c.get("fixture"))
    found += [f"bundle {b} names more than one fixture" for b, f in sorted(fixtures.items()) if len(f) > 1]
    if len(claims) != expected["claims"] or summary.get("claims") != expected["claims"]:
        found.append(f"claims: {len(claims)} != {expected['claims']}")
    if len({c["claim_id"] for c in claims}) != len(claims):
        found.append("claim ids repeat")
    if any(c.get("fixture") not in FIXTURE_FILES for c in claims):
        found.append("a claim names an unknown fixture")
    return found


def build_batches(claims: list[dict[str, Any]], pairs: list[dict[str, Any]]) -> tuple[list[dict], list[dict]]:
    """Return (batches, key). Items get neutral ids in hash order; each batch is
    one bundle's claims plus contrast sentences of the same fixture, filled
    until the prompt would pass PROMPT_BUDGET."""
    template = _template("auditor.md")
    items: list[dict[str, Any]] = [
        {"source": f"claim:{c['claim_id']}", "bundle": c["bundle"], "fixture": c["fixture"],
         "text": c["text"], "kind": "claim", "claim_id": c["claim_id"]} for c in claims]
    bundles_by_fixture: dict[str, list[str]] = defaultdict(list)
    for c in claims:
        if c["bundle"] not in bundles_by_fixture[c["fixture"]]:
            bundles_by_fixture[c["fixture"]].append(c["bundle"])
    for fixture, fixture_pairs in _group(pairs, "fixture").items():
        bundles = sorted(bundles_by_fixture[fixture])
        if len(bundles) < 2:
            raise Stop(f"{fixture}: fewer than two bundles, so a pair's sentences would share a batch")
        for n, pair in enumerate(sorted(fixture_pairs, key=lambda p: p["pair_id"])):
            for side, offset in (("accurate", 0), ("false", 1)):
                items.append({"source": f"pair:{pair['pair_id']}:{side}",
                              "bundle": bundles[(n + offset) % len(bundles)], "fixture": fixture,
                              "text": pair[f"{side}_sentence"], "kind": f"contrast_{side}",
                              "pair_id": pair["pair_id"]})
    items.sort(key=lambda i: _sha(i["source"]))
    key = []
    for n, item in enumerate(items, start=1):
        item["item_id"] = f"i{n:04d}"
        key.append({k: v for k, v in item.items() if k != "text"})
    batches: list[dict[str, Any]] = []
    for bundle, bundle_items in sorted(_group(items, "bundle").items()):
        fixture = bundle_items[0]["fixture"]
        base = len(template.replace("{manuscript}", manuscript_text(fixture)).replace(
            "{claims}", "").encode("utf-8"))
        current: list[dict[str, Any]] = []
        size = base
        for item in bundle_items:
            extra = len(_item_line(item["item_id"], item["text"]).encode("utf-8")) + 1
            if base + extra > PROMPT_BUDGET:
                raise Stop(f"{item['item_id']}: one item does not fit a {PROMPT_BUDGET}-byte prompt")
            if current and size + extra > PROMPT_BUDGET:
                batches.append(_batch(bundle, fixture, len(batches), current))
                current, size = [], base
            current.append(item)
            size += extra
        if current:
            batches.append(_batch(bundle, fixture, len(batches), current))
    return batches, key


def _batch(bundle: str, fixture: str, n: int, items: list[dict[str, Any]]) -> dict[str, Any]:
    return {"batch_id": f"b{n + 1:03d}", "bundle": bundle, "fixture": fixture,
            "items": [{"claim_id": i["item_id"], "text": i["text"]} for i in items]}


def batch_prompt(batch: dict[str, Any]) -> str:
    claims = "\n".join(_item_line(i["claim_id"], i["text"]) for i in batch["items"])
    return _template("auditor.md").replace("{manuscript}", manuscript_text(batch["fixture"])).replace(
        "{claims}", claims)


def _inputs_digest() -> dict[str, str]:
    """Hashes of every file whose change would change a prompt or a score."""
    files = [SUITE / "plan.json", SUITE / "rubric.md", SUITE / "PREREGISTRATION.md",
             *sorted((SUITE / "prompts").glob("*.md")), *(MANUSCRIPTS / f for f in FIXTURE_FILES.values()),
             Path(__file__).resolve(), REPO_ROOT / "scripts" / "extract_panel_claims.py"]
    return {str(f.resolve().relative_to(REPO_ROOT)): _file_sha(f) for f in files}


# Files the build copies into the batches directory and binds by hash. Every
# later step reads these copies, never the originals.
SNAPSHOTS = ("claims.jsonl", "summary.json", "accepted_pairs.jsonl", "pair_calls.jsonl")


def cmd_build(args) -> int:
    plan = load_plan()
    claims_dir = args.claims.parent
    claims = read_jsonl(args.claims)
    summary = json.loads(read_text(claims_dir / "summary.json"))
    pairs, verify_problems, _rejected = accepted_pairs(args.pairs_dir, plan)
    problems = inventory_problems(claims, summary, plan) + verify_problems + pair_problems(pairs, plan)
    if problems:
        print(json.dumps({"problems": problems}))
        return 1
    out = guard(args.out)
    if out.exists() and any(out.iterdir()):
        raise Stop(f"{out} is not empty; build into a new directory")
    batches, key = build_batches(claims, pairs)
    if args.match_manifest:
        want = json.loads(read_text(args.match_manifest))["batches"]
        got = {b["batch_id"]: _sha(batch_prompt(b)) for b in batches}
        if got != want:
            differ = sorted(k for k in set(want) | set(got) if want.get(k) != got.get(k))
            print(json.dumps({"problems": [f"batch prompts differ from {args.match_manifest}: {differ[:10]}"]}))
            return 1
    out.mkdir(parents=True, exist_ok=True)
    for b in batches:
        _write_aux(out / f"{b['batch_id']}.json", json.dumps(b, ensure_ascii=False, indent=1) + "\n")
    write_jsonl(out / "item_key.jsonl", key)
    sources = {"claims.jsonl": args.claims, "summary.json": claims_dir / "summary.json",
               "pair_calls.jsonl": _pair_log(args.pairs_dir)}
    for name, src in sources.items():
        _write_aux(out / name, guard(src).read_bytes())
    write_jsonl(out / "accepted_pairs.jsonl", pairs)
    manifest = {"built_at": _now(), "inputs": _inputs_digest(),
                "snapshots": {name: _file_sha(out / name) for name in SNAPSHOTS},
                "seat_key_sha256": _file_sha(claims_dir / "key.jsonl"),
                "item_key_sha256": _file_sha(out / "item_key.jsonl"),
                "batches": {b["batch_id"]: _sha(batch_prompt(b)) for b in batches}}
    _write_aux(out / "build_manifest.json", json.dumps(manifest, indent=1) + "\n")
    print(json.dumps({"batches": len(batches), "items": len(key),
                      "contrast_items": sum(1 for k in key if k["kind"] != "claim"),
                      "largest_prompt_bytes": max(len(batch_prompt(b).encode("utf-8")) for b in batches)}))
    return 0


def load_build(batches_dir: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    """Load batches and key, refusing any drift from the build manifest."""
    manifest = json.loads(read_text(batches_dir / "build_manifest.json"))
    if manifest["inputs"] != _inputs_digest():
        raise Stop("an input file changed since the build (plan, rubric, preregistration, prompts, "
                   "manuscripts, or the scripts)")
    for name in (*SNAPSHOTS, "item_key.jsonl"):
        want = manifest["item_key_sha256"] if name == "item_key.jsonl" else manifest["snapshots"][name]
        if _file_sha(batches_dir / name) != want:
            raise Stop(f"{name} changed since the build")
    batches = []
    for batch_id in sorted(manifest["batches"]):
        if not BATCH_ID_RE.fullmatch(str(batch_id)):
            raise Stop(f"build manifest names a batch id that is not a file-name stem: {batch_id!r}")
        batch = json.loads(read_text(batches_dir / f"{batch_id}.json"))
        if batch.get("batch_id") != batch_id:
            raise Stop(f"{batch_id}.json holds batch {batch.get('batch_id')}")
        batches.append(batch)
    for b in batches:
        if _sha(batch_prompt(b)) != manifest["batches"][b["batch_id"]]:
            raise Stop(f"{b['batch_id']}: its prompt changed since the build")
    return batches, read_jsonl(batches_dir / "item_key.jsonl")


# ---------------------------------------------------------------------------
# Run.
# ---------------------------------------------------------------------------


def _positive_int(value: str) -> int:
    number = int(value)
    if number < 1:
        raise argparse.ArgumentTypeError(f"expected a whole number of at least 1, got {value}")
    return number


def contrast_batches(batches: list[dict[str, Any]], key: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """The batches that hold at least one contrast sentence (plan v10)."""
    contrast = {k["item_id"] for k in key if k["kind"] != "claim"}
    return [b for b in batches if any(i["claim_id"] in contrast for i in b["items"])]


def run_judge(judge: str, replicate: int, batches_dir: Path, out_root: Path, limit: int | None = None,
              runner=bounded_run, cap_usd: float | None = None, contrast_only: bool = False) -> dict[str, Any]:
    """Send each batch to ``judge``. The Gemini judge needs ``cap_usd``: a new
    call starts only when the logged Gemini spend under ``out_root`` plus the
    call's worst case fits under it; otherwise the run stops (budget_exhausted).
    A Claude judge (plan v10) runs the contrast batches only."""
    if (judge in CLAUDE_JUDGES) != contrast_only:
        raise Stop("--contrast-only is for the Claude judges, and they need it (plan v10)")
    if judge == "gemini" and not (cap_usd is not None and 0 < cap_usd <= GEMINI_CAP_MAX_USD):
        raise Stop(f"the gemini judge is paid: give --cap-usd above 0 and at most {GEMINI_CAP_MAX_USD:.0f}")
    if limit is not None and limit < 1:
        raise Stop(f"--limit must be at least 1, not {limit}")
    batches, key = load_build(batches_dir)
    if contrast_only:
        batches = contrast_batches(batches, key)
    out_dir = guard(out_root) / judge / f"r{replicate}"
    log = out_dir / "calls.jsonl"

    def paid_call(prompt: str, out_file: Path, call_id: str, attempt: int) -> str:
        if judge == "gemini" and completed_output(log, call_id, out_file, prompt, judge) is None:
            if _now()[:10] > GEMINI_PRICE_UNTIL:
                raise Stop(f"the Gemini price table holds through {GEMINI_PRICE_UNTIL}; update it before a paid call")
            spent = gemini_spent(guard(out_root))
            if spent + worst_case_usd(prompt) > cap_usd:
                raise Stop(f"budget_exhausted: {spent:.4f} USD logged, the next call can cost up to "
                           f"{worst_case_usd(prompt):.4f}, cap {cap_usd:.2f}")
        return call_model(judge, prompt, out_file, log, call_id, attempt=attempt, runner=runner)

    def call(prompt: str, out_file: Path, call_id: str, attempt: int = 1) -> str:
        """One attempt; a Gemini attempt that failed with a resendable finish
        reason is sent once more (plans v5, v8). A resend that failed stops the run."""
        # The first attempt's own output is checked first, as scoring does: an
        # output with no matching completed call stops here, before any resend.
        done = completed_output(log, call_id, out_file, prompt, judge)
        if done is not None:
            return done
        if not (judge == "gemini" and failed_resendable(log, call_id, prompt)):
            try:
                return paid_call(prompt, out_file, call_id, attempt)
            except Stop:
                if not (judge == "gemini" and failed_resendable(log, call_id, prompt)):
                    raise
        resend_id, resend_file = _resend(call_id, out_file)
        failed = [e for e in _logged(log, resend_id) if e.get("status") == "failed"]
        if failed:
            raise Stop(f"{resend_id}: the one resend after {_logged(log, call_id)[-1].get('error')} failed "
                       f"({failed[-1].get('error')})")
        return paid_call(prompt, resend_file, resend_id, attempt)

    # One paid run at a time per runs directory, so two replicates cannot both
    # pass the cap check on the same remaining budget.
    run_lock = guard(out_root) / judge / "run.lock"
    if judge == "gemini":
        run_lock.parent.mkdir(parents=True, exist_ok=True)
        try:
            os.close(os.open(run_lock, os.O_CREAT | os.O_EXCL | os.O_WRONLY))
        except FileExistsError:
            raise Stop(f"another gemini run holds {run_lock} (remove it if no run is active)") from None
    try:
        return _run_batches(judge, replicate, batches, limit, out_dir, call)
    finally:
        if judge == "gemini":
            run_lock.unlink()


def _run_batches(judge: str, replicate: int, batches: list[dict[str, Any]], limit: int | None, out_dir: Path,
                 call: Callable[..., str]) -> dict[str, Any]:
    done = 0
    for batch in (batches if limit is None else batches[:limit]):
        ids = [i["claim_id"] for i in batch["items"]]
        prompt = batch_prompt(batch)
        stem = f"{judge}-r{replicate}-{batch['batch_id']}"
        text = call(prompt, out_dir / f"{batch['batch_id']}.a1.out", f"{stem}-a1")
        _rows, problem = read_verdicts(text, ids)
        if problem:
            text = call(prompt + RETRY_NOTE.format(reason=problem),
                        out_dir / f"{batch['batch_id']}.a2.out", f"{stem}-a2", attempt=2)
            _rows, problem = read_verdicts(text, ids)
            if problem:
                raise Stop(f"{stem}: unreadable after one retry ({problem})")
        done += 1
    return {"judge": judge, "replicate": replicate, "batches": done}


def cmd_run(args) -> int:
    print(json.dumps(run_judge(args.judge, args.replicate, args.batches, args.out, args.limit,
                               cap_usd=args.cap_usd, contrast_only=args.contrast_only)))
    return 0


# ---------------------------------------------------------------------------
# Score.
# ---------------------------------------------------------------------------


def load_replicate(runs: Path, judge: str, replicate: int, batches: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """{item_id: verdict row} for one judge and replicate, from the attempt
    ``run_judge`` would use: the first, or the retry when the first is
    unreadable, each through its plan-v5 resend when it has one. Each output must match its completed log line for this
    build's prompt and this judge's transport (``completed_output``)."""
    out_dir = runs / judge / f"r{replicate}"
    log = out_dir / "calls.jsonl"
    found: dict[str, dict[str, Any]] = {}
    for batch in batches:
        ids = [i["claim_id"] for i in batch["items"]]
        prompt = batch_prompt(batch)
        stem = f"{judge}-r{replicate}-{batch['batch_id']}"
        text = attempt_output(log, f"{stem}-a1", out_dir / f"{batch['batch_id']}.a1.out", prompt, judge)
        if text is None:
            continue
        rows, problem = read_verdicts(text, ids)
        if problem:
            text = attempt_output(log, f"{stem}-a2", out_dir / f"{batch['batch_id']}.a2.out",
                                  prompt + RETRY_NOTE.format(reason=problem), judge)
            if text is None:
                continue
            rows, problem = read_verdicts(text, ids)
            if problem:
                continue
        found.update(rows)
    return found


def judge_flag(rows: list[dict[str, Any] | None], claim_text: str, manuscript: str) -> str:
    """One judge's flag on one item over its replicates: ``missing``, ``true``
    (every replicate false with checked evidence), ``false`` (no replicate
    false), or ``unresolved``."""
    if any(r is None for r in rows):
        return "missing"
    falses = [r["verdict"] == "false" for r in rows]
    if not any(falses):
        return "false"
    if all(falses) and all(evidence_ok(r, claim_text, manuscript) for r in rows):
        return "true"
    return "unresolved"


def contrast_gate(key: list[dict[str, Any]], replicates: list[dict[str, dict[str, Any]]],
                  bar: dict[str, float]) -> dict[str, Any]:
    """A judge passes only with a verdict for every contrast item in every
    replicate. A false sentence is detected when every replicate says false; an
    accurate sentence is flagged when any replicate says false."""
    false_items = [k["item_id"] for k in key if k["kind"] == "contrast_false"]
    true_items = [k["item_id"] for k in key if k["kind"] == "contrast_accurate"]
    missing = sorted(i for i in false_items + true_items for rows in replicates if i not in rows)
    def verdicts(i):
        return [rows[i]["verdict"] for rows in replicates if i in rows]
    detected = sum(1 for i in false_items if verdicts(i) and all(v == "false" for v in verdicts(i)))
    flagged = sum(1 for i in true_items if any(v == "false" for v in verdicts(i)))
    detection = detected / len(false_items) if false_items else None
    false_flag = flagged / len(true_items) if true_items else None
    passed = (not missing and detection is not None and false_flag is not None
              and detection >= bar["min_detection"] and false_flag <= bar["max_false_flag"])
    return {"false_sentences": len(false_items), "detected": detected, "detection_rate": detection,
            "accurate_sentences": len(true_items), "flagged": flagged, "false_flag_rate": false_flag,
            "missing_contrast_verdicts": len(missing), "pass": passed}


def classify(flags: dict[str, str]) -> str:
    """The one agreement list for a claim, from the valid judges' flags."""
    values = set(flags.values())
    if "missing" in values:
        return "missing"
    if "unresolved" in values:
        return "replicate_instability"
    if values == {"true"}:
        return "agreed_false"
    if values == {"false"}:
        return "agreed_not_false"
    return "cross_judge_divergence"


def score(batches_dir: Path, runs: Path, out: Path, seat_key: Path | None = None) -> dict[str, Any]:
    plan = load_plan()
    batches, key = load_build(batches_dir)
    texts = {i["claim_id"]: (i["text"], b["fixture"]) for b in batches for i in b["items"]}
    manuscripts = {f: manuscript_text(f) for f in FIXTURE_FILES}
    judges = plan["judges"]
    per_judge = {j: [load_replicate(runs, j, r, batches) for r in range(1, plan["replicates"] + 1)]
                 for j in judges}
    gates = {j: contrast_gate(key, per_judge[j], plan["contrast_gate"]) for j in judges}
    valid = [j for j in judges if gates[j]["pass"]]
    claims = [k for k in key if k["kind"] == "claim"]
    flags = {}
    for k in claims:
        text, fixture = texts[k["item_id"]]
        flags[k["item_id"]] = {j: judge_flag([rows.get(k["item_id"]) for rows in per_judge[j]],
                                             text, manuscripts[fixture]) for j in judges}
    lists: dict[str, list[str]] = defaultdict(list)
    for k in claims:
        lists[classify({j: flags[k["item_id"]][j] for j in valid}) if valid else "void"].append(k["item_id"])
    spread = {j: [sum(1 for k in claims if rows.get(k["item_id"], {}).get("verdict") == "false")
                  for rows in per_judge[j]] for j in judges}
    status = {2: "decision_relevant", 1: "exploratory_one_valid_judge", 0: "void"}[min(len(valid), 2)]
    result = {"judges": judges, "valid_judges": valid, "status": status, "contrast_gate": gates,
              "claims": len(claims), "lists": {name: lists.get(name, []) for name in (
                  "agreed_false", "agreed_not_false", "cross_judge_divergence", "replicate_instability",
                  "missing", "void")},
              "raw_false_by_judge_and_replicate": spread,
              "coverage_missing": {j: [sum(1 for k in claims if k["item_id"] not in rows) for rows in per_judge[j]]
                                   for j in judges}}
    review = lists["cross_judge_divergence"] + lists["replicate_instability"] + lists["missing"]
    out = guard(out)
    out.mkdir(parents=True, exist_ok=True)
    _write_aux(out / "score.json", json.dumps(result, indent=1) + "\n")
    write_adjudication_packet(out / "adjudication_packet.md", review, texts, per_judge, judges)
    decisions = load_decisions(out / "adjudication_decisions.json", batches_dir, review, texts)
    seats = load_seats(seat_key, batches_dir, key) if seat_key else None
    result["headline"] = headline(result, decisions, key, review, seats)
    _write_aux(out / "score.json", json.dumps(result, indent=1) + "\n")
    write_execution_manifest(out, [batches_dir / "pair_calls.jsonl", *sorted(guard(runs).rglob("calls.jsonl"))])
    return result


def load_decisions(path: Path, batches_dir: Path, review: list[str], texts) -> dict[str, Any]:
    """The maintainer's decisions file. Score writes it once, bound to this
    build and to each reviewed claim's text; a file from another build, or an
    entry whose claim text differs, stops."""
    build = _file_sha(batches_dir / "build_manifest.json")
    if not guard(path).exists():
        _write_aux(path, json.dumps({"build_manifest_sha256": build, "decisions": {
            i: {"text_sha256": _sha(texts[i][0]), "verdict": None, "criterion": None} for i in review}},
            indent=1) + "\n")
    decisions = json.loads(read_text(path))
    if decisions.get("build_manifest_sha256") != build:
        raise Stop(f"{path.name} belongs to another build")
    for item_id, entry in decisions.get("decisions", {}).items():
        if item_id in texts and (entry or {}).get("text_sha256") != _sha(texts[item_id][0]):
            raise Stop(f"{path.name}: the decision for {item_id} was made on another claim text")
    return decisions


def load_seats(seat_key: Path, batches_dir: Path, key: list[dict[str, Any]]) -> dict[str, str]:
    """{extractor claim id: seat} from the extractor's key.jsonl, which must be
    the file the build hashed and must cover every claim exactly once."""
    if _file_sha(seat_key) != json.loads(read_text(batches_dir / "build_manifest.json"))["seat_key_sha256"]:
        raise Stop("the seat key is not the key.jsonl of this build's claims")
    rows = read_jsonl(seat_key)
    seats = {r.get("claim_id"): r.get("seat") for r in rows}
    claims = {k["claim_id"]: k["bundle"] for k in key if k["kind"] == "claim"}
    if (len(seats) != len(rows) or set(seats) != set(claims)
            or any(s not in ("eic", "methodology", "domain", "perspective", "da") for s in seats.values())
            or any(r.get("bundle") != claims.get(r.get("claim_id")) for r in rows)):
        raise Stop("the seat key does not match this build's claims one to one")
    return seats


def headline(result: dict[str, Any], decisions: dict[str, Any], key: list[dict[str, Any]],
             review: list[str], seats: dict[str, str]) -> dict[str, Any]:
    """The adjudicated counts, once every reviewed claim has a verdict and a
    criterion. ``seats`` maps extractor claim ids to seats (key.jsonl, checked
    by ``load_seats``); it is used only here, after every verdict exists."""
    if result["status"] != "decision_relevant":
        return {"computed": False, "reason": result["status"]}
    made = decisions.get("decisions", {})
    pending = [i for i in review if (made.get(i) or {}).get("verdict") not in VERDICTS
               or (made.get(i) or {}).get("criterion") not in CRITERIA]
    if pending:
        return {"computed": False, "reason": f"{len(pending)} adjudication decisions pending"}
    false_items = set(result["lists"]["agreed_false"]) | {i for i in review if made[i]["verdict"] == "false"}
    claims = [k for k in key if k["kind"] == "claim"]
    by_seat: dict[str, list[int]] = defaultdict(lambda: [0, 0])
    for k in claims if seats is not None else ():
        by_seat[seats[k["claim_id"]]][0] += k["item_id"] in false_items
        by_seat[seats[k["claim_id"]]][1] += 1
    panels = {k["bundle"] for k in claims}
    panels_false = {k["bundle"] for k in claims if k["item_id"] in false_items}
    return {"computed": True, "estimand_status": "point_estimate",
            "false_claims": len(false_items), "claims": len(claims),
            "false_claim_rate": len(false_items) / len(claims),
            "by_seat": ({s: {"false": f, "claims": n, "rate": f / n} for s, (f, n) in sorted(by_seat.items())}
                        if seats is not None else "not computed: no --seat-key"),
            "panels_with_false_claim": len(panels_false), "panels": len(panels),
            "panels_with_false_claim_share": len(panels_false) / len(panels),
            "false_item_ids": sorted(false_items)}


def write_adjudication_packet(path: Path, items: list[str], texts, per_judge, judges) -> None:
    """One section per item to review: the claim, then each reading, labelled
    by a per-item shuffled letter so the packet does not show the judge. The
    packet is regenerated; decisions live in adjudication_decisions.json."""
    lines = ["# Adjudication packet (#1002)", "",
             "Apply rubric V1-V3 and R1-R5. Record each decision in adjudication_decisions.json "
             "(verdict and criterion id); this packet is rewritten on every score run.", ""]
    for item_id in items:
        text, fixture = texts[item_id]
        lines += [f"## {item_id} ({fixture})", "", "> " + text.replace("\n", "\n> "), ""]
        readings = [(j, r, rows.get(item_id)) for j in judges for r, rows in enumerate(per_judge[j], 1)]
        readings.sort(key=lambda t: _sha(f"{item_id}:{t[0]}:{t[1]}"))
        for letter, (_j, _r, row) in zip("ABCDEFGH", readings):
            if row is None:
                lines.append(f"- Reading {letter}: **missing**")
                continue
            detail = (f" | {row.get('evidence')} | {row.get('locator')} | \"{row.get('quote')}\""
                      if row["verdict"] == "false" else "")
            lines.append(f"- Reading {letter}: **{row['verdict']}**{detail} | {row.get('reason', '')}")
        lines.append("")
    _write_aux(path, "\n".join(lines) + "\n")


def write_execution_manifest(out: Path, logs: list[Path]) -> None:
    """``execution_manifest.json`` (heldout-execution-manifest/1.0) from every
    completed call of the generator, verifier, and judges, and
    ``call_attempts.json`` with every logged attempt, failed and interrupted
    ones included, which the manifest schema has no field for."""
    entries = []
    for log in logs:
        if guard(log).exists():
            source = "pairs" if log.name == "pair_calls.jsonl" else f"{log.parent.parent.name}/{log.parent.name}"
            entries += [{**e, "log": source} for e in read_jsonl(log)]
    entries.sort(key=lambda e: (e["started_at"], e["call_id"], e.get("status", "")))
    completed = [e for e in entries if e.get("status") == "completed"]
    manifest = {"schema_version": "heldout-execution-manifest/1.0", "suite": "panel_claim_factuality",
                "created_at": _now(), "write_once": True,
                "calls": [{"call_id": e["call_id"], "sequence_index": n, "started_at": e["started_at"],
                           "completed_at": e["completed_at"], "prompt_sha256": e["prompt_sha256"],
                           "output_sha256": e["output_sha256"], "attempt": e["attempt"]}
                          for n, e in enumerate(completed, start=1)]}
    if manifest["calls"]:
        _write_aux(guard(out) / "execution_manifest.json", json.dumps(manifest, indent=1) + "\n")
    _write_aux(out / "call_attempts.json", json.dumps({"attempts": entries}, indent=1) + "\n")


def contrast_score(batches_dir: Path, runs: Path, judges: list[str]) -> dict[str, Any]:
    """Plan v10: the contrast gate alone, for each Claude judge, over its
    replicates of the contrast batches. Each reply is read and checked whole,
    as in ``score``, but only the contrast items are counted."""
    plan = load_plan()
    batches, key = load_build(batches_dir)
    batches = contrast_batches(batches, key)
    return {j: contrast_gate(key, [load_replicate(runs, j, r, batches) for r in range(1, plan["replicates"] + 1)],
                             plan["contrast_gate"]) for j in judges}


def cmd_contrast_score(args) -> int:
    print(json.dumps(contrast_score(args.batches, args.runs, args.judge), indent=1))
    return 0


def cmd_score(args) -> int:
    result = score(args.batches, args.runs, args.out, args.seat_key)
    print(json.dumps({"status": result["status"], "valid_judges": result["valid_judges"],
                      "lists": {k: len(v) for k, v in result["lists"].items()},
                      "headline_computed": result["headline"]["computed"]}))
    return 0


# ---------------------------------------------------------------------------
# CLI.
# ---------------------------------------------------------------------------


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sub = parser.add_subparsers(dest="cmd", required=True)
    g = sub.add_parser("generate")
    g.add_argument("--fixture", choices=sorted(FIXTURE_FILES), required=True)
    g.add_argument("--out", type=Path, required=True, help="The pairs directory.")
    c = sub.add_parser("check-pairs")
    c.add_argument("--pairs-dir", type=Path, required=True)
    v = sub.add_parser("verify-pairs")
    v.add_argument("--pairs-dir", type=Path, required=True)
    b = sub.add_parser("build")
    b.add_argument("--claims", type=Path, required=True,
                   help="claims.jsonl, with summary.json and key.jsonl beside it.")
    b.add_argument("--pairs-dir", type=Path, required=True)
    b.add_argument("--out", type=Path, required=True)
    b.add_argument("--match-manifest", type=Path, help="An earlier build_manifest.json whose batch prompt "
                   "hashes this build must equal (plan v4 rebuild); otherwise nothing is written.")
    r = sub.add_parser("run")
    r.add_argument("--judge", choices=("codex", "gemini", *CLAUDE_JUDGES), required=True)
    r.add_argument("--replicate", type=int, choices=(1, 2), required=True)
    r.add_argument("--batches", type=Path, required=True)
    r.add_argument("--out", type=Path, required=True)
    r.add_argument("--limit", type=_positive_int, help="Send only the first N batches (the pilot); N >= 1.")
    r.add_argument("--cap-usd", type=float, help="Spend cap for the paid gemini judge, over every Gemini "
                   "call logged under --out (the pilot included).")
    r.add_argument("--contrast-only", action="store_true",
                   help="Send only the batches that hold contrast sentences (plan v10; Claude judges).")
    s = sub.add_parser("score")
    s.add_argument("--batches", type=Path, required=True)
    s.add_argument("--runs", type=Path, required=True)
    s.add_argument("--out", type=Path, required=True)
    s.add_argument("--seat-key", type=Path, help="extract_panel_claims key.jsonl, for rates by seat.")
    cs = sub.add_parser("contrast-score", help="Plan v10: the contrast gate for each Claude judge.")
    cs.add_argument("--batches", type=Path, required=True)
    cs.add_argument("--runs", type=Path, required=True)
    cs.add_argument("--judge", choices=sorted(CLAUDE_JUDGES), action="append", required=True)
    sub.add_parser("gemini-api-call", help="Internal: the gemini judge transport (prompt on stdin).")
    args = parser.parse_args(argv)
    handlers = {"generate": cmd_generate, "check-pairs": cmd_check_pairs, "verify-pairs": cmd_verify_pairs,
                "build": cmd_build, "run": cmd_run, "score": cmd_score, "contrast-score": cmd_contrast_score,
                "gemini-api-call": cmd_gemini_api_call}
    try:
        return handlers[args.cmd](args)
    except Stop as stop:
        print(f"STOP: {_printable(str(stop))}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
