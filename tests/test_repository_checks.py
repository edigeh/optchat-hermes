"""Publication failures must surface without exposing rejected file contents."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class PublicationGuardTests(unittest.TestCase):
    def setUp(self) -> None:
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.repository = Path(temporary.name) / "repository"
        shutil.copytree(
            Path(__file__).resolve().parents[1],
            self.repository,
            ignore=shutil.ignore_patterns(".git", ".venv", "venv", "__pycache__", ".pytest_cache"),
        )

    def run_guard(self) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "scripts/check_repository.py"],
            cwd=self.repository,
            capture_output=True,
            text=True,
            timeout=10,
            check=False,
        )

    def test_rejected_access_value_is_absent_from_cli_output(self) -> None:
        fixture_value = "ghp_" + "synthetic" * 4
        (self.repository / "rejected.txt").write_text(fixture_value, encoding="utf-8")

        result = self.run_guard()

        self.assertEqual(result.returncode, 1)
        self.assertIn("github-token-signature", result.stderr)
        self.assertNotIn(fixture_value, result.stdout + result.stderr)

    def test_private_assignment_prevents_publication_without_printing_it(self) -> None:
        directory = self.repository / "prompts"
        directory.mkdir(exist_ok=True)
        fixture_text = "Privately supplied assignment for a separate agent."
        (directory / "build-optchat-hermes.md").write_text(fixture_text, encoding="utf-8")

        result = self.run_guard()

        self.assertEqual(result.returncode, 1)
        self.assertIn("private implementation assignment", result.stderr)
        self.assertNotIn(fixture_text, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
