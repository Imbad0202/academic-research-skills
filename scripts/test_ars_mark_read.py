"""Unit tests for scripts/ars_mark_read.py.

Per v3.6.8 spec §3.6 + Step 7 (round-2 R2-002, round-5 R5-003 amends).
Covers:
- 4 fail-fast modes (no active passport / passport not found / parent unreadable / read-log unwritable)
- First-time write (creates file with YAML schema header)
- Citation-key validation against active literature_corpus[]
- Batch form (space-separated keys)
- Append-only write (existing entries preserved)
- /ars-unmark-read writes rescinded_at (never deletes)
- Idempotency on re-mark of same key (append, not in-place)
"""
from __future__ import annotations

import os
import stat
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import yaml

from tests.test_helpers import run_script


SCRIPT = Path(__file__).parent / "ars_mark_read.py"


# Minimal Material Passport carrying a literature_corpus[] with 2 entries.
# Passport is YAML per adapter contract (folder_scan / zotero / obsidian all
# emit YAML); only the literature_corpus[] field is consulted by
# ars_mark_read for citation_key validation.
def _write_passport(path: Path, *, citation_keys: list[str]) -> None:
    payload = {
        "literature_corpus": [
            {"citation_key": k, "year": 2024, "title": f"Title {k}"}
            for k in citation_keys
        ],
    }
    with path.open("w", encoding="utf-8") as f:
        yaml.safe_dump(payload, f, sort_keys=False, allow_unicode=True)


def _read_log(passport_path: Path) -> dict:
    log_path = passport_path.parent / f"{passport_path.stem}_human_read_log.yaml"
    with log_path.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


class TestMarkReadHappyPath(unittest.TestCase):
    def test_first_time_write_creates_file_with_schema_header(self) -> None:
        """Spec §3.6 R5-003: first-time write creates the file with the YAML
        schema header before appending. Not a fail-fast mode."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            passport = root / "passport_abc123.json"
            _write_passport(passport, citation_keys=["smith2024"])

            result = run_script(SCRIPT, "smith2024", "--passport-path", str(passport))

            self.assertEqual(result.returncode, 0, msg=f"stderr: {result.stderr}")
            log_data = _read_log(passport)
            self.assertIn("session_id", log_data)
            self.assertIn("created_at", log_data)
            self.assertEqual(len(log_data["human_read"]), 1)
            self.assertEqual(log_data["human_read"][0]["citation_key"], "smith2024")
            self.assertIn("marked_at", log_data["human_read"][0])

    def test_batch_form_appends_multiple_entries(self) -> None:
        """Spec §3.6: /ars-mark-read accepts space-separated keys (batch form).
        Each key produces one entry."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            passport = root / "passport_abc123.json"
            _write_passport(passport, citation_keys=["smith2024", "jones2023"])

            result = run_script(
                SCRIPT, "smith2024", "jones2023", "--passport-path", str(passport)
            )

            self.assertEqual(result.returncode, 0, msg=f"stderr: {result.stderr}")
            log_data = _read_log(passport)
            keys = [e["citation_key"] for e in log_data["human_read"]]
            self.assertEqual(keys, ["smith2024", "jones2023"])

    def test_append_only_preserves_existing_entries(self) -> None:
        """Spec §3.6 firm rule 3: log is append-only. New marks do not
        rewrite or replace prior entries."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            passport = root / "passport_abc123.json"
            _write_passport(passport, citation_keys=["smith2024", "jones2023"])

            # First mark
            run_script(SCRIPT, "smith2024", "--passport-path", str(passport))
            # Second mark, different key
            result = run_script(
                SCRIPT, "jones2023", "--passport-path", str(passport)
            )

            self.assertEqual(result.returncode, 0, msg=f"stderr: {result.stderr}")
            log_data = _read_log(passport)
            keys = [e["citation_key"] for e in log_data["human_read"]]
            self.assertEqual(keys, ["smith2024", "jones2023"])


class TestMarkReadFailFast(unittest.TestCase):
    """4 fail-fast modes per spec §3.6 R5-003 amend."""

    def test_no_active_passport_fails(self) -> None:
        """Fail-fast mode 1: --passport-path omitted and no ambient
        passport discoverable. Emit canonical error, exit non-zero."""
        with TemporaryDirectory() as tmp:
            result = run_script(SCRIPT, "smith2024", cwd=Path(tmp))

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("[ARS-MARK-READ ERROR:", result.stderr + result.stdout)
            self.assertIn("no active passport path", result.stderr + result.stdout)

    def test_passport_not_found_fails(self) -> None:
        """Fail-fast mode 2: --passport-path points to non-existent file."""
        with TemporaryDirectory() as tmp:
            phantom = Path(tmp) / "does_not_exist.json"

            result = run_script(
                SCRIPT, "smith2024", "--passport-path", str(phantom)
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn("[ARS-MARK-READ ERROR:", result.stderr + result.stdout)
            self.assertIn("passport file not found", result.stderr + result.stdout)

    def test_passport_parent_unreadable_fails(self) -> None:
        """Fail-fast mode 3: passport parent directory lacks R_OK."""
        if os.geteuid() == 0:
            self.skipTest("root bypasses POSIX permissions")
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            locked = root / "locked"
            locked.mkdir()
            passport = locked / "passport.json"
            _write_passport(passport, citation_keys=["smith2024"])
            # Strip read permission from the parent dir.
            os.chmod(locked, 0o000)
            try:
                result = run_script(
                    SCRIPT, "smith2024", "--passport-path", str(passport)
                )

                self.assertNotEqual(result.returncode, 0)
                self.assertIn(
                    "[ARS-MARK-READ ERROR:", result.stderr + result.stdout
                )
                self.assertIn(
                    "unreadable", result.stderr + result.stdout
                )
            finally:
                # Restore permissions so TemporaryDirectory cleanup works.
                os.chmod(locked, 0o700)

    def test_readlog_unwritable_fails(self) -> None:
        """Fail-fast mode 4: read-log parent (== passport parent) lacks W_OK.
        Spec §3.6 R5-003: refuse to write when target is unwritable."""
        if os.geteuid() == 0:
            self.skipTest("root bypasses POSIX permissions")
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            passport = root / "passport.json"
            _write_passport(passport, citation_keys=["smith2024"])
            # Read-only parent: can stat the passport but cannot create the
            # sibling read-log file.
            os.chmod(root, 0o500)
            try:
                result = run_script(
                    SCRIPT, "smith2024", "--passport-path", str(passport)
                )

                self.assertNotEqual(result.returncode, 0)
                self.assertIn(
                    "[ARS-MARK-READ ERROR:", result.stderr + result.stdout
                )
                self.assertIn("unwritable", result.stderr + result.stdout)
            finally:
                os.chmod(root, 0o700)


class TestMarkReadCitationKeyValidation(unittest.TestCase):
    def test_invalid_citation_key_hard_errors(self) -> None:
        """Spec §3.6 firm rule 2: invalid <citation_key> is a hard error,
        not a silent miss. Canonical message includes the slug."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            passport = root / "passport.json"
            _write_passport(passport, citation_keys=["smith2024"])

            result = run_script(
                SCRIPT, "bogus_key", "--passport-path", str(passport)
            )

            self.assertNotEqual(result.returncode, 0)
            combined = result.stderr + result.stdout
            self.assertIn("[ARS-MARK-READ ERROR:", combined)
            self.assertIn("'bogus_key'", combined)
            self.assertIn("not in literature_corpus[]", combined)
            # Spec firm rule 2: refuse to write. No read-log file should be
            # created from an invalid attempt.
            log_path = passport.parent / "passport_human_read_log.yaml"
            self.assertFalse(
                log_path.exists(),
                msg="invalid key must not create the read-log file",
            )

    def test_batch_with_one_invalid_key_rejects_whole_batch(self) -> None:
        """Spec firm rule 2 (refuse to write) applied to batch: if any key
        in the batch is invalid, the whole batch is rejected. No partial
        writes. This preserves the all-or-nothing semantic that audit
        replay relies on."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            passport = root / "passport.json"
            _write_passport(passport, citation_keys=["smith2024"])

            result = run_script(
                SCRIPT,
                "smith2024",
                "bogus_key",
                "--passport-path",
                str(passport),
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "[ARS-MARK-READ ERROR:", result.stderr + result.stdout
            )
            log_path = passport.parent / "passport_human_read_log.yaml"
            self.assertFalse(
                log_path.exists(),
                msg="partial batch write must not occur on any invalid key",
            )


class TestUnmarkRead(unittest.TestCase):
    def test_unmark_writes_rescinded_at(self) -> None:
        """Spec §3.6 firm rule 3 + Step 7: /ars-unmark-read writes
        rescinded_at to the matching entry, never deletes."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            passport = root / "passport.json"
            _write_passport(passport, citation_keys=["smith2024"])
            run_script(SCRIPT, "smith2024", "--passport-path", str(passport))

            result = run_script(
                SCRIPT, "smith2024", "--passport-path", str(passport), "--unmark"
            )

            self.assertEqual(result.returncode, 0, msg=f"stderr: {result.stderr}")
            log_data = _read_log(passport)
            # Original entry preserved (not deleted).
            self.assertEqual(len(log_data["human_read"]), 1)
            entry = log_data["human_read"][0]
            self.assertEqual(entry["citation_key"], "smith2024")
            self.assertIn("marked_at", entry)
            self.assertIn("rescinded_at", entry)

    def test_unmark_unknown_key_hard_errors(self) -> None:
        """/ars-unmark-read for a citation_key that was never marked is
        a hard error. Audit-replay requires the rescind target exist."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            passport = root / "passport.json"
            _write_passport(passport, citation_keys=["smith2024", "jones2023"])
            run_script(SCRIPT, "smith2024", "--passport-path", str(passport))

            result = run_script(
                SCRIPT, "jones2023", "--passport-path", str(passport), "--unmark"
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "[ARS-MARK-READ ERROR:", result.stderr + result.stdout
            )


class TestMarkReadYAMLPassport(unittest.TestCase):
    """Issue #195: real adapter output is YAML, not JSON. Earlier fixtures
    wrote JSON which was a parser-coincidence pass (YAML is a JSON superset).
    These tests pin the real adapter-format expectation with .yaml extension
    + canonical YAML serializer output."""

    def test_yaml_passport_happy_path(self) -> None:
        """A passport written by any adapter (folder_scan / zotero / obsidian)
        is YAML. /ars-mark-read must read it without crashing."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            passport = root / "passport.yaml"
            _write_passport(passport, citation_keys=["smith2024"])

            result = run_script(
                SCRIPT, "smith2024", "--passport-path", str(passport)
            )

            self.assertEqual(result.returncode, 0, msg=f"stderr: {result.stderr}")
            log_data = _read_log(passport)
            self.assertEqual(len(log_data["human_read"]), 1)
            self.assertEqual(
                log_data["human_read"][0]["citation_key"], "smith2024"
            )

    def test_yaml_passport_invalid_citation_key_hard_errors(self) -> None:
        """Citation-key validation works the same against a YAML passport."""
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            passport = root / "passport.yaml"
            _write_passport(passport, citation_keys=["smith2024"])

            result = run_script(
                SCRIPT, "nobody2099", "--passport-path", str(passport)
            )

            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "not in literature_corpus[]", result.stderr + result.stdout
            )


class TestReadLogUnwritableExistingFile(unittest.TestCase):
    """Issue #195 companion P2: parent W_OK check passes but the log file
    itself is unwritable. Must surface canonical fail-fast, not bare
    PermissionError."""

    def test_existing_unwritable_log_file_fails_fast(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            passport = root / "passport.yaml"
            _write_passport(passport, citation_keys=["smith2024"])
            log_path = root / f"{passport.stem}_human_read_log.yaml"
            log_path.write_text("human_read: []\n", encoding="utf-8")
            # Read-only on the existing log file. Parent dir stays writable.
            log_path.chmod(stat.S_IRUSR)
            try:
                result = run_script(
                    SCRIPT, "smith2024", "--passport-path", str(passport)
                )
                self.assertNotEqual(
                    result.returncode, 0, msg="should fail-fast not succeed"
                )
                combined = result.stderr + result.stdout
                self.assertIn("[ARS-MARK-READ ERROR:", combined)
                # Bare Python traceback is the failure mode we are guarding
                # against. Spec §3.6 firm rule 4 wants a canonical surface.
                self.assertNotIn("Traceback (most recent call last)", combined)
            finally:
                log_path.chmod(stat.S_IRUSR | stat.S_IWUSR)




class TestReadScopeAttestation(unittest.TestCase):
    """#513: optional read_scope attestation on ledger marks — declaration-only,
    all-or-nothing batch validation, byte-shape backward compat when absent."""

    def _mark(self, tmp, *extra, keys=("smith2024",)):
        root = Path(tmp)
        passport = root / "p.yaml"
        _write_passport(passport, citation_keys=["smith2024", "lee2023"])
        result = run_script(SCRIPT, *keys, "--passport-path", str(passport), *extra)
        return passport, result

    def test_scope_less_mark_writes_no_read_scope_key(self):
        with TemporaryDirectory() as tmp:
            passport, result = self._mark(tmp)
            self.assertEqual(result.returncode, 0, result.stderr)
            (entry,) = _read_log(passport)["human_read"]
            self.assertNotIn("read_scope", entry)

    def test_each_level_persisted(self):
        for level in ("full_text", "abstract_only", "toc_only", "unknown"):
            with self.subTest(level=level), TemporaryDirectory() as tmp:
                passport, result = self._mark(tmp, "--scope", level)
                self.assertEqual(result.returncode, 0, result.stderr)
                (entry,) = _read_log(passport)["human_read"]
                self.assertEqual(entry["read_scope"], {"level": level})

    def test_sections_with_locators_and_note(self):
        with TemporaryDirectory() as tmp:
            passport, result = self._mark(
                tmp, "--scope", "sections", "--locator", "pp. 10-24",
                "--locator", "section 3", "--note", "methods read closely",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            (entry,) = _read_log(passport)["human_read"]
            self.assertEqual(
                entry["read_scope"],
                {"level": "sections", "locators": ["pp. 10-24", "section 3"],
                 "note": "methods read closely"},
            )

    def test_batch_applies_same_scope_to_every_key(self):
        with TemporaryDirectory() as tmp:
            passport, result = self._mark(
                tmp, "--scope", "full_text", keys=("smith2024", "lee2023"),
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            entries = _read_log(passport)["human_read"]
            self.assertEqual(len(entries), 2)
            for entry in entries:
                self.assertEqual(entry["read_scope"], {"level": "full_text"})

    def test_invalid_level_rejected_no_write(self):
        with TemporaryDirectory() as tmp:
            passport, result = self._mark(tmp, "--scope", "skimmed")
            self.assertNotEqual(result.returncode, 0)
            log_path = passport.parent / f"{passport.stem}_human_read_log.yaml"
            self.assertFalse(log_path.exists(), "invalid attestation must not write")

    def test_locator_requires_sections_level(self):
        for level in ("full_text", "abstract_only", "toc_only", "unknown"):
            with self.subTest(level=level), TemporaryDirectory() as tmp:
                passport, result = self._mark(
                    tmp, "--scope", level, "--locator", "pp. 1-2",
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("[ARS-MARK-READ ERROR:", result.stderr)
                log_path = passport.parent / f"{passport.stem}_human_read_log.yaml"
                self.assertFalse(log_path.exists())

    def test_locator_or_note_without_scope_rejected(self):
        for extra in (("--locator", "pp. 1-2"), ("--note", "read it")):
            with self.subTest(extra=extra), TemporaryDirectory() as tmp:
                passport, result = self._mark(tmp, *extra)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("[ARS-MARK-READ ERROR:", result.stderr)

    def test_attestation_args_rejected_with_unmark(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            passport = root / "p.yaml"
            _write_passport(passport, citation_keys=["smith2024"])
            run_script(SCRIPT, "smith2024", "--passport-path", str(passport))
            result = run_script(
                SCRIPT, "smith2024", "--passport-path", str(passport),
                "--unmark", "--scope", "full_text",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("[ARS-MARK-READ ERROR:", result.stderr)
            (entry,) = _read_log(passport)["human_read"]
            self.assertNotIn("rescinded_at", entry, "rejected unmark must not write")

    def test_legacy_entries_untouched_by_new_scoped_mark(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            passport = root / "p.yaml"
            _write_passport(passport, citation_keys=["smith2024", "lee2023"])
            run_script(SCRIPT, "smith2024", "--passport-path", str(passport))
            result = run_script(
                SCRIPT, "lee2023", "--passport-path", str(passport),
                "--scope", "abstract_only",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            first, second = _read_log(passport)["human_read"]
            self.assertNotIn("read_scope", first)
            self.assertEqual(second["read_scope"], {"level": "abstract_only"})

    def test_empty_string_note_is_present_not_absent(self):
        # codex #513 r1: --note "" is an explicitly supplied attestation arg;
        # truthiness checks would let it bypass the requires-scope rule.
        with TemporaryDirectory() as tmp:
            passport, result = self._mark(tmp, "--note", "")
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("[ARS-MARK-READ ERROR:", result.stderr)

    def test_empty_note_with_unmark_rejected(self):
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            passport = root / "p.yaml"
            _write_passport(passport, citation_keys=["smith2024"])
            run_script(SCRIPT, "smith2024", "--passport-path", str(passport))
            result = run_script(
                SCRIPT, "smith2024", "--passport-path", str(passport),
                "--unmark", "--note", "",
            )
            self.assertNotEqual(result.returncode, 0)
            (entry,) = _read_log(passport)["human_read"]
            self.assertNotIn("rescinded_at", entry)

    def test_schema_bounds_enforced_at_write_time(self):
        # codex #513 r1: the CLI must never produce a ledger the sidecar schema
        # rejects — empty and oversize locator/note values are refused.
        cases = [
            ("--scope", "sections", "--locator", ""),
            ("--scope", "sections", "--locator", "x" * 201),
            ("--scope", "full_text", "--note", "x" * 1001),
        ]
        for extra in cases:
            with self.subTest(extra=extra[-1][:10] or "(empty)"), TemporaryDirectory() as tmp:
                passport, result = self._mark(tmp, *extra)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("[ARS-MARK-READ ERROR:", result.stderr)
                log_path = passport.parent / f"{passport.stem}_human_read_log.yaml"
                self.assertFalse(log_path.exists())

    def test_max_length_boundary_values_accepted(self):
        with TemporaryDirectory() as tmp:
            passport, result = self._mark(
                tmp, "--scope", "sections",
                "--locator", "x" * 200, "--note", "y" * 1000,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            (entry,) = _read_log(passport)["human_read"]
            self.assertEqual(len(entry["read_scope"]["locators"][0]), 200)
            self.assertEqual(len(entry["read_scope"]["note"]), 1000)

    def test_schema_rejects_locators_on_non_sections_level(self):
        # codex #513 r2: the sidecar schema mirrors the CLI's locators-require-
        # sections rule so audit-time validation matches the writer contract.
        import json

        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema not installed")
        schema_path = (
            Path(SCRIPT).resolve().parent.parent
            / "shared" / "contracts" / "passport" / "human_read_log.schema.json"
        )
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        bad = {
            "session_id": "s", "created_at": "2026-07-20T00:00:00Z",
            "human_read": [{
                "citation_key": "smith2024", "marked_at": "2026-07-20T00:00:00Z",
                "read_scope": {"level": "full_text", "locators": ["pp. 1-2"]},
            }],
        }
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(bad, schema)
        bad["human_read"][0]["read_scope"] = {"level": "sections", "locators": ["pp. 1-2"]}
        jsonschema.validate(bad, schema)  # sections+locators stays valid

    def test_ledger_validates_against_sidecar_schema(self):
        import json

        try:
            import jsonschema
        except ImportError:
            self.skipTest("jsonschema not installed")
        schema_path = (
            Path(SCRIPT).resolve().parent.parent
            / "shared" / "contracts" / "passport" / "human_read_log.schema.json"
        )
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        with TemporaryDirectory() as tmp:
            passport, result = self._mark(
                tmp, "--scope", "sections", "--locator", "pp. 1-9",
                "--note", "intro only",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            run_script(SCRIPT, "smith2024", "--passport-path", str(passport), "--unmark")
            jsonschema.validate(_read_log(passport), schema)

if __name__ == "__main__":
    unittest.main()
