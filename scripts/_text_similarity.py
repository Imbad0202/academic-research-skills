#!/usr/bin/env python3
"""Shared title-similarity + retry-budget helpers for the v3.9.0 cross-index
triangulation clients.

Previously triple-implemented byte-equivalently in
`semantic_scholar_client.py`, `openalex_client.py`, and `crossref_client.py`.
Extracted in #128 (v3.9.1 housekeeping) to prevent sibling drift — any
threshold tuning or normalization rule change now happens in one place.

`_normalize_title` / `_similarity` stay byte-equivalent with the v3.7.3 /
v3.9.0 client implementations for every NON-dotted-acronym title; #431 §0.1
adds a dotted-acronym pre-pass that can only *raise* `_similarity` (taken via
`max`), plus the `exact_normalized_title` / `generic_title` identity helpers the
exact-title-or-bust gate (§0.12) reads. See `test_text_similarity.py` for the
similarity contract and `test_431_exact_or_bust.py` for the gate behavior.
"""
from __future__ import annotations

import re
import string
from difflib import SequenceMatcher


_PUNCT_TRANSLATION = str.maketrans({c: " " for c in string.punctuation})

# #431 §0.1: collapse a run of two-or-more `<letter>.` units at a word boundary
# (`R.A.G.` → `RAG`) BEFORE punctuation→whitespace, so a dotted acronym and its
# undotted spelling normalize byte-equal. `/`, `&`, and spaced initials
# (`D. H.`) are NOT dotted runs and stay untouched (`A/B`, `R&D`, `Q&A`).
_DOTTED_ACRONYM = re.compile(r"\b(?:[A-Za-z]\.){2,}")


# Per protocol: shared retry budget for the index clients. S2 / Crossref
# sleep a fixed _BACKOFF_SECONDS per 429; OpenAlex uses it as the base of
# an exponential backoff (2s → 4s → 8s, #495); arXiv does not use it — its
# 429 backoff is the 3s ToU pacing floor (_ARXIV_MIN_INTERVAL, #495).
_BACKOFF_SECONDS = 2.0
_MAX_RETRIES = 3


# Per PaperOrchestra (Song et al. 2026 Appx D.3) + protocol §"Query Patterns"
# Pattern 1: title-similarity threshold for "matched" verdict.
_TITLE_SIMILARITY_THRESHOLD = 0.70


def _normalize_title(s: str) -> str:
    """Per protocol §"Query Patterns" Pattern 1: 'case-insensitive, stripped
    of punctuation' before computing similarity. Punctuation becomes
    whitespace so token boundaries are preserved, then collapse runs of
    whitespace. The byte-equivalent base form for every non-dotted title."""
    cleaned = s.lower().translate(_PUNCT_TRANSLATION)
    return " ".join(cleaned.split())


def _normalize_title_acronym(s: str) -> str:
    """#431 §0.1: base normalization plus the dotted-acronym pre-pass. The
    dots inside a `<letter>.`-run span are stripped first (`R.A.G.` → `RAG`),
    then the base path runs. Provably additive over the dotted form only — any
    title with no dotted run normalizes identically to `_normalize_title`.

    This is the form `exact_normalized_title` compares on: under #431's
    exact-title-or-bust gate the equality (not the ratio) is load-bearing, so a
    legitimate `R.A.G.`/`RAG` acronym variant must reach byte-equality here. The
    base form alone leaves them 'r a g …' ≠ 'rag …' — a high ratio but NOT
    equal, which under the gate would wrongly fall to `unresolvable`."""
    collapsed = _DOTTED_ACRONYM.sub(lambda m: m.group(0).replace(".", ""), s)
    return _normalize_title(collapsed)


# CJK Unified Ideographs (U+4E00-U+9FFF). Extension blocks are deliberately not
# scanned: the base block is sufficient for the applicability gate, and a
# narrower gate errs toward the pre-repair behavior, which is the safe
# direction. Fullwidth Latin (U+FF01-U+FF5E) is deliberately NOT in this range
# either: a title of only fullwidth Latin is not a Chinese title and must not
# enter the CJK comparison path.
_CJK_LO = "一"
_CJK_HI = "鿿"

_CN_WRAPPERS = {
    ("《", "》"), ("「", "」"), ("『", "』"), ("【", "】"),
    ("“", "”"), ("‘", "’"),
}
# The fullwidth-ASCII fold maps `．` to `.` first. `?`/`？` are kept: they can
# distinguish an interrogative title from an otherwise identical one.
_CN_TERMINAL_MARKS = "。."
_CN_HAN_ADJACENT_SPACE = re.compile(rf"(?<=[{_CJK_LO}-{_CJK_HI}]) +| +(?=[{_CJK_LO}-{_CJK_HI}])")


def has_cjk(text: str | None) -> bool:
    """True iff the string contains a CJK Unified Ideograph."""
    return any(_CJK_LO <= ch <= _CJK_HI for ch in text or "")


def normalize_cn_title(title: str | None) -> str:
    """Chinese-aware title normalization (#431 CJK repair).

    The base `_normalize_title` is ASCII-centric and, measured on real ISTIC
    metadata 2026-07-27, rejects four legitimate variants of one identical
    Chinese title:

      - fullwidth latin/digits (ＰｒｏＥＸＣ vs ProEXC): `.lower()` folds case
        but never width, so U+FF30 never reaches U+0050 (measured similarity
        0.625, exact=False)
      - a trailing CJK full stop (。) and outer wrappers (《》): not members of
        `string.punctuation`, so the base form keeps them (0.970, False)
      - spaces touching Han characters: Chinese carries no word breaks, so these
        are typesetting noise; whitespace between non-CJK tokens stays
        significant (0.941, False)
      - the ideographic space U+3000, likewise absent from `string.punctuation`

    Simplified/Traditional folding is deliberately NOT done: it is lossy for
    proper nouns, and a wrong fold would manufacture a false match. The pair is
    surfaced to the human instead.

    Behaviorally equivalent to the implementation this was promoted from in
    `chinese_literature_client.py`, which re-imports it from here rather than
    keeping a second copy (#128 anti-drift). Not byte-identical: the promotion
    hoists the wrapper/terminal-mark sets to module constants, precompiles the
    Han-adjacent-space regex, and rewrites the comments. Equivalence of
    *behavior* is what the tests pin, on both the CJK path and — through the
    pre-fix oracles in `test_text_similarity.py` — every non-CJK verdict and
    ratio.
    """
    # Fold only the fullwidth ASCII compatibility block that was observed in the
    # motivating metadata. Whole-string NFKC/casefold is too broad for an exact
    # scientific-title key: it collapses e.g. 2² with 22 and Straße with
    # Strasse. U+3000 is the fullwidth/ideographic space and is removed below.
    text = "".join(
        chr(ord(ch) - 0xFEE0) if "！" <= ch <= "～" else " " if ch == "　" else ch
        for ch in (title or "")
    ).strip()

    # Only remove wrappers and terminal marks that are demonstrated typesetting
    # noise. Scientific operators and measurements remain byte-significant:
    # ER+ != ER-, CD4+ != CD4−, and 4.5% != 45%. In particular, do not return to
    # a Unicode-category-wide P*/S* deletion rule.
    while text:
        previous = text
        text = text.rstrip(_CN_TERMINAL_MARKS).strip()
        if len(text) >= 2 and (text[0], text[-1]) in _CN_WRAPPERS:
            text = text[1:-1].strip()
        if text == previous:
            break

    # Whitespace touching a Han character is ordinary Chinese typesetting noise,
    # including spaces around an embedded Latin abbreviation. Preserve
    # whitespace *between* non-CJK tokens, where deleting it can collapse
    # scientifically distinct names (for example `PD L1` versus `PDL 1`). Case is
    # likewise retained: gene/protein symbols can be case-sensitive.
    text = re.sub(r"\s+", " ", text).strip()
    return _CN_HAN_ADJACENT_SPACE.sub("", text)


def _cjk_titles_match(a: str, b: str) -> bool:
    """Exact equality after Chinese-aware normalization, for two titles that
    BOTH carry a Han ideograph.

    The fuzzy ratio is excluded from this rule in both directions. It is not
    *sufficient*: Han characters give unrelated papers a high baseline overlap
    (two genuinely different cervical-cancer papers measured 0.510). And it is
    not safe as an extra *necessary* condition either — the fullwidth spelling
    of an identical title measured 0.625, below the 0.70 floor, so ANDing the
    ratio in would veto a match exact normalization had correctly established
    and file a real paper at P0 next to the word "fabricated".

    An empty normalized key never matches, mirroring `_cn_titles_match`'s
    non-empty guard: `《》` and `「」` both normalize to "" and are not the
    same work.
    """
    if not (has_cjk(a) and has_cjk(b)):
        return False
    left, right = normalize_cn_title(a), normalize_cn_title(b)
    return bool(left) and left == right


def _similarity(a: str, b: str) -> float:
    """`max` over the base and dotted-acronym normalizations (#431 §0.1,
    F4 non-destructive): the acronym pre-pass can only ever *raise* the score,
    so `D. H.` vs `D. H.` stays 1.000 (it would be 0.981 if the acronym form
    replaced the base form). For non-dotted titles both forms are byte-equal, so
    the second pass is skipped and the result is the pre-#431 single-form ratio."""
    a_base, b_base = _normalize_title(a), _normalize_title(b)
    base = SequenceMatcher(None, a_base, b_base).ratio()
    # CJK repair: the DOI-keyed cross-check in every resolver gates on this
    # ratio ALONE, and a legitimate fullwidth spelling of an identical Chinese
    # title measures 0.625 — under the 0.70 floor — turning a correct DOI into
    # DOI_MISMATCH. Folded in via `max` (same F4 non-destructive shape as the
    # acronym pre-pass), so this can only ever raise a score, never lower one.
    if _cjk_titles_match(a, b):
        return 1.0
    a_acr, b_acr = _normalize_title_acronym(a), _normalize_title_acronym(b)
    if a_acr == a_base and b_acr == b_base:  # no dotted run in either title
        return base
    return max(base, SequenceMatcher(None, a_acr, b_acr).ratio())


def exact_normalized_title(a: str, b: str) -> bool:
    """#431 §0.12.1: the one identity signal all four resolvers can compute.
    True iff the two titles are byte-equal under EITHER the base normalization
    OR the dotted-acronym-aware one. Both forms are checked (mirroring
    `_similarity`'s `max`, F4 non-destructive): the acronym pre-pass must only
    ever *add* matches, never drop one the base form already had. Checking only
    the acronym form would regress a punctuation-only variant where exactly one
    side is a contiguous initialism — `D.H. Lawrence` vs `D. H. Lawrence`
    normalizes byte-equal under the base form (`d h lawrence`) but NOT under the
    acronym form (`dh` vs `d h`), and would wrongly fall to `unresolvable`.
    Legitimate punctuation / case / subtitle-spacing / `R.A.G.`→`RAG` acronym
    variants all match here; a distinct related work (different subtitle, Part I
    vs Part II, a correction-notice prefix) matches under neither and stays
    `unresolvable` rather than a false `matched`."""
    return (
        _normalize_title(a) == _normalize_title(b)
        or _normalize_title_acronym(a) == _normalize_title_acronym(b)
        # CJK repair: additive third form, gated on BOTH sides carrying a Han
        # ideograph. A Latin-only or romanized shadow title is never comparable
        # this way — there is no translation oracle here, so a cross-script
        # difference must stay a non-match rather than become evidence.
        or _cjk_titles_match(a, b)
    )


# #431 §0.12.2: the closed generic/section/type/notice set. `generic_title` is
# EXACT set-membership on the normalized title — NOT substring or endswith. A
# content title that merely begins with or contains a type word (`Case Report of
# a Rare Tumor`, `A Comprehensive Review`) has a normalized form ≠ the bare type
# word, so it is NOT generic and is not demoted. This list is the single source
# of truth (spec §0.12.2); the regression fixture pins `Short Communication` /
# `Editorial Comment` / `Case Report` / `Publisher Correction` (exact title + no
# ID) → `unresolvable`.
_GENERIC_TITLES = frozenset(
    _normalize_title(t)
    for t in (
        "editorial", "guest editorial", "editorial comment", "introduction",
        "preface", "foreword", "letter", "letters", "letter to the editor",
        "letters to the editor", "reply", "comment", "commentary", "response",
        "correspondence", "book review", "book reviews", "review", "news",
        "obituary", "in memoriam", "acknowledgements", "front matter",
        "back matter", "table of contents", "abstracts", "abstract",
        "proceedings", "keynote", "panel discussion", "workshop summary",
        "special issue", "untitled", "note", "notes", "highlights", "errata",
        "erratum", "corrigendum", "addendum", "author correction",
        "publisher correction", "retraction", "expression of concern",
        "short communication", "rapid communication", "brief communication",
        "short report", "brief report", "technical report", "meeting report",
        "conference report", "case report", "case study", "research article",
        "original article", "original research", "short paper", "perspective",
        "perspectives", "viewpoint", "opinion", "discussion", "summary",
        "conclusion", "conclusions", "abstract only", "supplementary material",
    )
)


def generic_title(title: str) -> bool:
    """#431 §0.12.2: True iff the normalized title is byte-equal to a member of
    the closed generic set. Under the exact-or-bust gate an exact title match
    that is *also* generic accepts only when an ID/DOI corroborates; otherwise
    it is `unresolvable` (a bare `Editorial` collides across thousands of
    distinct works)."""
    return _normalize_title(title) in _GENERIC_TITLES
