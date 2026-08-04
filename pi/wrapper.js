import { existsSync, readFileSync, realpathSync } from "node:fs";
import { fileURLToPath } from "node:url";
import { dirname, resolve } from "node:path";

const repoRoot = resolve(dirname(fileURLToPath(import.meta.url)), "..");
const commandPattern = /^\/(ars-[a-z0-9-]+)(?:\s+([\s\S]*))?$/;
const skillNames = ["deep-research", "academic-paper", "academic-paper-reviewer", "academic-pipeline"];
const skillPattern = new RegExp(`^/skill:(${skillNames.join("|")})(?:\\s|$)`);
const stateEntryType = "ars-pi-state";
const orchestrationPattern = /subagent|workflow|parallel[-_ ]agent|multi[-_ ]agent/i;
const webPattern = /websearch|web[-_ ]search|brave[-_ ]search|webfetch|web[-_ ]fetch|page[-_ ]retrieval/i;

function uniqueMatches(items, pattern) {
  return [...new Set(items.filter((item) => pattern.test(item.search)).map((item) => item.label))];
}

const xmlEntities = {
  amp: "&",
  lt: "<",
  gt: ">",
  quot: '"',
  apos: "'",
};

function decodeXml(text) {
  return text.replace(/&(amp|lt|gt|quot|apos);/g, (_match, entity) => xmlEntities[entity]);
}

function canonicalPath(path) {
  try {
    return realpathSync(path);
  } catch {
    return undefined;
  }
}

const skillLocations = new Set(
  skillNames
    .map((name) => canonicalPath(resolve(repoRoot, name, "SKILL.md")))
    .filter((location) => location !== undefined),
);

// Upstream SKILL.md files stay unmodified, so hide their exact Pi listings while ARS is inactive.
function hideArsSkills(systemPrompt) {
  return systemPrompt.replace(
    /(?:\r?\n)?[ \t]*<skill>(?:(?!<skill>)[\s\S])*?<\/skill>/g,
    (block) => {
      const location = block.match(/<location>([^<]+)<\/location>/)?.[1];
      const canonicalLocation = location ? canonicalPath(decodeXml(location)) : undefined;
      return canonicalLocation && skillLocations.has(canonicalLocation) ? "" : block;
    },
  );
}

async function probe(pi, command, args) {
  try {
    const result = await pi.exec(command, args, { timeout: 3000 });
    if (result.code !== 0) return "missing";
    return (result.stdout || result.stderr).trim().split("\n")[0] || "available";
  } catch {
    return "missing";
  }
}

const compatibility = `
## Academic Research Skills compatibility for Pi

Apply this section only while using an Academic Research Skills (ARS) skill or an \`/ars-*\` prompt.

- The original Claude Code ARS files are the source of truth. Do not replace their research, writing, review, integrity, or checkpoint rules.
- Resolve repository-relative ARS paths such as \`shared/\`, \`scripts/\`, \`commands/\`, \`deep-research/\`, \`academic-paper/\`, \`academic-paper-reviewer/\`, and \`academic-pipeline/\` from \`${repoRoot}\`.
- Treat Claude Code tool names as capability names. Use the equivalent tools available in the current Pi session.
- When ARS requests multiple agents, first inspect the available Pi tools and installed skills for a subagent, workflow, or parallel-agent capability; if none is obvious, search the configured Pi skill locations. Use a matching capability when available. Otherwise run the roles sequentially in the current agent and disclose that degraded execution mode. Do not require a specific orchestration add-on.
- When ARS requests \`WebSearch\`, \`WebFetch\`, or \`/websearch\`, first inspect the available tools and installed skills for web search or page retrieval; if none is obvious, search the configured Pi skill locations. Prefer an installed web-search skill when available. Otherwise use a permitted HTTP or bibliographic-API capability. If none exists, report the limitation and do not claim that a source was verified.
- Ask questions through normal conversation or any available user-question tool. Ignore Claude-only command \`model\` metadata and inherit the current Pi model.
`;

export default function (pi) {
  let arsActive = false;

  const setArsActive = (active) => {
    if (arsActive === active) return;
    arsActive = active;
    pi.appendEntry(stateEntryType, { active });
  };

  const restoreArsState = (ctx) => {
    const state = ctx.sessionManager.getBranch()
      .filter((entry) => entry.type === "custom" && entry.customType === stateEntryType)
      .pop();
    arsActive = state?.data?.active === true;
  };

  pi.on("session_start", (_event, ctx) => {
    restoreArsState(ctx);
  });

  pi.on("session_tree", (_event, ctx) => {
    restoreArsState(ctx);
  });

  pi.on("input", (event) => {
    const match = event.text.match(commandPattern);
    if (!match) {
      if (skillPattern.test(event.text)) setArsActive(true);
      return { action: "continue" };
    }

    const commandPath = resolve(repoRoot, "commands", `${match[1]}.md`);
    if (!existsSync(commandPath)) return { action: "continue" };

    setArsActive(true);
    const raw = readFileSync(commandPath, "utf8");
    const body = raw.replace(/^---\r?\n[\s\S]*?\r?\n---\r?\n?/, "").trim();
    const args = match[2]?.trim() ?? "";
    const hasArgumentPlaceholder = body.includes("$ARGUMENTS") || body.includes("$@");
    const executableBody = body.replace(
      /\b(python3?|bash|sh) scripts\/([^\s`]+)/g,
      (_match, command, script) => `${command} "${repoRoot}/scripts/${script}"`,
    );
    const expanded = executableBody.replace(/\$ARGUMENTS|\$@/g, () => args);
    const commandText = args && !hasArgumentPlaceholder
      ? `${expanded}\n\nUser request / arguments:\n${args}`
      : expanded;
    const skillName = body.match(/^Trigger the `([^`]+)` (?:skill|orchestrator)/m)?.[1];
    const text = skillName ? `/skill:${skillName} ${commandText}` : commandText;

    return { action: "transform", text };
  });

  pi.registerCommand("ars-pi-start", {
    description: "Enable ARS compatibility and automatic skill selection in this session",
    handler: async (_args, ctx) => {
      setArsActive(true);
      ctx.ui.notify("ARS compatibility instructions enabled for this session", "info");
    },
  });

  pi.registerCommand("ars-pi-stop", {
    description: "Disable ARS compatibility and automatic skill selection in this session",
    handler: async (_args, ctx) => {
      setArsActive(false);
      ctx.ui.notify("ARS compatibility instructions disabled for this session", "info");
    },
  });

  pi.registerCommand("ars-pi-doctor", {
    description: "Check optional Pi capabilities and local ARS runtime dependencies",
    handler: async () => {
      const activeTools = new Set(pi.getActiveTools());
      const tools = pi.getAllTools().map((tool) => ({
        label: `${activeTools.has(tool.name) ? "active tool" : "installed tool"}: ${tool.name}`,
        search: `${tool.name} ${tool.description}`,
      }));
      const commands = pi.getCommands()
        .filter((command) => !command.name.startsWith("ars-") && !command.name.startsWith("skill:academic-"))
        .map((command) => ({
          label: `${command.source}: /${command.name}`,
          search: `${command.name} ${command.description ?? ""}`,
        }));
      const candidates = [...tools, ...commands];
      const orchestration = uniqueMatches(candidates, orchestrationPattern);
      const web = uniqueMatches(candidates, webPattern);
      const python = await probe(pi, "python3", ["--version"]);
      const pyyaml = await probe(pi, "python3", ["-c", "import yaml; print(f'PyYAML {yaml.__version__}')"]);
      const pandoc = await probe(pi, "pandoc", ["--version"]);
      const tectonic = await probe(pi, "tectonic", ["--version"]);
      const sandbox = pi.getCommands().some((command) => command.name === "sandbox")
        ? `detected; allow read access to ${repoRoot} when running outside the checkout`
        : "not detected";
      const format = (matches) => matches.length > 0 ? matches.join(", ") : "none; sequential/degraded mode";
      const report = [
        "ARS Pi doctor",
        `Repository: ${repoRoot}`,
        `Orchestration: ${format(orchestration)}`,
        `Web retrieval: ${format(web)}`,
        `Python: ${python}`,
        `PyYAML: ${pyyaml}`,
        `Pandoc: ${pandoc}`,
        `Tectonic: ${tectonic}`,
        `Sandbox: ${sandbox}`,
        "Claude hooks: unavailable in Pi; write-scope enforcement remains prompt-level",
      ].join("\n");

      pi.sendMessage({ customType: "ars-pi-doctor", content: report, display: true });
    },
  });

  pi.on("before_agent_start", (event) => {
    if (!arsActive) return { systemPrompt: hideArsSkills(event.systemPrompt) };
    return { systemPrompt: `${event.systemPrompt}\n${compatibility}` };
  });
}
