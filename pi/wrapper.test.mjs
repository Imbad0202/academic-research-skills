import assert from "node:assert/strict";
import test from "node:test";
import { mkdtempSync, rmSync, symlinkSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import wrapper from "./wrapper.js";

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const compatibilityMarker = "## Academic Research Skills compatibility for Pi";
const arsSkillNames = ["deep-research", "academic-paper", "academic-paper-reviewer", "academic-pipeline"];
const arsSkillLocations = arsSkillNames.map((name) => resolve(repoRoot, name, "SKILL.md"));
const externalSkillLocation = "/example/external/deep-research/SKILL.md";
const escapeXml = (text) => text
  .replaceAll("&", "&amp;")
  .replaceAll("<", "&lt;")
  .replaceAll(">", "&gt;")
  .replaceAll('"', "&quot;")
  .replaceAll("'", "&apos;");
const skillBlock = (name, description, location) => `  <skill>
    <name>${name}</name>
    <description>${description}</description>
    <location>${location}</location>
  </skill>`;
const baseSystemPrompt = [
  "Base prompt",
  "",
  "<available_skills>",
  ...arsSkillNames.map((name, index) => skillBlock(name, "ARS skill", arsSkillLocations[index])),
  skillBlock("deep-research", "Unrelated skill with a colliding name", externalSkillLocation),
  "</available_skills>",
].join("\n");

function createHarness() {
  const handlers = new Map();
  const commands = new Map();
  const entries = [];
  const notifications = [];
  let branch = [];
  const sessionContext = {
    sessionManager: { getBranch: () => branch },
  };
  const pi = {
    on(name, handler) {
      handlers.set(name, handler);
    },
    registerCommand(name, command) {
      commands.set(name, command);
    },
    appendEntry(customType, data) {
      const entry = { type: "custom", customType, data };
      entries.push(entry);
      branch.push(entry);
    },
  };

  wrapper(pi);
  handlers.get("session_start")({}, sessionContext);

  return {
    handlers,
    commands,
    entries,
    notifications,
    sessionContext,
    setBranch(nextBranch) {
      branch = nextBranch;
    },
    commandContext: {
      ui: { notify: (message, level) => notifications.push({ message, level }) },
    },
  };
}

function runBeforeAgentStart(harness, systemPrompt = baseSystemPrompt) {
  const result = harness.handlers.get("before_agent_start")({ systemPrompt });
  return result?.systemPrompt ?? systemPrompt;
}

test("ordinary prompts hide only package ARS skills", () => {
  const harness = createHarness();
  const systemPrompt = runBeforeAgentStart(harness);

  for (const location of arsSkillLocations) assert.equal(systemPrompt.includes(location), false);
  assert.equal(systemPrompt.includes(externalSkillLocation), true);
  assert.equal(systemPrompt.includes(compatibilityMarker), false);
});

test("skill hiding does not cross into an adjacent skill block", () => {
  const systemPrompt = [
    "Base prompt",
    "",
    "<available_skills>",
    `  <skill>
    <name>${arsSkillNames[0]}</name>
    <description>ARS skill</description>
    <location>${arsSkillLocations[0]}</location></skill>`,
    skillBlock("deep-research", "Unrelated skill", externalSkillLocation),
    "</available_skills>",
  ].join("\n");

  const result = runBeforeAgentStart(createHarness(), systemPrompt);

  assert.equal(result.includes(arsSkillLocations[0]), false);
  assert.equal(result.includes(externalSkillLocation), true);
});

test("ordinary prompts hide ARS skills loaded through an XML-escaped symlink path", (t) => {
  const tempRoot = mkdtempSync(join(tmpdir(), "ars-pi-&-"));
  t.after(() => rmSync(tempRoot, { recursive: true, force: true }));
  const linkedRoot = join(tempRoot, "linked-checkout");
  symlinkSync(repoRoot, linkedRoot, process.platform === "win32" ? "junction" : "dir");
  const linkedLocations = arsSkillNames.map((name) => resolve(linkedRoot, name, "SKILL.md"));
  const systemPrompt = [
    "Base prompt",
    "",
    "<available_skills>",
    ...arsSkillNames.map((name, index) => skillBlock(name, "ARS skill", escapeXml(linkedLocations[index]))),
    skillBlock("deep-research", "Unrelated missing skill", "/missing/deep-research/SKILL.md"),
    "</available_skills>",
  ].join("\n");

  const result = runBeforeAgentStart(createHarness(), systemPrompt);

  for (const location of linkedLocations) assert.equal(result.includes(escapeXml(location)), false);
  assert.equal(result.includes("/missing/deep-research/SKILL.md"), true);
});

test("/ars-* activates compatibility for the same agent run", () => {
  const harness = createHarness();
  const result = harness.handlers.get("input")({ text: "/ars-plan topic" });
  const systemPrompt = runBeforeAgentStart(harness);

  assert.equal(result.action, "transform");
  for (const location of arsSkillLocations) assert.equal(systemPrompt.includes(location), true);
  assert.equal(systemPrompt.includes(compatibilityMarker), true);
});

test("direct ARS /skill:* activates compatibility", () => {
  const harness = createHarness();
  harness.handlers.get("input")({ text: "/skill:academic-pipeline topic" });
  const systemPrompt = runBeforeAgentStart(harness);

  assert.equal(systemPrompt.includes(compatibilityMarker), true);
});

test("command arguments are not rewritten as script paths", () => {
  const harness = createHarness();
  const result = harness.handlers.get("input")({
    text: "/ars-cache-invalidate python scripts/user-provided.py",
  });

  assert.match(result.text, /python scripts\/user-provided\.py/);
  assert.equal(result.text.includes(`${repoRoot}/scripts/user-provided.py`), false);
  assert.equal(result.text.includes(`${repoRoot}/scripts/ars_cache_invalidate.py`), true);
});

test("argument placeholders are substituted in one pass", () => {
  const harness = createHarness();
  const result = harness.handlers.get("input")({
    text: "/ars-cache-invalidate alpha$@omega",
  });

  assert.match(result.text, /alpha\$@omega/);
  assert.doesNotMatch(result.text, /alphaalpha\$@omegaomega/);
});

test("/tree navigation recomputes activation from the selected branch", () => {
  const harness = createHarness();
  harness.handlers.get("input")({ text: "/ars-plan topic" });
  assert.equal(runBeforeAgentStart(harness).includes(compatibilityMarker), true);

  harness.setBranch([]);
  const sessionTree = harness.handlers.get("session_tree");
  assert.ok(sessionTree);
  sessionTree({}, harness.sessionContext);
  assert.equal(runBeforeAgentStart(harness).includes(compatibilityMarker), false);

  harness.setBranch([{ type: "custom", customType: "ars-pi-state", data: { active: true } }]);
  sessionTree({}, harness.sessionContext);
  assert.equal(runBeforeAgentStart(harness).includes(compatibilityMarker), true);
});

test("/ars-pi-start and /ars-pi-stop toggle automatic invocation", async () => {
  const harness = createHarness();
  const start = harness.commands.get("ars-pi-start");
  const stop = harness.commands.get("ars-pi-stop");

  assert.ok(start);
  await start.handler("", harness.commandContext);
  assert.equal(runBeforeAgentStart(harness).includes(compatibilityMarker), true);
  for (const location of arsSkillLocations) {
    assert.equal(runBeforeAgentStart(harness).includes(location), true);
  }

  await stop.handler("", harness.commandContext);
  assert.equal(runBeforeAgentStart(harness).includes(compatibilityMarker), false);
  for (const location of arsSkillLocations) {
    assert.equal(runBeforeAgentStart(harness).includes(location), false);
  }
});
