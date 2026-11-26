"""Pin PDF compilation, retained uncited entries, and MLA 9 cells (#1192–1194)."""

from tests.test_formatter_1071 import FORMATTER, _rows_with_first_cell


def test_pdf_uses_generated_tex_and_biber() -> None:
    text = FORMATTER.read_text(encoding="utf-8")
    overview = text.split("### 4. PDF (via LaTeX)\n", 1)[1].split("\n### ", 1)[0]
    assert "generated `paper.tex` and its `references.bib`" in overview
    assert "Stage 5 confirmation before compilation" in overview

    commands = text.split("### Conversion Commands (if applicable)\n", 1)[1]
    commands = commands.split("\n```", 1)[0]
    assert (
        "- PDF: Run `xelatex paper.tex && biber paper && xelatex paper.tex "
        "&& xelatex paper.tex` in the directory containing the generated "
        "`paper.tex` and `references.bib`."
    ) in commands
    assert "pandoc paper.md -o paper.pdf" not in text
    assert "pandoc input.md -o output.pdf" not in text


def test_latex_retains_uncited_entries_before_printing_bibliography() -> None:
    text = FORMATTER.read_text(encoding="utf-8")
    template = text.split("**LaTeX document structure template**:", 1)[1]
    block = template.split("```latex\n", 1)[1].split("\n```", 1)[0]
    assert r"\addbibresource{references.bib}" in block
    assert (
        "% Body sections\n"
        r"% In full mode, insert one \nocite{key} here for each retained "
        "reference-list entry with no in-text citation, in incoming reference-list "
        "order. Replace key with the entry's actual key from references.bib.\n"
        r"\printbibliography"
    ) in block


def test_docx_passes_explicit_retained_keys_to_citeproc() -> None:
    text = FORMATTER.read_text(encoding="utf-8")
    section = text.split("### Markdown -> DOCX Conversion Rules\n", 1)[1]
    section = section.split("**Style Mapping", 1)[0]
    assert (
        "In `full` mode, when the incoming reference list retains entries "
        "with no in-text citation, use the citation-processing command below."
    ) in section
    assert "```yaml\n---\nnocite: |\n  @FirstKey, @SecondKey\n---\n```" in section
    assert "Use explicit keys only." in section
    assert "--citeproc \\\n  --bibliography=references.bib" in section
    assert (
        "For Chinese DOCX output in this case, use the same citation-processing "
        "command with `--reference-doc=template_zh.docx`."
    ) in section
    assert (
        "- DOCX: Provide the applicable command from Markdown -> DOCX Conversion "
        "Rules, including the citation-processing command and `nocite` metadata "
        "when `full` mode retains uncited entries."
    ) in text


def test_mla_journal_year_and_doi_cells() -> None:
    text = FORMATTER.read_text(encoding="utf-8")
    features = text.split("### Format-Specific Features\n", 1)[1].split("\n### ", 1)[0]
    header = next(line for line in features.splitlines() if line.startswith("|"))
    columns = [cell.strip() for cell in header.strip("|").split("|")]
    mla = columns.index("MLA 9")
    for label, expected in (
        ("Year position", "After volume and issue, before pages and DOI (journal article)"),
        ("DOI format", "https://doi.org/..."),
    ):
        rows = _rows_with_first_cell(features, label)
        assert len(rows) == 1
        cells = [cell.strip() for cell in rows[0].strip("|").split("|")]
        assert cells[mla] == expected
