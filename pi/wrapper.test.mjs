import assert from "node:assert/strict";
import test from "node:test";
import { dirname, resolve } from "node:path";
import { fileURLToPath } from "node:url";
import wrapper from "./wrapper.js";

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const compatibilityMarker = "## Academic Research Skills compatibility for Pi";
const arsSkillNames = ["deep-research", "academic-paper", "academic-paper-reviewer", "academic-pipeline"];
const arsSkillLocations = arsSkillNames.map((name) => resolve(repoRoot, name, "SKILL.md"));
const externalSkillLocation = "/example/external/deep-research/SKILL.md";
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
  const pi = {
    on(name, handler) {
      handlers.set(name, handler);
    },
    registerCommand(name, command) {
      commands.set(name, command);
    },
    appendEntry(type, data) {
      entries.push({ type, data });
    },
  };

  wrapper(pi);
  handlers.get("session_start")({}, {
    sessionManager: { getBranch: () => [] },
  });

  return {
    handlers,
    commands,
    entries,
    notifications,
    commandContext: {
      ui: { notify: (message, level) => notifications.push({ message, level }) },
    },
  };
}

function runBeforeAgentStart(harness) {
  const result = harness.handlers.get("before_agent_start")({ systemPrompt: baseSystemPrompt });
  return result?.systemPrompt ?? baseSystemPrompt;
}

test("ordinary prompts hide only package ARS skills", () => {
  const harness = createHarness();
  const systemPrompt = runBeforeAgentStart(harness);

  for (const location of arsSkillLocations) assert.doesNotMatch(systemPrompt, new RegExp(location));
  assert.match(systemPrompt, new RegExp(externalSkillLocation));
  assert.doesNotMatch(systemPrompt, new RegExp(compatibilityMarker));
});

test("/ars-* activates compatibility for the same agent run", () => {
  const harness = createHarness();
  const result = harness.handlers.get("input")({ text: "/ars-plan topic" });
  const systemPrompt = runBeforeAgentStart(harness);

  assert.equal(result.action, "transform");
  for (const location of arsSkillLocations) assert.match(systemPrompt, new RegExp(location));
  assert.match(systemPrompt, new RegExp(compatibilityMarker));
});

test("direct ARS /skill:* activates compatibility", () => {
  const harness = createHarness();
  harness.handlers.get("input")({ text: "/skill:academic-pipeline topic" });
  const systemPrompt = runBeforeAgentStart(harness);

  assert.match(systemPrompt, new RegExp(compatibilityMarker));
});

test("/ars-pi-start and /ars-pi-stop toggle automatic invocation", async () => {
  const harness = createHarness();
  const start = harness.commands.get("ars-pi-start");
  const stop = harness.commands.get("ars-pi-stop");

  assert.ok(start);
  await start.handler("", harness.commandContext);
  assert.match(runBeforeAgentStart(harness), new RegExp(compatibilityMarker));
  for (const location of arsSkillLocations) {
    assert.match(runBeforeAgentStart(harness), new RegExp(location));
  }

  await stop.handler("", harness.commandContext);
  assert.doesNotMatch(runBeforeAgentStart(harness), new RegExp(compatibilityMarker));
  for (const location of arsSkillLocations) {
    assert.doesNotMatch(runBeforeAgentStart(harness), new RegExp(location));
  }
});
