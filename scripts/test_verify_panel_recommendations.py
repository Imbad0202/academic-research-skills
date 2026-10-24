#!/usr/bin/env python3
"""Tests for scripts/verify_panel_recommendations.py (#1001).

Resolver clients are MagicMocks, so no test makes a network call. Reports are
synthetic text written to tmp_path.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from unittest.mock import MagicMock

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT / "scripts") not in sys.path:
    sys.path.insert(0, str(REPO_ROOT / "scripts"))

import verify_panel_recommendations as vpr  # noqa: E402

AGENT_FILES = (
    "academic-paper-reviewer/agents/domain_reviewer_agent.md",
    "academic-paper-reviewer/agents/perspective_reviewer_agent.md",
)


@pytest.fixture(autouse=True)
def _isolated_cache(tmp_path, monkeypatch):
    """The check runs live; point the cache at tmp_path to prove it is not written."""
    monkeypatch.setenv("ARS_VERIFICATION_CACHE_PATH", str(tmp_path / "cache.db"))
    monkeypatch.delenv("ARS_CACHE_REVALIDATE", raising=False)


def _miss():
    m = MagicMock()
    m.doi_lookup_with_title_check.return_value = None
    m.title_search.return_value = None
    m.arxiv_id_lookup.return_value = None
    m.lookup.return_value = {"matched": False}
    return m


def _clients(**overrides):
    clients = {name: _miss() for name in ("crossref", "openalex", "semantic_scholar", "arxiv")}
    clients.update(overrides)
    return clients


def _factory(clients):
    return lambda: clients


def _write(tmp_path, name, text):
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return path


BLOCK = """#### Missing Key References
- Davis (1989) is the origin of the construct.

~~~yaml suggested-references
- title: "Perceived usefulness, perceived ease of use, and user acceptance of information technology"
  authors: ["Davis, F. D."]
  year: 1989
  doi: "https://doi.org/10.2307/249008"
  arxiv_id: null
~~~
"""


# ---------- reading the blocks ----------


def test_tilde_and_backtick_fences_are_both_read():
    text = ("~~~yaml suggested-references\n- title: A\n~~~\n"
            "```yaml suggested-references\n- title: B\n```\n")
    assert vpr.extract_blocks(text) == ["- title: A", "- title: B"]


def test_untagged_yaml_fence_is_ignored():
    assert vpr.extract_blocks("```yaml\n- title: A\n```\n") == []


def test_block_inside_a_markdown_wrapper_is_found():
    text = "```markdown\n## Report\n~~~yaml suggested-references\n- title: A\n~~~\n```\n"
    assert vpr.extract_blocks(text) == ["- title: A"]


def test_indented_block_loses_its_indent():
    text = "- item\n   ~~~yaml suggested-references\n   - title: A\n     year: 2020\n   ~~~\n"
    assert vpr.extract_blocks(text) == ["- title: A\n  year: 2020"]


def test_closing_fence_must_match_character_and_length():
    text = "````yaml suggested-references\n- title: A\n```\n````\n"
    assert vpr.extract_blocks(text) == ["- title: A\n```"]


def test_a_deeper_indented_fence_line_is_block_content():
    text = ("~~~yaml suggested-references\n- title: |\n    Alpha\n    ~~~\n    Omega\n~~~\n")
    assert vpr.extract_blocks(text) == ["- title: |\n    Alpha\n    ~~~\n    Omega"]


def test_tab_and_space_indents_compare_by_column():
    text = "\t~~~yaml suggested-references\n\t- title: A\n\t  year: 2020\n     ~~~\n"
    assert vpr.extract_blocks(text) == ["- title: A\n  year: 2020"]


def test_a_less_indented_body_line_keeps_its_inner_indent():
    text = "    ~~~yaml suggested-references\n  - title: A\n    year: 2020\n    ~~~\n"
    assert vpr.extract_blocks(text) == ["- title: A\nyear: 2020"]


def test_unclosed_block_runs_to_the_end():
    assert vpr.extract_blocks("~~~yaml suggested-references\n- title: A\n") == ["- title: A\n"]


def test_scalars_keep_the_text_the_reviewer_wrote(tmp_path):
    report = _write(tmp_path, "r.md", "~~~yaml suggested-references\n"
                    "- title: X\n  arxiv_id: 2401.10230\n  year: '2024'\n  doi: ~\n"
                    "- title: Y\n  arxiv_id: arXiv:2401.00001\n  doi: doi:10.1/ABC\n  year: soon\n"
                    "- title: Z\n  year: \"\u00b2\u2070\u00b2\u2074\"\n~~~\n")
    _record, items, problems = vpr.read_report("R2", report)
    assert problems == []
    assert items[0]["arxiv_id"] == "2401.10230"
    assert items[0]["year"] == 2024 and items[0]["doi"] is None
    assert items[1]["arxiv_id"] == "2401.00001"
    assert items[1]["doi"] == "10.1/ABC" and items[1]["year"] is None
    assert items[2]["year"] is None  # superscript digits are not a year


def test_item_without_title_or_mapping_is_listed_not_looked_up(tmp_path):
    report = _write(tmp_path, "r.md", "~~~yaml suggested-references\n"
                    "- authors: [A]\n- just a string\n- title: Kept\n~~~\n")
    _record, items, problems = vpr.read_report("R3", report)
    assert [i["title"] for i in items] == ["Kept"]
    assert items[0]["index"] == 3
    assert problems == [{"seat": "R3", "index": 1, "reason": "no_title"},
                        {"seat": "R3", "index": 2, "reason": "not_a_mapping"}]


# ---------- results ----------


def test_doi_and_title_match_is_found(tmp_path):
    cr = _miss()
    cr.doi_lookup_with_title_check.return_value = {"title": ["Perceived usefulness"]}
    report = vpr.build_report([("R2", _write(tmp_path, "r2.md", BLOCK))], _factory(_clients(crossref=cr)))
    assert report["status"] == "checked"
    assert report["items"][0]["result"] == "found"
    cr.doi_lookup_with_title_check.assert_called_once()
    assert cr.doi_lookup_with_title_check.call_args.args[0] == "10.2307/249008"


def test_unresolved_doi_is_id_not_found(tmp_path):
    report = vpr.build_report([("R2", _write(tmp_path, "r2.md", BLOCK))], _factory(_clients()))
    assert report["items"][0]["result"] == "id_not_found"


def test_title_only_miss_is_title_not_found(tmp_path):
    text = "~~~yaml suggested-references\n- title: Some unindexed report\n~~~\n"
    report = vpr.build_report([("R3", _write(tmp_path, "r3.md", text))], _factory(_clients()))
    assert report["status"] == "checked"
    assert report["items"][0]["result"] == "title_not_found"


def test_no_index_answering_is_no_answer_and_partial(tmp_path):
    from crossref_client import CrossrefUnavailable
    from openalex_client import OpenAlexUnavailable
    from contamination_signals import SemanticScholarUnavailable

    def down(exc):
        m = _miss()
        m.doi_lookup_with_title_check.side_effect = exc("down")
        m.title_search.side_effect = exc("down")
        m.lookup.side_effect = exc("down")
        return m

    clients = _clients(crossref=down(CrossrefUnavailable), openalex=down(OpenAlexUnavailable),
                       semantic_scholar=down(SemanticScholarUnavailable))
    text = "~~~yaml suggested-references\n- title: T\n~~~\n"
    report = vpr.build_report([("R2", _write(tmp_path, "r.md", text))], _factory(clients))
    item = report["items"][0]
    assert item["result"] == "no_answer"
    assert item["resolver_outcomes"] is not None  # the gate ran; not the catch-all
    assert {k: v["status"] for k, v in item["resolver_outcomes"].items()} == {
        "crossref": "unreachable", "openalex": "unreachable",
        "semantic_scholar": "unreachable", "arxiv": "skipped"}
    assert report["status"] == "partial"


def test_an_unanswered_identifier_is_not_called_title_only(tmp_path):
    from arxiv_client import ArxivUnavailable

    ax = _miss()
    ax.arxiv_id_lookup.side_effect = ArxivUnavailable("down")
    ax.title_search.side_effect = ArxivUnavailable("down")
    text = "~~~yaml suggested-references\n- title: T\n  arxiv_id: '2401.00001'\n~~~\n"
    report = vpr.build_report([("R2", _write(tmp_path, "r.md", text))], _factory(_clients(arxiv=ax)))
    item = report["items"][0]
    assert item["resolver_outcomes"]["arxiv"]["status"] == "unreachable"
    assert item["result"] == "no_answer"


def test_unexpected_lookup_error_is_no_answer(tmp_path):
    cr = _miss()
    cr.title_search.side_effect = RuntimeError("boom")
    text = "~~~yaml suggested-references\n- title: T\n~~~\n"
    report = vpr.build_report([("R2", _write(tmp_path, "r.md", text))], _factory(_clients(crossref=cr)))
    assert report["items"][0]["result"] == "no_answer"
    assert report["items"][0]["resolver_outcomes"] is None


def test_same_reference_from_two_seats_is_looked_up_once(tmp_path):
    cr = _miss()
    clients = _clients(crossref=cr)
    report = vpr.build_report([("R2", _write(tmp_path, "r2.md", BLOCK)),
                               ("R3", _write(tmp_path, "r3.md", BLOCK))], _factory(clients))
    assert [i["seat"] for i in report["items"]] == ["R2", "R3"]
    assert cr.doi_lookup_with_title_check.call_count == 1


def test_the_verification_cache_is_not_written(tmp_path):
    vpr.build_report([("R2", _write(tmp_path, "r2.md", BLOCK))], _factory(_clients()))
    assert not (tmp_path / "cache.db").exists()


# ---------- coverage ----------


def test_missing_block_and_bad_yaml_make_the_report_partial(tmp_path):
    r2 = _write(tmp_path, "r2.md", "#### Missing Key References\n- none named\n")
    r3 = _write(tmp_path, "r3.md", "~~~yaml suggested-references\n- title: [unclosed\n~~~\n"
                "~~~yaml suggested-references\ntitle: not a list\n~~~\n")
    report = vpr.build_report([("R2", r2), ("R3", r3)], _factory(_clients()))
    assert report["status"] == "partial"
    assert report["reports"][0]["problems"] == [{"kind": "missing"}]
    assert report["reports"][1]["problems"] == [{"kind": "bad_yaml", "block": 1},
                                                {"kind": "not_a_list", "block": 2}]
    out = vpr.render(report, "en")
    assert "- R2: the report has no suggested-references block." in out
    assert "- R3: block 1 is not valid YAML." in out
    assert "No suggested reference could be read." in out
    assert "No seat recommends a specific work." not in out


@pytest.mark.parametrize("body", ["", "# nothing listed yet"])
def test_an_empty_block_is_not_a_no_suggestion_answer(tmp_path, body):
    text = f"~~~yaml suggested-references\n{body}\n~~~\n"
    report = vpr.build_report([("R2", _write(tmp_path, "r.md", text))], _factory(_clients()))
    assert report["status"] == "partial"
    assert report["reports"][0]["problems"] == [{"kind": "empty_block", "block": 1}]
    assert "No seat recommends a specific work." not in vpr.render(report, "en")


def test_empty_list_is_a_complete_answer(tmp_path):
    text = "~~~yaml suggested-references\n[]\n~~~\n"
    clients = _clients()
    report = vpr.build_report([("R2", _write(tmp_path, "r.md", text))], _factory(clients))
    assert report["status"] == "checked" and report["items"] == []
    assert clients["crossref"].title_search.call_count == 0


def test_unreadable_reports_are_not_checked(tmp_path):
    report = vpr.build_report([("R2", tmp_path / "absent.md")], _factory(_clients()))
    assert report["status"] == "not_checked"
    assert vpr.render(report, "en").endswith("Not checked: no reviewer report file could be read.")


def test_one_unreadable_report_of_two_is_partial(tmp_path):
    report = vpr.build_report([("R2", tmp_path / "absent.md"),
                               ("R3", _write(tmp_path, "r3.md", BLOCK))], _factory(_clients()))
    assert report["status"] == "partial"
    out = vpr.render(report, "en")
    assert "- R2: the report file could not be read." in out
    assert "Seats read: R3 (partial)." in out
    assert "已讀審稿席次：R3（部分）。" in vpr.render(report, "zh-TW")


# ---------- rendering and CLI ----------


def test_table_cells_escape_pipes_and_line_breaks(tmp_path):
    text = "~~~yaml suggested-references\n- title: \"A | B\"\n  authors: [\"Lee, J.\", \"Park, S.\"]\n  year: 2019\n~~~\n"
    report = vpr.build_report([("R2", _write(tmp_path, "r.md", text))], _factory(_clients()))
    row = [line for line in vpr.render(report, "en").splitlines() if line.startswith("| R2")][0]
    assert row == '| R2 | 1 | Lee, J. et al. (2019) "A \\| B" | Title not matched; no DOI or arXiv ID to check |'


def test_table_cells_render_markdown_and_html_as_literal_text(tmp_path):
    title = 'See ![p](https://example.org/x.png) <!-- hidden --> a\\|b *c* `d`'
    text = "~~~yaml suggested-references\n- title: " + json.dumps(title) + "\n~~~\n"
    report = vpr.build_report([("R2", _write(tmp_path, "r.md", text))], _factory(_clients()))
    row = [line for line in vpr.render(report, "en").splitlines() if line.startswith("| R2")][0]
    cell = row.split(" | ")[2]
    assert cell == ('"See !\\[p\\](https://example.org/x.png) &lt;!-- hidden --&gt; '
                    'a\\\\\\|b \\*c\\* \\`d\\`"')


def test_zh_tw_report(tmp_path):
    report = vpr.build_report([("R2", _write(tmp_path, "r.md", BLOCK))], _factory(_clients()))
    out = vpr.render(report, "zh-TW")
    assert out.splitlines()[0] == "建議文獻查核（腳本輸出，不是審稿意見；#1001）"
    assert "DOI 或 arXiv 編號查不到，標題也比對不到" in out


def test_cli_exit_codes_and_json(tmp_path, capsys):
    r2 = _write(tmp_path, "r2.md", BLOCK)
    out_json = tmp_path / "out.json"
    assert vpr.main(["--report", f"R2={r2}", "--json-out", str(out_json)], _factory(_clients())) == 0
    data = json.loads(out_json.read_text(encoding="utf-8"))
    assert data["checker"] == vpr.CHECKER and data["items"][0]["result"] == "id_not_found"
    assert vpr.main(["--report", f"R2={tmp_path / 'none.md'}"], _factory(_clients())) == 2
    capsys.readouterr()


def test_cli_rejects_bad_seat_and_json_over_a_report(tmp_path):
    r2 = _write(tmp_path, "r2.md", BLOCK)
    with pytest.raises(SystemExit):
        vpr.main(["--report", f"R 2={r2}"], _factory(_clients()))
    with pytest.raises(SystemExit):
        vpr.main(["--report", f"R2={r2}", "--json-out", str(r2)], _factory(_clients()))


# ---------- the reviewer prompts ----------


@pytest.mark.parametrize("relpath", AGENT_FILES)
def test_agent_prompt_shows_exactly_one_readable_block(relpath):
    """Each reviewer prompt shows the block in its output template; the script
    must read that example, or the reviewer copies a shape the script ignores."""
    text = (REPO_ROOT / relpath).read_text(encoding="utf-8")
    blocks = vpr.extract_blocks(text)
    assert len(blocks) == 1
    import yaml
    data = yaml.load(blocks[0], Loader=yaml.BaseLoader)
    assert isinstance(data, list) and set(data[0]) == {"title", "authors", "year", "doi", "arxiv_id"}


# ---------- the review letter's attachment ----------

ATTACHMENT_HEADING = "## Attachment: Suggested-Reference Check (advisory, #1001)"
ACRONYM_HEADING = "## Attachment: Acronym Check (advisory, #849)"
DECISION_TEMPLATE = REPO_ROOT / "academic-paper-reviewer" / "templates" / "editorial_decision_template.md"


def _attachment(tmp_path, lang):
    """The section as the dispatching session appends it, from a synthetic report."""
    r2 = _write(tmp_path, "r2.md", BLOCK)
    r3 = _write(tmp_path, "r3.md", "#### Cross-Disciplinary Reading Recommendations\n- none\n")
    report = vpr.build_report([("R2", r2), ("R3", r3)], _factory(_clients()))
    return f"\n---\n\n{ATTACHMENT_HEADING}\n\n{vpr.render(report, lang)}"


@pytest.mark.parametrize("lang", ["en", "zh-TW"])
def test_the_attachment_leaves_the_panel_decision_unchanged(tmp_path, lang):
    from scripts import check_panel_synthesis as cps
    from scripts.test_check_panel_synthesis import FULL, reports, synthesis_for

    panel = reports()
    synthesis, expressions = synthesis_for(panel)
    parsed = cps.parse_synthesis("s.md", synthesis + "\n" + _attachment(tmp_path, lang), FULL)
    assert parsed == cps.parse_synthesis("s.md", synthesis, FULL)
    assert cps.layer2_check(panel, FULL, expressions, parsed, []) == []


def test_the_attachment_leaves_the_re_review_letter_extraction_unchanged(tmp_path):
    from scripts.check_re_review_synthesis import parse_letter_blocks

    letter = ("# Editorial Decision\n\n## Required Revisions * (Must Fix)\n\n"
              "### Required Item Details\n\n"
              "**R1: Sample size justification**\n"
              "- **Acceptance criteria**: A formal power analysis appears in Methods §3.2.\n")
    blocks = parse_letter_blocks(letter)
    assert [rid for rid, _ in blocks] == ["R1"]
    for lang in ("en", "zh-TW"):
        assert parse_letter_blocks(letter + _attachment(tmp_path, lang)) == blocks


def test_the_template_puts_the_attachment_before_the_claim_check_and_the_acronym_check():
    text = DECISION_TEMPLATE.read_text(encoding="utf-8")
    start = text.index("```markdown\n")
    letter = text[start:text.index("\n```\n", start)]
    headings = [line for line in letter.split("\n") if line.startswith("## ")]
    assert headings[-3:] == [ATTACHMENT_HEADING, "## Attachment: Reviewer Claim Check (advisory, #1002)", ACRONYM_HEADING]
    skill = (REPO_ROOT / "academic-paper-reviewer" / "SKILL.md").read_text(encoding="utf-8")
    assert f"`{ATTACHMENT_HEADING}`" in skill
    assert "before the acronym check attachment, which stays the letter's last write" in skill
