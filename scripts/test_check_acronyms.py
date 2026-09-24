#!/usr/bin/env python3
"""Tests for scripts/check_acronyms.py (#849).

Every fixture is synthetic. The small cases below give one manuscript per
token rule and exclusion in the issue; the full manuscript under
tests/fixtures/acronym_check/ pins the JSON and both Markdown reports
byte for byte, so a change in wording, ordering, or line numbers shows.
"""
from __future__ import annotations

import hashlib
import json
import os
import random
from pathlib import Path

import pytest

from scripts.check_acronyms import (
    DEFAULT_ALLOWLIST,
    SCOPES,
    NotChecked,
    base_form,
    build_report,
    check,
    is_candidate,
    render,
)
from tests.test_helpers import run_script

REPO = Path(__file__).resolve().parents[1]
SCRIPT = REPO / "scripts" / "check_acronyms.py"
FIXTURES = REPO / "tests" / "fixtures" / "acronym_check"


def rows(report: dict) -> list[tuple]:
    return [(f["scope"], f["line"], f["rule"], f["acronym"]) for f in report["findings"]]


def findings(text: str, **kwargs) -> list[tuple]:
    return rows(check(text, **kwargs))


# --- rules ---------------------------------------------------------------


def test_defined_before_use_is_clean() -> None:
    assert findings("A randomized controlled trial (RCT) ran. The RCT ended.\n") == []


def test_undefined_is_reported_at_first_use_with_the_count() -> None:
    report = check("We ran an RCT.\n\nThe RCT ended.\n")
    assert report["findings"] == [{"scope": "body", "line": 1, "rule": "undefined", "acronym": "RCT",
                                   "expansion": None, "occurrences": 2}]


def test_use_before_the_definition() -> None:
    text = "The RCT ran.\nA randomized controlled trial (RCT) is a design.\n"
    report = check(text)
    [finding] = report["findings"]
    assert (finding["line"], finding["rule"], finding["expansion"]) == (
        1, "defined_after_use", "randomized controlled trial")


def test_each_repeated_definition_is_reported_on_its_line() -> None:
    text = ("A large language model (LLM) helps.\n"
            "Later, a large language model (LLM) again.\n"
            "And large language models (LLMs) a third time.\n")
    assert findings(text) == [("body", 2, "defined_again", "LLM"), ("body", 3, "defined_again", "LLM")]


def test_scopes_define_independently() -> None:
    text = ("## Abstract\n\nThe RCT worked.\n\n"
            "## 摘要\n\n本研究採隨機對照試驗（randomized controlled trial, RCT）。\n\n"
            "## Introduction\n\nA randomized controlled trial (RCT) ran; the RCT ended.\n")
    assert findings(text) == [("abstract_en", 3, "undefined", "RCT")]


def test_chinese_definition_forms() -> None:
    text = ("## 中文摘要\n\n以大型語言模型（LLM）與隨機對照試驗（randomized controlled trial，RCT）。"
            "使用RCT設計與LLM輔助。\n")
    assert findings(text) == []


def test_unread_definition_form_is_a_coverage_limit_not_a_finding() -> None:
    report = check("The RCT (randomized controlled trial) ran. The RCT ended.\n")
    assert report["findings"] == []
    assert report["status"] == "partial"
    assert report["coverage_limits"] == [{"scope": "body", "line": 1, "acronym": "RCT",
                                          "reason": "unread_definition_form"}]


def test_chinese_words_after_an_acronym_are_an_unread_definition_form() -> None:
    report = check("本研究使用 RCT（隨機對照試驗）。RCT 有效。\n")
    assert report["findings"] == []
    assert report["coverage_limits"] == [{"scope": "body", "line": 1, "acronym": "RCT",
                                          "reason": "unread_definition_form"}]
    # A cross-reference is a use, in either language.
    assert findings("本研究的 RCT（見第二節）有效。\n") == [("body", 1, "undefined", "RCT")]
    text = "The RCT (see recruitment criteria in Table 1) enrolled 120 participants.\n"
    assert findings(text) == [("body", 1, "undefined", "RCT")]


def test_a_parenthetical_whose_words_do_not_spell_the_acronym_is_a_use() -> None:
    assert findings("The RCT (n = 120) ran. The LLM (see Section 2) helped.\n") == [
        ("body", 1, "undefined", "LLM"), ("body", 1, "undefined", "RCT")]


def test_a_definition_across_a_line_break() -> None:
    assert findings("A randomized controlled\ntrial (RCT) ran; the RCT ended.\n") == []
    assert findings("In a trial (randomized controlled trial,\nRCT) we saw the RCT end.\n") == []


def test_a_parenthetical_at_the_start_of_a_paragraph_is_not_a_definition() -> None:
    assert findings("(RCT) was run.\n") == [("body", 1, "undefined", "RCT")]
    assert findings("Trials vary.\n\n(RCT) was run.\n") == [("body", 3, "undefined", "RCT")]


def _outcome(text: str) -> tuple[list[tuple], list[tuple]]:
    report = check(text)
    return ([(f["rule"], f["acronym"], f["expansion"], f["occurrences"]) for f in report["findings"]],
            [(c["acronym"], c["reason"]) for c in report["coverage_limits"]])


@pytest.mark.parametrize("text", [
    "A randomized controlled trial (RCT) ran. The RCT ended.",
    "The RCT ran. A randomized controlled trial (RCT) is a design.",
    "The RCT (randomized controlled trial) ran. The RCT ended.",
    "We compared several methods (RCT). The RCT ended.",
    "Designs vary (e.g. randomized controlled trials, RCTs). A randomized controlled trial (RCT) ran.",
    "As reported (see also Smith et al., 2020, pp. 4, 6; WHO, 2019), the SEM held.",
    "Smith JA, Jones BC (2019) agreed, as did Lee KM et al. about the IRT.",
    "Smith AB, McDonald EF, van der Berg GH (2020) agreed about the IRT.",
    "Smith AB and Jones EF (2020) agreed, as did Lee GH & Wu KM (2021), about the IRT.",
    "The World Health Organization [WHO] said so. The LLM helped.",
    "Randomized controlled trials (RCTs; Smith, 2020, Chapter 3) help. The RCT ended.",
    "The effect held, as in Figure 2. The RCT ran. A randomized controlled trial (RCT) is a design.",
    "本研究採隨機對照試驗（randomized controlled trial, RCT）。The RCT ended.",
    "Structural equation modeling (that is, SEM) was used. Structural equation modeling (SEM) ran.",
    "The SEM (i.e., structural equation modeling) was used. Two designs (namely RCT) ran.",
    "We tried methods (for instance, NMF). Nonnegative matrix factorization (NMF) won.",
    "Structural equation modeling (i. e., SEM) was used. The RCT (e. g., a pilot trial) ran.",
    "The RCT (including recruitment, consent, and treatment) lasted six months.",
    "Structural equation modeling (hereafter referred to as SEM) was used. The SEM held.",
])
def test_a_line_break_at_any_space_reads_as_the_space(text: str) -> None:
    expected = _outcome(text + "\n")
    for i, char in enumerate(text):
        if char == " ":
            wrapped = text[:i] + "\n" + text[i + 1:] + "\n"
            assert _outcome(wrapped) == expected, wrapped


@pytest.mark.parametrize("text", [
    "本研究採隨機對照試驗（RCT）。RCT 有效。",
    "本研究使用 RCT（隨機對照試驗）。RCT 有效。",
    "RCT 有效。本研究採隨機對照試驗（RCT）。",
    "RCT 有效。此設計（隨機對照試驗，RCT）。",
    "RCT（包括招募與同意）持續六個月。",
    "多種方法（例如 PCA，NMF）。非負矩陣分解（NMF）表現最好。",
    "結構方程模型（亦即 SEM）被使用。結構方程模型（也就是 SEM）再次被使用。",
    "SEM（也就是結構方程模型）被使用。",
    "結構方程模型（以下簡稱 SEM）被使用。結構方程模型（structural equation modeling，下稱 SEM）再次被使用。",
])
def test_a_line_break_between_chinese_characters_changes_nothing(text: str) -> None:
    expected = _outcome(text + "\n")
    for i in range(1, len(text)):
        if "\u3400" <= text[i - 1] <= "\u9fff" and "\u3400" <= text[i] <= "\u9fff":
            wrapped = text[:i] + "\n" + text[i:] + "\n"
            assert _outcome(wrapped) == expected, wrapped


def test_a_parenthetical_it_cannot_confirm_is_a_coverage_limit() -> None:
    report = check("We compared several methods (RCT). The RCT ended.\n")
    assert report["findings"] == []
    assert report["status"] == "partial"
    assert report["coverage_limits"] == [{"scope": "body", "line": 1, "acronym": "RCT",
                                          "reason": "unconfirmed_definition"}]
    assert "RCT (the initials before its parentheses do not spell it)" in render(report, "en")
    assert "RCT（括號前各字的字首拼不出這個縮寫）" in render(report, "zh-TW")


@pytest.mark.parametrize("text, expected", [
    ("Designs vary (e.g., RCT). The RCT ended.\n", [("body", 1, "undefined", "RCT")]),
    ("Two designs (SEM, RCT) ran.\n", [("body", 1, "undefined", "RCT"),
                                       ("body", 1, "undefined", "SEM")]),
    ("Designs vary (e.g.\nrandomized controlled trials, RCTs).\nA randomized controlled trial "
     "(RCT) is one.\n", [("body", 2, "defined_after_use", "RCT")]),
])
def test_example_and_list_parentheticals_are_uses(text: str, expected: list[tuple]) -> None:
    assert findings(text) == expected


@pytest.mark.parametrize("text, expansion", [
    ("The eGFR fell.\nWe measured the estimated glomerular filtration rate (eGFR).\n",
     "estimated glomerular filtration rate"),
    ("The DoE paid.\nThe Department of Education (DoE) funds it.\n", "Department of Education"),
    ("The RCTs ended.\nRandomized controlled trials (RCTs; Smith, 2020) help.\n",
     "Randomized controlled trials"),
    ("The RCT ended.\nA *randomized controlled trial* (RCT) ran.\n", "randomized controlled trial"),
    ("The eGFR fell.\nWe measured (the estimated glomerular filtration rate, eGFR).\n",
     "estimated glomerular filtration rate"),
    ("The T2D rose.\nPatients had type 2 diabetes (T2D).\n", "type 2 diabetes"),
    ("The T2D rose.\nPatients had (type 2 diabetes, T2D).\n", "type 2 diabetes"),
])
def test_the_expansion_is_the_shortest_run_that_spells_it(text: str, expansion: str) -> None:
    [finding] = check(text)["findings"]
    assert (finding["rule"], finding["expansion"]) == ("defined_after_use", expansion)


@pytest.mark.parametrize("definition, expansion", [
    ("國際疾病及相關健康問題統計分類第十次修訂版（ICD）", "國際疾病及相關健康問題統計分類第十次修訂版"),  # 21 characters
    ("本研究採用結構方程模型（SEM）", "本研究採用結構方程模型"),
    ("2型糖尿病（T2D）", "型糖尿病"),
])
def test_a_chinese_expansion_is_the_run_of_chinese_characters_before_it(definition: str,
                                                                        expansion: str) -> None:
    acronym = definition[definition.index("（") + 1:-1]
    for text, rule in ((f"{acronym} 很常用。{definition}。\n", "defined_after_use"),
                       (f"{definition}。{definition}。\n", "defined_again")):
        [finding] = check(text)["findings"]
        assert (finding["rule"], finding["acronym"], finding["expansion"]) == (rule, acronym, expansion)


# --- allowlist -------------------------------------------------------------


def test_default_and_user_allowlists() -> None:
    assert findings("DNA and HIV and the PhD and MHz.\n") == []
    assert findings("NLP helped.\n", allow=DEFAULT_ALLOWLIST | {"NLP"}) == []
    assert findings("NLP helped.\n") == [("body", 1, "undefined", "NLP")]


def test_allowlist_file_and_repeated_flags(tmp_path: Path) -> None:
    manuscript = tmp_path / "m.md"
    manuscript.write_text("NLP and SEM and IRT.\n", encoding="utf-8")
    allow = tmp_path / "allow.txt"
    allow.write_text("# discipline list\nSEM\n\nIRT  # item response theory\n", encoding="utf-8")
    report = build_report(manuscript, ",".join(SCOPES), ["NLP"], allow)
    assert report["findings"] == [] and report["allowlist"]["user"] == ["IRT", "NLP", "SEM"]


# --- token rules -----------------------------------------------------------


@pytest.mark.parametrize("token, expected", [
    ("RCT", True), ("eGFR", True), ("qPCR", True), ("mRNA", True), ("PhD", True), ("AI", True),
    ("BRCA1", True), ("RCT2", True), ("IV", True),
    ("H2O", False), ("CO2", False), ("H1N1", False),        # element symbols with counts
    ("II", False), ("XII", False), ("XXXIX", False),        # Roman numerals up to XXXIX
    ("XL", True), ("CD", True), ("MI", True), ("LV", True),  # larger ones stay candidates
    ("SD", False), ("SE", False), ("CI", False),            # statistical symbols
    ("A", False), ("ABCDEFG", False), ("Hello", False), ("iPad", False),
    ("2FA", False), ("2SLS", False),                        # a candidate starts with a letter
])
def test_candidate_shape(token: str, expected: bool) -> None:
    assert is_candidate(token) is expected


@pytest.mark.parametrize("word, expected", [
    ("RCTs", "RCT"), ("IVs", "IV"), ("PhDs", "PhD"), ("RCT", "RCT"),
    ("CIs", None), ("SDs", None), ("SEs", None), ("IIs", None), ("CO2s", None),  # excluded bases
])
def test_a_plural_counts_as_its_base(word: str, expected: str | None) -> None:
    assert base_form(word) == expected


@pytest.mark.parametrize("text, acronym", [
    ("We compared error measures (SDs, RMSE). The RMSE decreased.\n", "RMSE"),
    ("We compared error measures (SE, RMSE). The RMSE decreased.\n", "RMSE"),
    ("Gases rose (CO2, NOx) in the NOx series.\n", "NOx"),
])
def test_a_list_with_excluded_tokens_is_a_use(text: str, acronym: str) -> None:
    assert findings(text) == [("body", 1, "undefined", acronym)]


_FUZZ_PIECES = ["(", ")", "（", "）", ",", "，", "、", ";", "/", "-", " and ", " or ", "與", "$R^2$", "`x`",
                "($R^2$, ", "(`x`, ", "（、",
                "<!-- c -->", "RCT", "CIs", "OR", "HR", "e.g.,", "randomized controlled trial", "隨機對照試驗",
                "（見第二節）", "Figure 1 |", "Table III.", "圖一：", "Note.", "Smith AB", " (2020a)",
                "(WHO, n.d.-a)", "[WHO]", "\n", "\n\n", "# Abstract\n", "## 摘要\n", "## References\n",
                "| a | b |\n|---|---|\n", "- ", "> ", "```\n", "![img](x.png)\n", "***\n", "===\n", "\\",
                "*", "Keywords: ", "\r\n", "\u2028", "and/or", "1", "2020", "et al.", "hereafter ", "以下簡稱",
                "i.e., ", "「", "」", "“", "'", " – ", "Figure 1A", "stage IV", "第IV期", "圖1–圖",
                "](#RCT)", "][RCT]", "[RCT]: https://x.org\n", "(<a b>"]


def test_mixed_constructs_never_crash_the_check() -> None:
    # Every input gives a report or a not_checked state, never an exception.
    rng = random.Random(849)
    for _ in range(1500):
        text = "Body prose ran. " + "".join(rng.choice(_FUZZ_PIECES) for _ in range(rng.randint(1, 30)))
        try:
            report = check(text)
        except NotChecked:
            continue
        render(report, "en")
        render(report, "zh-TW")


@pytest.mark.parametrize("item", ["$R^2$", "`r2`", "<!-- fit -->", "R²", "χ²", "p < .05", "n = 120",
                                  "M = 3.2, SD = 1.1"])
def test_symbols_numbers_and_unread_items_leave_a_use(item: str) -> None:
    assert findings(f"We compared fit statistics ({item}, AIC).\n") == [("body", 1, "undefined", "AIC")]


@pytest.mark.parametrize("lead", ["for example,", "e. g., matrix methods,", "such as matrix methods,",
                                  "including PCA,"])
def test_an_example_led_list_is_a_use(lead: str) -> None:
    text = f"We tried methods ({lead} NMF). Nonnegative matrix factorization (NMF) won.\n"
    assert ("body", 1, "defined_after_use", "NMF") in findings(text)


@pytest.mark.parametrize("text", [
    "The RCT (including recruitment, consent, and treatment) lasted six months.\n",
    "The RCT（包括招募與同意）持續六個月。\n",
])
def test_an_example_led_parenthetical_after_an_acronym_is_a_use(text: str) -> None:
    assert findings(text) == [("body", 1, "undefined", "RCT")]


_MARS_LASSO = ("Multivariate adaptive regression splines (MARS) and the least absolute shrinkage and\n"
               "selection operator (LASSO) ran.\n\n")


@pytest.mark.parametrize("text, rule", [
    ("We compared ML (MARS, LASSO). Machine learning (ML) won.\n", "defined_after_use"),
    ("我們比較 ML（MARS, LASSO）。機器學習（ML）較好。\n", "defined_after_use"),
    ("We compared ML (MARS, LASSO).\n", "undefined"),
    ("Machine learning (ML) ran. We compared ML (MARS, LASSO). Machine learning (ML) won.\n",
     "defined_again"),
])
def test_an_acronym_list_after_an_acronym_is_a_use(text: str, rule: str) -> None:
    # The initials of "MARS, LASSO" spell ML, but a list of acronyms is not its expansion.
    assert findings(_MARS_LASSO + text) == [("body", 4, rule, "ML")]


def test_a_list_after_an_acronym_whose_initials_spell_it_is_a_coverage_limit() -> None:
    report = check(_MARS_LASSO + "We compared ML (MARS, LASSO, and random forests).\n")
    assert rows(report) == [] and [limit["acronym"] for limit in report["coverage_limits"]] == ["ML"]


@pytest.mark.parametrize("lead", ["i.e.,", "i.e.", "i. e.,", "ie", "viz.", "namely,", "namely", "That is,",
                                  "that is,", "that is to say,", "in other words,"])
def test_a_restatement_lead_is_read_without_its_words(lead: str) -> None:
    assert findings(f"Structural equation modeling ({lead} SEM) was used.\n") == []
    report = check(f"The SEM ({lead} structural equation modeling) was used.\n")
    assert rows(report) == [] and report["coverage_limits"][0]["acronym"] == "SEM"
    for text in (f"Two designs ({lead} SEM) were used.\n",
                 f"The SEM ({lead} the model in Section 2) was used.\n"):
        assert findings(text) == [("body", 1, "undefined", "SEM")]


@pytest.mark.parametrize("lead", ["即", "即 ", "亦即", "也就是"])
def test_a_chinese_restatement_lead_is_read_without_its_words(lead: str) -> None:
    assert findings(f"結構方程模型（{lead}SEM）被使用。\n") == []
    report = check(f"SEM（{lead}結構方程模型）被使用。\n")
    assert rows(report) == [] and report["coverage_limits"][0]["acronym"] == "SEM"


@pytest.mark.parametrize("lead", ["hereafter", "Hereafter,", "hereinafter", "henceforth", "abbreviated as",
                                  "referred to as", "hereafter referred to as", "also known as", "aka",
                                  "a.k.a.", "called", "termed", "Called", "Known as", "Abbreviated as",
                                  "Aka"])
def test_a_naming_lead_is_read_without_its_words(lead: str) -> None:
    assert findings(f"Structural equation modeling ({lead} SEM) was used.\n") == []
    assert findings(f"A new method (structural equation modeling, {lead} SEM) was used.\n") == []
    report = check(f"Two designs ({lead} RCT) ran.\n")
    assert rows(report) == [] and report["coverage_limits"][0]["reason"] == "unconfirmed_definition"


@pytest.mark.parametrize("lead", ["以下簡稱", "以下簡稱 ", "簡稱", "簡稱為", "下稱", "以下稱為", "又稱", "或稱", "稱為",
                                  "縮寫為", "英文縮寫", "即為"])
def test_a_chinese_naming_lead_is_read_without_its_words(lead: str) -> None:
    assert findings(f"結構方程模型（{lead}SEM）被使用。\n") == []
    assert findings(f"結構方程模型（structural equation modeling，{lead}SEM）被使用。\n") == []


@pytest.mark.parametrize("text", ["結構方程模型（以下簡稱「SEM」）被使用。\n", "結構方程模型（『SEM』）被使用。\n",
                                  "Structural equation modeling (hereafter “SEM”) was used.\n",
                                  "Structural equation modeling ('SEM') was used.\n"])
def test_quotation_marks_around_a_defined_acronym_are_ignored(text: str) -> None:
    assert findings(text) == []


def test_quotation_marks_around_a_chinese_expansion_are_ignored() -> None:
    assert findings("本研究採用「結構方程模型」（SEM）。\n") == []
    assert findings("本研究採用『結構方程模型』（SEM）。\n") == []
    text = "本研究採用此方法（「結構方程模型」，SEM）。結構方程模型（SEM）再次被使用。\n"
    assert findings(text) == [("body", 1, "defined_again", "SEM")]
    report = check("SEM（「結構方程模型」）被使用。\n")
    assert rows(report) == [] and report["coverage_limits"][0]["reason"] == "unread_definition_form"


@pytest.mark.parametrize("text", ["As shown in Table IV, the arms differ.\n",
                                  "Patients with stage IV cancer enrolled.\n",
                                  "This phase IV trial ran.\n", "Grade IV glioma was rare.\n",
                                  "Stages III and IV were pooled.\n", "Grades III–IV toxicity was rare.\n",
                                  "Tables II, III, and IV list arms.\n", "第IV期病人較少。\n", "IV 期病人較少。\n",
                                  "Patients with stage-IV disease enrolled.\n",
                                  "Stages I through IV were pooled.\n",
                                  "Stage IIA, IIB, and IIIA tumors.\n",
                                  "Stage IIIB and IV disease.\n", "stage IVA disease.\n",
                                  "As shown in Table\nIV, the arms differ.\n",
                                  "Stages III and\nIV were pooled.\n",
                                  "Patients with stage IIID melanoma enrolled.\n",
                                  "Stages IIID and IV were included.\n",
                                  "Stages IA1, IA2, and IA3 were pooled.\n"])
def test_iv_and_stage_numerals_after_a_numbering_word_are_numerals(text: str) -> None:
    assert findings(text) == []


@pytest.mark.parametrize(("text", "acronym"), [
    ("Patients received IV fluids.\n", "IV"), ("Two types of IV access were used.\n", "IV"),
    ("病人接受 IV 注射。\n", "IV"), ("Patients with IIIB disease.\n", "IIIB"),
    ("Patients with IIID disease.\n", "IIID")])
def test_iv_and_stage_numerals_elsewhere_are_acronyms(text: str, acronym: str) -> None:
    assert findings(text) == [("body", 1, "undefined", acronym)]


@pytest.mark.parametrize(("text", "line"), [
    ("Patients were classified by stage.\n\nIV fluids were administered.\n", 3),
    ("Patients were classified by stage\n\nIV fluids were administered.\n", 3),
    ("Patients were classified by stage. IV fluids were given.\n", 1),
    ("Stages III and\n\nIV were pooled.\n", 3)])
def test_a_numbering_word_stops_at_a_sentence_end_or_a_blank_line(text: str, line: int) -> None:
    assert findings(text) == [("body", line, "undefined", "IV")]


def test_acronyms_shaped_like_leads_stay_acronyms() -> None:
    assert findings("Internet Explorer (IE) crashed. Also known as (AKA) forms vary.\n") == []


@pytest.mark.parametrize("lead", ["例如，", "例如 PCA，", "包括 PCA，"])
def test_a_chinese_example_led_list_is_a_use(lead: str) -> None:
    text = f"我們比較方法（{lead}NMF）。非負矩陣分解（NMF）最佳。\n"
    assert ("body", 1, "defined_after_use", "NMF") in findings(text)


def test_a_word_or_chinese_before_the_acronym_can_still_define_it() -> None:
    assert findings("Doses were given (in vivo, IV) twice.\n") == []
    assert findings("Ratios were used (likelihood ratio, LR). The LR fell.\n") == []
    assert findings("這是設計（試驗，RCT）。本研究使用 RCT。\n") == []
    report = check("We compared fit statistics (adjusted R², AIC).\n")
    assert rows(report) == [] and report["coverage_limits"][0]["acronym"] == "AIC"


def test_acronyms_joined_by_a_slash_hyphen_or_word_form_a_list() -> None:
    for joined in ("PCA/ICA", "PCA and ICA", "PCA and/or ICA", "PCA+ICA", "PCA & ICA"):
        text = ("Principal component analysis (PCA) and independent component analysis (ICA) ran.\n"
                f"We compared them ({joined}, NMF). Nonnegative matrix factorization (NMF) won.\n")
        assert findings(text) == [("body", 2, "defined_after_use", "NMF")], joined
    text = "Cases rose (COVID-19, ARDS) in the ARDS unit.\n"
    assert findings(text, allow=DEFAULT_ALLOWLIST | {"COVID"}) == [("body", 1, "undefined", "ARDS")]
    # An acronym spelled like a joining word stays an acronym.
    text = "We compared estimates (OR, HR). The hazard ratio (HR) decreased.\n"
    assert findings(text, allow=DEFAULT_ALLOWLIST | {"OR"}) == [("body", 1, "defined_after_use", "HR")]
    # Chinese joining words need no spaces.
    for joined in ("PCA與ICA", "PCA 與 ICA", "PCA／ICA"):
        text = f"本研究比較方法（{joined}，NMF）。非負矩陣分解（NMF）效果最佳。\n"
        assert ("body", 1, "defined_after_use", "NMF") in findings(text), joined


def test_plural_and_possessive_count_as_the_base() -> None:
    text = "Large language models (LLMs) help. The LLM's output and two LLMs' outputs.\n"
    report = check(text)
    assert report["findings"] == []
    assert findings("The RCTs and the RCT's arm.\n") == [("body", 1, "undefined", "RCT")]


def test_whole_token_matching() -> None:
    report = check("The AIDS cohort and AI-based tools.\n")
    assert [(f["acronym"], f["occurrences"]) for f in report["findings"]] == [("AI", 1)]


# --- exclusions ------------------------------------------------------------


@pytest.mark.parametrize("label, text", [
    ("code span", "Use `RCT` here.\n"),
    ("code fence", "```\nRCT\n```\n"),
    ("tilde fence", "~~~python\nRCT = 1\n~~~\n"),
    ("html comment", "Text <!-- RCT --> text.\n"),
    ("multi-line comment", "<!-- a\nRCT\n-->\n"),
    ("ref and anchor markers", "A claim.<!--ref:smith2020--><!--anchor:quote:RCT%20arm-->\n"),
    ("front matter", "---\ntitle: RCT\n---\n\nBody.\n"),
    ("heading", "## The RCT\n\nBody.\n"),
    ("reference list", "Body.\n\n## References\n\nSmith, J. (2020). RCT methods. *RCT Journal*.\n"),
    ("table", "| RCT | x |\n|---|---|\n| LLM | y |\n"),
    ("image", "![RCT flow](flow.png)\n"),
    ("figure caption", "Figure 2. The RCT flow\n"),
    ("table caption", "**Table 1**\n"),
    ("note", "*Note.* RCT = randomized controlled trial.\n"),
    ("chinese note", "註：RCT 為隨機對照試驗。\n"),
    ("keywords", "**Keywords**: RCT, LLM\n"),
    ("chinese keywords", "關鍵詞：RCT、LLM\n"),
    ("inline math", "The effect $F_{RCT}$ held.\n"),
    ("display math", "$$\nRCT = 1\n$$\n"),
    ("url", "See https://example.org/RCT and [a link](https://example.org/LLM).\n"),
    ("year citation", "As reported (WHO, 2020), it held.\n"),
    ("citation list", "As shown (see Smith et al., 2020, p. 4; WHO, 2019), it held.\n"),
    ("citation page list", "Earlier work (WHO, 2020, pp. 4, 6) supported this.\n"),
    ("citation section", "As defined (APA, 2020, Section 8.1; WHO, 2019, ch. 3), it held.\n"),
    ("link reference definition", "[RCT]: https://example.org/design\n"),
    ("link destination", "See the [trial protocol](#RCT) and the [notes](<RCT notes.md>).\n"),
    ("link title", "See [the site](https://example.org \"RCT protocol\") and [the page](#a 'RCT').\n"),
    ("full reference link label", "See the [trial protocol][RCT].\n\n[RCT]: https://example.org\n"),
    ("pipe-less table", "Design | Arms\n--- | ---\nRCT | 2\nSEM | 1\n"),
    ("multi-line note", "*Note.* RCT = randomized\ncontrolled trial; SEM = structural model.\n"),
    ("multi-line caption", "Figure 1. The RCT flow,\nwith SEM paths.\n"),
    ("group author", "The World Health Organization [WHO] said so.\n"),
    ("author initials", "Smith JA, Jones BC (2019) agreed, as did Lee KM et al.\n"),
    ("accented author initials", "García AB, Jones EF (2020) agreed.\n"),
    ("accented citation author", "As reported (WHO & Öztürk, 2020), it held.\n"),
    ("supplementary caption", "Figure S1. The RCT flow\n"),
    ("appendix table caption", "Table A.1. The SEM fit\n"),
    ("dotted caption", "Figure 1.2. The RCT flow\n"),
    ("chapter-numbered captions", "Figure 2-1. The RCT flow\n\n圖 3-2：SEM 路徑\n"),
    ("chinese-numeral caption", "表一：RCT 分組\n"),
    ("roman-numbered and all-caps captions",
     "Table III. The RCT arms\n\nTABLE IV\nSEM fit indices\n\nFIG. 2. The GLM flow\n"),
    ("letter-numbered caption", "Figure B. The RCT flow\n"),
    ("prefixed and boxed captions",
     "Supplementary Table 2. The RCT arms\n\nExtended Data Fig. 1. The SEM paths\n\n"
     "Box 1. The GLM terms\n\n附表 1：IRT 參數\n"),
    ("undated citations", "Earlier work (WHO, n.d.-a, n.d.-b; NIH, n.d.) supported this.\n"),
    ("in-press, reprint, and range citations",
     "As argued (WHO, in press-a; APA, 1900/1953; NIH, 1959–1963), it held.\n"),
    ("compound surname initials", "Smith AB, McDonald EF (2020) reported this.\n"),
    ("apostrophe and hyphen surnames", "O'Brien AB, Smith-Jones EF (2020) agreed.\n"),
    ("surname particles", "Smith AB, van der Berg EF, Van Dyke GH (2020) agreed.\n"),
    ("authors joined by and", "Smith AB and Jones EF (2020) reported this.\n"),
    ("serial and", "Smith AB, Jones EF, and Lee GH (2020) agreed.\n"),
    ("ampersand", "Smith AB & Jones EF (2020) agreed.\n"),
    ("vietnamese surnames", "Nguyễn AB and Trần EF (2020) reported this.\n"),
    ("author initials before other date forms",
     "Smith AB and Jones EF (2020a) agreed, as did Lee KM (n.d.) and Park JH (1900/1953).\n"),
    ("statistical symbol", "The SD was 2.1 and the CI was narrow.\n"),
    ("plural statistical symbols", "We report 95% CIs, SDs, and SEs.\n"),
])
def test_exclusions(label: str, text: str) -> None:
    # A prose paragraph after the case keeps the body present (an all-excluded
    # input is not_checked, tested below).
    assert findings(text + "\nThe study ended.\n") == [], label


@pytest.mark.parametrize("text, expected", [
    ("Use \\`RCT\\` here.\n", [("body", 1, "undefined", "RCT")]),  # escaped backticks are literal
    ("An `RCT`` run.\n", [("body", 1, "undefined", "RCT")]),          # unequal runs open no span
    ("A ``RCT`x`` span.\n", []),                                       # a span may hold a backtick
    ("Use `C:\\RCT\\` here.\n", []),     # a backslash inside a span is literal
    ("A \\\\`RCT` span.\n", []),          # an escaped backslash leaves the backtick free
    ("The marker `![alt](flow.png)` adds an image. The RCT ran.\n",  # an image in a span is text
     [("body", 1, "undefined", "RCT")]),
])
def test_code_spans_pair_equal_backtick_runs(text: str, expected: list[tuple]) -> None:
    assert findings(text) == expected


@pytest.mark.parametrize("text", [
    "The marker `<!--` opens a comment. The RCT worked. It closes with `-->`.\n",
    "<!--> The RCT worked. <!-- a note -->\n",           # "<!-->" is a whole comment
    "An escaped \\<!-- marker. The RCT worked. -->\n",   # an escaped "<" opens nothing
    "<!-- a `note --> The RCT worked.\n",                # a comment that starts first holds the backtick
    "It cost \\$5 per RCT arm and \\$10 per site.\n",       # an escaped dollar opens no math
])
def test_comment_and_math_markers_follow_markdown(text: str) -> None:
    assert findings(text) == [("body", 1, "undefined", "RCT")]


def test_a_caption_or_note_starts_a_paragraph() -> None:
    text = "The effect held, as in\nFigure 2. The RCT ran.\nNote. The SEM fit.\n"
    assert findings(text) == [("body", 2, "undefined", "RCT"), ("body", 3, "undefined", "SEM")]
    assert findings("![Flow](flow.png)\nFigure 1. The RCT flow.\n\nThe study ended.\n") == []
    # A supplementary caption's definition does not reach the body, nor does a
    # Chinese caption's.
    text = "Figure S1. Randomized controlled trial (RCT) flow.\n\nThe RCT ended.\n"
    assert findings(text) == [("body", 3, "undefined", "RCT")]
    for label in ("圖一：", "圖 2-1："):
        text = f"{label}隨機對照試驗（RCT）流程。\n\n本研究使用 RCT。\n"
        assert findings(text) == [("body", 3, "undefined", "RCT")], label
    for label in ("Table III. ", "Supplementary Figure S1. ", "Box 1. ", "Figure 1 | ", "Fig. 2 – ",
                  "Figure 3— ", "Figure 4 - ", "Figure 5–", "Figure 6–Comparison. ", "Figure 1 – A ",
                  "圖1–流程。", "Figure 1 – T cell counts. ", "Table I – A summary. ",
                  "Figure 1 – Box plots. ", "Figure 1A – Comparison. ", "圖1 – 圖示流程。", "表1 – 表現比較。",
                  "TABLE II – CI estimates. ", "TABLE I – X-ray findings. ",
                  "Figure 1A – C-reactive protein. ", "TABLE I – XXII cohorts. "):
        text = f"{label}Randomized controlled trial (RCT) results.\n\nThe RCT ended.\n"
        assert findings(text) == [("body", 3, "undefined", "RCT")], label
    # A thematic break ends a paragraph, so a caption or a link definition may follow it.
    assert findings("Intro.\n\n***\nFigure 2. The RCT flow\n\nBody text.\n") == []
    text = "See [RCT].\nA randomized controlled trial (RCT) ran.\n***\n[RCT]: https://example.org\n"
    assert findings(text) == [("body", 1, "defined_after_use", "RCT")]


def test_a_fence_closes_only_on_a_matching_closer() -> None:
    text = ("````\nRCT\n```\nLLM\n~~~~\nSEM\n````  \nThe IRT held.\n"
            "```python\nNLP\n```python\nABC\n    ```\nXYZ\n```\nThe GLM fit.\n")
    assert findings(text) == [("body", 8, "undefined", "IRT"), ("body", 16, "undefined", "GLM")]


def test_a_dotted_figure_number_opening_a_sentence_is_prose() -> None:
    text = "Figure S1.2 shows the RCT arm.\n\nA randomized controlled trial (RCT) ran.\n"
    assert findings(text) == [("body", 1, "defined_after_use", "RCT")]
    assert findings("Table 2.1 lists the SEM fit.\n") == [("body", 1, "undefined", "SEM")]


def test_sentence_start_word_before_an_acronym_is_not_an_author() -> None:
    assert findings("The RCT, conducted in 2020, ended.\n") == [("body", 1, "undefined", "RCT")]
    assert findings("Our RCT (2020) ended.\n") == [("body", 1, "undefined", "RCT")]
    assert findings("Using LLM (2024) helped.\n") == [("body", 1, "undefined", "LLM")]
    assert findings("As Smith JA (2019) and Lee KM et al. showed.\n") == []


def test_prose_shaped_like_an_author_list_is_read_as_one() -> None:
    # A disclosed limit: the author-list rule matches by shape.
    assert findings("Delphi RCT and Bayesian SEM (2020) were compared.\n") == []


def test_years_before_1800_are_not_citation_years() -> None:
    # A disclosed limit: citations and author lists read years from 1800 to 2099.
    assert findings("As reported (WHO, 1799), it held.\n") == [("body", 1, "undefined", "WHO")]
    assert findings("As reported (WHO, 1800), it held.\n") == []


def test_a_parenthetical_with_a_year_is_not_always_a_citation() -> None:
    assert findings("Uptake grew (the RCT ran from 2019 to 2020).\n") == [
        ("body", 1, "undefined", "RCT")]
    text = "We used models (LLM use began in May 2020). A large language model (LLM) helped.\n"
    assert findings(text) == [("body", 1, "defined_after_use", "LLM")]


def test_a_link_label_is_not_a_group_author() -> None:
    text = "We used [RCT](#design). A randomized controlled trial (RCT) ran.\n"
    assert findings(text) == [("body", 1, "defined_after_use", "RCT")]
    assert findings("The Trial [RCT](#x) ran.\n") == [("body", 1, "undefined", "RCT")]
    # A shortcut link: its label has a definition (matched case-insensitively).
    text = "See [RCT].\nA randomized controlled trial (RCT) ran.\n\n[rct]: https://example.org/design\n"
    assert findings(text) == [("body", 1, "defined_after_use", "RCT")]
    # A link whose destination is a URL.
    text = "See [RCT](https://example.org/design). A randomized controlled trial (RCT) ran.\n"
    assert findings(text) == [("body", 1, "defined_after_use", "RCT")]


def test_a_link_destination_title_or_named_label_is_not_a_use() -> None:
    text = ("See the [trial protocol][RCT] and [the design](#RCT \"RCT\").\n\n"
            "A randomized controlled trial (RCT) ran.\n\n[rct]: https://example.org/protocol\n")
    assert findings(text) == []
    # A label that no link reference definition names is shown as text, and so is link text.
    text = "See [1][RCT] and [RCT][1].\n\n[1]: https://example.org\n"
    assert findings(text) == [("body", 1, "undefined", "RCT")]


@pytest.mark.parametrize("target", ["(#trial 'RCT investigator\\'s guide')", '(#trial "RCT \\"guide\\"")',
                                    "(#trial (RCT \\(draft\\) guide))", "(docs/RCT\\)notes.md)",
                                    "(<docs/RCT\\>notes.md>)"])
def test_an_escape_inside_a_link_destination_or_title_does_not_end_it(target: str) -> None:
    # Only the two shown uses count: the one after the link and the definition.
    text = f"See the [protocol]{target} and the RCT.\n\nA randomized controlled trial (RCT) ran.\n"
    [finding] = check(text)["findings"]
    assert (finding["line"], finding["rule"], finding["occurrences"]) == (1, "defined_after_use", 2)


def test_a_link_reference_definition_starts_a_paragraph() -> None:
    text = "[RCT]: https://example.org/design\n\nA randomized controlled trial (RCT) ran.\n"
    assert findings(text) == []
    # Inside a paragraph the same line is text, and its bracket is not a link.
    assert findings("We ran it.\n[RCT]: see the design.\n") == [("body", 2, "undefined", "RCT")]


def test_a_roman_range_above_xxxix_is_prose() -> None:
    # XL stays a candidate (larger numerals are also acronyms), so it is reported too.
    text = "Table XXXIX–XL shows the RCT arms.\n\nA randomized controlled trial (RCT) ran.\n"
    assert sorted(findings(text)) == [("body", 1, "defined_after_use", "RCT"),
                                      ("body", 1, "undefined", "XL")]


def test_caption_word_at_sentence_start_is_still_prose() -> None:
    for text in ("Table 2 shows the RCT arm.\n", "Figure 2-1 shows the RCT arm.\n",
                 "Table III shows the RCT arm.\n", "Box 1 lists the RCT arm.\n",
                 "Fig. 1 Flow diagram of the RCT.\n",  # a disclosed limit: no mark after the number
                 "Tables 2–4 list the RCT arms.\n", "Table 2–4 list the RCT arms.\n",
                 "Figure 1 – 3 show the RCT arm.\n", "圖1–3顯示 RCT 的流程。\n",
                 "Figure 1A–C shows the RCT arm.\n", "Table S1–S3 list the RCT arms.\n",
                 "Table I–III list the RCT arms.\n", "Figure 1—3 show the RCT arm.\n",
                 "圖一–三顯示 RCT 的流程。\n", "Table 1–Table 3 list the RCT arms.\n",
                 "Figure 1–C show the RCT arm.\n", "Table 1-based estimates of the RCT.\n",
                 "Figure 1A – C shows the RCT arm.\n", "Figure 1A—C shows the RCT arm.\n",
                 "Table I – III list the RCT arms.\n", "Table I—III list the RCT arms.\n",
                 "Figure 1—C show the RCT arm.\n", "圖一 – 三顯示 RCT 的流程。\n",
                 "Figure 1 – Figure 3 show the RCT.\n", "圖1–圖3顯示 RCT 的流程。\n",
                 "圖一 – 圖三顯示 RCT 的流程。\n", "表S1—表S3列出 RCT 的分組。\n",
                 "Table I – XXI list the RCT arms.\n",
                 "表一所示的 RCT 分組。\n"):
        assert findings(text) == [("body", 1, "undefined", "RCT")], text


# --- scopes and coverage ---------------------------------------------------


def test_scope_runs_to_the_next_heading_at_its_level() -> None:
    text = ("## English Abstract\n\n### Paper title\n\nThe RCT worked.\n\n"
            "## Chinese Abstract (zh-TW)\n\n這項 LLM 研究。\n\n## Methods\n\nThe SEM fit.\n")
    report = check(text)
    assert rows(report) == [("body", 13, "undefined", "SEM"), ("abstract_en", 5, "undefined", "RCT"),
                            ("abstract_zh", 9, "undefined", "LLM")]
    assert report["scope_lines"] == {"body": [[12, 13]], "abstract_en": [[2, 2], [4, 6]],
                                     "abstract_zh": [[8, 10]]}


def test_setext_headings_set_scopes() -> None:
    text = ("Abstract\n========\n\nThe RCT worked.\n\n"
            "Methods\n=======\n\nA randomized controlled trial (RCT) ran.\n\n---\n\n"
            "- A list item\n---\n\nThe SEM fit.\n")
    assert rows(check(text)) == [("body", 16, "undefined", "SEM"),
                                 ("abstract_en", 4, "undefined", "RCT")]


def test_a_nested_excluded_section_returns_to_its_parent_scope() -> None:
    text = ("## Abstract\n\nThe RCT worked.\n\n### Keywords\n\nSEM, IRT\n\n"
            "### Plain-language summary\n\nThe LLM helped.\n\n## Methods\n\nThe GLM fit.\n")
    assert rows(check(text)) == [("body", 15, "undefined", "GLM"),
                                 ("abstract_en", 3, "undefined", "RCT"),
                                 ("abstract_en", 11, "undefined", "LLM")]


@pytest.mark.parametrize("rule", ["***", "---", "___", " _ _ _"])
def test_a_table_ends_at_a_blank_line_or_another_block(rule: str) -> None:
    assert findings("| a |\n|---|\n| RCT |\n\nThe LLM ran.\n") == [
        ("body", 5, "undefined", "LLM")]
    assert findings("| a |\n|---|\n| x |\n> The RCT ran.\n- The SEM fit.\n") == [
        ("body", 4, "undefined", "RCT"), ("body", 5, "undefined", "SEM")]
    assert findings(f"Intro.\n\n| a |\n|---|\n| x |\n{rule}\nThe RCT worked.\n") == [
        ("body", 7, "undefined", "RCT")]


def test_a_scope_is_present_only_with_prose() -> None:
    report = check("\n## Abstract\n\nThe RCT worked.\n")
    assert report["coverage"] == {"body": "not_in_input", "abstract_en": "checked",
                                  "abstract_zh": "not_in_input"}
    for markers in ("---", "***", "- ", "> ", "| |\n|---|"):
        with pytest.raises(NotChecked):
            check(f"## Abstract\n\n{markers}\n", ("abstract_en",))


def test_unread_abstract_section_makes_coverage_partial() -> None:
    report = check("## Resumen\n\nUn ECA.\n\n## Body\n\nText.\n")
    assert report["unread_sections"] == [{"line": 1, "heading": "Resumen"}]
    assert report["status"] == "partial" and report["findings"] == []


def test_requested_scope_absent_from_the_input() -> None:
    report = check("Body text.\n", ("body", "abstract_en"))
    assert report["coverage"] == {"body": "checked", "abstract_en": "not_in_input",
                                  "abstract_zh": "not_requested"}
    assert report["status"] == "partial"


def test_unrequested_scope_is_not_read() -> None:
    text = "## Abstract\n\nThe RCT.\n\n## Body\n\nText.\n"
    assert findings(text, scopes=("body",)) == []


# --- clean versus not checked ------------------------------------------------


def _write(tmp_path: Path, name: str, data: bytes) -> Path:
    path = tmp_path / name
    path.write_bytes(data)
    return path


def test_clean_result_is_distinct_from_not_checked(tmp_path: Path) -> None:
    clean = build_report(_write(tmp_path, "m.md", b"A randomized controlled trial (RCT).\n"),
                         "body", [], None)
    assert (clean["status"], clean["findings"]) == ("checked", [])
    assert "reason" not in clean
    assert render(clean, "en").endswith("Coverage: body (complete)\nNo findings.")
    cases = {
        "unsupported_format": (_write(tmp_path, "m.docx", b"PK"), "body"),
        "unreadable_input": (_write(tmp_path, "bad.md", b"\xff\xfe RCT"), "body"),
        "unknown_scope": (_write(tmp_path, "ok.md", b"RCT\n"), "body,methods"),
        "no_requested_scope_in_input": (_write(tmp_path, "body.md", b"Body only.\n"), "abstract_zh"),
    }
    for reason, (path, scopes) in cases.items():
        report = build_report(path, scopes, [], None)
        assert (report["status"], report["reason"]) == ("not_checked", reason)
        assert "findings" not in report
        assert render(report, "en").splitlines()[1].startswith("Not checked: ")
        assert render(report, "zh-TW").splitlines()[1].startswith("未檢查：")
    missing = build_report(tmp_path / "absent.md", "body", [], None)
    assert missing["reason"] == "unreadable_input"
    for i, empty in enumerate((b"", b"\n\n", b"## Methods\n", b"```\nRCT\n```\n")):
        report = build_report(_write(tmp_path, f"empty{i}.md", empty), "body", [], None)
        assert (report["status"], report["reason"]) == ("not_checked", "no_requested_scope_in_input")


def test_cli_exit_codes_and_outputs(tmp_path: Path) -> None:
    manuscript = _write(tmp_path, "m.md", b"We ran an RCT.\n")
    out = tmp_path / "report.json"
    result = run_script(SCRIPT, "--input", str(manuscript), "--json-out", str(out))
    assert result.returncode == 0, result.stderr
    assert "| Body | 1 | Not defined | RCT | 1 |" in result.stdout
    assert json.loads(out.read_text(encoding="utf-8"))["findings"][0]["acronym"] == "RCT"
    result = run_script(SCRIPT, "--input", str(_write(tmp_path, "m.pdf", b"%PDF")))
    assert result.returncode == 2 and "Not checked:" in result.stdout


def test_json_out_may_not_overwrite_an_input(tmp_path: Path) -> None:
    manuscript = _write(tmp_path, "m.md", b"We ran an RCT.\n")
    allow = _write(tmp_path, "allow.txt", b"SEM\n")
    os.link(manuscript, tmp_path / "hard-link.md")
    for target in (manuscript, allow, tmp_path / "hard-link.md"):
        result = run_script(SCRIPT, "--input", str(manuscript), "--allow-file", str(allow),
                            "--json-out", str(target))
        assert result.returncode == 2
        assert "may not be the input file or the allowlist file" in result.stderr
    assert (manuscript.read_bytes(), allow.read_bytes()) == (b"We ran an RCT.\n", b"SEM\n")


# --- fidelity and determinism -------------------------------------------------


def test_full_fixture_matches_the_pinned_reports(tmp_path: Path) -> None:
    source = FIXTURES / "manuscript.md"
    before = source.read_bytes()
    report = build_report(source, ",".join(SCOPES), [], None)
    assert source.read_bytes() == before  # the checker never edits the manuscript
    assert report.pop("input") == str(source)
    assert report["input_sha256"] == hashlib.sha256(before).hexdigest()
    pinned = (FIXTURES / "expected.json").read_text(encoding="utf-8")
    assert json.dumps(report, ensure_ascii=False, indent=2) + "\n" == pinned
    for lang in ("en", "zh-TW"):
        pinned = (FIXTURES / f"expected.{lang}.md").read_text(encoding="utf-8")
        assert render(report, lang) + "\n" == pinned


def test_source_lines_survive_masking() -> None:
    text = ("<!-- one\ntwo\nthree -->\n```\ncode\n```\n---\n\nThe RCT ran.\n")
    assert findings(text) == [("body", 9, "undefined", "RCT")]
    lines = (FIXTURES / "manuscript.md").read_text(encoding="utf-8").split("\n")
    report = json.loads((FIXTURES / "expected.json").read_text(encoding="utf-8"))
    for finding in report["findings"]:
        assert finding["acronym"] in lines[finding["line"] - 1], finding


def test_ordering_is_deterministic() -> None:
    text = ("## 摘要\n\nLLM。\n\n## Abstract\n\nThe SEM and the RCT.\n\n## Body\n\n"
            "ZZZ then AAA.\n")
    first = check(text)
    assert first == check(text)
    assert rows(first) == [("body", 11, "undefined", "AAA"), ("body", 11, "undefined", "ZZZ"),
                              ("abstract_en", 7, "undefined", "RCT"),
                              ("abstract_en", 7, "undefined", "SEM"),
                              ("abstract_zh", 3, "undefined", "LLM")]


def test_crlf_input_keeps_line_numbers(tmp_path: Path) -> None:
    path = _write(tmp_path, "m.md", b"First line.\r\n\r\nThe RCT ran.\r\n")
    report = build_report(path, "body", [], None)
    assert report["findings"][0]["line"] == 3


# --- the review letter's attachment (#849, reviewer side) ----------------------

ATTACHMENT_HEADING = "## Attachment: Acronym Check (advisory, #849)"
DECISION_TEMPLATE = REPO / "academic-paper-reviewer" / "templates" / "editorial_decision_template.md"


def _attachment(lang: str) -> str:
    """The letter's last section, as the dispatching session appends it."""
    report = (FIXTURES / f"expected.{lang}.md").read_text(encoding="utf-8")
    return f"\n---\n\n{ATTACHMENT_HEADING}\n\n{report}"


@pytest.mark.parametrize("lang", ["en", "zh-TW"])
def test_the_attachment_leaves_the_panel_decision_unchanged(lang: str) -> None:
    from scripts import check_panel_synthesis as cps
    from scripts.test_check_panel_synthesis import FULL, reports, synthesis_for

    # The checker reads the synthesis only through parse_synthesis and layer2_check.
    panel = reports()
    synthesis, expressions = synthesis_for(panel)
    parsed = cps.parse_synthesis("s.md", synthesis + "\n" + _attachment(lang), FULL)
    assert parsed == cps.parse_synthesis("s.md", synthesis, FULL)
    assert cps.layer2_check(panel, FULL, expressions, parsed, []) == []


def test_the_attachment_leaves_the_re_review_letter_extraction_unchanged() -> None:
    from scripts.check_re_review_synthesis import parse_letter_blocks

    # The Required Item Details section is the letter's last one here, so only the
    # attachment's own heading ends it.
    letter = ("# Editorial Decision\n\n## Required Revisions * (Must Fix)\n\n"
              "### Required Item Details\n\n"
              "**R1: Sample size justification**\n"
              "- **Acceptance criteria**: A formal power analysis appears in Methods §3.2.\n\n"
              "**R2: Missing limitation**\n"
              "- **Acceptance criteria**: A limitations paragraph names the bounds.\n")
    blocks = parse_letter_blocks(letter)
    assert [rid for rid, _ in blocks] == ["R1", "R2"]
    for lang in ("en", "zh-TW"):
        assert parse_letter_blocks(letter + _attachment(lang)) == blocks


def test_the_template_ends_the_letter_with_the_attachment() -> None:
    text = DECISION_TEMPLATE.read_text(encoding="utf-8")
    start = text.index("```markdown\n")
    letter = text[start:text.index("\n```\n", start)]
    assert [line for line in letter.split("\n") if line.startswith("## ")][-1] == ATTACHMENT_HEADING
    assert "Leave this section out" in letter[letter.index(ATTACHMENT_HEADING):]
    skill = (REPO / "academic-paper-reviewer" / "SKILL.md").read_text(encoding="utf-8")
    assert f"`{ATTACHMENT_HEADING}`" in skill
