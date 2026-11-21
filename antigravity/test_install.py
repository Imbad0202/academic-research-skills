"""Run: python3 antigravity/test_install.py"""
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import install  # noqa: E402

ROOT = install.ROOT


class InstallTest(unittest.TestCase):
    def test_build(self):
        with tempfile.TemporaryDirectory() as tmp:
            dest = Path(tmp) / "plugin"
            count = install.build(dest)
            skills = sorted(p.name for p in (dest / "skills").iterdir())
            commands = sorted(p.stem for p in (ROOT / "commands").glob("ars-*.md"))
            self.assertEqual(skills, sorted(install.SKILLS + commands))
            self.assertEqual(count, len(skills))
            for name in skills:
                text = (dest / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
                self.assertLess(len(text.encode("utf-8")), 24000, name)
                # the only occurrence left is the compatibility note defining the variable
                self.assertEqual(text.count("${CLAUDE_PLUGIN_ROOT}"), 1, name)
                self.assertNotIn("{root}", text, name)
                self.assertIn("compatibility rules", text, name)
            for name in install.SKILLS:  # trigger text must be the original, byte for byte
                original = (ROOT / name / "SKILL.md").read_text(encoding="utf-8")
                front, _ = install.split_frontmatter(original)
                loader = (dest / "skills" / name / "SKILL.md").read_text(encoding="utf-8")
                self.assertTrue(loader.startswith(front), name)
                self.assertIn(f"{ROOT.as_posix()}/{name}/SKILL.md", loader)

    def test_refuses_foreign_directory_and_replaces_own(self):
        with tempfile.TemporaryDirectory() as home:
            env = dict(os.environ, HOME=home, USERPROFILE=home)
            dest = Path(home) / ".gemini" / "config" / "plugins" / "academic-research-skills"
            dest.mkdir(parents=True)
            (dest / "keep.txt").write_text("user data")
            cmd = [sys.executable, str(Path(install.__file__))]
            self.assertNotEqual(subprocess.run(cmd, env=env, capture_output=True).returncode, 0)
            self.assertTrue((dest / "keep.txt").exists())
            (dest / "keep.txt").unlink()
            dest.rmdir()
            for _ in range(2):  # a second run replaces our own install
                self.assertEqual(subprocess.run(cmd, env=env, capture_output=True).returncode, 0)
            self.assertTrue((dest / "skills" / "ars-full" / "SKILL.md").is_file())


if __name__ == "__main__":
    unittest.main()
