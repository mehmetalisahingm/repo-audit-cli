from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

if str(SRC) not in sys.path:
    sys.path.insert(0, str(SRC))

from repo_audit.analyzer import audit_repository
from repo_audit.reporting import render_report


class AuditRepositoryTests(unittest.TestCase):
    def test_full_score_repository(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._create_full_repo(root)

            report = audit_repository(root)

            self.assertEqual(report.total_score, 100)
            self.assertEqual(report.grade, "A")
            self.assertFalse(report.recommendations)

    def test_partial_repository_generates_recommendations(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / ".git").mkdir()
            (root / "README.md").write_text("# Demo\n", encoding="utf-8")

            report = audit_repository(root)

            self.assertEqual(report.total_score, 18)
            self.assertEqual(report.grade, "E")
            self.assertTrue(report.recommendations)
            self.assertIn("Add an open-source license file.", report.recommendations)

    def test_json_render_contains_expected_fields(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._create_full_repo(root)

            rendered = render_report(audit_repository(root), "json")
            payload = json.loads(rendered)

            self.assertEqual(payload["total_score"], 100)
            self.assertEqual(payload["grade"], "A")
            self.assertEqual(len(payload["checks"]), 8)

    def _create_full_repo(self, root: Path) -> None:
        (root / ".git").mkdir()
        (root / ".github" / "workflows").mkdir(parents=True)
        (root / "tests").mkdir()
        (root / "tests" / "test_sample.py").write_text("def test_placeholder():\n    assert True\n", encoding="utf-8")
        (root / ".github" / "workflows" / "ci.yml").write_text("name: CI\n", encoding="utf-8")
        (root / ".gitignore").write_text("__pycache__/\n", encoding="utf-8")
        (root / "pyproject.toml").write_text("[project]\nname='demo'\n", encoding="utf-8")
        (root / "LICENSE").write_text("MIT\n", encoding="utf-8")
        (root / "CONTRIBUTING.md").write_text("Contributing\n", encoding="utf-8")
        (root / "CODE_OF_CONDUCT.md").write_text("Respect people.\n", encoding="utf-8")
        (root / "SECURITY.md").write_text("Report issues privately.\n", encoding="utf-8")
        (root / "README.md").write_text(
            "# Demo\n\n## Installation\nDo this.\n\n## Usage\nUse it.\n",
            encoding="utf-8",
        )


if __name__ == "__main__":
    unittest.main()
