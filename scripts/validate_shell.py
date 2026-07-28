#!/usr/bin/env python3
"""Run bash syntax validation for every repository-owned shell script."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
IGNORED_DIRECTORIES = {".git", ".venv", "node_modules", "vendor"}


def shell_files() -> list[Path]:
    return sorted(
        path
        for path in ROOT.rglob("*.sh")
        if path.is_file()
        and not any(
            part in IGNORED_DIRECTORIES
            for part in path.relative_to(ROOT).parts
        )
    )


def main() -> int:
    files = shell_files()
    if not files:
        print("VALID: shell=none")
        return 0

    errors = 0
    for path in files:
        result = subprocess.run(
            ["bash", "-n", str(path)],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode:
            errors += 1
            detail = (result.stdout + result.stderr).strip()
            print(
                f"ERROR: {path.relative_to(ROOT)}: {detail or 'bash -n failed'}",
                file=sys.stderr,
            )
    if errors:
        print(f"INVALID: shell errors={errors}", file=sys.stderr)
        return 1
    print(f"VALID: shell={len(files)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
