#!/usr/bin/env python3
"""Create a right-sized Cerebro project skeleton without overwriting by default."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
ASSET_ROOT = SCRIPT_DIR.parent / "assets" / "project"

MINIMAL_FILES = {
    ".cerebro/project.json",
    ".cerebro/stack-profile.json",
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

STACK_FILES = {
    "sqlserver": {
        "docs/DATA.md",
        "database/templates/sqlserver/function-inline-table.sql",
        "database/templates/sqlserver/function-scalar.sql",
        "database/templates/sqlserver/stored-procedure-delete.sql",
        "database/templates/sqlserver/stored-procedure-get.sql",
        "database/templates/sqlserver/stored-procedure-insert.sql",
        "database/templates/sqlserver/stored-procedure-update.sql",
        "database/templates/sqlserver/stored-procedure-write-transaction.sql",
        "database/templates/sqlserver/trigger-dml.sql",
        "database/templates/sqlserver/type-table.sql",
    },
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


def parse_stacks(raw: str) -> set[str]:
    stacks = {item.strip().lower() for item in raw.split(",") if item.strip()}
    unknown = stacks - STACK_FILES.keys()
    if unknown:
        raise ValueError(f"unknown scaffold stacks: {', '.join(sorted(unknown))}")
    return stacks


def planned_files(
    profile: str,
    agents: str,
    features: set[str],
    stacks: set[str] | None = None,
) -> list[str]:
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

    for stack in stacks or set():
        if stack not in STACK_FILES:
            raise ValueError(f"unsupported scaffold stack: {stack}")
        files.update(STACK_FILES[stack])

    if agents in {"claude", "both"}:
        files.update(CLAUDE_BASE_FILES)
        if profile in {"standard", "critical"}:
            files.update(CLAUDE_MAINTAINED_FILES)

    return sorted(files)


def validate_target(target: Path) -> Path:
    expanded = target.expanduser()
    if expanded.is_symlink():
        raise ValueError(f"refusing symlink target path: {expanded}")
    resolved = expanded.resolve()
    if resolved == Path(resolved.anchor) or resolved == Path.home().resolve():
        raise ValueError(f"refusing broad target path: {resolved}")
    return resolved


def validate_relative_path(relative_path: str) -> Path:
    if "\\" in relative_path or "\x00" in relative_path:
        raise ValueError(f"unsafe project-relative path: {relative_path!r}")
    relative = Path(relative_path)
    if (
        relative.is_absolute()
        or not relative.parts
        or any(part in {"", ".", ".."} for part in relative.parts)
    ):
        raise ValueError(f"unsafe project-relative path: {relative_path!r}")
    return relative


def validate_destination(root: Path, relative_path: str) -> Path:
    relative = validate_relative_path(relative_path)
    destination = root / relative
    current = root
    for part in relative.parts:
        current = current / part
        if current.is_symlink():
            raise ValueError(
                f"refusing symlink destination or ancestor: {relative_path}"
            )
    try:
        destination.resolve(strict=False).relative_to(root)
    except ValueError as exc:
        raise ValueError(
            f"destination escapes project root: {relative_path}"
        ) from exc
    return destination


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


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def plugin_version() -> str:
    manifest = SCRIPT_DIR.parents[2] / ".codex-plugin" / "plugin.json"
    try:
        payload = json.loads(manifest.read_text(encoding="utf-8"))
        version = payload["version"]
    except (OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        raise ValueError(f"cannot resolve Cerebro plugin version: {exc}") from exc
    if not isinstance(version, str) or not version:
        raise ValueError("Cerebro plugin version is empty")
    return version


def secure_write_text(
    root: Path,
    relative_path: str,
    content: str,
    *,
    replace_existing: bool,
) -> None:
    """Write through directory file descriptors when supported.

    The complete plan is validated before this function is called. Directory
    descriptors plus O_NOFOLLOW close the final symlink race on supported
    POSIX platforms; the fallback revalidates every ancestor and refuses a
    symlink destination.
    """

    relative = validate_relative_path(relative_path)
    root.mkdir(parents=True, exist_ok=True)
    supports_dir_fd = (
        hasattr(os, "O_NOFOLLOW")
        and os.open in os.supports_dir_fd
        and os.mkdir in os.supports_dir_fd
    )
    if not supports_dir_fd:
        destination = validate_destination(root, relative_path)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination = validate_destination(root, relative_path)
        flags = os.O_WRONLY | os.O_CREAT
        flags |= os.O_TRUNC if replace_existing else os.O_EXCL
        flags |= getattr(os, "O_NOFOLLOW", 0)
        descriptor = os.open(destination, flags, 0o666)
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
        return

    directory_flags = (
        os.O_RDONLY
        | getattr(os, "O_DIRECTORY", 0)
        | getattr(os, "O_NOFOLLOW", 0)
    )
    root_descriptor = os.open(root, directory_flags)
    current_descriptor = root_descriptor
    try:
        for part in relative.parts[:-1]:
            try:
                os.mkdir(part, mode=0o777, dir_fd=current_descriptor)
            except FileExistsError:
                pass
            next_descriptor = os.open(
                part,
                directory_flags,
                dir_fd=current_descriptor,
            )
            if current_descriptor != root_descriptor:
                os.close(current_descriptor)
            current_descriptor = next_descriptor

        flags = os.O_WRONLY | os.O_CREAT | os.O_NOFOLLOW
        flags |= os.O_TRUNC if replace_existing else os.O_EXCL
        descriptor = os.open(
            relative.parts[-1],
            flags,
            0o666,
            dir_fd=current_descriptor,
        )
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as stream:
            stream.write(content)
    finally:
        if current_descriptor != root_descriptor:
            os.close(current_descriptor)
        os.close(root_descriptor)


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
    parser.add_argument(
        "--stacks",
        default="",
        help="Comma-separated stack-specific scaffold assets: sqlserver",
    )
    parser.add_argument(
        "--stack-profile",
        type=Path,
        help="Reviewed selector output to install instead of the draft profile",
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
        project_name = args.name.strip()
        if not project_name:
            raise ValueError("project name must not be empty")
        features = parse_features(args.features)
        stacks = parse_stacks(args.stacks)
        files = planned_files(args.profile, args.agents, features, stacks)
        destinations = {
            path: validate_destination(target, path) for path in files
        }
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    missing_assets = [path for path in files if not asset_for(path).is_file()]
    if missing_assets:
        print("ERROR: missing scaffold assets:", file=sys.stderr)
        for path in missing_assets:
            print(f"  - {path}", file=sys.stderr)
        return 2

    conflicts = [
        path
        for path, destination in destinations.items()
        if destination.exists() or destination.is_symlink()
    ]
    if conflicts and not (args.merge or args.force):
        print(f"ERROR: {len(conflicts)} target files already exist; use --merge or explicit --force", file=sys.stderr)
        for path in conflicts:
            print(f"  - {path}", file=sys.stderr)
        return 3

    action = "PLAN" if args.dry_run else "CREATE"
    print(f"{action}: {target}")
    print(
        f"profile={args.profile} agents={args.agents} "
        f"features={','.join(sorted(features)) or 'none'} "
        f"stacks={','.join(sorted(stacks)) or 'none'}"
    )
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
        "AGENTS_JSON": json.dumps(args.agents),
        "DATE": dt.date.today().isoformat(),
        "FEATURES_JSON": json.dumps(sorted(features)),
        "PLUGIN_VERSION": plugin_version(),
        "PROFILE": args.profile,
        "PROFILE_JSON": json.dumps(args.profile),
        "PROJECT_NAME": project_name,
        "PROJECT_NAME_JSON": json.dumps(project_name),
        "PROJECT_SLUG": slugify(project_name),
        "PROJECT_SLUG_JSON": json.dumps(slugify(project_name)),
        "REQUIRED_FILES_JSON": json.dumps(files),
        "STACKS_JSON": json.dumps(sorted(stacks)),
        "SUMMARY": args.summary.strip(),
    }

    stack_profile_path = ".cerebro/stack-profile.json"
    try:
        if args.stack_profile:
            stack_profile_text = args.stack_profile.read_text(encoding="utf-8")
            stack_profile_data = json.loads(stack_profile_text)
            if not isinstance(stack_profile_data, dict):
                raise ValueError("--stack-profile root must be a JSON object")
            if stack_profile_data.get("schema_version") != 1:
                raise ValueError("--stack-profile has unsupported schema_version")
            if not stack_profile_text.endswith("\n"):
                stack_profile_text += "\n"
        else:
            stack_profile_text = render(
                asset_for(stack_profile_path).read_text(encoding="utf-8"),
                values,
            )
            stack_profile_data = json.loads(stack_profile_text)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(f"ERROR: cannot load stack profile: {exc}", file=sys.stderr)
        return 2

    values["PROJECT_STATUS_JSON"] = json.dumps(
        "reference-approved"
        if stack_profile_data.get("status") == "approved"
        else "draft"
    )
    values["STACK_PROFILE_SHA256"] = sha256_text(stack_profile_text)

    rendered_files: dict[str, str] = {}
    try:
        for relative_path in files:
            if relative_path == stack_profile_path:
                rendered_files[relative_path] = stack_profile_text
                continue
            content = asset_for(relative_path).read_text(encoding="utf-8")
            rendered_files[relative_path] = render(content, values)
        # Re-run every containment check after all rendering and before the
        # first filesystem write.
        destinations = {
            path: validate_destination(target, path) for path in files
        }
    except (OSError, ValueError) as exc:
        print(f"ERROR: cannot build safe write plan: {exc}", file=sys.stderr)
        return 2

    created = 0
    replaced = 0
    preserved = 0
    for relative_path in files:
        destination = destinations[relative_path]
        if destination.exists() and args.merge:
            preserved += 1
            continue
        existed = destination.exists()
        try:
            secure_write_text(
                target,
                relative_path,
                rendered_files[relative_path],
                replace_existing=existed and args.force,
            )
        except (OSError, ValueError) as exc:
            print(
                f"ERROR: safe write rejected {relative_path}: {exc}",
                file=sys.stderr,
            )
            return 2
        if existed:
            replaced += 1
        else:
            created += 1

    print(f"RESULT: created={created} replaced={replaced} preserved={preserved}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
