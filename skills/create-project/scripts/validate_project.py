#!/usr/bin/env python3
"""Validate a Cerebro-generated project structure and readiness evidence."""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

from bootstrap_project import parse_features, planned_files, validate_target


TOKEN_RE = re.compile(r"\{\{[A-Z0-9_]+\}\}|\[TODO(?::[^\]]*)?\]", re.IGNORECASE)
LOCAL_LINK_RE = re.compile(r"\[[^\]]+\]\((?!https?://|mailto:|#)([^)]+)\)")
SAFETY_MARKERS = (
    "NO MAGIC",
    "VERIFY BEFORE DONE",
    "DISSENT",
    "SCOPE DRIFT DETECTION",
    "WORKSPACE BOUNDARY",
    "`R0`",
    "`R1`",
    "`R2`",
    "Claude Code",
    "Codex",
)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True, type=Path)
    parser.add_argument("--profile", choices=("minimal", "standard", "critical"), required=True)
    parser.add_argument("--agents", choices=("codex", "claude", "both"), default="both")
    parser.add_argument("--features", default="")
    parser.add_argument("--allow-draft", action="store_true")
    return parser


def check_local_links(root: Path, markdown: Path) -> list[str]:
    errors: list[str] = []
    text = markdown.read_text(encoding="utf-8")
    for match in LOCAL_LINK_RE.finditer(text):
        raw = match.group(1).split("#", 1)[0].strip()
        if not raw or raw.startswith("<"):
            raw = raw.strip("<>")
        if raw and not (markdown.parent / raw).resolve().exists():
            errors.append(f"broken link in {markdown.relative_to(root)}: {match.group(1)}")
    return errors


def main() -> int:
    args = build_parser().parse_args()
    try:
        root = validate_target(args.target)
        features = parse_features(args.features)
        required = planned_files(args.profile, args.agents, features)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    errors: list[str] = []
    warnings: list[str] = []

    if not root.is_dir():
        errors.append(f"target directory does not exist: {root}")
    else:
        for relative_path in required:
            if not (root / relative_path).is_file():
                errors.append(f"missing required file: {relative_path}")

        for forbidden in ("PROCESS.md", "docs/PROCESS.md"):
            if (root / forbidden).exists():
                errors.append(f"forbidden duplicate process surface: {forbidden}")

        for markdown in root.rglob("*.md"):
            if any(part == ".git" for part in markdown.parts):
                continue
            text = markdown.read_text(encoding="utf-8")
            token = TOKEN_RE.search(text)
            if token:
                errors.append(f"unresolved template token in {markdown.relative_to(root)}: {token.group(0)}")
            errors.extend(check_local_links(root, markdown))

        line_limits = {"AGENTS.md": 300, "CLAUDE.md": 180, "PROJECT_STATE.md": 250}
        for relative_path, limit in line_limits.items():
            path = root / relative_path
            if path.is_file():
                lines = len(path.read_text(encoding="utf-8").splitlines())
                if lines > limit:
                    errors.append(f"{relative_path} is {lines} lines; limit is {limit}")

        agents_text = (root / "AGENTS.md").read_text(encoding="utf-8") if (root / "AGENTS.md").is_file() else ""
        for marker in SAFETY_MARKERS:
            if marker not in agents_text:
                errors.append(f"AGENTS.md is missing safety/workflow marker: {marker}")

        if args.agents in {"claude", "both"}:
            claude_text = (root / "CLAUDE.md").read_text(encoding="utf-8") if (root / "CLAUDE.md").is_file() else ""
            for marker in ("primary planner, implementer, and finding fixer", "independent Codex CLI review"):
                if marker not in claude_text:
                    errors.append(f"CLAUDE.md is missing delivery-loop marker: {marker}")

        if not args.allow_draft:
            requirements = (root / "docs/REQUIREMENTS.md").read_text(encoding="utf-8") if (root / "docs/REQUIREMENTS.md").is_file() else ""
            state = (root / "PROJECT_STATE.md").read_text(encoding="utf-8") if (root / "PROJECT_STATE.md").is_file() else ""
            for pattern, label in (
                (r"\bFR-\d{3}\b", "functional requirement ID"),
                (r"\bNFR-\d{3}\b", "non-functional requirement ID"),
                (r"\bAC-\d{3}\b", "acceptance criterion ID"),
            ):
                if not re.search(pattern, requirements):
                    errors.append(f"docs/REQUIREMENTS.md has no {label}")
            if "IMPLEMENTATION_READY" not in state:
                errors.append("PROJECT_STATE.md does not declare IMPLEMENTATION_READY")
            if re.search(r"OPEN-BLOCKING|blocking gaps?:\s*(?!none\b)", requirements, re.IGNORECASE):
                errors.append("docs/REQUIREMENTS.md still contains a blocking gap marker")
            for markdown in root.rglob("*.md"):
                if any(part == ".git" for part in markdown.parts):
                    continue
                for line_number, line in enumerate(markdown.read_text(encoding="utf-8").splitlines(), start=1):
                    if "TBD" in line and "TBD-NONBLOCKING" not in line:
                        errors.append(
                            f"unresolved TBD in {markdown.relative_to(root)}:{line_number}; "
                            "resolve it or mark it TBD-NONBLOCKING with an owner"
                        )

        if args.profile == "critical":
            for relative_path in (
                "docs/SECURITY.md",
                "docs/DATA.md",
                "docs/OPERATIONS.md",
                "docs/quality/THREAT_MODEL.md",
                "docs/quality/RELEASE_CHECKLIST.md",
            ):
                path = root / relative_path
                if path.is_file() and len(path.read_text(encoding="utf-8").strip()) < 100:
                    errors.append(f"critical project document is effectively empty: {relative_path}")

    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)

    if errors:
        print(f"INVALID: errors={len(errors)} warnings={len(warnings)}", file=sys.stderr)
        return 1
    print(f"VALID: profile={args.profile} agents={args.agents} warnings={len(warnings)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
