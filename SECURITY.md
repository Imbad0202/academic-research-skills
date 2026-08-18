# Security Policy

## Supported versions

Only the latest release on the `main` branch receives security fixes.

| Version | Supported |
|---------|-----------|
| Latest (`main`) | Yes |
| Older releases | No |

## Reporting a vulnerability

If you find a security issue (e.g. prompt injection, credential exposure, unintended data exfiltration through API calls), **do not open a public issue**.

Instead, use GitHub's **private vulnerability reporting**:

1. Go to the [Security Advisories](https://github.com/Imbad0202/academic-research-skills/security/advisories) page.
2. Click **"Report a vulnerability"**.
3. Fill in the details — what you found, how to reproduce it, and the potential impact.

You will receive an acknowledgement within 7 days. What happens after that follows the triage procedure below.

## Triage and response procedure

This project is solo-maintained ([GOVERNANCE.md](GOVERNANCE.md)). The 7-day acknowledgement above is the only hard time-bound promise; the fix targets below are best-effort, stated so they can be held to honestly. These promises hold while the project is actively maintained — on end-of-life (GOVERNANCE.md § Continuity and end of life) they lapse with the rest of maintenance.

1. **Acknowledgement** — within 7 days of the report: confirmation it arrived and, where possible, a first read on whether it is in scope.
2. **Severity classification** — each in-scope report is classified:

   | Severity | Definition | Response |
   |---|---|---|
   | **Critical** | Exploitable on a default install path: credential exposure, or data leaving the machine beyond the [docs/DATA_FLOWS.md](docs/DATA_FLOWS.md) map | Best-effort target 14 days; GitHub security advisory published with the fix |
   | **High** | Integrity-gate bypass or prompt injection that reaches gate decisions on a default path | Fix in the next release; best-effort target 30 days; advisory published with the fix |
   | **Moderate / Low** | Hardening of opt-in paths, defense-in-depth, issues requiring unusual configuration | Scheduled into ordinary release work; no target date promised |

3. **Resolution** — accepted reports get a fix on `main` and credit in the release notes (say so if you prefer no credit). Declined reports get a written explanation.
4. **Coordinated disclosure** — please hold exploit details until a fix is released; a GitHub security advisory is published for Critical and High fixes. You are welcome to ask for a status update in the same private thread at any time.

## Scope

The following are in scope for security reports:

- **Prompt injection** — inputs that cause agents to bypass IRON RULE constraints, integrity gates, or ethics protocols
- **Credential leakage** — configurations or agent behaviors that expose API keys (`ARS_CROSS_MODEL`, Semantic Scholar API key, etc.)
- **Data exfiltration** — agent behaviors that send user research data to unintended external services. The *intended* network touchpoints and local stores are mapped in [docs/DATA_FLOWS.md](docs/DATA_FLOWS.md); anything beyond that map is report-worthy.
- **Integrity gate bypass** — inputs that skip Stage 2.5 or Stage 4.5 blocking checks

The following are **out of scope**:

- AI output quality issues (hallucinations, weak arguments) — these are research limitations, not security vulnerabilities
- Feature requests or general bugs — use [Issues](https://github.com/Imbad0202/academic-research-skills/issues) instead
