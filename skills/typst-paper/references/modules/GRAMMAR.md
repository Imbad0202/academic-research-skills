# 模块：语法分析（英文）
**触发词**: grammar, 语法, proofread, 润色, article usage

**脚本用法**:
```bash
uv run python ../scripts/analyze_grammar.py main.typ
uv run python ../scripts/analyze_grammar.py main.typ --section introduction
```

**重点检查领域**:
- 主谓一致
- 冠词使用（a/an/the）
- 时态一致性（方法用过去时，结果用现在时）
- Chinglish 检测

**输出格式**:
```typst
// GRAMMAR（第23行）[Severity: Major] [Priority: P1]: 冠词缺失
// 原文：We propose method for...
// 修改后：We propose a method for...
// 理由：单数可数名词前缺少不定冠词
```

**常见语法错误**:
| 错误类型 | 示例 | 修正 |
|----------|------|------|
| 冠词缺失 | propose method | propose a method |
| 主谓不一致 | The data shows | The data show |
| 时态混乱 | We proposed... The results shows | We proposed... The results show |
| Chinglish | more and more | increasingly |

参考：[COMMON_ERRORS.md](../references/COMMON_ERRORS.md)、[STYLE_GUIDE.md](../references/STYLE_GUIDE.md)

