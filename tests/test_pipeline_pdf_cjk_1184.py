"""Pin Stage 5 PDF fallback and non-APA CJK font guidance (#1184 items 16–18)."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
PIPELINE = ROOT / "academic-pipeline" / "SKILL.md"
PROTOCOL = (
    ROOT / "academic-pipeline" / "references" / "process_summary_protocol.md"
)
AUDIT = ROOT / "academic-pipeline" / "references" / "reproducibility_audit.md"
TEMPLATE = (
    ROOT / "academic-paper" / "references" / "latex_template_reference.md"
)

FORMATTER_SECTION = "Chinese LaTeX Compilation Settings"
PROTOCOL_PATH = "../../academic-paper/agents/formatter_agent.md"
TEMPLATE_PATH = "../agents/formatter_agent.md"
OLD_STAGE5_CLAUSE = "say so instead of substituting another route"
OLD_FONT = "Source Han Serif TC VF"
PROCESS_RECORD_COMPILE_RULE = (
    "Use tectonic when installed; otherwise run xelatex twice on the same "
    "generated record .tex file so the table of contents resolves."
)

BASIC_CJK_COMMENT = (
    "% Only if the paper contains CJK text, choose an installed main font "
    "for the target OS\n"
    "% and an installed sans font for the target OS, then uncomment all "
    "three lines.\n"
    "% Replace <installed font> and <installed sans font> with those fonts\n"
    '% from "Chinese LaTeX Compilation Settings" in ../agents/formatter_agent.md.\n'
    "% \\usepackage{xeCJK}\n"
    "% \\setCJKmainfont{<installed font>}\n"
    "% \\setCJKsansfont{<installed sans font>}"
)
XELATEX_INTRO = (
    "For zh-TW content, replace `<installed font>` below with an installed "
    "main font for the target OS and `<installed sans font>` with an "
    "installed sans font for the target OS from “Chinese LaTeX Compilation "
    f"Settings” in `{TEMPLATE_PATH}`."
)
PANDOC_INTRO = (
    "Replace `<installed font>` with an installed main font for the target "
    "OS from “Chinese LaTeX Compilation Settings” "
    f"in `{TEMPLATE_PATH}`."
)


def _between(text: str, start: str, end: str) -> str:
    if start not in text:
        raise AssertionError(f"missing start marker: {start!r}")
    tail = text.split(start, 1)[1]
    if end not in tail:
        raise AssertionError(f"missing end marker: {end!r}")
    return tail.split(end, 1)[0]


def _stage5_output_bullet(text: str) -> str:
    block = _between(
        text,
        "Stage 5: academic-paper (format-convert mode)\n",
        "\n```",
    )
    bullets = [
        line
        for line in block.splitlines()
        if line.startswith("  - Then the Stage 5 output process")
    ]
    assert len(bullets) == 1
    return bullets[0]


def test_stage5_output_follows_formatter_pdf_route() -> None:
    """Stage 5 confirms content, then uses tectonic or XeLaTeX from paper.tex."""
    bullet = _stage5_output_bullet(PIPELINE.read_text(encoding="utf-8"))
    assert OLD_STAGE5_CLAUSE not in bullet
    confirm_at = bullet.index("content confirmation")
    tectonic_at = bullet.index("Use tectonic when installed")
    otherwise_at = bullet.index("Otherwise use XeLaTeX")
    assert confirm_at < tectonic_at < otherwise_at
    assert "after content confirmation" in bullet
    assert bullet.index("after content confirmation") < tectonic_at
    assert (
        "bibliography backend selected from the generated paper.tex" in bullet
    )
    assert "PDF (via LaTeX)" in bullet
    assert "academic-paper/agents/formatter_agent.md" in bullet
    assert (
        "the .tex source when asked for, or both paper.tex and "
        "references.bib if a requested PDF cannot be delivered"
    ) in bullet
    assert (
        "If the requested PDF cannot be delivered, report why and follow "
        "the formatter’s PDF source-delivery and build-command instructions."
    ) in bullet


def _protocol_pdf_step(text: str) -> str:
    return _between(
        text,
        "4. Only when a PDF was asked for, convert to LaTeX and compile PDF:\n",
        "\n5. Terminal acknowledgement",
    )


def _protocol_generation_bullet(text: str) -> str:
    step = _protocol_pdf_step(text)
    bullets = [line for line in step.splitlines() if "xeCJK" in line or "CJK" in line]
    assert len(bullets) == 1
    return bullets[0]


def _protocol_latex_template(text: str) -> str:
    specs = text.split("## Output Specifications\n", 1)[1]
    lines = [
        line for line in specs.splitlines() if line.startswith("- **LaTeX template**:")
    ]
    assert len(lines) == 1
    return lines[0]


@pytest.mark.parametrize(
    ("extract", "condition", "font_choice", "require_font_command"),
    [
        pytest.param(
            _protocol_generation_bullet,
            "If the record contains CJK text",
            "installed main font for the target OS",
            True,
            id="generation-bullet",
        ),
        pytest.param(
            _protocol_latex_template,
            "For CJK text",
            "installed CJK main font for the target OS",
            False,
            id="latex-template",
        ),
    ],
)
def test_process_record_uses_formatter_cjk_main_font(
    extract,
    condition: str,
    font_choice: str,
    require_font_command: bool,
) -> None:
    """Each process-record font instruction points at the formatter list."""
    snippet = extract(PROTOCOL.read_text(encoding="utf-8"))
    assert condition in snippet
    assert "xeCJK" in snippet
    assert font_choice in snippet
    assert FORMATTER_SECTION in snippet
    assert PROTOCOL_PATH in snippet
    assert OLD_FONT not in snippet
    if require_font_command:
        assert r"\setCJKmainfont" in snippet


def test_process_record_compile_rule_follows_cjk_font_guidance() -> None:
    protocol = PROTOCOL.read_text(encoding="utf-8")
    step_bullets = [
        line
        for line in _protocol_pdf_step(protocol).splitlines()
        if line.startswith("   - ")
    ]
    font_bullet = _protocol_generation_bullet(protocol)
    compile_bullet = f"   - {PROCESS_RECORD_COMPILE_RULE}"
    assert r"\setCJKmainfont" in font_bullet
    assert compile_bullet in step_bullets
    assert step_bullets.index(font_bullet) < step_bullets.index(compile_bullet)

    specs = protocol.split("## Output Specifications\n", 1)[1]
    compilation = [
        line for line in specs.splitlines() if line.startswith("- **Compilation**:")
    ]
    assert len(compilation) == 1
    assert (
        "tectonic when installed; otherwise run `xelatex` twice on the same "
        "generated record `.tex` file" in compilation[0]
    )
    assert "same toolchain as Stage 5" not in compilation[0]

    audit = AUDIT.read_text(encoding="utf-8")
    finalize = [
        line for line in audit.splitlines() if line.startswith("Stage 5 FINALIZE:")
    ]
    assert len(finalize) == 1
    assert (
        "tectonic when installed, otherwise XeLaTeX with the bibliography backend "
        "selected from the generated paper.tex" in finalize[0]
    )


def _template_section(text: str, start: str, end: str) -> str:
    return _between(text, start, end)


@pytest.mark.parametrize(
    ("start", "end", "kind"),
    [
        pytest.param(
            "## Basic Article Template\n",
            "\n## ",
            "commented",
            id="basic-article",
        ),
        pytest.param(
            "## XeLaTeX for Chinese Content\n",
            "\n## ",
            "active",
            id="xelatex",
        ),
        pytest.param(
            "### Markdown → PDF (with Chinese)\n",
            "\n### ",
            "pandoc",
            id="pandoc",
        ),
    ],
)
def test_non_apa_examples_use_installed_cjk_main_font(
    start: str,
    end: str,
    kind: str,
) -> None:
    """Non-APA examples substitute an installed CJK main font; no Noto pin."""
    section = _template_section(TEMPLATE.read_text(encoding="utf-8"), start, end)
    assert "<installed font>" in section
    assert "installed main font for the target OS" in section
    assert FORMATTER_SECTION in section
    assert TEMPLATE_PATH in section
    assert "Noto" not in section
    if kind == "commented":
        assert section.count(BASIC_CJK_COMMENT) == 1
        active = [
            line.strip()
            for line in section.splitlines()
            if line.strip() and not line.strip().startswith("%")
        ]
        assert not any(
            "xeCJK" in line
            or r"\setCJKmainfont" in line
            or r"\setCJKsansfont" in line
            for line in active
        )
    elif kind == "active":
        assert XELATEX_INTRO in section
        active = [
            line.strip()
            for line in section.splitlines()
            if line.strip() and not line.strip().startswith("%")
        ]
        assert r"\usepackage{xeCJK}" in active
        assert r"\setCJKmainfont{<installed font>}" in active
        assert r"\setCJKsansfont{<installed sans font>}" in active
    else:
        assert PANDOC_INTRO in section
        assert "--pdf-engine=xelatex" in section
        assert '-V CJKmainfont="<installed font>"' in section
        assert "--bibliography=references.bib" in section
