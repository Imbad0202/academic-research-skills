---
name: ars-reviewer
description: "Trigger the simulated peer-review panel for an academic paper draft"
skills:
  - academic-paper-reviewer
---

# /ars-reviewer

When this command is invoked, immediately initialize the `academic-paper-reviewer` team pipeline. 

## Default Execution Flow
1. **Intake**: Accept the user's paper draft, manuscript text, or repository files.
2. **Analysis**: Route the text through the 5-panel reviewer agents (`devils_advocate`, `domain_reviewer`, `editorial_synthesizer`, `methodology_reviewer`, `perspective_reviewer`).
3. **Output**: Deliver the full structured Peer Review Report, including the Five-Dimension Rubric scores and actionable Critical/Major/Minor issues lists.

## Available Modifiers
- `/ars-reviewer --mode=quick`: Triggers an EIC quick assessment and key issues list.
- `/ars-reviewer --mode=methodology`: Forces an in-depth focus strictly on methods and data rigor.
- `/ars-reviewer --mode=re-review`: Initializes a verification checklist to check author revisions against a prior report.
