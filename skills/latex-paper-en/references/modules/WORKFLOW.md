# Workflow & Best Practices

Choose the smallest module sequence that fits the user request.

## Common Review Paths

1. Build/debug path:
   `compile` -> `bibliography`
2. Prose quality path:
   `grammar` -> `sentences` -> `logic`
3. Submission hygiene path:
   `format` -> `figures` -> `title`
4. Language cleanup path:
   `translation` or `deai`, then `expression` if tone polish is still needed
5. Experiment scrutiny path:
   `experiment` on its own unless the user also asks for logic or figure review

## Best Practices

1. Route to one concern at a time instead of invoking every module by default.
2. Preserve `\cite{}`, `\ref{}`, `\label{}`, math, and custom macros unless edits are explicitly requested.
3. Treat script output as raw analysis; convert it into concise LaTeX-friendly findings for the final response.
4. Use version control when the user asks for source edits after the review phase.
