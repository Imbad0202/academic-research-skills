# Module: Long Sentence Analysis

**Trigger**: long sentence, 长句, simplify, decompose, >50 words

Trigger condition: Sentences >50 words OR >3 subordinate clauses

```bash
uv run python -B scripts/analyze_sentences.py main.tex
uv run python -B scripts/analyze_sentences.py main.tex --section introduction --max-words 45 --max-clauses 3
```

Output format:
```latex
% LONG SENTENCE (Line 45, 67 words) [Severity: Minor] [Priority: P2]
% Core: [subject + verb + object]
% Subordinates:
%   - [Relative] which...
%   - [Purpose] to...
% Suggested: [simplified version]
```

