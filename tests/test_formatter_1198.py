"""Pin the APA 7 XeTeX font stack so xeCJK loads only for CJK text (#1198)."""

from __future__ import annotations

from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FORMATTER = ROOT / "academic-paper" / "agents" / "formatter_agent.md"
TEMPLATE = (
    ROOT / "academic-paper" / "references" / "latex_template_reference.md"
)

ACTIVE_LATIN = (
    r"\usepackage{fontspec}",
    r"\setmainfont{Times New Roman}",
    r"\setmonofont{Courier New}",
)

FORMATTER_CJK_COMMENT = (
    "% Only if the paper contains CJK text, include both commands below "
    "in the preamble.\n"
    "% Replace <installed font> with an installed main font for the target OS\n"
    '% from "Chinese LaTeX Compilation Settings" below, then uncomment both '
    "lines.\n"
    "% \\usepackage{xeCJK}\n"
    "% \\setCJKmainfont{<installed font>}"
)

TEMPLATE_CJK_COMMENT = (
    "% Only if the paper contains CJK text, include both commands below "
    "in the preamble.\n"
    "% Replace <installed font> with an installed main font for the target OS\n"
    '% from "Chinese LaTeX Compilation Settings" in ../agents/formatter_agent.md,\n'
    "% then uncomment both lines.\n"
    "% \\usepackage{xeCJK}\n"
    "% \\setCJKmainfont{<installed font>}"
)

SETUP_EN = ROOT / "docs" / "SETUP.md"
SETUP_ZH_TW = ROOT / "docs" / "SETUP.zh-TW.md"

LATIN_FONTS = ("Times New Roman", "Courier New")
OS_MAIN_FONTS = (
    ("macOS", "Songti TC"),
    ("Windows", "DFKai-SB"),
    ("Linux", "Noto Serif CJK TC"),
)


def _between(text: str, start: str, end: str) -> str:
    if start not in text:
        raise AssertionError(f"missing start marker: {start!r}")
    tail = text.split(start, 1)[1]
    if end not in tail:
        raise AssertionError(f"missing end marker: {end!r}")
    return tail.split(end, 1)[0]


def _formatter_font_stack(text: str) -> str:
    section = _between(
        text,
        "### APA 7.0 LaTeX (`apa7` Class) — Mandatory Rules\n",
        "\n### ",
    )
    stack = _between(section, "**Font stack**", "\n**")
    return _between(stack, "```latex\n", "\n```")


def _template_font_block(text: str) -> str:
    section = _between(
        text,
        "## APA 7.0 Template (`apa7` Class) — Preferred for APA Output\n",
        "\n## ",
    )
    return _between(section, "% === Fonts (XeTeX) ===\n", "\n% === ")


def _bullets(text: str) -> list[str]:
    return [line for line in text.splitlines() if line.startswith("- ")]


def _active_lines(block: str) -> list[str]:
    return [
        line.strip()
        for line in block.splitlines()
        if line.strip() and not line.strip().startswith("%")
    ]


@pytest.mark.parametrize(
    ("path", "extract", "cjk_comment"),
    [
        pytest.param(
            FORMATTER,
            _formatter_font_stack,
            FORMATTER_CJK_COMMENT,
            id="formatter",
        ),
        pytest.param(
            TEMPLATE,
            _template_font_block,
            TEMPLATE_CJK_COMMENT,
            id="template",
        ),
    ],
)
def test_apa_font_stack_loads_xecjk_only_for_cjk_text(
    path: Path,
    extract,
    cjk_comment: str,
) -> None:
    block = extract(path.read_text(encoding="utf-8"))
    active = _active_lines(block)
    for line in ACTIVE_LATIN:
        assert line in active
    cjk_active = [
        line
        for line in active
        if "xeCJK" in line or r"\setCJKmainfont" in line
    ]
    assert cjk_active == []
    assert block.count(cjk_comment) == 1


@pytest.mark.parametrize(
    ("path", "label", "cjk_only"),
    [
        pytest.param(
            SETUP_EN,
            "**Required fonts**",
            "Only papers containing CJK text need an additional font.",
            id="english",
        ),
        pytest.param(
            SETUP_ZH_TW,
            "**所需字型**",
            "只有含中日韓文字（CJK）的論文才需要額外的字型。",
            id="zh-TW",
        ),
    ],
)
def test_setup_guides_list_per_os_cjk_main_fonts(
    path: Path,
    label: str,
    cjk_only: str,
) -> None:
    """Each setup guide names the formatter's per-OS CJK main font."""
    block = _between(path.read_text(encoding="utf-8"), label, "\n>")
    assert "Source Han Serif TC VF" not in block
    assert cjk_only in block
    before, _, after = block.partition(cjk_only)
    before_bullets = _bullets(before)
    after_bullets = _bullets(after)
    for font in LATIN_FONTS:
        assert any(font in line for line in before_bullets), (
            f"{font} bullet does not precede the CJK-only sentence"
        )
    assert len(after_bullets) == len(OS_MAIN_FONTS)
    for bullet, (os_name, font) in zip(after_bullets, OS_MAIN_FONTS, strict=True):
        assert os_name in bullet and f"**{font}**" in bullet, (
            f"{os_name} and {font} are not on the same bullet"
        )


PIPELINE = ROOT / "academic-pipeline" / "SKILL.md"
STAGE5_FONT_LINE = (
    "  - Fonts: Times New Roman (English) + Courier New (monospace). "
    "For CJK text, use the installed CJK main font for the target OS from "
    '"Chinese LaTeX Compilation Settings" in '
    "academic-paper/agents/formatter_agent.md."
)
README_CJK_SENTENCES = (
    pytest.param(
        "README.md",
        "Papers containing CJK text also need a [CJK font](docs/SETUP.md) "
        "for PDF output.",
        id="en",
    ),
    pytest.param(
        "README.zh-TW.md",
        "含中日韓文字的論文在輸出 PDF 時還需要 [CJK 字型](docs/SETUP.md)。",
        id="zh-TW",
    ),
    pytest.param(
        "README.es-ES.md",
        "Los artículos con texto en chino, japonés o coreano también "
        "necesitan una [fuente CJK](docs/SETUP.md) para generar el PDF.",
        id="es-ES",
    ),
    pytest.param(
        "README.pt-BR.md",
        "Artigos com texto em chinês, japonês ou coreano também precisam "
        "de uma [fonte CJK](docs/SETUP.md) para gerar o PDF.",
        id="pt-BR",
    ),
    pytest.param(
        "README.ja-JP.md",
        "中国語・日本語・韓国語の文字を含む論文を PDF に出力する場合は、"
        "[CJK フォント](docs/SETUP.md)も必要です。",
        id="ja-JP",
    ),
    pytest.param(
        "README.ko-KR.md",
        "중국어·일본어·한국어 문자가 포함된 논문을 PDF로 출력하려면 "
        "[CJK 글꼴](docs/SETUP.md)도 필요합니다.",
        id="ko-KR",
    ),
)


def test_pipeline_stage_5_points_to_formatter_cjk_fonts() -> None:
    """Stage 5 names the formatter's per-OS CJK list, not one CJK font."""
    block = _between(
        PIPELINE.read_text(encoding="utf-8"),
        "Stage 5: academic-paper (format-convert mode)\n",
        "\n```",
    )
    font_lines = [
        line for line in block.splitlines() if line.startswith("  - Fonts:")
    ]
    assert len(font_lines) == 1
    line = font_lines[0]
    for font in LATIN_FONTS:
        assert font in line
    assert "For CJK text" in line
    assert "target OS" in line
    assert "Chinese LaTeX Compilation Settings" in line
    assert "academic-paper/agents/formatter_agent.md" in line
    assert "Source Han Serif TC" not in line
    assert line == STAGE5_FONT_LINE


@pytest.mark.parametrize(("filename", "cjk_sentence"), README_CJK_SENTENCES)
def test_readme_install_line_explains_cjk_font(
    filename: str,
    cjk_sentence: str,
) -> None:
    """The install bullet points CJK papers at the setup guide."""
    bullets = [
        line
        for line in (ROOT / filename).read_text(encoding="utf-8").splitlines()
        if line.startswith("- ") and "Pandoc" in line and "tectonic" in line
    ]
    assert len(bullets) == 1
    bullet = bullets[0]
    for token in ("DOCX", "APA 7.0", "PDF", "Markdown"):
        assert token in bullet
    assert cjk_sentence in bullet
    assert "Source Han Serif TC" not in bullet
    assert "思源宋體 TC" not in bullet
