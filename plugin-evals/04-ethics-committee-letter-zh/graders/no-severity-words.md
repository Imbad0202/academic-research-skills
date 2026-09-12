---
type: regex
target: last_message
match: not_contains
flags: i
weight: 0.5
---
(嚴重度|優先級|優先順序|severity|priority)\s*[：:|]\s*(高|中|低|high|medium|low|major|minor|critical)
