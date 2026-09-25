# Academic Research Skills for Claude Code

[![Version](https://img.shields.io/badge/version-v3.22.2-blue)](https://github.com/Imbad0202/academic-research-skills/releases/tag/v3.22.2)
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

> **AI 是你的副驾驶，不是机长。** 它可以起草文字，full mode 甚至会起草整篇论文；但决定权在你，pipeline 每个阶段都会停下来等你确认。它处理繁琐工作（搜文献、排格式、验数据、查逻辑一致性），让你专注在真正需要思考的事上：定义问题、选择方法、解读数据意义、决定「我认为」后面要接什么。作者是你，提交的每一个主张都由你负责。
>
> 和 humanizer 不同，这个工具不是帮你隐藏使用 AI 协作的事实，而是帮你把关文章质量。风格校准会从你过去的文章中学习你的声音，写作质量检查会识别让文字读起来像机器生成的模式。目标是质量，不是掩饰。

### 为什么选「人机协作」而不是「全自动」？

Lu 等人（2026，*Nature* 651:914-919）发表的 **The AI Scientist** 是第一个端到端全自动的 AI 研究系统，其生成的论文通过 ICLR 2025 workshop 的盲审（评分 6.33/10，workshop 平均 4.87）。他们自己的 Limitations 段落也列出了这类系统会遇到的结构性失败模式：实现错误、幻觉实验结果、取巧特征依赖、实现错误被包装成「意外发现」、方法论伪造、框架锁定、引用幻觉。

ARS 建立在这个前提上：**人类研究者 + AI 的组合，比纯自动或纯人工更能避开这些失败模式**。Stage 2.5 与 Stage 4.5 学术诚信闸门运行 7 类阻断式检查清单（见 [`academic-pipeline/references/ai_research_failure_modes.md`](academic-pipeline/references/ai_research_failure_modes.md)），reviewer 也提供 opt-in 的 calibration mode 用用户提供的 gold set 测量 FNR/FPR。

[**Zhao 等人**](https://arxiv.org/abs/2605.07723)（2026-05）盘点了 arXiv、bioRxiv、SSRN、PMC 上 250 万篇论文中的 1.11 亿条引用，保守估计 2025 年单年就有 146,932 条幻觉引用，并观察到 2024 年中是上升的拐点；bioRxiv-to-PMC 这条配对的「预印本进入正式发表版本」幻觉存活率达 85.3%。他们把「真实引用被用来支撑被引文献其实没有提出的主张」描述为当前未解的问题。ARS v3.7.1 为来源 provenance 加上 trust-chain frontmatter，v3.7.3 为未来的 claim-level 审计铺设 locator 基础设施（三层引用 anchor），并在引用阶段呈现 advisory 风险信号（ARS 内部把这条 claim-faithfulness 缺口标记为「L3」，此为 ARS 的用词，不是论文的用词）。v3.7.x 的设计动机来自 Zhao 等人的 corpus-scale 发现；ARS 本身的 corpus-scale 评估仍是未来工作。

v3.8 补上 L3 缺口的另一半。v3.7.3 让每一条引用都带 locator anchor，v3.8 在这个基础上加一道 opt-in 审计（`ARS_CLAIM_AUDIT=1`）：获取每个 anchor 指向的原始文本，判断论文里的 claim 是否真有被该引用支撑。五类新的 HIGH-WARN annotation（claim-not-supported、negative-constraint-violation、fabricated-reference、anchorless、constraint-violation-uncited）会在 formatter terminal hard gate 直接阻止输出。Calibration runner 随 release 附一组 25 条的合成 gold set，采用 FNR<0.15、FPR<0.10 双阈值。随附的测试使用直接返回标准答案的替身裁判，所以它验证的是工具本身，不是真正的 AI 裁判；目前还没有真实裁判的 calibration 结果，正式放大投入要等这份证据（v3.8 spec §5）。

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

**👉 [docs/PERFORMANCE.md](docs/PERFORMANCE.md)** — 各模式 token 预算、完整 pipeline 估算（一篇 15k 字论文，按 2026-09 牌价约 US$3–7，未计 cache 折扣），以及建议的 Claude Code 设置（Auto 模式；Agent Team 选用）。

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

查看一次完整 pipeline 运行的实际产出，包含**同行评审报告、学术诚信验证报告、完稿论文**：

> **这是 2026 年 3 月的记录，不代表现在的表现。** 这次运行（2026-03-07 至 03-08）使用的是 academic-pipeline v2.3，当时 ARS 还没有在 v3.3 加入 Semantic Scholar 核对，也还没有在 v3.11 加入确定性的四索引引用闸门。这里的数字描述的是那个版本，现行闸门还没有在这篇论文上测量过。作者栏写 Claude（Anthropic），是因为研究者在这次实验中这样要求。这篇论文不是 Anthropic 的出版物；ARS 的定位是工具不取代研究者，也不主张作者身份（见 [POSITIONING.md](POSITIONING.md#what-this-is-not)）。

**[浏览所有 pipeline 产出 →](examples/showcase/)**

| 产出物 | 说明 |
|---|---|
| [完稿论文（英文）](examples/showcase/full_paper_apa7.pdf) | APA 7.0 格式，LaTeX 编译 |
| [完稿论文（中文）](examples/showcase/full_paper_zh_apa7.pdf) | 中文版，APA 7.0 |
| [学术诚信报告 — 审稿前](examples/showcase/integrity_report_stage2.5.pdf) | Stage 2.5：标出 15 条有问题的引用（8 条书目错误、6–8 条疑似虚构）+ 3 个统计错误 |
| [学术诚信报告 — 最终](examples/showcase/integrity_report_stage4.5.pdf) | Stage 4.5：确认零回归 |
| [同行评审第一轮](examples/showcase/stage3_review_report.pdf) | Journal-Fit Reviewer + 3 审查者 + 魔鬼代言人 |
| [再审](examples/showcase/stage3prime_rereview_report.pdf) | 修订后验证审查 |
| [同行评审第二轮](examples/showcase/stage3_review_report_r2.pdf) | 跟踪审查 |
| [回复审查意见](examples/showcase/response_to_reviewers_r2.pdf) | 逐点回复 |
| [出版后审计报告](examples/showcase/post_publication_audit_2026-03-09.pdf) | 另行用 Claude Code + WebSearch 审计全部引用：经过 3 轮学术诚信审查后，最后 68 条引用中仍有 21 条有问题 |

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

### Academic Pipeline (v3.22.2)

10 阶段调度器，含学术诚信验证、两阶段审查、苏格拉底指导、协作质量评估。Pipeline 规则（由 agent 按流程遵守，不是运行时保证）：每个阶段都需用户确认 checkpoint；学术诚信验证（Stage 2.5 + 4.5）为 MANDATORY 且没有不留记录的绕过路径（所有覆写都须记录用户理由、供 Stage 6 使用）；R&R 追溯矩阵（Schema 11）把每一项审查意见对应到作者的修订主张，并记录复审是否验证通过。v3.4 添加 Compliance Agent（PRISMA-trAIce + RAISE）于 Stage 2.5 / 4.5。v3.5 添加 **协作深度观察员**（`collaboration_depth_agent`，仅咨询性质、永不阻挡流程）于每一次 FULL/SLIM checkpoint 与 pipeline 完成时。MANDATORY 学术诚信闸门（2.5 / 4.5）明确跳过观察员，避免稀释合规检查。理论基础：Wang & Zhang (2026), IJETHE 23:11。逐阶段矩阵（agent、产出物、闸门）：见 ARCHITECTURE.md §3。

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

### v3.22.2（2026-09-25）— 运行记录与交接检查、缩写检查、扩大 instruction/data 边界，以及路由与首页修复

> **两个确定性检查由合成测试固定；提示层变更的效果尚未测量：**v3.22.2 新增运行记录（#887）。pipeline 有 passport 文件时，orchestrator 会把用户的初始指示、每个 checkpoint 的提问与用户原话的回答、步骤回执与文件哈希，追加到 passport 旁的本地记录文件。发生 compaction、续跑或 subagent 返回之后，`scripts/run_ledger.py report` 会比对记录与摘要或报告的声明，列出差异；现在它会自己以英文或繁体中文打印这份交接检查，并在写入记录时计算该条记录所指文件的哈希（#898）。记录文件保存用户的原话，`docs/DATA_FLOWS.md` 列出这个文件与删除方式。本版也新增 `scripts/check_acronyms.py`（#849，由 @reiropke 提议），不调用模型，报告未定义、先用后定义或重复定义的缩写；提示会让调用方在保存好的草稿与摘要上运行它，审稿时则把报告附在 Editorial Decision Letter 最后，作为参考附件，审稿决定、修订路线图与复审准则都不引用它。两个脚本都由合成测试固定；实际运行时是否写入记录、是否调用检查，尚未测量。instruction/data 边界现在覆盖派工与 passport 导入中的第三方文字（#890）、接收端通过自己的工具调用读到的文字，以及每个 skill 的主 session（#894）；lint 固定每一份副本，效果尚未测量（可选的 claim-audit 裁判提示也随之改变，旧提示的缓存判定不再沿用）。修复：路由核心现在也送达 plugin 与 skills 复制安装（#892）；模式惯用的输入缺失时，明确的请求仍视为明确（#889）；`/ars-lit-review` 不再把进行中的运行导向别的流程（#897）；修订教练不再把同行评审导入委员会往来变体（#854）；orchestrator 把「权威」skill 输出限定为交付物的归属（#888）；首页与 showcase 的说法与来源一致（#908）。路由结果来自每个 fixture 一个 session，只是初步验证，不代表比率。新增一个描述记录文件的 schema；没有任何既有 schema、指令模型或推理强度设置的变更。

### v3.22.1（2026-09-23）— 模型现况对齐（Opus 5.5）、引用检查加载与中文 APA 7 修复、Pi 包装器修正

> **模型现况对齐与修复，新增提示层防线的效果尚未测量：**v3.22.1 在两个模型各自通读 Opus 5.5 system card 的审计之后，把 Claude Opus 5.5 与 Claude Fable 5.1 并列为受支持的 session 模型，审计没有退役任何防护（#883）。文档新增推理强度建议（Claude Code 让 Opus 5.5 以 `medium` 起步，重度任务应使用 `high` 及以上）、两个模型共用的一段标价换算，以及分层说明：阶梯顺序是厂商的产品排序，不是能力排序。card 指出 Opus 5.5 比先前的模型更常照做粘贴文字里的指令，因此修订教练现在把粘贴的审稿与委员会文字当作数据处理，并由 lint 固定；这道提示层防线的效果尚未测量。本版也修复模式加载与引用检查：13 个 plugin 模式命令直接调用其命名空间下的核心 skill，并从 plugin 根目录解析附带的参考文件，恢复引用检查的加载（#857）；中文 APA 7 检查会找出正文缺少的作者简称，保留歧义例外与完整的参考文献作者字段，只在有笔画排序颠倒的证据时才建议重排（#882）；引用检查整体也把可见的语法错误与未经核实的解析或来源声明分开（#882）；新增的英文、繁体中文与韩文触发词会把请求引导到引用检查，CI 也把每份 skill 描述限制在 1,024 个 code point 以内（#858、#864）。Pi 包装器可接受字符串数组形式的 system prompt（#880）。没有任何 schema、命令模型或推理强度设置的变更。

### v3.22.0（2026-09-16）— 输出语言对契约、语系轨、plugin eval 套件与 Windows／传输修复

> **加的是结构，证据保持有界：**v3.22.0 让一次运行可以通过注册表键控的 Schema 4 字段声明输出语言对，字段缺席时旧有文件逐字重现（#862 Phase 1、PR #869），并围绕它建立语系轨：@didacrios 贡献的 es-ES README 与保守的触发词、社区维护的语系包政策，以及单一 owner 的暂定申请路径。两套 `claude plugin eval` 套件（revision-coach、citation-check）与 reviewer-calibration harness 仅作为回归防线与派发基底发布，均不声称测得的提升或校准值。修复：`/ars-mark-read` 与其余五个锁点通过一个共用的 `msvcrt` 后端在 Windows 可用、OpenAI 请求不再发送 GPT-6 Astra 拒收的参数、受限的 Codex 传输拒绝 `effort=ultra`、审计来源记录实际的裁判身份、苏格拉底路径 F6 不再预选方向、无来源支撑的声明不能再靠 hedge 过关。README 只保留最近三版；Gartenberg 等人与 Wang、Li 等人加入 human-in-the-loop 锚点。Roadmap Phase 4（阶段级证据上限）本版未交付，窗口顺延。
