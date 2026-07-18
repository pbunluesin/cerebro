from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "skills" / "audit-project" / "scripts" / "audit_project.py"


class AuditProjectTests(unittest.TestCase):
    def test_inventory_reports_sources_and_ignores_generated_directories(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            (target / "AGENTS.md").write_text("# Rules\n", encoding="utf-8")
            (target / "PROJECT_STATE.md").write_text("# State\n", encoding="utf-8")
            (target / "PROCESS.md").write_text("# Legacy\n", encoding="utf-8")
            (target / "docs").mkdir()
            (target / "docs/CONTEXT.md").write_text("# Domain Context\n", encoding="utf-8")
            (target / "node_modules/pkg").mkdir(parents=True)
            (target / "node_modules/pkg/AGENTS.md").write_text("ignored\n", encoding="utf-8")
            (target / "build").mkdir()
            (target / "build/PROCESS.md").write_text("ignored\n", encoding="utf-8")

            result = subprocess.run(
                [sys.executable, str(AUDIT), "--target", str(target), "--json"],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertEqual(report["file_count"], 4)
            self.assertEqual(
                report["canonical_docs_present"],
                ["AGENTS.md", "PROJECT_STATE.md", "docs/CONTEXT.md"],
            )
            self.assertEqual(report["process_candidates"], ["PROCESS.md"])
            self.assertEqual(report["domain_context_documents"], ["docs/CONTEXT.md"])


if __name__ == "__main__":
    unittest.main()
