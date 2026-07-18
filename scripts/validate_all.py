#!/usr/bin/env python3
"""Validate Cerebro's manifests, skills, references, assets, and Python scripts."""

from __future__ import annotations

import ast
import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"
LINK_RE = re.compile(r"\[[^\]]+\]\(([^)]+)\)")
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SAFETY_MARKERS = (
    "NO MAGIC",
    "VERIFY BEFORE DONE",
    "DISSENT",
    "SCOPE DRIFT DETECTION",
    "WORKSPACE BOUNDARY",
    "`R0`",
    "`R1`",
    "`R2`",
)
REQUIRED_SKILLS = {
    "audit-project",
    "codebase-design",
    "create-project",
    "domain-modeling",
    "fix-findings",
    "handoff",
    "improve-codebase-architecture",
    "review-code",
    "review-plan",
}
SKILL_CONTRACT_MARKERS = {
    "codebase-design": ("deep-module-design.md", "interface", "seam", "locality", "at least two"),
    "create-project": ("domain-modeling", "codebase-design", "ARCHITECTURE_READY"),
    "domain-modeling": ("domain-modeling-standard.md", "docs/CONTEXT.md", "docs/CONTEXT_MAP.md", "all three gates"),
    "improve-codebase-architecture": (
        "architecture-improvement-standard.md",
        "Present before designing",
        "Ask which candidate",
        "No candidate is a valid outcome",
    ),
}


def parse_frontmatter(path: Path) -> tuple[dict[str, str], str]:
    text = path.read_text(encoding="utf-8")
    if not text.startswith("---\n"):
        raise ValueError("missing YAML frontmatter")
    parts = text.split("---\n", 2)
    if len(parts) != 3:
        raise ValueError("frontmatter is not closed")
    data: dict[str, str] = {}
    for raw_line in parts[1].splitlines():
        if not raw_line.strip():
            continue
        if ":" not in raw_line:
            raise ValueError(f"invalid frontmatter line: {raw_line}")
        key, value = raw_line.split(":", 1)
        data[key.strip()] = value.strip()
    return data, parts[2]


def validate_manifest(path: Path, expected_name: str) -> list[str]:
    errors: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{path.relative_to(ROOT)}: {exc}"]
    if data.get("name") != expected_name:
        errors.append(f"{path.relative_to(ROOT)}: name must be {expected_name}")
    if not re.fullmatch(r"\d+\.\d+\.\d+(?:[-+][0-9A-Za-z.-]+)?", str(data.get("version", ""))):
        errors.append(f"{path.relative_to(ROOT)}: invalid semantic version")
    if not data.get("description"):
        errors.append(f"{path.relative_to(ROOT)}: missing description")
    if "TODO" in path.read_text(encoding="utf-8"):
        errors.append(f"{path.relative_to(ROOT)}: contains TODO")
    return errors


def validate_marketplace(path: Path, expected_name: str) -> list[str]:
    errors: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{path.relative_to(ROOT)}: {exc}"]
    if data.get("name") != expected_name:
        errors.append(f"{path.relative_to(ROOT)}: marketplace name must be {expected_name}")
    plugins = data.get("plugins")
    if not isinstance(plugins, list) or len(plugins) != 1:
        errors.append(f"{path.relative_to(ROOT)}: expected exactly one plugin entry")
    elif plugins[0].get("name") != expected_name or not plugins[0].get("source"):
        errors.append(f"{path.relative_to(ROOT)}: invalid plugin name or source")
    return errors


def validate_document_links(path: Path) -> list[str]:
    errors: list[str] = []
    for raw_link in LINK_RE.findall(path.read_text(encoding="utf-8")):
        target = raw_link.split("#", 1)[0].strip().strip("<>")
        if not target or re.match(r"^[a-z]+://", target) or target.startswith("mailto:"):
            continue
        if not (path.parent / target).resolve().exists():
            errors.append(f"{path.relative_to(ROOT)}: missing linked document {raw_link}")
    return errors


def validate_skill(skill_dir: Path) -> list[str]:
    errors: list[str] = []
    skill_file = skill_dir / "SKILL.md"
    try:
        frontmatter, body = parse_frontmatter(skill_file)
    except (OSError, ValueError) as exc:
        return [f"{skill_file.relative_to(ROOT)}: {exc}"]

    expected = skill_dir.name
    if frontmatter.get("name") != expected:
        errors.append(f"{skill_file.relative_to(ROOT)}: name must match folder {expected}")
    if not NAME_RE.fullmatch(expected) or len(expected) > 64:
        errors.append(f"{skill_file.relative_to(ROOT)}: invalid skill name")
    if not frontmatter.get("description") or "TODO" in frontmatter.get("description", ""):
        errors.append(f"{skill_file.relative_to(ROOT)}: incomplete description")
    if set(frontmatter) != {"name", "description"}:
        errors.append(f"{skill_file.relative_to(ROOT)}: frontmatter may contain only name and description")
    if len(body.splitlines()) > 500:
        errors.append(f"{skill_file.relative_to(ROOT)}: body exceeds 500 lines")
    if "[TODO" in body:
        errors.append(f"{skill_file.relative_to(ROOT)}: contains scaffold TODO")

    for link in LINK_RE.findall(body):
        target = link.split("#", 1)[0]
        if target and not re.match(r"^[a-z]+://", target) and not (skill_dir / target).exists():
            errors.append(f"{skill_file.relative_to(ROOT)}: missing linked resource {link}")

    metadata = skill_dir / "agents" / "openai.yaml"
    if not metadata.is_file():
        errors.append(f"{skill_dir.relative_to(ROOT)}: missing agents/openai.yaml")
    else:
        yaml_text = metadata.read_text(encoding="utf-8")
        if f"${expected}" not in yaml_text:
            errors.append(f"{metadata.relative_to(ROOT)}: default_prompt must mention ${expected}")
        if "TODO" in yaml_text:
            errors.append(f"{metadata.relative_to(ROOT)}: contains TODO")
    return errors


def validate_python(path: Path) -> list[str]:
    try:
        ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        return []
    except (OSError, SyntaxError) as exc:
        return [f"{path.relative_to(ROOT)}: {exc}"]


def validate_safety_surface(path: Path, markers: tuple[str, ...] = SAFETY_MARKERS) -> list[str]:
    text = path.read_text(encoding="utf-8")
    return [f"{path.relative_to(ROOT)}: missing safety marker {marker}" for marker in markers if marker not in text]


def main() -> int:
    errors: list[str] = []
    errors.extend(validate_manifest(ROOT / ".codex-plugin" / "plugin.json", "cerebro"))
    errors.extend(validate_manifest(ROOT / ".claude-plugin" / "plugin.json", "cerebro"))
    errors.extend(validate_marketplace(ROOT / ".agents" / "plugins" / "marketplace.json", "cerebro"))
    errors.extend(validate_marketplace(ROOT / ".claude-plugin" / "marketplace.json", "cerebro"))

    try:
        claude_plugin = json.loads((ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        claude_marketplace = json.loads((ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
        marketplace_version = claude_marketplace["plugins"][0].get("version")
        if marketplace_version != claude_plugin.get("version"):
            errors.append(".claude-plugin/marketplace.json: plugin version differs from plugin.json")
    except (OSError, json.JSONDecodeError, KeyError, IndexError, TypeError):
        # The manifest-specific checks above already report the malformed file.
        pass

    for forbidden in ROOT.rglob("PROCESS.md"):
        if ".git" not in forbidden.parts:
            errors.append(f"forbidden process surface: {forbidden.relative_to(ROOT)}")

    root_documents = list(ROOT.glob("*.md")) + list((ROOT / "docs").rglob("*.md"))
    for document in sorted(root_documents):
        errors.extend(validate_document_links(document))

    errors.extend(validate_safety_surface(ROOT / "AGENTS.md"))
    errors.extend(validate_safety_surface(ROOT / "skills" / "create-project" / "assets" / "project" / "AGENTS.md.tmpl"))
    errors.extend(validate_safety_surface(ROOT / "skills" / "create-project" / "references" / "safety-contract.md"))
    errors.extend(
        validate_safety_surface(
            ROOT / "skills" / "create-project" / "assets" / "project" / ".claude" / "rules" / "guardrails.md.tmpl",
            ("NO MAGIC", "VERIFY BEFORE DONE", "DISSENT", "SCOPE DRIFT", "R0:", "R1:", "R2:", "WORK_ROOT"),
        )
    )

    tooling_text = (ROOT / "skills" / "create-project" / "scripts" / "check_tooling.py").read_text(encoding="utf-8")
    for marker in ("caveman@caveman", "https://github.com/JuliusBrussee/caveman"):
        if marker not in tooling_text:
            errors.append(f"check_tooling.py: missing Caveman marker {marker}")

    skill_dirs = sorted(path for path in SKILLS.iterdir() if path.is_dir())
    if not skill_dirs:
        errors.append("skills/: no skill directories found")
    skill_names = {path.name for path in skill_dirs}
    for missing in sorted(REQUIRED_SKILLS - skill_names):
        errors.append(f"skills/: missing required skill {missing}")
    for skill_dir in skill_dirs:
        errors.extend(validate_skill(skill_dir))
        skill_text = (skill_dir / "SKILL.md").read_text(encoding="utf-8")
        for marker in SKILL_CONTRACT_MARKERS.get(skill_dir.name, ()):
            if marker not in skill_text:
                errors.append(f"{skill_dir.name}/SKILL.md: missing workflow marker {marker}")

    for path in sorted(ROOT.rglob("*.py")):
        if ".git" not in path.parts:
            errors.extend(validate_python(path))

    sys.path.insert(0, str(SKILLS / "create-project" / "scripts"))
    try:
        from bootstrap_project import asset_for, planned_files

        combinations = (
            ("minimal", "codex", set()),
            ("minimal", "both", set()),
            ("standard", "both", {"api", "data"}),
            ("critical", "both", {"api", "migration"}),
        )
        for profile, agents, features in combinations:
            for relative_path in planned_files(profile, agents, features):
                if not asset_for(relative_path).is_file():
                    errors.append(f"missing asset for {profile}/{agents}: {relative_path}.tmpl")
    except (ImportError, ValueError) as exc:
        errors.append(f"bootstrap asset validation failed: {exc}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print(f"INVALID: {len(errors)} error(s)")
        return 1
    print(f"VALID: manifests=2 marketplaces=2 skills={len(skill_dirs)} python=ok assets=ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
