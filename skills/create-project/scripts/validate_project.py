#!/usr/bin/env python3
"""Validate a Cerebro-generated project structure and readiness evidence."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import re
import sys
from pathlib import Path

from bootstrap_project import (
    parse_features,
    parse_stacks,
    planned_files,
    validate_target,
)


SCRIPT_DIR = Path(__file__).resolve().parent
CANONICAL_RULES = (
    SCRIPT_DIR.parent / "references" / "stack-packs" / "rules.json"
)
TOKEN_RE = re.compile(r"\{\{[A-Z0-9_]+\}\}|\[TODO(?::[^\]]*)?\]", re.IGNORECASE)
LOCAL_LINK_RE = re.compile(r"\[[^\]]+\]\((?!https?://|mailto:|#)([^)]+)\)")
EXACT_VERSION_RE = re.compile(r"^\d+(?:\.\d+){0,3}$")
UNSTABLE_SOURCE_REF_RE = re.compile(
    r"(^|[^a-z0-9])(latest|canary|main|master|alpha|beta|rc|nightly|preview)"
    r"([^a-z0-9]|$)",
    re.IGNORECASE,
)
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
    parser.add_argument("--stacks", default="")
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
        stacks = parse_stacks(args.stacks)
        required = planned_files(args.profile, args.agents, features, stacks)
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

        stack_profile_path = root / ".cerebro/stack-profile.json"
        stack_profile: dict = {}
        if stack_profile_path.is_file():
            try:
                stack_profile = json.loads(
                    stack_profile_path.read_text(encoding="utf-8")
                )
            except json.JSONDecodeError as exc:
                errors.append(f".cerebro/stack-profile.json is invalid JSON: {exc}")
            if stack_profile and stack_profile.get("schema_version") != 1:
                errors.append(".cerebro/stack-profile.json has unsupported schema_version")

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
            if stack_profile.get("status") != "approved":
                errors.append(
                    ".cerebro/stack-profile.json must have status approved"
                )
            if not stack_profile.get("approval_record"):
                errors.append(
                    ".cerebro/stack-profile.json has no human approval_record"
                )
            selected_scopes: set[str] = set()
            if not stack_profile.get("stacks"):
                errors.append(".cerebro/stack-profile.json has no resolved stacks")
            else:
                for stack in stack_profile["stacks"]:
                    if not isinstance(stack, dict):
                        errors.append(
                            ".cerebro/stack-profile.json has malformed stack entry"
                        )
                        continue
                    selected_scopes.add(str(stack.get("scope", "")))
                    if not EXACT_VERSION_RE.fullmatch(str(stack.get("version", ""))):
                        errors.append(
                            ".cerebro/stack-profile.json stack "
                            f"{stack.get('scope')!r} has no exact numeric version"
                        )
                    if not stack.get("paths"):
                        errors.append(
                            ".cerebro/stack-profile.json stack "
                            f"{stack.get('scope')!r} has no path scope"
                        )
                if ("sqlserver" in selected_scopes) != (
                    "sqlserver" in stacks
                ):
                    errors.append(
                        "SQL Server profile/scaffold mismatch; validate with "
                        "--stacks sqlserver exactly when the approved profile "
                        "selects sqlserver"
                    )
            official_references = stack_profile.get("official_references")
            if not isinstance(official_references, list):
                errors.append(
                    ".cerebro/stack-profile.json has malformed official_references"
                )
            else:
                for reference in official_references:
                    if not isinstance(reference, dict):
                        errors.append(
                            ".cerebro/stack-profile.json has malformed official reference"
                        )
                        continue
                    resolved_ref = str(reference.get("resolved_ref", ""))
                    if (
                        not resolved_ref
                        or UNSTABLE_SOURCE_REF_RE.search(resolved_ref)
                        or not re.search(
                            r"\d|[0-9a-f]{7,40}", resolved_ref, re.IGNORECASE
                        )
                    ):
                        errors.append(
                            ".cerebro/stack-profile.json official reference "
                            f"{reference.get('scope')!r} is not exact/stable"
                        )
            selected_ids = stack_profile.get("selected_rule_ids")
            selected_rules = stack_profile.get("rule_bindings")
            if not isinstance(selected_ids, list) or not selected_ids:
                errors.append(
                    ".cerebro/stack-profile.json has no selected_rule_ids"
                )
            if (
                not isinstance(selected_rules, list)
                or not all(isinstance(rule, dict) for rule in selected_rules)
                or [rule.get("id") for rule in selected_rules] != selected_ids
            ):
                errors.append(
                    ".cerebro/stack-profile.json rule_bindings do not match selected_rule_ids"
                )
            pack = stack_profile.get("pack")
            if not isinstance(pack, dict):
                errors.append(".cerebro/stack-profile.json has no pack metadata")
            else:
                for field in (
                    "version_policy_next_review_at",
                    "source_catalog_next_light_review_at",
                ):
                    try:
                        deadline = dt.date.fromisoformat(pack[field])
                    except (KeyError, TypeError, ValueError):
                        errors.append(
                            f".cerebro/stack-profile.json has invalid {field}"
                        )
                        continue
                    if dt.date.today() > deadline:
                        errors.append(
                            f".cerebro/stack-profile.json is stale: {field}={deadline}"
                        )
                try:
                    canonical = json.loads(
                        CANONICAL_RULES.read_text(encoding="utf-8")
                    )
                except (OSError, json.JSONDecodeError):
                    errors.append(
                        "installed Cerebro rules.json is missing or malformed"
                    )
                else:
                    expected_pack = {
                        "best_practices_version": canonical["packs"][
                            "best_practices"
                        ]["version"],
                        "best_practices_sha256": canonical["packs"][
                            "best_practices"
                        ]["sha256"],
                        "anti_patterns_version": canonical["packs"][
                            "anti_pattern_guardrails"
                        ]["version"],
                        "anti_patterns_sha256": canonical["packs"][
                            "anti_pattern_guardrails"
                        ]["sha256"],
                        "version_policy_version": canonical["version_policy"][
                            "version"
                        ],
                        "version_policy_sha256": canonical["version_policy"][
                            "sha256"
                        ],
                        "source_catalog_version": canonical["source_catalog"][
                            "version"
                        ],
                        "source_catalog_sha256": canonical["source_catalog"][
                            "sha256"
                        ],
                    }
                    for field, expected in expected_pack.items():
                        if pack.get(field) != expected:
                            errors.append(
                                ".cerebro/stack-profile.json requires reviewed "
                                f"regeneration: {field} does not match installed "
                                "Cerebro"
                            )
                    if "sqlserver" in selected_scopes:
                        expected_standards = canonical["source_catalog"].get(
                            "house_standards", {}
                        ).get("sqlserver", [])
                        sql_references = [
                            reference
                            for reference in official_references
                            if isinstance(reference, dict)
                            and reference.get("scope") == "sqlserver"
                        ]
                        if len(sql_references) != 1:
                            errors.append(
                                ".cerebro/stack-profile.json must contain one "
                                "SQL Server official reference"
                            )
                        elif (
                            sql_references[0].get("house_standards")
                            != expected_standards
                        ):
                            errors.append(
                                ".cerebro/stack-profile.json SQL Server house "
                                "standard version/hash does not match installed "
                                "Cerebro; regenerate and review the profile"
                            )
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
    print(
        f"VALID: profile={args.profile} agents={args.agents} "
        f"stacks={','.join(sorted(stacks)) or 'none'} warnings={len(warnings)}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
