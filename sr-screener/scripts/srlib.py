"""Shared helpers for the sr-screener scripts (Python 3.9+, standard library only).

Covers: reading bibliographic exports (RIS, PubMed/MEDLINE .nbib, Web of Science
plain text, CSV), normalising records, de-duplication keys, batch formatting,
configuration loading, agreement statistics and RIS writing.
"""
from __future__ import annotations

import collections
import csv
import difflib
import io
import json
import os
import re
import sys
import textwrap
import unicodedata

VERSION = "1.0.0"
TOOL = "sr-screener"

ADVANCE = ("include", "unclear")
LABELS = ("include", "unclear", "exclude")
FIXED_CODES = {"include": "INC", "unclear": "UNC"}
DOI_RE = re.compile(r"^10\.\d{4,9}/\S+$")
DB_PRIORITY = ["PubMed", "MEDLINE", "Embase", "Cochrane CENTRAL", "Scopus", "Web of Science"]

LANG = {
    "eng": "English", "chi": "Chinese", "zho": "Chinese", "fre": "French", "fra": "French",
    "ger": "German", "deu": "German", "jpn": "Japanese", "rus": "Russian", "spa": "Spanish",
    "ita": "Italian", "per": "Persian", "fas": "Persian", "pol": "Polish", "por": "Portuguese",
    "tur": "Turkish", "kor": "Korean", "cze": "Czech", "ces": "Czech", "hun": "Hungarian",
    "dut": "Dutch", "nld": "Dutch", "swe": "Swedish", "dan": "Danish", "nor": "Norwegian",
    "fin": "Finnish", "heb": "Hebrew", "ukr": "Ukrainian", "srp": "Serbian", "hrv": "Croatian",
    "rum": "Romanian", "ron": "Romanian", "bul": "Bulgarian", "gre": "Greek", "ell": "Greek",
    "slv": "Slovenian", "slo": "Slovak", "slk": "Slovak", "lit": "Lithuanian", "ara": "Arabic",
    "tha": "Thai", "vie": "Vietnamese", "ind": "Indonesian", "may": "Malay", "msa": "Malay",
    "hin": "Hindi", "urd": "Urdu", "est": "Estonian", "lav": "Latvian", "ice": "Icelandic",
}

TY_LABEL = {
    "JOUR": "Journal article", "EJOUR": "Journal article", "JFULL": "Journal article",
    "CHAP": "Book chapter", "BOOK": "Book", "EBOOK": "Book", "EDBOOK": "Book",
    "CONF": "Conference paper", "CPAPER": "Conference paper", "ABST": "Abstract",
    "THES": "Thesis", "RPRT": "Report", "GEN": "Generic", "SER": "Serial", "UNPB": "Unpublished",
    "ELEC": "Web page", "PAT": "Patent", "NEWS": "Newspaper", "MGZN": "Magazine", "STAT": "Statute",
}


# ----------------------------------------------------------------------------- io

def utf8_stdout():
    """Make print() safe for non-ASCII titles on Windows consoles."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


def read_text(path):
    raw = open(path, "rb").read()
    if raw[:2] in (b"\xff\xfe", b"\xfe\xff"):
        text = raw.decode("utf-16")
    else:
        try:
            text = raw.decode("utf-8-sig")
        except UnicodeDecodeError:
            text = raw.decode("cp1252", errors="replace")
    return text.replace("\r\n", "\n").replace("\r", "\n")


def load_json(path, default=None):
    if not os.path.exists(path):
        return default
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def save_json(path, obj, indent=None):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=indent)
    os.replace(tmp, path)


def skill_dir():
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# ------------------------------------------------------------------------- config

DEFAULT_CONFIG = {
    "review_title": "",
    "exclusion_codes": [
        {"code": "E1", "label": "Publication type not eligible"},
        {"code": "E2", "label": "Population not eligible"},
        {"code": "E3", "label": "Intervention / exposure / index test not eligible"},
        {"code": "E4", "label": "Comparator not eligible"},
        {"code": "E5", "label": "Outcome not eligible"},
        {"code": "E6", "label": "Study design not eligible"},
        {"code": "E9", "label": "Other (explain)"},
    ],
    "ft_exclusion_codes": None,
    "core_criteria": ["population", "intervention or index test"],
    "personas": {
        "A": "You are REVIEWER A, a clinician-researcher and content expert in the review topic.",
        "B": "You are REVIEWER B, a systematic-review methodologist.",
    },
    "conflict_policy": "adjudicate",
    "qc": {"near_miss": {}, "random_exclusion_sample": 0, "random_seed": 2026, "policy": "advance"},
    "seeds": [],
    "languages_allowed": [],
    "models": {"A": "haiku", "B": "haiku", "ADJ": "sonnet", "QC": "sonnet",
               "FTA": "sonnet", "FTB": "sonnet", "FTADJ": "sonnet"},
    "model_labels": {},
    "agent_type": "",
    "batching": {"max_records": 50, "max_chars": 90000, "wrap": 150},
    "dedup": {"doi_title_guard": True},
    "read_limit": 900,
    "grep_after": 60,
}


def load_config(path):
    cfg = json.loads(json.dumps(DEFAULT_CONFIG))
    if path:
        with open(path, encoding="utf-8") as f:
            user = json.load(f)
        for k, v in user.items():
            if isinstance(v, dict) and isinstance(cfg.get(k), dict):
                cfg[k].update(v)
            else:
                cfg[k] = v
    for c in cfg["exclusion_codes"]:
        if not re.match(r"^[A-Z][A-Z0-9_-]{0,9}$", c["code"]) or c["code"] in ("INC", "UNC"):
            raise SystemExit(f"invalid exclusion code {c['code']!r} (use e.g. E1..E9; INC/UNC are reserved)")
    if cfg["conflict_policy"] not in ("adjudicate", "liberal"):
        raise SystemExit("conflict_policy must be 'adjudicate' or 'liberal'")
    return cfg


def exclusion_codes(cfg, stage="ta"):
    lst = cfg.get("ft_exclusion_codes") if stage == "ft" and cfg.get("ft_exclusion_codes") else cfg["exclusion_codes"]
    return [c["code"] for c in lst]


def code_labels(cfg, stage="ta"):
    lst = cfg.get("ft_exclusion_codes") if stage == "ft" and cfg.get("ft_exclusion_codes") else cfg["exclusion_codes"]
    out = {"INC": "Include", "UNC": "Unclear - needs next stage / team decision"}
    out.update({c["code"]: f"{c['code']} {c['label']}" for c in lst})
    return out


def valid_decision(d, codes):
    """A decision is usable only when its label and code agree."""
    if not isinstance(d, dict):
        return False
    lab, code = d.get("d"), d.get("code")
    if lab == "include":
        return code == "INC"
    if lab == "unclear":
        return code == "UNC"
    if lab == "exclude":
        return code in codes
    return False


# ------------------------------------------------------------------------ parsing

RIS_LINE = re.compile(r"^([A-Z][A-Z0-9])  - ?(.*)$")
RIS_TYPE_FIX = {
    "label.ris.referenceType.BOOK_CHAPTER": "CHAP",
    "label.ris.referenceType.SHORT_SURVEY": "JOUR",
    "label.ris.referenceType.CONFERENCE_PAPER": "CPAPER",
    "label.ris.referenceType.CONFERENCE_REVIEW": "CPAPER",
}
JOIN_SPACE = {"AB", "N2", "TI", "T1", "T2", "BT", "JO", "JF", "N1"}


def detect_format(text, path):
    ext = os.path.splitext(path)[1].lower()
    head = text[:20000]
    if re.search(r"(?m)^PMID- ", head):
        return "medline"
    if re.search(r"(?m)^TY  - ", head):
        return "ris"
    if re.search(r"(?m)^(FN |PT [A-Z]\s*$)", head) and re.search(r"(?m)^ER\s*$", text):
        return "wos"
    if ext in (".csv", ".tsv"):
        return "csv"
    return None


def parse_ris(text):
    recs, cur = [], None
    for line in text.split("\n"):
        m = RIS_LINE.match(line)
        if m:
            tag, val = m.group(1), m.group(2).strip()
            if tag == "TY":
                if cur is not None:
                    recs.append(cur)
                val = RIS_TYPE_FIX.get(val, val)
                if not re.fullmatch(r"[A-Z]{3,6}", val):
                    val = "GEN"
                cur = collections.OrderedDict()
            elif tag == "ER":
                if cur is not None:
                    recs.append(cur)
                cur = None
                continue
            if cur is not None:
                cur.setdefault(tag, []).append(val)
        elif line.strip() and cur:
            tag = next(reversed(cur))
            sep = " " if tag in JOIN_SPACE else "; "
            cur[tag][-1] = (cur[tag][-1] + sep + line.strip()).strip()
    if cur:
        recs.append(cur)
    return recs


MEDLINE_LINE = re.compile(r"^([A-Z][A-Z0-9 ]{1,3}?)\s*- (.*)$")


def parse_medline(text):
    recs, cur, last = [], None, None
    for line in text.split("\n"):
        m = MEDLINE_LINE.match(line)
        if m and not line.startswith(" "):
            tag, val = m.group(1).strip(), m.group(2)
            if tag == "PMID":
                cur = collections.defaultdict(list)
                recs.append(cur)
            if cur is None:
                continue
            cur[tag].append(val.strip())
            last = tag
        elif line.startswith("      ") and cur is not None and last:
            cur[last][-1] += " " + line.strip()
        elif not line.strip():
            last = None
    return [medline_to_ris(r) for r in recs]


def _expand_pages(pg):
    m = re.match(r"^([A-Za-z]*\d+)-(\d+)$", pg or "")
    if not m:
        return pg or "", ""
    s, e = m.group(1), m.group(2)
    digits = re.search(r"\d+$", s).group()
    if len(e) < len(digits):
        e = digits[: len(digits) - len(e)] + e
    return s, e


def medline_to_ris(r):
    g = lambda k: r.get(k, [])
    first = lambda k: (r.get(k) or [""])[0]
    out = collections.OrderedDict()

    def put(tag, val):
        if val:
            out.setdefault(tag, []).append(val)

    put("TY", "CHAP" if g("BTI") and not g("TA") else "JOUR")
    for a in (g("FAU") or g("AU")) + g("CN"):
        put("AU", a)
    put("TI", first("TI") or first("BTI") or first("TT"))
    if g("TT") and first("TI"):
        put("TT", first("TT"))
    put("T2", first("JT") or first("BTI"))
    put("J2", first("TA"))
    dp = first("DP")
    y = re.match(r"(\d{4})", dp)
    put("PY", y.group(1) if y else "")
    put("DA", dp)
    put("VL", first("VI"))
    put("IS", first("IP"))
    sp, ep = _expand_pages(first("PG"))
    put("SP", sp)
    put("EP", ep)
    doi = ""
    for v in g("LID") + g("AID"):
        m = re.match(r"^(10\.\S+)\s+\[doi\]", v)
        if m:
            doi = m.group(1)
            break
    put("DO", doi)
    put("AB", first("AB") or first("OAB"))
    for k in g("MH") + g("OT"):
        put("KW", k)
    for a in g("AD"):
        put("AD", a)
    for s in g("IS"):
        m = re.match(r"^(\S+)", s)
        if m:
            put("SN", m.group(1))
    for lang in g("LA"):
        put("LA", lang)
    put("PB", first("PB"))
    put("CY", first("PL"))
    put("AN", first("PMID"))
    put("C2", first("PMC"))
    if g("PT"):
        put("M3", "; ".join(g("PT")))
    put("UR", f"https://pubmed.ncbi.nlm.nih.gov/{first('PMID')}/")
    put("DB", "PubMed")
    put("ID", first("PMID"))
    return out


def parse_wos(text):
    recs, cur, last = [], None, None
    for line in text.split("\n"):
        if line.startswith("   ") and cur is not None and last:
            cur[last].append(line.strip())
            continue
        m = re.match(r"^([A-Z][A-Z0-9])(?: (.*))?$", line)
        if not m:
            continue
        tag, val = m.group(1), (m.group(2) or "").strip()
        if tag in ("FN", "VR", "EF"):
            continue
        if tag == "PT":
            cur = collections.defaultdict(list)
        if tag == "ER":
            if cur is not None:
                recs.append(wos_to_ris(cur))
            cur, last = None, None
            continue
        if cur is not None:
            cur[tag].append(val)
            last = tag
    return recs


def wos_to_ris(r):
    j = lambda k, sep=" ": sep.join(r.get(k, [])).strip()
    out = collections.OrderedDict()

    def put(tag, val):
        if val:
            out.setdefault(tag, []).append(val)

    dt = j("DT", " ")
    pt = j("PT")
    put("TY", "CHAP" if "Book Chapter" in dt else ("BOOK" if pt == "B" else ("PAT" if pt == "P" else "JOUR")))
    for a in r.get("AF") or r.get("AU") or []:
        put("AU", a)
    put("TI", j("TI"))
    put("T2", j("SO"))
    put("J2", j("J9") or j("JI"))
    put("PY", j("PY"))
    put("VL", j("VL"))
    put("IS", j("IS"))
    put("SP", j("BP"))
    put("EP", j("EP"))
    put("DO", j("DI"))
    put("AB", j("AB"))
    for k in re.split(r";\s*", j("DE", " ")) + re.split(r";\s*", j("ID", " ")):
        put("KW", k.strip())
    put("LA", j("LA"))
    put("M3", dt)
    put("C2", j("PM"))
    put("AN", j("UT"))
    put("SN", j("SN"))
    put("PB", j("PU"))
    put("DB", "Web of Science")
    return out


CSV_FIELDS = {
    "TI": ["title", "articletitle", "documenttitle", "ti", "primarytitle"],
    "AB": ["abstract", "ab", "abstractnote"],
    "PY": ["year", "publicationyear", "py", "pubyear", "date", "publicationdate"],
    "DO": ["doi", "di"],
    "C2": ["pmid", "pubmedid", "pubmed"],
    "T2": ["sourcetitle", "journal", "journaltitle", "publicationtitle", "source", "so", "t2", "secondarytitle"],
    "AU": ["authors", "author", "au", "authorfullnames", "authornames"],
    "M3": ["documenttype", "publicationtype", "type", "itemtype", "dt", "pt", "referencetype"],
    "LA": ["languageoforiginaldocument", "language", "la"],
    "KW": ["authorkeywords", "keywords", "indexkeywords", "manualtags", "automatictags", "kw", "de", "meshterms"],
}


def _hkey(h):
    return re.sub(r"[^a-z0-9]", "", (h or "").lower())


def parse_csv(text):
    sample = text[:5000]
    try:
        dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
    except csv.Error:
        dialect = csv.excel
    rows = list(csv.DictReader(io.StringIO(text), dialect=dialect))
    recs = []
    for row in rows:
        keyed = {_hkey(k): (v or "").strip() for k, v in row.items() if k}
        out = collections.OrderedDict()
        out["TY"] = ["JOUR"]
        for tag, names in CSV_FIELDS.items():
            vals = [keyed[n] for n in names if keyed.get(n)]
            if not vals:
                continue
            if tag == "AU":
                out["AU"] = [a.strip() for a in re.split(r";\s*|\s+and\s+", vals[0]) if a.strip()]
            elif tag == "KW":
                kws = []
                for v in vals:
                    kws += [k.strip() for k in re.split(r";\s*", v) if k.strip()]
                out["KW"] = kws
            elif tag == "PY":
                m = re.search(r"(1[89]\d\d|20\d\d|2100)", vals[0])
                if m:
                    out["PY"] = [m.group(1)]
            else:
                out[tag] = [vals[0]]
        if out.get("TI") or out.get("AB"):
            recs.append(out)
    return recs


def load_export(path, db_hint=None):
    """Return (format, [raw RIS-style records]) for one export file."""
    text = read_text(path)
    fmt = detect_format(text, path)
    if fmt == "ris":
        recs = parse_ris(text)
    elif fmt == "medline":
        recs = parse_medline(text)
    elif fmt == "wos":
        recs = parse_wos(text)
    elif fmt == "csv":
        recs = parse_csv(text)
    else:
        return None, []
    for r in recs:
        if db_hint and not r.get("DB"):
            r["DB"] = [db_hint]
    return fmt, recs


# -------------------------------------------------------------------- normalising

def norm_doi(d):
    d = (d or "").strip().lower()
    d = re.sub(r"^(https?://)?(dx\.)?doi\.org/", "", d)
    d = re.sub(r"^doi:\s*", "", d)
    d = d.rstrip(".;,")
    return d if DOI_RE.match(d) else ""


def norm_title(t):
    t = re.sub(r"<[^>]+>", "", t or "")
    t = unicodedata.normalize("NFKD", t)
    t = "".join(ch for ch in t if not unicodedata.combining(ch))
    return re.sub(r"[\W_]+", "", t.lower())


def _first(r, *tags):
    for t in tags:
        for v in r.get(t, []):
            if v and v.strip():
                return v.strip()
    return ""


def infer_db(r, fallback):
    db = _first(r, "DB", "DP")
    if db:
        low = db.lower()
        if "pubmed" in low or "medline" in low:
            return "PubMed"
        if "scopus" in low:
            return "Scopus"
        if "web of science" in low or "wos" == low or "clarivate" in low:
            return "Web of Science"
        if "embase" in low:
            return "Embase"
        if "cochrane" in low:
            return "Cochrane CENTRAL"
        return db
    urls = " ".join(r.get("UR", []) + r.get("L1", []) + r.get("L2", [])).lower()
    an = _first(r, "AN")
    if "scopus.com" in urls:
        return "Scopus"
    if an.upper().startswith("WOS:"):
        return "Web of Science"
    if "embase" in urls:
        return "Embase"
    if "cochranelibrary" in urls:
        return "Cochrane CENTRAL"
    if "pubmed" in urls:
        return "PubMed"
    return fallback


def unify(r, db, src_file, idx):
    """Normalise one raw record into the fields the pipeline uses."""
    m3 = _first(r, "M3")
    doi = ""
    for cand in r.get("DO", []) + r.get("DI", []) + ([m3] if norm_doi(m3) else []):
        doi = norm_doi(cand)
        if doi:
            break
    if not doi:
        for u in r.get("UR", []) + r.get("L3", []):
            if "doi.org/" in u.lower():
                doi = norm_doi(u)
                if doi:
                    break
    pmid = ""
    an = _first(r, "AN")
    if db == "PubMed" and an.isdigit():
        pmid = an
    if not pmid:
        c2 = _first(r, "C2")
        if c2.isdigit() and 5 <= len(c2) <= 9:
            pmid = c2
    if not pmid:
        blob = " ".join(r.get("UR", []) + r.get("N1", []) + r.get("M2", []))
        m = re.search(r"pubmed\.ncbi\.nlm\.nih\.gov/(\d{5,9})|PMID:?\s*(\d{5,9})", blob)
        if m:
            pmid = m.group(1) or m.group(2)
    ty = _first(r, "TY") or "GEN"
    typ = m3 if m3 and not norm_doi(m3) else TY_LABEL.get(ty, ty)
    year = ""
    for v in r.get("PY", []) + r.get("Y1", []) + r.get("DA", []) + r.get("Y2", []):
        m = re.search(r"(1[89]\d\d|20\d\d|2100)", v)
        if m:
            year = m.group(1)
            break
    langs = []
    for lang in r.get("LA", []):
        for part in re.split(r"[;,]\s*", lang):
            part = part.strip()
            if part:
                langs.append(LANG.get(part.lower(), part))
    return dict(
        idx=idx, db=db, src_file=src_file, ty=ty,
        title=_first(r, "TI", "T1", "CT"),
        abstract=_first(r, "AB", "N2"),
        year=year,
        journal=_first(r, "T2", "JO", "JF", "JA", "T3", "BT"),
        type=typ,
        lang="; ".join(dict.fromkeys(langs)),
        doi=doi, pmid=pmid,
        authors=r.get("AU", []) or r.get("A1", []),
        kw=[k for k in r.get("KW", []) if k],
    )


def titles_compatible(a, b):
    if not a or not b:
        return True
    a, b = a[:120], b[:120]
    if a[:30] == b[:30]:
        return True
    return difflib.SequenceMatcher(None, a, b).ratio() >= 0.4


def db_rank(db):
    return DB_PRIORITY.index(db) if db in DB_PRIORITY else len(DB_PRIORITY)


# ------------------------------------------------------------------------ batches

def record_block(u, wrap=150):
    fill = lambda s: textwrap.fill(s, wrap, break_long_words=True, break_on_hyphens=False)
    head = f"### {u['id']} | {u['year'] or 'n/a'} | {u['type'] or 'n/a'} | Lang: {u['lang'] or 'n/a'}"
    lines = [head, fill("TI: " + (u["title"] or "[no title]")),
             fill("AB: " + (u["abstract"] or "[NO ABSTRACT AVAILABLE]"))]
    if u.get("kw"):
        lines.append(fill("KW: " + "; ".join(u["kw"])))
    return "\n".join(lines) + "\n"


def id_width(n):
    return max(5, len(str(n)))


# -------------------------------------------------------------------- statistics

def agreement(pairs):
    """pairs: list of (a_advances: bool, b_advances: bool). Returns counts, po, kappa, PABAK."""
    n = len(pairs)
    both_adv = sum(1 for a, b in pairs if a and b)
    both_exc = sum(1 for a, b in pairs if not a and not b)
    a_only = sum(1 for a, b in pairs if a and not b)
    b_only = sum(1 for a, b in pairs if b and not a)
    if not n:
        return dict(n=0, both_advance=0, both_exclude=0, a_only_advance=0, b_only_advance=0,
                    observed_agreement=None, kappa=None, pabak=None)
    po = (both_adv + both_exc) / n
    pa = (both_adv + a_only) / n
    pb = (both_adv + b_only) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    kappa = (po - pe) / (1 - pe) if pe < 1 else None
    return dict(n=n, both_advance=both_adv, both_exclude=both_exc, a_only_advance=a_only,
                b_only_advance=b_only, observed_agreement=round(po, 4),
                kappa=None if kappa is None else round(kappa, 3), pabak=round(2 * po - 1, 3))


# --------------------------------------------------------------------------- RIS

def _ris_value(v):
    return re.sub(r"\s+", " ", str(v)).strip()


def write_ris(path, items, replace=("LB", "ID")):
    """items: iterable of (raw_record_dict, extra_tags list[(tag, value)]).

    Tags listed in `replace` are dropped from the raw record when the extra tags
    supply them (label, record ID); every other extra tag is appended (N1, KW).
    """
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        for raw, extra in items:
            ty = (raw.get("TY") or ["JOUR"])[0]
            f.write("TY  - %s\r\n" % ty)
            drop = {t for t, _ in extra if t in replace}
            for tag, vals in raw.items():
                if tag in ("TY", "ER") or tag in drop:
                    continue
                for v in vals:
                    v = _ris_value(v)
                    if v:
                        f.write("%s  - %s\r\n" % (tag, v))
            for tag, v in extra:
                f.write("%s  - %s\r\n" % (tag, _ris_value(v)))
            f.write("ER  - \r\n\r\n")
