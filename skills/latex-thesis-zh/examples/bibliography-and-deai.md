# 示例：参考文献与去 AI 化

用户请求：
帮我按 GB/T 7714 检查参考文献，并看看绪论是不是有明显 AI 腔。

推荐模块顺序：
1. `bibliography`
2. `deai`

命令：
```bash
uv run python $SKILL_DIR/scripts/verify_bib.py references.bib --standard gb7714
uv run python $SKILL_DIR/scripts/deai_check.py main.tex --section introduction
```

预期输出：
- 参考文献格式问题、缺失字段或疑似异常项。
- 仅针对可见文字的去 AI 化建议，不改动引用和公式。
