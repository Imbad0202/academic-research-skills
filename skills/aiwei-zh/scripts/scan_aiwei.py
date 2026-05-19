#!/usr/bin/env python3
"""aiwei-zh scanner — detect AI-tone markers in Chinese academic prose.

Implements the framework from 皇甫博媛 (2026) 《"AI 味"与"人机感"》, plus
em-dash hard gate and structural anti-patterns (burstiness, throat clearing,
perfect symmetry).

Supports input: .md / .txt / .tex / .typ / .docx
Modes: scan / gate / playbook

Run:
    uv run python scan_aiwei.py [--mode gate|scan|playbook] [--strict]
                                 [--format md|json] FILE
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path

# ---------------------------------------------------------------------------
# Configuration

# Aiwei marker thresholds: occurrences per 1000 visible Chinese characters.
# 0 means "no legitimate use in Chinese academic prose; flag every instance".
TERM_THRESHOLDS = {
    "程式化": 0,
    "模板化": 0,
    "模板": 0,
    "八股": 0,
    "堆砌": 0,
    "完美": 1,
    "全面": 2,
    "高效": 2,
    "结构化": 5,  # context-sensitive, see HUANGFU_2026_FRAMEWORK.md
    "形式化": 3,
    "死板": 1,
    "装模作样": 0,
    "不自然": 1,
    "模仿": 2,
    "面无表情": 0,
    "毫无激情": 0,
    "冷冰冰": 1,
    "空洞": 1,
    "毫无灵韵": 0,
    "违和": 1,
    "枯燥": 1,
    "粗糙": 1,
    "虚假": 1,
    "敷衍": 1,
    "诡异": 1,
    "尴尬": 1,
    "编造": 1,
}

STRICT_FACTOR = 0.7  # --strict shrinks thresholds by 30%

# Chinese curly-quote pair density thresholds (pairs per 1000 visible CJK chars)
# Background: 学术中文里引号只在首次引入术语 / 直接引用 / 表反讽时用。
# 把每个名词都拎出来打引号是 AI 写作的"术语标注 tic"，读起来居高临下。
QUOTE_PAIR_MINOR = 10  # warning threshold
QUOTE_PAIR_MAJOR = 16  # clear overuse threshold

THROAT_CLEARING_PATTERNS = [
    "综上所述",
    "总而言之",
    "总的来说",
    "由此可见",
    "值得指出的是",
    "值得注意的是",
    "需要指出的是",
    "需要说明的是",
    "不难发现",
    "不难看出",
    "众所周知",
    "毋庸讳言",
]

THROAT_CLEARING_PREFIXES = [
    "首先，",
    "其次，",
    "然而，",
    "此外，",
    "一方面，",
    "另一方面，",
]

# Severity codes
CRITICAL = "CRITICAL"
MAJOR = "MAJOR"
MINOR = "MINOR"
OBSERVATION = "OBSERVATION"


@dataclass
class Finding:
    kind: (
        str  # em_dash | term_freq | burstiness | throat_clearing | perfect_symmetry | quote_mixing
    )
    severity: str  # CRITICAL | MAJOR | MINOR | OBSERVATION
    source: str  # "[Script]" or "[Judgment]"
    location: str  # paragraph index or section reference
    description: str
    context: str = ""
    suggestion: str = ""


# ---------------------------------------------------------------------------
# Input parsers


def extract_paragraphs(path: Path) -> list[str]:
    """Return a list of paragraph strings (visible body text), per file format."""
    suffix = path.suffix.lower()
    if suffix in (".md", ".txt"):
        return _extract_markdown(path)
    if suffix == ".tex":
        return _extract_latex(path)
    if suffix == ".typ":
        return _extract_typst(path)
    if suffix == ".docx":
        return _extract_docx(path)
    raise ValueError(f"Unsupported file type: {suffix}")


def _extract_markdown(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    paras = []
    for block in re.split(r"\n\s*\n", text):
        block = block.strip()
        if not block:
            continue
        if block.startswith(">"):  # block quote / metadata
            continue
        if block.startswith("```"):  # code fence
            continue
        if block.startswith("---"):  # frontmatter separator
            continue
        # Strip leading heading marks but keep heading text for scanning
        block = re.sub(r"^#+\s*", "", block)
        paras.append(block)
    return paras


def _extract_latex(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    # Strip comments (% to end of line, unprefixed by backslash)
    text = re.sub(r"(?<!\\)%[^\n]*", "", text)
    # Strip math environments (rough)
    text = re.sub(r"\$[^$]*\$", " ", text)
    text = re.sub(r"\\begin\{equation\*?\}.*?\\end\{equation\*?\}", " ", text, flags=re.DOTALL)
    # Strip \cite{...} \ref{...} \label{...} contents
    text = re.sub(r"\\(cite|ref|label|eqref|autoref)\{[^}]*\}", " ", text)
    # Strip remaining \command{arg} but keep arg text where reasonable
    text = re.sub(r"\\[a-zA-Z]+\*?(\[[^\]]*\])?\{?", " ", text)
    text = text.replace("}", " ")
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    return paras


def _extract_typst(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    # Strip line comments and block comments
    text = re.sub(r"//[^\n]*", "", text)
    text = re.sub(r"/\*.*?\*/", "", text, flags=re.DOTALL)
    # Strip math $...$
    text = re.sub(r"\$[^$]*\$", " ", text)
    # Strip @cite anchors, labels <...>
    text = re.sub(r"@[\w:-]+", " ", text)
    text = re.sub(r"<[^>]+>", " ", text)
    paras = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    return paras


def _extract_docx(path: Path) -> list[str]:
    """Extract paragraph text from .docx, one entry per <w:p> element.

    Combines all <w:t> runs within a paragraph. Stays robust to multi-run
    formatting.
    """
    with zipfile.ZipFile(path) as zf, zf.open("word/document.xml") as f:
        xml = f.read().decode("utf-8")
    para_re = re.compile(r"<w:p\b[^>]*>(.*?)</w:p>", re.DOTALL)
    text_re = re.compile(r"<w:t[^>]*>([^<]*)</w:t>")
    paras = []
    for m in para_re.finditer(xml):
        body = m.group(1)
        runs = text_re.findall(body)
        joined = "".join(runs)
        if joined.strip():
            paras.append(joined)
    return paras


# ---------------------------------------------------------------------------
# Helpers


def has_chinese(s: str) -> bool:
    return any("一" <= c <= "鿿" for c in s)


def char_count_zh(s: str) -> int:
    return sum(1 for c in s if "一" <= c <= "鿿")


# ---------------------------------------------------------------------------
# Checks


def check_em_dashes(paras: list[str]) -> list[Finding]:
    findings = []
    for i, p in enumerate(paras):
        if not has_chinese(p):
            continue  # skip English-only paragraphs (Abstract, English refs)
        # Each em dash occurrence (paired ——  counts as 1 conceptual instance,
        # single — counts as 1; we report each U+2014 position).
        for m in re.finditer(r"—+", p):
            length = len(m.group(0))
            label = "——" if length >= 2 else "—"
            start = max(0, m.start() - 15)
            end = min(len(p), m.end() + 15)
            findings.append(
                Finding(
                    kind="em_dash",
                    severity=CRITICAL,
                    source="[Script]",
                    location=f"paragraph {i}",
                    description=f"破折号 {label} 在中文段落中出现",
                    context=f"...{p[start:end]}...",
                    suggestion="按 EMDASH_PLAYBOOK.md 的 7 种模式选择替换标点",
                )
            )
    return findings


def check_quote_mixing(paras: list[str]) -> list[Finding]:
    findings = []
    for i, p in enumerate(paras):
        if not has_chinese(p):
            continue
        if '"' in p:
            count = p.count('"')
            findings.append(
                Finding(
                    kind="quote_mixing",
                    severity=MAJOR,
                    source="[Script]",
                    location=f"paragraph {i}",
                    description=f'中文段落中出现 {count} 个直引号 "',
                    context=f"...{p[:60]}...",
                    suggestion="规范化为中文弯引号 “” ，注意左右配对",
                )
            )
    return findings


def check_corner_brackets(paras: list[str]) -> list[Finding]:
    """Detect 「」『』 (Japanese / Taiwan / HK convention) in mainland Chinese
    paragraphs. GB/T 15834-2011 specifies "" / '' for mainland publications;
    corner brackets are a regional / LLM-output fingerprint that doesn't fit
    mainland academic / publishing conventions.
    """
    findings = []
    for i, p in enumerate(paras):
        if not has_chinese(p):
            continue
        for m in re.finditer(r"[「」『』]", p):
            ch = m.group(0)
            start = max(0, m.start() - 15)
            end = min(len(p), m.end() + 15)
            findings.append(
                Finding(
                    kind="corner_bracket",
                    severity=CRITICAL,
                    source="[Script]",
                    location=f"paragraph {i}",
                    description=(
                        f'中文段落出现日文 / 港台体例引号 "{ch}"'
                        "（GB/T 15834-2011 规定大陆出版物用 “” / ‘’）"
                    ),
                    context=f"...{p[start:end]}...",
                    suggestion="改为 “” 或 ‘’ ，或直接删除（学术中文里术语只在首次引入时打引号）",
                )
            )
    return findings


def check_quote_density(paras: list[str]) -> list[Finding]:
    """Flag overuse of Chinese curly quotes "" pairs.

    Even with correct typography, wrapping every technical term in quotes is an
    AI writing tic that reads condescending (the writer doesn't trust the
    reader to recognize a term). Threshold counts left-quote U+201C as a
    proxy for pairs.
    """
    findings = []
    visible = "\n".join(p for p in paras if has_chinese(p))
    total_zh = char_count_zh(visible)
    if total_zh < 200:
        return findings  # too short to be meaningful
    pair_count = visible.count("“")  # U+201C left curly double quote
    per_k = total_zh / 1000.0
    density = pair_count / per_k
    if density > QUOTE_PAIR_MAJOR:
        sev = MAJOR
    elif density > QUOTE_PAIR_MINOR:
        sev = MINOR
    else:
        return findings
    findings.append(
        Finding(
            kind="quote_density",
            severity=sev,
            source="[Script]",
            location="document",
            description=(
                f"中文弯引号密度 {density:.1f} 对/千字 "
                f"（阈值 MINOR {QUOTE_PAIR_MINOR} / MAJOR {QUOTE_PAIR_MAJOR}）"
            ),
            suggestion=(
                "学术中文里引号只在首次引入术语 / 直接引用 / 表反讽时用。"
                "把每个名词都拎出来打引号读起来居高临下，删一些"
            ),
        )
    )
    return findings


def check_term_frequency(paras: list[str], strict: bool) -> list[Finding]:
    findings = []
    visible = "\n".join(paras)
    total_zh = char_count_zh(visible)
    per_k = max(total_zh / 1000.0, 0.001)
    factor = STRICT_FACTOR if strict else 1.0
    for term, threshold in TERM_THRESHOLDS.items():
        count = visible.count(term)
        if count == 0:
            continue
        density = count / per_k
        adjusted = threshold * factor
        if adjusted == 0:
            # zero-tolerance terms
            severity = CRITICAL if count >= 2 else MAJOR
            findings.append(
                Finding(
                    kind="term_freq",
                    severity=severity,
                    source="[Script]",
                    location="document",
                    description=f'零容忍词 "{term}" 出现 {count} 次（阈值 0）',
                    suggestion="检查每处是否可改写为具体描述",
                )
            )
            continue
        if density > adjusted * 1.5:
            sev = MAJOR
        elif density > adjusted:
            sev = MINOR
        else:
            sev = OBSERVATION
        if sev != OBSERVATION:
            findings.append(
                Finding(
                    kind="term_freq",
                    severity=sev,
                    source="[Script]",
                    location="document",
                    description=(
                        f'"{term}" 出现 {count} 次，密度 {density:.2f}/千字 （阈值 {adjusted:.2f}）'
                    ),
                    suggestion=(
                        "结构化等技术词在 Harness / 数据 / 工程语境合法，"
                        "见 HUANGFU_2026_FRAMEWORK.md 阈值表的语境说明"
                    ),
                )
            )
    return findings


def check_burstiness(paras: list[str]) -> list[Finding]:
    findings = []
    if len(paras) < 3:
        return findings
    for i in range(len(paras) - 2):
        prefixes = [p[:4] for p in paras[i : i + 3] if len(p) >= 4]
        if len(prefixes) < 3:
            continue
        if prefixes[0] == prefixes[1] == prefixes[2]:
            findings.append(
                Finding(
                    kind="burstiness",
                    severity=MINOR,
                    source="[Script]",
                    location=f"paragraphs {i}-{i + 2}",
                    description=f'连续 3 段以 "{prefixes[0]}" 开头',
                    suggestion="把至少一段改写为不同的句法形态",
                )
            )
    return findings


def check_throat_clearing(paras: list[str]) -> list[Finding]:
    findings = []
    for i, p in enumerate(paras):
        if not has_chinese(p):
            continue
        first_line = p.split("\n", 1)[0].strip()
        for pat in THROAT_CLEARING_PATTERNS:
            if first_line.startswith(pat):
                findings.append(
                    Finding(
                        kind="throat_clearing",
                        severity=MINOR,
                        source="[Script]",
                        location=f"paragraph {i}",
                        description=f'段首清嗓子 "{pat}"',
                        context=first_line[:50],
                        suggestion="删除清嗓子短语，直接陈述要点",
                    )
                )
                break
        for pat in THROAT_CLEARING_PREFIXES:
            if first_line.startswith(pat):
                findings.append(
                    Finding(
                        kind="throat_clearing",
                        severity=MINOR,
                        source="[Script]",
                        location=f"paragraph {i}",
                        description=f'段首过渡词 "{pat.rstrip("，")}" 开头',
                        context=first_line[:50],
                        suggestion="非必要时删除，AI 习惯用",
                    )
                )
                break
    return findings


def check_perfect_symmetry(paras: list[str]) -> list[Finding]:
    findings = []
    for i, p in enumerate(paras):
        if not has_chinese(p):
            continue
        colon_count = p.count("：")
        comma_ji_count = len(re.findall(r"，即", p))
        if colon_count >= 3:
            findings.append(
                Finding(
                    kind="perfect_symmetry",
                    severity=MINOR,
                    source="[Script]",
                    location=f"paragraph {i}",
                    description=f'段内出现 {colon_count} 个冒号 "X：Y" 结构',
                    suggestion="一段最多 2 个，超过则打散为其它句式",
                )
            )
        if comma_ji_count >= 3:
            findings.append(
                Finding(
                    kind="perfect_symmetry",
                    severity=MINOR,
                    source="[Script]",
                    location=f"paragraph {i}",
                    description=f'段内出现 {comma_ji_count} 个 "，即" 展开',
                    suggestion="一段最多 2 个，超过则改为句号或其它过渡",
                )
            )
    return findings


# ---------------------------------------------------------------------------
# Reporters


def report_markdown(findings: list[Finding], mode: str, gate_pass: bool) -> str:
    out = ["# aiwei-zh report", ""]
    out.append(f"**Mode**: {mode}  ")
    if mode == "gate":
        out.append(f"**Gate result**: {'PASS' if gate_pass else 'FAIL'}  ")
    out.append(f"**Findings**: {len(findings)}  ")
    out.append("")
    by_sev = {CRITICAL: [], MAJOR: [], MINOR: [], OBSERVATION: []}
    for f in findings:
        by_sev[f.severity].append(f)
    for sev in (CRITICAL, MAJOR, MINOR, OBSERVATION):
        items = by_sev[sev]
        if not items:
            continue
        out.append(f"## {sev} ({len(items)})")
        out.append("")
        for f in items:
            out.append(f"- `{f.source}` **{f.kind}** @ {f.location}: {f.description}")
            if f.context:
                out.append(f"  - context: `{f.context}`")
            if f.suggestion:
                out.append(f"  - suggest: {f.suggestion}")
        out.append("")
    return "\n".join(out)


def report_json(findings: list[Finding], mode: str, gate_pass: bool) -> str:
    return json.dumps(
        {
            "mode": mode,
            "gate_result": "PASS" if gate_pass else "FAIL",
            "findings_count": len(findings),
            "findings": [asdict(f) for f in findings],
        },
        ensure_ascii=False,
        indent=2,
    )


# ---------------------------------------------------------------------------
# Main


def run(path: Path, mode: str, strict: bool, fmt: str) -> tuple[str, bool]:
    paras = extract_paragraphs(path)

    em = check_em_dashes(paras)
    qm = check_quote_mixing(paras)
    cb = check_corner_brackets(paras)

    if mode == "gate":
        # Hard gate: em dash + straight quote in CJK + corner brackets must be 0
        gate_pass = len(em) == 0 and len(qm) == 0 and len(cb) == 0
        findings = em + qm + cb
        if gate_pass:
            findings += check_term_frequency(paras, strict)
            findings += check_quote_density(paras)
            findings += check_burstiness(paras)
            findings += check_throat_clearing(paras)
            findings += check_perfect_symmetry(paras)
    elif mode == "playbook":
        # Focus on em dashes + corner brackets with replacement guidance
        gate_pass = len(em) == 0 and len(cb) == 0
        findings = em + cb
    else:  # scan
        gate_pass = len(em) == 0 and len(cb) == 0
        findings = em + qm + cb + check_term_frequency(paras, strict)
        findings += check_quote_density(paras)
        findings += check_burstiness(paras) + check_throat_clearing(paras)
        findings += check_perfect_symmetry(paras)

    if fmt == "json":
        return report_json(findings, mode, gate_pass), gate_pass
    return report_markdown(findings, mode, gate_pass), gate_pass


def main():
    ap = argparse.ArgumentParser(description="aiwei-zh scanner")
    ap.add_argument("file", type=Path, help="path to .md/.txt/.tex/.typ/.docx")
    ap.add_argument("--mode", choices=["scan", "gate", "playbook"], default="scan")
    ap.add_argument("--strict", action="store_true", help="tighten term thresholds by 30%%")
    ap.add_argument("--format", choices=["md", "json"], default="md")
    args = ap.parse_args()

    if not args.file.exists():
        print(f"File not found: {args.file}", file=sys.stderr)
        sys.exit(2)

    output, gate_pass = run(args.file, args.mode, args.strict, args.format)
    print(output)

    if args.mode == "gate" and not gate_pass:
        sys.exit(1)


if __name__ == "__main__":
    main()
