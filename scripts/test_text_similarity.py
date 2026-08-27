#!/usr/bin/env python3
"""Tests for `scripts/_text_similarity.py` — shared title-similarity helpers
extracted from `semantic_scholar_client.py` / `openalex_client.py` /
`crossref_client.py` to prevent sibling drift (#128 v3.9.1 housekeeping).

These tests rebuild the byte-equivalent behavior previously triple-implemented
in each client. The 3 client modules will import these helpers after the
extraction lands; their existing tests continue to verify the *integration*
(client uses similarity correctly) while these tests verify the *behavior*
(normalization + threshold semantics) of the shared module itself.
"""
from __future__ import annotations

import os
import sys
import unittest
from difflib import SequenceMatcher

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import _text_similarity as ts  # noqa: E402


class NormalizeTitleTest(unittest.TestCase):
    """Per protocol §"Query Patterns" Pattern 1: case-insensitive, punctuation
    stripped (becomes whitespace), whitespace collapsed."""

    def test_lowercases(self) -> None:
        self.assertEqual(ts._normalize_title("Foo Bar Baz"), "foo bar baz")

    def test_punctuation_becomes_whitespace_then_collapsed(self) -> None:
        self.assertEqual(ts._normalize_title("Foo,  Bar... Baz!"), "foo bar baz")

    def test_acronym_dots_collapse(self) -> None:
        self.assertEqual(ts._normalize_title("R.A.G."), "r a g")

    def test_empty_string(self) -> None:
        self.assertEqual(ts._normalize_title(""), "")

    def test_whitespace_only(self) -> None:
        self.assertEqual(ts._normalize_title("   \t\n  "), "")

    def test_already_normalized_unchanged(self) -> None:
        self.assertEqual(ts._normalize_title("attention is all you need"), "attention is all you need")


class SimilarityTest(unittest.TestCase):
    """SequenceMatcher.ratio over normalized titles."""

    def test_acronym_punctuation_clears_threshold(self) -> None:
        """Codex R4-1 closure (preserved from S2 client tests): 'R.A.G.' vs
        'RAG' clears 0.70 after normalize."""
        self.assertGreaterEqual(ts._similarity("R.A.G.", "RAG"), 0.70)

    def test_punctuation_stripped_before_similarity(self) -> None:
        self.assertGreater(
            ts._similarity(
                "Attention Is All You Need: A Transformers Story",
                "attention is all you need a transformers story",
            ),
            0.95,
        )

    def test_identical_strings_score_one(self) -> None:
        self.assertEqual(ts._similarity("foo bar", "foo bar"), 1.0)

    def test_completely_different_strings_score_low(self) -> None:
        self.assertLess(ts._similarity("alpha beta gamma", "xyz qrs uvw"), 0.3)


#: The motivating ISTIC title, measured 2026-07-27 (see
#: `deep-research/references/chinese_literature_api_protocol.md` §"Chinese title
#: matching"). Every entry in `_CN_LEGITIMATE_VARIANTS` is the SAME work; the
#: shared ASCII-centric normalizer rejected all four before this fix.
_CN_TITLE = "基于ProEXC的宫颈癌筛查研究"
_CN_LEGITIMATE_VARIANTS = {
    "fullwidth_latin": "基于ＰｒｏＥＸＣ的宫颈癌筛查研究",
    "terminal_cjk_stop": "基于ProEXC的宫颈癌筛查研究。",
    "spaces_touching_han": "基于 ProEXC 的宫颈癌筛查研究",
    "book_title_wrapper": "《基于ProEXC的宫颈癌筛查研究》",
    "ideographic_space": "基于ProEXC的宫颈癌筛查研究　",
}


class CjkExactTitleTest(unittest.TestCase):
    """A CJK title must survive the four legitimate typesetting variants that
    Chinese indexes actually serve.

    Before this fix the shared helpers were ASCII-centric: `.lower()` folds case
    but not width (Ｐ U+FF30 never reaches P U+0050), and `string.punctuation`
    does not contain `。`, `《》`, or U+3000. A real paper therefore reduced to
    `unresolvable` / `DOI_MISMATCH` — the same state a fabricated citation
    produces.
    """

    def test_legitimate_variants_are_exact_matches(self) -> None:
        for name, variant in _CN_LEGITIMATE_VARIANTS.items():
            with self.subTest(variant=name):
                self.assertTrue(
                    ts.exact_normalized_title(_CN_TITLE, variant),
                    f"{name}: legitimate CJK variant rejected as a non-match",
                )

    def test_exact_match_is_symmetric(self) -> None:
        for name, variant in _CN_LEGITIMATE_VARIANTS.items():
            with self.subTest(variant=name):
                self.assertEqual(
                    ts.exact_normalized_title(_CN_TITLE, variant),
                    ts.exact_normalized_title(variant, _CN_TITLE),
                )

    def test_legitimate_variants_clear_the_ratio_threshold(self) -> None:
        """The DOI-keyed path (e.g. `crossref_client.doi_lookup`) gates on the
        ratio ALONE, so exact-match repair is not enough on its own. The
        fullwidth variant measured 0.625 — below the 0.70 floor — which turned a
        correct DOI into `DOI_MISMATCH`."""
        for name, variant in _CN_LEGITIMATE_VARIANTS.items():
            with self.subTest(variant=name):
                self.assertGreaterEqual(
                    ts._similarity(_CN_TITLE, variant),
                    ts._TITLE_SIMILARITY_THRESHOLD,
                    f"{name}: legitimate CJK variant fails the DOI cross-check",
                )

    def test_distinct_cjk_papers_still_rejected(self) -> None:
        """The measured guard: two genuinely different papers on a related topic
        scored 0.510 on Han overlap alone. Han characters give unrelated CJK
        titles a high baseline, so the fix must not convert overlap into a
        match."""
        other = "基于液基细胞学的宫颈癌筛查研究"
        self.assertFalse(ts.exact_normalized_title(_CN_TITLE, other))

    def test_true_match_outranks_an_unrelated_paper(self) -> None:
        """Before the repair the ratio was actively ANTI-correlated on this
        pair: the identical title scored 0.606 while a genuinely different paper
        scored 0.645 — the wrong paper ranked higher. Han overlap dominates the
        ratio once fullwidth codepoints break the true match apart.

        The repair does not touch the unrelated pair's score (it is not equal
        under the CJK form, so nothing is folded in); it lifts the true match to
        1.0, restoring the ordering that title ranking depends on."""
        unrelated = "基于液基细胞学的宫颈癌筛查研究"
        true_match = ts._similarity(_CN_TITLE, _CN_LEGITIMATE_VARIANTS["fullwidth_latin"])
        self.assertGreater(true_match, ts._similarity(_CN_TITLE, unrelated))

    def test_simplified_traditional_not_folded(self) -> None:
        """Deliberately NOT folded: the fold is lossy for proper nouns and a
        wrong fold would manufacture a false match. The variant pair is
        surfaced to the human instead."""
        self.assertFalse(
            ts.exact_normalized_title("宫颈癌筛查研究", "宮頸癌篩查研究")
        )


def _pre_fix_exact_normalized_title(a: str, b: str) -> bool:
    """The #431 formula exactly as it stood before the CJK repair.

    Used as an oracle: the repair is only allowed to change the verdict for a
    pair where BOTH sides carry a Han ideograph. Everywhere else it must agree
    with this function byte-for-byte. Written out in full (rather than captured
    from the module) so the oracle cannot drift with the code it checks."""
    return (
        ts._normalize_title(a) == ts._normalize_title(b)
        or ts._normalize_title_acronym(a) == ts._normalize_title_acronym(b)
    )


def _pre_fix_similarity(a: str, b: str) -> float:
    """`_similarity` exactly as it stood before the CJK repair.

    The companion oracle to `_pre_fix_exact_normalized_title`, and written out
    in full for the same reason: captured from the module it checks, it would
    drift with it. Includes the dotted-acronym branch, so this is the whole
    pre-fix formula rather than the base ratio alone — off the CJK path the
    repair must reproduce it exactly, in BOTH directions."""
    a_base, b_base = ts._normalize_title(a), ts._normalize_title(b)
    base = SequenceMatcher(None, a_base, b_base).ratio()
    a_acr, b_acr = ts._normalize_title_acronym(a), ts._normalize_title_acronym(b)
    if a_acr == a_base and b_acr == b_base:  # no dotted run in either title
        return base
    return max(base, SequenceMatcher(None, a_acr, b_acr).ratio())


#: Non-CJK pairs spanning every branch of the pre-fix formula: case, ASCII
#: punctuation, dotted acronyms, the `D. H.` base-form carve-out, distinct
#: related works, and the empty/whitespace degenerate cases.
_NON_CJK_PAIRS = [
    ("Attention Is All You Need", "attention is all you need"),
    ("D.H. Lawrence and the Novel", "D. H. Lawrence and the Novel"),
    ("R.A.G. for Question Answering", "RAG for Question Answering"),
    ("Foo: A Study", "Foo — A Study"),
    ("Deep Learning, Part I", "Deep Learning, Part II"),
    ("A Study of Foo", "A Study of Bar"),
    ("Correction to: A Study of Foo", "A Study of Foo"),
    ("A/B testing", "A B testing"),
    ("R&D strategy", "R D strategy"),
    ("", ""),
    ("   ", ""),
    ("　", ""),
    ("。", "《》"),
    ("ＰｒｏＥＸＣ assay", "ProEXC assay"),
    # #800: wrapper marks present but no Han ideograph — the pairedness check
    # must not leak through the has_cjk gate and accidentally strip wrappers
    # on non-CJK titles. (If normalize_cn_title were called on these, the
    # outer marks would strip and the pairs would match — exactly the
    # regression this entry is pinned against.)
    ("《Attention Is All You Need》", "Attention Is All You Need"),
    ("《A Study of Foo》", "A Study of Foo"),
]


class CjkNonDestructiveTest(unittest.TestCase):
    """The safety property: the repair may only change the verdict for a pair
    where BOTH sides carry a Han ideograph. Every other pair must agree with
    the pre-fix formula exactly."""

    def test_agrees_with_pre_fix_formula_off_the_cjk_path(self) -> None:
        for left, right in _NON_CJK_PAIRS:
            with self.subTest(pair=(left, right)):
                self.assertEqual(
                    ts.exact_normalized_title(left, right),
                    _pre_fix_exact_normalized_title(left, right),
                    "repair changed a verdict outside the both-sides-CJK path",
                )

    def test_ratio_unchanged_off_the_cjk_path(self) -> None:
        """Off the CJK path `_similarity` must not move AT ALL — asserted as
        exact equality against the full pre-fix formula, not as a lower bound.

        A `>=` assertion against the base ratio would pass a regression that
        *raised* a non-CJK score (0.6 → 1.0 is still `>= base`), and would also
        miss the dotted-acronym branch entirely. Both directions are pinned:
        the repair may neither lower nor raise a score outside the
        both-sides-CJK gate."""
        for left, right in _NON_CJK_PAIRS:
            with self.subTest(pair=(left, right)):
                self.assertEqual(
                    ts._similarity(left, right),
                    _pre_fix_similarity(left, right),
                    "repair moved a ratio outside the both-sides-CJK path",
                )

    def test_mixed_script_pair_is_not_a_match(self) -> None:
        """A Latin-only shadow title is not comparable to a Chinese title: there
        is no translation oracle, so the difference must stay a non-match rather
        than become chimeric-citation evidence."""
        self.assertFalse(
            ts.exact_normalized_title(_CN_TITLE, "ProEXC-based cervical cancer screening")
        )

    def test_scientific_names_not_collapsed(self) -> None:
        """The CJK path must not collapse scientifically distinct titles.

        Only pairs the pre-fix formula already separated are asserted here.
        `ER+`/`ER-` and `p53`/`P53` are NOT listed: the base ASCII normalization
        maps ASCII punctuation to whitespace and lowercases, so it already
        collapses those two pairs, and `exact_normalized_title` ORs that form
        in. That is a pre-existing behavior this additive repair neither causes
        nor removes — see `test_preserves_case` /
        `test_preserves_scientific_operators` for the CJK normalizer's own
        (stricter) behavior in isolation."""
        for left, right in [
            ("基于PD L1的研究", "基于PDL 1的研究"),
            ("基于4.5%的研究", "基于45%的研究"),
        ]:
            with self.subTest(pair=(left, right)):
                self.assertFalse(ts.exact_normalized_title(left, right))

    def test_cjk_repair_adds_no_empty_string_match(self) -> None:
        """Two blank-normalizing CJK-free titles must not become a match via the
        new path. (`("", "")` is True under the pre-fix formula and stays True —
        that is pinned by the oracle test above, not changed here.)"""
        for left, right in [("。", "《》"), ("　", " ")]:
            with self.subTest(pair=(left, right)):
                self.assertFalse(ts.has_cjk(left) and ts.has_cjk(right))

    def test_cjk_titles_normalizing_to_empty_never_match(self) -> None:
        """The CJK path itself refuses an empty normalized key, mirroring
        `_cn_titles_match`'s non-empty guard."""
        self.assertEqual(ts.normalize_cn_title("《》"), "")
        self.assertFalse(ts.exact_normalized_title("《》。", "「」。"))


class NormalizeCnTitleTest(unittest.TestCase):
    """Unit-level behavior of the CJK-aware normalizer itself."""

    def test_folds_fullwidth_ascii_to_halfwidth(self) -> None:
        self.assertEqual(ts.normalize_cn_title("ＰｒｏＥＸＣ"), "ProEXC")

    def test_strips_terminal_cjk_full_stop(self) -> None:
        self.assertEqual(ts.normalize_cn_title("研究。"), "研究")

    def test_strips_outer_title_wrappers(self) -> None:
        for wrapped in ("《研究》", "「研究」", "『研究』", "【研究】"):
            with self.subTest(wrapped=wrapped):
                self.assertEqual(ts.normalize_cn_title(wrapped), "研究")

    def test_strips_outer_quotation_wrappers(self) -> None:
        for wrapped in ("“围城”", "‘围城’"):
            with self.subTest(wrapped=wrapped):
                self.assertEqual(ts.normalize_cn_title(wrapped), "围城")

    def test_keeps_marks_when_outer_marks_belong_to_two_different_pairs(self) -> None:
        """#800: the first/last marks of `《红楼梦》与《金瓶梅》` match as pair
        TYPES (`《`/`》`) but belong to two different brackets — one opening
        each title. Positional stripping left an orphaned `》` mid-string; the
        pairedness check keeps the title intact instead."""
        for title in ("《红楼梦》与《金瓶梅》", "“研究”与“实践”"):
            with self.subTest(title=title):
                self.assertEqual(ts.normalize_cn_title(title), title)

    def test_nested_interior_wrapper_survives_outer_strip(self) -> None:
        """A genuine outer pair enclosing a balanced interior still strips, and
        the balanced interior marks survive as content."""
        self.assertEqual(
            ts.normalize_cn_title("《基于「ProEXC」的研究》"),
            "基于「ProEXC」的研究",
        )

    def test_unclosed_opener_in_interior_keeps_marks(self) -> None:
        """An opener inside the interior that never closes proves the outer
        marks are not one unit — a distinct failure mode from the stray-closer
        case above (stack non-empty at the end vs. pop from empty), and also
        verified to fail against the pre-fix positional strip."""
        self.assertEqual(ts.normalize_cn_title("“研究与“实践”"), "“研究与“实践”")

    def test_apostrophe_in_embedded_english_does_not_veto_the_outer_strip(self) -> None:
        """#804 review P1: `’` is the closer of `‘`, but it is ALSO the
        apostrophe in embedded English — the same codepoint in a non-wrapper
        role. A family-blind interior scan read the lone `’` in
        `《Alzheimer’s病中…》` as an unbalanced quote and refused to strip a
        genuine `《…》` wrap, so a title that matched on main stopped matching:
        exact False and ratio 0.6818, below the 0.70 floor. That takes out the
        DOI-keyed ratio gate and the title-fallback exact gate at once, which
        is the exact failure class #798 repaired — not something #800's
        conservative-direction blessing covers, since here the outer pair DOES
        enclose the title.

        Scoping the balance scan to the outer pair's own family fixes it: a
        `《…》` wrap tracks only `《`/`》` and is blind to quote marks."""
        for wrapped, bare in (
            ("《Alzheimer’s病中ＰｒｏＥＸＣ表达》", "Alzheimer’s病中ProEXC表达"),
            ("《’98年香港回归研究》", "’98年香港回归研究"),
        ):
            with self.subTest(wrapped=wrapped):
                self.assertEqual(ts.normalize_cn_title(wrapped), ts.normalize_cn_title(bare))
                self.assertTrue(ts.exact_normalized_title(wrapped, bare))
                self.assertEqual(ts._similarity(wrapped, bare), 1.0)

    def test_interior_scan_ignores_other_families_but_not_its_own(self) -> None:
        """The family scoping is a narrowing, not a blanket weakening: a stray
        closer of the OUTER pair's own family still blocks the strip, while a
        stray mark of any other family is content.

        `《「研究』》` is the interaction the review flagged: the interior
        `「研究』` is mismatched, but not in the `《》` family, so the outer pair
        still encloses one unit and strips. The mismatched interior marks
        survive as content — which is correct, since they are exactly what
        distinguishes this title from `《研究》`."""
        self.assertEqual(ts.normalize_cn_title("《「研究』》"), "「研究』")
        # Same-family stray closer still blocks, at any interior depth.
        self.assertEqual(ts.normalize_cn_title("《红楼梦》与《金瓶梅》"), "《红楼梦》与《金瓶梅》")

    def test_unclosed_interior_opener_blocks_the_strip(self) -> None:
        """The trailing `depth == 0` check, pinned on its own: `《基于《研究」的分析》`
        has an interior `《` that nothing closes, so the outer `》` is closing the
        INNER opener and the outer pair is not one unit."""
        self.assertEqual(
            ts.normalize_cn_title("《基于《研究」的分析》"), "《基于《研究」的分析》"
        )

    def test_stray_interior_closer_blocks_the_strip_independently(self) -> None:
        """#804 review advisory: the depth-0 stray-closer branch had no
        discriminating test — a mutant clamping it (`depth = max(0, depth - 1)`)
        instead of refusing passed the whole suite, including the two natural
        titles above.

        The reason is arithmetic, and worth recording so this test is not
        "simplified" back later: clamping absorbs one closer, so a title whose
        opener/closer counts are equal — every natural case here, including
        `《红楼梦》与《金瓶梅》` — ends at depth 1 under the mutant and is refused
        anyway, by the OTHER branch. Discriminating requires interior closers to
        outnumber openers by exactly the clamp count, which no natural title
        shape produces. Hence a deliberately synthetic string, asserted against
        the helper directly: `《》研究《实践》》` opens at depth 0 with a `》`,
        which is precisely what the branch exists to refuse."""
        self.assertFalse(ts._outer_pair_encloses("《》研究《实践》》"))
        # The natural stray-closer title stays refused too — belt and braces,
        # since this is the branch that keeps `《红楼梦》与《金瓶梅》` intact.
        self.assertFalse(ts._outer_pair_encloses("《红楼梦》与《金瓶梅》"))

    def test_mangled_key_still_matches_its_identically_mangled_counterpart(self) -> None:
        """Matching correctness was never broken by the positional strip (both
        sides mangled identically), and the pairedness fix must not change that
        either way: equal normalizations still match on both paths."""
        a = "《红楼梦》与《金瓶梅》"
        self.assertTrue(ts.exact_normalized_title(a, a))
        # The paired form now keeps its marks while an old-style bare variant
        # differs — conservative non-matching is acceptable per #800.
        self.assertFalse(ts.exact_normalized_title(a, "红楼梦》与《金瓶梅"))

    def test_ungated_client_path_narrowing_is_explicit(self) -> None:
        """#804 review advisory: the invariance claim must not be stated more
        broadly than the code supports.

        `exact_normalized_title` and `_similarity` reach the CJK form only
        behind `has_cjk`, so a Han-free title is untouched there. The client's
        `_cn_titles_match` has NO such gate — it calls `normalize_cn_title`
        directly — so a mark-carrying Han-free title can change verdict on that
        path. Pinned here as a known, accepted narrowing rather than left to be
        rediscovered: the path is DOI-keyed and Chinese-corpus-only in
        practice."""
        from chinese_literature_client import _cn_titles_match

        wrapped, mangled = "《Hamlet》and《Macbeth》", "Hamlet》and《Macbeth"
        self.assertFalse(_cn_titles_match(wrapped, mangled))
        # The gated shared helpers never saw this pair as CJK, before or after.
        self.assertFalse(ts.exact_normalized_title(wrapped, mangled))

    def test_empty_wrapper_guard_is_a_cjk_branch_property(self) -> None:
        """The "`《》` never matches" guarantee belongs to `_cjk_titles_match`,
        which requires a non-empty normalized key. `exact_normalized_title`
        still returns True for `《》` vs itself through the ungated BASE
        normalization branch — unchanged by #800, and pinned so the changelog's
        narrowed wording stays honest."""
        self.assertEqual(ts.normalize_cn_title("《》"), "")
        self.assertFalse(ts._cjk_titles_match("《》", "「」"))
        self.assertTrue(ts.exact_normalized_title("《》", "《》"))

    def test_pairedness_behavior_is_shared_by_the_cjk_client(self) -> None:
        """#800 acceptance: both consumers change together. The client
        re-imports the shared function (#799), so identity covers it — pinned
        behaviorally here so a future private copy cannot hide the drift."""
        import chinese_literature_client as cn

        title = "《红楼梦》与《金瓶梅》"
        self.assertEqual(cn.normalize_cn_title(title), ts.normalize_cn_title(title))
        self.assertEqual(cn.normalize_cn_title(title), title)

    def test_removes_whitespace_touching_han(self) -> None:
        self.assertEqual(ts.normalize_cn_title("基于 ProEXC 的研究"), "基于ProEXC的研究")

    def test_preserves_whitespace_between_latin_tokens(self) -> None:
        self.assertEqual(ts.normalize_cn_title("PD L1"), "PD L1")

    def test_preserves_case(self) -> None:
        self.assertEqual(ts.normalize_cn_title("p53"), "p53")

    def test_preserves_scientific_operators(self) -> None:
        """Unlike the base ASCII normalization, the CJK normalizer keeps `+`,
        `-`, `.` and `%` byte-significant: ER+ != ER-, 4.5% != 45%."""
        self.assertNotEqual(ts.normalize_cn_title("ER+"), ts.normalize_cn_title("ER-"))
        self.assertNotEqual(
            ts.normalize_cn_title("4.5%"), ts.normalize_cn_title("45%")
        )

    def test_handles_none(self) -> None:
        self.assertEqual(ts.normalize_cn_title(None), "")


class HasCjkTest(unittest.TestCase):
    def test_detects_han_ideograph(self) -> None:
        self.assertTrue(ts.has_cjk("基于ProEXC"))

    def test_latin_only_is_not_cjk(self) -> None:
        self.assertFalse(ts.has_cjk("ProEXC"))

    def test_fullwidth_latin_alone_is_not_cjk(self) -> None:
        """Fullwidth Latin is not a Han ideograph — a title of only fullwidth
        Latin must not enter the CJK path."""
        self.assertFalse(ts.has_cjk("ＰｒｏＥＸＣ"))

    def test_none_and_empty(self) -> None:
        self.assertFalse(ts.has_cjk(None))
        self.assertFalse(ts.has_cjk(""))


class SharedHelperReachesEveryResolverTest(unittest.TestCase):
    """The repair is only worth anything if all four index resolvers pick it up.

    Preventing sibling drift is the stated reason `_text_similarity` exists
    (#128), so pin that each client resolves the SAME function object rather
    than a re-implementation that could silently diverge again."""

    CLIENTS = (
        "semantic_scholar_client",
        "openalex_client",
        "crossref_client",
        "arxiv_client",
    )

    def test_every_resolver_shares_the_repaired_helpers(self) -> None:
        import importlib

        for name in self.CLIENTS:
            module = importlib.import_module(name)
            with self.subTest(client=name):
                self.assertIs(module._similarity, ts._similarity)
                self.assertIs(module.exact_normalized_title, ts.exact_normalized_title)

    def test_cjk_client_shares_the_promoted_normalizer(self) -> None:
        """`normalize_cn_title` was promoted out of `chinese_literature_client`;
        it must now re-import the shared one, not keep a private copy."""
        import chinese_literature_client as cn

        self.assertIs(cn.normalize_cn_title, ts.normalize_cn_title)
        self.assertIs(cn.has_cjk, ts.has_cjk)


class ConstantsTest(unittest.TestCase):
    """Lock the magic numbers — these are protocol-level invariants, not
    arbitrary tuning."""

    def test_title_similarity_threshold_is_protocol_value(self) -> None:
        """Per PaperOrchestra (Song et al. 2026 Appx D.3) + protocol §Query
        Patterns Pattern 1."""
        self.assertEqual(ts._TITLE_SIMILARITY_THRESHOLD, 0.70)

    def test_backoff_seconds(self) -> None:
        """Per protocol: 429 → 2s backoff × 3 retries."""
        self.assertEqual(ts._BACKOFF_SECONDS, 2.0)

    def test_max_retries(self) -> None:
        self.assertEqual(ts._MAX_RETRIES, 3)

    def test_punct_translation_has_all_punctuation(self) -> None:
        """`_PUNCT_TRANSLATION` should map every string.punctuation char to ' '."""
        import string

        for c in string.punctuation:
            self.assertEqual(ts._PUNCT_TRANSLATION[ord(c)], " ", f"char {c!r} not mapped to space")


if __name__ == "__main__":
    unittest.main()
