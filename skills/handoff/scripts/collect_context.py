#!/usr/bin/env python3
"""Collect a bounded, read-only Git snapshot for a Cerebro handoff."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


COMMAND_TIMEOUT_SECONDS = 10


def run_git(root: Path, *arguments: str) -> tuple[bool, str]:
    try:
        result = subprocess.run(
            ["git", "-C", str(root), *arguments],
            text=True,
            capture_output=True,
            check=False,
            env={**os.environ, "GIT_OPTIONAL_LOCKS": "0"},
            timeout=COMMAND_TIMEOUT_SECONDS,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        return False, str(exc)
    output = result.stdout.strip()
    if result.returncode == 0:
        return True, output
    return False, result.stderr.strip() or output or f"git exited {result.returncode}"


def lines(value: str) -> list[str]:
    return [line for line in value.splitlines() if line]


def optional_git(root: Path, warnings: list[str], label: str, *arguments: str) -> str:
    ok, output = run_git(root, *arguments)
    if ok:
        return output
    warnings.append(f"{label}: {output}")
    return ""


def collect(root: Path) -> dict[str, object]:
    inside, output = run_git(root, "rev-parse", "--is-inside-work-tree")
    if not inside or output != "true":
        return {
            "schema_version": 1,
            "project": root.name,
            "git_repository": False,
            "reason": "not a Git worktree",
        }

    warnings: list[str] = []
    branch = optional_git(root, warnings, "branch", "branch", "--show-current")
    head = optional_git(root, warnings, "head", "rev-parse", "HEAD")
    status = lines(optional_git(root, warnings, "status", "status", "--short", "--untracked-files=all"))
    recent = lines(optional_git(root, warnings, "recent commits", "log", "-5", "--oneline"))
    diff_safety = ("--no-ext-diff", "--no-textconv")
    unstaged_stat = optional_git(root, warnings, "unstaged diff stat", "diff", *diff_safety, "--stat")
    unstaged_files = lines(
        optional_git(root, warnings, "unstaged files", "diff", *diff_safety, "--name-only")
    )
    staged_stat = optional_git(root, warnings, "staged diff stat", "diff", "--cached", *diff_safety, "--stat")
    staged_files = lines(
        optional_git(root, warnings, "staged files", "diff", "--cached", *diff_safety, "--name-only")
    )

    report: dict[str, object] = {
        "schema_version": 1,
        "project": root.name,
        "git_repository": True,
        "branch": branch or "DETACHED_OR_UNBORN",
        "head": head or "UNBORN",
        "status": status,
        "recent_commits": recent,
        "unstaged": {
            "files": unstaged_files,
            "stat": unstaged_stat,
        },
        "staged": {
            "files": staged_files,
            "stat": staged_stat,
        },
        "untracked_files": [entry[3:] for entry in status if entry.startswith("?? ")],
    }
    if warnings:
        report["warnings"] = warnings
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True, type=Path, help="Project directory to inspect")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    target = args.target.expanduser().resolve()
    if not target.is_dir():
        print(f"ERROR: target directory does not exist: {target}", file=sys.stderr)
        return 2
    print(json.dumps(collect(target), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
