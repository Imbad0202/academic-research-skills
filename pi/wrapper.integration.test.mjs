import assert from "node:assert/strict";
import test from "node:test";
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath, pathToFileURL } from "node:url";

const packageRoot = process.env.PI_CODING_AGENT_ROOT;
const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");

// Opt-in: exercises the installed Pi runtime, without a provider or model calls.
test("real Pi runner handles structured prompts, legacy options and earlier overrides", {
  skip: !packageRoot && "Set PI_CODING_AGENT_ROOT to an installed Pi package directory",
}, async (t) => {
  const load = (path) => import(pathToFileURL(resolve(packageRoot, path)).href);
  const { loadExtensions } = await load("dist/core/extensions/loader.js");
  const { ExtensionRunner } = await load("dist/core/extensions/runner.js");
  const { buildSystemPrompt, buildSystemPromptSections } = await load("dist/core/system-prompt.js");
  const { version } = JSON.parse(readFileSync(resolve(packageRoot, "package.json"), "utf8"));
  t.diagnostic(`Pi ${version}, Node ${process.version}, ${process.platform}/${process.arch}`);

  for (const active of [false, true]) {
    for (const override of [false, true]) {
      await t.test(`active=${active}, earlier override=${override}`, async (t) => {
        const tempRoot = mkdtempSync(join(tmpdir(), "ars-pi-composition-"));
        t.after(() => rmSync(tempRoot, { recursive: true, force: true }));
        const early = join(tempRoot, "early.mjs");
        const late = join(tempRoot, "late.mjs");
        writeFileSync(early, `export default pi => pi.on("before_agent_start", event => {
          if (${override} || !event.systemPromptOptions?.sections) {
            return { systemPrompt: event.systemPrompt + "\\nMCP sentinel from an earlier extension" };
          }
          event.systemPromptOptions.sections.mcp_servers = "MCP sentinel from an earlier extension";
        });`);
        writeFileSync(late, `export default pi => pi.on("before_agent_start", event => {
          const options = event.systemPromptOptions;
          if (!options?.sections || options.forceSystemPrompt !== undefined) {
            return { systemPrompt: event.systemPrompt + "\\nSentinel from a later extension" };
          }
          options.sections.later_extension = "Sentinel from a later extension";
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
        };
        if (buildSystemPromptSections) options.sections = {};
        if (active) await runner.emitInput("/skill:academic-pipeline topic", undefined, "interactive");
        let result;
        switch (runner.emitBeforeAgentStart.length) {
          case 4: // Pi through 0.85: (prompt, images, rendered prompt, options).
            result = await runner.emitBeforeAgentStart("Test prompt", undefined, buildSystemPrompt(options), options);
            break;
          case 3: // Pi 0.86 / 1.1: (prompt, images, options).
            result = await runner.emitBeforeAgentStart("Test prompt", undefined, options);
            break;
          case 2: // Pi 1.3: (trigger, options).
            result = await runner.emitBeforeAgentStart({ messageType: "user", prompt: "Test prompt" }, options);
            break;
          default:
            assert.fail("Unrecognized Pi runner signature");
        }
        assert.deepEqual(errors, []);
        const prompt = result?.systemPrompt ?? buildSystemPrompt(result?.systemPromptOptions ?? options);
        assert.match(prompt, /MCP sentinel/);
        assert.match(prompt, /Sentinel from a later extension/);
        assert.match(prompt, /\/missing\/external\/SKILL.md/);
        for (const name of names) assert.equal(prompt.includes(resolve(repoRoot, name, "SKILL.md")), active);
        assert.equal(prompt.includes("## Academic Research Skills compatibility for Pi"), active);
        if (buildSystemPromptSections && !override) {
          assert.equal(result.systemPromptOptions.forceSystemPrompt, undefined);
          assert.equal(result.systemPromptOptions.skills.length, active ? 5 : 1);
          const sections = buildSystemPromptSections(result.systemPromptOptions);
          assert.match(sections.mcp_servers, /MCP sentinel/);
          assert.match(sections.later_extension, /Sentinel from a later extension/);
          assert.equal(Object.hasOwn(sections, "ars_compatibility"), active);
          assert.equal(buildSystemPrompt(result.systemPromptOptions), prompt);
        }
      });
    }
  }
});
