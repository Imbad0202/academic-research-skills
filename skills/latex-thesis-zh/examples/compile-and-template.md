# 示例：编译与模板识别

用户请求：
这个中文硕士论文项目一直编译失败，你顺便帮我确认它到底是不是 `thuthesis` 模板。

推荐模块顺序：
1. `template`
2. `compile`

命令：
```bash
uv run python $SKILL_DIR/scripts/detect_template.py main.tex
uv run python $SKILL_DIR/scripts/compile.py main.tex
```

预期输出：
- 模板识别结果。
- 编译失败时的精确命令、退出码和下一步排查建议。
