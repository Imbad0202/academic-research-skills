# 整稿验收协议

## 1. Hard gate 定义

中文学术文档交付前，**必须**同时满足下列三类硬指标：

### 1.1 排印指纹三重门控（CRITICAL）

| 指标 | 阈值 | 验证方式 |
|------|------|---------|
| 破折号 `——`（U+2014 双连）| **0** | grep `——` 全文 |
| 破折号 `—`（U+2014 单字符）| **0** | grep `—` 全文，扣除英文段落 |
| 日文 / 港台引号 `「」`（U+300C/U+300D）| **0** | per-paragraph check（仅在含 CJK 段落） |
| 日文 / 港台书名号 `『』`（U+300E/U+300F）| **0** | per-paragraph check |
| 直引号 `"` 在含中文字符的段落中 | **0** | per-paragraph check |

依据：

- 破折号：LLM 中文输出指纹（dizzy 2026-05-11 反馈）
- `「」` `『』`：国标 GB/T 15834-2011《标点符号用法》规定大陆出版物用 `“”` / `‘’`，不列 `「」`；LLM 中文输出大量出现，是另一种指纹
- 直引号 `"`：中文段落里出现直引号违反国标双引号规定，且通常由半角引号未规范化导致

### 1.2 结构指纹（MINOR / MAJOR）

| 指标 | 阈值 | 验证方式 |
|------|------|---------|
| 段首前 4 字连续 3 段重复 | **0** | burstiness check |
| 段首 throat-clearing 短语 | **0** | pattern match |
| 弯引号 `“”` 密度 | ≤ 16 对 / 千字 | per-document density |

### 1.3 例外与豁免

英文段落（如英文 Abstract、英文参考文献条目）中的破折号 `—` 与直引号 `"` 不计入。判定标准：段落中是否含 CJK 字符。

`「」` `『』` 在英文段落中也不会出现，所以判定逻辑不需要英文豁免。

排印指纹的 hard gate 不允许豁免。如果作者明确要求保留某处破折号或 `「」`（极少见，比如直接引用日文原文），作者必须手动批注 `<!-- aiwei-zh: keep -->` 标记，脚本会跳过该处但仍记一条 `[Judgment] OBSERVATION` 提示。

## 2. 整稿覆盖原则

**验收范围必须等于交付范围，不能等于润色范围**。

如果用户委托润色第 2 章，但最终交付的是包含第 1-5 章的全文 docx，验收对象是**整份 docx**，不是第 2 章。

具体动作：

1. 打开交付文件本身（不是润色时使用的中间文件），grep 全文。
2. 报告时按章节定位每个发现，让用户看到"未润色章节也有问题"。
3. 不能省略未润色章节的扫描，理由是"那不在我的工作范围"。验收的语义是"这份文件能不能交"，不是"我做的工作有没有错"。

## 3. 合并稿事故复盘（2026-05-17）

### 事件

dizzy（南大编辑出版学研究生）的硕士论文修订工作流：

1. 原稿（`00_原稿.docx`，96 段）保留有 101 处破折号，来自第一稿的写作习惯。
2. 我把第 2、4.3、5 章独立出来做四轮润色，产出 `04_文献回顾与结语_润色稿.docx`。这份润色稿在我新写/改的段落中破折号为 0。
3. 我把润色稿合并回原稿结构，产出 `05_全文_润色合并版.docx`。
4. 我宣布"验收通过，破折号 = 0"。
5. dizzy 当场指出：05 全文里有 101 个破折号没动。

### 失败原因

我把"润色范围 = 验收范围"。润色范围是 §2 / §4.3 / §5，验收时我只扫了这三个章节。§1、§3、§4.1-4.2、§4.4 的破折号是从 `00_原稿.docx` 继承过来的，**从未被检查**。

### 修复

立刻重新对全文做 grep `—`，找到 101 处，按 `EMDASH_PLAYBOOK.md` 全部替换，再 grep 确认 0。

### 教训

1. 整稿验收是单独的工序，不是润色的副产品。
2. "我只润色了 X" 不能作为"我只验收 X" 的借口。
3. **Hard gate 检查的对象是 final artifact，不是 work-in-progress**。
4. 此 skill 的 `gate` mode 就是为这个失败模式而设计。只要用户跑一次 `gate`，这类事故不会再发生。

## 4. Gate mode 标准执行流

```
1. Receive: 文件路径
2. Detect: 根据扩展名选解析器（.docx / .md / .tex / .typ / .txt）
3. Extract: 抽取全文可见正文（剥离引用、公式、注释、图表标签）
4. Check 1 (排印指纹 hard gate):
   - count 破折号 —— 和 — （扣除英文段落）
   - count 「」 和 『』 （扣除英文段落）
   - count 中文段落里的直引号 "
   - 若任一 > 0: 返回 FAIL，列出每一处的章节 + 段落 + 上下文 30 字
5. Check 2 (六维词频 + 引号密度，仅在 hard gate 通过后):
   - 走 HUANGFU_2026_FRAMEWORK.md 阈值
   - 超阈值 50%+ 记 MAJOR；30-50% 记 MINOR；阈值内 OBSERVATION
   - 弯引号 "" 密度 > 10/千字 记 MINOR，> 16/千字 记 MAJOR
6. Check 3 (结构告警):
   - burstiness、throat-clearing、完美对称
7. Return:
   - PASS / FAIL
   - 若 FAIL：每一处定位 + 建议替换标点（指向 EMDASH_PLAYBOOK.md 的对应模式编号）
   - 若 PASS：六维词频报告 + 结构告警
```

## 5. 与其它 skill 的协作

- **跟 `paper-audit`**：`paper-audit` 的 `gate` mode 关心的是"内容/方法/证据是否足以投稿"。本 skill 的 `gate` mode 关心的是"文本是否还有 AI 味痕迹"。两者正交，可以串联跑：`paper-audit --mode gate` 通过后，再跑 `aiwei-zh --mode gate` 做文本层最终验收。
- **跟 `latex-thesis-zh deai` 模块**：那个模块是基于词频阈值的扫描，本 skill 是其超集，加入了 hard gate、6 维框架、上下文敏感的破折号 playbook、整稿验收协议。`latex-thesis-zh deai` 仍可用于 LaTeX 源码的快速扫描，本 skill 用于交付前最终验收。

## 6. 自动化集成示例

CI 流水线中加入这一步：

```bash
# 在 docx 构建之后
uv run python aiwei-zh/scripts/scan_aiwei.py \
    --mode gate \
    --format json \
    build/output.docx > aiwei_report.json

# 任何 FAIL 退出非零，CI 会失败
if jq -e '.gate_result == "FAIL"' aiwei_report.json; then
    echo "AI 味 hard gate failed"
    jq '.findings[]' aiwei_report.json
    exit 1
fi
```

这样可以确保任何 push 出去的稿件都先过 hard gate。
