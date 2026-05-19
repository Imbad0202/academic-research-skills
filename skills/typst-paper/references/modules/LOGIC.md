# 模块：逻辑衔接与方法论深度
**触发词**: logic, coherence, 逻辑, 衔接, methodology, 方法论, 论证, argument

**脚本用法**:
```bash
uv run python ../scripts/analyze_logic.py main.typ
uv run python ../scripts/analyze_logic.py main.typ --section methods
```

**目标**：确保段落间逻辑流畅，强化方法论的严谨性。

**重点检查领域**：

**1. 段落级逻辑衔接（AXES 模型）**：
| 组成部分 | 说明 | 示例 |
|----------|------|------|
| **A**ssertion（主张） | 清晰的主题句，陈述核心观点 | "注意力机制能够提升序列建模效果。" |
| **X**ample（例证） | 支撑主张的具体证据或数据 | "实验中，注意力机制达到95%准确率。" |
| **E**xplanation（解释） | 分析证据为何支撑主张 | "这一提升源于其捕获长程依赖的能力。" |
| **S**ignificance（意义） | 与更广泛论点或下一段的联系 | "这一发现为本文架构设计提供了依据。" |

**2. 过渡信号词**：
| 关系类型 | 中文信号词 | 英文对应 |
|----------|------------|----------|
| 递进 | 此外、进一步、更重要的是 | furthermore, moreover |
| 转折 | 然而、但是、相反 | however, nevertheless |
| 因果 | 因此、由此可见、故而 | therefore, consequently |
| 顺序 | 首先、随后、最后 | first, subsequently, finally |
| 举例 | 例如、具体而言、特别是 | for instance, specifically |

**3. 方法论深度检查清单**：
- [ ] 每个主张都有证据支撑（数据、引用或逻辑推理）
- [ ] 方法选择有充分理由（为何选此方法而非其他？）
- [ ] 明确承认研究局限性
- [ ] 清晰陈述前提假设
- [ ] 可复现性细节充分（参数、数据集、评估指标）

**4. 常见问题**：
| 问题类型 | 表现 | 修正方法 |
|----------|------|----------|
| 逻辑断层 | 段落间缺乏衔接 | 添加过渡句说明段落关系 |
| 无据主张 | 断言缺乏证据支撑 | 补充引用、数据或推理 |
| 方法论浅薄 | "本文采用X"但无理由 | 解释为何X适合本问题 |
| 隐含假设 | 前提条件未明示 | 显式陈述假设条件 |

**输出格式**：
```typst
// 逻辑衔接（第45行）[Severity: Major] [Priority: P1]: 段落间逻辑断层
// 问题：从问题描述直接跳转到解决方案，缺乏过渡
// 原文：数据存在噪声。本文提出一种滤波方法。
// 修改后：数据存在噪声，这对后续分析造成干扰。因此，本文提出一种滤波方法以解决该问题。
// 理由：添加因果过渡，连接问题与解决方案

// 方法论深度（第78行）[Severity: Major] [Priority: P1]: 方法选择缺乏论证
// 问题：方法选择未说明理由
// 原文：本文采用ResNet作为骨干网络。
// 修改后：本文采用ResNet作为骨干网络，其残差连接结构能有效缓解梯度消失问题，且在特征提取任务中表现优异。
// 理由：用技术原理论证架构选择
```

**分章节指南**：
| 章节 | 逻辑衔接重点 | 方法论深度重点 |
|------|--------------|----------------|
| Abstract | 目的→方法→结果→结论的流畅衔接 | 突出核心贡献 |
| Introduction | 问题→空白→贡献的流畅衔接 | 论证研究意义 |
| Related Work | 按主题分组，显式对比 | 定位与前人工作的关系 |
| Methods | 步骤间逻辑递进 | 论证每个设计选择 |
| Experiments | 设置→结果→分析的流程 | 解释评估指标选择 |
| Discussion | 发现→启示→局限的衔接 | 承认研究边界 |

**最佳实践**：
1. **一段一主题**：每段聚焦单一核心观点
2. **主题句先行**：段首即陈述本段主张
3. **证据链完整**：每个主张都需支撑（数据、引用或逻辑）
4. **显式过渡**：使用信号词标明段落关系
5. **论证而非描述**：解释"为何"，而非仅陈述"是什么"

参考：[WRITING_PHILOSOPHY.md](../references/WRITING_PHILOSOPHY.md)

---

## Literature Review Quality Validation (A1-A4)

> Authoritative rules are defined in `latex-paper-en/references/modules/LOGIC.md`. This section mirrors them for Typst usage.

### A1: Thematic Clustering (Not Author/Year Enumeration)

Related Work must organize references by research theme. Detecting 3+ consecutive sentences following "Author (Year) proposed..." signals enumeration → Major/P1.

**Script detection**: `analyze_logic.py` checks for consecutive author/year enumeration patterns in the `related` section.

### A2: Critical Analysis After Each Theme Cluster (LLM-judgment)

Each thematic group must end with a synthesis sentence that compares or evaluates. *Requires LLM judgment.*

### A3: Research Gap Derivation

The final paragraph of Related Work must contain explicit research gap language. The script scans the last 10 lines for gap keywords (`gap|limitation|remains|lack|overlooked|under-explored`). No match → Major/P1.

### A4: Funnel-Shaped Citation Density (LLM-judgment)

Citation density should follow broad→focused→specific. *Requires LLM judgment.*

---

## Cross-Section Logic Chain Closure (C3)

Introduction contribution claims must be answered in the Conclusion. The script extracts contribution keywords from `introduction` and answer keywords from `conclusion`. If intro has claims but conclusion has zero answer language → Major/P1 (`[Script]` observation).

Activate with `--cross-section` flag or full-document analysis (no `--section`).

