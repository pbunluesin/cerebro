#!/usr/bin/env python3
"""Select version-compatible Cerebro rules for explicit stack/path scopes.

Examples:
  python3 select_stack_rules.py \
    --stack nextjs@16.1.0 --stack react@19.2.0 \
    --stack typescript@5.9.0 --stack a11y@2.2 \
    --path 'nextjs=apps/web/**' \
    --approval-record 'requirements-final:2026-07-28:project-owner' \
    --out .cerebro/stack-profile.json

The selector is deliberately offline and dependency-free. Updating upstream
knowledge is a separate reviewed operation; project generation consumes only
the pinned catalog and generated rules committed with Cerebro.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path

from stack_freshness import evaluate_freshness


SCRIPT_DIR = Path(__file__).resolve().parent
REFERENCE_DIR = SCRIPT_DIR.parent / "references"
DEFAULT_RULES = REFERENCE_DIR / "stack-packs" / "rules.json"
DEFAULT_POLICY = REFERENCE_DIR / "stack-version-policy.json"
DEFAULT_CATALOG = REFERENCE_DIR / "official-sources.json"
VERSION = re.compile(r"^\d+(?:\.\d+){0,3}$")
UNSTABLE_REF = re.compile(
    r"(^|[^a-z0-9])(latest|canary|main|master|alpha|beta|rc|nightly|preview)"
    r"([^a-z0-9]|$)",
    re.IGNORECASE,
)
APPROVAL_RECORD_RE = re.compile(
    r"^requirements-final:(\d{4}-\d{2}-\d{2}):"
    r"([A-Za-z0-9][A-Za-z0-9._@-]{1,127})$"
)
SOURCE_REF_TOKENS = re.compile(
    r"(\{version\}|\{major\}|\{minor\}|\{patch\}|\{date\})"
)


class SelectionError(ValueError):
    pass


def load_json(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SelectionError(f"cannot load {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise SelectionError(f"{path}: root must be a JSON object")
    return value


def numeric_version(raw: str) -> tuple[int, ...]:
    if not VERSION.fullmatch(raw):
        raise SelectionError(
            f"version {raw!r} is not exact; use a resolved numeric version"
        )
    return tuple(int(part) for part in raw.split("."))


def compare(left: tuple[int, ...], right: tuple[int, ...]) -> int:
    width = max(len(left), len(right))
    padded_left = left + (0,) * (width - len(left))
    padded_right = right + (0,) * (width - len(right))
    return (padded_left > padded_right) - (padded_left < padded_right)


def satisfies(version: str, constraint: str) -> bool:
    actual = numeric_version(version)
    for term in constraint.split(","):
        match = re.fullmatch(r"\s*(=|>=|<=|>|<)\s*(\d+(?:\.\d+){0,3})\s*", term)
        if not match:
            raise SelectionError(f"unsupported version constraint {constraint!r}")
        operator, expected_raw = match.groups()
        relation = compare(actual, numeric_version(expected_raw))
        accepted = {
            "=": relation == 0,
            ">=": relation >= 0,
            "<=": relation <= 0,
            ">": relation > 0,
            "<": relation < 0,
        }[operator]
        if not accepted:
            return False
    return True


def parse_pairs(values: list[str], separator: str, label: str) -> dict[str, str]:
    parsed: dict[str, str] = {}
    for value in values:
        if separator not in value:
            raise SelectionError(
                f"{label} {value!r} must use <scope>{separator}<value>"
            )
        scope, item = value.split(separator, 1)
        scope, item = scope.strip(), item.strip()
        if not scope or not item:
            raise SelectionError(f"{label} {value!r} has an empty scope or value")
        if scope in parsed and parsed[scope] != item:
            raise SelectionError(f"{label} {scope!r} was provided more than once")
        parsed[scope] = item
    return parsed


def parse_paths(values: list[str]) -> dict[str, set[str]]:
    parsed: dict[str, set[str]] = {}
    for value in values:
        if "=" not in value:
            raise SelectionError(f"--path {value!r} must use <scope>=<path-glob>")
        scope, path = value.split("=", 1)
        scope, path = scope.strip(), path.strip()
        if not scope or not path:
            raise SelectionError(f"--path {value!r} has an empty scope or path")
        if (
            "\\" in path
            or "\x00" in path
            or path.startswith("/")
            or re.match(r"^[A-Za-z]:", path)
            or any(part in {"", ".", ".."} for part in path.split("/"))
        ):
            raise SelectionError(
                f"--path {path!r} must be a normalized project-relative glob "
                "without absolute, empty, dot, parent, drive, or backslash segments"
            )
        parsed.setdefault(scope, set()).add(path)
    return parsed


def source_ref_regex(template: str, version: str) -> re.Pattern[str]:
    parts = version.split(".")
    replacements = {
        "{version}": re.escape(version),
        "{major}": re.escape(parts[0]),
        "{minor}": re.escape(parts[1] if len(parts) > 1 else "0"),
        "{patch}": re.escape(parts[2] if len(parts) > 2 else "0"),
        "{date}": r"\d{4}-\d{2}-\d{2}",
    }
    pattern = "".join(
        replacements.get(part, re.escape(part))
        for part in SOURCE_REF_TOKENS.split(template)
        if part
    )
    return re.compile(f"^{pattern}$")


def validate_source_refs(
    source_refs: dict[str, str],
    versions: dict[str, str],
    catalog: dict,
) -> None:
    for scope, source_ref in source_refs.items():
        if UNSTABLE_REF.search(source_ref):
            raise SelectionError(
                f"{scope} source ref {source_ref!r} is not a stable exact ref"
            )
        if not re.search(r"\d|[0-9a-f]{7,40}", source_ref, re.IGNORECASE):
            raise SelectionError(
                f"{scope} source ref {source_ref!r} has no version, date, or commit"
            )
        source = catalog.get("stacks", {}).get(scope)
        if not source:
            continue
        formats = source.get("source_ref_formats")
        if (
            not isinstance(formats, list)
            or not formats
            or not all(isinstance(item, str) and item for item in formats)
        ):
            raise SelectionError(
                f"{scope} source catalog has no source_ref_formats contract"
            )
        version = versions.get(scope)
        if not version or not any(
            source_ref_regex(template, version).fullmatch(source_ref)
            for template in formats
        ):
            raise SelectionError(
                f"{scope} source ref {source_ref!r} does not match the "
                f"approved format for {scope}@{version}; expected one of "
                + ", ".join(formats)
            )


def validate_approval_record(
    approval_record: str | None,
    as_of: dt.date,
) -> None:
    if approval_record is None:
        return
    match = APPROVAL_RECORD_RE.fullmatch(approval_record)
    if not match:
        raise SelectionError(
            "--approval-record must use "
            "requirements-final:<YYYY-MM-DD>:<approver>"
        )
    try:
        approved_at = dt.date.fromisoformat(match.group(1))
    except ValueError as exc:
        raise SelectionError("--approval-record has an invalid date") from exc
    if approved_at > as_of:
        raise SelectionError("--approval-record date cannot be after --as-of")


def sha256(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(65536), b""):
            value.update(chunk)
    return value.hexdigest()


def validate_input_bundle(
    args: argparse.Namespace,
    rules: dict,
) -> tuple[str, str, str]:
    try:
        actual_rules_hash = sha256(args.rules)
        actual_policy_hash = sha256(args.version_policy)
        actual_catalog_hash = sha256(args.source_catalog)
    except OSError as exc:
        raise SelectionError(f"cannot hash selection input bundle: {exc}") from exc
    if rules.get("version_policy", {}).get("sha256") != actual_policy_hash:
        raise SelectionError(
            "version policy content does not match rules.json; regenerate the "
            "reviewed rule bundle"
        )
    if rules.get("source_catalog", {}).get("sha256") != actual_catalog_hash:
        raise SelectionError(
            "source catalog content does not match rules.json; regenerate the "
            "reviewed rule bundle"
        )
    custom_inputs = any(
        supplied.resolve() != canonical.resolve()
        for supplied, canonical in (
            (args.rules, DEFAULT_RULES),
            (args.version_policy, DEFAULT_POLICY),
            (args.source_catalog, DEFAULT_CATALOG),
        )
    )
    if args.approval_record and custom_inputs:
        raise SelectionError(
            "custom rule/catalog/policy paths may produce candidate output "
            "only; approved profiles require the installed canonical bundle"
        )
    return actual_rules_hash, actual_policy_hash, actual_catalog_hash


def check_local_references(
    as_of: dt.date, selected_scopes: set[str], catalog: dict
) -> None:
    for scope in sorted(selected_scopes):
        source = catalog.get("stacks", {}).get(scope, {})
        for field, label in (
            ("house_standards", "house standard"),
            ("engineering_guides", "engineering guide"),
        ):
            for reference in source.get(field, []):
                if reference.get("status") != "approved":
                    raise SelectionError(
                        f"{scope} {label} {reference.get('id')} is not approved"
                    )
                try:
                    deadline = dt.date.fromisoformat(
                        reference.get("next_review_at")
                    )
                except (TypeError, ValueError) as exc:
                    raise SelectionError(
                        f"{scope} {label} {reference.get('id')} has an "
                        "invalid review deadline"
                    ) from exc
                if as_of > deadline:
                    raise SelectionError(
                        f"{scope} {label} {reference.get('id')} is stale as "
                        f"of {as_of}; review it before selecting rules"
                    )


def closure(selected: set[str], scopes: dict) -> set[str]:
    resolved = set(selected)
    pending = list(selected)
    while pending:
        scope = pending.pop()
        for included in scopes[scope].get("includes", []):
            if included != "global" and included not in scopes:
                raise SelectionError(
                    f"version policy scope {scope} includes unknown scope {included}"
                )
            if included not in resolved:
                resolved.add(included)
                if included != "global":
                    pending.append(included)
    resolved.add("global")
    return resolved


def resolve_paths(
    selected_versions: dict[str, str],
    explicit_paths: dict[str, set[str]],
    scopes: dict,
) -> dict[str, list[str]]:
    unknown = sorted(set(explicit_paths) - set(selected_versions))
    if unknown:
        raise SelectionError(
            "path supplied for unselected scope(s): " + ", ".join(unknown)
        )

    resolved: dict[str, set[str]] = {
        scope: set(paths) for scope, paths in explicit_paths.items()
    }
    changed = True
    while changed:
        changed = False
        for scope, paths in list(resolved.items()):
            if scope not in scopes:
                continue
            for included in scopes[scope].get("includes", []):
                if included == "global":
                    continue
                before = len(resolved.get(included, set()))
                resolved.setdefault(included, set()).update(paths)
                changed = changed or len(resolved[included]) != before

    missing = sorted(set(selected_versions) - set(resolved))
    if missing:
        raise SelectionError(
            "missing path scope(s): "
            + ", ".join(missing)
            + "; supply --path scope=glob on each independent stack root"
        )
    all_paths = sorted({path for values in resolved.values() for path in values})
    resolved["global"] = set(all_paths)
    return {scope: sorted(paths) for scope, paths in sorted(resolved.items())}


def select(args: argparse.Namespace) -> dict:
    rules = load_json(args.rules)
    policy = load_json(args.version_policy)
    catalog = load_json(args.source_catalog)
    if rules.get("schema_version") != 2:
        raise SelectionError("rules.json must use schema_version 2")
    (
        actual_rules_hash,
        actual_policy_hash,
        actual_catalog_hash,
    ) = validate_input_bundle(args, rules)

    try:
        as_of = dt.date.fromisoformat(args.as_of)
    except ValueError as exc:
        raise SelectionError("--as-of must be an ISO date") from exc
    validate_approval_record(args.approval_record, as_of)

    versions = parse_pairs(args.stack, "@", "--stack")
    paths = parse_paths(args.path)
    source_refs = parse_pairs(args.source_ref, "=", "--source-ref")
    scopes = policy.get("scopes", {})
    unknown = sorted(set(versions) - set(scopes))
    if unknown:
        raise SelectionError("unknown stack scope(s): " + ", ".join(unknown))
    if not versions:
        raise SelectionError("at least one --stack scope@exact-version is required")
    try:
        freshness = evaluate_freshness(
            as_of,
            policy,
            catalog,
            set(versions),
        )
    except ValueError as exc:
        raise SelectionError(str(exc)) from exc
    if freshness["overdue"]:
        overdue = freshness["overdue"][0]
        raise SelectionError(
            f"{overdue['label']} is stale as of {as_of}; review deadline "
            f"was {overdue['date']}"
        )
    check_local_references(as_of, set(versions), catalog)
    source_scopes = set(versions) & set(catalog.get("stacks", {}))
    unknown_source_refs = sorted(set(source_refs) - source_scopes)
    if unknown_source_refs:
        raise SelectionError(
            "source ref supplied for unselected/non-catalog scope(s): "
            + ", ".join(unknown_source_refs)
        )
    missing_source_refs = sorted(source_scopes - set(source_refs))
    if missing_source_refs:
        raise SelectionError(
            "resolved official --source-ref required for scope(s): "
            + ", ".join(missing_source_refs)
        )
    validate_source_refs(source_refs, versions, catalog)

    applicable_scopes = closure(set(versions), scopes)
    rules_by_scope: dict[str, list[dict]] = {}
    for rule in rules["rules"]:
        rules_by_scope.setdefault(rule["scope"], []).append(rule)

    missing_versions = sorted(
        scope
        for scope in applicable_scopes
        if scope not in {"global"}
        and scope not in versions
        and any(
            rule["applicability"].get("version_bound")
            for rule in rules_by_scope.get(scope, [])
        )
    )
    if missing_versions:
        raise SelectionError(
            "exact version required for included scope(s): "
            + ", ".join(missing_versions)
        )

    for scope, version in versions.items():
        resolved_version = numeric_version(version)
        constraint = scopes[scope]["constraint"]
        if not satisfies(version, constraint):
            raise SelectionError(
                f"{scope}@{version} is outside approved range {constraint}"
            )
        allowed_majors = scopes[scope].get("allowed_majors")
        if allowed_majors and resolved_version[0] not in allowed_majors:
            raise SelectionError(
                f"{scope}@{version} major is not approved; allowed majors are "
                + ", ".join(str(major) for major in allowed_majors)
            )

    resolved_paths = resolve_paths(versions, paths, scopes)
    selected_rules: list[dict] = []
    for rule in rules["rules"]:
        scope = rule["scope"]
        if scope not in applicable_scopes:
            continue
        applicability = rule["applicability"]
        if applicability.get("version_bound") and scope != "global":
            version = versions.get(scope)
            if not version:
                continue
            constraint = applicability.get("constraint", scopes[scope]["constraint"])
            if not satisfies(version, constraint):
                continue
        selected_rules.append(
            {
                "id": rule["id"],
                "scope": scope,
                "paths": resolved_paths.get(scope, resolved_paths["global"]),
            }
        )

    stack_records = []
    for scope, version in sorted(versions.items()):
        source = catalog.get("stacks", {}).get(scope)
        stack_records.append(
            {
                "scope": scope,
                "version": version,
                "paths": resolved_paths[scope],
                "constraint": scopes[scope]["constraint"],
                "version_source": scopes[scope]["version_source"],
                "resolved_source_ref": source_refs.get(scope),
                "approved_ref": source.get("approved_ref") if source else None,
                "observed_ref": source.get("observed_ref") if source else None,
            }
        )

    official_references = []
    for scope in sorted(set(versions) & set(catalog.get("stacks", {}))):
        source = catalog["stacks"][scope]
        scaffold = source.get("scaffold") or {}
        official_references.append(
            {
                "scope": scope,
                "approved_ref": source["approved_ref"],
                "observed_ref": source["observed_ref"],
                "resolved_ref": source_refs[scope],
                "scaffold_repository": scaffold.get("repository"),
                "scaffold_command": scaffold.get("command"),
                "docs": source.get("docs", [])[:2],
                "examples": source.get("examples", [])[:1],
                "house_standards": source.get("house_standards", []),
                "engineering_guides": source.get("engineering_guides", []),
            }
        )

    return {
        "schema_version": 1,
        "status": "approved" if args.approval_record else "candidate",
        "resolved_at": args.as_of,
        "approval_record": args.approval_record,
        "pack": {
            "best_practices_version": rules["packs"]["best_practices"]["version"],
            "best_practices_sha256": rules["packs"]["best_practices"]["sha256"],
            "anti_patterns_version": rules["packs"]["anti_pattern_guardrails"][
                "version"
            ],
            "anti_patterns_sha256": rules["packs"]["anti_pattern_guardrails"][
                "sha256"
            ],
            "version_policy_version": policy["policy_version"],
            "version_policy_sha256": actual_policy_hash,
            "version_policy_next_review_at": policy["next_review_at"],
            "source_catalog_version": catalog["catalog_version"],
            "source_catalog_sha256": actual_catalog_hash,
            "source_catalog_next_light_review_at": catalog[
                "next_light_review_at"
            ],
            "source_catalog_next_full_review_at": catalog[
                "next_full_review_at"
            ],
            "rules_sha256": actual_rules_hash,
        },
        "stacks": stack_records,
        "official_references": official_references,
        "selected_rule_ids": [rule["id"] for rule in selected_rules],
        "rule_bindings": selected_rules,
        "exceptions": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--stack",
        action="append",
        default=[],
        help="repeatable scope@exact-version",
    )
    parser.add_argument(
        "--path", action="append", default=[], help="repeatable scope=path-glob"
    )
    parser.add_argument(
        "--source-ref",
        action="append",
        default=[],
        help="repeatable catalog-scope=exact package/tag/commit or dated docs ref",
    )
    parser.add_argument(
        "--approval-record",
        help="human-approved requirements/ADR checkpoint; otherwise status is candidate",
    )
    parser.add_argument(
        "--as-of", default=dt.date.today().isoformat(), help="ISO evaluation date"
    )
    parser.add_argument("--rules", type=Path, default=DEFAULT_RULES)
    parser.add_argument("--version-policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--source-catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()

    try:
        payload = select(args)
    except SelectionError as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 1

    rendered = json.dumps(payload, ensure_ascii=False, indent=2) + "\n"
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding="utf-8")
        print(
            f"OK: wrote {args.out} with {len(payload['selected_rule_ids'])} rules "
            f"({payload['status']})"
        )
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    sys.exit(main())
