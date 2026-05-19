# Academic Translation Guide


## 目录

- [Overview / 概述](#overview-概述)
- [1. Translation Principles / 翻译原则](#1-translation-principles-翻译原则)
  - [1.1 Core Principles / 核心原则](#11-core-principles-核心原则)
  - [1.2 Academic Tone / 学术语气](#12-academic-tone-学术语气)
- [2. Common Chinglish Corrections / 常见中式英语修正](#2-common-chinglish-corrections-常见中式英语修正)
  - [2.1 Redundant Expressions / 冗余表达](#21-redundant-expressions-冗余表达)
  - [2.2 Verb Improvements / 动词改进](#22-verb-improvements-动词改进)
  - [2.3 Structure Improvements / 结构改进](#23-structure-improvements-结构改进)
- [3. Section-Specific Guidelines / 各章节翻译指南](#3-section-specific-guidelines-各章节翻译指南)
  - [3.1 Abstract / 摘要](#31-abstract-摘要)
  - [3.2 Introduction / 引言](#32-introduction-引言)
  - [3.3 Related Work / 相关工作](#33-related-work-相关工作)
  - [3.4 Method / 方法](#34-method-方法)
  - [3.5 Experiments / 实验](#35-experiments-实验)
  - [3.6 Conclusion / 结论](#36-conclusion-结论)
- [4. Tense Usage Summary / 时态使用总结](#4-tense-usage-summary-时态使用总结)
- [5. Translation Workflow / 翻译工作流](#5-translation-workflow-翻译工作流)
  - [Step 1: Terminology Extraction / 术语提取](#step-1-terminology-extraction-术语提取)
  - [Step 2: Structure Mapping / 结构映射](#step-2-structure-mapping-结构映射)
  - [Step 3: Sentence Translation / 句子翻译](#step-3-sentence-translation-句子翻译)
  - [Step 4: Polish & Review / 润色审查](#step-4-polish-review-润色审查)
- [6. Quick Reference Patterns / 快速参考模板](#6-quick-reference-patterns-快速参考模板)
  - [6.1 Proposing Method / 提出方法](#61-proposing-method-提出方法)
  - [6.2 Describing Results / 描述结果](#62-describing-results-描述结果)
  - [6.3 Comparing Methods / 比较方法](#63-comparing-methods-比较方法)
  - [6.4 Analyzing Results / 分析结果](#64-analyzing-results-分析结果)
- [7. Domain-Specific Notes / 领域特定说明](#7-domain-specific-notes-领域特定说明)
  - [Deep Learning Papers](#deep-learning-papers)
  - [Time Series Papers](#time-series-papers)
  - [Industrial Control Papers](#industrial-control-papers)
- [Checklist / 检查清单](#checklist-检查清单)

---

> 中英学术翻译指南 - 从中文草稿到英文论文

## Overview / 概述

本指南帮助将中文学术草稿翻译为符合国际期刊/会议标准的英文论文。
核心原则：**准确性 > 流畅性 > 简洁性**

---

## 1. Translation Principles / 翻译原则

### 1.1 Core Principles / 核心原则

| 原则 | 说明 | 示例 |
|------|------|------|
| **准确性** | 技术术语必须准确，不可意译 | 卷积 → convolution (非 rolling) |
| **一致性** | 同一术语全文统一 | 不要混用 method/approach/technique |
| **简洁性** | 避免冗余表达 | ❌ in order to → ✅ to |
| **客观性** | 避免主观评价词 | ❌ very good → ✅ effective |

### 1.2 Academic Tone / 学术语气

```
❌ 避免:
- 口语化表达 (a lot of, kind of, stuff)
- 绝对化表述 (always, never, perfect)
- 情感化词汇 (amazing, terrible, exciting)

✅ 使用:
- 正式学术词汇 (significant, substantial, considerable)
- 谨慎限定词 (generally, typically, approximately)
- 客观描述 (effective, efficient, accurate)
```

---

## 2. Common Chinglish Corrections / 常见中式英语修正

### 2.1 Redundant Expressions / 冗余表达

| ❌ Chinglish | ✅ Academic English | 说明 |
|--------------|---------------------|------|
| in recent years | recently | 简化 |
| more and more | increasingly | 简化 |
| play an important role in | is crucial for / contributes to | 简化 |
| make a contribution to | contribute to | 简化 |
| have a great influence on | significantly affect | 简化 |
| in order to | to | 简化 |
| due to the fact that | because / since | 简化 |
| a large number of | many / numerous | 简化 |
| in the field of | in | 简化 |
| it is worth noting that | notably | 简化 |

### 2.2 Verb Improvements / 动词改进

| ❌ Weak Verb | ✅ Strong Verb | Context |
|--------------|----------------|---------|
| use | employ, utilize, leverage, adopt | 方法使用 |
| get | obtain, achieve, acquire, derive | 获得结果 |
| make | construct, develop, generate, create | 构建 |
| do | perform, conduct, execute, carry out | 执行 |
| show | demonstrate, illustrate, indicate, reveal | 展示 |
| give | provide, offer, present, yield | 提供 |
| have | possess, exhibit, contain | 具有 |
| put forward | propose, present, introduce | 提出 |

### 2.3 Structure Improvements / 结构改进

| ❌ Chinese Structure | ✅ English Structure |
|---------------------|---------------------|
| 本文提出了一种... | We propose... / This paper presents... |
| 首先...然后...最后... | First,... Subsequently,... Finally,... |
| 通过...实现了... | ... is achieved by/through... |
| 与...相比，...更好 | Compared with..., ... outperforms... |
| 实验结果表明... | Experimental results demonstrate that... |

---

## 3. Section-Specific Guidelines / 各章节翻译指南

### 3.1 Abstract / 摘要

```
结构: Background → Problem → Method → Results → Conclusion
时态: 
  - 背景/现状: 现在时
  - 本文工作: 现在时 (We propose...)
  - 实验结果: 过去时 (achieved, obtained)
长度: 150-250 words (根据会议/期刊要求)

模板:
[Background] ... remains a challenging problem.
[Problem] Existing methods suffer from...
[Method] In this paper, we propose...
[Results] Experimental results on ... demonstrate that...
[Conclusion] Our approach achieves state-of-the-art performance.
```

### 3.2 Introduction / 引言

```
结构: Context → Problem → Limitations → Contribution → Organization
时态:
  - 领域背景: 现在时
  - 已有工作: 现在完成时 (have been proposed)
  - 本文贡献: 现在时

贡献陈述模板:
The main contributions of this paper are summarized as follows:
• We propose a novel ... for ...
• We design a ... mechanism to address ...
• Extensive experiments demonstrate that ...
```

### 3.3 Related Work / 相关工作

```
时态: 现在完成时 + 过去时
  - 领域发展: 现在完成时 (have been widely studied)
  - 具体工作: 过去时 (proposed, introduced, developed)

过渡词:
- 同类工作: Similarly, Likewise, Along this line
- 对比: However, In contrast, Unlike
- 扩展: Furthermore, Moreover, Additionally
- 总结: Overall, In summary
```

### 3.4 Method / 方法

```
时态: 现在时 (描述方法本身)
语态: 被动语态为主，主动语态描述设计决策

结构词:
- 整体描述: consists of, comprises, is composed of
- 步骤: First, Then, Subsequently, Finally
- 公式引入: is defined as, is computed by, is formulated as

公式描述模板:
where $x$ denotes the input, $W$ represents the weight matrix,
and $b$ is the bias term.
```

### 3.5 Experiments / 实验

```
时态:
  - 实验设置: 过去时 (was conducted, were used)
  - 结果描述: 现在时 (shows, demonstrates)
  - 结果分析: 现在时

比较表达:
- 优于: outperforms, surpasses, exceeds
- 相当: is comparable to, is on par with
- 显著: significantly, substantially, considerably
- 略微: slightly, marginally

数值描述:
- 提升: improves by X%, achieves X% improvement
- 降低: reduces by X%, decreases X%
- 最优: achieves the best/lowest/highest
```

### 3.6 Conclusion / 结论

```
时态:
  - 总结工作: 过去时 (proposed, presented)
  - 结论陈述: 现在时
  - 未来工作: 将来时 (will, plan to)

模板:
In this paper, we proposed ... for ...
Experimental results demonstrated that ...
In future work, we plan to extend ...
```

---

## 4. Tense Usage Summary / 时态使用总结

| Section | Tense | Example |
|---------|-------|---------|
| Abstract - Background | Present | ... is an important task |
| Abstract - Method | Present | We propose... |
| Abstract - Results | Past | achieved, obtained |
| Introduction - Background | Present | ... has attracted attention |
| Introduction - Contribution | Present | We propose... |
| Related Work - General | Present Perfect | have been proposed |
| Related Work - Specific | Past | proposed, introduced |
| Method | Present | consists of, computes |
| Experiments - Setup | Past | was conducted |
| Experiments - Results | Present | shows, demonstrates |
| Conclusion - Summary | Past | proposed, presented |
| Conclusion - Future | Future | will explore |

---

## 5. Translation Workflow / 翻译工作流

### Step 1: Terminology Extraction / 术语提取
```
1. 识别中文稿中的专业术语
2. 查阅 TERMINOLOGY.md 确定标准译法
3. 建立本文术语表，确保一致性
```

### Step 2: Structure Mapping / 结构映射
```
1. 分析中文段落结构
2. 调整为英文学术结构（主题句在前）
3. 确保逻辑连接词使用正确
```

### Step 3: Sentence Translation / 句子翻译
```
1. 识别主干（主谓宾）
2. 处理修饰成分
3. 检查时态和语态
4. 简化冗余表达
```

### Step 4: Polish & Review / 润色审查
```
1. 检查术语一致性
2. 检查时态正确性
3. 检查 Chinglish
4. 检查学术语气
```

---

## 6. Quick Reference Patterns / 快速参考模板

### 6.1 Proposing Method / 提出方法

```latex
% 中文: 本文提出了一种基于...的...方法
We propose a novel [METHOD] based on [TECHNIQUE] for [TASK].
This paper presents a [ADJ] approach to [PROBLEM] using [METHOD].
In this work, we introduce [METHOD] that [BENEFIT].
```

### 6.2 Describing Results / 描述结果

```latex
% 中文: 实验结果表明，我们的方法取得了最好的效果
Experimental results demonstrate that our method achieves 
state-of-the-art performance on [DATASET].

Our approach outperforms existing methods by [X]% in terms of [METRIC].

The proposed method achieves [VALUE] [METRIC], which is [X]% higher 
than the best baseline.
```

### 6.3 Comparing Methods / 比较方法

```latex
% 中文: 与传统方法相比，我们的方法具有以下优势
Compared with conventional methods, our approach offers 
the following advantages: ...

Unlike previous methods that [LIMITATION], our method [ADVANTAGE].

While existing approaches [LIMITATION], we address this by [SOLUTION].
```

### 6.4 Analyzing Results / 分析结果

```latex
% 中文: 这是因为...
This improvement can be attributed to [REASON].
The performance gain is due to [REASON].
This is because [EXPLANATION].

% 中文: 值得注意的是...
It is worth noting that [OBSERVATION].
Notably, [FINDING].
An interesting observation is that [FINDING].
```

---

## 7. Domain-Specific Notes / 领域特定说明

### Deep Learning Papers
- 模型名称保持原文（BERT, GPT, ResNet）
- 超参数使用标准符号（$\alpha$, $\beta$, $\lambda$）
- 损失函数用 $\mathcal{L}$ 表示

### Time Series Papers
- 时间索引用 $t$，序列长度用 $T$ 或 $L$
- 预测步长用 horizon 或 forecasting horizon
- 历史窗口用 lookback window 或 historical window

### Industrial Control Papers
- 控制变量用标准符号（$u$ 输入，$y$ 输出，$x$ 状态）
- 强调实际应用场景和工业意义
- 注意安全性和可靠性相关表述

---

## Checklist / 检查清单

翻译完成后，请检查：

- [ ] 术语全文一致
- [ ] 时态使用正确
- [ ] 无 Chinglish 表达
- [ ] 无冗余词汇
- [ ] 学术语气恰当
- [ ] 公式符号统一
- [ ] 图表标题规范
- [ ] 参考文献格式正确
