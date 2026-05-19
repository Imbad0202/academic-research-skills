# 示例：结构与一致性检查

用户请求：
请把这篇中文学位论文的结构梳理出来，再检查术语和缩略语有没有前后不一致。

推荐模块顺序：
1. `structure`
2. `consistency`

命令：
```bash
uv run python $SKILL_DIR/scripts/map_structure.py main.tex
uv run python $SKILL_DIR/scripts/check_consistency.py main.tex --terms
uv run python $SKILL_DIR/scripts/check_consistency.py main.tex --abbreviations
```

预期输出：
- 章节结构概览。
- 术语、缩略语漂移问题及其所在位置。
