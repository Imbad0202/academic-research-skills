"""Pin PDF backend selection, retained LaTeX entries, basic DOCX, and MLA 9 cells (#1192–1194)."""

from tests.test_formatter_1071 import FORMATTER, _rows_with_first_cell

BIBER_SEQUENCE = (
    "xelatex paper.tex && biber paper && xelatex paper.tex && xelatex paper.tex"
)
BIBTEX_SEQUENCE = (
    "xelatex paper.tex && bibtex paper && xelatex paper.tex && xelatex paper.tex"
)

BIBER_RULE = (
    "For biblatex with its default or explicit Biber backend, including a "
    "style package that loads biblatex, run `" + BIBER_SEQUENCE + "`. The "
    "biblatex option `natbib=true` enables `\\citep` and `\\citet` and does "
    "not select BibTeX."
)
BIBTEX_RULE = (
    "For a template using `\\bibliography{...}` with BibTeX, run `"
    + BIBTEX_SEQUENCE
    + "`. This includes the natbib reference template, "
    "`\\documentclass[man,12pt,natbib]{apa7}`, and journal templates that use "
    "this bibliography interface. Also use BibTeX if the generated biblatex "
    "configuration explicitly selects `backend=bibtex`."
)
TECTONIC_RULE = (
    "- When tectonic is installed, run `tectonic paper.tex`. For a biblatex "
    "file using its default or explicit Biber backend, also install `biber`: "
    "tectonic calls it during the build."
)
OTHERWISE_LINE = (
    "- Otherwise, use XeLaTeX and select the bibliography backend from the "
    "generated `paper.tex`:"
)
COMPILABILITY_ROW = (
    "| LaTeX compilability | The selected build command under PDF (via LaTeX) "
    "completes without errors (warnings acceptable) | Fix compilation errors |"
)

PDF_DELIVERY_LINE = (
    "- PDF: When the formatter does not deliver a requested compiled PDF, "
    "deliver `paper.tex` and `references.bib`. Give a build command only "
    "when both files are delivered, to run in the directory containing both "
    "files. If the formatter compiled the PDF, give the command it used. If "
    "it did not, give both routes under PDF (via LaTeX): `tectonic paper.tex`, "
    "and the XeLaTeX sequence for the bibliography backend of the generated "
    "`paper.tex`. For zh-TW content, configure the CJK font in `paper.tex` "
    "before compilation."
)
PDF_SOURCE_DELIVERY_LINES = (
    "      │            deliver paper.tex and references.bib when "
    "output_format includes LaTeX or Combined,\n"
    "      │            or when output_format includes PDF and the "
    "formatter does not deliver a compiled PDF"
)

APA_BIBTEX_PROSE = (
    "- When tectonic is installed, run `tectonic paper.tex`. The mandatory "
    "`apa7` class option `natbib` uses BibTeX, which tectonic runs itself.\n"
    "- Otherwise, compile the generated APA `paper.tex` with XeLaTeX and "
    "BibTeX:"
)

CHINESE_COMPILE = (
    "% Compile using the command under PDF (via LaTeX) for this paper.tex."
)

NOCITE_RULE = (
    "In `full` mode, for every LaTeX template, insert one `\\nocite{key}` for "
    "each retained reference-list entry with no in-text citation. Use the "
    "entry's actual key from `references.bib`. Place these commands after the "
    "body citations and before the template's bibliography command "
    "(`\\printbibliography` or `\\bibliography{...}`). Emit the keys in the "
    "order the entries take in the converted reference list. For IEEE and "
    "Vancouver, use ascending final reference number. When converting from "
    "APA 7, Chicago, or MLA 9 to a numbered style, number uncited entries "
    "after all cited entries, in their original reference-list order, as "
    "specified under Handling Numbered References."
)

DOCX_BASIC_BULLET = (
    "- Use Pandoc command: `pandoc input.md -o output.docx "
    "--reference-doc=template.docx`"
)
DOCX_COMMANDS_LINE = (
    "- DOCX: `pandoc paper.md -o paper.docx --reference-doc=template.docx`"
)
BASIC_PANDOC = "pandoc paper.md -o paper.docx --reference-doc=template.docx"

CHICAGO_FROM_BULLET = (
    "- If the note retains other text or a verbatim citation, convert the "
    "citations that can be converted inside the note and keep the note and "
    "its marker. Only when the note held nothing but citations that were "
    "converted, move those citations into the text and remove the note and "
    "its marker."
)


def test_pdf_selects_backend_from_generated_tex() -> None:
    text = FORMATTER.read_text(encoding="utf-8")
    overview = text.split("### 4. PDF (via LaTeX)\n", 1)[1].split("\n### ", 1)[0]
    assert "generated `paper.tex` and its `references.bib`" in overview
    assert "Stage 5 confirmation before compilation" in overview
    assert TECTONIC_RULE in overview.splitlines()
    assert OTHERWISE_LINE in overview.splitlines()
    otherwise_at = overview.index(OTHERWISE_LINE)
    assert otherwise_at < overview.index(BIBER_RULE)
    assert otherwise_at < overview.index(BIBTEX_RULE)
    assert BIBER_RULE in overview
    assert BIBTEX_RULE in overview
    assert overview.count(BIBER_SEQUENCE) == 1
    assert overview.count(BIBTEX_SEQUENCE) == 1
    assert BIBER_SEQUENCE in BIBER_RULE
    assert BIBTEX_SEQUENCE in BIBTEX_RULE
    assert BIBER_SEQUENCE not in BIBTEX_RULE
    assert BIBTEX_SEQUENCE not in BIBER_RULE
    assert "pandoc paper.md -o paper.pdf" not in text
    assert "pandoc input.md -o output.pdf" not in text
    assert "pdflatex" not in overview.lower()
    checklist = text.split("### Pass Criteria\n", 1)[1].split("\n### ", 1)[0]
    assert COMPILABILITY_ROW in checklist.splitlines()


def test_pdf_delivery_includes_sources_and_build_command() -> None:
    text = FORMATTER.read_text(encoding="utf-8")
    commands = text.split("### Conversion Commands (if applicable)\n", 1)[1]
    commands = commands.split("\n```", 1)[0]
    assert PDF_DELIVERY_LINE in commands.splitlines()
    assert "- PDF: Run `" not in commands

    step = text.split("1.2 Determine which files to generate:\n", 1)[1]
    step = step.split("Step 2:", 1)[0]
    assert (
        "LaTeX -> generated from the Markdown when output_format includes "
        "LaTeX, PDF, or Combined;"
    ) in step
    assert PDF_SOURCE_DELIVERY_LINES in step


def test_apa_pdf_uses_tectonic_or_xelatex_with_bibtex() -> None:
    text = FORMATTER.read_text(encoding="utf-8")
    apa = text.split(
        "### APA 7.0 LaTeX (`apa7` Class) — Mandatory Rules\n", 1
    )[1].split("\n### ", 1)[0]
    assert r"\documentclass[man,12pt,natbib]{apa7}" in apa
    assert APA_BIBTEX_PROSE in apa
    pdf = apa.split("**PDF compilation** (mandatory):\n", 1)[1]
    tectonic_bullet = APA_BIBTEX_PROSE.split("\n", 1)[0]
    assert tectonic_bullet in pdf.split("```", 1)[0].splitlines()
    assert pdf.index(tectonic_bullet) < pdf.index("```")
    command = pdf.split("```\n", 1)[1].split("\n```", 1)[0]
    assert command == BIBTEX_SEQUENCE
    overview = text.split("### 4. PDF (via LaTeX)\n", 1)[1].split("\n### ", 1)[0]
    assert f"run `{BIBTEX_SEQUENCE}`" in overview


def test_chinese_pdf_follows_selected_backend() -> None:
    text = FORMATTER.read_text(encoding="utf-8")
    section = text.split("### Chinese LaTeX Compilation Settings\n", 1)[1]
    section = section.split("\n### ", 1)[0]
    assert CHINESE_COMPILE in section
    assert "then run XeLaTeX twice more" not in section
    assert "% biber paper" not in section


def test_latex_retains_uncited_entries_in_converted_list_order() -> None:
    text = FORMATTER.read_text(encoding="utf-8")
    rules = text.split("### Markdown -> LaTeX Conversion Rules\n", 1)[1]
    rules = rules.split("\n### ", 1)[0]
    before, fence = rules.split("```latex\n", 1)
    assert NOCITE_RULE in before
    assert before.index(NOCITE_RULE) < before.index(
        "**LaTeX document structure template**:"
    )
    assert "insert one `\\nocite{key}` for each retained" in before
    assert "actual key from `references.bib`" in before
    assert "`\\printbibliography` or `\\bibliography{...}`" in before
    assert "ascending final reference number" in before
    assert (
        "When converting from APA 7, Chicago, or MLA 9 to a numbered style, "
        "number uncited entries after all cited entries, in their original "
        "reference-list order, as specified under Handling Numbered References."
    ) in before
    block = fence.split("\n```", 1)[0]
    assert r"\addbibresource{references.bib}" in block
    assert r"\nocite" not in block
    assert "incoming reference-list order" not in block


def test_docx_uses_basic_conversion_for_phase_7_markdown() -> None:
    text = FORMATTER.read_text(encoding="utf-8")
    docx_format = text.split("### 3. DOCX (via Pandoc when available)\n", 1)[1]
    docx_format = docx_format.split("\n### ", 1)[0]
    assert DOCX_BASIC_BULLET in docx_format.splitlines()
    assert "nocite" not in docx_format

    commands = text.split("### Conversion Commands (if applicable)\n", 1)[1]
    commands = commands.split("\n```", 1)[0]
    assert DOCX_COMMANDS_LINE in commands.splitlines()
    assert "nocite" not in commands

    section = text.split("### Markdown -> DOCX Conversion Rules\n", 1)[1]
    section = section.split("**Style Mapping", 1)[0]
    assert section.split("# Basic conversion\n", 1)[1].splitlines()[0] == BASIC_PANDOC
    assert "nocite" not in section
    assert "retained uncited" not in section
    assert "Use explicit keys only." not in section
    assert "@FirstKey" not in section
    assert "--citeproc" in section


def test_mla_year_and_doi_cells() -> None:
    text = FORMATTER.read_text(encoding="utf-8")
    features = text.split("### Format-Specific Features\n", 1)[1].split("\n### ", 1)[0]
    header = next(line for line in features.splitlines() if line.startswith("|"))
    columns = [cell.strip() for cell in header.strip("|").split("|")]
    mla = columns.index("MLA 9")
    for label, expected in (
        (
            "Year position",
            "After volume and issue, before pages and DOI (journal article); "
            "after publisher (book)",
        ),
        ("DOI format", "https://doi.org/..."),
    ):
        rows = _rows_with_first_cell(features, label)
        assert len(rows) == 1
        cells = [cell.strip() for cell in rows[0].strip("|").split("|")]
        assert cells[mla] == expected


def test_chicago_footnote_marker_follows_retained_content() -> None:
    text = FORMATTER.read_text(encoding="utf-8")
    section = text.split(
        "### Handling Footnotes (Chicago Notes-Bibliography)\n", 1
    )[1].split("\n### ", 1)[0]
    from_chicago = section.split(
        "When converting **from** Chicago Notes-Bibliography:\n", 1
    )[1]
    assert CHICAGO_FROM_BULLET in from_chicago
    assert (
        "Remove footnote markers; insert appropriate in-text citations"
        not in from_chicago
    )
    to_chicago = section.split(
        "When converting **from** Chicago Notes-Bibliography:", 1
    )[0]
    assert CHICAGO_FROM_BULLET not in to_chicago
