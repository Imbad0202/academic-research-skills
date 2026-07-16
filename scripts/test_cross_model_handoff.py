"""Deterministic owner → dispatcher → owner fixtures for the #527 envelope.

Fake transport only — no external API, no manuscript upload. These fixtures
pin the normative grammar in scripts/cross_model_handoff.py: recognition,
fail-closed validation, blindness, and the complete outcome routing.
"""
import json
import unittest

import cross_model_handoff as cmh


def _envelope(kind: str, expected: str, owner_decision: str | None, payload: str = "RQ Brief...\nBlueprint...", owner: str | None = None) -> str:
    lines = [
        cmh.OPEN_FENCE,
        f"checkpoint_kind: {kind}",
        f"owner_agent: {owner or cmh.EXPECTED_OWNERS.get(kind, 'research_architect_agent')}",
        "correlation_id: design-freeze-demo-001",
        f"expected_result: {expected}",
    ]
    if owner_decision is not None:
        lines.append(f"owner_decision: {owner_decision}")
    lines += ["payload:", payload, cmh.CLOSE_FENCE]
    return "\n".join(lines)


OWNER_SOUND = json.dumps({"decision": "sound", "drivers": ["traces to RQ"], "confidence": "high"})


class ModuleConstantsTests(unittest.TestCase):
    """Literal pins — assertions elsewhere compare against the module's own
    constants, so a mutated constant would otherwise stay green (codex #527
    round-3 P1: self-referential testing)."""

    def test_outcome_literals_are_pinned_and_distinct(self) -> None:
        self.assertEqual(cmh.AGREEMENT_FILL, "agreement_fill_no_reinvoke")
        self.assertEqual(cmh.DIVERGENCE_REINVOKE, "divergence_reinvoke_owner")
        self.assertEqual(cmh.FULL_RETURN_REINVOKE, "full_return_reinvoke_owner")
        self.assertEqual(cmh.UNAVAILABLE, "unavailable")
        self.assertEqual(
            len({cmh.AGREEMENT_FILL, cmh.DIVERGENCE_REINVOKE, cmh.FULL_RETURN_REINVOKE, cmh.UNAVAILABLE}),
            4,
        )

    def test_owner_bindings_are_pinned(self) -> None:
        self.assertEqual(
            cmh.EXPECTED_OWNERS,
            {
                "design_freeze": "research_architect_agent",
                "editorial_decision": "editorial_synthesizer_agent",
                "da_critique": "devils_advocate_reviewer_agent",
            },
        )

    def test_wrong_owner_rejected_for_every_kind(self) -> None:
        cases = {
            "design_freeze": ("enum_comparison", OWNER_SOUND, "editorial_synthesizer_agent"),
            "editorial_decision": (
                "enum_comparison",
                json.dumps({"decision": "accept", "drivers": [], "confidence": "low"}),
                "research_architect_agent",
            ),
            "da_critique": ("full_return", None, "research_architect_agent"),
        }
        for kind, (expected, od, wrong_owner) in cases.items():
            with self.assertRaises(cmh.HandoffError, msg=kind):
                cmh.parse_handoff(_envelope(kind, expected, od, owner=wrong_owner))

    def test_fence_literals_are_pinned(self) -> None:
        self.assertEqual(cmh.OPEN_FENCE, "[CROSS-MODEL-HANDOFF v1]")
        self.assertEqual(cmh.CLOSE_FENCE, "[/CROSS-MODEL-HANDOFF]")

    def test_contract_limits_are_pinned(self) -> None:
        """codex round-4 P1: MAX_DRIVERS / CONFIDENCE_VALUES could expand
        green — pin the literals."""
        self.assertEqual(cmh.MAX_DRIVERS, 3)
        self.assertEqual(cmh.CONFIDENCE_VALUES, ("low", "medium", "high"))

    def test_four_drivers_rejected(self) -> None:
        h = cmh.parse_handoff(_envelope("design_freeze", "enum_comparison", OWNER_SOUND))
        raw = json.dumps({"decision": "sound", "drivers": ["a", "b", "c", "d"], "confidence": "low"})
        r = cmh.route_result(h, transport_ok=True, raw_result=raw)
        self.assertEqual(r.outcome, "unavailable")

    def test_exactly_three_drivers_accepted(self) -> None:
        """codex round-13 P1: the documented maximum (three drivers) is
        VALID — an off-by-one tightening must fail this witness."""
        h = cmh.parse_handoff(_envelope("design_freeze", "enum_comparison", OWNER_SOUND))
        raw = json.dumps({"decision": "sound", "drivers": ["a", "b", "c"], "confidence": "low"})
        r = cmh.route_result(h, transport_ok=True, raw_result=raw)
        self.assertEqual(r.outcome, "agreement_fill_no_reinvoke")

    def test_nan_infinity_rejected_on_both_paths(self) -> None:
        """codex round-13 P1: NaN/Infinity are not standard JSON."""
        bad = '{"decision": "sound", "drivers": ["x"], "confidence": "high", "extra": NaN}'
        h = cmh.parse_handoff(_envelope("design_freeze", "enum_comparison", OWNER_SOUND))
        r = cmh.route_result(h, transport_ok=True, raw_result=bad)
        self.assertEqual(r.outcome, "unavailable")
        with self.assertRaises(cmh.HandoffError):
            cmh.parse_handoff(_envelope("design_freeze", "enum_comparison", bad))

    def test_out_of_contract_confidence_rejected(self) -> None:
        h = cmh.parse_handoff(_envelope("design_freeze", "enum_comparison", OWNER_SOUND))
        raw = json.dumps({"decision": "sound", "drivers": [], "confidence": "unbounded"})
        r = cmh.route_result(h, transport_ok=True, raw_result=raw)
        self.assertEqual(r.outcome, "unavailable")


class ExtractionTests(unittest.TestCase):
    def test_plain_deliverable_has_no_block(self) -> None:
        self.assertIsNone(cmh.extract_handoff_block("## Blueprint\n\nOrdinary deliverable text."))

    def test_block_is_recognized_inside_larger_output(self) -> None:
        text = "preamble\n" + _envelope("design_freeze", "enum_comparison", OWNER_SOUND) + "\ntrailer"
        block = cmh.extract_handoff_block(text)
        self.assertIsNotNone(block)
        self.assertTrue(block.startswith(cmh.OPEN_FENCE) and block.endswith(cmh.CLOSE_FENCE))

    def test_unclosed_fence_is_malformed(self) -> None:
        with self.assertRaises(cmh.HandoffError):
            cmh.extract_handoff_block(cmh.OPEN_FENCE + "\ncheckpoint_kind: design_freeze")

    def test_closing_fence_without_opening_is_malformed(self) -> None:
        """Round-9 probe: an output carrying only a closing fence must raise,
        never pass as an ordinary deliverable."""
        with self.assertRaises(cmh.HandoffError):
            cmh.extract_handoff_block("some text\n" + cmh.CLOSE_FENCE + "\nmore text")

    def test_close_before_open_is_malformed(self) -> None:
        """Round-9 probe: a closing fence ABOVE the opening fence must raise."""
        text = cmh.CLOSE_FENCE + "\n" + cmh.OPEN_FENCE + "\ncheckpoint_kind: design_freeze"
        with self.assertRaises(cmh.HandoffError):
            cmh.extract_handoff_block(text)

    def test_parse_direct_rejects_wrong_first_line(self) -> None:
        """Round-9 probe: parse_handoff called directly (bypassing extract)
        must reject a block whose first line is not the exact v1 fence."""
        block = "preamble\n" + _envelope("design_freeze", "enum_comparison", OWNER_SOUND)
        with self.assertRaises(cmh.HandoffError):
            cmh.parse_handoff(block)

    def test_parse_direct_rejects_missing_last_line_closer(self) -> None:
        block = _envelope("design_freeze", "enum_comparison", OWNER_SOUND) + "\ntrailer"
        with self.assertRaises(cmh.HandoffError):
            cmh.parse_handoff(block)


class ParseTests(unittest.TestCase):
    def test_valid_design_freeze(self) -> None:
        h = cmh.parse_handoff(_envelope("design_freeze", "enum_comparison", OWNER_SOUND))
        self.assertEqual(h.checkpoint_kind, "design_freeze")
        self.assertEqual(h.owner_decision["decision"], "sound")
        self.assertIn("Blueprint", h.payload)

    def test_valid_editorial_decision(self) -> None:
        od = json.dumps({"decision": "minor_revision", "drivers": [], "confidence": "medium"})
        h = cmh.parse_handoff(_envelope("editorial_decision", "enum_comparison", od))
        self.assertEqual(h.decision_enum, ("accept", "minor_revision", "major_revision", "reject"))

    def test_valid_da_critique_needs_no_owner_decision(self) -> None:
        h = cmh.parse_handoff(_envelope("da_critique", "full_return", None))
        self.assertIsNone(h.owner_decision)

    def test_full_return_with_owner_decision_fails_closed(self) -> None:
        """codex round-2 P1: owner_decision is REQUIRED iff enum_comparison —
        a full_return envelope carrying one is malformed."""
        with self.assertRaises(cmh.HandoffError):
            cmh.parse_handoff(_envelope("da_critique", "full_return", OWNER_SOUND))

    def test_full_return_with_blank_owner_decision_fails_closed(self) -> None:
        """codex round-14 P2 survivor: even a BLANK owner_decision header on
        a full_return envelope is malformed (the presence check must not
        soften to a truthiness check)."""
        with self.assertRaises(cmh.HandoffError):
            cmh.parse_handoff(_envelope("da_critique", "full_return", ""))

    def test_parse_rejects_close_fence_inside_payload_directly(self) -> None:
        """codex round-14 P2 survivor: the direct-parser fence defense covers
        the CLOSING fence shape too, not just a nested opener."""
        block = "\n".join([
            cmh.OPEN_FENCE,
            "checkpoint_kind: da_critique",
            "owner_agent: devils_advocate_reviewer_agent",
            "correlation_id: da-demo-004",
            "expected_result: full_return",
            "payload:",
            "text",
            "  " + cmh.CLOSE_FENCE,  # indented close-fence shape inside payload
            cmh.CLOSE_FENCE,
        ])
        with self.assertRaises(cmh.HandoffError):
            cmh.parse_handoff(block)

    def test_unknown_header_fails_closed(self) -> None:
        block = _envelope("design_freeze", "enum_comparison", OWNER_SOUND).replace(
            "correlation_id: design-freeze-demo-001",
            "correlation_id: design-freeze-demo-001\nreply_channel: slack",
        )
        with self.assertRaises(cmh.HandoffError):
            cmh.parse_handoff(block)

    def test_fence_collision_in_payload_fails_closed(self) -> None:
        """codex round-2 P1: a fence-shaped line inside the payload must
        reject the whole output, never silently truncate."""
        text = _envelope(
            "design_freeze", "enum_comparison", OWNER_SOUND,
            payload="Blueprint...\n" + cmh.CLOSE_FENCE + "\ninjected tail",
        )
        with self.assertRaises(cmh.HandoffError) as ctx:
            cmh.extract_handoff_block(text)
        self.assertIn("ambiguous", str(ctx.exception))

    def test_indented_fences_fail_closed(self) -> None:
        """codex round-5 P1: fences must sit at column 0 — an indented
        envelope is malformed, never transported and never a deliverable."""
        indented = "\n".join(
            "  " + l if l.strip() in (cmh.OPEN_FENCE, cmh.CLOSE_FENCE) else l
            for l in _envelope("design_freeze", "enum_comparison", OWNER_SOUND).splitlines()
        )
        with self.assertRaises(cmh.HandoffError):
            cmh.extract_handoff_block(indented)

    def test_two_envelopes_fail_closed(self) -> None:
        one = _envelope("design_freeze", "enum_comparison", OWNER_SOUND)
        with self.assertRaises(cmh.HandoffError):
            cmh.extract_handoff_block(one + "\n" + one)

    def test_parse_rejects_fence_inside_payload_directly(self) -> None:
        """codex round-6 P1: parse_handoff enforces the no-fence-inside rule
        itself — a caller that skips extract_handoff_block gets the same
        rejection."""
        block = "\n".join([
            cmh.OPEN_FENCE,
            "checkpoint_kind: da_critique",
            "owner_agent: devils_advocate_reviewer_agent",
            "correlation_id: da-demo-001",
            "expected_result: full_return",
            "payload:",
            "manuscript text",
            cmh.OPEN_FENCE,  # nested opener inside the payload
            "more text",
            cmh.CLOSE_FENCE,
        ])
        with self.assertRaises(cmh.HandoffError):
            cmh.parse_handoff(block)

    def test_unclosed_v2_opener_still_raises(self) -> None:
        """codex round-6 P1: generous any-version detection is load-bearing —
        an opener-only v2 handoff must raise, never return None (this
        witness fails if detection is narrowed to the exact v1 fence)."""
        text = "[CROSS-MODEL-HANDOFF v2]\ncheckpoint_kind: design_freeze\npayload:\nx"
        with self.assertRaises(cmh.HandoffError):
            cmh.extract_handoff_block(text)

    def test_any_unknown_version_opener_raises_even_unclosed(self) -> None:
        """Property-level (codex round-7 P1): ANY version token — not just
        v2 — must be detected and rejected, even opener-only."""
        for version in ("v2", "v3", "v99", "vNEXT", ""):
            text = f"[CROSS-MODEL-HANDOFF {version}]".replace(" ]", "]") + "\ncheckpoint_kind: design_freeze\npayload:\nx"
            with self.assertRaises(cmh.HandoffError, msg=f"version={version!r}"):
                cmh.extract_handoff_block(text)

    def test_any_cf_prefixed_fence_detected_and_rejected(self) -> None:
        """Property-level (codex round-7 P1): every Unicode Cf format char —
        not just U+200B — folds away in detection, then the raw acceptance
        check rejects the line."""
        for cf in ("​", "⁠", "﻿", "­", "‎"):
            text = cf + _envelope("design_freeze", "enum_comparison", OWNER_SOUND)
            with self.assertRaises(cmh.HandoffError, msg=f"cf=U+{ord(cf):04X}"):
                cmh.extract_handoff_block(text)

    def test_parse_detects_cf_masked_fence_inside_payload(self) -> None:
        block = "\n".join([
            cmh.OPEN_FENCE,
            "checkpoint_kind: da_critique",
            "owner_agent: devils_advocate_reviewer_agent",
            "correlation_id: da-demo-002",
            "expected_result: full_return",
            "payload:",
            "⁠" + cmh.OPEN_FENCE,  # word-joiner-masked nested opener
            cmh.CLOSE_FENCE,
        ])
        with self.assertRaises(cmh.HandoffError):
            cmh.parse_handoff(block)

    def test_zero_width_prefixed_fence_detected_and_rejected(self) -> None:
        """Invisible-character defense (#524 lesson): a U+200B-prefixed fence
        is DETECTED (folded) then REJECTED by raw acceptance — never an
        ordinary deliverable."""
        text = "\u200b" + _envelope("design_freeze", "enum_comparison", OWNER_SOUND)
        with self.assertRaises(cmh.HandoffError):
            cmh.extract_handoff_block(text)

    def test_unknown_kind_fails_closed(self) -> None:
        with self.assertRaises(cmh.HandoffError):
            cmh.parse_handoff(_envelope("integrity_sample", "enum_comparison", OWNER_SOUND))

    def test_kind_result_mismatch_fails_closed(self) -> None:
        with self.assertRaises(cmh.HandoffError):
            cmh.parse_handoff(_envelope("design_freeze", "full_return", OWNER_SOUND))

    def test_missing_owner_decision_fails_closed(self) -> None:
        with self.assertRaises(cmh.HandoffError):
            cmh.parse_handoff(_envelope("design_freeze", "enum_comparison", None))

    def test_owner_decision_outside_enum_fails_closed(self) -> None:
        bad = json.dumps({"decision": "approve", "drivers": []})
        with self.assertRaises(cmh.HandoffError):
            cmh.parse_handoff(_envelope("design_freeze", "enum_comparison", bad))

    def test_missing_payload_fails_closed(self) -> None:
        with self.assertRaises(cmh.HandoffError):
            cmh.parse_handoff(_envelope("design_freeze", "enum_comparison", OWNER_SOUND, payload=" "))

    def test_each_required_header_missing_fails_closed(self) -> None:
        """codex round-11 P1: every required header raises HandoffError when
        missing — independently, so exempting one from the check cannot
        stay green (a missing value must never surface as KeyError)."""
        base = _envelope("design_freeze", "enum_comparison", OWNER_SOUND)
        removable = {
            "checkpoint_kind": "checkpoint_kind: design_freeze",
            "owner_agent": "owner_agent: research_architect_agent",
            "correlation_id": "correlation_id: design-freeze-demo-001",
            "expected_result": "expected_result: enum_comparison",
        }
        for name, line in removable.items():
            mutated = "\n".join(l for l in base.splitlines() if l != line)
            self.assertNotEqual(mutated, base, msg=name)
            with self.assertRaises(cmh.HandoffError, msg=name):
                cmh.parse_handoff(mutated)

    def test_missing_payload_marker_is_handoff_error(self) -> None:
        """codex round-13 P1: an envelope with NO payload: marker at all must
        raise HandoffError, never TypeError."""
        block = "\n".join([
            cmh.OPEN_FENCE,
            "checkpoint_kind: da_critique",
            "owner_agent: devils_advocate_reviewer_agent",
            "correlation_id: da-demo-003",
            "expected_result: full_return",
            cmh.CLOSE_FENCE,
        ])
        with self.assertRaises(cmh.HandoffError):
            cmh.parse_handoff(block)

    def test_invisible_only_correlation_id_is_missing(self) -> None:
        """codex round-13 P1: a zero-width-only correlation_id is not a
        stable token."""
        block = _envelope("design_freeze", "enum_comparison", OWNER_SOUND).replace(
            "correlation_id: design-freeze-demo-001", "correlation_id: ​"
        )
        with self.assertRaises(cmh.HandoffError):
            cmh.parse_handoff(block)

    def test_invisible_only_payload_is_missing(self) -> None:
        """codex round-11 P1: a Cf-only payload is blank — no substance to
        transport."""
        with self.assertRaises(cmh.HandoffError):
            cmh.parse_handoff(
                _envelope("design_freeze", "enum_comparison", OWNER_SOUND, payload="​⁠")
            )

    def test_duplicate_header_fails_closed(self) -> None:
        block = _envelope("design_freeze", "enum_comparison", OWNER_SOUND).replace(
            "owner_agent: research_architect_agent",
            "owner_agent: research_architect_agent\nowner_agent: someone_else",
        )
        with self.assertRaises(cmh.HandoffError):
            cmh.parse_handoff(block)

    def test_unknown_version_fence_fails_closed(self) -> None:
        """codex round-1 P1: a v2 fence must be malformed, never an
        ordinary deliverable."""
        text = _envelope("design_freeze", "enum_comparison", OWNER_SOUND).replace(
            cmh.OPEN_FENCE, "[CROSS-MODEL-HANDOFF v2]"
        )
        with self.assertRaises(cmh.HandoffError):
            cmh.extract_handoff_block(text)

    def test_wrong_owner_for_kind_fails_closed(self) -> None:
        """codex round-1 P1: kind->owner binding — a design_freeze envelope
        claiming the editorial owner must be malformed."""
        with self.assertRaises(cmh.HandoffError):
            cmh.parse_handoff(
                _envelope("design_freeze", "enum_comparison", OWNER_SOUND, owner="editorial_synthesizer_agent")
            )

    def test_invalid_owner_decision_is_envelope_class(self) -> None:
        """codex round-1 P1: owner-side validation errors are
        malformed_handoff, not malformed_result."""
        bad = json.dumps({"decision": "approve", "drivers": [], "confidence": "low"})
        with self.assertRaises(cmh.HandoffError) as ctx:
            cmh.parse_handoff(_envelope("design_freeze", "enum_comparison", bad))
        self.assertIn("malformed_handoff", str(ctx.exception))

    def test_payload_never_contains_owner_decision(self) -> None:
        """Blindness invariant: the parsed payload (the ONLY thing a
        dispatcher forwards) carries no trace of the committed decision."""
        h = cmh.parse_handoff(_envelope("design_freeze", "enum_comparison", OWNER_SOUND))
        self.assertNotIn("sound", h.payload)
        self.assertNotIn("owner_decision", h.payload)


class RoutingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.h = cmh.parse_handoff(_envelope("design_freeze", "enum_comparison", OWNER_SOUND))

    def test_transport_failure_is_unavailable(self) -> None:
        r = cmh.route_result(self.h, transport_ok=False, raw_result=None)
        self.assertEqual(r.outcome, cmh.UNAVAILABLE)
        self.assertEqual(r.error, "transport_failure")

    def test_agreement_fills_without_reinvoking_owner(self) -> None:
        raw = json.dumps({"decision": "sound", "drivers": ["ok"], "confidence": "medium"})
        r = cmh.route_result(self.h, transport_ok=True, raw_result=raw)
        self.assertEqual(r.outcome, cmh.AGREEMENT_FILL)
        self.assertEqual(r.return_context, {})  # nothing goes back to the owner

    def test_divergence_reinvokes_owner_with_minimum_context(self) -> None:
        raw = json.dumps({"decision": "fundamental_concern", "drivers": ["RQ unanswerable"], "confidence": "high"})
        r = cmh.route_result(self.h, transport_ok=True, raw_result=raw)
        self.assertEqual(r.outcome, "divergence_reinvoke_owner")
        # The COMPLETE minimum context, asserted exactly (codex round-5 P1:
        # a truncated cross_model_decision stayed green under partial
        # assertions) — the owner needs the drivers/confidence for the
        # mandated targeted rebuttal.
        self.assertEqual(
            r.return_context,
            {
                "correlation_id": "design-freeze-demo-001",
                "owner_agent": "research_architect_agent",
                "owner_decision": {"decision": "sound", "drivers": ["traces to RQ"], "confidence": "high"},
                "cross_model_decision": {
                    "decision": "fundamental_concern",
                    "drivers": ["RQ unanswerable"],
                    "confidence": "high",
                },
                "original_payload": "RQ Brief...\nBlueprint...",
            },
        )

    def test_ok_transport_with_no_body_is_unavailable(self) -> None:
        """Round-9 probe: transport_ok=True with raw_result=None must still
        be unavailable — the None guard is independently load-bearing."""
        r = cmh.route_result(self.h, transport_ok=True, raw_result=None)
        self.assertEqual(r.outcome, "unavailable")
        self.assertEqual(r.error, "transport_failure")

    def test_blank_full_return_body_is_unavailable(self) -> None:
        """codex round-10 P1: a blank/whitespace DA response is a failed
        transport — never a critique handed back to the owner."""
        h = cmh.parse_handoff(_envelope("da_critique", "full_return", None))
        for body in ("", "   \n\t", "​", "⁠ ​"):
            r = cmh.route_result(h, transport_ok=True, raw_result=body)
            self.assertEqual(r.outcome, "unavailable", msg=repr(body))

    def test_duplicate_json_keys_rejected_on_both_paths(self) -> None:
        """codex round-10 P1: two different decision values in one object is
        ambiguity, not a judgment — rejected on the result path (unavailable)
        and the owner path (malformed_handoff)."""
        dup = '{"decision": "sound", "decision": "fundamental_concern", "drivers": ["x"], "confidence": "high"}'
        r = cmh.route_result(self.h, transport_ok=True, raw_result=dup)
        self.assertEqual(r.outcome, "unavailable")
        self.assertIn("malformed_result", r.error)
        with self.assertRaises(cmh.HandoffError) as ctx:
            cmh.parse_handoff(_envelope("design_freeze", "enum_comparison", dup))
        self.assertIn("malformed_handoff", str(ctx.exception))

    def test_transport_failure_wins_over_residual_body(self) -> None:
        """codex round-5 P1: transport_ok is authoritative — a failed
        transport carrying a valid-looking residual body must still be
        unavailable, never routed."""
        raw = json.dumps({"decision": "sound", "drivers": ["ok"], "confidence": "high"})
        r = cmh.route_result(self.h, transport_ok=False, raw_result=raw)
        self.assertEqual(r.outcome, "unavailable")
        self.assertEqual(r.error, "transport_failure")

    def test_pathologically_nested_result_is_unavailable(self) -> None:
        """codex round-7 P1: a RecursionError from deeply nested JSON must
        fail closed like any other malformed input."""
        nested = "[" * 100000 + "]" * 100000
        r = cmh.route_result(self.h, transport_ok=True, raw_result=nested)
        self.assertEqual(r.outcome, "unavailable")
        self.assertIn("malformed_result", r.error)

    def test_pathologically_nested_owner_decision_is_envelope_error(self) -> None:
        nested = "[" * 100000 + "]" * 100000
        with self.assertRaises(cmh.HandoffError) as ctx:
            cmh.parse_handoff(_envelope("design_freeze", "enum_comparison", nested))
        self.assertIn("malformed_handoff", str(ctx.exception))

    def test_non_string_driver_rejected(self) -> None:
        """codex round-5 P1: adverse witness for the drivers element-type
        rule."""
        raw = json.dumps({"decision": "sound", "drivers": [7], "confidence": "high"})
        r = cmh.route_result(self.h, transport_ok=True, raw_result=raw)
        self.assertEqual(r.outcome, "unavailable")
        self.assertIn("malformed_result", r.error)

    def test_incomplete_result_is_unavailable(self) -> None:
        """codex round-1 P1: the #518 output contract requires all three
        fields — a bare decision must not route to agreement."""
        r = cmh.route_result(self.h, transport_ok=True, raw_result=json.dumps({"decision": "sound"}))
        self.assertEqual(r.outcome, cmh.UNAVAILABLE)
        self.assertIn("malformed_result", r.error)

    def test_each_missing_field_is_unavailable_independently(self) -> None:
        """codex round-8 P1: drivers and confidence are pinned SEPARATELY —
        a default supplied for either single field must not reach
        agreement, on both the result and the owner path."""
        missing_confidence = {"decision": "sound", "drivers": ["ok"]}
        missing_drivers = {"decision": "sound", "confidence": "high"}
        for name, obj in (("confidence", missing_confidence), ("drivers", missing_drivers)):
            r = cmh.route_result(self.h, transport_ok=True, raw_result=json.dumps(obj))
            self.assertEqual(r.outcome, "unavailable", msg=f"result missing {name}")
            with self.assertRaises(cmh.HandoffError, msg=f"owner missing {name}"):
                cmh.parse_handoff(_envelope("design_freeze", "enum_comparison", json.dumps(obj)))

    def test_malformed_result_is_unavailable_not_fabricated(self) -> None:
        r = cmh.route_result(self.h, transport_ok=True, raw_result="I think the design is sound overall.")
        self.assertEqual(r.outcome, cmh.UNAVAILABLE)
        self.assertIn("malformed_result", r.error)

    def test_unknown_result_enum_is_unavailable(self) -> None:
        raw = json.dumps({"decision": "approve_with_comments", "drivers": []})
        r = cmh.route_result(self.h, transport_ok=True, raw_result=raw)
        self.assertEqual(r.outcome, cmh.UNAVAILABLE)
        self.assertIn("malformed_result", r.error)

    def test_da_full_return_body_is_verbatim_not_normalized(self) -> None:
        """codex round-14 P2 survivor: the response goes back to the owner
        VERBATIM — surrounding whitespace included."""
        h = cmh.parse_handoff(_envelope("da_critique", "full_return", None))
        body = "\n  Critique with leading/trailing space  \n"
        r = cmh.route_result(h, transport_ok=True, raw_result=body)
        self.assertEqual(r.return_context["cross_model_response"], body)

    def test_da_full_return_always_returns_to_owner(self) -> None:
        h = cmh.parse_handoff(_envelope("da_critique", "full_return", None))
        r = cmh.route_result(h, transport_ok=True, raw_result="Critique: three CRITICAL issues...")
        self.assertEqual(r.outcome, "full_return_reinvoke_owner")
        # The complete required context: correlation + owner + verbatim
        # response (codex round-4 P1: correlation could disappear green).
        self.assertEqual(
            r.return_context,
            {
                "correlation_id": "design-freeze-demo-001",
                "owner_agent": "devils_advocate_reviewer_agent",
                "cross_model_response": "Critique: three CRITICAL issues...",
            },
        )

    def test_end_to_end_owner_dispatcher_owner(self) -> None:
        """The full deterministic replay: owner emits inside a larger
        deliverable, dispatcher extracts + parses, fake transport diverges,
        routing returns the rebuttal invocation to the same owner."""
        owner_output = "## Blueprint draft\n...\n" + _envelope("design_freeze", "enum_comparison", OWNER_SOUND)
        block = cmh.extract_handoff_block(owner_output)
        handoff = cmh.parse_handoff(block)

        def fake_transport(payload: str) -> str:  # never sees the decision
            assert "sound" not in payload
            return json.dumps({"decision": "revise_before_freeze", "drivers": ["sampling frame unstated"], "confidence": "medium"})

        r = cmh.route_result(handoff, transport_ok=True, raw_result=fake_transport(handoff.payload))
        self.assertEqual(r.outcome, cmh.DIVERGENCE_REINVOKE)
        self.assertEqual(r.return_context["owner_agent"], handoff.owner_agent)


if __name__ == "__main__":
    unittest.main()
