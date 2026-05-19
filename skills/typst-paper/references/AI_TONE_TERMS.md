# AI Tone Terms (Bilingual, Typst) — Reference

Typst 模板被中英双语论文共用，本文件同时记录两套高频词表和触发说明。
配套阈值文件 `AI_TONE_THRESHOLDS.yaml` 是 `deai_check.py` 实际读取的权威配置。

## 阈值生效方式

- `deai_check.py` 启动时读取 `AI_TONE_THRESHOLDS.yaml`。
- `term_thresholds:` 中：
  - key 全部 ASCII 字母 → 按 word boundary 计数（大小写不敏感）。
  - key 含非 ASCII 字符 → 按 substring 直接计数。
- 每个超阈值的词触发一次 `[Script] LOW` 痕迹。
- 阈值仅在 yaml 中改；此 MD 仅为说明。

## English

| Word          | Threshold | Why it matters                                                  |
|---------------|-----------|------------------------------------------------------------------|
| significant   | 5         | Often hides missing effect size or p-value                       |
| comprehensive | 3         | Marketing language; rarely earned by a single study              |
| effective     | 5         | Cheap claim without baseline comparison                          |
| novel         | 4         | Reviewers discount the word unless the novelty is named          |
| robust        | 4         | Needs the perturbation / noise level that justifies the claim    |
| important     | 5         | Replace with what is at stake                                    |
| various       | 5         | Vague quantifier; usually fixable with a number                  |
| several       | 5         | Vague quantifier                                                 |
| numerous      | 3         | Vague quantifier                                                 |
| furthermore   | 3         | Padding connector                                                |
| moreover      | 3         | Padding connector                                                |
| notably       | 3         | Editorial framing                                                |
| obviously     | 3         | Over-confident hedge                                             |
| clearly       | 4         | Over-confident hedge                                             |

## 中文

| 词     | 阈值 | 备注                          |
|--------|------|--------------------------------|
| 首先   | 4    | 议论开头模板                  |
| 其次   | 4    | 与"首先"成对                  |
| 然而   | 5    | 转折滥用                      |
| 因此   | 6    | 可保留更多                    |
| 显然   | 3    | 越自然越不需要                |
| 显著   | 5    | 通常缺定量支撑                |
| 全面   | 3    | 单一研究难"全面"              |
| 深入   | 3    | 营销语言                      |
| 重要   | 5    | 解释清楚何为"重要"            |
| 关键   | 5    | 同上                          |
| 核心   | 4    | 一篇论文不该有太多"核心"      |

## Burstiness（段首重复）

连续 3 段以相同的前 8 个字符开头时触发。该 8 字符设定同时覆盖中英文：

- "Furtherm..." / "Furtherm..." / "Furtherm..."（英文）
- "首先，我..." / "首先，我..." / "首先，我..."（中文）

修复方法：把至少一段重写为不同的句法形态。

## Throat clearing（段首套话）

英文与中文段首套话各 10 条左右，命中即记一次 `[Script] LOW`。
完整列表见 `AI_TONE_THRESHOLDS.yaml`。

## Punctuation

- 全文 `—` / `---` 总数超过 `max_em_dashes_per_doc` → 在首次出现处记一次聚合痕迹。
- 正文章节中出现 `!` 或 `！` → 每次记一条痕迹。

## Out of scope

- 句法语法（由编辑器自检覆盖）。
- 引用密度（由 `verify_bib.py` 覆盖）。
- 章节结构（由 `check_format.py` 覆盖）。
- 受保护术语和数学环境（参见 SKILL.md / FORBIDDEN_TERMS.md 风格章节）。
