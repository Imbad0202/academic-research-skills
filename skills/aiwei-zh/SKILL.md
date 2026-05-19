---
name: aiwei-zh
description: 检测并清除中文学术写作中的 AI 味（机器写作痕迹），基于皇甫博媛 2026《"AI 味"与"人机感"》的六维框架（语言表达 / 个性 / 行为方式 / 情感与共情 / 灵韵 / 真实性）。提供三类排印指纹的 hard gate：破折号 ——/— 必须为 0、日文港台引号 「」『』 必须为 0、中文段落直引号 " 必须为 0；再加上下文敏感的破折号替换 playbook、引号密度阈值告警、AI 味词频扫描、整份文档验收协议。支持 .md .txt .tex .typ .docx 输入。当用户说"去 AI 味"、"读起来像 AI 写的"、"破折号太多"、"引号太密"、"全文扫一下"、"答辩稿/投稿前最后清一遍"、"人机感"、"活人感"、"瑕疵感"、"模板化"、"程式化"、"八股"、"堆砌"、"完美对称"等时触发。也用于跨章节合并、章节嫁接、续写后必经的整稿验收。Do not use for typesetting, citation formatting, or non-Chinese text editing (use latex-paper-en / latex-thesis-zh for those).
metadata:
  category: academic-writing
  tags: [chinese, deai, ai-tone, polish, audit, gate, em-dash, huangfu-2026, docx, markdown, latex, typst]
  version: "1.0"
  last_updated: "2026-05-17"
argument-hint: "[file.md|file.docx|file.tex|file.typ] [--mode scan|gate|playbook] [--strict] [--format md|json]"
allowed-tools: Read, Glob, Grep, Bash(uv *), Bash(python3 *)
---

# AI 味检测与清除（中文学术写作）

`aiwei-zh` 解决一个具体的失败模式：中文学术稿件读起来"像 AI 写的"，让作者、编辑、答辩老师本能反感。这个 skill 基于皇甫博媛在 2026 年《新闻与写作》第 3 期发表的实证研究，把"AI 味"操作化为六维可识别、可量化、可清除的标记。

它不是另一个语法检查器。它的核心是三件事：

1. **三重 hard gate**：任何交付的中文学术文档必须同时满足：破折号 `——` `—` = 0、日文港台引号 `「」` `『』` = 0、中文段落里的直引号 `"` = 0。无破折号、无 `「」`、无直引号是 must-have，不是 nice-to-have。
2. **六维扫描 + 引号密度告警**：按论文识别的六个 AI 味维度定位词频热点；额外检测中文弯引号 `“”` 的密度，超阈值即告警（即使用了正确的国标引号，密度过高本身也是 AI 写作的 tic）。
3. **整稿验收**：润色范围 ≠ 验收范围。任何合并、嫁接、续写、章节替换之后，验收对象是整份文档，不是被改的段落。

## Why This Skill Exists

中文学术写作中，AI 味问题不能由通用语法检查覆盖。皇甫博媛通过 1084 条社交媒体话语的实证编码发现，用户感知到的 AI 味集中在六个维度的特定关键词上（详见 `references/HUANGFU_2026_FRAMEWORK.md`）。这些标记单独看都不算错，但密度过高就让中文读者本能觉得不是活人写的。

除了词汇维度，还有**排印指纹**这一族（详见 `references/CHINESE_TYPOGRAPHY_FINGERPRINT.md`）：

- **破折号 `——`** 是最显眼的：它把 `X——Y（其展开）` 做成机械可复制的解释模板，是结构化 / 程式化家族的典型样本。LLM 大量参与写作之前，中文学术稿里的破折号密度远低于 LLM 输出。
- **`「」` `『』`** 是日文 / 港台繁体的体例，国标 GB/T 15834-2011 规定大陆出版物用 `“”` / `‘’`，根本不列 `「」`。LLM 中文输出大量出 `「」`，跟训练数据里日文 / 繁体权重相关。大陆读者一眼识别为 AI 写的。
- **`""` 密度过高** 即使用了正确的国标引号，把每个技术词都框起来本身就是 AI 写作的 tic。学术中文里引号只在首次引入术语 / 直接引用 / 表反讽时用，多数 `"X"` 应该直接写成 `X`。

这三类都属于"中文 AI 排印指纹"，是非词法层面的、外形上一打照面就出戏的标记。

## Capability Summary

- 扫描中文文档的破折号、`「」`、直引号、AI 味高频词、段首重复、堆砌排比、过度对称结构、引号密度
- 把破折号按上下文分类，提供 7 种替换模式的 playbook，避免一律换成冒号造成新模板
- 提供 hard-gate 验收协议：整稿（非段落）扫描，破折号 + `「」` + 中文段落直引号都为 0 才放行
- 支持 `.md` `.txt` `.tex` `.typ` `.docx` 输入
- 给出可执行的 diff/suggestion 块，区分 `[Script]`（机械确定）与 `[Judgment]`（需要人工裁决）

## Modes

| Mode | When to use | Output |
|------|------------|--------|
| `scan` | 想看全文 AI 味分布 | 按六维 + 破折号的频次报告，定位热点段落 |
| `gate` | 答辩 / 投稿 / 合并稿交付前的最后一步 | PASS / FAIL，破折号 ≠ 0 即 FAIL，无回旋余地 |
| `playbook` | 已识别出破折号，想知道每个怎么替换 | 按 7 种模式分类，给出对应替换建议 |

## Required Inputs

- 中文学术文档路径（`.md` / `.txt` / `.tex` / `.typ` / `.docx`）。
- 可选 `--strict`：把六维词频阈值收紧 30%，用于高规格稿件。

## Output Contract

- 默认 Markdown 格式报告，每条发现标 `[Script]` 或 `[Judgment]`、严重度（CRITICAL / MAJOR / MINOR / OBSERVATION）、定位（章节 / 段落 / 行号）。
- 破折号发现一律 `[Script] CRITICAL`，因为这是 hard gate。
- 六维词频发现按密度分级：超阈值 50% 以上 = MAJOR；30-50% = MINOR；阈值内 = OBSERVATION。
- `--format json` 输出结构化 JSON，便于自动化流水线接入。

## Workflow

1. Parse 输入文件路径，根据扩展名走对应的解析器（docx 走 zip + XML 抽取，tex/typ 复用 `latex-thesis-zh` / `typst-paper` 的 parsers，md/txt 直接读）。
2. 走对应 mode：
   - `scan`：跑 `scripts/scan_aiwei.py`，输出六维 + 破折号的全文报告。
   - `gate`：跑同一个脚本，但只取破折号项，破折号 ≠ 0 即返回 FAIL 并列出每一处定位；破折号 = 0 才检查六维词频，全部在阈值内则 PASS。
   - `playbook`：先 `scan` 找出所有破折号，再按 `references/EMDASH_PLAYBOOK.md` 的 7 种模式分类，对每一处给出建议替换。
3. 报告必须按 `references/VERIFICATION_PROTOCOL.md` 第 2 节规定的"整稿覆盖"原则——所有章节都扫，不能只扫 changed sections。

## Critical Rules

- **三重 hard gate**：润色完成的判定不取决于段落数、字数变化、关键词命中率，只取决于三件事是否同时为 0：破折号 `——`/`—`、日文港台引号 `「」`/`『』`、中文段落里的直引号 `"`。这条规则不可与作者协商豁免。
- **润色范围 ≠ 验收范围**：用户只让你润色第 2 章不代表只验第 2 章。任何整稿交付物（包括合并稿、嫁接稿、续写稿）必须对全文 grep。这是从一个具体失败案例里总结出来的硬规则（详见 `references/VERIFICATION_PROTOCOL.md` 第 3 节）。
- **不要一律把破折号换成冒号**：替换本身就是改写决策。一律冒号会造出新的 `X：Y` 模板，落入论文里结构化 / 程式化的另一种 AI 味。`references/EMDASH_PLAYBOOK.md` 列出 7 种模式，每种对应不同的替换标点（冒号 / 句号 / 逗号 / 即 / 圆括号 / 顿号 / 重写），需要按上下文选。
- **`「」` 替换前先问：要不要保留引号**：很多 `「术语」` 在大陆中文里直接写成 `术语` 就够了；改成 `"术语"` 只是把日文体例换成国标体例，没解决"引号过密"的根本问题。先看密度告警，密度高就一并删，密度低再按形改。
- **保留瑕疵**：皇甫博媛论文最深的洞察是用户偏爱带有瑕疵的活人感。润色不是把所有句子都修整齐。三联排比里故意让一条不对称、长短句故意混合、个别口语化连接词保留，都是反 AI 味的工程实践。
- **结构化等技术词在专业语境里要保留**：六维框架里的"结构化"在 AI 味语境是负面词，但在 Harness / 工程 / 数据科学语境是中性技术术语。脚本只标频次，最终判断必须看上下文。
- **不在 `\cite{}` `\ref{}` `<label>` 等保护区域内动手**：与本仓库其它 skill 一致，引用 / 标签 / 公式 / 代码块永不被修改。
- **不捏造作者意图**：发现模板化句子时，可以建议改写方向，但不能假定作者本意。`[Judgment]` 类发现必须等用户裁决。

## Safety Boundaries

- 在 `--strict` 模式下也不会自动改写文本。所有替换建议默认以 diff 形式呈现，由用户决定是否采纳。
- 英文段落（如英文 Abstract、英文参考文献条目）中的破折号 `—` 与直引号 `"` 不被本 skill 处理——它们符合英文体例，不是 AI 味问题。判定标准：段落中是否含 CJK 字符。
- 对 `.docx`：默认只读取并扫描，不直接写回原文档。需要写回时必须用户显式确认目标文件名（避免覆盖原稿）。

## Reference Map

- `references/HUANGFU_2026_FRAMEWORK.md` — 皇甫博媛六维 AI 味框架的完整词表、阈值建议、引用出处。
- `references/CHINESE_TYPOGRAPHY_FINGERPRINT.md` — 中文 AI 排印指纹三类（破折号、`「」`、引号密度），含 GB/T 15834-2011 体例依据与修复优先级。
- `references/EMDASH_PLAYBOOK.md` — 破折号 7 种上下文模式 → 替换标点的决策表，含正反例。
- `references/VERIFICATION_PROTOCOL.md` — 整稿验收协议、三重 hard gate 定义、合并稿失败案例复盘。

只在执行对应 mode 时按需加载，不一次性全读。

## 与现有 skill 的关系

| 场景 | 使用哪个 skill |
|------|--------------|
| 写中文学位论文 LaTeX，编译 + 国标 + 章节检查 | `latex-thesis-zh`（其 `deai` 模块是上一代实现，本 skill 是其超集 + 扩展到 .docx） |
| 写英文会议/期刊论文 LaTeX | `latex-paper-en` |
| 投稿前多角度审稿 | `paper-audit` |
| 已写完中文稿件，去 AI 味 / 答辩前最后清一遍 | **本 skill** |
| 已合并多章节 / 嫁接修订段落 / 续写章节 | **本 skill 的 `gate` mode**（用于验收，避免本仓库历史上出现过的"只验润色段、忽略全文"事故） |

## Example Requests

- "帮我把这份答辩稿的 AI 味清一下，重点是破折号"
- "全文扫一下有没有像 AI 写的地方"
- "合并完了，跑一次 gate 确认能交"
- "这段读着像 AI 八股，怎么改"
- "破折号太多了，每个该怎么换"
- "按皇甫博媛那个框架给我个 AI 味报告"

## Example Workflows

**用户问**："我刚把 §2 的润色稿合并回全文，能跑一次最终检查吗？"

**正确执行流**：
1. 路由到 `gate` mode（关键词："合并完"+"最终检查"）。
2. 加载 `references/VERIFICATION_PROTOCOL.md`，注意第 3 节"合并稿事故复盘"。
3. 跑 `scripts/scan_aiwei.py --mode gate path/to/全文合并稿.docx`。
4. 若破折号 ≠ 0：返回 FAIL，输出每一处定位，告知用户哪些段落继承自未润色章节。
5. 若破折号 = 0：进入第二步检查六维词频，若全部在阈值内返回 PASS。
6. 不要省略第 4 步的定位输出——它是用户决定下一步行动的依据。
