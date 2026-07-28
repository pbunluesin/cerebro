#!/usr/bin/env python3
"""Validate a Cerebro-generated project from its canonical local manifest."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import os
import re
import sys
from pathlib import Path

from bootstrap_project import (
    STACK_FILES,
    parse_features,
    parse_stacks,
    planned_files,
    slugify,
    validate_destination,
    validate_target,
)
from select_stack_rules import SelectionError, select


SCRIPT_DIR = Path(__file__).resolve().parent
REFERENCE_DIR = SCRIPT_DIR.parent / "references"
CANONICAL_RULES = REFERENCE_DIR / "stack-packs" / "rules.json"
CANONICAL_POLICY = REFERENCE_DIR / "stack-version-policy.json"
CANONICAL_CATALOG = REFERENCE_DIR / "official-sources.json"
SCAN_POLICY = REFERENCE_DIR / "project-scan-policy.json"
TOKEN_RE = re.compile(
    r"\{\{[A-Z0-9_]+\}\}|\[TODO(?::[^\]]*)?\]",
    re.IGNORECASE,
)
LOCAL_LINK_RE = re.compile(r"\[[^\]]+\]\((?!https?://|mailto:|#)([^)]+)\)")
EXACT_VERSION_RE = re.compile(r"^\d+(?:\.\d+){0,3}$")
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
    parser.add_argument(
        "--profile",
        choices=("minimal", "standard", "critical"),
        help="compatibility assertion only; canonical value comes from project.json",
    )
    parser.add_argument(
        "--agents",
        choices=("codex", "claude", "both"),
        help="compatibility assertion only; canonical value comes from project.json",
    )
    parser.add_argument(
        "--features",
        help="compatibility assertion only; canonical value comes from project.json",
    )
    parser.add_argument(
        "--stacks",
        help="compatibility assertion only; canonical value comes from project.json",
    )
    parser.add_argument("--allow-draft", action="store_true")
    return parser


def load_json(path: Path, label: str) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"{label} is missing or invalid JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{label} root must be a JSON object")
    return payload


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            value.update(chunk)
    return value.hexdigest()


def ignored_directories() -> set[str]:
    policy = load_json(SCAN_POLICY, "project scan policy")
    if policy.get("schema_version") != 1:
        raise ValueError("project scan policy has unsupported schema_version")
    values = policy.get("ignored_directories")
    if (
        not isinstance(values, list)
        or not values
        or not all(isinstance(item, str) and item for item in values)
    ):
        raise ValueError("project scan policy ignored_directories is malformed")
    return set(values)


def project_markdown(root: Path) -> tuple[list[Path], list[str]]:
    markdown: list[Path] = []
    errors: list[str] = []
    ignored = ignored_directories()
    for directory, names, files in os.walk(root, topdown=True, followlinks=False):
        current = Path(directory)
        kept: list[str] = []
        for name in names:
            candidate = current / name
            if name in ignored:
                continue
            if candidate.is_symlink():
                errors.append(
                    "project-owned directory is a symlink: "
                    f"{candidate.relative_to(root)}"
                )
                continue
            kept.append(name)
        names[:] = kept
        for name in files:
            if not name.lower().endswith(".md"):
                continue
            candidate = current / name
            if candidate.is_symlink():
                errors.append(
                    "project-owned Markdown is a symlink: "
                    f"{candidate.relative_to(root)}"
                )
                continue
            try:
                candidate.resolve(strict=False).relative_to(root)
            except ValueError:
                errors.append(
                    "project-owned Markdown escapes project root: "
                    f"{candidate.relative_to(root)}"
                )
                continue
            markdown.append(candidate)
    return sorted(markdown), errors


def check_local_links(root: Path, markdown: Path) -> list[str]:
    errors: list[str] = []
    text = markdown.read_text(encoding="utf-8")
    for match in LOCAL_LINK_RE.finditer(text):
        raw = match.group(1).split("#", 1)[0].strip().strip("<>")
        if not raw:
            continue
        link = Path(raw)
        candidate = markdown.parent / link
        if link.is_absolute():
            errors.append(
                f"absolute local link in {markdown.relative_to(root)}: "
                f"{match.group(1)}"
            )
            continue
        try:
            relative = candidate.resolve(strict=False).relative_to(root)
        except ValueError:
            errors.append(
                f"local link escapes project root in "
                f"{markdown.relative_to(root)}: {match.group(1)}"
            )
            continue
        current = root
        symlinked = False
        for part in relative.parts:
            current = current / part
            if current.is_symlink():
                symlinked = True
                break
        if symlinked:
            errors.append(
                f"local link crosses a symlink in "
                f"{markdown.relative_to(root)}: {match.group(1)}"
            )
        elif not candidate.exists():
            errors.append(
                f"broken link in {markdown.relative_to(root)}: {match.group(1)}"
            )
    return errors


def has_blocking_gap(requirements: str) -> tuple[bool, bool]:
    found = False
    blocked = "OPEN-BLOCKING" in requirements.upper()
    for line in requirements.splitlines():
        match = re.match(
            r"^\s*(?:[-*]\s*)?blocking gaps?\s*:\s*(.*?)\s*$",
            line,
            re.IGNORECASE,
        )
        if not match:
            continue
        found = True
        value = match.group(1).strip().strip("`").lower()
        if value not in {"none", "no blocking gaps", "n/a", "not applicable"}:
            blocked = True
    return found, blocked


def derive_manifest_contract(
    manifest: dict,
) -> tuple[str, str, set[str], set[str], list[str]]:
    if manifest.get("schema_version") != 1:
        raise ValueError("project.json has unsupported schema_version")
    if manifest.get("status") not in {
        "draft",
        "reference-approved",
        "implementation-ready",
    }:
        raise ValueError("project.json has invalid status")
    try:
        dt.date.fromisoformat(str(manifest.get("generated_at")))
    except ValueError as exc:
        raise ValueError("project.json has invalid generated_at") from exc
    generated_by = manifest.get("generated_by")
    if (
        not isinstance(generated_by, dict)
        or generated_by.get("tool") != "cerebro"
        or not re.fullmatch(
            r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?",
            str(generated_by.get("plugin_version", "")),
        )
    ):
        raise ValueError("project.json has invalid generated_by contract")
    project = manifest.get("project")
    if (
        not isinstance(project, dict)
        or not isinstance(project.get("name"), str)
        or not project["name"].strip()
        or project.get("slug") != slugify(project["name"])
    ):
        raise ValueError("project.json has invalid project identity")
    scaffold = manifest.get("scaffold")
    if not isinstance(scaffold, dict):
        raise ValueError("project.json has no scaffold contract")
    profile = scaffold.get("profile")
    agents = scaffold.get("agents")
    if profile not in {"minimal", "standard", "critical"}:
        raise ValueError("project.json has invalid scaffold.profile")
    if agents not in {"codex", "claude", "both"}:
        raise ValueError("project.json has invalid scaffold.agents")
    raw_features = scaffold.get("features")
    raw_stacks = scaffold.get("stacks")
    required_files = scaffold.get("required_files")
    if not isinstance(raw_features, list) or not all(
        isinstance(item, str) for item in raw_features
    ):
        raise ValueError("project.json has malformed scaffold.features")
    if raw_features != sorted(set(raw_features)):
        raise ValueError(
            "project.json scaffold.features must be sorted and unique"
        )
    if not isinstance(raw_stacks, list) or not all(
        isinstance(item, str) for item in raw_stacks
    ):
        raise ValueError("project.json has malformed scaffold.stacks")
    if raw_stacks != sorted(set(raw_stacks)):
        raise ValueError(
            "project.json scaffold.stacks must be sorted and unique"
        )
    if (
        not isinstance(required_files, list)
        or not required_files
        or not all(isinstance(item, str) and item for item in required_files)
    ):
        raise ValueError("project.json has malformed scaffold.required_files")
    features = parse_features(",".join(raw_features))
    stacks = parse_stacks(",".join(raw_stacks))
    expected = planned_files(profile, agents, features, stacks)
    if required_files != expected:
        raise ValueError(
            "project.json required_files do not match the canonical scaffold "
            "plan; regenerate the project manifest"
        )
    return profile, agents, features, stacks, expected


def rebuild_stack_profile(stack_profile: dict) -> dict:
    stacks = stack_profile.get("stacks")
    if not isinstance(stacks, list) or not stacks:
        raise ValueError("stack-profile.json has no resolved stacks")
    stack_args: list[str] = []
    path_args: list[str] = []
    source_args: list[str] = []
    for stack in stacks:
        if not isinstance(stack, dict):
            raise ValueError("stack-profile.json has malformed stack entry")
        scope = stack.get("scope")
        version = stack.get("version")
        paths = stack.get("paths")
        if not isinstance(scope, str) or not EXACT_VERSION_RE.fullmatch(
            str(version)
        ):
            raise ValueError("stack-profile.json has malformed stack identity")
        if (
            not isinstance(paths, list)
            or not paths
            or not all(isinstance(path, str) for path in paths)
        ):
            raise ValueError(f"stack-profile.json stack {scope} has bad paths")
        stack_args.append(f"{scope}@{version}")
        path_args.extend(f"{scope}={path}" for path in paths)
        source_ref = stack.get("resolved_source_ref")
        if source_ref is not None:
            source_args.append(f"{scope}={source_ref}")

    namespace = argparse.Namespace(
        stack=stack_args,
        path=path_args,
        source_ref=source_args,
        approval_record=stack_profile.get("approval_record"),
        as_of=stack_profile.get("resolved_at"),
        rules=CANONICAL_RULES,
        version_policy=CANONICAL_POLICY,
        source_catalog=CANONICAL_CATALOG,
        out=None,
    )
    try:
        return select(namespace)
    except (SelectionError, TypeError, ValueError) as exc:
        raise ValueError(f"stack-profile.json cannot be reproduced: {exc}") from exc


def main() -> int:
    args = build_parser().parse_args()
    try:
        root = validate_target(args.target)
    except ValueError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2

    errors: list[str] = []
    warnings: list[str] = []
    manifest: dict = {}
    project_manifest_path: Path | None = None
    try:
        project_manifest_path = validate_destination(
            root,
            ".cerebro/project.json",
        )
        manifest = load_json(project_manifest_path, ".cerebro/project.json")
        profile, agents, features, stacks, required = derive_manifest_contract(
            manifest
        )
    except ValueError as exc:
        errors.append(str(exc))
        profile, agents, features, stacks, required = (
            "minimal",
            "codex",
            set(),
            set(),
            [],
        )

    try:
        asserted_features = (
            None if args.features is None else parse_features(args.features)
        )
        asserted_stacks = (
            None if args.stacks is None else parse_stacks(args.stacks)
        )
    except ValueError as exc:
        errors.append(f"invalid compatibility assertion: {exc}")
        asserted_features = None
        asserted_stacks = None
    assertions = (
        ("--profile", args.profile, profile),
        ("--agents", args.agents, agents),
        ("--features", asserted_features, features),
        ("--stacks", asserted_stacks, stacks),
    )
    for label, supplied, canonical in assertions:
        if supplied is not None and supplied != canonical:
            errors.append(
                f"{label} conflicts with .cerebro/project.json; "
                f"supplied={supplied!r} canonical={canonical!r}"
            )

    if not root.is_dir():
        errors.append(f"target directory does not exist: {root}")
    else:
        for relative_path in required:
            try:
                candidate = validate_destination(root, relative_path)
            except ValueError as exc:
                errors.append(str(exc))
                continue
            if not candidate.is_file():
                errors.append(f"missing required file: {relative_path}")

        for forbidden in ("PROCESS.md", "docs/PROCESS.md"):
            if (root / forbidden).exists():
                errors.append(f"forbidden duplicate process surface: {forbidden}")

        try:
            markdown_files, scan_errors = project_markdown(root)
            errors.extend(scan_errors)
        except ValueError as exc:
            errors.append(str(exc))
            markdown_files = []
        for markdown in markdown_files:
            text = markdown.read_text(encoding="utf-8")
            token = TOKEN_RE.search(text)
            if token:
                errors.append(
                    "unresolved template token in "
                    f"{markdown.relative_to(root)}: {token.group(0)}"
                )
            errors.extend(check_local_links(root, markdown))

        line_limits = {
            "AGENTS.md": 300,
            "CLAUDE.md": 180,
            "PROJECT_STATE.md": 250,
        }
        for relative_path, limit in line_limits.items():
            path = root / relative_path
            if path.is_file() and not path.is_symlink():
                lines = len(path.read_text(encoding="utf-8").splitlines())
                if lines > limit:
                    errors.append(
                        f"{relative_path} is {lines} lines; limit is {limit}"
                    )

        agents_path = root / "AGENTS.md"
        agents_text = (
            agents_path.read_text(encoding="utf-8")
            if agents_path.is_file() and not agents_path.is_symlink()
            else ""
        )
        for marker in SAFETY_MARKERS:
            if marker not in agents_text:
                errors.append(
                    f"AGENTS.md is missing safety/workflow marker: {marker}"
                )

        if agents in {"claude", "both"}:
            claude_path = root / "CLAUDE.md"
            claude_text = (
                claude_path.read_text(encoding="utf-8")
                if claude_path.is_file() and not claude_path.is_symlink()
                else ""
            )
            for marker in (
                "primary planner, implementer, and finding fixer",
                "independent Codex CLI review",
            ):
                if marker not in claude_text:
                    errors.append(
                        f"CLAUDE.md is missing delivery-loop marker: {marker}"
                    )

        stack_profile: dict = {}
        stack_profile_path: Path | None = None
        stack_contract = manifest.get("stack_profile")
        if not isinstance(stack_contract, dict):
            errors.append("project.json has no stack_profile contract")
        elif stack_contract.get("path") != ".cerebro/stack-profile.json":
            errors.append(
                "project.json stack_profile.path must be "
                ".cerebro/stack-profile.json"
            )
        else:
            try:
                stack_profile_path = validate_destination(
                    root,
                    stack_contract["path"],
                )
                actual_hash = sha256(stack_profile_path)
                if stack_contract.get("sha256") != actual_hash:
                    errors.append(
                        "project.json stack_profile.sha256 does not match "
                        ".cerebro/stack-profile.json"
                    )
                stack_profile = load_json(
                    stack_profile_path,
                    ".cerebro/stack-profile.json",
                )
            except (OSError, ValueError) as exc:
                errors.append(str(exc))

        if not args.allow_draft:
            requirements_path = root / "docs/REQUIREMENTS.md"
            state_path = root / "PROJECT_STATE.md"
            requirements = (
                requirements_path.read_text(encoding="utf-8")
                if requirements_path.is_file()
                and not requirements_path.is_symlink()
                else ""
            )
            state = (
                state_path.read_text(encoding="utf-8")
                if state_path.is_file() and not state_path.is_symlink()
                else ""
            )
            for pattern, label in (
                (r"\bFR-\d{3}\b", "functional requirement ID"),
                (r"\bNFR-\d{3}\b", "non-functional requirement ID"),
                (r"\bAC-\d{3}\b", "acceptance criterion ID"),
            ):
                if not re.search(pattern, requirements):
                    errors.append(f"docs/REQUIREMENTS.md has no {label}")
            if not re.search(
                r"(?m)^- Phase:\s*`?IMPLEMENTATION_READY`?\s*$",
                state,
            ):
                errors.append(
                    "PROJECT_STATE.md does not declare an exact "
                    "IMPLEMENTATION_READY phase"
                )
            gap_marker_found, blocking_gap = has_blocking_gap(requirements)
            if not gap_marker_found:
                errors.append(
                    "docs/REQUIREMENTS.md has no Blocking gaps declaration"
                )
            elif blocking_gap:
                errors.append(
                    "docs/REQUIREMENTS.md still contains a blocking gap marker"
                )

            if manifest.get("status") not in {
                "reference-approved",
                "implementation-ready",
            }:
                errors.append(
                    ".cerebro/project.json is not reference-approved"
                )
            if stack_profile.get("schema_version") != 1:
                errors.append(
                    ".cerebro/stack-profile.json has unsupported schema_version"
                )
            if stack_profile.get("status") != "approved":
                errors.append(
                    ".cerebro/stack-profile.json must have status approved"
                )
            if not stack_profile.get("approval_record"):
                errors.append(
                    ".cerebro/stack-profile.json has no human approval_record"
                )

            if stack_profile:
                selected_stack_scopes = {
                    str(item.get("scope"))
                    for item in stack_profile.get("stacks", [])
                    if isinstance(item, dict)
                }
                expected_asset_stacks = (
                    selected_stack_scopes & set(STACK_FILES)
                )
                if stacks != expected_asset_stacks:
                    errors.append(
                        ".cerebro/project.json scaffold.stacks must match "
                        "stack-specific assets required by the approved "
                        "stack profile; "
                        f"manifest={sorted(stacks)} "
                        f"profile={sorted(expected_asset_stacks)}"
                    )
                try:
                    expected_profile = rebuild_stack_profile(stack_profile)
                except ValueError as exc:
                    errors.append(str(exc))
                else:
                    for field in (
                        "status",
                        "resolved_at",
                        "approval_record",
                        "pack",
                        "stacks",
                        "official_references",
                        "selected_rule_ids",
                        "rule_bindings",
                        "exceptions",
                    ):
                        if stack_profile.get(field) != expected_profile.get(field):
                            errors.append(
                                ".cerebro/stack-profile.json cannot be "
                                f"reproduced from canonical rules: {field} differs"
                            )

            pack = stack_profile.get("pack")
            if isinstance(pack, dict):
                for field in (
                    "version_policy_next_review_at",
                    "source_catalog_next_light_review_at",
                    "source_catalog_next_full_review_at",
                ):
                    try:
                        deadline = dt.date.fromisoformat(str(pack[field]))
                    except (KeyError, ValueError):
                        errors.append(
                            f".cerebro/stack-profile.json has invalid {field}"
                        )
                        continue
                    if dt.date.today() > deadline:
                        errors.append(
                            ".cerebro/stack-profile.json is stale: "
                            f"{field}={deadline}"
                        )

            for markdown in markdown_files:
                for line_number, line in enumerate(
                    markdown.read_text(encoding="utf-8").splitlines(),
                    start=1,
                ):
                    if (
                        re.search(r"\bTBD\b", line)
                        and "TBD-NONBLOCKING" not in line
                    ):
                        errors.append(
                            f"unresolved TBD in "
                            f"{markdown.relative_to(root)}:{line_number}; "
                            "resolve it or mark it TBD-NONBLOCKING with an owner"
                        )

        if profile == "critical":
            for relative_path in (
                "docs/SECURITY.md",
                "docs/DATA.md",
                "docs/OPERATIONS.md",
                "docs/quality/THREAT_MODEL.md",
                "docs/quality/RELEASE_CHECKLIST.md",
            ):
                path = root / relative_path
                if (
                    path.is_file()
                    and not path.is_symlink()
                    and len(path.read_text(encoding="utf-8").strip()) < 100
                ):
                    errors.append(
                        "critical project document is effectively empty: "
                        f"{relative_path}"
                    )

    for warning in warnings:
        print(f"WARNING: {warning}")
    for error in errors:
        print(f"ERROR: {error}", file=sys.stderr)
    if errors:
        print(
            f"INVALID: errors={len(errors)} warnings={len(warnings)}",
            file=sys.stderr,
        )
        return 1
    print(
        f"VALID: profile={profile} agents={agents} "
        f"stacks={','.join(sorted(stacks)) or 'none'} "
        f"warnings={len(warnings)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
