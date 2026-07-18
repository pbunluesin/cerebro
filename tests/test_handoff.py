from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
COLLECT = ROOT / "skills" / "handoff" / "scripts" / "collect_context.py"
HANDOFF = ROOT / "skills" / "handoff" / "SKILL.md"
CONTRACT = ROOT / "skills" / "handoff" / "references" / "handoff-contract.md"
METADATA = ROOT / "skills" / "handoff" / "agents" / "openai.yaml"
STATE_TEMPLATE = ROOT / "skills" / "create-project" / "assets" / "project" / "PROJECT_STATE.md.tmpl"


class HandoffTests(unittest.TestCase):
    def run_tool(self, target: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(COLLECT), "--target", str(target)],
            text=True,
            capture_output=True,
            check=False,
        )

    def git(self, root: Path, *arguments: str) -> None:
        result = subprocess.run(
            ["git", "-C", str(root), *arguments],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_handoff_requires_explicit_invocation_and_single_state_owner(self) -> None:
        skill = HANDOFF.read_text(encoding="utf-8")
        metadata = METADATA.read_text(encoding="utf-8")
        self.assertIn("Invoke this skill explicitly", skill)
        self.assertIn("PROJECT_STATE.md", skill)
        self.assertIn("Do not create a second same-project handoff file", skill)
        self.assertIn("allow_implicit_invocation: false", metadata)

    def test_contract_preserves_operational_context_and_safe_delivery(self) -> None:
        contract = CONTRACT.read_text(encoding="utf-8")
        state = STATE_TEMPLATE.read_text(encoding="utf-8")
        for marker in (
            "Do not retry",
            "Runtime/environment state",
            "Known gotchas",
            "Next invocation",
            ".cerebro/inbox/",
            "explicit approval for the exact target root",
            "SQL Server stored procedure",
            "parameter name, order, SQL type",
        ):
            self.assertIn(marker, contract)
        for marker in (
            "Exact stopping point",
            "Verified evidence",
            "Relevant contracts",
            "Do not retry",
            "Runtime/environment state",
            "Known gotchas",
            "Next invocation",
            "Next command",
        ):
            self.assertIn(marker, state)

    def test_collector_reports_non_git_directory_without_guessing(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result = self.run_tool(Path(temporary))
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertFalse(report["git_repository"])
            self.assertEqual(report["reason"], "not a Git worktree")

    def test_collector_separates_staged_unstaged_and_untracked_state(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary) / "repo"
            root.mkdir()
            self.git(root, "init", "-b", "main")
            self.git(root, "config", "user.name", "Cerebro Test")
            self.git(root, "config", "user.email", "cerebro@example.invalid")
            (root / "tracked.txt").write_text("one\n", encoding="utf-8")
            self.git(root, "add", "tracked.txt")
            self.git(root, "commit", "-m", "Initial")

            (root / "tracked.txt").write_text("two\n", encoding="utf-8")
            (root / "staged.txt").write_text("staged\n", encoding="utf-8")
            (root / "untracked.txt").write_text("untracked\n", encoding="utf-8")
            self.git(root, "add", "staged.txt")

            result = self.run_tool(root)
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            self.assertTrue(report["git_repository"])
            self.assertEqual(report["branch"], "main")
            self.assertEqual(report["unstaged"]["files"], ["tracked.txt"])
            self.assertEqual(report["staged"]["files"], ["staged.txt"])
            self.assertEqual(report["untracked_files"], ["untracked.txt"])


if __name__ == "__main__":
    unittest.main()
