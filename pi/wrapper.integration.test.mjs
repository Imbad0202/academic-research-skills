import assert from "node:assert/strict";
import test from "node:test";
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const packageRoot = process.env.PI_CODING_AGENT_ROOT;
const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");

// Opt-in: exercises the installed Pi runtime, without a provider or model calls.
test("real Pi runner composes ARS with earlier/later extension sections", {
  skip: !packageRoot && "Set PI_CODING_AGENT_ROOT to an installed Pi package directory",
}, async (t) => {
  const load = (path) => import(pathToFileURL(resolve(packageRoot, path)).href);
  const { loadExtensions } = await load("dist/core/extensions/loader.js");
  const { ExtensionRunner } = await load("dist/core/extensions/runner.js");
  const { buildSystemPrompt, buildSystemPromptSections } = await load("dist/core/system-prompt.js");
  const { version } = JSON.parse(readFileSync(resolve(packageRoot, "package.json"), "utf8"));
  t.diagnostic(`Pi ${version}, Node ${process.version}, ${process.platform}/${process.arch}`);

  const tempRoot = mkdtempSync(join(tmpdir(), "ars-pi-composition-"));
  t.after(() => rmSync(tempRoot, { recursive: true, force: true }));
  const early = join(tempRoot, "early.mjs");
  const late = join(tempRoot, "late.mjs");
  writeFileSync(early, `export default pi => pi.on("before_agent_start", event => {
    event.systemPromptOptions.sections.mcp_servers = "MCP sentinel from an earlier extension";
  });`);
  writeFileSync(late, `export default pi => pi.on("before_agent_start", event => {
    event.systemPromptOptions.sections.later_extension = "Sentinel from a later extension";
  });`);
  const loaded = await loadExtensions([early, resolve(repoRoot, "pi/wrapper.js"), late], tempRoot);
  assert.deepEqual(loaded.errors, []);
  // State persistence is isolated; no user session or provider is opened.
  loaded.runtime.appendEntry = () => {};
  const runner = new ExtensionRunner(loaded.extensions, loaded.runtime, tempRoot, {}, {});
  const errors = [];
  runner.onError((error) => errors.push(error));
  const names = ["deep-research", "academic-paper", "academic-paper-reviewer", "academic-pipeline"];
  const options = {
    cwd: tempRoot,
    skills: [
      ...names.map((name) => ({
        name, description: "ARS skill", filePath: resolve(repoRoot, name, "SKILL.md"),
        baseDir: resolve(repoRoot, name), source: "test",
      })),
      { name: "deep-research", description: "Unrelated", filePath: "/missing/external/SKILL.md", baseDir: "/missing/external", source: "test" },
    ],
    sections: {},
  };
  for (const active of [false, true]) {
    if (active) await runner.emitInput("/skill:academic-pipeline topic", undefined, "interactive");
    // Pi 1.1 takes (prompt, images, options); 1.3 takes (trigger, options).
    const { systemPromptOptions } = runner.emitBeforeAgentStart.length === 3
      ? await runner.emitBeforeAgentStart("Test prompt", undefined, options)
      : await runner.emitBeforeAgentStart({ messageType: "user", prompt: "Test prompt" }, options);
    assert.equal(systemPromptOptions.forceSystemPrompt, undefined);
    assert.equal(systemPromptOptions.skills.length, active ? 5 : 1);
    const sections = buildSystemPromptSections(systemPromptOptions);
    assert.match(sections.mcp_servers, /MCP sentinel/);
    assert.match(sections.later_extension, /Sentinel from a later extension/);
    assert.equal(Object.hasOwn(sections, "ars_compatibility"), active);
    if (active) assert.match(sections.ars_compatibility, /Academic Research Skills compatibility/);
    const prompt = buildSystemPrompt(systemPromptOptions);
    assert.match(prompt, /MCP sentinel/);
    assert.match(prompt, /Sentinel from a later extension/);
    // Rebuilding retained structured options must not depend on the rendered override.
    assert.equal(buildSystemPrompt(systemPromptOptions), prompt);
  }
  assert.deepEqual(errors, []);
});
