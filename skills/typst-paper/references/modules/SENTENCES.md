# 模块：长难句分析
**触发词**: long sentence, 长句, simplify, decompose, 拆解

**脚本用法**:
```bash
uv run python ../scripts/analyze_sentences.py main.typ
uv run python ../scripts/analyze_sentences.py main.typ --threshold 50
```

**触发条件**:
- 英文：句子 >50 词 或 >3 个从句
- 中文：句子 >60 字 或 >3 个分句

**输出格式**:
```typst
// 长难句检测（第45行，共67词）[Severity: Minor] [Priority: P2]
// 主干：[主语 + 谓语 + 宾语]
// 修饰成分：
//   - [关系从句] which...
//   - [目的状语] to...
// 建议改写：[简化版本]
```

**拆分策略**:
1. 识别主干结构
2. 提取修饰成分
3. 拆分为多个短句
4. 保持逻辑连贯性

