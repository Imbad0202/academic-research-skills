# 模块：翻译（中译英）
**触发词**: translate, 翻译, 中译英, Chinese to English

**脚本用法**:
```bash
uv run python ../scripts/translate_academic.py "中文文本"
uv run python ../scripts/translate_academic.py input_zh.txt --domain deep-learning
```

**翻译流程**:

**步骤 1：领域识别**
确定专业领域术语：
- 深度学习：neural networks, attention, loss functions
- 时间序列：forecasting, ARIMA, temporal patterns
- 工业控制：PID, fault detection, SCADA

**步骤 2：术语确认**
```markdown
| 中文 | English | 领域 |
|------|---------|------|
| 注意力机制 | attention mechanism | DL |
| 时间序列预测 | time series forecasting | TS |
```

**步骤 3：翻译并注释**
```typst
// 原文：本文提出了一种基于Transformer的方法
// 译文：We propose a Transformer-based approach
// 注释："本文提出" -> "We propose"（学术标准表达）
```

**步骤 4：Chinglish 检查**
| 中式英语 | 地道表达 |
|----------|----------|
| more and more | increasingly |
| in recent years | recently |
| play an important role | is crucial for |

**常用学术句式**:
| 中文 | English |
|------|---------|
| 本文提出... | We propose... / This paper presents... |
| 实验结果表明... | Experimental results demonstrate that... |
| 与...相比 | Compared with... / In comparison to... |
| 综上所述 | In summary / In conclusion |

参考：[STYLE_GUIDE.md](../references/STYLE_GUIDE.md)、[COMMON_ERRORS.md](../references/COMMON_ERRORS.md)

