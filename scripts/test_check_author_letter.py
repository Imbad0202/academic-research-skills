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

| 項次 | 審查紀錄編號 |
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
    # The last level-2 section, 建議修改, has no item map subsection.
    letter = LETTER.split("## 附錄")[0]
    assert any(p.startswith("[AUTHOR-LETTER-APPENDIX]") for p in cal.check(letter, PACKAGE, MANUSCRIPT))


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


def test_a_quotation_inside_a_quotation_fails():
    # Template Rule 4: quote a shorter part without the inner marks instead.
    ms = MANUSCRIPT + "作者提出「雙軌制」架構。\nWe define \"burnout\" as exhaustion.\n"
    for quoted in ("原稿寫「提出『雙軌制』架構」", "“We define \"burnout\" as exhaustion”"):
        letter = LETTER.replace("請說明三所學校怎麼選出", quoted)
        assert any("without its pair" in p for p in cal.check(letter, PACKAGE, ms))
    shorter = LETTER.replace("請說明三所學校怎麼選出", "原稿寫「架構」與“as exhaustion”")
    assert cal.check(shorter, PACKAGE, ms) == []


def test_single_quotation_marks_and_apostrophes_are_kept():
    # ’ is kept, so a nested ‘…’ that the manuscript writes as "…" does not
    # match: the letter must copy the quotation exactly or paraphrase it.
    ms = MANUSCRIPT + "We define \"burnout\" as exhaustion.\n"
    letter = LETTER.replace("請說明三所學校怎麼選出", "“We define ‘burnout’ as exhaustion”")
    assert any("AUTHOR-LETTER-QUOTE" in p for p in cal.check(letter, PACKAGE, ms))


def test_singular_and_plural_possessives_differ():
    ms = MANUSCRIPT + "The patients’ records were reviewed.\n"
    letter = LETTER.replace("請說明三所學校怎麼選出", "“The patient’s records were reviewed.”")
    assert any("AUTHOR-LETTER-QUOTE" in p for p in cal.check(letter, PACKAGE, ms))


def test_a_quote_must_start_at_a_word_boundary():
    ms = MANUSCRIPT + "The study found an insignificant difference between groups.\n"
    bad = LETTER.replace("請說明三所學校怎麼選出", "“significant difference between groups”")
    assert any("AUTHOR-LETTER-QUOTE" in p for p in cal.check(bad, PACKAGE, ms))
    good = LETTER.replace("請說明三所學校怎麼選出", "“an insignificant difference between groups”")
    assert cal.check(good, PACKAGE, ms) == []


def test_a_top_level_single_curly_quotation_fails():
    # ’ is also the apostrophe (“the patients’ outcomes”), so a ‘…’ span has
    # no reliable end; the letter must use “…” or 「…」 instead.
    letter = LETTER.replace("請說明三所學校怎麼選出", "‘The patients’ outcomes improved.’")
    assert any("‘…’ quotation outside another quotation" in p for p in cal.check(letter, PACKAGE, None))


def test_a_plural_possessive_inside_a_double_quotation_is_checked_whole():
    ms = MANUSCRIPT + "The patients’ outcomes worsened.\n"
    good = LETTER.replace("請說明三所學校怎麼選出", "“The patients’ outcomes worsened.”")
    assert cal.check(good, PACKAGE, ms) == []
    bad = LETTER.replace("請說明三所學校怎麼選出", "“The patients’ outcomes improved.”")
    assert any("AUTHOR-LETTER-QUOTE" in p for p in cal.check(bad, PACKAGE, ms))


def test_english_word_boundaries_still_count():
    ms = MANUSCRIPT + "The signal is now here.\n"
    letter = LETTER.replace("請說明三所學校怎麼選出", "“The signal is nowhere.”")
    assert any("AUTHOR-LETTER-QUOTE" in p for p in cal.check(letter, PACKAGE, ms))


def test_a_cjk_manuscript_line_break_does_not_fail_a_real_quote():
    ms = "本研究以虛構的三所\n學校為例，問卷回收率為百分之六十。\n表 S1 列出各校樣本數。\n"
    assert cal.check(LETTER, PACKAGE, ms) == []


@pytest.mark.parametrize("line", ["見 _REV-3_。", "對應 __SC-2__。", "狀態 _NOT_CALIBRATED_"])
def test_an_id_in_markdown_emphasis_fails(line):
    letter = LETTER.replace("## 建議修改", f"{line}\n\n## 建議修改")
    assert any(p.startswith("[AUTHOR-LETTER-MACHINE-LINE]") for p in cal.check(letter, PACKAGE, MANUSCRIPT))


EMPTY_PACKAGE = "# Editorial Decision Package\n\n### Required Revisions (Must Fix)\n\n### Suggested Revisions (Should Fix)\n"
ACCEPT = "# 審查意見\n\n## 審查決定\n\n接受。\n\n## 必須修改\n\n無。\n\n## 請作者回答的問題\n\n無。\n"


def test_an_accept_letter_without_its_appendix_fails():
    problems = cal.check(ACCEPT, EMPTY_PACKAGE, MANUSCRIPT)
    assert any(p.startswith("[AUTHOR-LETTER-APPENDIX]") for p in problems)


def test_an_accept_letter_with_its_appendix_passes():
    letter = ACCEPT + "\n## 附錄\n\n### 這份審查的限制\n\nAI 模擬。\n\n### 項次對照\n\n| 項次 | 審查紀錄編號 |\n|------|------------|\n"
    assert cal.check(letter, EMPTY_PACKAGE, MANUSCRIPT) == []


def test_an_accept_letter_cut_before_its_item_map_fails():
    letter = ACCEPT + "\n## 附錄\n\n### 這份審查的限制\n\nAI 模擬。\n"
    problems = cal.check(letter, EMPTY_PACKAGE, MANUSCRIPT)
    assert any("the item map has no table" in p for p in problems)


def test_an_unclosed_quotation_mark_does_not_reach_the_next_paragraph():
    assert cal.quotations("他說“沒有結尾\n\n下一段「原稿」。") == ["原稿"]


@pytest.mark.parametrize("line", [
    "此為DA-CRITICAL問題",
    "屬於must_fix項目",
    "狀態NOT_CALIBRATED時",
    "[CONSENSUS-10] 共識",
    "~~~yaml",
])
def test_machine_ids_beside_cjk_text_and_other_forms_fail(line):
    letter = LETTER.replace("## 建議修改", f"{line}\n\n## 建議修改")
    assert any(p.startswith("[AUTHOR-LETTER-MACHINE-LINE]") for p in cal.check(letter, PACKAGE, MANUSCRIPT))


def test_a_reviewer_table_before_the_item_map_is_not_the_item_map():
    letter = LETTER.replace("### 項次對照", "### 各審查人摘要\n\n| 審查人 | 建議 |\n|---|---|\n| R1 | 大幅修改 |\n\n### 項次對照")
    assert cal.check(letter, PACKAGE, MANUSCRIPT) == []


def test_transport_reform_is_ordinary_english():
    letter = LETTER.replace("政策建議和發現分開寫。", "政策建議和發現分開寫，包括 public transport reform 的部分。")
    assert cal.check(letter, PACKAGE, MANUSCRIPT) == []


def test_an_id_in_the_appendix_fails_too():
    letter = LETTER.replace("### 項次對照", "### 輔助檢查\n\n- 對應 REV-2。\n\n### 項次對照")
    assert any(p.startswith("[AUTHOR-LETTER-MACHINE-LINE]") for p in cal.check(letter, PACKAGE, MANUSCRIPT))


def test_a_circled_number_in_the_item_map_is_a_problem_not_a_crash():
    letter = LETTER.replace("| 3 | S1 |", "| ③ | S1 |")
    problems = cal.check(letter, PACKAGE, MANUSCRIPT)
    assert any("needs one item number and one ref" in p for p in problems)


def test_full_width_numbering_is_not_a_list_item():
    # Markdown has no "3、" list; template Rule 3 asks for "3.".
    letter = LETTER.replace("3. 〔§5〕", "3、〔§5〕")
    assert "[AUTHOR-LETTER-MAPPING] item map item 3 is not a numbered item of the body" in cal.check(letter, PACKAGE, MANUSCRIPT)
    assert cal.numbered_items("請見附表\n1、附表 2\n") == []


def test_a_body_item_numbered_twice_fails():
    letter = LETTER.replace("3. 〔§5〕", "1. 〔§5〕")
    problems = cal.check(letter, PACKAGE, MANUSCRIPT)
    assert "[AUTHOR-LETTER-MAPPING] body item 1 is numbered more than once" in problems


def test_a_numbered_item_in_the_appendix_fails():
    letter = LETTER.replace("### 項次對照", "### 各審查人摘要\n\n1. 審查人一\n\n### 項次對照")
    assert any("the appendix has a numbered item" in p for p in cal.check(letter, PACKAGE, MANUSCRIPT))


def test_case_must_match_in_a_quotation():
    ms = MANUSCRIPT + "Each well held 5 mM glucose.\n"
    letter = LETTER.replace("請說明三所學校怎麼選出", "“Each well held 5 mm glucose.”")
    assert any("AUTHOR-LETTER-QUOTE" in p for p in cal.check(letter, PACKAGE, ms))


def test_a_straight_and_a_curly_apostrophe_are_the_same_mark():
    ms = MANUSCRIPT + "The patients' outcomes worsened.\n"
    letter = LETTER.replace("請說明三所學校怎麼選出", "“The patients’ outcomes worsened.”")
    assert cal.check(letter, PACKAGE, ms) == []


@pytest.mark.parametrize("ms_text,quote", [("Add caféine to the cup.", "café"), ("An étude for piano.", "tude")])
def test_word_boundaries_count_for_accented_letters(ms_text, quote):
    letter = LETTER.replace("請說明三所學校怎麼選出", f"“{quote}”")
    assert any("AUTHOR-LETTER-QUOTE" in p for p in cal.check(letter, PACKAGE, MANUSCRIPT + ms_text + "\n"))


def test_a_latin_term_beside_cjk_text_needs_no_boundary():
    ms = MANUSCRIPT + "本研究以BMI指數衡量體型。\n"
    letter = LETTER.replace("請說明三所學校怎麼選出", "原稿的「BMI」")
    assert cal.check(letter, PACKAGE, ms) == []


ACCEPT_APPENDIX = ACCEPT + "\n## 附錄\n\n### 這份審查的限制\n\nAI 模擬。\n\n### 項次對照\n\n"


def test_a_horizontal_rule_is_not_an_item_map_table():
    problems = cal.check(ACCEPT_APPENDIX + "---\n", EMPTY_PACKAGE, MANUSCRIPT)
    assert any("the item map has no table" in p for p in problems)


def test_a_header_row_alone_is_not_a_table():
    problems = cal.check(ACCEPT_APPENDIX + "| 項次 | 審查紀錄編號 |\n", EMPTY_PACKAGE, MANUSCRIPT)
    assert any("the item map has no table" in p for p in problems)


def test_a_row_without_a_ref_fails():
    letter = ACCEPT_APPENDIX + "| 項次 | 審查紀錄編號 |\n|---|---|\n| 1 | — |\n"
    problems = cal.check(letter, EMPTY_PACKAGE, MANUSCRIPT)
    assert any("needs one item number and one ref" in p for p in problems)


def test_a_table_without_outer_pipes_is_read():
    table = "| 項次 | 審查紀錄編號 |\n|------|---------------|\n| 1 | R1 |\n| 2 | R2 |\n| 3 | S1 |\n"
    bare = "項次 | 審查紀錄編號\n--- | ---\n1 | R1\n2 | R2\n3 | S1\n"
    assert table in LETTER
    assert cal.check(LETTER.replace(table, bare), PACKAGE, MANUSCRIPT) == []
    package = PACKAGE.replace("| R1 | Describe how the schools were chosen | SC-1 |", "R1 | Describe how the schools were chosen | SC-1")
    assert package != PACKAGE
    assert cal.check(LETTER, package, MANUSCRIPT) == []


def test_a_header_row_over_a_horizontal_rule_is_not_a_table():
    problems = cal.check(ACCEPT_APPENDIX + "| 項次 | 審查紀錄編號 |\n---\n", EMPTY_PACKAGE, MANUSCRIPT)
    assert any("the item map has no table" in p for p in problems)


def test_a_narrow_delimiter_row_is_a_table():
    letter = LETTER.replace("|------|---------------|", "| - | :- |")
    assert letter != LETTER
    assert cal.check(letter, PACKAGE, MANUSCRIPT) == []


@pytest.mark.parametrize("quoted", ["“本研究以三所學校為例\"", "「本研究以三所學校為例", "“本研究以“三所”學校為例”", "「本研究以「三所」學校為例」"])
def test_an_unpaired_or_nested_quotation_mark_fails(quoted):
    letter = LETTER.replace("請說明三所學校怎麼選出", quoted)
    assert any("without its pair" in p for p in cal.check(letter, PACKAGE, MANUSCRIPT))


def test_a_number_wrapped_inside_a_paragraph_is_not_an_item():
    letter = LETTER.replace("但還不能支持因果推論。", "但資料只涵蓋到\n2023. 年為止。")
    assert letter != LETTER
    assert cal.check(letter, PACKAGE, MANUSCRIPT) == []
    appendix = LETTER.replace("### 項次對照", "### 這份審查的限制\n\n本次只讀到\n2. 章為止。\n\n### 項次對照")
    assert cal.check(appendix, PACKAGE, MANUSCRIPT) == []


def test_a_paragraph_after_a_blank_line_ends_the_list():
    assert cal.numbered_items("1. a\n2. b\n\n文字\n3. c\n\n4. d\n") == ["1", "2", "4"]


def test_an_unclosed_mark_inside_another_quotation_fails():
    letter = LETTER.replace("本研究以虛構的三所學校為例", "本研究以“虛構的三所學校為例")
    assert any("without its pair" in p for p in cal.check(letter, PACKAGE, MANUSCRIPT))


@pytest.mark.parametrize("empty", ['""', "“”", "「」", "『』"])
def test_an_empty_quotation_is_ignored(empty):
    letter = LETTER.replace("請說明三所學校怎麼選出", f"請說明{empty}三所學校怎麼選出")
    assert cal.check(letter, PACKAGE, MANUSCRIPT) == []


def test_a_thai_quotation_needs_no_word_boundary():
    ms = MANUSCRIPT + "ประเทศไทยมีประชากร\n"
    letter = LETTER.replace("請說明三所學校怎麼選出", "“ประเทศไทย”")
    assert cal.check(letter, PACKAGE, ms) == []


def test_an_indented_continuation_line_is_not_an_item():
    assert cal.numbered_items("1. 資料涵蓋到\n   2023. 年為止。\n2. 說明抽樣方法。\n") == ["1", "2"]


@pytest.mark.parametrize("table", ["| 項次 |\n|---|---|\n", "| 項次 | 審查紀錄編號 |\n|---|\n", "| 項次 | 審查紀錄編號 |\n|---|---|---|\n", "| 項次 | 審查紀錄編號 | 備註 |\n|---|---|---|\n"])
def test_an_item_map_needs_exactly_two_columns(table):
    problems = cal.check(ACCEPT_APPENDIX + table, EMPTY_PACKAGE, MANUSCRIPT)
    assert any("the item map has no table" in p for p in problems)


def test_a_ref_outside_the_second_column_fails():
    letter = LETTER.replace("| 1 | R1 |", "| 1 | — | R1 |")
    problems = cal.check(letter, PACKAGE, MANUSCRIPT)
    assert any("needs one item number and one ref" in p for p in problems)


def test_straight_quotation_marks_nested_in_straight_ones_fail():
    letter = LETTER.replace("請說明三所學校怎麼選出", 'The text states "the "made up" result"')
    assert any("without its pair" in p for p in cal.check(letter, PACKAGE, MANUSCRIPT))


@pytest.mark.parametrize("ms,quoted", [
    ("本研究共納入\n120名受試者。", "「共納入120名受試者」"),
    ("本研究共納入120名受試者。", "「共納入\n120名受試者」"),
    ("作者訪談𠮷\n1號受試者。", "「訪談𠮷1號受試者」"),
])
def test_a_line_break_beside_a_chinese_character_adds_no_space(ms, quoted):
    letter = LETTER.replace("請說明三所學校怎麼選出", quoted)
    assert cal.check(letter, PACKAGE, MANUSCRIPT + ms + "\n") == []


def test_a_cell_keeps_an_empty_first_column():
    assert cal._cells("|| S1 | Fix Table S1 |") == ["", "S1", "Fix Table S1"]
