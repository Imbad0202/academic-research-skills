---
type: llm
focus: last_message
weight: 1
---
Work through all ordering claims and quote evidence. The supplied venue explicitly requires alphabetical order of the author-provided surnames Tsai, Wu, Yang while retaining Chinese display names. The current 蔡 → 吳 → 楊 order is correct under that rule. Pass only if the response recognizes the venue override and accepts the current order. Fail if it flags this order as wrong, recommends 吳 → 楊 → 蔡 stroke ordering, or invents different romanizations.
