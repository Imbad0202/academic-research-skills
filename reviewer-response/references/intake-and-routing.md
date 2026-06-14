# Intake And Routing

Use `reviewer-response` when the response package itself is the main deliverable.

Route instead to:

- `academic-paper` `revision` when the main draft text must be rewritten as the main task
- `academic-paper-reviewer` `re-review` when the main task is verification of whether revisions addressed prior concerns
- `academic-pipeline` when the user needs multi-stage orchestration from review comments through final integrity and finalization

Minimum input for useful output:

1. reviewer comments, panel comments, or decision text
2. title or a short description of the paper, abstract, proposal, or submission
3. if available, author notes about what has already been changed

If the user lacks revision-detail evidence, produce a `draft_with_placeholders` package rather than fabricating specifics.
