"""Tests for the Han/kana Script table and its generator (#1077)."""
from __future__ import annotations

import unicodedata

import pytest

from scripts import _unspaced_scripts as table
from scripts import gen_unspaced_scripts as gen

POINTS = set()
for _first, _last in table.RANGES:
    POINTS.update(range(_first, _last + 1))


def test_ranges_are_sorted_merged_and_in_unicode():
    previous = -2
    for first, last in table.RANGES:
        assert previous + 1 < first <= last <= 0x10FFFF
        previous = last


def test_table_records_its_source():
    assert table.UNICODE_VERSION.count(".") == 2
    assert set(table.SOURCE_SHA256) == set(gen.SOURCE_FILES)
    assert all(len(digest) == 64 for digest in table.SOURCE_SHA256.values())


@pytest.mark.parametrize("ch", [
    "一", "丽", "𠀀", "々", "〆", "〇", "あ", "ア", "ｱ", "ー", "ｰ",
])
def test_han_and_kana_letters_are_in(ch):
    assert ord(ch) in POINTS


@pytest.mark.parametrize("cp", [
    0xA000,   # Yi syllable
    0x17000,  # Tangut ideograph
    0x18B00,  # Khitan small script character
    0x1B170,  # Nushu character
    0xAC00,   # Hangul syllable: Korean puts spaces between words
    0x3105,   # Bopomofo letter
    0x2F00,   # Kangxi radical (a symbol, not a letter)
    0x30FB,   # katakana middle dot (punctuation)
    0x3001,   # ideographic comma
    0x0041,   # Latin
])
def test_other_scripts_and_marks_are_out(cp):
    assert cp not in POINTS


def _version(text: str) -> tuple[int, ...]:
    return tuple(int(part) for part in text.split("."))


@pytest.mark.skipif(
    _version(unicodedata.unidata_version) > _version(table.UNICODE_VERSION),
    reason="Python's Unicode data is newer than the table; regenerate it",
)
def test_every_ideograph_and_kana_letter_python_knows_is_in():
    # Each letter that Python's Unicode data names as an ideograph or kana
    # must be in the table.
    prefixes = ("CJK UNIFIED IDEOGRAPH-", "CJK COMPATIBILITY IDEOGRAPH-",
                "HIRAGANA LETTER ", "KATAKANA LETTER ",
                "HALFWIDTH KATAKANA LETTER ")
    missing = [
        hex(cp) for cp in range(0x110000)
        if unicodedata.name(chr(cp), "").startswith(prefixes)
        and cp not in POINTS
    ]
    assert missing == []


def _ucd(version="17.0.0", scripts="", extensions="", categories=""):
    return {
        "Scripts.txt": f"# Scripts-{version}.txt\n{scripts}",
        "ScriptExtensions.txt": f"# ScriptExtensions-{version}.txt\n{extensions}",
        "DerivedGeneralCategory.txt":
            f"# DerivedGeneralCategory-{version}.txt\n{categories}",
    }


def test_build_uses_extensions_and_letter_categories():
    version, ranges = gen.build(_ucd(
        scripts=("4E00..4E02 ; Han # x\n3001 ; Common\n30FC ; Common\n"
                 "2F00 ; Han\nA000 ; Yi\n"),
        extensions="3001 ; Hani Hira # comma\n30FC ; Hira Kana\n",
        categories=("4E00..4E02 ; Lo\n3001 ; Po\n30FC ; Lm\n2F00 ; So\n"
                    "A000 ; Lo\n"),
    ))
    assert version == "17.0.0"
    assert ranges == [(0x30FC, 0x30FC), (0x4E00, 0x4E02)]


def test_build_keeps_numbers_and_each_wanted_script():
    _, ranges = gen.build(_ucd(
        scripts=("3007 ; Han\n3041 ; Hiragana\n30A1 ; Katakana\n"
                 "FF9E ; Common\n0030 ; Common\n"),
        extensions="FF9E ; Kana\n",
        categories="3007 ; Nl\n3041 ; Lo\n30A1 ; Lo\nFF9E ; Lm\n0030 ; Nd\n",
    ))
    assert ranges == [(0x3007, 0x3007), (0x3041, 0x3041),
                      (0x30A1, 0x30A1), (0xFF9E, 0xFF9E)]


@pytest.mark.parametrize("line", ["4E00.. ; Lo\n", "4E00 ;\n", "4E00\n"])
def test_build_refuses_malformed_lines(line):
    with pytest.raises((gen.UcdError, ValueError)):
        gen.build(_ucd(scripts="4E00 ; Han\n", categories=line))


def test_an_extension_list_replaces_the_script():
    _, ranges = gen.build(_ucd(
        scripts="4E00 ; Han\n", extensions="4E00 ; Yiii\n",
        categories="4E00 ; Lo\n"))
    assert ranges == []


@pytest.mark.parametrize("sources", [
    {**_ucd(), "Scripts.txt": "# Scripts-16.0.0.txt\n"},
    {**_ucd(), "ScriptExtensions.txt": "no header\n"},
])
def test_build_refuses_mixed_or_unlabelled_files(sources):
    with pytest.raises(gen.UcdError):
        gen.build(sources)


def test_check_mode_reports_drift(tmp_path):
    for name, text in _ucd(scripts="4E00 ; Han\n",
                           categories="4E00 ; Lo\n").items():
        (tmp_path / name).write_text(text, encoding="utf-8")
    out = tmp_path / "table.py"
    assert gen.main(["--ucd", str(tmp_path), "--output", str(out)]) == 0
    assert "(0x4E00, 0x4E00)," in out.read_text(encoding="utf-8")
    assert gen.main(["--ucd", str(tmp_path), "--output", str(out),
                     "--check"]) == 0
    out.write_text(out.read_text(encoding="utf-8") + "# edit\n",
                   encoding="utf-8")
    assert gen.main(["--ucd", str(tmp_path), "--output", str(out),
                     "--check"]) == 1


def test_reads_the_official_folder_layout(tmp_path):
    files = _ucd(scripts="4E00 ; Han\n", categories="4E00 ; Lo\n")
    (tmp_path / "extracted").mkdir()
    for name, text in files.items():
        folder = tmp_path / "extracted" if name.startswith("Derived") else tmp_path
        (folder / name).write_text(text, encoding="utf-8")
    out = tmp_path / "table.py"
    assert gen.main(["--ucd", str(tmp_path), "--output", str(out)]) == 0
    assert "(0x4E00, 0x4E00)," in out.read_bytes().decode("utf-8")
    assert b"\r\n" not in out.read_bytes()


def test_missing_file_is_a_usage_error(tmp_path):
    assert gen.main(["--ucd", str(tmp_path), "--output",
                     str(tmp_path / "t.py")]) == 2
