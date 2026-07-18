#!/usr/bin/env python3
"""Create a right-sized Cerebro project skeleton without overwriting by default."""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
ASSET_ROOT = SCRIPT_DIR.parent / "assets" / "project"

MINIMAL_FILES = {
    ".gitignore",
    "AGENTS.md",
    "PROJECT_STATE.md",
    "README.md",
    "docs/ARCHITECTURE.md",
    "docs/PRODUCT.md",
    "docs/README.md",
    "docs/REQUIREMENTS.md",
    "docs/TESTING.md",
    "docs/decisions/0000-template.md",
}

STANDARD_FILES = MINIMAL_FILES | {
    ".env.example",
    ".github/pull_request_template.md",
    "docs/CONTEXT.md",
    "docs/OPERATIONS.md",
    "docs/SECURITY.md",
    "docs/quality/REVIEW_CONTRACT.md",
    "docs/quality/findings/.gitkeep",
}

CRITICAL_FILES = STANDARD_FILES | {
    "docs/DATA.md",
    "docs/quality/RELEASE_CHECKLIST.md",
    "docs/quality/THREAT_MODEL.md",
}

FEATURE_FILES = {
    "api": {"docs/API.md"},
    "context": {"docs/CONTEXT.md"},
    "data": {"docs/DATA.md"},
    "migration": {"docs/MIGRATION.md"},
    "operations": {"docs/OPERATIONS.md"},
    "security": {"docs/SECURITY.md"},
}

CLAUDE_BASE_FILES = {
    "CLAUDE.md",
    ".claude/rules/guardrails.md",
}

CLAUDE_MAINTAINED_FILES = {
    ".claude/agents/cerebro-fixer.md",
    ".claude/agents/cerebro-reviewer.md",
    ".claude/rules/docs-routing.md",
}


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "project"


def parse_features(raw: str) -> set[str]:
    features = {item.strip().lower() for item in raw.split(",") if item.strip()}
    unknown = features - FEATURE_FILES.keys()
    if unknown:
        raise ValueError(f"unknown features: {', '.join(sorted(unknown))}")
    return features


def planned_files(profile: str, agents: str, features: set[str]) -> list[str]:
    if profile == "minimal":
        files = set(MINIMAL_FILES)
    elif profile == "standard":
        files = set(STANDARD_FILES)
    elif profile == "critical":
        files = set(CRITICAL_FILES)
    else:
        raise ValueError(f"unsupported profile: {profile}")

    for feature in features:
        files.update(FEATURE_FILES[feature])

    if agents in {"claude", "both"}:
        files.update(CLAUDE_BASE_FILES)
        if profile in {"standard", "critical"}:
            files.update(CLAUDE_MAINTAINED_FILES)

    return sorted(files)


def validate_target(target: Path) -> Path:
    resolved = target.expanduser().resolve()
    if resolved == Path(resolved.anchor) or resolved == Path.home().resolve():
        raise ValueError(f"refusing broad target path: {resolved}")
    return resolved


def asset_for(relative_path: str) -> Path:
    return ASSET_ROOT / f"{relative_path}.tmpl"


def render(template: str, values: dict[str, str]) -> str:
    result = template
    for key, value in values.items():
        result = result.replace("{{" + key + "}}", value)
    unresolved = sorted(set(re.findall(r"\{\{[A-Z0-9_]+\}\}", result)))
    if unresolved:
        raise ValueError(f"unresolved template tokens: {', '.join(unresolved)}")
    return result


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--target", required=True, type=Path)
    parser.add_argument("--name", required=True)
    parser.add_argument("--profile", choices=("minimal", "standard", "critical"), required=True)
    parser.add_argument("--agents", choices=("codex", "claude", "both"), default="both")
    parser.add_argument(
        "--features",
        default="",
        help="Comma-separated optional concerns: api,context,data,migration,operations,security",
    )
    parser.add_argument("--summary", default="TBD — replace with the confirmed project outcome.")
    parser.add_argument("--dry-run", action="store_true")
    overwrite = parser.add_mutually_exclusive_group()
    overwrite.add_argument("--merge", action="store_true", help="Create missing files and preserve conflicts")
    overwrite.add_argument("--force", action="store_true", help="Overwrite planned files")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    try:
        target = validate_target(args.target)
        features = parse_features(args.features)
        files = planned_files(args.profile, args.agents, features)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    missing_assets = [path for path in files if not asset_for(path).is_file()]
    if missing_assets:
        print("ERROR: missing scaffold assets:", file=sys.stderr)
        for path in missing_assets:
            print(f"  - {path}", file=sys.stderr)
        return 2

    conflicts = [path for path in files if (target / path).exists()]
    if conflicts and not (args.merge or args.force):
        print(f"ERROR: {len(conflicts)} target files already exist; use --merge or explicit --force", file=sys.stderr)
        for path in conflicts:
            print(f"  - {path}", file=sys.stderr)
        return 3

    action = "PLAN" if args.dry_run else "CREATE"
    print(f"{action}: {target}")
    print(f"profile={args.profile} agents={args.agents} features={','.join(sorted(features)) or 'none'}")
    for path in files:
        if path in conflicts and args.merge:
            print(f"PRESERVE {path}")
        elif path in conflicts and args.force:
            print(f"REPLACE  {path}")
        else:
            print(f"CREATE   {path}")

    if args.dry_run:
        return 0

    values = {
        "DATE": dt.date.today().isoformat(),
        "PROFILE": args.profile,
        "PROJECT_NAME": args.name,
        "PROJECT_SLUG": slugify(args.name),
        "SUMMARY": args.summary.strip(),
    }

    created = 0
    replaced = 0
    preserved = 0
    for relative_path in files:
        destination = target / relative_path
        if destination.exists() and args.merge:
            preserved += 1
            continue
        content = asset_for(relative_path).read_text(encoding="utf-8")
        rendered = render(content, values)
        destination.parent.mkdir(parents=True, exist_ok=True)
        existed = destination.exists()
        destination.write_text(rendered, encoding="utf-8")
        if existed:
            replaced += 1
        else:
            created += 1

    print(f"RESULT: created={created} replaced={replaced} preserved={preserved}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
