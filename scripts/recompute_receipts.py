#!/usr/bin/env python3
"""#610 step-5 deterministic arithmetic-receipt calculator.

Consumes one gate-validated ``## Recompute Extraction`` artifact (the
isolated numeric input surface: typed manuscript values transcribed by the
methodology seat, never the manuscript itself) and emits the exact
``## Arithmetic Receipts`` section grammar pinned by
``check_phase_conformance.py`` — minus ``finding_ref:`` lines, which are
linkage judgments the seat adds in Phase 2 under the injected-receipt
identity gate.

Determinism contract:

- Same extraction bytes -> same receipts bytes ON THE SAME HOST. No clock,
  no randomness, no environment reads, no filesystem access beyond the two
  CLI paths. The scope is per-platform by design: tail probabilities go
  through libm (`lgamma`/`erfc`), whose last-ulp behavior varies across
  platforms, so a value at a 3-significant-digit formatting breakpoint may
  render differently on a different OS. Every #610 cohort is dispatched and
  gated on one host, which is the domain the determinism contract serves;
  exact-rational procedures (GRIM/GRIMMER/n_from_df) are
  platform-independent outright.
- GRIM / GRIMMER / n_from_df run on exact rational arithmetic
  (``fractions.Fraction``); reported-SD reachability is decided on SD^2 so
  no square root ever enters a verdict.
- p-values use stdlib-only regularized incomplete beta/gamma
  (continued-fraction forms) plus ``math.erfc``; every verdict comparison
  carries a 1e-9 boundary guard that resolves to a ``not_computable``
  reason, never a float coin-flip.
- The calculator emits ``consistent`` / ``mismatch`` / ``not_computable``
  only. ``not_applicable`` stays grammar-legal for the self-compute path but
  an RR is by construction an applicability claim, so it is never
  script-emitted.

Exit codes: 0 receipts written; 2 the extraction artifact does not parse
(a should-never state after the ``--extraction`` conformance gate — the
dispatcher classifies it as a harness infra fault, not a conformance abort).
"""
from __future__ import annotations

import argparse
import math
import re
import sys
from dataclasses import dataclass, field
from fractions import Fraction
from pathlib import Path

EXTRACTION_SECTION = "Recompute Extraction"
RECEIPT_SECTION = "Arithmetic Receipts"
ATTESTATION_KEY = "no_recomputable_statistics"

PROCEDURES = ("p_from_test_statistic", "grim", "grimmer", "n_from_df")
TEST_FAMILIES = ("t", "z", "F", "chi_square")
COMPARATORS = (
    "equals", "less_than", "less_than_or_equal",
    "greater_than", "greater_than_or_equal",
)
TAILS = ("two-tailed", "one-tailed", "upper-tail", "unstated")
ROUNDING_RULES = ("half-up", "half-even", "truncation", "unstated")
SD_CONVENTIONS = ("sample", "population", "unstated")
DF_IDENTITIES = ("df=N-1", "df=N1+N2-2", "other_or_corrected", "unavailable")
N_RELATIONS = ("equals", "at_most", "at_least", "unavailable")

COMMON_FIELDS = (
    "procedure_id", "evidence_anchor", "reported_inputs", "assumptions",
)
PROCEDURE_FIELDS = {
    "p_from_test_statistic": (
        "test_family", "statistic_value", "df", "reported_p_comparator",
        "reported_p_value", "tail_convention",
    ),
    "grim": (
        "n", "reported_mean", "scale_min", "scale_max", "rounding_rule",
    ),
    "grimmer": (
        "n", "reported_mean", "scale_min", "scale_max", "rounding_rule",
        "reported_sd", "sd_convention",
    ),
    "n_from_df": (
        "df_reported", "df_identity_candidate", "stated_n",
        "stated_n_relation",
    ),
}
ALL_FIELD_KEYS = frozenset(COMMON_FIELDS) | {
    key for keys in PROCEDURE_FIELDS.values() for key in keys
}

# The verdict boundary guard: a derived float this close to a rounding-
# interval endpoint or inequality threshold is refused as ambiguous rather
# than decided. Far below any reported-p precision, far above the special-
# function error.
_EPS = 1e-9

# GRIMMER reachability is exhaustive or refused; this bounds the memoized
# (value-index, remaining-count, remaining-sum) state space, beyond which the
# honest status is `reachability_not_completed`. The seeded MS01 case
# (N=10, 5-point scale) uses well under 1e3 states.
_STATE_BUDGET = 200_000
# The state budget bounds COUNT, not size: each memoized state retains a
# frozenset of attainable sums of squares, so total retained elements is the
# real memory bound (security round 1, P1-2). Exceeding it is the same
# honest refusal, never an approximation.
_ELEMENT_BUDGET = 2_000_000
# GRIM's candidate-sum window is ~2n/10^places wide; a zero-decimal mean
# over a huge N would otherwise iterate without bound. Same honest refusal.
_SUM_WINDOW_BUDGET = 500_000
# Total enumeration-loop iterations across one GRIMMER reachability call:
# the state and element budgets bound what is RETAINED, this bounds what is
# VISITED (an infeasible prefix retains nothing while it spins).
_WORK_BUDGET = 5_000_000
# Numeric-domain bounds shared by the gate and the calculator (they run the
# same parser, so no accept/refuse divergence is possible). The char cap
# keeps every token far inside float range; the p-procedure magnitude cap
# is the domain over which the tail special functions are empirically
# verified to converge under the iteration ceilings below (a manuscript t,
# F, chi-square, or df beyond 1e7 is not a plausible transcription).
_MAX_NUMERIC_CHARS = 18
_MAX_P_MAGNITUDE = 10_000_000
# 10 places comfortably exceeds any journal's printed precision while
# keeping every equality comparison's half-interval (5e-11) resolvable by
# the exact-rational procedures; p comparisons finer than the float guard
# degrade to `rounding_boundary_ambiguous` via _EPS rather than deciding.
# The extraction fragment tells the seat that a value the grammar cannot
# carry is OUT OF DOMAIN — no RR — so this cap can never trap a faithful
# transcription in an unsatisfiable retry (codex round 2).
_MAX_DECIMAL_PLACES = 10
# Free-text values ride verbatim into receipts and then into the Phase 2
# card under the identity gate, so tokens that other gates read as machine
# markup are refused at the source (security round 1, P2-2/P2-3/P2-4):
# bold spans (the finding grammar's declaration markers), HTML comment
# markup (banned in the receipt section), and closing-tag shapes (the
# dispatcher's delimiter fences). Carriage returns are refused line-level —
# the card-side reader splits on CR, this parser does not, and the identity
# gate must never straddle two line models.
_FORBIDDEN_VALUE_TOKENS = ("**", "<!--", "-->", "</")

_DECIMAL_RE = re.compile(r"^-?(?:\d+\.\d+|\.\d+|\d+)$")
_INT_RE = re.compile(r"^-?\d+$")
_DF_PAIR_RE = re.compile(r"^(\d+)\s*,\s*(\d+)$")
_H2_RE = re.compile(r"^## (\S.*?)\s*$")
_H3_RE = re.compile(r"^### (\S.*?)\s*$")
_RR_TITLE_RE = re.compile(r"^RR[1-9]\d*$")
_FENCE_OPEN_RE = re.compile(r"^[ ]{0,3}(`{3,}|~{3,})(.*)$")
_FENCE_CLOSE_RE = re.compile(r"^[ ]{0,3}(`{3,}|~{3,})[ \t]*$")
# Mirrors the gate's canonical field shape: optional single list marker,
# balanced-or-absent bold around the key, one space after the colon.
_FIELD_RE = re.compile(
    r"^(?:[-*] )?(?:\*\*(?P<bkey>[a-z_]+)\*\*|(?P<key>[a-z_]+)): "
    r"(?P<value>\S.*?)\s*$"
)


class ExtractionError(ValueError):
    """The extraction artifact violates the RR grammar this module consumes."""


@dataclass
class Request:
    """One gate-validated RR subsection."""

    rr_id: str
    fields: dict[str, str]

    def __getitem__(self, key: str) -> str:
        return self.fields[key]


@dataclass
class Extraction:
    attestation: str | None
    requests: list[Request] = field(default_factory=list)


@dataclass
class Receipt:
    procedure_id: str
    evidence_anchor: str
    reported_inputs: str
    assumptions: str
    derivation: str
    derived_value_or_range: str
    comparison_rule: str
    status: str
    not_computable_reason: str | None = None
    tail_convention: str | None = None
    rounding_interval: str | None = None
    nearest_achievable: str | None = None
    df_identity: str | None = None


# --- extraction parsing ---------------------------------------------------

def parse_extraction(text: str) -> Extraction:
    lines = _section_lines(text)
    current: Request | None = None
    requests: list[Request] = []
    attestation: str | None = None
    for line in lines:
        if not line.strip():
            continue
        if "\r" in line:
            raise ExtractionError(
                "carriage return inside a machine line; the card-side "
                "reader and this parser would disagree about line breaks"
            )
        if match := _H3_RE.fullmatch(line):
            title = match.group(1)
            if not _RR_TITLE_RE.fullmatch(title):
                raise ExtractionError(f"invalid subsection heading: {title}")
            expected = f"RR{len(requests) + 1}"
            if title != expected:
                raise ExtractionError(
                    f"RR ids must be contiguous: expected {expected}, "
                    f"found {title}"
                )
            current = Request(title, {})
            requests.append(current)
            continue
        match = _FIELD_RE.fullmatch(line)
        if not match:
            raise ExtractionError(f"not a machine line: {line!r}")
        key = match.group("bkey") or match.group("key")
        value = match.group("value")
        for token in _FORBIDDEN_VALUE_TOKENS:
            if token in value:
                raise ExtractionError(
                    f"forbidden token {token!r} inside a field value; "
                    "machine-markup shapes never belong in transcribed "
                    "content"
                )
        if key == ATTESTATION_KEY:
            if current is not None or attestation is not None:
                raise ExtractionError(
                    "attestation must be the only content of the section"
                )
            attestation = value
            continue
        if current is None:
            raise ExtractionError(
                f"field line outside any RR subsection: {line!r}"
            )
        if key not in ALL_FIELD_KEYS:
            raise ExtractionError(f"unknown field: {key}")
        if key in current.fields:
            raise ExtractionError(f"{current.rr_id}: duplicate field {key}")
        current.fields[key] = value
    if attestation is not None and requests:
        raise ExtractionError("attestation and RR subsections cannot coexist")
    if attestation is None and not requests:
        raise ExtractionError(
            "section carries neither RR subsections nor the attestation"
        )
    for request in requests:
        _validate_request(request)
    return Extraction(attestation, requests)


def _section_lines(text: str) -> list[str]:
    """The extraction section's content lines, fence-transparently.

    CommonMark-stateful (codex round 1, P2-3): an opening fence remembers
    its run and only a matching closer ends it, a backtick fence's info
    string may not contain a backtick (so ```` ```bad`tick ```` is a
    paragraph line, not a silently-dropped delimiter), and only an
    UNFENCED H2 delimits — the #637/#638 display-form discipline. Interior
    lines are kept as content, so a fenced machine line is still read and
    the calculator agrees with the gate about what was said.
    """
    collected: list[str] = []
    inside = False
    found = False
    fence: str | None = None
    for raw in text.split("\n"):
        line = raw.rstrip("\r")
        if fence is not None:
            close = _FENCE_CLOSE_RE.match(line)
            if close and close.group(1)[0] == fence[0] \
                    and len(close.group(1)) >= len(fence):
                fence = None
                continue
            if inside:
                collected.append(line)
            continue
        opener = _FENCE_OPEN_RE.match(line)
        if opener and not (opener.group(1)[0] == "`"
                           and "`" in opener.group(2)):
            fence = opener.group(1)
            continue
        if match := _H2_RE.fullmatch(line):
            inside = match.group(1) == EXTRACTION_SECTION
            found = found or inside
            continue
        if inside:
            collected.append(line)
    if not found:
        raise ExtractionError(f"no ## {EXTRACTION_SECTION} section")
    return collected


def _validate_request(request: Request) -> None:
    procedure = request.fields.get("procedure_id")
    if procedure not in PROCEDURES:
        raise ExtractionError(
            f"{request.rr_id}: procedure_id must be one of {PROCEDURES}"
        )
    required = COMMON_FIELDS + PROCEDURE_FIELDS[procedure]
    for key in required:
        if key not in request.fields:
            raise ExtractionError(f"{request.rr_id}: missing field {key}")
    extra = set(request.fields) - set(required)
    if extra:
        raise ExtractionError(
            f"{request.rr_id}: fields {sorted(extra)} do not belong to "
            f"{procedure}"
        )
    enums = {
        "test_family": TEST_FAMILIES + ("unavailable",),
        "reported_p_comparator": COMPARATORS,
        "tail_convention": TAILS,
        "rounding_rule": ROUNDING_RULES,
        "sd_convention": SD_CONVENTIONS,
        "df_identity_candidate": DF_IDENTITIES,
        "stated_n_relation": N_RELATIONS,
    }
    for key, allowed in enums.items():
        if key in request.fields and request.fields[key] not in allowed:
            raise ExtractionError(
                f"{request.rr_id}: {key} must be one of {allowed}, "
                f"got {request.fields[key]!r}"
            )
    decimals = {
        "p_from_test_statistic": ("reported_p_value",),
        "grim": ("reported_mean",),
        "grimmer": ("reported_mean", "reported_sd"),
        "n_from_df": (),
    }[procedure]
    for key in decimals:
        if not _DECIMAL_RE.fullmatch(request.fields[key]):
            raise ExtractionError(
                f"{request.rr_id}: {key} must be a plain decimal, "
                f"got {request.fields[key]!r}"
            )
    optional_decimal = {"statistic_value"}
    optional_int = {"n", "scale_min", "scale_max", "stated_n"}
    required_int = {"df_reported"}
    for key in optional_decimal & set(request.fields):
        value = request.fields[key]
        if value != "unavailable" and not _DECIMAL_RE.fullmatch(value):
            raise ExtractionError(
                f"{request.rr_id}: {key} must be a decimal or "
                f"'unavailable', got {value!r}"
            )
    for key in (optional_int | required_int) & set(request.fields):
        value = request.fields[key]
        allow_sentinel = key in optional_int
        if not _INT_RE.fullmatch(value) and not (
            allow_sentinel and value == "unavailable"
        ):
            raise ExtractionError(
                f"{request.rr_id}: {key} must be an integer"
                + (" or 'unavailable'" if allow_sentinel else "")
                + f", got {value!r}"
            )
    if procedure == "p_from_test_statistic":
        df_value = request.fields["df"]
        if df_value not in ("none", "unavailable") and not (
            _INT_RE.fullmatch(df_value) or _DF_PAIR_RE.fullmatch(df_value)
        ):
            raise ExtractionError(
                f"{request.rr_id}: df must be an integer, 'int,int', "
                f"'none', or 'unavailable', got {df_value!r}"
            )
        # Family-consistent df shape (codex round 1, P2-2): a t with an F
        # df pair is a transcription slip, and refusing it HERE makes it a
        # retryable gate diagnostic instead of a misleading not_computable
        # receipt downstream.
        family = request.fields["test_family"]
        shape_rules = {
            "t": (lambda v: _INT_RE.fullmatch(v),
                  "a single integer df"),
            "chi_square": (lambda v: _INT_RE.fullmatch(v),
                           "a single integer df"),
            "z": (lambda v: v == "none", "df 'none'"),
            "F": (lambda v: _DF_PAIR_RE.fullmatch(v), "df as 'df1,df2'"),
        }
        if family in shape_rules and df_value != "unavailable":
            accepts, description = shape_rules[family]
            if not accepts(df_value):
                raise ExtractionError(
                    f"{request.rr_id}: a {family} statistic carries "
                    f"{description} (or 'unavailable'), got {df_value!r}"
                )
    _validate_numeric_domain(request, procedure)


def _validate_numeric_domain(request: Request, procedure: str) -> None:
    """Shared gate/calculator domain bounds (security round 1, P1-2/P2-1).

    Everything accepted here is verified computable: the char cap keeps
    every token far inside float range, the p-magnitude cap is the
    empirically-verified convergence domain of the tail functions, and the
    decimal-places cap bounds every rounding-interval denominator. GRIM /
    GRIMMER magnitudes are deliberately NOT capped here — their compute
    layer refuses over-budget searches with the honest
    `reachability_not_completed` instead.
    """
    numeric_keys = (
        "statistic_value", "df", "reported_p_value", "n", "reported_mean",
        "scale_min", "scale_max", "reported_sd", "df_reported", "stated_n",
    )
    for key in numeric_keys:
        value = request.fields.get(key)
        if value is None or value in ("unavailable", "none"):
            continue
        for token in re.split(r"[,\s]+", value):
            if len(token) > _MAX_NUMERIC_CHARS:
                raise ExtractionError(
                    f"{request.rr_id}: {key} token {token!r} exceeds "
                    f"{_MAX_NUMERIC_CHARS} characters; not a plausible "
                    "manuscript value"
                )
    decimal_keys = {
        "p_from_test_statistic": ("reported_p_value",),
        "grim": ("reported_mean",),
        "grimmer": ("reported_mean", "reported_sd"),
        "n_from_df": (),
    }[procedure]
    for key in decimal_keys:
        _, places = _parse_decimal(request.fields[key])
        if places > _MAX_DECIMAL_PLACES:
            raise ExtractionError(
                f"{request.rr_id}: {key} reports more than "
                f"{_MAX_DECIMAL_PLACES} decimal places; not a plausible "
                "manuscript precision"
            )
    if procedure == "p_from_test_statistic":
        statistic = request.fields["statistic_value"]
        if statistic != "unavailable" and abs(
                Fraction(statistic)) > _MAX_P_MAGNITUDE:
            raise ExtractionError(
                f"{request.rr_id}: statistic_value exceeds the verified "
                f"convergence domain (|value| <= {_MAX_P_MAGNITUDE})"
            )
        df_value = request.fields["df"]
        if df_value not in ("none", "unavailable"):
            pair = _DF_PAIR_RE.fullmatch(df_value)
            components = (
                (int(pair.group(1)), int(pair.group(2))) if pair
                else (int(df_value),)
            )
            if any(component > _MAX_P_MAGNITUDE
                   for component in components):
                raise ExtractionError(
                    f"{request.rr_id}: df exceeds the verified "
                    f"convergence domain (df <= {_MAX_P_MAGNITUDE})"
                )


# --- exact rational helpers ----------------------------------------------

def _parse_decimal(text: str) -> tuple[Fraction, int]:
    """Exact value and its reported decimal precision."""
    if not _DECIMAL_RE.fullmatch(text):
        raise ExtractionError(f"not a decimal: {text!r}")
    places = len(text.split(".")[1]) if "." in text else 0
    return Fraction(text), places


def _rounds_to(value: Fraction, reported: Fraction, places: int,
               rule: str) -> bool:
    """Does ``value`` round to ``reported`` at ``places`` decimals?

    Exact: ties are decided by the named rule, never by binary floating
    point. ``reported`` must be exactly representable at ``places`` (it is:
    it was parsed from that digit string).
    """
    scale = 10 ** places
    scaled = value * scale
    target = reported * scale
    if target.denominator != 1:
        raise AssertionError("reported value not exact at stated precision")
    floor = scaled.numerator // scaled.denominator
    frac = scaled - floor
    if rule == "half-up":
        # Round half away from zero.
        if scaled >= 0:
            rounded = floor + (1 if frac >= Fraction(1, 2) else 0)
        else:
            rounded = floor + (1 if frac > Fraction(1, 2) else 0)
    elif rule == "half-even":
        if frac > Fraction(1, 2):
            rounded = floor + 1
        elif frac < Fraction(1, 2):
            rounded = floor
        else:
            rounded = floor if floor % 2 == 0 else floor + 1
    elif rule == "truncation":
        # Toward zero.
        rounded = floor if scaled >= 0 else floor + (1 if frac else 0)
    else:
        raise AssertionError(f"unknown rounding rule {rule!r}")
    return rounded == target.numerator


def _fmt_fraction(value: Fraction, places: int) -> str:
    """Fixed-point decimal rendering of an exact rational (half-up ties)."""
    sign = "-" if value < 0 else ""
    magnitude = abs(value) * 10 ** places
    units = magnitude.numerator // magnitude.denominator
    if magnitude - units >= Fraction(1, 2):
        units += 1
    digits = str(units).rjust(places + 1, "0")
    if places == 0:
        return sign + digits
    return f"{sign}{digits[:-places]}.{digits[-places:]}"


def _fmt_p(value: float) -> str:
    # Near 1, three significant digits would print a literal "1" beside a
    # verdict that depends on the value being below 1 — an internally
    # contradictory receipt (codex round 2). Show enough digits to keep
    # the displayed value on the same side of 1 as the compared one.
    if 0.999 < value < 1.0:
        return f"{value:.12g}"
    return f"{value:.3g}"


def _interval_text(reported: Fraction, places: int, rules: list[str],
                   quantity: str) -> str:
    """The reporting interval under the operative rounding rule(s), stated
    with its true endpoint behavior (codex round 1, P1-2): a receipt must
    never print a half-up-shaped interval for a truncation or ties-to-even
    verdict — the interval line is part of what adjudication audits.
    """
    step = Fraction(1, 10 ** places)
    half = step / 2
    decimals = places + 1
    if rules == ["truncation"]:
        # Toward zero: [v, v+step) for v > 0, (v-step, v] for v < 0, and
        # BOTH sides for v == 0 — truncation maps (-step, step) to zero
        # (codex round 2).
        if reported == 0:
            return (f"{_fmt_fraction(-step, decimals)} < {quantity} < "
                    f"{_fmt_fraction(step, decimals)} (truncation)")
        if reported > 0:
            return (f"{_fmt_fraction(reported, decimals)} <= {quantity} < "
                    f"{_fmt_fraction(reported + step, decimals)} "
                    "(truncation)")
        return (f"{_fmt_fraction(reported - step, decimals)} < {quantity} "
                f"<= {_fmt_fraction(reported, decimals)} (truncation)")
    low_text = _fmt_fraction(reported - half, decimals)
    high_text = _fmt_fraction(reported + half, decimals)
    if rules == ["half-up"]:
        # Ties away from zero: the tie endpoint on the zero side is
        # included, the other excluded.
        if reported >= 0:
            return (f"{low_text} <= {quantity} < {high_text} "
                    "(half-up, ties away from zero)")
        return (f"{low_text} < {quantity} <= {high_text} "
                "(half-up, ties away from zero)")
    if rules == ["half-even"]:
        # Endpoint membership is the target's parity: an even last digit
        # claims both tie endpoints, an odd one claims neither (codex
        # round 2 — the closed-interval display was wrong for odd
        # targets).
        target_even = (reported * 10 ** places).numerator % 2 == 0
        if target_even:
            return (f"{low_text} <= {quantity} <= {high_text} "
                    "(ties-to-even; both endpoint ties round to this even "
                    "value)")
        return (f"{low_text} < {quantity} < {high_text} (ties-to-even; "
                "the endpoint ties round to the even neighbors)")
    return (f"{low_text} <= {quantity} <= {high_text} (interval interior; "
            "endpoint ties depend on the unstated rule, and a verdict is "
            "issued only where half-up and ties-to-even agree)")


# --- stdlib distribution tails -------------------------------------------

def _reg_inc_beta(a: float, b: float, x: float,
                  one_minus_x: float | None = None) -> float:
    """Regularized incomplete beta I_x(a, b), continued-fraction form.

    Callers that know the complement analytically pass it explicitly: near
    x = 1 the float subtraction 1.0 - x loses every significant digit and a
    near-zero t/F statistic would collapse to exactly 1.0 (codex round 1,
    P1-1) — a wrong verdict, not just a display error.
    """
    if one_minus_x is None:
        one_minus_x = 1.0 - x
    if x <= 0.0:
        return 0.0
    if one_minus_x <= 0.0:
        return 1.0
    ln_front = (
        math.lgamma(a + b) - math.lgamma(a) - math.lgamma(b)
        + a * math.log(x) + b * math.log(one_minus_x)
    )
    front = math.exp(ln_front)
    if x < (a + 1.0) / (a + b + 2.0):
        return front * _betacf(a, b, x) / a
    return 1.0 - front * _betacf(b, a, one_minus_x) / b


def _betacf(a: float, b: float, x: float) -> float:
    """Lentz continued fraction for the incomplete beta (NR §6.4 form)."""
    tiny = 1e-300
    qab, qap, qam = a + b, a + 1.0, a - 1.0
    c = 1.0
    d = 1.0 - qab * x / qap
    if abs(d) < tiny:
        d = tiny
    d = 1.0 / d
    h = d
    for m in range(1, 20000):
        m2 = 2 * m
        numerator = m * (b - m) * x / ((qam + m2) * (a + m2))
        d = 1.0 + numerator * d
        if abs(d) < tiny:
            d = tiny
        c = 1.0 + numerator / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        h *= d * c
        numerator = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
        d = 1.0 + numerator * d
        if abs(d) < tiny:
            d = tiny
        c = 1.0 + numerator / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-14:
            return h
    raise ArithmeticError("incomplete beta failed to converge")


def _reg_gamma_q(a: float, x: float) -> float:
    """Regularized upper incomplete gamma Q(a, x)."""
    if x < 0.0 or a <= 0.0:
        raise ArithmeticError("invalid incomplete gamma arguments")
    if x == 0.0:
        return 1.0
    if x < a + 1.0:
        # Series for P, complement for Q.
        term = 1.0 / a
        total = term
        current = a
        for _ in range(20000):
            current += 1.0
            term *= x / current
            total += term
            if abs(term) < abs(total) * 1e-15:
                break
        else:
            raise ArithmeticError("incomplete gamma series did not converge")
        ln_p = -x + a * math.log(x) - math.lgamma(a)
        return 1.0 - total * math.exp(ln_p)
    # Lentz continued fraction for Q directly.
    tiny = 1e-300
    b0 = x + 1.0 - a
    c = 1.0 / tiny
    d = 1.0 / b0
    h = d
    for i in range(1, 20000):
        an = -i * (i - a)
        b0 += 2.0
        d = an * d + b0
        if abs(d) < tiny:
            d = tiny
        c = b0 + an / c
        if abs(c) < tiny:
            c = tiny
        d = 1.0 / d
        delta = d * c
        h *= delta
        if abs(delta - 1.0) < 1e-14:
            break
    else:
        raise ArithmeticError("incomplete gamma fraction did not converge")
    ln_front = -x + a * math.log(x) - math.lgamma(a)
    return math.exp(ln_front) * h


def t_tail_two(t: float, df: int) -> float:
    denominator = df + t * t
    return _reg_inc_beta(df / 2.0, 0.5, df / denominator,
                         one_minus_x=(t * t) / denominator)


def t_tail_upper(t: float, df: int) -> float:
    half = t_tail_two(t, df) / 2.0
    return half if t >= 0 else 1.0 - half


def z_tail_two(z: float) -> float:
    return math.erfc(abs(z) / math.sqrt(2.0))


def z_tail_upper(z: float) -> float:
    return math.erfc(z / math.sqrt(2.0)) / 2.0


def f_tail_upper(f_value: float, df1: int, df2: int) -> float:
    denominator = df2 + df1 * f_value
    return _reg_inc_beta(df2 / 2.0, df1 / 2.0, df2 / denominator,
                         one_minus_x=(df1 * f_value) / denominator)


def chi2_tail_upper(chi2: float, df: int) -> float:
    return _reg_gamma_q(df / 2.0, chi2 / 2.0)


# --- procedure: p_from_test_statistic ------------------------------------

_COMPARATOR_TEXT = {
    "equals": "=", "less_than": "<", "less_than_or_equal": "<=",
    "greater_than": ">", "greater_than_or_equal": ">=",
}


def _p_receipt(request: Request) -> Receipt:
    base = _base_receipt(request)
    base.tail_convention = request["tail_convention"]
    family = request["test_family"]
    comparator = request["reported_p_comparator"]
    reported, places = _parse_decimal(request["reported_p_value"])
    reported_text = request["reported_p_value"]

    def stop(reason: str, why: str) -> Receipt:
        return _not_computable(base, reason, why)

    if family == "unavailable":
        return stop("test_family_ambiguous",
                    "the test family is not identifiable from the report")
    if request["statistic_value"] == "unavailable":
        return stop("missing_reported_value",
                    "the test statistic is not reported")
    statistic = float(Fraction(request["statistic_value"]))
    df_value = request["df"]
    if df_value == "unavailable":
        return stop("missing_reported_value",
                    "the degrees of freedom are not reported")
    tail = request["tail_convention"]
    if family in ("F", "chi_square"):
        if tail not in ("upper-tail", "unstated"):
            return stop(
                "nonstandard_p_procedure",
                f"{family} tests are upper-tail by family; a paper-stated "
                f"{tail} p has no bounded procedure here",
            )
        if statistic < 0:
            return stop("nonstandard_p_procedure",
                        f"a negative {family} statistic is not interpretable")
        # Family normalization: the receipt names the operative tail. An
        # unstated extraction stays honest about the paper, but F and
        # chi-square are upper-tail by family (§5.1), so the receipt's
        # tail_convention is the family rule — also what exempts these
        # receipts from the both-tails display rule, which has no second
        # tail to show here.
        base.tail_convention = "upper-tail"
    # Tail probabilities per licensed tail label.
    if family == "t":
        if not _INT_RE.fullmatch(df_value):
            return stop("df_identity_ambiguous",
                        "a t statistic needs a single integer df")
        df = int(df_value)
        if df < 1:
            return stop("missing_reported_value", "df must be at least 1")
        tails = {
            "two-tailed": t_tail_two(statistic, df),
            "one-tailed": t_tail_two(statistic, df) / 2.0,
            "upper-tail": t_tail_upper(statistic, df),
        }
        derivation = (
            f"t distribution, df={df}: tail probabilities of |t|={abs(statistic)} "
            "via the regularized incomplete beta; the two-tailed value doubles "
            "the one-tailed"
        )
    elif family == "z":
        if df_value != "none":
            return stop("df_identity_ambiguous",
                        "a z statistic carries no df; extraction must say "
                        "'none'")
        tails = {
            "two-tailed": z_tail_two(statistic),
            "one-tailed": z_tail_two(statistic) / 2.0,
            "upper-tail": z_tail_upper(statistic),
        }
        derivation = (
            f"standard normal: tail probabilities of |z|={abs(statistic)} via "
            "erfc; the two-tailed value doubles the one-tailed"
        )
    elif family == "F":
        pair = _DF_PAIR_RE.fullmatch(df_value)
        if not pair:
            return stop("df_identity_ambiguous",
                        "an F statistic needs df as 'df1,df2'")
        df1, df2 = int(pair.group(1)), int(pair.group(2))
        if df1 < 1 or df2 < 1:
            return stop("missing_reported_value",
                        "F dfs must be at least 1")
        tails = {"upper-tail": f_tail_upper(statistic, df1, df2)}
        derivation = (
            f"F distribution, df=({df1},{df2}): upper-tail probability of "
            f"F={statistic} via the regularized incomplete beta"
        )
    else:  # chi_square
        if not _INT_RE.fullmatch(df_value):
            return stop("df_identity_ambiguous",
                        "a chi-square statistic needs a single integer df")
        df = int(df_value)
        if df < 1:
            return stop("missing_reported_value", "df must be at least 1")
        tails = {"upper-tail": chi2_tail_upper(statistic, df)}
        derivation = (
            f"chi-square distribution, df={df}: upper-tail probability of "
            f"chi2={statistic} via the regularized upper incomplete gamma"
        )

    if family in ("F", "chi_square"):
        candidates = [("upper-tail", tails["upper-tail"])]
    elif tail == "unstated":
        candidates = [
            ("two-tailed", tails["two-tailed"]),
            ("one-tailed", tails["one-tailed"]),
        ]
    else:
        candidates = [(tail, tails[tail])]

    verdicts = []
    for _, derived in candidates:
        verdict = _compare_p(derived, comparator, reported, places)
        if verdict == "boundary":
            return stop(
                "rounding_boundary_ambiguous",
                "a derived tail probability sits on the reported value's "
                "rounding-interval boundary within numeric tolerance",
            )
        if verdict == "threshold":
            return stop(
                "inequality_unresolvable",
                "a derived tail probability equals the reported inequality "
                "threshold within numeric tolerance",
            )
        verdicts.append(verdict)

    shown = "; ".join(
        f"p = {_fmt_p(derived)} ({label})" for label, derived in candidates
    )
    base.derivation = derivation
    base.derived_value_or_range = shown
    if comparator == "equals":
        base.comparison_rule = (
            f"reported p = {reported_text} at {places} decimals: a tail is "
            "compatible only if its derived probability falls in that "
            "rounding interval"
        )
    else:
        base.comparison_rule = (
            f"reported p {_COMPARATOR_TEXT[comparator]} {reported_text}: a "
            "tail is compatible only if its derived probability satisfies "
            "the inequality"
        )
    if len(set(verdicts)) > 1:
        return stop(
            "tail_ambiguous",
            "the verdict depends on an unstated tail choice: "
            + shown,
        )
    base.status = "consistent" if verdicts[0] == "pass" else "mismatch"
    return base


def _compare_p(derived: float, comparator: str, reported: Fraction,
               places: int) -> str:
    reported_f = float(reported)
    if comparator == "equals":
        half = 0.5 * 10.0 ** (-places)
        low, high = reported_f - half, reported_f + half
        if abs(derived - low) < _EPS or abs(derived - high) < _EPS:
            return "boundary"
        return "pass" if low < derived < high else "fail"
    if abs(derived - reported_f) < _EPS:
        return "threshold"
    satisfied = {
        "less_than": derived < reported_f,
        "less_than_or_equal": derived <= reported_f,
        "greater_than": derived > reported_f,
        "greater_than_or_equal": derived >= reported_f,
    }[comparator]
    return "pass" if satisfied else "fail"


# --- procedure: grim ------------------------------------------------------

def _grim_rules(request: Request) -> list[str]:
    rule = request["rounding_rule"]
    return ["half-up", "half-even"] if rule == "unstated" else [rule]


def _grim_ints(request: Request, base: Receipt) -> tuple | Receipt:
    if request["n"] == "unavailable":
        return _not_computable(base, "analytic_n_ambiguous",
                               "the item-specific analytic N is not reported")
    if request["scale_min"] == "unavailable" or (
            request["scale_max"] == "unavailable"):
        return _not_computable(base, "scale_support_unknown",
                               "the response-scale support is not reported")
    n = int(request["n"])
    lo, hi = int(request["scale_min"]), int(request["scale_max"])
    if n < 1 or lo > hi:
        return _not_computable(base, "scale_support_unknown",
                               "N or the scale bounds are not interpretable")
    return n, lo, hi


def _reachable_sums(n: int, lo: int, hi: int, reported: Fraction,
                    places: int, rule: str) -> list[int]:
    step = Fraction(1, 10 ** places)
    window_low = max(n * lo, math.floor((reported - step) * n) - 1)
    window_high = min(n * hi, math.ceil((reported + step) * n) + 1)
    if window_high - window_low > _SUM_WINDOW_BUDGET:
        raise _BudgetExceeded
    return [
        total for total in range(window_low, window_high + 1)
        if _rounds_to(Fraction(total, n), reported, places, rule)
    ]


def _grim_neighbors(n: int, lo: int, hi: int,
                    reported: Fraction) -> list[tuple[int, Fraction]]:
    target = reported * n
    below = math.floor(target)
    above = below + 1
    neighbors = []
    for total in (below, above):
        clamped = min(max(total, n * lo), n * hi)
        neighbors.append((clamped, Fraction(clamped, n)))
    return neighbors


def _grim_receipt(request: Request) -> Receipt:
    base = _base_receipt(request)
    ints = _grim_ints(request, base)
    if isinstance(ints, Receipt):
        return ints
    n, lo, hi = ints
    reported, places = _parse_decimal(request["reported_mean"])
    mean_text = request["reported_mean"]
    rules = _grim_rules(request)
    try:
        reachable = {rule: _reachable_sums(n, lo, hi, reported, places, rule)
                     for rule in rules}
    except _BudgetExceeded:
        return _not_computable(
            base, "reachability_not_completed",
            "the candidate-sum search exceeds this calculator's documented "
            "window budget",
        )
    verdicts = {rule: bool(sums) for rule, sums in reachable.items()}
    interval = _interval_text(reported, places, rules, "mean")
    neighbor_places = max(places + 1, 4)
    neighbors = "; ".join(
        f"{total}/{n} = {_fmt_fraction(value, neighbor_places)}"
        for total, value in _grim_neighbors(n, lo, hi, reported)
    )
    base.derivation = (
        f"an unweighted mean of N={n} integer responses on [{lo},{hi}] must "
        f"be an integer sum divided by {n}; candidate sums range over "
        f"[{n * lo},{n * hi}]"
    )
    base.comparison_rule = (
        f"the reported mean {mean_text} at {places} decimals is reachable "
        "only if some integer sum lands in its rounding interval under "
        + ("the stated rounding rule" if len(rules) == 1
           else "every conventional rounding rule (half-up, half-even)")
    )
    base.rounding_interval = interval
    if len(set(verdicts.values())) > 1:
        return _not_computable(
            base, "rounding_rule_ambiguous",
            "reachability changes with the unstated rounding rule",
        )
    reachable_now = next(iter(verdicts.values()))
    if reachable_now:
        achieving = reachable[rules[0]][0]
        base.derived_value_or_range = (
            f"sum {achieving} gives {achieving}/{n} = "
            f"{_fmt_fraction(Fraction(achieving, n), neighbor_places)}, "
            f"which rounds to {mean_text}"
        )
        base.nearest_achievable = (
            f"achieving sum {achieving}; adjacent sums {neighbors}"
        )
        base.status = "consistent"
    else:
        base.derived_value_or_range = (
            f"no integer sum in [{n * lo},{n * hi}] rounds to {mean_text} "
            f"at {places} decimals"
        )
        base.nearest_achievable = neighbors
        base.status = "mismatch"
    return base


# --- procedure: grimmer ---------------------------------------------------

class _BudgetExceeded(Exception):
    pass


def _attainable_sumsq(n: int, lo: int, hi: int, total: int) -> frozenset:
    """Every attainable sum of squares over n integers in [lo, hi] summing
    to ``total``. Memoized exhaustive enumeration; raises when the state
    budget is exceeded rather than approximating."""
    values = list(range(lo, hi + 1))
    cache: dict[tuple[int, int, int], frozenset] = {}
    retained = 0
    work = 0

    def rec(index: int, count: int, remaining: int) -> frozenset:
        nonlocal retained, work
        if count == 0:
            return frozenset({0}) if remaining == 0 else frozenset()
        if index == len(values) - 1:
            value = values[index]
            if remaining == value * count:
                return frozenset({value * value * count})
            return frozenset()
        key = (index, count, remaining)
        if key in cache:
            return cache[key]
        if len(cache) > _STATE_BUDGET or retained > _ELEMENT_BUDGET:
            raise _BudgetExceeded
        value = values[index]
        rest_lo, rest_hi = values[index + 1], values[-1]
        results = set()
        for chosen in range(count + 1):
            # The work counter bounds ITERATIONS, not just states: a long
            # infeasible prefix creates no cache entry, so a state-count
            # budget alone could spin unbounded before ever firing
            # (security round 2, NEW-2).
            work += 1
            if work > _WORK_BUDGET:
                raise _BudgetExceeded
            left = count - chosen
            leftover = remaining - chosen * value
            if not left * rest_lo <= leftover <= left * rest_hi:
                continue
            for sub in rec(index + 1, left, leftover):
                results.add(chosen * value * value + sub)
        frozen = frozenset(results)
        cache[key] = frozen
        retained += len(frozen)
        return frozen

    return rec(0, n, total)


def _sd_reachable(variances: set[Fraction], reported: Fraction, places: int,
                  rule: str) -> bool:
    """Is any attainable SD (given as its exact square) reportable as
    ``reported`` at ``places`` decimals under ``rule``? Decided on SD^2, so
    only a rational SD exactly on an interval endpoint needs the tie rule."""
    step = Fraction(1, 10 ** places)
    if rule == "truncation":
        low, high = reported, reported + step
        low_closed = True
    else:
        half = step / 2
        low, high = reported - half, reported + half
        low_closed = None  # endpoint membership decided by the tie rule
    if high <= 0:
        # A nonpositive reporting interval is unreachable outright: an SD
        # is nonnegative by definition, and clamping only the lower
        # endpoint before squaring silently inverted the interval for a
        # negative reported SD (codex round 1, P1-3).
        return False
    low = max(low, Fraction(0))
    low_sq, high_sq = low * low, high * high
    for variance in variances:
        if low_sq < variance < high_sq:
            return True
        for endpoint, square in ((low, low_sq), (high, high_sq)):
            if variance == square:
                # SD is exactly the rational endpoint; ask the tie rule.
                if rule == "truncation":
                    if endpoint == low and low_closed:
                        return True
                elif _rounds_to(endpoint, reported, places, rule):
                    return True
    return False


def _grimmer_receipt(request: Request) -> Receipt:
    base = _base_receipt(request)
    ints = _grim_ints(request, base)
    if isinstance(ints, Receipt):
        return ints
    n, lo, hi = ints
    convention = request["sd_convention"]
    if n < 2:
        # A population SD is defined (zero) for one response; a sample SD
        # is not (codex round 1, P2-1). Only the genuinely undefined or
        # convention-dependent cases stop here.
        if convention == "sample":
            return _not_computable(
                base, "analytic_n_ambiguous",
                "a sample SD is undefined for a single response")
        if convention == "unstated":
            return _not_computable(
                base, "sd_convention_unknown",
                "with one response a population SD is defined (zero) but "
                "a sample SD is not; the verdict depends on the unstated "
                "convention")
    mean_reported, mean_places = _parse_decimal(request["reported_mean"])
    sd_reported, sd_places = _parse_decimal(request["reported_sd"])
    sd_text = request["reported_sd"]
    rules = _grim_rules(request)
    conventions = (
        ["sample", "population"] if convention == "unstated"
        else [convention]
    )
    per_rule: dict[str, dict[str, str]] = {}
    variance_sets: dict[str, dict[str, set[Fraction]]] = {}
    try:
        for rule in rules:
            sums = _reachable_sums(n, lo, hi, mean_reported, mean_places,
                                   rule)
            if not sums:
                per_rule[rule] = {conv: "mean_fail" for conv in conventions}
                continue
            variances: dict[str, set[Fraction]] = {
                conv: set() for conv in conventions
            }
            for total in sums:
                for sumsq in _attainable_sumsq(n, lo, hi, total):
                    centered = Fraction(sumsq) - Fraction(total * total, n)
                    if "sample" in variances:
                        variances["sample"].add(centered / (n - 1))
                    if "population" in variances:
                        variances["population"].add(centered / n)
                    # n == 1 reaches here only as population-stated, where
                    # centered is identically zero; the sample division
                    # above is guarded by the n < 2 gate.
            variance_sets[rule] = variances
            per_rule[rule] = {
                conv: (
                    "reachable"
                    if _sd_reachable(variances[conv], sd_reported,
                                     sd_places, rule)
                    else "unreachable"
                )
                for conv in conventions
            }
    except _BudgetExceeded:
        return _not_computable(
            base, "reachability_not_completed",
            "the exhaustive feasible-value search exceeds this calculator's "
            "documented state budget",
        )

    base.derivation = (
        f"mean-compatible integer sums are enumerated first (GRIM); for "
        f"each, every attainable sum of squares over N={n} responses on "
        f"[{lo},{hi}] is enumerated exhaustively and the implied SD is "
        "compared exactly on its square"
    )
    base.rounding_interval = _interval_text(
        sd_reported, sd_places, rules, "SD")
    base.comparison_rule = (
        f"the reported SD {sd_text} at {sd_places} decimals is reachable "
        "only if some attainable SD lands in its rounding interval; "
        + ("the stated " if len(rules) == 1 else "every conventional ")
        + "rounding rule applies to the mean and the SD alike"
    )
    # Decision order (documented, deterministic): the mean's own GRIM gate
    # first; then an unstated rounding rule that changes any verdict; then
    # an unstated SD convention that does.
    mean_failed = [
        rule for rule in rules
        if per_rule[rule][conventions[0]] == "mean_fail"
    ]
    if len(mean_failed) == len(rules):
        return _not_computable(
            base, "mean_grim_inconsistent",
            "the reported mean is itself GRIM-inconsistent, so no response "
            "set exists whose SD could be checked",
        )
    if mean_failed:
        return _not_computable(
            base, "rounding_rule_ambiguous",
            "the mean is reachable under one unstated rounding rule and "
            "unreachable under another",
        )
    for conv in conventions:
        if len({per_rule[rule][conv] for rule in rules}) > 1:
            return _not_computable(
                base, "rounding_rule_ambiguous",
                "reachability changes with the unstated rounding rule",
            )
    outcomes = {per_rule[rules[0]][conv] for conv in conventions}
    if len(outcomes) > 1:
        return _not_computable(
            base, "sd_convention_unknown",
            "the verdict depends on whether the reported SD is the sample "
            "or the population statistic",
        )
    outcome = outcomes.pop()
    first_rule = rules[0]
    conv_label = (
        conventions[0] if len(conventions) == 1
        else "sample-or-population"
    )
    variances = variance_sets[first_rule][conventions[0]]
    nearest = _nearest_sds(variances, sd_reported)
    base.nearest_achievable = nearest
    if outcome == "reachable":
        base.derived_value_or_range = (
            f"an attainable {conv_label} SD rounds to {sd_text}; nearest "
            f"attainable values: {nearest}"
        )
        base.status = "consistent"
    else:
        base.derived_value_or_range = (
            f"no attainable {conv_label} SD rounds to {sd_text} at "
            f"{sd_places} decimals; nearest attainable values: {nearest}"
        )
        base.status = "mismatch"
    return base


def _nearest_sds(variances: set[Fraction], reported: Fraction) -> str:
    if not variances:
        return "none (no attainable response set)"
    reported_sq = reported * reported
    below = [v for v in variances if v <= reported_sq]
    above = [v for v in variances if v >= reported_sq]
    parts = []
    if below:
        parts.append(f"SD = {math.sqrt(max(below)):.4f}")
    if above:
        parts.append(f"SD = {math.sqrt(min(above)):.4f}")
    return " and ".join(parts)


# --- procedure: n_from_df -------------------------------------------------

_IDENTITY_OFFSETS = {"df=N-1": 1, "df=N1+N2-2": 2}


def _n_from_df_receipt(request: Request) -> Receipt:
    base = _base_receipt(request)
    identity = request["df_identity_candidate"]
    if identity == "other_or_corrected":
        return _not_computable(
            base, "model_correction_or_pooling",
            "the analysis uses a corrected, pooled, or model-based df whose "
            "required inputs are not present",
        )
    if identity == "unavailable":
        return _not_computable(
            base, "df_identity_ambiguous",
            "no test-specific df identity is identifiable from the report",
        )
    if request["stated_n"] == "unavailable" or (
            request["stated_n_relation"] == "unavailable"):
        return _not_computable(
            base, "missing_reported_value",
            "no manuscript N claim is available to compare the implied N "
            "against",
        )
    df_reported = int(request["df_reported"])
    stated_n = int(request["stated_n"])
    relation = request["stated_n_relation"]
    implied = df_reported + _IDENTITY_OFFSETS[identity]
    ceiling_note = (
        "; Welch-Satterthwaite df cannot exceed the ordinary total-df "
        "ceiling, so every variant needs at least this N"
        if identity == "df=N1+N2-2" else ""
    )
    base.derivation = (
        f"{identity} gives implied N = {df_reported} + "
        f"{_IDENTITY_OFFSETS[identity]} = {implied}{ceiling_note}"
    )
    base.derived_value_or_range = f"implied N = {implied}"
    relation_text = {
        "equals": f"must equal the stated N = {stated_n}",
        "at_most": f"must not exceed the stated bound N <= {stated_n}",
        "at_least": f"must not fall below the stated bound N >= {stated_n}",
    }[relation]
    base.comparison_rule = f"the implied N {relation_text}"
    mismatch = {
        "equals": implied != stated_n,
        "at_most": implied > stated_n,
        "at_least": implied < stated_n,
    }[relation]
    base.df_identity = identity
    base.status = "mismatch" if mismatch else "consistent"
    return base


# --- receipt assembly -----------------------------------------------------

def _base_receipt(request: Request) -> Receipt:
    return Receipt(
        procedure_id=request["procedure_id"],
        evidence_anchor=request["evidence_anchor"],
        reported_inputs=request["reported_inputs"],
        assumptions=request["assumptions"],
        derivation="", derived_value_or_range="", comparison_rule="",
        status="",
    )


def _not_computable(base: Receipt, reason: str, why: str) -> Receipt:
    base.status = "not_computable"
    base.not_computable_reason = reason
    if not base.derivation:
        base.derivation = f"stopped before derivation: {why}"
    if not base.derived_value_or_range:
        base.derived_value_or_range = "none (procedure stopped)"
    if not base.comparison_rule:
        base.comparison_rule = "none (no comparison was licensed)"
    return base


_PROCEDURE_IMPL = {
    "p_from_test_statistic": _p_receipt,
    "grim": _grim_receipt,
    "grimmer": _grimmer_receipt,
    "n_from_df": _n_from_df_receipt,
}


def compute_receipts(extraction: Extraction) -> str:
    """Render the full ``## Arithmetic Receipts`` section, trailing newline
    included. ``finding_ref:`` is never emitted here — linkage is the seat's
    Phase 2 judgment, enforced by the injected-receipt identity gate."""
    lines = [f"## {RECEIPT_SECTION}", ""]
    if extraction.attestation is not None:
        lines.append(f"{ATTESTATION_KEY}: {extraction.attestation}")
        return "\n".join(lines) + "\n"
    for index, request in enumerate(extraction.requests, start=1):
        receipt = _PROCEDURE_IMPL[request["procedure_id"]](request)
        lines.append(f"### AR{index}")
        lines.append(f"procedure_id: {receipt.procedure_id}")
        lines.append(f"evidence_anchor: {receipt.evidence_anchor}")
        lines.append(f"reported_inputs: {receipt.reported_inputs}")
        lines.append(f"assumptions: {receipt.assumptions}")
        lines.append(f"derivation: {receipt.derivation}")
        lines.append(
            f"derived_value_or_range: {receipt.derived_value_or_range}"
        )
        lines.append(f"comparison_rule: {receipt.comparison_rule}")
        lines.append(f"status: {receipt.status}")
        if receipt.not_computable_reason is not None:
            lines.append(
                f"not_computable_reason: {receipt.not_computable_reason}"
            )
        if receipt.tail_convention is not None:
            lines.append(f"tail_convention: {receipt.tail_convention}")
        if receipt.rounding_interval is not None and receipt.status in (
                "consistent", "mismatch"):
            lines.append(f"rounding_interval: {receipt.rounding_interval}")
        if receipt.nearest_achievable is not None and receipt.status in (
                "consistent", "mismatch"):
            lines.append(f"nearest_achievable: {receipt.nearest_achievable}")
        if receipt.df_identity is not None:
            lines.append(f"df_identity: {receipt.df_identity}")
        lines.append("")
    while lines and lines[-1] == "":
        lines.pop()
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--extraction", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        text = args.extraction.read_text(encoding="utf-8")
    except OSError as exc:
        print(f"cannot read extraction: {exc}", file=sys.stderr)
        return 2
    try:
        extraction = parse_extraction(text)
        receipts = compute_receipts(extraction)
    except (ExtractionError, ArithmeticError) as exc:
        print(f"extraction rejected: {exc}", file=sys.stderr)
        return 2
    try:
        # Exclusive create: the receipts file is bundle evidence and joins
        # the harness's write-once discipline (security round 1, P3-1).
        # newline="\n" pins the artifact bytes: default newline translation
        # would emit CRLF on Windows and the identity gate compares bytes
        # (codex round 1, P2-5).
        with args.output.open("x", encoding="utf-8",
                              newline="\n") as stream:
            stream.write(receipts)
    except OSError as exc:
        print(f"cannot write receipts: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
