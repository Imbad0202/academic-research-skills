# Academic Research Skills for Claude Code

[![Version](https://img.shields.io/badge/version-v3.21.2-blue)](https://github.com/Imbad0202/academic-research-skills/releases/tag/v3.21.2)
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.20696614-blue)](https://doi.org/10.5281/zenodo.20696614)
[![License: CC BY-NC 4.0](https://img.shields.io/badge/license-CC%20BY--NC%204.0-lightgrey)](https://creativecommons.org/licenses/by-nc/4.0/)
[![Sponsor](https://img.shields.io/badge/sponsor-Buy%20Me%20a%20Coffee-orange?logo=buy-me-a-coffee)](https://buymeacoffee.com/crucify020v)

[English](README.md) | [繁體中文版](README.zh-TW.md) | [日本語版](README.ja-JP.md) | [한국어](README.ko-KR.md) | [Español](README.es-ES.md)

一套完整的学术研究 Claude Code 技能包，涵盖从研究到论文出版的全流程。

**30 秒安装**（Claude Code CLI / VS Code / JetBrains，v3.7.0+）：

```text
/plugin marketplace add Imbad0202/academic-research-skills
/plugin install academic-research-skills
```

安装后运行 `/ars-plan`，ARS 会用苏格拉底式对话帮你规划章节结构。需要前置条件或传统 symlink 安装，请看 [快速安装](#快速安装)。

> **AI 是你的副驾驶，不是机长。** 这个工具不会替你写论文。它处理繁琐工作：搜文献、排格式、验数据、查逻辑一致性。这样你就能专注在真正需要思考的事上：定义问题、选择方法、解读数据意义、写出「我认为」后面那句话。
>
> 和 humanizer 不同，这个工具不是帮你隐藏使用 AI 协作的事实，而是帮你把关文章质量。风格校准会从你过去的文章中学习你的声音，写作质量检查会识别让文字读起来像机器生成的模式。目标是质量，不是掩饰。

### 为什么选「人机协作」而不是「全自动」？

Lu 等人（2026，*Nature* 651:914-919）发表的 **The AI Scientist** 是第一个端到端全自动的 AI 研究系统，其生成的论文通过 ICLR 2025 workshop 的盲审（评分 6.33/10，workshop 平均 4.87）。他们自己的 Limitations 段落也列出了这类系统会遇到的结构性失败模式：实现错误、幻觉实验结果、取巧特征依赖、实现错误被包装成「意外发现」、方法论伪造、框架锁定、引用幻觉。

ARS 建立在这个前提上：**人类研究者 + AI 的组合，比纯自动或纯人工更能避开这些失败模式**。Stage 2.5 与 Stage 4.5 学术诚信闸门运行 7 类阻断式检查清单（见 [`academic-pipeline/references/ai_research_failure_modes.md`](academic-pipeline/references/ai_research_failure_modes.md)），reviewer 也提供 opt-in 的 calibration mode 用用户提供的 gold set 测量 FNR/FPR。

[**Zhao 等人**](https://arxiv.org/abs/2605.07723)（2026-05）盘点了 arXiv、bioRxiv、SSRN、PMC 上 250 万篇论文中的 1.11 亿条引用，保守估计 2025 年单年就有 146,932 条幻觉引用，并观察到 2024 年中是上升的拐点；bioRxiv-to-PMC 这条配对的「预印本进入正式发表版本」幻觉存活率达 85.3%。他们把「真实引用被用来支撑被引文献其实没有提出的主张」描述为当前未解的问题。ARS v3.7.1 为来源 provenance 加上 trust-chain frontmatter，v3.7.3 为未来的 claim-level 审计铺设 locator 基础设施（三层引用 anchor），并在引用阶段呈现 advisory 风险信号（ARS 内部把这条 claim-faithfulness 缺口标记为「L3」，此为 ARS 的用词，不是论文的用词）。v3.7.x 的设计动机来自 Zhao 等人的 corpus-scale 发现；ARS 本身的 corpus-scale 评估仍是未来工作。

v3.8 补上 L3 缺口的另一半。v3.7.3 让每一条引用都带 locator anchor，v3.8 在这个基础上加一道 opt-in 审计（`ARS_CLAIM_AUDIT=1`）：获取每个 anchor 指向的原始文本，判断论文里的 claim 是否真有被该引用支撑。五类新的 HIGH-WARN annotation（claim-not-supported、negative-constraint-violation、fabricated-reference、anchorless、constraint-violation-uncited）会在 formatter terminal hard gate 直接阻止输出。Calibration 随 release 提供 20 条 gold set，采用 FNR<0.15、FPR<0.10 双阈值；正式放大投入前要先有 calibration 证据（v3.8 spec §5）。

v3.3 的灵感来自 [**PaperOrchestra**](https://arxiv.org/abs/2604.05018)（Song, Song, Pfister & Yoon, 2026, Google）：Semantic Scholar API 验证、反泄露协议、VLM 图表验证、修订轨迹追踪。ARS 当前以分类式、证据锚定的准则轨迹实现最后一项，不计算分数差。

---

## 架构与 pipeline

**👉 [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)** — 完整 pipeline 视图：流程图、阶段 × 维度矩阵、数据访问流、skill 依赖图、质量闸门、模式清单。

这份架构文档取代了原本散在 README 各处的 pipeline 描述。关于「哪个阶段跑什么」的所有信息都集中在一个地方。

## 快速安装

**前置条件**

- [Claude Code](https://docs.claude.com/en/docs/claude-code/setup)（建议最新版；plugin packaging 需要近期版本）
- 已导出 `ANTHROPIC_API_KEY`，或在第一次运行 `claude` 时设置
- *选用：* Pandoc 用于 DOCX 输出，tectonic + 思源宋体 TC 用于 APA 7.0 PDF（纯 Markdown 输出不需要这两者）

**Plugin 安装（v3.7.0+，推荐）：**

```text
/plugin marketplace add Imbad0202/academic-research-skills
/plugin install academic-research-skills
```

**验证可用：** 运行 `/ars-plan` 并描述你正在写的论文，ARS 会用苏格拉底式对话帮你规划章节结构。如果想做单次测试，可以运行 `/ars-lit-review "你的主题"`。

**👉 [docs/SETUP.md](docs/SETUP.md)** — 完整指南：安装 Claude Code、设置 API key、选用的 Pandoc/tectonic（DOCX/PDF）、跨模型验证（`ARS_CROSS_MODEL`），以及六种安装方式（Plugin、项目 skills、全局 skills、claude.ai Project、repo clone、Claude Science 导入）。

> **你的安装渠道实际启用哪些控制机制？** 可用性因安装渠道而异，请查逐渠道对照表：[docs/CONTROL_AVAILABILITY.md](docs/CONTROL_AVAILABILITY.md)（英文）。

**👉 [docs/DATA_FLOWS.md](docs/DATA_FLOWS.md)** — 哪些数据会离开你的电脑（书目 resolver、可选且需明确同意的跨模型调用、更新检查）、本地缓存存什么与存多久、每条路径怎么关闭。（英文）

**使用 Claude Science？** 四个 skill 可直接导入：**Skills → Import from GitHub**，粘贴 `https://github.com/Imbad0202/academic-research-skills`，点 **Preview**，再点 **Import 4 skills**（需本 repo v3.14.0+——导入器读取 marketplace manifest 中显式声明的 skill 路径）。导入是一次性快照：ARS 更新后需重新导入。导入的 skill 承载 ARS 方法论（研究／写作／评审协议）；Claude Code 专属机制——slash commands、hooks、subagent 编排——不会转移。详见 [docs/SETUP.md](docs/SETUP.md) Method 5。

**使用 Pi？** 运行 `pi install git:github.com/Imbad0202/academic-research-skills` 安装仓库内的社区维护 wrapper。它继续以原始 ARS 内容为准，并记录 Pi 在编排和 hooks 方面的限制。详见 [`pi/README.md`](pi/README.md)。

**用 Codex CLI？** 请安装姐妹版：[`Imbad0202/academic-research-skills-codex`](https://github.com/Imbad0202/academic-research-skills-codex)。同一套 workflow 内容，Codex 原生打包为单一 `$academic-research-suite` skill，提供 `ars-*` 别名。

## 性能与费用

**👉 [docs/PERFORMANCE.md](docs/PERFORMANCE.md)** — 各模式 token 预算、完整 pipeline 估算（一篇 15k 字论文约 ~$4–6），以及建议的 Claude Code 设置（Auto 模式；Agent Team 选用）。

## 使用指南与文章

- [学术写作不该是一个人的事：一套开源 AI 协作工具如何改变研究者的工作流](https://open.substack.com/pub/edwardwu223235/p/ai?r=4dczl&utm_medium=ios) — 完整使用指南（繁体中文）
- [Academic Writing Shouldn't Be a Solo Act](https://open.substack.com/pub/edwardwu223235/p/academic-writing-shouldnt-be-a-solo?r=4dczl&utm_medium=ios) — Full pipeline walkthrough (English)

---

## 功能特色一览

- **Deep Research** — 13 个 Agent 的研究团队，支持苏格拉底引导、PRISMA 系统性回顾、意图检测、对话健康度监控、可选跨模型 DA、Semantic Scholar API 验证。
- **Academic Paper** — 12 个 Agent 的论文撰写团队，含风格校准、写作质量检查、LaTeX 输出强化、可视化、修订教练、引用格式转换、反泄露协议、VLM 图表验证。
- **Academic Paper Reviewer** — 7 个 Agent 的多视角同行评审，采用逐准则、证据锚定的叙事判断（Journal-Fit Reviewer + 3 位动态审查者 + 魔鬼代言人），含让步门槛协议、攻击强度保持、可选跨模型 DA critique / calibration、R&R 追溯矩阵、只读约束。目前 live review 一律为 `NOT_CALIBRATED`；完整 calibration 只产生有界候选 profile，尚未接入 live review。
- **Academic Pipeline** — 10 阶段全流程调度器，含自适应 checkpoint、主张验证、材料护照、可选 `repro_lock`、可选跨模型学术诚信验证、中途强化机制，以及逐项准则的叙事退步检查（typed trajectory 尚未实现）。
- **数据访问层级标注**（v3.3.2+）— 每个 skill 声明 `data_access_level`（`raw` / `redacted` / `verified_only`），由 `scripts/check_data_access_level.py` 强制执行。设计灵感来自 Anthropic 的 automated-w2s-researcher（2026）。详见 [`shared/ground_truth_isolation_pattern.md`](shared/ground_truth_isolation_pattern.md)。
- **任务类型标注**（v3.3.2+）— 每个 skill 声明 `task_type`（`open-ended` 或 `outcome-gradable`）。目前 ARS 所有 skills 皆为 `open-ended`。
- **Benchmark 报告 Schema**（v3.3.5+）— JSON Schema + lint script，要求诚实的 benchmark 比较报告。详见 [`shared/benchmark_report_pattern.md`](shared/benchmark_report_pattern.md)。
- **Artifact 可复现性 Lockfile**（v3.3.5+）— Material Passport 添加可选 `repro_lock` 子区块。**是配置文档化，不是重播保证** — LLM 输出不是逐字节可复现。详见 [`shared/artifact_reproducibility_pattern.md`](shared/artifact_reproducibility_pattern.md)。
- **实验来源凭证登录**（#260）— Material Passport 可选的 `experiment_provenance[]` 记录研究者在**外部**跑过的实验（ARS 从不执行实验），论文主张通过 `claim_intent_manifest.planned_experiment_ids[]` 与之 join。诚信 gate（Stage 2.5/4.5）逐条比对实验支撑型主张与登录凭证 — `ALIGNED` / `OVERSTATED` / `NOT_SUPPORTED_BY_PROVENANCE` / `PROVENANCE_INSUFFICIENT` — **但不判定实验本身是否正确**。fail-closed 的 `experiment_intake_declaration` 让「有没有跑实验」成为 Stage 1 明确决定。详见 [`shared/handoff_schemas.md`](shared/handoff_schemas.md)。

**诚信与验证边界：**ARS 检查的是论文与所报告的研究过程，包括引用是否存在、主张与来源是否一致、所述方法、已登记实验结果与论文主张的一致性、图表忠实度，以及报告／流程／提交包的一致性；部分检查采用抽样或由 LLM 判断。ARS **不能**证明程序确实执行、原始数据真实，或结果可复现；如果捏造内容被前后一致地报告，仍可能通过这些检查。详见 [POSITIONING.md〈Integrity checks and the empirical-work boundary〉](POSITIONING.md#integrity-checks-and-the-empirical-work-boundary)。

---

## 实际产出展示

查看完整 10 阶段 pipeline 的实际产出 — 包含**同行评审报告、学术诚信验证报告、完稿论文**：

**[浏览所有 pipeline 产出 →](examples/showcase/)**

| 产出物 | 说明 |
|---|---|
| [完稿论文（英文）](examples/showcase/full_paper_apa7.pdf) | APA 7.0 格式，LaTeX 编译 |
| [完稿论文（中文）](examples/showcase/full_paper_zh_apa7.pdf) | 中文版，APA 7.0 |
| [学术诚信报告 — 审稿前](examples/showcase/integrity_report_stage2.5.pdf) | Stage 2.5：发现 15 个虚构引用 + 3 个统计错误 |
| [学术诚信报告 — 最终](examples/showcase/integrity_report_stage4.5.pdf) | Stage 4.5：确认零回归 |
| [同行评审第一轮](examples/showcase/stage3_review_report.pdf) | Journal-Fit Reviewer + 3 审查者 + 魔鬼代言人 |
| [再审](examples/showcase/stage3prime_rereview_report.pdf) | 修订后验证审查 |
| [同行评审第二轮](examples/showcase/stage3_review_report_r2.pdf) | 跟踪审查 |
| [回复审查意见](examples/showcase/response_to_reviewers_r2.pdf) | 逐点回复 |
| [出版后审计报告](examples/showcase/post_publication_audit_2026-03-09.pdf) | 独立全引用审计：发现 21/68 篇问题，在 3 轮学术诚信审查后仍被漏掉 |

---

## 搭配工具：Experiment Agent

如果你的研究需要在写作前做实验（代码或人工研究），[Experiment Agent](https://github.com/Imbad0202/experiment-agent) 技能填补 ARS Stage 1（研究）和 Stage 2（写作）之间的空缺。

```
ARS Stage 1 研究      →  RQ Brief + Methodology Blueprint
        ↓
  experiment-agent     →  运行/管理实验 → 验证结果
        ↓
ARS Stage 2 写作      →  用验证过的实验结果撰写论文
```

**功能**：执行代码实验（Python、R 等）并实时监控、管理人工研究 protocol 与 IRB 伦理审查、11 种统计谬误检测、可复现性验证。

**搭配使用方式**：ARS pipeline 完成 Stage 1 后暂停，在另一个 experiment-agent session 中执行实验，完成后将结果（含 Material Passport）带回 ARS Stage 2。ARS 不需要任何修改。详见 [experiment-agent README](https://github.com/Imbad0202/experiment-agent)。

---

## 使用方式

### 快速开始

```
# 启动完整研究 pipeline
你: "我想做一篇关于 AI 对高等教育质量保障影响的研究论文"

# 苏格拉底引导模式
你: "引导我研究 AI 在教育评估中的应用"

# 引导式论文撰写
你: "引导我写一篇关于少子化影响的论文"

# 审查现有论文
你: "帮我审查这篇论文"（接着提供论文）

# 查看 pipeline 进度
你: "进度" 或 "status"
```

### 个别 Skill 使用

#### Deep Research（深度研究，8 种模式）

```
"研究 AI 对高等教育的影响"                    → full mode（完整研究）
"给我一份 X 的快速摘要"                       → quick mode（快速简报）
"帮我做 X 的系统性文献回顾，含 PRISMA"        → systematic-review mode
"引导我研究 X"                                → socratic mode（苏格拉底引导）
"帮我核查这些说法"                            → fact-check mode（事实核查）
"帮我做文献回顾"                              → lit-review mode（文献回顾）
"审查这篇论文的研究质量"                      → review mode（论文审查）
```

#### Academic Paper（学术论文撰写，11 种模式）

```
"帮我写一篇论文"                              → full mode（完整撰写）
"引导我写论文"                                → plan mode（引导规划）
"先帮我搭论文大纲"                            → outline-only mode（只做大纲）
"我有初稿，这是审稿意见"                      → revision mode（修订）
"帮我整理这些审稿意见成修订路线图"            → revision-coach mode
"帮我写这篇的摘要"                            → abstract-only mode（摘要）
"把这批数据写成文献回顾论文"                  → lit-review mode（文献回顾论文）
"转换成 LaTeX" / "引用格式转 IEEE"            → format-convert mode（格式转换）
"检查引用格式"                                → citation-check mode（引用检查）
"帮我生成 NeurIPS 的 AI 使用声明"             → disclosure mode（AI 使用声明）
```

#### Academic Paper Reviewer（论文审查，6 种模式）

```
"审查这篇论文"                                → full mode（Journal-Fit Reviewer + R1/R2/R3 + 魔鬼代言人）
"快速评估这篇论文"                            → quick mode（快速评估）
"引导我改进这篇论文"                          → guided mode（引导改进）
"检查研究方法"                                → methodology-focus mode（方法论聚焦）
"验收修订"                                    → re-review mode（再审验收）
"用我的 gold set 校准 reviewer"               → calibration mode（校准）
```

#### Academic Pipeline（全流程调度器）

```
"我想做一篇完整的研究论文"                    → 从 Stage 1 开始完整 pipeline
"我已经有论文，帮我审查"                      → 从 Stage 2.5 进入（先做学术诚信审查）
"我收到审稿意见了"                            → 从 Stage 4 进入
```

> Pipeline 结束时自动产出 **Stage 6：过程记录** — 含论文创建过程记录与 6 维度协作质量评估（1–100 分）。

### 支持语言

- **繁体中文** — 用户以中文对话时默认使用
- **English** — 用户以英文对话时默认使用
- 学术论文自动产出双语摘要（中文 + English）

> **使用其他语言？** 苏格拉底模式（deep-research）和 Plan 模式（academic-paper）采用**意图匹配**启动 — 检测你的请求含义，而非比对特定关键字。这代表它们**支持任何语言**，无需额外设置。
>
> 不过，一般的 `Trigger Keywords` 区块（决定 skill 是否被启动）仍以英文和繁体中文为主。如果你发现 skill 在你的语言下触发不稳定，可以在各 `SKILL.md` 的 `### Trigger Keywords` 区块中加入你的语言的关键字，提高匹配信心。

### 支持引用格式

- APA 7.0（默认，含中文引用规则）
- Chicago（Notes & Author-Date）
- MLA
- IEEE
- Vancouver

### 支持论文结构

- IMRaD（实证研究）
- 主题式文献回顾
- 理论分析
- 个案研究
- 政策简报
- 研讨会论文

---

## Skill 详细信息

各 agent 的职责与各阶段产出物现已移至 [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md)。版本号保留在此以维持 release metadata 集中管理。

### Deep Research (v2.12.1)

13 个 Agent 的研究团队。模式：full、quick、review、lit-review、three-way-scan、fact-check、socratic、systematic-review。完整 agent 名单与产出物：见 ARCHITECTURE.md §3。

### Academic Paper (v3.3.1)

12 个 Agent 的论文撰写 pipeline。模式：full、plan、outline-only、revision、revision-coach、abstract-only、lit-review、format-convert、citation-check、disclosure、rebuttal-audit。输出：MD + DOCX（Pandoc 可用时）+ LaTeX（APA 7.0 `apa7` class / IEEE / Chicago）→ tectonic 编译 PDF。完整 agent 名单与各 phase 职责：见 ARCHITECTURE.md §3。

### Academic Paper Reviewer (v1.11.1)

7 个 Agent 的多视角审查，采用 **逐准则、证据锚定的叙事判断**。模式：full、re-review、quick、methodology-focus、guided、calibration。目前 live review 与 Schema 6 package 一律为 `NOT_CALIBRATED`；完整 calibration 可产生有界候选 profile，但尚未接入 live review。不得以固定总分映射接受、小修、大修或退稿。第一轮审查面板 vs. 契约治理再审调度的分界：见 ARCHITECTURE.md §3 Stage 3 / Stage 3'。

### Academic Pipeline (v3.21.2)

10 阶段调度器，含学术诚信验证、两阶段审查、苏格拉底指导、协作质量评估。Pipeline 保证：每个阶段都需用户确认 checkpoint；学术诚信验证（Stage 2.5 + 4.5）为 MANDATORY 且没有不留记录的绕过路径（所有覆写都须记录用户理由、供 Stage 6 使用）；R&R 追溯矩阵（Schema 11）独立验证作者修订主张。v3.4 添加 Compliance Agent（PRISMA-trAIce + RAISE）于 Stage 2.5 / 4.5。v3.5 添加 **协作深度观察员**（`collaboration_depth_agent`，仅咨询性质、永不阻挡流程）于每一次 FULL/SLIM checkpoint 与 pipeline 完成时。MANDATORY 学术诚信闸门（2.5 / 4.5）明确跳过观察员，避免稀释合规检查。理论基础：Wang & Zhang (2026), IJETHE 23:11。逐阶段矩阵（agent、产出物、闸门）：见 ARCHITECTURE.md §3。

---

## v3.0 优化：我们发现了 AI 的哪些结构性限制

在使用 ARS 撰写一篇关于 AI 与高等教育的反思文章时，我们遇到了三个结构性问题：

1. **框架锁定**：AI 在给定框架内越来越精致，但无法质疑框架本身
2. **谄媚倾向**：每次挑战魔鬼代言人的攻击，它都让步得太快
3. **意图检测错误**：苏格拉底模式在用户仍在探索时就急着收敛

### 改了什么

- **魔鬼代言人让步门槛**：反驳必须评分 1-5，≥4 才允许让步。不允许连续让步。框架锁定检测。
- **苏格拉底意图检测**：检测用户是「探索型」还是「目标型」。探索型模式停用自动收敛。
- **对话健康度指针**：每 5 轮后台自检，检测持续同意、回避冲突、过早收敛。
- **跨模型验证**：设置 `ARS_CROSS_MODEL` 激活第二 AI 模型独立审查。详见 [docs/SETUP.md](docs/SETUP.md)。
- **AI 自我反思报告**：Pipeline 结束后自动产出 AI 行为自评。

这些优化不能完全解决 AI 的结构性限制——它们让限制变得可见、可追踪、可被人类介入。

---

## 授权条款

本作品采用 [CC-BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/) 授权。

**你可以自由：**
- 分享 — 复制并分发本作品
- 改编 — 重混、转换、以本作品为基础进行创作

**但须遵守以下条件：**
- **署名** — 你必须给予适当署名
- **非商业性** — 你不得将本作品用于商业目的

**署名格式：**
```
Based on Academic Research Skills by Cheng-I Wu
https://github.com/Imbad0202/academic-research-skills
```

---

## 贡献者

**吴政宜** (Cheng-I Wu) — 作者与维护者

**[aspi6246](https://github.com/aspi6246)** — 贡献者。v3.1 优化灵感来自 [Claude-Code-Skills-for-Academics](https://github.com/aspi6246/Claude-Code-Skills-for-Academics)：只读约束模式、Anti-Pattern 作为一等公民设计、认知框架方法（教「如何思考」而非只有步骤）、精简 skill 体量理念。

**[mchesbro1](https://github.com/mchesbro1)** — 贡献者。最初提出并撰写了 IS Basket of 8 期刊清单（[Issue #5](https://github.com/Imbad0202/academic-research-skills/issues/5)）。

**[cloudenochcsis](https://github.com/cloudenochcsis)** — 贡献者。将 IS 章节从 *Basket of 8* 扩充为完整的 *Senior Scholars' Basket of 11*，补上 *Decision Support Systems*、*Information & Management*、*Information and Organization*（[Issue #7](https://github.com/Imbad0202/academic-research-skills/issues/7)、[PR #8](https://github.com/Imbad0202/academic-research-skills/pull/8)）。数据源：[AIS Senior Scholars' List of Premier Journals](https://aisnet.org/research/seniorscholarsbasket/)。

**[eltociear](https://github.com/eltociear)**（Ikko Eltociear Ashimine）— 贡献者。翻译了日文版 README（[`README.ja-JP.md`](README.ja-JP.md)）（[PR #161](https://github.com/Imbad0202/academic-research-skills/pull/161)）。

**[xpfo-go](https://github.com/xpfo-go)**（xpfo）— 贡献者。翻译了简体中文版 README（[`README.zh-CN.md`](README.zh-CN.md)）（[PR #181](https://github.com/Imbad0202/academic-research-skills/pull/181)）。

**[ktao732084-arch](https://github.com/ktao732084-arch)** — 贡献者。扩展了 `academic-paper` 披露系统，新增九个医学出版政策目标、按目标收集必需事实的流程，以及 fail-closed 的独立披露渲染（[Issue #596](https://github.com/Imbad0202/academic-research-skills/issues/596)、[PR #599](https://github.com/Imbad0202/academic-research-skills/pull/599)）；扩充 EQUATOR 临床报告参考，加入 CARE、STARD 和 TRIPOD+AI 的精简指引，以及 fail-closed 的研究设计路由流程（[Issue #594](https://github.com/Imbad0202/academic-research-skills/issues/594)、[PR #601](https://github.com/Imbad0202/academic-research-skills/pull/601)）；并设计及贡献独立的中文文献解析器、API 协议和合成传输 fixture 测试套件（[Issue #595](https://github.com/Imbad0202/academic-research-skills/issues/595)、[PR #600](https://github.com/Imbad0202/academic-research-skills/pull/600)）。

---

## 更新纪录

这里只列最近三个版本。完整更新记录在英文版 [CHANGELOG.md](CHANGELOG.md)。到 v3.21.2 为止的简体中文版本摘要已冻结存放于 [docs/changelog-archive/zh-CN.md](docs/changelog-archive/zh-CN.md)，之后不再更新。

### v3.21.2（2026-09-06）— 模型现况对齐（Fable 5.1 / GPT-6 Astra）、检查点决策来源与 CJK 标题匹配修复

> **对齐现况与决策来源，不是新能力：**v3.21.2 依据两份 2026 年 9 月的厂商 system card 对齐套件。`gpt-6-astra` 以 provisional 身份进入跨模型表（两条传输均如此），并依世代现况政策成为推荐的 OpenAI 验证模型；`gpt-5.6-sol` 保留其在 ChatGPT 订阅引用传输上的 validated 身份，本版不声称任何新的 bakeoff 结果。受限的 Codex 传输 reasoning-effort 集合新增 `ultra`。新增两道 guardrail，均为 prompt 层、由厂商文档而非 ARS 测量驱动：检查点决策来源（只有用户回合算决策；决策逐字转交子代理；风险 R11），以及供应商端监控或安全介入一律视为传输失败、永远不是判定。针对两份卡片的 harness 淘汰审计没有淘汰任何东西（0 条 prompt 文字淘汰；8 条 keep-as-debt 项目补上卡片引注）。修复：CJK 标题不再在四个索引解析器的精确标题门失败（#798），外层引号只在构成单一平衡单位时才剥除（#800）；autolink round-trip 测试明示其依赖（#801）；`check_surface_form_parity` 改为指名坏掉的环境而非 manifest；新增 skill 清单一致性 lint（#809）；R10 残余缺口去过时化（#813）；修正一行 MLA 规则（#805）。套件／pipeline → v3.21.2；deep-research → v2.12.1；academic-paper → v3.3.1；academic-paper-reviewer → v1.11.1。

### v3.21.1（2026-08-24）— 有界工作流基础、封存式 bakeoff 与传输强化

> **有明确测量才视为已测量，其余保持有界：**v3.21.1 修复 codex-cli 0.147.0 下受限的 ChatGPT 订阅引用传输，并记录首次 Promotion Bakeoff：`gpt-5.6-sol` 仅在该订阅传输上取得 validated，first-party API 路径仍为 provisional；今后的 bakeoff 则必须采用封存式预注册。本版还新增 default-off 的研究工作流 profile 基础（只有离线、确定性的 conformance；没有 pipeline hook，也未提供特定研究家族的成品 profile）、opt-in 的 inquiry-ledger alpha（`ARS_INQUIRY_LEDGER=1`），以及尚未实现、仅冻结设计的 alternative register。其行为证据保持 `NOT_RUN`，不声明可用性、恢复、创新性、正确性或研究结果收益。评审标准 registry 新增一组有来源支持、仅用于示范的 MSR 2027 exact-profile proving set；这不代表投稿期刊／会议与学科覆盖、真实作者 attest，也不是 constructive-review 证据，所需的独立人类评估仍未完成。其他变更包括对齐 `data_access_level`、合并 markdown lint 语法、登记 guard launcher 的降级路径，以及在不背书的前提下将 OrcaRouter 列为社区集成。套件／pipeline → v3.21.1；deep-research → v2.12.1；academic-paper → v3.3.1；academic-paper-reviewer → v1.11.1。

### v3.21.0（2026-08-18）— ISO/IEC 42001 精神轨：透明、可验证、可行

> **可被检验的透明：**v3.21.0 完成 ISO/IEC 42001 精神审计轨（#753–#760）。对外声明对齐证据记录，并新增四份常设文件回答用户真正想问的问题：你的安装渠道有哪些控制实际运作（`docs/CONTROL_AVAILABILITY.md`）、哪些数据离开你的机器与存放多久（`docs/DATA_FLOWS.md`）、每个 CI workflow 实际的强制力等级（`docs/ARCHITECTURE.md` §7.1）、每个机制对应哪个风险及其证据状态、残余缺口（`docs/RISK_REGISTER.md`），每份都由专属 CI lint 防漂移。`GOVERNANCE.md` 言明决策权限、cross-model 评审提供与不提供什么（error-detection control、非组织独立性）与 end-of-life 姿态；`SECURITY.md` 新增一人可运转的分级 triage 程序。这些是附 ISO/IEC 42001 信息性锚点的操作原则、不是认证声明，本版也不新增任何效果数字。套件／pipeline → v3.21.0；deep-research → v2.12.1；academic-paper → v3.3.1；academic-paper-reviewer → v1.11.1。
