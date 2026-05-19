# 模块：学术表达
**触发词**: academic tone, 学术表达, improve writing, weak verbs

**脚本用法**:
```bash
uv run python ../scripts/improve_expression.py main.typ
uv run python ../scripts/improve_expression.py main.typ --section methods
```

**英文学术表达**:
| 弱动词 | 学术替代 |
|----------|------------|
| use | employ, utilize, leverage |
| get | obtain, achieve, acquire |
| make | construct, develop, generate |
| show | demonstrate, illustrate, indicate |

**中文学术表达**:
| 口语化 | 学术化 |
|----------|----------|
| 很多研究表明 | 大量研究表明 |
| 效果很好 | 具有显著优势 |
| 我们使用 | 本文采用 |
| 可以看出 | 由此可见 |

**使用方式**：用户提供段落源码，Agent 分析并返回润色版本及对比表格。

**输出格式**（Markdown 对比表格）:
```markdown
| Original / 原文 | Revised / 改进版本 | Issue Type / 问题类型 | Rationale / 优化理由 |
|-----------------|---------------------|----------------------|---------------------|
| We use machine learning to get better results. | We employ machine learning to achieve superior performance. | Weak verbs | Replace "use" -> "employ", "get" -> "achieve" for academic tone |
```

**备选格式**（源码内注释）:
```typst
// EXPRESSION（第23行）[Severity: Minor] [Priority: P2]: 提升学术语气
// 原文：We use machine learning to get better results.
// 修改后：We employ machine learning to achieve superior performance.
// 理由：用学术替代词替换弱动词
```

参考：[STYLE_GUIDE.md](../references/STYLE_GUIDE.md)

