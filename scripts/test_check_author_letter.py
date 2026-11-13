#!/usr/bin/env python3
"""Tests for scripts/check_author_letter.py (#1078). All text is synthetic."""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

import check_author_letter as cal  # noqa: E402

MANUSCRIPT = (
    "第三章 研究方法\n本研究以虛構的三所學校為例，問卷回收率為百分之六十。\n"
    "表 S1 列出各校樣本數。\n"
)
PACKAGE = """# Editorial Decision Package

## Part 2: Revision Roadmap

### Required Revisions (Must Fix)

| Transport ref | Revision Item | Sub-Claim(s) |
|---|---|---|
| R1 | Describe how the schools were chosen | SC-1 |
| R2 | Report the non-response handling | SC-2 |

### Suggested Revisions (Should Fix)

| Transport ref | Revision Item | Sub-Claim(s) |
|---|---|---|
| S1 | Separate the policy advice from the findings | — |

### Source-Traceability Checklist

- [ ] R1 — obligation `must_fix`: Describe how the schools were chosen
"""
LETTER = """# 審查意見

## 審查決定

大幅修改。研究設計能支持描述性結論，但還不能支持因果推論。

## 必須修改

抽樣

1. 〔§3〕原稿寫「本研究以虛構的三所學校為例」，請說明三所學校怎麼選出。
2. 〔§3〕說明未回收問卷的處理方式；可參考表 S1 的樣本數。

## 建議修改

3. 〔§5〕政策建議和發現分開寫。

## 附錄

### 項次對照

| 項次 | Transport ref |
|------|---------------|
| 1 | R1 |
| 2 | R2 |
| 3 | S1 |
"""


def test_a_clean_letter_passes():
    assert cal.check(LETTER, PACKAGE, MANUSCRIPT) == []


def test_a_quote_not_in_the_manuscript_fails():
    letter = LETTER.replace("本研究以虛構的三所學校為例", "本研究以三所學校為例")
    problems = cal.check(letter, PACKAGE, MANUSCRIPT)
    assert [p for p in problems if p.startswith("[AUTHOR-LETTER-QUOTE]")]


@pytest.mark.parametrize("marks", [("“", "”"), ('"', '"'), ("『", "』"), ("「", "」")])
def test_every_quote_mark_is_checked(marks):
    letter = LETTER.replace("請說明", f"請說明{marks[0]}沒有這句話{marks[1]}")
    assert any("AUTHOR-LETTER-QUOTE" in p for p in cal.check(letter, PACKAGE, MANUSCRIPT))


def test_a_quote_in_the_appendix_is_checked_too():
    letter = LETTER + "\n### 各審查人摘要\n\n審查人 1 認為「抽樣沒有分層」。\n"
    assert any("AUTHOR-LETTER-QUOTE" in p for p in cal.check(letter, PACKAGE, MANUSCRIPT))


def test_without_a_manuscript_the_quote_check_is_skipped():
    letter = LETTER.replace("本研究以虛構的三所學校為例", "不存在的句子")
    assert cal.check(letter, PACKAGE, None) == []


@pytest.mark.parametrize("line", [
    "dimension_verdicts: D1=pass",
    "fired_conditions: F2",
    "editorial_decision=major_revision",
    "calibration_status: NOT_CALIBRATED",
    "見 REV-3。",
    "對應 SC-2。",
    "來自 R2-W1。",
    "[CONSENSUS-4] 共識",
    "DA-CRITICAL 問題",
    "Transport ref R1",
    "<!-- note -->",
    "```yaml",
    "obligation must_fix",
])
def test_a_machine_line_in_the_body_fails(line):
    letter = LETTER.replace("## 建議修改", f"{line}\n\n## 建議修改")
    problems = cal.check(letter, PACKAGE, MANUSCRIPT)
    assert any(p.startswith("[AUTHOR-LETTER-MACHINE-LINE]") for p in problems), problems


def test_a_supplementary_table_location_is_not_a_machine_id():
    # "表 S1" is a manuscript location with the form of a transport ref.
    assert "表 S1" in LETTER
    assert cal.check(LETTER, PACKAGE, MANUSCRIPT) == []


def test_a_dropped_roadmap_item_fails():
    letter = LETTER.replace("| 3 | S1 |\n", "")
    problems = cal.check(letter, PACKAGE, MANUSCRIPT)
    assert "[AUTHOR-LETTER-MAPPING] roadmap item S1 is not in the item map" in problems


def test_an_unknown_and_a_repeated_ref_fail():
    letter = LETTER.replace("| 3 | S1 |", "| 3 | S1 |\n| 4 | S2 |\n| 5 | R1 |")
    problems = cal.check(letter, PACKAGE, MANUSCRIPT)
    assert "[AUTHOR-LETTER-MAPPING] item map ref S2 is not a roadmap item" in problems
    assert "[AUTHOR-LETTER-MAPPING] item map ref R1 appears more than once" in problems


def test_refs_outside_the_roadmap_tables_are_not_roadmap_items():
    # The Source-Traceability Checklist names R1 again; only table rows count.
    assert cal.roadmap_refs(PACKAGE) == ["R1", "R2", "S1"]


def test_a_letter_with_one_level_2_heading_has_no_appendix():
    problems = cal.check("# 審查意見\n\n## 審查決定\n\n大幅修改。\n", PACKAGE, MANUSCRIPT)
    assert any(p.startswith("[AUTHOR-LETTER-APPENDIX]") for p in problems)


def test_a_letter_cut_before_its_appendix_fails():
    letter = LETTER.split("## 附錄")[0]
    assert cal.check(letter, PACKAGE, MANUSCRIPT)


@pytest.mark.parametrize("heading", ["## Appendix", "## Apéndice", "## 附录", "## 부록"])
def test_the_appendix_heading_can_be_in_any_language(heading):
    letter = LETTER.replace("## 附錄", heading)
    assert cal.check(letter, PACKAGE, MANUSCRIPT) == []


def test_a_quote_wrapped_onto_a_new_line_is_checked():
    wrapped = LETTER.replace("「本研究以虛構的三所學校為例」", "「本研究以虛構的\n三所學校為例」")
    assert cal.check(wrapped, PACKAGE, MANUSCRIPT) == []
    absent = LETTER.replace("請說明三所學校怎麼選出", "「原稿沒有的第一行\n以及第二行」")
    assert any("AUTHOR-LETTER-QUOTE" in p for p in cal.check(absent, PACKAGE, MANUSCRIPT))


def test_a_body_item_left_out_of_the_letter_fails():
    letter = LETTER.replace("3. 〔§5〕政策建議和發現分開寫。\n", "")
    problems = cal.check(letter, PACKAGE, MANUSCRIPT)
    assert "[AUTHOR-LETTER-MAPPING] item map item 3 is not a numbered item of the body" in problems


def test_an_item_map_that_repeats_an_item_number_fails():
    letter = LETTER.replace("| 2 | R2 |", "| 1 | R2 |")
    problems = cal.check(letter, PACKAGE, MANUSCRIPT)
    assert "[AUTHOR-LETTER-MAPPING] item map item 1 appears more than once" in problems
    assert "[AUTHOR-LETTER-MAPPING] body item 2 is not in the item map" in problems


def test_a_row_with_two_refs_fails():
    letter = LETTER.replace("| 3 | S1 |", "| 3 | S1 | R2 |")
    problems = cal.check(letter, PACKAGE, MANUSCRIPT)
    assert any("needs one item number and one ref" in p for p in problems)


def test_bulleted_questions_are_not_items():
    letter = LETTER.replace("## 附錄", "## 請作者回答的問題\n\n- 第二年的樣本有沒有換人？\n\n## 附錄")
    assert cal.check(letter, PACKAGE, MANUSCRIPT) == []


def test_the_cli_exit_codes(tmp_path, capsys):
    paths = {}
    for name, text in (("letter", LETTER), ("package", PACKAGE), ("manuscript", MANUSCRIPT)):
        paths[name] = tmp_path / f"{name}.md"
        paths[name].write_text(text, encoding="utf-8")
    args = ["--letter", str(paths["letter"]), "--package", str(paths["package"])]
    assert cal.main(args + ["--manuscript", str(paths["manuscript"])]) == 0
    assert "AUTHOR-LETTER: PASS" in capsys.readouterr().out
    assert cal.main(args) == 0
    assert "QUOTE-CHECK-NOT-RUN" in capsys.readouterr().out
    paths["letter"].write_text(LETTER.replace("| 3 | S1 |\n", ""), encoding="utf-8")
    assert cal.main(args) == 1
    with pytest.raises(SystemExit) as exc:
        cal.main(["--letter", str(tmp_path / "missing.md"), "--package", str(paths["package"])])
    assert exc.value.code == 2


def test_the_skill_names_the_step_and_the_template():
    skill = (REPO_ROOT / "academic-paper-reviewer" / "SKILL.md").read_text(encoding="utf-8")
    assert "### Author letter (#1078)" in skill
    assert "python3 scripts/check_author_letter.py --letter" in skill
    assert (REPO_ROOT / "academic-paper-reviewer" / "templates" / "author_letter_template.md").is_file()
