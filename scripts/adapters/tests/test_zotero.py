"""Tests for scripts/adapters/zotero.py."""
from pathlib import Path
import subprocess
import json

from jsonschema import Draft202012Validator
import pytest

from scripts.adapters._common import strip_doi

REPO_ROOT = Path(__file__).resolve().parents[3]
ADAPTER = REPO_ROOT / "scripts/adapters/zotero.py"
FIXTURE_INPUT = REPO_ROOT / "scripts/adapters/examples/zotero/input_fixture/export.json"
EXPECTED_PASSPORT = REPO_ROOT / "scripts/adapters/examples/zotero/expected_passport.yaml"
EXPECTED_REJECTION = REPO_ROOT / "scripts/adapters/examples/zotero/expected_rejection_log.yaml"


def _run(*args):
    return subprocess.run(
        ["python", str(ADAPTER)] + list(args),
        capture_output=True,
        text=True,
        cwd=REPO_ROOT,
    )


def test_adapter_exists():
    assert ADAPTER.exists()


def test_happy_path(tmp_path, load_yaml, clean_timestamps):
    p = tmp_path / "p.yaml"
    r = tmp_path / "r.yaml"
    res = _run("--input", str(FIXTURE_INPUT), "--passport", str(p), "--rejection-log", str(r))
    assert res.returncode == 0, res.stderr
    assert clean_timestamps(load_yaml(p)) == clean_timestamps(load_yaml(EXPECTED_PASSPORT))
    assert clean_timestamps(load_yaml(r)) == clean_timestamps(load_yaml(EXPECTED_REJECTION))


def test_malformed_json_fails_loud(tmp_path):
    bad = tmp_path / "bad.json"
    bad.write_text("{not json", encoding="utf-8")
    p = tmp_path / "p.yaml"
    r = tmp_path / "r.yaml"
    res = _run("--input", str(bad), "--passport", str(p), "--rejection-log", str(r))
    assert res.returncode == 1
    assert "json" in res.stderr.lower() or "parse" in res.stderr.lower()


def test_empty_array_emits_empty_passport(tmp_path, load_yaml):
    empty = tmp_path / "empty.json"
    empty.write_text("[]", encoding="utf-8")
    p = tmp_path / "p.yaml"
    r = tmp_path / "r.yaml"
    res = _run("--input", str(empty), "--passport", str(p), "--rejection-log", str(r))
    assert res.returncode == 0
    doc = load_yaml(p)
    assert doc == {"literature_corpus": []}


def test_institution_author_preserved(tmp_path, load_yaml):
    data = [
        {
            "citationKey": "who2024",
            "itemType": "report",
            "title": "World report",
            "creators": [{"creatorType": "author", "name": "World Health Organization"}],
            "date": "2024",
            "itemID": "AAAA1111",
        }
    ]
    infile = tmp_path / "i.json"
    infile.write_text(json.dumps(data), encoding="utf-8")
    p = tmp_path / "p.yaml"
    r = tmp_path / "r.yaml"
    res = _run("--input", str(infile), "--passport", str(p), "--rejection-log", str(r))
    assert res.returncode == 0
    doc = load_yaml(p)
    assert doc["literature_corpus"][0]["authors"] == [{"literal": "World Health Organization"}]


def test_no_authors_rejected(tmp_path, load_yaml):
    data = [
        {
            "citationKey": "anon2024",
            "itemType": "journalArticle",
            "title": "Untitled",
            "creators": [{"creatorType": "editor", "firstName": "A", "lastName": "B"}],
            "date": "2024",
            "itemID": "BBBB1111",
        }
    ]
    infile = tmp_path / "i.json"
    infile.write_text(json.dumps(data), encoding="utf-8")
    p = tmp_path / "p.yaml"
    r = tmp_path / "r.yaml"
    res = _run("--input", str(infile), "--passport", str(p), "--rejection-log", str(r))
    assert res.returncode == 0
    pp = load_yaml(p)
    rr = load_yaml(r)
    assert pp["literature_corpus"] == []
    assert len(rr["rejected"]) == 1
    assert rr["rejected"][0]["reason"] == "authors_unparseable"


def test_unparseable_date_rejected(tmp_path, load_yaml):
    data = [
        {
            "citationKey": "fwd2024",
            "itemType": "journalArticle",
            "title": "Forthcoming",
            "creators": [{"creatorType": "author", "firstName": "A", "lastName": "B"}],
            "date": "forthcoming",
            "itemID": "CCCC1111",
        }
    ]
    infile = tmp_path / "i.json"
    infile.write_text(json.dumps(data), encoding="utf-8")
    p = tmp_path / "p.yaml"
    r = tmp_path / "r.yaml"
    res = _run("--input", str(infile), "--passport", str(p), "--rejection-log", str(r))
    assert res.returncode == 0
    rr = load_yaml(r)
    assert rr["rejected"][0]["reason"] == "year_unparseable"


# ---------------------------------------------------------------------------
# P1 — schema-violating empty values
# ---------------------------------------------------------------------------

def test_blank_corporate_author_rejected(tmp_path, load_yaml):
    """Blank literal author (name='') must be rejected, not emit literal: ''."""
    data = [
        {
            "citationKey": "blank_corp2024",
            "itemType": "report",
            "title": "Some report",
            "creators": [{"creatorType": "author", "name": "   "}],
            "date": "2024",
            "itemID": "ZZZZ0001",
        }
    ]
    infile = tmp_path / "i.json"
    infile.write_text(json.dumps(data), encoding="utf-8")
    p = tmp_path / "p.yaml"
    r = tmp_path / "r.yaml"
    res = _run("--input", str(infile), "--passport", str(p), "--rejection-log", str(r))
    assert res.returncode == 0
    pp = load_yaml(p)
    rr = load_yaml(r)
    assert pp["literature_corpus"] == [], "blank corporate author must not reach passport"
    assert len(rr["rejected"]) == 1
    assert rr["rejected"][0]["reason"] == "missing_required_field"
    assert "authors" in rr["rejected"][0]["missing_fields"]


def test_missing_title_rejected(tmp_path, load_yaml):
    """Item without a title must be rejected with missing_required_field."""
    data = [
        {
            "citationKey": "notitle2024",
            "itemType": "journalArticle",
            "creators": [{"creatorType": "author", "firstName": "A", "lastName": "B"}],
            "date": "2024",
            "itemID": "ZZZZ0002",
        }
    ]
    infile = tmp_path / "i.json"
    infile.write_text(json.dumps(data), encoding="utf-8")
    p = tmp_path / "p.yaml"
    r = tmp_path / "r.yaml"
    res = _run("--input", str(infile), "--passport", str(p), "--rejection-log", str(r))
    assert res.returncode == 0
    pp = load_yaml(p)
    rr = load_yaml(r)
    assert pp["literature_corpus"] == [], "missing title must not reach passport"
    assert len(rr["rejected"]) == 1
    assert rr["rejected"][0]["reason"] == "missing_required_field"
    assert "title" in rr["rejected"][0]["missing_fields"]


def test_missing_citation_key_rejected(tmp_path, load_yaml):
    """Item without citationKey and without key must be rejected."""
    data = [
        {
            "itemType": "journalArticle",
            "title": "No citekey paper",
            "creators": [{"creatorType": "author", "firstName": "A", "lastName": "B"}],
            "date": "2024",
            "itemID": "ZZZZ0003",
        }
    ]
    infile = tmp_path / "i.json"
    infile.write_text(json.dumps(data), encoding="utf-8")
    p = tmp_path / "p.yaml"
    r = tmp_path / "r.yaml"
    res = _run("--input", str(infile), "--passport", str(p), "--rejection-log", str(r))
    assert res.returncode == 0
    pp = load_yaml(p)
    rr = load_yaml(r)
    assert pp["literature_corpus"] == [], "missing citationKey must not reach passport"
    assert len(rr["rejected"]) == 1
    assert rr["rejected"][0]["reason"] == "missing_required_field"
    assert "citation_key" in rr["rejected"][0]["missing_fields"]


# ---------------------------------------------------------------------------
# P2-A — duplicate citekey handling
# ---------------------------------------------------------------------------

def test_duplicate_citekey_disambiguated(tmp_path, load_yaml):
    """Two items with the same citationKey must both be accepted with suffixed keys."""
    data = [
        {
            "citationKey": "smith2024",
            "itemType": "journalArticle",
            "title": "First paper",
            "creators": [{"creatorType": "author", "firstName": "Alice", "lastName": "Smith"}],
            "date": "2024",
            "itemID": "DUP10001",
        },
        {
            "citationKey": "smith2024",
            "itemType": "journalArticle",
            "title": "Second paper",
            "creators": [{"creatorType": "author", "firstName": "Alice", "lastName": "Smith"}],
            "date": "2024",
            "itemID": "DUP10002",
        },
    ]
    infile = tmp_path / "i.json"
    infile.write_text(json.dumps(data), encoding="utf-8")
    p = tmp_path / "p.yaml"
    r = tmp_path / "r.yaml"
    res = _run("--input", str(infile), "--passport", str(p), "--rejection-log", str(r))
    assert res.returncode == 0
    pp = load_yaml(p)
    entries = pp["literature_corpus"]
    assert len(entries) == 2, "both items must be accepted"
    keys = {e["citation_key"] for e in entries}
    assert len(keys) == 2, f"citation keys must be unique, got: {keys}"
    # first item keeps original key, second gets a suffix
    assert "smith2024" in keys
    assert any(k.startswith("smith2024") and k != "smith2024" for k in keys)


# ---------------------------------------------------------------------------
# P2-B — issued fallback + seasonal date rejection + source_pointer contract
# ---------------------------------------------------------------------------

def test_issued_fallback_no_date_field(tmp_path, load_yaml):
    """Item with only `issued` (no `date`) must resolve year from issued."""
    data = [
        {
            "citationKey": "issued2023",
            "itemType": "journalArticle",
            "title": "Issued-only paper",
            "creators": [{"creatorType": "author", "firstName": "A", "lastName": "B"}],
            "issued": {"date-parts": [[2023]]},
            "itemID": "ISS10001",
        }
    ]
    infile = tmp_path / "i.json"
    infile.write_text(json.dumps(data), encoding="utf-8")
    p = tmp_path / "p.yaml"
    r = tmp_path / "r.yaml"
    res = _run("--input", str(infile), "--passport", str(p), "--rejection-log", str(r))
    assert res.returncode == 0
    pp = load_yaml(p)
    entries = pp["literature_corpus"]
    assert len(entries) == 1
    assert entries[0]["year"] == 2023


def test_issued_as_string_fallback(tmp_path, load_yaml):
    """Item with `issued` as string (no `date`) must resolve year from issued string."""
    data = [
        {
            "citationKey": "issued2022",
            "itemType": "journalArticle",
            "title": "Issued string paper",
            "creators": [{"creatorType": "author", "firstName": "A", "lastName": "B"}],
            "issued": "2022-06-15",
            "itemID": "ISS10002",
        }
    ]
    infile = tmp_path / "i.json"
    infile.write_text(json.dumps(data), encoding="utf-8")
    p = tmp_path / "p.yaml"
    r = tmp_path / "r.yaml"
    res = _run("--input", str(infile), "--passport", str(p), "--rejection-log", str(r))
    assert res.returncode == 0
    pp = load_yaml(p)
    entries = pp["literature_corpus"]
    assert len(entries) == 1
    assert entries[0]["year"] == 2022


def test_seasonal_date_rejected(tmp_path, load_yaml):
    """'Spring 2024' must be rejected — seasonal strings are not valid dates."""
    data = [
        {
            "citationKey": "spring2024",
            "itemType": "journalArticle",
            "title": "Spring paper",
            "creators": [{"creatorType": "author", "firstName": "A", "lastName": "B"}],
            "date": "Spring 2024",
            "itemID": "SEA10001",
        }
    ]
    infile = tmp_path / "i.json"
    infile.write_text(json.dumps(data), encoding="utf-8")
    p = tmp_path / "p.yaml"
    r = tmp_path / "r.yaml"
    res = _run("--input", str(infile), "--passport", str(p), "--rejection-log", str(r))
    assert res.returncode == 0
    pp = load_yaml(p)
    rr = load_yaml(r)
    assert pp["literature_corpus"] == [], "seasonal date must not reach passport"
    assert len(rr["rejected"]) == 1
    assert rr["rejected"][0]["reason"] == "year_unparseable"


def test_nd_date_rejected(tmp_path, load_yaml):
    """'n.d.' (no date) must be rejected."""
    data = [
        {
            "citationKey": "nodate2024",
            "itemType": "journalArticle",
            "title": "No date paper",
            "creators": [{"creatorType": "author", "firstName": "A", "lastName": "B"}],
            "date": "n.d.",
            "itemID": "ND100001",
        }
    ]
    infile = tmp_path / "i.json"
    infile.write_text(json.dumps(data), encoding="utf-8")
    p = tmp_path / "p.yaml"
    r = tmp_path / "r.yaml"
    res = _run("--input", str(infile), "--passport", str(p), "--rejection-log", str(r))
    assert res.returncode == 0
    pp = load_yaml(p)
    rr = load_yaml(r)
    assert pp["literature_corpus"] == [], "n.d. date must not reach passport"
    assert len(rr["rejected"]) == 1
    assert rr["rejected"][0]["reason"] == "year_unparseable"


def test_missing_source_pointer_rejected(tmp_path, load_yaml):
    """Item with neither itemID nor key must be rejected (no valid source_pointer)."""
    data = [
        {
            "citationKey": "noptr2024",
            "itemType": "journalArticle",
            "title": "No pointer paper",
            "creators": [{"creatorType": "author", "firstName": "A", "lastName": "B"}],
            "date": "2024",
        }
    ]
    infile = tmp_path / "i.json"
    infile.write_text(json.dumps(data), encoding="utf-8")
    p = tmp_path / "p.yaml"
    r = tmp_path / "r.yaml"
    res = _run("--input", str(infile), "--passport", str(p), "--rejection-log", str(r))
    assert res.returncode == 0
    pp = load_yaml(p)
    rr = load_yaml(r)
    assert pp["literature_corpus"] == [], "item without source_pointer must not reach passport"
    assert len(rr["rejected"]) == 1
    assert rr["rejected"][0]["reason"] == "missing_required_field"
    assert "source_pointer" in rr["rejected"][0]["missing_fields"]


def test_zotero_key_used_as_source_pointer(tmp_path, load_yaml):
    """Item with Zotero `key` (8-char) but no itemID uses key as source_pointer."""
    data = [
        {
            "citationKey": "keyonly2024",
            "itemType": "journalArticle",
            "title": "Key-only paper",
            "creators": [{"creatorType": "author", "firstName": "A", "lastName": "B"}],
            "date": "2024",
            "key": "ABCD1234",
        }
    ]
    infile = tmp_path / "i.json"
    infile.write_text(json.dumps(data), encoding="utf-8")
    p = tmp_path / "p.yaml"
    r = tmp_path / "r.yaml"
    res = _run("--input", str(infile), "--passport", str(p), "--rejection-log", str(r))
    assert res.returncode == 0
    pp = load_yaml(p)
    entries = pp["literature_corpus"]
    assert len(entries) == 1
    # source_pointer must use the Zotero key, not @citekey
    assert entries[0]["source_pointer"] == "zotero://select/items/ABCD1234"
    assert "@" not in entries[0]["source_pointer"]


# ---------------------------------------------------------------------------
# P3 — all-rejected corpus
# ---------------------------------------------------------------------------

def test_all_rejected_corpus(tmp_path, load_yaml):
    """When every item is rejected, passport must be empty and rejection_log populated."""
    data = [
        {
            "citationKey": "noauth2024",
            "itemType": "journalArticle",
            "title": "No author",
            "creators": [],
            "date": "2024",
            "itemID": "AR100001",
        },
        {
            "citationKey": "noyr2024",
            "itemType": "journalArticle",
            "title": "No year",
            "creators": [{"creatorType": "author", "firstName": "A", "lastName": "B"}],
            "date": "forthcoming",
            "itemID": "AR100002",
        },
    ]
    infile = tmp_path / "i.json"
    infile.write_text(json.dumps(data), encoding="utf-8")
    p = tmp_path / "p.yaml"
    r = tmp_path / "r.yaml"
    res = _run("--input", str(infile), "--passport", str(p), "--rejection-log", str(r))
    assert res.returncode == 0
    pp = load_yaml(p)
    rr = load_yaml(r)
    assert pp["literature_corpus"] == []
    assert rr["summary"]["total_rejected"] == 2


# --- v3.10 venue_type mapping (spec §3 PR-B item 13) ---

def _import_zotero():
    import importlib.util
    spec = importlib.util.spec_from_file_location("zotero_adapter", ADAPTER)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_zotero_map_venue_type_known_types():
    z = _import_zotero()
    assert z.map_venue_type("journalArticle") == ("journal-article", "adapter_declared")
    assert z.map_venue_type("conferencePaper") == ("conference-paper", "adapter_declared")
    assert z.map_venue_type("book") == ("book", "adapter_declared")
    assert z.map_venue_type("thesis") == ("dissertation", "adapter_declared")


def test_zotero_map_venue_type_unknown_and_absent():
    z = _import_zotero()
    # Unknown item type → unknown/unknown (honors pair invariant; never guessed).
    assert z.map_venue_type("blogPost") == ("unknown", "unknown")
    assert z.map_venue_type(None) == ("unknown", "unknown")
    assert z.map_venue_type("") == ("unknown", "unknown")


def test_strip_doi_url_prefixes():
    # literature_corpus_entry.schema.json requires a bare DOI (^10\.).
    for raw in ("10.1000/xyz", "doi:10.1000/xyz", "https://doi.org/10.1000/xyz",
                "https://dx.doi.org/10.1000/xyz", "http://dx.doi.org/10.1000/xyz",
                "https://www.doi.org/10.1000/xyz"):
        assert strip_doi(raw) == "10.1000/xyz", raw


# --- #1056: entry["doi"] must satisfy the corpus entry schema ---------------

ENTRY_SCHEMA_PATH = REPO_ROOT / "shared/contracts/passport/literature_corpus_entry.schema.json"
REJECTION_SCHEMA_PATH = REPO_ROOT / "shared/contracts/passport/rejection_log.schema.json"


def _validator_for(schema_path):
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    return Draft202012Validator(schema, format_checker=Draft202012Validator.FORMAT_CHECKER)


def _doi_item(doi, *, citation_key="smith2024", item_id=1):
    item = {
        "citationKey": citation_key,
        "itemID": item_id,
        "itemType": "journalArticle",
        "title": "A title",
        "creators": [{"creatorType": "author", "lastName": "Smith", "firstName": "A"}],
        "date": "2024",
    }
    if doi is not None:
        item["DOI"] = doi
    return item


def _run_items(tmp_path, items, load_yaml):
    src = tmp_path / "in.json"
    src.write_text(json.dumps(items), encoding="utf-8")
    p = tmp_path / "p.yaml"
    r = tmp_path / "r.yaml"
    res = _run("--input", str(src), "--passport", str(p), "--rejection-log", str(r))
    assert res.returncode == 0, res.stderr
    return load_yaml(p)["literature_corpus"], load_yaml(r)


@pytest.mark.parametrize("raw", [
    "doi:https://doi.org/10.1000/xyz",
    "https://doi.org/doi:10.1000/xyz",
    "doi: https://dx.doi.org/10.1000/xyz",
    "DOI:doi:10.1000/xyz",
])
def test_nested_doi_prefixes_reach_the_entry_as_a_bare_doi(tmp_path, load_yaml, raw):
    corpus, log = _run_items(tmp_path, [_doi_item(raw)], load_yaml)
    assert log["rejected"] == []
    assert corpus[0]["doi"] == "10.1000/xyz"
    _validator_for(ENTRY_SCHEMA_PATH).validate(corpus[0])


@pytest.mark.parametrize("raw", [
    "not-a-doi",
    "doi.org/10.1000/xyz",
    "10.1000/xyz and more",
    "10.12/xyz",
    "10.1000/",
])
def test_doi_that_is_still_not_bare_is_rejected_with_a_log_row(tmp_path, load_yaml, raw):
    corpus, log = _run_items(tmp_path, [_doi_item(raw, item_id=7)], load_yaml)
    assert corpus == []
    assert len(log["rejected"]) == 1
    row = log["rejected"][0]
    assert row["source"] == "7"
    assert row["reason"] == "invalid_field_format"
    assert raw in row["detail"]
    _validator_for(REJECTION_SCHEMA_PATH).validate(log)
    # The case table itself is checked against the schema, not against the adapter.
    entry = {
        "citation_key": "smith2024",
        "title": "A title",
        "authors": [{"family": "Smith"}],
        "year": 2024,
        "source_pointer": "zotero://select/items/0_7",
        "doi": raw,
    }
    assert not _validator_for(ENTRY_SCHEMA_PATH).is_valid(entry)


@pytest.mark.parametrize("raw", [None, "", "   ", "doi:", "https://doi.org/"])
def test_blank_doi_keeps_the_entry_without_a_doi(tmp_path, load_yaml, raw):
    corpus, log = _run_items(tmp_path, [_doi_item(raw)], load_yaml)
    assert log["rejected"] == []
    assert "doi" not in corpus[0]


def test_rejected_doi_does_not_reserve_the_citation_key(tmp_path, load_yaml):
    items = [
        _doi_item("not-a-doi", item_id=1),
        _doi_item("10.1000/xyz", item_id=2),
    ]
    corpus, log = _run_items(tmp_path, items, load_yaml)
    assert [row["source"] for row in log["rejected"]] == ["1"]
    assert [e["citation_key"] for e in corpus] == ["smith2024"]


# --- #1058: a wrong JSON type rejects one item; the run continues ------------

def _full_item(**overrides):
    item = {
        "citationKey": "smith2024",
        "itemID": 1,
        "key": "ABCD1234",
        "itemType": "journalArticle",
        "title": "A title",
        "creators": [{"creatorType": "author", "lastName": "Smith", "firstName": "A"}],
        "date": "2024",
        "publicationTitle": "A journal",
        "proceedingsTitle": "Some proceedings",
        "bookTitle": "A book",
        "DOI": "10.1000/xyz",
        "abstractNote": "An abstract",
        "tags": [{"tag": "a tag"}],
        "notes": [{"note": "<p>A note</p>"}],
    }
    item.update(overrides)
    return item


_SIBLING = _doi_item("10.1000/other", citation_key="jones2023", item_id=2)
_STRING_FIELDS = ("citationKey", "key", "itemType", "title", "publicationTitle",
                  "proceedingsTitle", "bookTitle", "abstractNote", "DOI")
_NOT_A_STRING = (123, 1.5, True, 0, False, [], ["x"], {}, {"a": 1})
_LIST_FIELDS = ("creators", "tags", "notes")
_NOT_A_LIST = (123, 1.5, True, 0, False, "text", {}, {"a": 1})
_NESTED_WRONG = {
    "creators": ([123], ["text"], [None], [[]],
                 [{"creatorType": 1, "lastName": "Smith"}],
                 [{"creatorType": "author", "name": 123}],
                 [{"creatorType": "author", "lastName": 123}],
                 [{"creatorType": "author", "lastName": "Smith", "firstName": []}]),
    "tags": ([123], ["text"], [None], [{"tag": 123}], [{"tag": ["x"]}]),
    "notes": ([123], ["text"], [None], [{"note": 123}], [{"note": {"a": 1}}]),
}
_WRONG_TYPE_CASES = (
    [(field, value) for field in _STRING_FIELDS for value in _NOT_A_STRING]
    + [(field, value) for field in _LIST_FIELDS for value in _NOT_A_LIST]
    + [(field, value) for field, values in _NESTED_WRONG.items() for value in values]
    + [("itemID", value) for value in (True, False, 1.5, ["x"], {"a": 1})]
    + [(field, value) for field in ("date", "issued")
       for value in (123, 1.5, True, 0, False, [], [2024], ["2024"])]
)


def _assert_outputs_match_schemas(corpus, log):
    entry_validator = _validator_for(ENTRY_SCHEMA_PATH)
    for entry in corpus:
        entry_validator.validate(entry)
    _validator_for(REJECTION_SCHEMA_PATH).validate(log)


@pytest.mark.parametrize("field,value", _WRONG_TYPE_CASES, ids=repr)
def test_wrong_type_rejects_only_that_item(tmp_path, load_yaml, field, value):
    corpus, log = _run_items(tmp_path, [_full_item(**{field: value}), _SIBLING], load_yaml)
    assert [e["citation_key"] for e in corpus] == ["jones2023"]
    assert [row["reason"] for row in log["rejected"]] == ["invalid_field_format"]
    assert field in log["rejected"][0]["detail"]
    _assert_outputs_match_schemas(corpus, log)


@pytest.mark.parametrize("item", [123, 1.5, True, "text", None, [], ["x"]], ids=repr)
def test_item_that_is_not_an_object_is_rejected(tmp_path, load_yaml, item):
    corpus, log = _run_items(tmp_path, [item, _SIBLING], load_yaml)
    assert [e["citation_key"] for e in corpus] == ["jones2023"]
    assert [row["reason"] for row in log["rejected"]] == ["invalid_field_format"]
    assert isinstance(log["rejected"][0]["raw"], str)
    _assert_outputs_match_schemas(corpus, log)


@pytest.mark.parametrize("field", ["key", "itemType", "publicationTitle", "proceedingsTitle",
                                   "bookTitle", "abstractNote", "DOI", "tags", "notes"])
def test_null_optional_field_keeps_the_item(tmp_path, load_yaml, field):
    corpus, log = _run_items(tmp_path, [_full_item(**{field: None})], load_yaml)
    assert log["rejected"] == []
    assert [e["citation_key"] for e in corpus] == ["smith2024"]
    _assert_outputs_match_schemas(corpus, log)


@pytest.mark.parametrize("overrides,reason,missing", [
    ({"citationKey": None}, "missing_required_field", "citation_key"),
    ({"title": None}, "missing_required_field", "title"),
    ({"date": None}, "year_unparseable", "year"),
    ({"creators": None}, "authors_unparseable", "authors"),
    ({"creators": [{"creatorType": "author", "name": None}]}, "authors_unparseable", "authors"),
    ({"creators": [{"creatorType": "author", "lastName": None}]}, "authors_unparseable", "authors"),
    ({"itemID": None, "key": None}, "missing_required_field", "source_pointer"),
], ids=repr)
def test_null_required_field_is_a_missing_field(tmp_path, load_yaml, overrides, reason, missing):
    corpus, log = _run_items(tmp_path, [_full_item(**overrides)], load_yaml)
    assert corpus == []
    assert log["rejected"][0]["reason"] == reason
    assert log["rejected"][0]["missing_fields"] == [missing]
    _assert_outputs_match_schemas(corpus, log)


@pytest.mark.parametrize("overrides,authors,tags", [
    ({"creators": [{"creatorType": "author", "name": None, "lastName": "Smith"}]},
     [{"family": "Smith"}], ["a tag"]),
    ({"creators": [{"creatorType": "author", "lastName": "Smith", "firstName": None}]},
     [{"family": "Smith"}], ["a tag"]),
    ({"creators": [{"creatorType": None, "lastName": "Jones"},
                   {"creatorType": "author", "lastName": "Smith"}]},
     [{"family": "Smith"}], ["a tag"]),
    ({"tags": [{"tag": None}, {"tag": "kept"}]},
     [{"family": "Smith", "given": "A"}], ["kept"]),
    ({"notes": [{"note": None}, {"note": "<p>kept</p>"}]},
     [{"family": "Smith", "given": "A"}], ["a tag"]),
], ids=repr)
def test_null_nested_field_counts_as_absent(tmp_path, load_yaml, overrides, authors, tags):
    corpus, log = _run_items(tmp_path, [_full_item(**overrides)], load_yaml)
    assert log["rejected"] == []
    assert corpus[0]["authors"] == authors
    assert corpus[0]["tags"] == tags
    if "notes" in overrides:
        assert corpus[0]["user_notes"] == "kept"
    _assert_outputs_match_schemas(corpus, log)


def test_wrong_type_citation_key_gives_a_string_source(tmp_path, load_yaml):
    item = _full_item(citationKey=123, itemID=None, key=None)
    _, log = _run_items(tmp_path, [item], load_yaml)
    assert log["rejected"][0]["source"] == "123"


def test_wrong_type_item_does_not_reserve_the_citation_key(tmp_path, load_yaml):
    items = [_full_item(title=123), _full_item(itemID=2)]
    corpus, log = _run_items(tmp_path, items, load_yaml)
    assert [row["source"] for row in log["rejected"]] == ["1"]
    assert [e["citation_key"] for e in corpus] == ["smith2024"]


@pytest.mark.parametrize("issued", [
    {"date-parts": [[True]]},
    {"date-parts": ["2023"]},
    {"date-parts": [[float("inf")]]},
    {"date-parts": [[2024.9]]},
], ids=repr)
def test_wrong_type_csl_year_is_rejected_and_the_run_continues(tmp_path, load_yaml, issued):
    item = _full_item(date=None, issued=issued)
    corpus, log = _run_items(tmp_path, [item, _SIBLING], load_yaml)
    assert [e["citation_key"] for e in corpus] == ["jones2023"]
    assert [row["reason"] for row in log["rejected"]] == ["year_unparseable"]
    _assert_outputs_match_schemas(corpus, log)


def test_csl_year_held_as_a_string_is_accepted(tmp_path, load_yaml):
    # CSL-JSON allows a date-part to be a string.
    corpus, log = _run_items(
        tmp_path, [_full_item(date=None, issued={"date-parts": [["2023"]]})], load_yaml
    )
    assert log["rejected"] == []
    assert corpus[0]["year"] == 2023


@pytest.mark.parametrize("overrides,year", [
    ({"date": "2022-06-15"}, 2022),
    ({"date": {"date-parts": [[2021]]}}, 2021),
    ({"date": None, "issued": "2020-01-02"}, 2020),
    ({"date": None, "issued": {"date-parts": [[2019]]}}, 2019),
], ids=repr)
def test_date_and_issued_accept_a_string_or_an_object(tmp_path, load_yaml, overrides, year):
    corpus, log = _run_items(tmp_path, [_full_item(**overrides)], load_yaml)
    assert log["rejected"] == []
    assert corpus[0]["year"] == year


@pytest.mark.parametrize("value", [{}, {"a": 1}, {"date-parts": "2024"}], ids=repr)
def test_date_object_without_a_year_is_unparseable(tmp_path, load_yaml, value):
    corpus, log = _run_items(tmp_path, [_full_item(date=value), _SIBLING], load_yaml)
    assert [e["citation_key"] for e in corpus] == ["jones2023"]
    assert [row["reason"] for row in log["rejected"]] == ["year_unparseable"]


# --- years before 1900, and the schema check before an entry is written ------

@pytest.mark.parametrize("date,year", [
    ("1899", 1899),
    ("1859-11-24", 1859),
    ("1066/10/14", 1066),
    ("c. 1850", 1850),
    ("1650, reprinted 2005", 2005),
    ("1900", 1900),
    ("2099", 2099),
], ids=repr)
def test_year_is_read_from_a_date_string(tmp_path, load_yaml, date, year):
    corpus, log = _run_items(tmp_path, [_full_item(date=date)], load_yaml)
    assert log["rejected"] == []
    assert corpus[0]["year"] == year


@pytest.mark.parametrize("date", ["999", "1850s", "Spring 1850", "forthcoming", "n.d."], ids=repr)
def test_date_string_without_a_clear_year_is_unparseable(tmp_path, load_yaml, date):
    corpus, log = _run_items(tmp_path, [_full_item(date=date)], load_yaml)
    assert corpus == []
    assert log["rejected"][0]["reason"] == "year_unparseable"


@pytest.mark.parametrize("year", [1, 999, 2101, 3000], ids=repr)
def test_entry_that_fails_the_schema_is_rejected_and_the_run_continues(tmp_path, load_yaml, year):
    item = _full_item(date=None, issued={"date-parts": [[year]]})
    corpus, log = _run_items(tmp_path, [item, _SIBLING], load_yaml)
    assert [e["citation_key"] for e in corpus] == ["jones2023"]
    row = log["rejected"][0]
    assert row["reason"] == "invalid_field_format"
    assert row["source"] == "1"
    assert "year" in row["detail"]
    _assert_outputs_match_schemas(corpus, log)


def test_entry_that_fails_the_schema_does_not_reserve_the_citation_key(tmp_path, load_yaml):
    bad = _full_item(date=None, issued={"date-parts": [[1]]})
    good = _full_item(itemID=2)
    corpus, log = _run_items(tmp_path, [bad, good], load_yaml)
    assert [row["source"] for row in log["rejected"]] == ["1"]
    assert [e["citation_key"] for e in corpus] == ["smith2024"]


@pytest.mark.parametrize("date", [
    "2101-01-01T00:00:00+1200",
    "20241106T090000+1100",
    "Report 1234",
    "24 November 1859",
], ids=repr)
def test_number_after_the_start_of_a_date_is_not_read_as_an_early_year(tmp_path, load_yaml, date):
    corpus, log = _run_items(tmp_path, [_full_item(date=date), _SIBLING], load_yaml)
    assert [e["citation_key"] for e in corpus] == ["jones2023"]
    assert [row["reason"] for row in log["rejected"]] == ["year_unparseable"]


@pytest.mark.parametrize("date,year", [
    ("1200-01-01T00:00:00+1100", 1200),
    ("c.1850", 1850),
    ("  1859  ", 1859),
    ("2024-01-01T00:00:00+1200", 2024),
], ids=repr)
def test_early_year_at_the_start_and_modern_year_anywhere_are_read(tmp_path, load_yaml, date, year):
    corpus, log = _run_items(tmp_path, [_full_item(date=date)], load_yaml)
    assert log["rejected"] == []
    assert corpus[0]["year"] == year


def test_rejected_item_between_two_items_with_one_key_frees_only_its_own_key(tmp_path, load_yaml):
    items = [
        _full_item(itemID=1),
        _full_item(itemID=2, date=None, issued={"date-parts": [[1]]}),
        _full_item(itemID=3, date="2023"),
    ]
    corpus, log = _run_items(tmp_path, items, load_yaml)
    assert [row["source"] for row in log["rejected"]] == ["2"]
    assert {e["citation_key"]: e["year"] for e in corpus} == {"smith2024": 2024, "smith2024a": 2023}
