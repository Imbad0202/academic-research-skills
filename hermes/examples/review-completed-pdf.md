# Example: Full Review of a Completed PDF

```text
/skill hermes-academic-reviewer
Полная peer-review имитация Editor + 3 reviewers + devil's advocate + editorial decision для файла <path>. Дай ответ на русском.
```

Expected workflow:

1. Verify the PDF exists.
2. Extract text with PyMuPDF.
3. Identify genre and sections.
4. Spawn independent reviewers with `delegate_task`.
5. Synthesize editorial decision and revision roadmap.
