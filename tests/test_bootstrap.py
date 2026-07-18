from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP = ROOT / "skills" / "create-project" / "scripts" / "bootstrap_project.py"
VALIDATE = ROOT / "skills" / "create-project" / "scripts" / "validate_project.py"


class BootstrapProjectTests(unittest.TestCase):
    def run_tool(self, script: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(script), *arguments],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_dry_run_does_not_create_target(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "new-project"
            result = self.run_tool(
                BOOTSTRAP,
                "--target", str(target),
                "--name", "New Project",
                "--profile", "minimal",
                "--agents", "both",
                "--dry-run",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(target.exists())
            self.assertIn("CREATE   AGENTS.md", result.stdout)

    def test_minimal_both_creates_shared_and_claude_guidance(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "minimal"
            result = self.run_tool(
                BOOTSTRAP,
                "--target", str(target),
                "--name", "Minimal App",
                "--profile", "minimal",
                "--agents", "both",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((target / "AGENTS.md").is_file())
            self.assertTrue((target / "CLAUDE.md").is_file())
            self.assertTrue((target / ".claude/rules/guardrails.md").is_file())
            self.assertFalse((target / ".claude/agents").exists())
            self.assertFalse((target / ".claude/rules/docs-routing.md").exists())
            self.assertFalse((target / "PROCESS.md").exists())
            self.assertFalse((target / "docs/DATA.md").exists())

            agents_text = (target / "AGENTS.md").read_text(encoding="utf-8")
            for marker in (
                "NO MAGIC",
                "VERIFY BEFORE DONE",
                "DISSENT",
                "SCOPE DRIFT DETECTION",
                "WORKSPACE BOUNDARY",
                "Claude Code",
                "Codex",
            ):
                self.assertIn(marker, agents_text)
            claude_text = (target / "CLAUDE.md").read_text(encoding="utf-8")
            self.assertIn("independent Codex CLI review", claude_text)

            validation = self.run_tool(
                VALIDATE,
                "--target", str(target),
                "--profile", "minimal",
                "--agents", "both",
                "--allow-draft",
            )
            self.assertEqual(validation.returncode, 0, validation.stderr)

    def test_standard_codex_adds_selected_features_only(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "standard"
            result = self.run_tool(
                BOOTSTRAP,
                "--target", str(target),
                "--name", "Service",
                "--profile", "standard",
                "--agents", "codex",
                "--features", "api,data",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((target / "docs/API.md").is_file())
            self.assertTrue((target / "docs/DATA.md").is_file())
            self.assertFalse((target / "CLAUDE.md").exists())
            self.assertFalse((target / ".claude").exists())
            context = (target / "docs/CONTEXT.md").read_text(encoding="utf-8")
            self.assertIn("canonical domain term", context)
            self.assertIn("CONTEXT_MAP.md", context)
            architecture = (target / "docs/ARCHITECTURE.md").read_text(encoding="utf-8")
            self.assertIn("Modules, interfaces, and responsibilities", architecture)
            self.assertIn("Seam/adapter rationale", architecture)
            decision = (target / "docs/decisions/0000-template.md").read_text(encoding="utf-8")
            self.assertIn("Decision and rationale", decision)
            self.assertIn("genuine alternatives existed", decision)

    def test_critical_profile_has_release_and_threat_controls(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "critical"
            result = self.run_tool(
                BOOTSTRAP,
                "--target", str(target),
                "--name", "Critical System",
                "--profile", "critical",
                "--agents", "both",
                "--features", "api,migration",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((target / "docs/DATA.md").is_file())
            self.assertTrue((target / "docs/MIGRATION.md").is_file())
            self.assertTrue((target / "docs/quality/THREAT_MODEL.md").is_file())
            self.assertTrue((target / "docs/quality/RELEASE_CHECKLIST.md").is_file())
            self.assertTrue((target / ".claude/agents/cerebro-reviewer.md").is_file())
            self.assertTrue((target / ".claude/agents/cerebro-fixer.md").is_file())
            review_contract = (target / "docs/quality/REVIEW_CONTRACT.md").read_text(encoding="utf-8")
            self.assertIn("latest currently approved Codex model", review_contract)
            self.assertIn("No silent fallback", review_contract)

    def test_conflict_requires_merge_or_force(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "existing"
            target.mkdir()
            original = "existing readme\n"
            (target / "README.md").write_text(original, encoding="utf-8")
            result = self.run_tool(
                BOOTSTRAP,
                "--target", str(target),
                "--name", "Existing",
                "--profile", "minimal",
                "--agents", "codex",
            )
            self.assertEqual(result.returncode, 3)
            self.assertEqual((target / "README.md").read_text(encoding="utf-8"), original)

            merged = self.run_tool(
                BOOTSTRAP,
                "--target", str(target),
                "--name", "Existing",
                "--profile", "minimal",
                "--agents", "codex",
                "--merge",
            )
            self.assertEqual(merged.returncode, 0, merged.stderr)
            self.assertEqual((target / "README.md").read_text(encoding="utf-8"), original)
            self.assertTrue((target / "AGENTS.md").is_file())

    def test_final_validation_rejects_unresolved_template_content(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "draft"
            created = self.run_tool(
                BOOTSTRAP,
                "--target", str(target),
                "--name", "Draft",
                "--profile", "minimal",
                "--agents", "codex",
            )
            self.assertEqual(created.returncode, 0, created.stderr)
            validation = self.run_tool(
                VALIDATE,
                "--target", str(target),
                "--profile", "minimal",
                "--agents", "codex",
            )
            self.assertNotEqual(validation.returncode, 0)
            self.assertIn("does not declare IMPLEMENTATION_READY", validation.stderr)


if __name__ == "__main__":
    unittest.main()
