#!/usr/bin/env python3
"""Produce a read-only structural inventory for a Cerebro project audit."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from collections import defaultdict
from pathlib import Path


STATE_NAMES = {"PROJECT_STATE.md", "STATE.md", "HANDOFF.md"}
PROCESS_NAMES = {"PROCESS.md", "WORKFLOW.md"}
DOC_NAMES = {
    "AGENTS.md",
    "CLAUDE.md",
    "PROJECT_STATE.md",
    "PRODUCT.md",
    "REQUIREMENTS.md",
    "CONTEXT.md",
    "CONTEXT_MAP.md",
    "ARCHITECTURE.md",
    "DATA.md",
    "API.md",
    "SECURITY.md",
    "TESTING.md",
    "OPERATIONS.md",
    "MIGRATION.md",
}
TOKEN_RE = re.compile(r"\{\{[A-Z0-9_]+\}\}|\[TODO(?::[^\]]*)?\]", re.IGNORECASE)
IGNORED_DIRS = {
    ".git",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "target",
    "vendor",
}


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            value.update(chunk)
    return value.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True, type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    root = args.target.expanduser().resolve()
    if not root.is_dir():
        parser.error(f"target is not a directory: {root}")

    files = sorted(
        path
        for path in root.rglob("*")
        if path.is_file()
        and not any(part in IGNORED_DIRS for part in path.relative_to(root).parts)
        and path.name != ".DS_Store"
    )
    by_hash: dict[str, list[str]] = defaultdict(list)
    unresolved: list[str] = []
    for path in files:
        relative = str(path.relative_to(root))
        by_hash[digest(path)].append(relative)
        if path.suffix.lower() in {".md", ".txt", ".json", ".toml", ".yaml", ".yml"}:
            try:
                if TOKEN_RE.search(path.read_text(encoding="utf-8")):
                    unresolved.append(relative)
            except UnicodeDecodeError:
                pass

    report = {
        "root": str(root),
        "file_count": len(files),
        "canonical_docs_present": sorted(str(path.relative_to(root)) for path in files if path.name in DOC_NAMES),
        "state_candidates": sorted(str(path.relative_to(root)) for path in files if path.name in STATE_NAMES),
        "process_candidates": sorted(str(path.relative_to(root)) for path in files if path.name in PROCESS_NAMES),
        "domain_context_documents": sorted(
            str(path.relative_to(root)) for path in files if path.name in {"CONTEXT.md", "CONTEXT_MAP.md"}
        ),
        "duplicate_groups": sorted(
            (paths for paths in by_hash.values() if len(paths) > 1),
            key=lambda group: (-len(group), group),
        ),
        "unresolved_tokens": sorted(unresolved),
        "agent_surfaces": sorted(
            str(path.relative_to(root))
            for path in files
            if path.name in {"AGENTS.md", "CLAUDE.md", "SKILL.md"} or ".claude" in path.parts or ".agents" in path.parts
        ),
    }

    if args.json:
        print(json.dumps(report, indent=2))
        return 0

    print(f"root: {report['root']}")
    print(f"files: {report['file_count']}")
    for key in (
        "canonical_docs_present",
        "state_candidates",
        "process_candidates",
        "domain_context_documents",
        "unresolved_tokens",
    ):
        values = report[key]
        print(f"{key}: {len(values)}")
        for value in values:
            print(f"  - {value}")
    print(f"duplicate_groups: {len(report['duplicate_groups'])}")
    for group in report["duplicate_groups"]:
        print("  group:")
        for value in group:
            print(f"    - {value}")
    print(f"agent_surfaces: {len(report['agent_surfaces'])}")
    for value in report["agent_surfaces"]:
        print(f"  - {value}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
