#!/usr/bin/env python3
"""Report Cerebro Stack Pack versions, freshness, and refresh targets."""

from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REFERENCE_DIR = SCRIPT_DIR.parent / "references"
DEFAULT_RULES = REFERENCE_DIR / "stack-packs" / "rules.json"
DEFAULT_POLICY = REFERENCE_DIR / "stack-version-policy.json"
DEFAULT_CATALOG = REFERENCE_DIR / "official-sources.json"


def load(path: Path) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ValueError(f"cannot load {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{path}: root must be a JSON object")
    return value


def parse_date(value: object, label: str) -> dt.date:
    try:
        return dt.date.fromisoformat(str(value))
    except ValueError as exc:
        raise ValueError(f"{label} has invalid ISO date {value!r}") from exc


def build_status(
    rules: dict, policy: dict, catalog: dict, as_of: dt.date
) -> dict:
    policy_due = parse_date(policy.get("next_review_at"), "version policy")
    light_due = parse_date(
        catalog.get("next_light_review_at"), "source catalog light review"
    )
    full_due = parse_date(
        catalog.get("next_full_review_at"), "source catalog full review"
    )
    stacks = []
    house_standards = []
    house_review_deadlines: list[dt.date] = []
    for scope, source in sorted(catalog.get("stacks", {}).items()):
        stacks.append(
            {
                "scope": scope,
                "approved_range": source.get("approved_range"),
                "observed_ref": source.get("observed_ref"),
                "approved_ref": source.get("approved_ref"),
                "new_project_allowed": source.get("new_project_allowed"),
                "next_action": (
                    source.get(
                        "observation_status", "semantic-review-required"
                    )
                    if source.get("observed_ref") != source.get("approved_ref")
                    else "no-ref-delta-recorded"
                ),
                "observation_note": source.get("observation_note"),
            }
        )
        for standard in source.get("house_standards", []):
            standard_due = parse_date(
                standard.get("next_review_at"),
                f"{scope} house standard {standard.get('id')}",
            )
            house_review_deadlines.append(standard_due)
            house_standards.append(
                {
                    "scope": scope,
                    "id": standard.get("id"),
                    "version": standard.get("version"),
                    "status": standard.get("status"),
                    "sha256": standard.get("sha256"),
                    "next_review_at": standard_due.isoformat(),
                    "next_action": (
                        "review-required"
                        if as_of > standard_due
                        else "current"
                    ),
                }
            )
    return {
        "as_of": as_of.isoformat(),
        "status": (
            "stale"
            if as_of
            > min([policy_due, light_due, *house_review_deadlines])
            else "full-review-due"
            if as_of > full_due
            else "current"
        ),
        "policy_version": policy.get("policy_version"),
        "catalog_version": catalog.get("catalog_version"),
        "best_practices_version": rules.get("packs", {})
        .get("best_practices", {})
        .get("version"),
        "anti_patterns_version": rules.get("packs", {})
        .get("anti_pattern_guardrails", {})
        .get("version"),
        "deadlines": {
            "version_policy": policy_due.isoformat(),
            "light_source_review": light_due.isoformat(),
            "full_semantic_review": full_due.isoformat(),
        },
        "stacks": stacks,
        "house_standards": house_standards,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--as-of", default=dt.date.today().isoformat())
    parser.add_argument("--rules", type=Path, default=DEFAULT_RULES)
    parser.add_argument("--version-policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--source-catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    try:
        as_of = dt.date.fromisoformat(args.as_of)
        status = build_status(
            load(args.rules),
            load(args.version_policy),
            load(args.source_catalog),
            as_of,
        )
    except ValueError as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 2

    if args.json:
        print(json.dumps(status, ensure_ascii=False, indent=2))
    else:
        deadlines = status["deadlines"]
        print(
            f"Stack Packs: {status['status']} as of {status['as_of']} "
            f"(BP {status['best_practices_version']}, "
            f"AP {status['anti_patterns_version']}, "
            f"policy {status['policy_version']}, "
            f"catalog {status['catalog_version']})"
        )
        print(
            "Deadlines: "
            f"policy={deadlines['version_policy']} "
            f"light={deadlines['light_source_review']} "
            f"full={deadlines['full_semantic_review']}"
        )
        for stack in status["stacks"]:
            print(
                f"{stack['scope']}: range={stack['approved_range']} "
                f"observed={stack['observed_ref']} "
                f"approved={stack['approved_ref']} "
                f"action={stack['next_action']}"
            )
            if stack["observation_note"]:
                print(f"  note: {stack['observation_note']}")
        for standard in status["house_standards"]:
            print(
                f"house-standard {standard['id']}: scope={standard['scope']} "
                f"version={standard['version']} "
                f"review={standard['next_review_at']} "
                f"action={standard['next_action']}"
            )
    return 1 if status["status"] == "stale" else 0


if __name__ == "__main__":
    sys.exit(main())
