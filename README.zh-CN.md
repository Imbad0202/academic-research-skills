# Academic Research Skills for Claude Code

[![Version](https://img.shields.io/badge/version-v3.24.0-blue)](https://github.com/Imbad0202/academic-research-skills/releases/tag/v3.24.0)
[![DOI](https://img.shields.io/badge/DOI-10.5281%2Fzenodo.20696614-blue)](https://doi.org/10.5281/zenodo.20696614)
[![License: CC BY-NC 4.0](https://img.shields.io/badge/license-CC%20BY--NC%204.0-lightgrey)](https://creativecommons.org/licenses/by-nc/4.0/)
[![Sponsor](https://img.shields.io/badge/sponsor-Buy%20Me%20a%20Coffee-orange?logo=buy-me-a-coffee)](https://buymeacoffee.com/crucify020v)

[English](README.md) | [繁體中文版](README.zh-TW.md) | [日本語版](README.ja-JP.md) | [한국어](README.ko-KR.md) | [Español](README.es-ES.md) | [Português](README.pt-BR.md)

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

**使用 Claude Science？** 五个 skill 可直接导入：**Skills → Import from GitHub**，粘贴 `https://github.com/Imbad0202/academic-research-skills`，点 **Preview**，再点 **Import**（需本 repo v3.14.0+——导入器读取 marketplace manifest 中显式声明的 skill 路径）。导入是一次性快照：ARS 更新后需重新导入。导入的 skill 承载 ARS 方法论（研究／写作／评审协议）；Claude Code 专属机制——slash commands、hooks、subagent 编排——不会转移。详见 [docs/SETUP.md](docs/SETUP.md) Method 5。

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
- **SR-Screener** — 系统综述、范围综述与快速综述的研究筛选，按用户确认的筛选规则执行：两位盲审 AI 审查者加第三位裁决者、按固定顺序的排除代码、不预设任何决定、可续跑的批次、质量检查（种子研究、近似排除复查、kappa 与 PABAK）、PRISMA 2020 数字、EndNote/Zotero RIS 分组，以及交给 `academic-paper` 的 `literature_corpus[]`。AI 的决定只是辅助，最终由研究团队核查。
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

#### SR-Screener（研究筛选，8 种模式）

```
"把我的计划书转成筛选规则"                    → protocol mode
"这篇摘要符合我的综述纳入条件吗？"            → quick mode（单一审查者初筛）
"先用种子研究试跑筛选"                        → pilot mode
"筛选这些数据库导出文件"                      → ta-screen mode
"筛选晋级记录的全文"                          → ft-screen mode
"裁决我 Rayyan 导出文件中的冲突"              → adjudicate mode
"帮我复查排除的记录"                          → audit mode
"给我这次筛选的 PRISMA 数字"                  → report mode
```

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

### Academic Pipeline (v3.24.0)

10 阶段调度器，含学术诚信验证、两阶段审查、苏格拉底指导、协作质量评估。Pipeline 规则（由 agent 按流程遵守，不是运行时保证）：每个阶段都需用户确认 checkpoint；学术诚信验证（Stage 2.5 + 4.5）为 MANDATORY 且没有不留记录的绕过路径（所有覆写都须记录用户理由、供 Stage 6 使用）；R&R 追溯矩阵（Schema 11）把每一项审查意见对应到作者的修订主张，并记录复审是否验证通过。v3.4 添加 Compliance Agent（PRISMA-trAIce + RAISE）于 Stage 2.5 / 4.5。v3.5 添加 **协作深度观察员**（`collaboration_depth_agent`，仅咨询性质、永不阻挡流程）于每一次 FULL/SLIM checkpoint 与 pipeline 完成时。MANDATORY 学术诚信闸门（2.5 / 4.5）明确跳过观察员，避免稀释合规检查。理论基础：Wang & Zhang (2026), IJETHE 23:11。逐阶段矩阵（agent、产出物、闸门）：见 ARCHITECTURE.md §3。

### SR-Screener (v1.0.0)

4 个 agent 的研究筛选，位于 `deep-research`（问题、计划书、检索）与 `academic-paper`（撰写综述）之间。模式：protocol、quick、pilot、ta-screen、ft-screen、adjudicate、audit、report。两位盲审的审查者 subagent（只能用 Read 与 Grep）按用户确认的筛选规则审每一条记录，第三位审查者裁决"晋级 vs. 排除"的冲突；只用标准库的 Python 脚本负责解析 RIS / PubMed .nbib / Web of Science / CSV 导出文件、去重、分批、合并，并产出筛选记录表、RIS 分组、PRISMA 2020 数字、含 `[TO COMPLETE]` 字段的方法段草稿，以及 `literature_corpus[]` 文件。Agent 遵守的规则（不是运行时保证）：用户确认筛选规则前不筛任何记录、失败的调用不会被当成默认"排除"、数字发表前由研究团队核查决定。详见 [`sr-screener/SKILL.md`](sr-screener/SKILL.md)。

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

### v3.24.0（2026-10-27）— 审查小组推荐文献与审查意见的参考检查、write-scope guard 启动器改为单一进程，以及诚信检查规则修复

> **两项审查参考检查与数项修复；没有新 skill，这两项检查在真实审查上的准确度尚未测量：**v3.24.0 在 Editorial Decision Letter 加上两份附件。第一份实时查询 Reviewer 2 与 Reviewer 3 推荐的每一篇著作，查询范围是引用验证关卡使用的四个索引，只报告有没有这条记录，不判断该著作是否支持推荐理由（#1001）。第二份把每一项 weakness，以及 Devil's Advocate 每一行 CRITICAL 或 MAJOR 意见，去掉审稿人席位标签后交给 session 模型的一个 subagent，由它判断稿件是否与该意见矛盾。只有判定者的引文通过脚本对稿件的比对检查，附件才列为矛盾；其他判定为错误的意见列为未确认（#1002）。这项检查默认开启，设置 `ARS_PANEL_CLAIM_CHECK=0` 可以关闭。两份附件都不影响审查决定、修订路线图或复审标准。第二项检查上线前，一项预注册的 held-out 审计检查了 805 条审查小组意见，估计错误意见的比例介于 1.5% 到 12.9%；Claude Opus 5.5 与 Claude Fable 5.1 担任判定者时都通过了它的对照关卡。write-scope guard 的启动器每次工具调用只启动一个 Python 进程，原来是三个，Windows 上 AppXSvc 的内存泄漏预计因此降为原来的三分之一左右，但 Windows 上的实际行为尚未测试（#1015）；guard 的代码注释也写明它检查哪些工具名称（#1022）。三条诚信检查规则在 Stage 5 入口、报告有效期限与 Stage 4′ 三点上取得一致（#1011），启动通知也改为只在有新版本时显示（#1027）。#1015、#1022 与 #1027 由外部用户报告。

### v3.23.2（2026-10-24）— 诚信检查只读引用的版本、Stage 2.5 一律执行，以及适配器、启动通知与 Windows 修复

> **修复；没有新 skill。一项提示层变更做了小规模行为检查，其余尚未测量：**v3.23.2 让 Stage 2.5 与 4.5 的声明核查只拿稿件引用的那个版本来比对（#1006）。读不到引用的版本时，核查会记录一条访问备注并请用户提供 PDF，不再改读工作论文或预印本。在一份合成测试稿上运行六次（Claude Opus 5.5 与 Claude Fable 5.1 各三次，关闭网络工具），六次都遵守这条规则。先前的诚信报告不再能让 pipeline 跳过 Stage 2.5，改为附上作为参考（#995）。缺少必要输入时，每一份规则文件都会阻止阶段转换（#990）；苏格拉底导师的示例不再为用户的想法排名（#992）。SessionStart 启动通知会把更新提醒显示给用户，给模型看的启动内容约减少 2.1 KB（#999）。Obsidian 适配器接受未加引号的 ISO 日期年份，并拒绝布尔值与上标数字年份（#988、#989）；六个 lint 在 Windows 上改用 POSIX 形式比较路径（#964、#978）；Pi 包装器改为与 Pi 的结构化提示区段组合（#985）；`CITATION.cff` 加上作者的 ORCID iD（#1007）。#978、#985、#988 由外部贡献者提供。

### v3.23.1（2026-10-16）— write-scope guard 修复、sr-screener 按 RFC 4180 读取 CSV、模型现况对齐（Gemini 4 Argon）

> **修复与模型现况对齐；没有新 skill，也不宣称任何准确度或性能提升：**v3.23.1 补上 write-scope guard 两条未经检查就放行写入的路径，一条出现在 plugin 派发的 agent，一条出现在 Windows 内置的 `timeout.exe`（#972），文档也改为说明防护实际在哪些情况下启用（#974）。`sr-screener` 改按 RFC 4180 的引号规则读取 CSV 导出文件，不再使用从样本推测的引号规则（#979）。Gemini 4 Argon 以 provisional 身份列入，并成为推荐的 Google 验证模型；`gemini-3.1-pro-preview` 保持 validated（#980）。路由核心写明：消息中段出现的 `[direct-mode]` 标记不是跳出机制（#892）；在 plugin 安装环境的冒烟测试中，Claude Fable 5.1 修改后仍有 6 次中 3 次遵从该标记（修改前 6 次中 6 次），未达到验收标准，#892 仍未关闭。另有数项由外部贡献者提供的 lint 与 Windows 修复（#956、#963、#965、#977），`THIRD_PARTY.md` 也列入 md-to-word（#969）。
