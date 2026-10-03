"""Shared helpers for the sr-screener scripts (Python 3.9+, standard library only).

Covers: reading bibliographic exports (RIS, PubMed/MEDLINE .nbib, Web of Science
plain text, CSV), normalising records, de-duplication keys, batch formatting,
configuration loading, agreement statistics and RIS writing.
"""
from __future__ import annotations

import collections
import csv
import difflib
import hashlib
import io
import json
import os
import re
import sys
import textwrap
import unicodedata
import uuid

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


def digest(obj):
    """Stable content identity, independent of JSON formatting and file timestamps."""
    return hashlib.sha256(json.dumps(obj, sort_keys=True, ensure_ascii=True,
                                    separators=(",", ":")).encode("utf-8")).hexdigest()


def dataset_identity(work):
    recs = load_json(os.path.join(work, "records.json"))
    if not recs:
        raise SystemExit("records.json not found - run prepare_records.py first")
    review_id = recs.get("review_id")
    if not review_id:
        # Migration of prepared work folders predating review identities; old results still
        # require an explicit audited legacy import, never a guessed identity.
        path = os.path.join(work, "review_identity.json")
        review_id = load_json(path)
        if not review_id:
            review_id = str(uuid.uuid4())
            save_json(path, review_id)
    return review_id, digest(recs["unique"])


def screening_config(cfg, stage):
    """Only effective decision inputs belong to a stage's configuration identity.

    Reporting labels/flags and preparation settings are not screening rules. The
    prepared dataset already binds actual de-duplication and batch membership.
    """
    roles = ("A", "B", "ADJ", "QC") if stage == "ta" else ("FTA", "FTB", "FTADJ")
    settings = {
        "codes": exclusion_codes(cfg, stage),
        "codes_text": codes_text(cfg, stage),
        "core_criteria": cfg["core_criteria"],
        "personas": {r: cfg["personas"][r] for r in ("A", "B")},
        "models": {r: cfg["models"].get(r) or "" for r in roles},
        "agent_type": cfg.get("agent_type") or "",
    }
    if stage == "ta":
        qc = cfg["qc"]
        settings.update(
            conflict_policy=cfg["conflict_policy"],
            qc={"near_miss": qc.get("near_miss") or {},
                "random_exclusion_sample": qc["random_exclusion_sample"],
                "random_seed": int(qc.get("random_seed", 2026)),
                "policy": qc.get("policy", "advance")},
            read_limit=int(cfg.get("read_limit", 900)),
            grep_after=int(cfg.get("grep_after", 60)),
        )
    return settings


def upgrade_config_identity(work, state, stage, cfg):
    """Upgrade an unchanged whole-config identity without discarding paid work.

    Old states did not store the config itself, so a changed legacy hash cannot
    establish which fields changed. Require the original config for that migration.
    Keep result/pilot context IDs and decision metadata intact.
    """
    old = state.get(stage)
    if old and "config_scope" not in old and old.get("config_hash") == digest(cfg):
        old["config_hash"] = digest(screening_config(cfg, stage))
        old["config_scope"] = "stage-v1"
        fields = ("review_id", "dataset", "stage", "protocol_hash", "config_hash", "input_hash")
        old["content_id"] = digest({k: old[k] for k in fields if k in old})
        save_json(os.path.join(work, "review_state.json"), state, indent=1)
    return old


def activate_context(work, stage, protocol_path, cfg):
    """Bind a revision to this review, dataset, confirmed protocol and effective config.

    Amendments archive the old decisions and QC state before clearing the active stage.
    Pilot scope is retained: an amendment permits re-piloting the same batches, not widening.
    """
    review_id, dataset = dataset_identity(work)
    protocol = read_text(protocol_path).strip()
    if len(protocol) < 200:
        raise SystemExit("the protocol file looks empty - write and confirm it first (protocol mode)")
    identity = dict(review_id=review_id, dataset=dataset, stage=stage,
                    protocol_hash=digest(protocol), config_hash=digest(screening_config(cfg, stage)))
    if stage == "ft":
        identity["input_hash"] = digest(load_json(os.path.join(work, "ft_preparation.json")))
    path = os.path.join(work, "review_state.json")
    state = load_json(path, {}) or {}
    old = upgrade_config_identity(work, state, stage, cfg)
    if old and "config_scope" not in old:
        raise SystemExit("legacy config identity cannot be upgraded with a changed config. Restore the "
                         "config used for this stage and regenerate its workflow first; then apply edits. "
                         "Existing decisions have been kept.")
    identity["content_id"] = digest(identity)
    if old and old.get("content_id") == identity["content_id"]:
        old["protocol_path"] = os.path.abspath(protocol_path)
        state[stage] = old
        save_json(path, state, indent=1)
        return old
    names = (["decisions.json", "decisions_meta.json", "pending.json", "agreement.json",
              "qc_batches.json", "qc_reasons.json", "qc_candidates.json"] if stage == "ta" else
             ["ft_decisions.json", "ft_decisions_meta.json", "ft_pending.json", "ft_agreement.json"])
    if old:
        history_path = os.path.join(work, "revision_history.json")
        history = load_json(history_path, []) or []
        history.append({"context": old, "state": {n: load_json(os.path.join(work, n)) for n in names}})
        save_json(history_path, history, indent=1)
        for name in names:
            p = os.path.join(work, name)
            if os.path.exists(p):
                os.remove(p)
        print(f"{stage} protocol/config revision changed: earlier decisions archived; re-screen this revision")
    identity.update(config_scope="stage-v1", revision=(old or {}).get("revision", 0) + 1,
                    protocol_path=os.path.abspath(protocol_path))
    identity["context_id"] = digest({"content_id": identity["content_id"], "revision": identity["revision"]})
    state[stage] = identity
    save_json(path, state, indent=1)
    return identity


def current_context(work, stage, cfg):
    state = load_json(os.path.join(work, "review_state.json"), {}) or {}
    context = upgrade_config_identity(work, state, stage, cfg)
    if not context:
        return None
    review_id, dataset = dataset_identity(work)
    path = context.get("protocol_path", "")
    if (context.get("review_id") != review_id or context.get("dataset") != dataset or
            context.get("config_scope") != "stage-v1" or
            context.get("config_hash") != digest(screening_config(cfg, stage)) or not os.path.isfile(path) or
            context.get("protocol_hash") != digest(read_text(path).strip())):
        return None
    if stage == "ft" and context.get("input_hash") != digest(load_json(os.path.join(work, "ft_preparation.json"))):
        return None
    return context


def decision_state_current(work, stage, cfg):
    context = current_context(work, stage, cfg)
    prefix = "ft_" if stage == "ft" else ""
    meta = load_json(os.path.join(work, prefix + "decisions_meta.json"), {}) or {}
    return bool(context and meta.get("context_id") == context["context_id"])


def ta_status(work, cfg):
    """Every prepared record needs a valid, current final decision, plus required QC."""
    records = load_json(os.path.join(work, "records.json"))["unique"]
    decisions = load_json(os.path.join(work, "decisions.json"), {}) or {}
    pending = load_json(os.path.join(work, "pending.json"), {}) or {}
    ids = {u["id"] for u in records}
    missing = {rid for rid in ids if not valid_decision(decisions.get(rid, {}).get("final"),
                                                      exclusion_codes(cfg))}
    qc_ids = {i for p in pending.get("qc", []) for i in p["ids"]}
    # The QC registry survives merges. Missing pending.json cannot erase unfinished rechecks.
    required = load_json(os.path.join(work, "qc_reasons.json"), {}) or {}
    qc_ids |= {rid for rid in required if rid in ids and
               decisions.get(rid, {}).get("final", {}).get("d") == "exclude" and
               not decisions.get(rid, {}).get("QC") and
               not decisions.get(rid, {}).get("human_override") and
               not decisions.get(rid, {}).get("final", {}).get("by", "").startswith("HUMAN")}
    missing |= {i for p in pending.get("screen", []) for i in p["missA"] + p["missB"]}
    missing |= {x["id"] for p in pending.get("adj", []) for x in p["items"]}
    problems = []
    if not decision_state_current(work, "ta", cfg):
        problems.append("title/abstract decisions have no current protocol/config identity")
        missing |= ids
    # If merge state disappeared, the joint-exclusion sample has not been certified complete.
    if not os.path.exists(os.path.join(work, "pending.json")):
        missing |= {rid for rid, r in decisions.items() if rid in ids and
                    r.get("final", {}).get("d") == "exclude" and
                    r.get("final", {}).get("by") == "A+B" and not r.get("QC")}
    return missing | qc_ids, qc_ids, problems


def ta_snapshot(work):
    decisions = load_json(os.path.join(work, "decisions.json"), {}) or {}
    return digest({"dataset": dataset_identity(work),
                   "context": load_json(os.path.join(work, "decisions_meta.json"), {}),
                   "final": {rid: r.get("final") for rid, r in decisions.items()}})


def fulltext_status(work, cfg):
    """The retrieved/not-retrieved partition must cover the *current* TA advances."""
    ta_ids, qc_ids, problems = ta_status(work, cfg)
    decisions = load_json(os.path.join(work, "decisions.json"), {}) or {}
    advanced = {rid for rid, r in decisions.items() if r.get("final", {}).get("d") in ADVANCE}
    man = load_json(os.path.join(work, "ft_manifest.json"))
    nr = load_json(os.path.join(work, "ft_not_retrieved.json"))
    meta = load_json(os.path.join(work, "ft_preparation.json"), {}) or {}
    retrieved = [x["id"] for x in man or []]
    not_retrieved = [x["id"] for x in nr or []]
    covered = set(retrieved) | set(not_retrieved)
    stale = (man is None or nr is None or meta.get("ta_snapshot") != ta_snapshot(work) or
             advanced != covered or set(retrieved) & set(not_retrieved) or
             len(retrieved) != len(set(retrieved)) or len(not_retrieved) != len(set(not_retrieved)) or
             meta.get("retrieval_hash") != digest({"manifest": man, "not_retrieved": nr}))
    if stale:
        problems.append("full-text set is out of date: rerun prepare_fulltext.py for the current title/abstract decisions")
    return ta_ids, qc_ids, problems, advanced ^ covered, bool(stale)


def spreadsheet_text(value):
    """Keep untrusted text inert in both Excel and CSV readers."""
    if isinstance(value, str):
        # A locale-specific CSV/TSV reader can split inside a quoted comma field.
        # Escape formula prefixes after alternative separators and line breaks as well
        # as at the start, also when quotes or spaces sit in between (#951). One pass,
        # so a long run of tabs or newlines stays linear.
        out, armed = [], False
        for ch in value:
            if armed and ch in "=+-@":
                out.append("'")
            if ch in ";\t\r\n":
                armed = True
            elif not (ch in "\"'" or ch.isspace()):
                armed = False
            out.append(ch)
        value = "".join(out)
        if value.startswith(("=", "+", "-", "@", "\t", "\r")):
            return "'" + value
    return value


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
    # random_exclusion_sample: records BOTH reviewers excluded, rechecked by the senior reviewer.
    # Required (a joint exclusion never reaches the adjudicator); see MIN_JOINT_EXCLUSION_SAMPLE.
    "qc": {"near_miss": {}, "random_exclusion_sample": 100, "random_seed": 2026, "policy": "advance"},
    "seeds": [],
    "languages_allowed": [],
    "models": {"A": "sonnet", "B": "sonnet", "ADJ": "sonnet", "QC": "sonnet",
               "FTA": "sonnet", "FTB": "sonnet", "FTADJ": "sonnet"},
    "model_labels": {},
    "agent_type": "",
    "batching": {"max_records": 50, "max_chars": 90000, "wrap": 150},
    "dedup": {"doi_title_guard": True},
    "read_limit": 900,
    "grep_after": 60,
}


MIN_JOINT_EXCLUSION_SAMPLE = 20


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
    k = cfg["qc"].get("random_exclusion_sample")
    if not isinstance(k, int) or k < MIN_JOINT_EXCLUSION_SAMPLE:
        raise SystemExit(
            f"qc.random_exclusion_sample must be an integer >= {MIN_JOINT_EXCLUSION_SAMPLE}: the QC recheck of records "
            "both reviewers excluded is required, because a joint exclusion never reaches the adjudicator "
            "(all joint exclusions are rechecked when there are fewer)")
    return cfg


def model_overrides(cfg):
    """Roles whose model differs from the shipped default, for the cost check."""
    return {r: m for r, m in cfg["models"].items() if m != DEFAULT_CONFIG["models"].get(r)}


def exclusion_codes(cfg, stage="ta"):
    lst = cfg.get("ft_exclusion_codes") if stage == "ft" and cfg.get("ft_exclusion_codes") else cfg["exclusion_codes"]
    return [c["code"] for c in lst]


def codes_text(cfg, stage):
    """The effective code descriptions supplied to screening agents."""
    lst = cfg.get("ft_exclusion_codes") if stage == "ft" and cfg.get("ft_exclusion_codes") else cfg["exclusion_codes"]
    parts = []
    for c in lst:
        short = c.get("short") or c["label"]
        short = short if len(short) <= 48 else short[:45].rstrip() + "..."
        parts.append(f"{c['code']} ({short})")
    return " > ".join(parts)


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
    fill = lambda s: textwrap.fill(s, wrap, break_long_words=True, break_on_hyphens=False,
                                  subsequent_indent="    ")
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
