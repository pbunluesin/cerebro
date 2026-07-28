#!/usr/bin/env python3
"""Extract and validate Cerebro's versioned stack packs.

Usage:
    python3 extract_stack_rules.py [--check] [-o rules.json]

Exit codes: 0 = OK (warnings allowed), 1 = validation or drift errors.

The two markdown packs remain the human-facing source of truth. This script is
the machine boundary: the plugin consumes rules.json, never the full markdown,
and
CI runs this script so every structural guarantee in the packs' validation
checklists is enforced automatically:

  * rule IDs unique within each pack; known level/class vocabulary only
  * table column integrity (AP rows = 6 cells, BP rows = 4 cells)
  * no unescaped '|' inside inline code spans in table rows (breaks Markdown)
  * every source referenced by an AP rule exists in the AP source registry
  * every ID in the related-pair map (AP section 2.5) exists in both packs
  * document_version present and listed in the change log of each pack
  * every version-bound rule maps to the version policy
  * official source and version policy metadata remain structurally valid
  * generated output includes source hashes and is deterministic
  * warning (non-fatal) when an exact pair mixes requirement strengths

The output is JSON, avoiding a plugin-level PyYAML dependency.
"""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
REFERENCE_DIR = SCRIPT_DIR.parent / "references"
PACK_DIR = REFERENCE_DIR / "stack-packs"
DEFAULT_AP = PACK_DIR / "anti-patterns.md"
DEFAULT_BP = PACK_DIR / "best-practices.md"
DEFAULT_POLICY = REFERENCE_DIR / "stack-version-policy.json"
DEFAULT_CATALOG = REFERENCE_DIR / "official-sources.json"
DEFAULT_OUT = PACK_DIR / "rules.json"

RULE_ID = re.compile(r"^[A-Z][A-Z0-9]*(?:-[A-Z0-9]+)*-\d{3}$")
SOURCE_ID = re.compile(r"^[A-Z][A-Z0-9]*-\d{2}$")
LINK = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

SCOPE_BY_PREFIX = {
    "GLOBAL": "global",
    "NODE": "nodejs",
    "TS": "typescript",
    "PHP73": "php73",
    "PHP8": "php8",
    "NEXT": "nextjs",
    "REACT": "react",
    "NEST": "nestjs",
    "VUE": "vue",
    "TW": "tailwind",
    "A11Y": "a11y",
    "PG": "postgresql",
    "MSSQL": "sqlserver",
}
SCOPE_ORDER = list(SCOPE_BY_PREFIX.values()) + ["other"]

AP_LEVELS = {"MUST_NOT", "SHOULD_NOT", "REVIEW_REQUIRED"}
BP_LEVELS = {"MUST", "SHOULD", "MAY", "MUST_NOT", "SHOULD_NOT"}
CLASSES = {
    "invariant",
    "version-bound",
    "legacy-constraint",
    "migration-risk",
    "project-policy",
    "context-sensitive",
}

PIPE_TOKEN = "\x00ESCPIPE\x00"


def split_row(line: str) -> list[str]:
    """Split a markdown table row into cells, honouring escaped pipes."""
    inner = line.strip().strip("|")
    cells = inner.replace(r"\|", PIPE_TOKEN).split("|")
    return [c.replace(PIPE_TOKEN, "|").strip() for c in cells]


def table_rows(text: str):
    """Yield (line_number, cells) for table rows outside fenced code blocks."""
    fenced = False
    for n, line in enumerate(text.splitlines(), 1):
        if line.lstrip().startswith("```"):
            fenced = not fenced
            continue
        if fenced or not line.lstrip().startswith("|"):
            continue
        yield n, split_row(line)


def strip_code(cell: str) -> str:
    return cell.strip().strip("`").strip()


def scope_of(rule_id: str) -> str:
    return SCOPE_BY_PREFIX.get(rule_id.split("-", 1)[0], "other")


class Report:
    def __init__(self) -> None:
        self.errors: list[str] = []
        self.warnings: list[str] = []

    def error(self, msg: str) -> None:
        self.errors.append(msg)

    def warn(self, msg: str) -> None:
        self.warnings.append(msg)


def check_common(name: str, text: str, report: Report) -> str:
    """Shared checks; returns the document version."""
    m = re.search(r'^document_version:\s*"(\d+\.\d+\.\d+)"', text, re.M)
    if not m:
        report.error(f"{name}: document_version frontmatter missing")
        return "0.0.0"
    version = m.group(1)
    if f"### {version} " not in text and f"### {version}\n" not in text:
        report.error(f"{name}: change log has no entry for {version}")
    for n, line in enumerate(text.splitlines(), 1):
        if not line.lstrip().startswith("|"):
            continue
        for code in re.findall(r"`[^`]*`", line):
            if "|" in code and r"\|" not in code:
                report.error(
                    f"{name}:{n}: unescaped '|' inside code span {code!r} breaks the table"
                )
    return version


def metadata_date(name: str, text: str, key: str, report: Report) -> str:
    match = re.search(rf'^{re.escape(key)}:\s*"(\d{{4}}-\d{{2}}-\d{{2}})"', text, re.M)
    if not match:
        report.error(f"{name}: {key} frontmatter missing")
        return "0001-01-01"
    return match.group(1)


def parse_ap(path: Path, report: Report) -> dict:
    text = path.read_text(encoding="utf-8")
    name = path.name
    version = check_common(name, text, report)

    rules: dict[str, dict] = {}
    related: dict[str, dict] = {}
    sources: dict[str, dict] = {}

    for n, cells in table_rows(text):
        head = strip_code(cells[0]) if cells else ""

        if RULE_ID.match(head) and len(cells) == 6:
            rid, level, cls = head, strip_code(cells[1]), strip_code(cells[2])
            if rid in rules:
                report.error(f"{name}:{n}: duplicate rule ID {rid}")
                continue
            if level not in AP_LEVELS:
                report.error(f"{name}:{n}: {rid} has unknown level {level!r}")
            if cls not in CLASSES:
                report.error(f"{name}:{n}: {rid} has unknown class {cls!r}")
            refs = [
                strip_code(tok)
                for tok in re.findall(r"`([^`]+)`", cells[5])
                if SOURCE_ID.match(strip_code(tok))
            ]
            rules[rid] = {
                "level": level,
                "class": cls,
                "pattern": cells[3],
                "remediation": cells[4],
                "sources": refs,
                "line": n,
            }
        elif RULE_ID.match(head) and len(cells) == 3:
            # Related-pair map in section 2.5: | ID | bp scope | ap scope |
            related[head] = {"bp_scope": cells[1], "ap_scope": cells[2]}
        elif SOURCE_ID.match(head) and len(cells) == 5:
            links = LINK.findall(cells[2])
            sources[head] = {
                "type": cells[1],
                "name": links[0][0] if links else cells[2],
                "urls": [u for _, u in links],
                "observed": cells[3],
                "scope": cells[4],
            }
        elif RULE_ID.match(head):
            report.error(
                f"{name}:{n}: rule row {head} has {len(cells)} cells (expected 6)"
            )

    for rid, rule in rules.items():
        for ref in rule["sources"]:
            if ref not in sources:
                report.error(
                    f"{name}:{rule['line']}: {rid} references unregistered source {ref}"
                )
        if not rule["sources"]:
            report.warn(f"{name}:{rule['line']}: {rid} cites no sources")

    return {
        "version": version,
        "last_verified_at": metadata_date(
            name, text, "last_verified_at", report
        ),
        "next_light_review_at": metadata_date(
            name, text, "next_light_review_at", report
        ),
        "next_full_review_at": metadata_date(
            name, text, "next_full_review_at", report
        ),
        "rules": rules,
        "related": related,
        "sources": sources,
    }


def parse_bp(path: Path, report: Report) -> dict:
    text = path.read_text(encoding="utf-8")
    name = path.name
    version = check_common(name, text, report)

    rules: dict[str, dict] = {}
    for n, cells in table_rows(text):
        head = strip_code(cells[0]) if cells else ""
        if not RULE_ID.match(head):
            continue
        if len(cells) != 4:
            report.error(
                f"{name}:{n}: rule row {head} has {len(cells)} cells (expected 4)"
            )
            continue
        rid, level, cls = head, strip_code(cells[1]), strip_code(cells[2])
        if rid in rules:
            report.error(f"{name}:{n}: duplicate rule ID {rid}")
            continue
        if level not in BP_LEVELS:
            report.error(f"{name}:{n}: {rid} has unknown level {level!r}")
        if cls not in CLASSES:
            report.error(f"{name}:{n}: {rid} has unknown class {cls!r}")
        rules[rid] = {"level": level, "class": cls, "rule": cells[3], "line": n}
    return {
        "version": version,
        "last_verified_at": metadata_date(
            name, text, "last_verified_at", report
        ),
        "next_light_review_at": metadata_date(
            name, text, "next_light_review_at", report
        ),
        "next_full_review_at": metadata_date(
            name, text, "next_full_review_at", report
        ),
        "rules": rules,
    }


STRENGTH_BP = {"MUST": 2, "MUST_NOT": 2, "SHOULD": 1, "SHOULD_NOT": 1, "MAY": 0}
STRENGTH_AP = {"MUST_NOT": 2, "SHOULD_NOT": 1, "REVIEW_REQUIRED": 1}


def cross_checks(ap: dict, bp: dict, report: Report) -> None:
    ap_ids, bp_ids = set(ap["rules"]), set(bp["rules"])
    for rid in ap["related"]:
        if rid not in ap_ids or rid not in bp_ids:
            report.error(
                f"related-pair map lists {rid}, which is missing from "
                f"{'AP' if rid not in ap_ids else 'BP'}"
            )
    for rid in sorted((ap_ids & bp_ids) - set(ap["related"])):
        s_bp = STRENGTH_BP.get(bp["rules"][rid]["level"])
        s_ap = STRENGTH_AP.get(ap["rules"][rid]["level"])
        if s_bp is not None and s_ap is not None and s_bp != s_ap:
            report.warn(
                f"exact pair {rid} mixes strengths: "
                f"BP {bp['rules'][rid]['level']} vs AP {ap['rules'][rid]['level']}"
            )


def load_json(path: Path, label: str, report: Report) -> dict:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        report.error(f"{label}: cannot load {path}: {exc}")
        return {}
    if not isinstance(value, dict):
        report.error(f"{label}: root must be a JSON object")
        return {}
    return value


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate_metadata(
    ap: dict,
    bp: dict,
    policy: dict,
    catalog: dict,
    as_of: dt.date,
    report: Report,
) -> None:
    scopes = policy.get("scopes")
    if policy.get("schema_version") != 1 or not isinstance(scopes, dict):
        report.error("version policy: expected schema_version 1 and scopes object")
        scopes = {}

    stacks = catalog.get("stacks")
    if catalog.get("schema_version") != 1 or not isinstance(stacks, dict):
        report.error("source catalog: expected schema_version 1 and stacks object")
        stacks = {}

    required_stacks = {
        "php73",
        "php8",
        "nodejs",
        "typescript",
        "a11y",
        "nextjs",
        "react",
        "nestjs",
        "vue",
        "tailwind",
        "postgresql",
        "sqlserver",
    }
    missing_stacks = sorted(required_stacks - set(stacks))
    if missing_stacks:
        report.error(
            "source catalog: missing required stack(s): " + ", ".join(missing_stacks)
        )

    for label, value, expected in (
        ("anti-pattern last_verified_at", ap["last_verified_at"], catalog.get("verified_at")),
        ("best-practice last_verified_at", bp["last_verified_at"], catalog.get("verified_at")),
        (
            "anti-pattern next_light_review_at",
            ap["next_light_review_at"],
            catalog.get("next_light_review_at"),
        ),
        (
            "best-practice next_light_review_at",
            bp["next_light_review_at"],
            catalog.get("next_light_review_at"),
        ),
        (
            "anti-pattern next_full_review_at",
            ap["next_full_review_at"],
            catalog.get("next_full_review_at"),
        ),
        (
            "best-practice next_full_review_at",
            bp["next_full_review_at"],
            catalog.get("next_full_review_at"),
        ),
    ):
        if value != expected:
            report.error(f"{label} {value!r} does not match catalog {expected!r}")

    for label, raw_deadline in (
        ("version policy", policy.get("next_review_at")),
        ("source catalog", catalog.get("next_light_review_at")),
    ):
        try:
            deadline = dt.date.fromisoformat(raw_deadline)
        except (TypeError, ValueError):
            report.error(f"{label}: invalid review deadline {raw_deadline!r}")
            continue
        if as_of > deadline:
            report.error(
                f"{label}: stale as of {as_of}; review deadline was {deadline}"
            )

    for scope, spec in scopes.items():
        if not isinstance(spec, dict):
            report.error(f"version policy: scope {scope} must be an object")
            continue
        if not spec.get("constraint") or not spec.get("version_source"):
            report.error(
                f"version policy: scope {scope} needs constraint and version_source"
            )
        source_id = spec.get("version_source")
        if source_id and source_id not in ap["sources"]:
            report.error(
                f"version policy: scope {scope} references unknown source {source_id}"
            )
        if scope in stacks:
            approved = stacks[scope].get("approved_range")
            if approved != spec.get("constraint"):
                report.error(
                    f"{scope}: catalog approved_range {approved!r} does not match "
                    f"policy constraint {spec.get('constraint')!r}"
                )
            if stacks[scope].get("approved_majors") != spec.get("allowed_majors"):
                if "approved_majors" in stacks[scope] or "allowed_majors" in spec:
                    report.error(
                        f"{scope}: catalog approved_majors "
                        f"{stacks[scope].get('approved_majors')!r} does not match "
                        f"policy allowed_majors {spec.get('allowed_majors')!r}"
                    )

    for scope, stack in stacks.items():
        standards = stack.get("house_standards", [])
        if not isinstance(standards, list):
            report.error(
                f"source catalog: {scope}.house_standards must be a list"
            )
            continue
        for standard in standards:
            if not isinstance(standard, dict):
                report.error(
                    f"source catalog: {scope} house standard must be an object"
                )
                continue
            standard_id = standard.get("id")
            if standard_id not in ap["sources"]:
                report.error(
                    f"source catalog: {scope} house standard references "
                    f"unknown source {standard_id!r}"
                )
            relative = standard.get("path")
            if not isinstance(relative, str) or not relative:
                report.error(
                    f"source catalog: {scope} house standard needs a path"
                )
                continue
            candidate = (REFERENCE_DIR / relative).resolve()
            try:
                candidate.relative_to(REFERENCE_DIR.resolve())
            except ValueError:
                report.error(
                    f"source catalog: {scope} house standard escapes references: "
                    f"{relative}"
                )
                continue
            if not candidate.is_file():
                report.error(
                    f"source catalog: {scope} house standard is missing: {relative}"
                )
                continue
            text = candidate.read_text(encoding="utf-8")
            version_match = re.search(
                r'^standard_version:\s*"(\d+\.\d+\.\d+)"',
                text,
                re.MULTILINE,
            )
            actual_version = version_match.group(1) if version_match else None
            if actual_version != standard.get("version"):
                report.error(
                    f"source catalog: {scope} house standard version "
                    f"{standard.get('version')!r} does not match file "
                    f"{actual_version!r}"
                )
            actual_hash = sha256(candidate)
            if actual_hash != standard.get("sha256"):
                report.error(
                    f"source catalog: {scope} house standard hash is stale; "
                    f"expected {actual_hash}"
                )
            try:
                standard_deadline = dt.date.fromisoformat(
                    standard.get("next_review_at")
                )
            except (TypeError, ValueError):
                report.error(
                    f"source catalog: {scope} house standard has invalid "
                    "next_review_at"
                )
            else:
                if as_of > standard_deadline:
                    report.error(
                        f"source catalog: {scope} house standard is stale as of "
                        f"{as_of}; review deadline was {standard_deadline}"
                    )

    for rid, rule in ap["rules"].items():
        scope = scope_of(rid)
        if scope == "other":
            report.error(f"{rid}: rule prefix has no registered scope")
        if (
            rule["class"] == "version-bound"
            and scope != "global"
            and scope not in scopes
        ):
            report.error(
                f"{rid}: version-bound scope {scope} is absent from version policy"
            )


def applicability_for(
    rid: str, ap_rule: dict | None, bp_rule: dict | None, policy: dict
) -> dict:
    scope = scope_of(rid)
    version_bound = any(
        rule and rule.get("class") == "version-bound"
        for rule in (ap_rule, bp_rule)
    )
    result: dict = {"scope": scope, "version_bound": version_bound}
    if not version_bound:
        return result
    if scope == "global":
        result["requires_resolved_stack"] = True
        return result

    spec = policy["scopes"][scope]
    result.update(
        {
            "constraint": spec.get("rule_constraints", {}).get(
                rid, spec["constraint"]
            ),
            "version_source": spec["version_source"],
            "requires_exact_version": True,
        }
    )
    return result


def build_payload(
    ap: dict,
    bp: dict,
    policy: dict,
    catalog: dict,
    ap_path: Path,
    bp_path: Path,
    policy_path: Path,
    catalog_path: Path,
) -> dict:
    all_ids = sorted(set(ap["rules"]) | set(bp["rules"]))
    entries = []
    for rid in sorted(
        all_ids, key=lambda r: (SCOPE_ORDER.index(scope_of(r)), r)
    ):
        in_ap, in_bp = rid in ap["rules"], rid in bp["rules"]
        if in_ap and in_bp:
            pairing = "related" if rid in ap["related"] else "exact"
        else:
            pairing = "ap_only" if in_ap else "bp_only"
        ap_rule = ap["rules"].get(rid)
        bp_rule = bp["rules"].get(rid)
        entry: dict = {
            "id": rid,
            "scope": scope_of(rid),
            "pairing": pairing,
            "applicability": applicability_for(rid, ap_rule, bp_rule, policy),
        }
        if in_bp:
            r = bp_rule
            entry["bp"] = {"level": r["level"], "class": r["class"], "rule": r["rule"]}
        if in_ap:
            r = ap_rule
            entry["ap"] = {
                "level": r["level"],
                "class": r["class"],
                "pattern": r["pattern"],
                "remediation": r["remediation"],
                "sources": r["sources"],
            }
        entries.append(entry)

    return {
        "schema_version": 2,
        "packs": {
            "best_practices": {
                "file": bp_path.name,
                "version": bp["version"],
                "sha256": sha256(bp_path),
            },
            "anti_pattern_guardrails": {
                "file": ap_path.name,
                "version": ap["version"],
                "sha256": sha256(ap_path),
            },
        },
        "version_policy": {
            "file": policy_path.name,
            "version": policy["policy_version"],
            "verified_at": policy["verified_at"],
            "next_review_at": policy["next_review_at"],
            "sha256": sha256(policy_path),
            "scopes": policy["scopes"],
        },
        "source_catalog": {
            "file": catalog_path.name,
            "version": catalog["catalog_version"],
            "verified_at": catalog["verified_at"],
            "next_light_review_at": catalog["next_light_review_at"],
            "next_full_review_at": catalog["next_full_review_at"],
            "sha256": sha256(catalog_path),
            "house_standards": {
                scope: stack.get("house_standards", [])
                for scope, stack in catalog["stacks"].items()
                if stack.get("house_standards")
            },
        },
        "counts": {
            "rules_total": len(entries),
            "exact_pairs": sum(e["pairing"] == "exact" for e in entries),
            "related_pairs": sum(e["pairing"] == "related" for e in entries),
            "ap_only": sum(e["pairing"] == "ap_only" for e in entries),
            "bp_only": sum(e["pairing"] == "bp_only" for e in entries),
        },
        "related_pair_map": ap["related"],
        "rules": entries,
        "sources": ap["sources"],
    }


def render(payload: dict) -> str:
    return json.dumps(payload, ensure_ascii=False, indent=2) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--ap", type=Path, default=DEFAULT_AP)
    parser.add_argument("--bp", type=Path, default=DEFAULT_BP)
    parser.add_argument("--version-policy", type=Path, default=DEFAULT_POLICY)
    parser.add_argument("--source-catalog", type=Path, default=DEFAULT_CATALOG)
    parser.add_argument("-o", "--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument(
        "--check",
        action="store_true",
        help="validate and fail if generated JSON differs; do not write",
    )
    parser.add_argument(
        "--as-of", default=dt.date.today().isoformat(), help="ISO freshness date"
    )
    args = parser.parse_args()

    report = Report()
    ap = parse_ap(args.ap, report)
    bp = parse_bp(args.bp, report)
    policy = load_json(args.version_policy, "version policy", report)
    catalog = load_json(args.source_catalog, "source catalog", report)
    cross_checks(ap, bp, report)
    try:
        as_of = dt.date.fromisoformat(args.as_of)
    except ValueError:
        report.error("--as-of must be an ISO date")
        as_of = dt.date.today()
    if policy and catalog:
        validate_metadata(ap, bp, policy, catalog, as_of, report)

    for w in report.warnings:
        print(f"WARN  {w}")
    for e in report.errors:
        print(f"ERROR {e}")
    if report.errors:
        print(f"\nFAILED: {len(report.errors)} error(s); {args.out} not written.")
        return 1

    payload = build_payload(
        ap,
        bp,
        policy,
        catalog,
        args.ap,
        args.bp,
        args.version_policy,
        args.source_catalog,
    )
    generated = render(payload)
    if args.check:
        try:
            current = args.out.read_text(encoding="utf-8")
        except OSError as exc:
            print(f"ERROR generated rules missing: {exc}")
            return 1
        if current != generated:
            print(
                f"ERROR {args.out} is stale. Run {Path(__file__).name} "
                "without --check and review the semantic diff."
            )
            return 1
        verb = "verified"
    else:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(generated, encoding="utf-8")
        verb = "wrote"

    c = payload["counts"]
    print(
        f"OK: {verb} {args.out} — {c['rules_total']} rules "
        f"(exact {c['exact_pairs']}, related {c['related_pairs']}, "
        f"ap_only {c['ap_only']}, bp_only {c['bp_only']}); "
        f"{len(report.warnings)} warning(s)."
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
