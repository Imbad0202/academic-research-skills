# 示例：主线逻辑与实验章节联查

用户请求：
请先检查这篇学位论文从绪论到结论的主线是不是闭合，再看看实验章节是不是更像项目汇报而不是论文讨论。

推荐模块顺序：
1. `logic`
2. `experiment`

命令：
```bash
uv run python $SKILL_DIR/scripts/analyze_logic.py main.tex --section introduction
uv run python $SKILL_DIR/scripts/analyze_logic.py main.tex --cross-section
uv run python $SKILL_DIR/scripts/analyze_experiment.py main.tex --section experiments
```

预期输出：
- 先指出绪论、贡献来源、结论之间是否错位。
- 再指出实验章节是否缺少比较、机制解释、限制讨论和未来工作。
- 两类问题分模块回报，不混成泛泛的“表达优化”。
