# 模块：标题优化
**触发词**: title, 标题, title optimization, create title, improve title

**目标**：根据 IEEE/ACM/Springer/NeurIPS 最佳实践，生成和优化学术论文标题。

**脚本用法**：
```bash
# 根据内容生成标题
uv run python ../scripts/optimize_title.py main.typ --generate

# 优化现有标题
uv run python ../scripts/optimize_title.py main.typ --optimize

# 检查标题质量
uv run python ../scripts/optimize_title.py main.typ --check

# 交互式模式（推荐）
uv run python ../scripts/optimize_title.py main.typ --interactive

# 标题对比测试
uv run python ../scripts/optimize_title.py main.typ --compare "Title A" "Title B" "Title C"
```

**标题质量标准**（基于 IEEE Author Center 及顶级会议/期刊）：

| 标准 | 权重 | 说明 |
|------|------|------|
| **简洁性** | 25% | 删除 "A Study of", "Research on", "Novel", "New" |
| **可搜索性** | 30% | 核心术语（方法+问题）在前 65 字符内 |
| **长度** | 15% | 最佳：10-15 词（英文）/ 15-25 字（中文）|
| **具体性** | 20% | 具体方法/问题名称，避免泛泛而谈 |
| **规范性** | 10% | 避免生僻缩写（除 AI, LSTM, DNA 等通识缩写）|

## 标题生成工作流

**步骤 1：内容分析**
从摘要/引言中提取：
- **研究问题**：解决什么挑战？
- **研究方法**：提出什么方法？
- **应用领域**：什么应用场景？
- **核心贡献**：主要成果是什么？（可选）

**步骤 2：关键词提取**
识别 3-5 个核心关键词：
- 方法关键词："Transformer", "Graph Neural Network", "Reinforcement Learning"
- 问题关键词："Time Series Forecasting", "Fault Detection", "Image Segmentation"
- 领域关键词："Industrial Control", "Medical Imaging", "Autonomous Driving"

**步骤 3：标题模板选择**
顶级会议/期刊常用模式：

| 模式 | 示例（英文） | 示例（中文） | 适用场景 |
|------|-------------|-------------|----------|
| Method for Problem | "Transformer for Time Series Forecasting" | "时间序列预测的Transformer方法" | 通用研究 |
| Method: Problem in Domain | "Graph Neural Networks: Fault Detection in Industrial Systems" | "图神经网络：工业系统故障检测" | 领域专项 |
| Problem via Method | "Time Series Forecasting via Attention Mechanisms" | "基于注意力机制的时间序列预测" | 方法聚焦 |
| Method + Key Feature | "Lightweight Transformer for Real-Time Detection" | "轻量级Transformer实时检测方法" | 性能聚焦 |

**步骤 4：生成标题候选**
生成 3-5 个不同侧重的候选标题：
1. 方法侧重型
2. 问题侧重型
3. 应用侧重型
4. 平衡型（推荐）
5. 简洁变体

**步骤 5：质量评分**
每个候选标题获得总体评分（0-100）、各标准细分评分、具体改进建议。

## 标题优化规则

**删除无效词汇**：

**英文**：
| 避免使用 | 原因 |
|----------|------|
| A Study of | Redundant (all papers are studies) |
| Research on | Redundant (all papers are research) |
| Novel / New | Implied by publication |
| Improved / Enhanced | Vague without specifics |
| Based on | Often unnecessary |
| Using / Utilizing | Can be replaced with prepositions |

**中文**：
| 避免使用 | 原因 |
|----------|------|
| 关于...的研究 | 冗余（所有论文都是研究） |
| ...的探索 | 冗余且不具体 |
| 新型 / 新颖的 | 发表即意味着新颖 |
| 改进的 / 优化的 | 不具体，需说明如何改进 |
| 基于...的 | 可简化为直接表述 |

**推荐结构示例**：

**英文**：
```
Good: "Transformer for Time Series Forecasting in Industrial Control"
Bad:  "A Novel Study on Improved Time Series Forecasting Using Transformers"

Good: "Attention-Based LSTM for Multivariate Time Series Prediction"
Bad:  "An Improved LSTM Model Using Attention Mechanism for Prediction"
```

**中文**：
```
好：工业控制系统时间序列预测的Transformer方法
差：关于基于Transformer的工业控制系统时间序列预测的研究

好：注意力机制的多变量时间序列预测方法
差：基于注意力机制的改进型多变量时间序列预测模型研究
```

## 关键词布局策略

- **前 65 字符（英文）/ 前 20 字（中文）**：最重要的关键词（方法+问题）
- **避免开头**：Articles (A, An, The) / "关于"、"对于"
- **优先使用**：名词和技术术语，而非动词和形容词

## 缩写使用准则

| 可接受 | 标题中避免 |
|----------|--------------|
| AI, ML, DL | Obscure domain-specific acronyms |
| LSTM, GRU, CNN | Chemical formulas (unless very common) |
| IoT, 5G, GPS | Lab-specific abbreviations |
| DNA, RNA, MRI | Non-standard method names |

## 会议/期刊特殊要求

**IEEE Transactions**：
- 避免带下标的公式
- 使用 Title Case（主要词首字母大写）
- 典型长度：10-15 词

**ACM Conferences**：
- 可使用更有创意的标题和冒号副标题
- 典型长度：8-12 词

**Springer Journals**：
- 偏好描述性而非创意性，可稍长（最多 20 词）

**NeurIPS/ICML**：
- 简洁有力（8-12 词），方法名通常突出

## 输出格式

**英文论文**：
```typst
// ============================================================
// TITLE OPTIMIZATION REPORT
// ============================================================
// Current Title: "A Novel Study on Time Series Forecasting Using Deep Learning"
// Quality Score: 45/100
//
// Issues Detected:
// 1. [Critical] Contains "Novel Study" (remove ineffective words)
// 2. [Major] Vague method description ("Deep Learning" too broad)
//
// Recommended Titles (Ranked):
// 1. "Transformer-Based Time Series Forecasting for Industrial Control" [Score: 92/100]
// 2. "Attention Mechanisms for Multivariate Time Series Prediction" [Score: 88/100]
//
// Suggested Typst Update:
// #align(center)[
//   #text(size: 18pt, weight: "bold")[
//     Transformer-Based Time Series Forecasting for Industrial Control
//   ]
// ]
// ============================================================
```

**中文论文**：
```typst
// ============================================================
// 标题优化报告
// ============================================================
// 当前标题："关于基于深度学习的时间序列预测的研究"
// 质量评分：48/100
//
// 推荐标题（按评分排序）：
// 1. "工业控制系统时间序列预测的Transformer方法" [评分: 94/100]
// 2. "多变量时间序列预测的注意力机制研究" [评分: 89/100]
// ============================================================
```

**Typst 标题设置示例**：

**英文论文**：
```typst
#align(center)[
  #text(size: 18pt, weight: "bold")[
    Transformer-Based Time Series Forecasting for Industrial Control
  ]
]
```

**中文论文**：
```typst
#align(center)[
  #text(size: 18pt, weight: "bold", font: "Source Han Serif")[
    工业控制系统时间序列预测的Transformer方法
  ]

  #v(0.5em)

  #text(size: 14pt, font: "Times New Roman")[
    Transformer-Based Time Series Forecasting for Industrial Control Systems
  ]
]
```

参考资源：
- [IEEE Author Center](https://conferences.ieeeauthorcenter.ieee.org/)
- [Royal Society Blog on Title Optimization](https://royalsociety.org/blog/2025/01/title-abstract-and-keywords-a-practical-guide-to-maximizing-the-visibility-and-impact-of-your-papers/)

