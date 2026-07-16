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

    def test_two_envelopes_fail_closed(self) -> None:
        one = _envelope("design_freeze", "enum_comparison", OWNER_SOUND)
        with self.assertRaises(cmh.HandoffError):
            cmh.extract_handoff_block(one + "\n" + one)

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
        self.assertEqual(r.outcome, cmh.DIVERGENCE_REINVOKE)
        ctx = r.return_context
        self.assertEqual(ctx["correlation_id"], "design-freeze-demo-001")
        self.assertEqual(ctx["owner_agent"], "research_architect_agent")
        self.assertEqual(ctx["owner_decision"]["decision"], "sound")
        self.assertEqual(ctx["cross_model_decision"]["decision"], "fundamental_concern")
        self.assertIn("Blueprint", ctx["original_payload"])

    def test_incomplete_result_is_unavailable(self) -> None:
        """codex round-1 P1: the #518 output contract requires all three
        fields — a bare decision must not route to agreement."""
        r = cmh.route_result(self.h, transport_ok=True, raw_result=json.dumps({"decision": "sound"}))
        self.assertEqual(r.outcome, cmh.UNAVAILABLE)
        self.assertIn("malformed_result", r.error)

    def test_malformed_result_is_unavailable_not_fabricated(self) -> None:
        r = cmh.route_result(self.h, transport_ok=True, raw_result="I think the design is sound overall.")
        self.assertEqual(r.outcome, cmh.UNAVAILABLE)
        self.assertIn("malformed_result", r.error)

    def test_unknown_result_enum_is_unavailable(self) -> None:
        raw = json.dumps({"decision": "approve_with_comments", "drivers": []})
        r = cmh.route_result(self.h, transport_ok=True, raw_result=raw)
        self.assertEqual(r.outcome, cmh.UNAVAILABLE)
        self.assertIn("malformed_result", r.error)

    def test_da_full_return_always_returns_to_owner(self) -> None:
        h = cmh.parse_handoff(_envelope("da_critique", "full_return", None))
        r = cmh.route_result(h, transport_ok=True, raw_result="Critique: three CRITICAL issues...")
        self.assertEqual(r.outcome, cmh.FULL_RETURN_REINVOKE)
        self.assertEqual(r.return_context["cross_model_response"], "Critique: three CRITICAL issues...")

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
