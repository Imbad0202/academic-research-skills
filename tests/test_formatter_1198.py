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
        assert os_name in bullet and font in bullet, (
            f"{os_name} and {font} are not on the same bullet"
        )
