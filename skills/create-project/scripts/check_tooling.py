#!/usr/bin/env python3
"""Report agent/tool availability without installing or changing configuration."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
from pathlib import Path


KNOWN_TOOLS = ("codex", "claude", "rtk")


def run_read_only(command: list[str]) -> dict[str, object]:
    try:
        result = subprocess.run(command, capture_output=True, text=True, timeout=10, check=False)
    except (OSError, subprocess.TimeoutExpired) as exc:
        return {"ok": False, "error": str(exc)}
    output = (result.stdout or result.stderr).strip()
    return {"ok": result.returncode == 0, "exit_code": result.returncode, "output": output}


def inspect_tool(name: str) -> dict[str, object]:
    executable = shutil.which(name)
    if not executable:
        return {"status": "ABSENT"}
    version_check = run_read_only([executable, "--version"])
    return {
        "status": "PRESENT" if version_check.get("ok") else "UNKNOWN",
        "executable": executable,
        "version": version_check.get("output", ""),
    }


def inspect_rtk_integration(target: Path, result: dict[str, object]) -> None:
    if result["status"] == "ABSENT":
        result["integration"] = {"claude": "ABSENT", "codex_project": "ABSENT"}
        return

    executable = str(result["executable"])
    show = run_read_only([executable, "init", "--show"])
    output = str(show.get("output", ""))
    claude_ready = "[ok] Hook:" in output and "settings.json: RTK hook configured" in output

    agents = target / "AGENTS.md"
    rtk_doc = target / "RTK.md"
    agents_mentions_rtk = agents.is_file() and "RTK.md" in agents.read_text(encoding="utf-8")
    codex_ready = rtk_doc.is_file() and agents_mentions_rtk

    result["integration"] = {
        "claude": "READY" if claude_ready else "BINARY_ONLY",
        "codex_project": "READY" if codex_ready else "BINARY_ONLY",
    }
    result["configuration_check"] = show


def inspect_caveman(
    claude_result: dict[str, object],
    *,
    config_dir: Path | None = None,
    home_dir: Path | None = None,
) -> dict[str, object]:
    home = home_dir or Path.home()
    claude_config = config_dir or Path(os.environ.get("CLAUDE_CONFIG_DIR", home / ".claude"))
    codex_config = Path(os.environ.get("CODEX_HOME", home / ".codex"))
    codex_candidates = (
        codex_config / "skills" / "caveman" / "SKILL.md",
        home / ".agents" / "skills" / "caveman" / "SKILL.md",
    )
    codex_ready = any(path.is_file() for path in codex_candidates)

    if claude_result["status"] == "ABSENT":
        return {
            "status": "PRESENT" if codex_ready else "ABSENT",
            "official_source": "https://github.com/JuliusBrussee/caveman",
            "integration": {"claude": "ABSENT", "codex": "READY" if codex_ready else "ABSENT"},
        }

    executable = str(claude_result["executable"])
    listing = run_read_only([executable, "plugin", "list", "--json"])
    if not listing.get("ok"):
        return {
            "status": "UNKNOWN",
            "official_source": "https://github.com/JuliusBrussee/caveman",
            "integration": {"claude": "UNKNOWN", "codex": "READY" if codex_ready else "ABSENT"},
            "configuration_check": {
                "ok": False,
                "exit_code": listing.get("exit_code"),
                "error": listing.get("error", "Claude plugin listing failed"),
            },
        }

    try:
        plugins = json.loads(str(listing.get("output", "")))
    except json.JSONDecodeError:
        plugins = []
    installed = next(
        (plugin for plugin in plugins if isinstance(plugin, dict) and plugin.get("id") == "caveman@caveman"),
        None,
    )

    flag = claude_config / ".caveman-active"
    mode = flag.read_text(encoding="utf-8").strip() if flag.is_file() else ""
    if installed and installed.get("enabled"):
        claude_status = "READY" if mode else "ENABLED_NO_ACTIVE_FLAG"
    elif installed:
        claude_status = "DISABLED"
    else:
        claude_status = "ABSENT"

    return {
        "status": "PRESENT" if installed or codex_ready else "ABSENT",
        "official_source": "https://github.com/JuliusBrussee/caveman",
        "version": installed.get("version", "") if installed else "",
        "mode": mode,
        "integration": {"claude": claude_status, "codex": "READY" if codex_ready else "ABSENT"},
        "configuration_check": {
            "ok": True,
            "plugin_found": installed is not None,
            "enabled": bool(installed and installed.get("enabled")),
            "active_flag": bool(mode),
        },
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", type=Path, default=Path.cwd())
    parser.add_argument("--json", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    target = args.target.expanduser().resolve()
    report: dict[str, object] = {"target": str(target), "tools": {}}
    tools = report["tools"]
    assert isinstance(tools, dict)

    for name in KNOWN_TOOLS:
        tools[name] = inspect_tool(name)
    inspect_rtk_integration(target, tools["rtk"])
    tools["caveman"] = inspect_caveman(tools["claude"])

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"target: {target}")
        for name, details in tools.items():
            assert isinstance(details, dict)
            print(f"{name}: {details['status']}")
            if details.get("version"):
                print(f"  version: {details['version']}")
            integration = details.get("integration")
            if isinstance(integration, dict):
                for agent, status in integration.items():
                    print(f"  {agent}: {status}")
            if details.get("action"):
                print(f"  action: {details['action']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
