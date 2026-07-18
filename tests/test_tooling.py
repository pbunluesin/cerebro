from __future__ import annotations

import importlib.util
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "create-project" / "scripts" / "check_tooling.py"
SPEC = importlib.util.spec_from_file_location("check_tooling", SCRIPT)
assert SPEC and SPEC.loader
CHECK_TOOLING = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CHECK_TOOLING)


class ToolingDetectionTests(unittest.TestCase):
    def test_absent_tool_is_reported_without_execution(self) -> None:
        with mock.patch.object(CHECK_TOOLING.shutil, "which", return_value=None):
            self.assertEqual(CHECK_TOOLING.inspect_tool("rtk"), {"status": "ABSENT"})

    def test_rtk_detects_claude_and_project_codex_integrations(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary)
            (target / "AGENTS.md").write_text("Read RTK.md before work.\n", encoding="utf-8")
            (target / "RTK.md").write_text("# RTK\n", encoding="utf-8")
            result: dict[str, object] = {"status": "PRESENT", "executable": "/bin/rtk"}
            show = {
                "ok": True,
                "exit_code": 0,
                "output": "[ok] Hook: configured\n[ok] settings.json: RTK hook configured",
            }
            with mock.patch.object(CHECK_TOOLING, "run_read_only", return_value=show):
                CHECK_TOOLING.inspect_rtk_integration(target, result)

            self.assertEqual(
                result["integration"],
                {"claude": "READY", "codex_project": "READY"},
            )

    def test_rtk_binary_only_when_agent_configuration_is_absent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            result: dict[str, object] = {"status": "PRESENT", "executable": "/bin/rtk"}
            show = {"ok": True, "exit_code": 0, "output": "RTK configuration: none"}
            with mock.patch.object(CHECK_TOOLING, "run_read_only", return_value=show):
                CHECK_TOOLING.inspect_rtk_integration(Path(temporary), result)

            self.assertEqual(
                result["integration"],
                {"claude": "BINARY_ONLY", "codex_project": "BINARY_ONLY"},
            )

    def test_caveman_detects_enabled_claude_and_codex_skill(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            config = home / ".claude"
            config.mkdir()
            (config / ".caveman-active").write_text("full\n", encoding="utf-8")
            codex_skill = home / ".agents/skills/caveman/SKILL.md"
            codex_skill.parent.mkdir(parents=True)
            codex_skill.write_text("# Caveman\n", encoding="utf-8")
            listing = {
                "ok": True,
                "exit_code": 0,
                "output": json.dumps([
                    {"id": "caveman@caveman", "version": "abc123", "enabled": True}
                ]),
            }
            claude = {"status": "PRESENT", "executable": "/bin/claude"}
            with mock.patch.object(CHECK_TOOLING, "run_read_only", return_value=listing):
                result = CHECK_TOOLING.inspect_caveman(claude, config_dir=config, home_dir=home)

            self.assertEqual(result["status"], "PRESENT")
            self.assertEqual(result["mode"], "full")
            self.assertEqual(result["integration"], {"claude": "READY", "codex": "READY"})
            self.assertNotIn("output", result["configuration_check"])

    def test_caveman_absent_when_no_agent_integration_exists(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            listing = {"ok": True, "exit_code": 0, "output": "[]"}
            claude = {"status": "PRESENT", "executable": "/bin/claude"}
            with mock.patch.object(CHECK_TOOLING, "run_read_only", return_value=listing):
                result = CHECK_TOOLING.inspect_caveman(
                    claude,
                    config_dir=home / ".claude",
                    home_dir=home,
                )

            self.assertEqual(result["status"], "ABSENT")
            self.assertEqual(result["integration"], {"claude": "ABSENT", "codex": "ABSENT"})


if __name__ == "__main__":
    unittest.main()
