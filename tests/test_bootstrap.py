from __future__ import annotations

import subprocess
import sys
import tempfile
import unittest
import hashlib
import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BOOTSTRAP = ROOT / "skills" / "create-project" / "scripts" / "bootstrap_project.py"
VALIDATE = ROOT / "skills" / "create-project" / "scripts" / "validate_project.py"
SELECT = (
    ROOT / "skills" / "create-project" / "scripts" / "select_stack_rules.py"
)


class BootstrapProjectTests(unittest.TestCase):
    def run_tool(self, script: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(script), *arguments],
            text=True,
            capture_output=True,
            check=False,
        )

    def resolve_draft_markdown(self, target: Path) -> None:
        for markdown in target.rglob("*.md"):
            text = markdown.read_text(encoding="utf-8")
            text = re.sub(r"\bTBD\b", "Resolved", text)
            markdown.write_text(text, encoding="utf-8")
        requirements = target / "docs/REQUIREMENTS.md"
        requirements.write_text(
            requirements.read_text(encoding="utf-8").replace(
                "- Blocking gaps: Resolved",
                "- Blocking gaps: None",
            ),
            encoding="utf-8",
        )
        state = target / "PROJECT_STATE.md"
        state.write_text(
            state.read_text(encoding="utf-8").replace(
                "- Phase: `DISCOVERY`",
                "- Phase: `IMPLEMENTATION_READY`",
            ),
            encoding="utf-8",
        )

    def create_final_ready_project(self, parent: Path) -> Path:
        stack_profile = parent / "approved-stack-profile.json"
        selected = self.run_tool(
            SELECT,
            "--stack", "nodejs@24.18.0",
            "--path", "nodejs=src/**",
            "--source-ref", "nodejs=node@v24.18.0",
            "--approval-record", "requirements-final:2026-07-28:test-owner",
            "--as-of", "2026-07-28",
            "--out", str(stack_profile),
        )
        self.assertEqual(selected.returncode, 0, selected.stderr)

        target = parent / "ready"
        created = self.run_tool(
            BOOTSTRAP,
            "--target", str(target),
            "--name", "Ready",
            "--profile", "minimal",
            "--agents", "codex",
            "--stack-profile", str(stack_profile),
        )
        self.assertEqual(created.returncode, 0, created.stderr)

        self.resolve_draft_markdown(target)
        return target

    def test_dry_run_does_not_create_target(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "new-project"
            result = self.run_tool(
                BOOTSTRAP,
                "--target", str(target),
                "--name", "New Project",
                "--profile", "minimal",
                "--agents", "both",
                "--dry-run",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertFalse(target.exists())
            self.assertIn("CREATE   AGENTS.md", result.stdout)

    def test_minimal_both_creates_shared_and_claude_guidance(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "minimal"
            result = self.run_tool(
                BOOTSTRAP,
                "--target", str(target),
                "--name", "Minimal App",
                "--profile", "minimal",
                "--agents", "both",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((target / "AGENTS.md").is_file())
            self.assertTrue((target / "CLAUDE.md").is_file())
            self.assertTrue((target / ".claude/rules/guardrails.md").is_file())
            self.assertTrue((target / ".cerebro/project.json").is_file())
            self.assertTrue((target / ".cerebro/stack-profile.json").is_file())
            self.assertFalse((target / ".claude/agents").exists())
            self.assertFalse((target / ".claude/rules/docs-routing.md").exists())
            self.assertFalse((target / "PROCESS.md").exists())
            self.assertFalse((target / "docs/DATA.md").exists())
            self.assertFalse((target / "database/templates/sqlserver").exists())

            agents_text = (target / "AGENTS.md").read_text(encoding="utf-8")
            for marker in (
                "NO MAGIC",
                "VERIFY BEFORE DONE",
                "DISSENT",
                "SCOPE DRIFT DETECTION",
                "WORKSPACE BOUNDARY",
                "Claude Code",
                "Codex",
            ):
                self.assertIn(marker, agents_text)
            claude_text = (target / "CLAUDE.md").read_text(encoding="utf-8")
            self.assertIn("independent Codex CLI review", claude_text)

            validation = self.run_tool(
                VALIDATE,
                "--target", str(target),
                "--profile", "minimal",
                "--agents", "both",
                "--allow-draft",
            )
            self.assertEqual(validation.returncode, 0, validation.stderr)

    def test_standard_codex_adds_selected_features_only(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "standard"
            result = self.run_tool(
                BOOTSTRAP,
                "--target", str(target),
                "--name", "Service",
                "--profile", "standard",
                "--agents", "codex",
                "--features", "api,data",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((target / "docs/API.md").is_file())
            self.assertTrue((target / "docs/DATA.md").is_file())
            self.assertFalse((target / "CLAUDE.md").exists())
            self.assertFalse((target / ".claude").exists())
            context = (target / "docs/CONTEXT.md").read_text(encoding="utf-8")
            self.assertIn("canonical domain term", context)
            self.assertIn("CONTEXT_MAP.md", context)
            architecture = (target / "docs/ARCHITECTURE.md").read_text(encoding="utf-8")
            self.assertIn("Modules, interfaces, and responsibilities", architecture)
            self.assertIn("Seam/adapter rationale", architecture)
            self.assertIn("Approved references", architecture)
            decision = (target / "docs/decisions/0000-template.md").read_text(encoding="utf-8")
            self.assertIn("Decision and rationale", decision)
            self.assertIn("genuine alternatives existed", decision)

    def test_critical_profile_has_release_and_threat_controls(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "critical"
            result = self.run_tool(
                BOOTSTRAP,
                "--target", str(target),
                "--name", "Critical System",
                "--profile", "critical",
                "--agents", "both",
                "--features", "api,migration",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((target / "docs/DATA.md").is_file())
            self.assertTrue((target / "docs/MIGRATION.md").is_file())
            self.assertTrue((target / "docs/quality/THREAT_MODEL.md").is_file())
            self.assertTrue((target / "docs/quality/RELEASE_CHECKLIST.md").is_file())
            self.assertTrue((target / ".claude/agents/cerebro-reviewer.md").is_file())
            self.assertTrue((target / ".claude/agents/cerebro-fixer.md").is_file())
            review_contract = (target / "docs/quality/REVIEW_CONTRACT.md").read_text(encoding="utf-8")
            self.assertIn("latest currently approved Codex model", review_contract)
            self.assertIn("No silent fallback", review_contract)

    def test_sqlserver_stack_adds_team_standard_templates_only_when_selected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "sqlserver"
            result = self.run_tool(
                BOOTSTRAP,
                "--target", str(target),
                "--name", "SQL Server Service",
                "--profile", "standard",
                "--agents", "both",
                "--stacks", "sqlserver",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertTrue((target / "docs/DATA.md").is_file())

            template_root = target / "database/templates/sqlserver"
            expected = {
                "function-inline-table.sql",
                "function-scalar.sql",
                "stored-procedure-get.sql",
                "stored-procedure-insert.sql",
                "stored-procedure-update.sql",
                "stored-procedure-delete.sql",
                "stored-procedure-write-transaction.sql",
                "trigger-dml.sql",
                "type-table.sql",
            }
            self.assertEqual(
                {path.name for path in template_root.glob("*.sql")},
                expected,
            )

            get_sql = (template_root / "stored-procedure-get.sql").read_text(
                encoding="utf-8"
            )
            self.assertIn(
                "SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;", get_sql
            )
            self.assertNotIn("BEGIN TRAN;", get_sql)
            self.assertNotIn("```", get_sql)
            self.assertNotIn("# template", get_sql)
            self.assertIn("CREATE PROC ", get_sql)
            self.assertTrue(get_sql.rstrip().endswith("GO"))

            write_procedures = {
                "stored-procedure-insert.sql",
                "stored-procedure-update.sql",
                "stored-procedure-delete.sql",
                "stored-procedure-write-transaction.sql",
            }
            for name in write_procedures:
                sql = (template_root / name).read_text(encoding="utf-8")
                for marker in (
                    "SET XACT_ABORT ON;",
                    "BEGIN TRY",
                    "BEGIN TRAN;",
                    "COMMIT TRAN;",
                    "XACT_STATE()",
                    "ROLLBACK TRAN;",
                    "THROW;",
                    "EXEC_TEST",
                ):
                    self.assertIn(marker, sql, f"{name}: {marker}")
                self.assertNotIn("```", sql)
                self.assertNotIn("# template", sql)

            object_markers = {
                "function-inline-table.sql": (
                    "Author",
                    "SELECT_TEST",
                    "CREATE FUNCTION",
                    "RETURNS TABLE",
                ),
                "function-scalar.sql": (
                    "Author",
                    "SELECT_TEST",
                    "CREATE FUNCTION",
                    "RETURNS",
                ),
                "trigger-dml.sql": (
                    "Author",
                    "DML_TEST",
                    "CREATE TRIGGER",
                    "inserted",
                    "deleted",
                ),
                "type-table.sql": (
                    "Author",
                    "DECLARE_TEST",
                    "CREATE TYPE",
                    "AS TABLE",
                ),
            }
            for name, markers in object_markers.items():
                sql = (template_root / name).read_text(encoding="utf-8")
                for marker in markers:
                    self.assertIn(marker, sql, f"{name}: {marker}")
                self.assertNotIn("```", sql)
                self.assertNotIn("# template", sql)
                self.assertTrue(sql.rstrip().endswith("GO"))

            insert_sql = (
                template_root / "stored-procedure-insert.sql"
            ).read_text(encoding="utf-8")
            self.assertIn("IF NOT EXISTS", insert_sql)
            self.assertIn("RAISERROR", insert_sql)

            validation = self.run_tool(
                VALIDATE,
                "--target", str(target),
                "--profile", "standard",
                "--agents", "both",
                "--stacks", "sqlserver",
                "--allow-draft",
            )
            self.assertEqual(validation.returncode, 0, validation.stderr)

    def test_unknown_scaffold_stack_fails_closed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "unknown"
            result = self.run_tool(
                BOOTSTRAP,
                "--target", str(target),
                "--name", "Unknown",
                "--profile", "minimal",
                "--agents", "codex",
                "--stacks", "mysql",
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("unknown scaffold stacks: mysql", result.stderr)
            self.assertFalse(target.exists())

    def test_conflict_requires_merge_or_force(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "existing"
            target.mkdir()
            original = "existing readme\n"
            (target / "README.md").write_text(original, encoding="utf-8")
            result = self.run_tool(
                BOOTSTRAP,
                "--target", str(target),
                "--name", "Existing",
                "--profile", "minimal",
                "--agents", "codex",
            )
            self.assertEqual(result.returncode, 3)
            self.assertEqual((target / "README.md").read_text(encoding="utf-8"), original)

            merged = self.run_tool(
                BOOTSTRAP,
                "--target", str(target),
                "--name", "Existing",
                "--profile", "minimal",
                "--agents", "codex",
                "--merge",
            )
            self.assertEqual(merged.returncode, 0, merged.stderr)
            self.assertEqual((target / "README.md").read_text(encoding="utf-8"), original)
            self.assertTrue((target / "AGENTS.md").is_file())

    def test_scaffold_rejects_symlinked_parent_before_any_write(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            target = parent / "target"
            outside = parent / "outside"
            target.mkdir()
            outside.mkdir()
            (target / "docs").symlink_to(outside, target_is_directory=True)

            result = self.run_tool(
                BOOTSTRAP,
                "--target", str(target),
                "--name", "Escaping",
                "--profile", "minimal",
                "--agents", "codex",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("symlink destination or ancestor", result.stderr)
            self.assertEqual(list(outside.iterdir()), [])
            self.assertEqual(
                sorted(path.name for path in target.iterdir()),
                ["docs"],
            )

    def test_scaffold_rejects_symlink_destination_and_nested_ancestor(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            for relative in ("README.md", ".cerebro"):
                with self.subTest(relative=relative):
                    target = parent / relative.replace("/", "-")
                    outside = parent / f"outside-{target.name}"
                    target.mkdir()
                    outside.mkdir()
                    if relative == "README.md":
                        outside_file = outside / "README.md"
                        outside_file.write_text("outside\n", encoding="utf-8")
                        (target / relative).symlink_to(outside_file)
                    else:
                        (target / relative).symlink_to(
                            outside,
                            target_is_directory=True,
                        )

                    result = self.run_tool(
                        BOOTSTRAP,
                        "--target", str(target),
                        "--name", "Symlink",
                        "--profile", "minimal",
                        "--agents", "codex",
                    )
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(
                        "symlink destination or ancestor",
                        result.stderr,
                    )
                    if relative == "README.md":
                        self.assertEqual(
                            outside_file.read_text(encoding="utf-8"),
                            "outside\n",
                        )
                    else:
                        self.assertEqual(list(outside.iterdir()), [])

    def test_manifest_is_canonical_and_caller_mismatch_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "critical"
            created = self.run_tool(
                BOOTSTRAP,
                "--target", str(target),
                "--name", "Critical",
                "--profile", "critical",
                "--agents", "both",
                "--features", "api,migration",
            )
            self.assertEqual(created.returncode, 0, created.stderr)
            manifest = json.loads(
                (target / ".cerebro/project.json").read_text(encoding="utf-8")
            )
            self.assertEqual(manifest["scaffold"]["profile"], "critical")
            self.assertEqual(manifest["scaffold"]["agents"], "both")
            self.assertIn(
                "docs/quality/THREAT_MODEL.md",
                manifest["scaffold"]["required_files"],
            )

            validation = self.run_tool(
                VALIDATE,
                "--target", str(target),
                "--profile", "minimal",
                "--agents", "codex",
                "--allow-draft",
            )
            self.assertNotEqual(validation.returncode, 0)
            self.assertIn(
                "--profile conflicts with .cerebro/project.json",
                validation.stderr,
            )
            self.assertIn(
                "--agents conflicts with .cerebro/project.json",
                validation.stderr,
            )

    def test_validator_rejects_required_symlink_and_external_local_link(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            target = parent / "draft"
            created = self.run_tool(
                BOOTSTRAP,
                "--target", str(target),
                "--name", "Draft",
                "--profile", "minimal",
                "--agents", "codex",
            )
            self.assertEqual(created.returncode, 0, created.stderr)

            agents = target / "AGENTS.md"
            agents.unlink()
            agents.symlink_to(parent / "outside-AGENTS.md")
            validation = self.run_tool(
                VALIDATE,
                "--target", str(target),
                "--allow-draft",
            )
            self.assertNotEqual(validation.returncode, 0)
            self.assertIn(
                "refusing symlink destination or ancestor: AGENTS.md",
                validation.stderr,
            )

            agents.unlink()
            agents.write_text(
                (
                    ROOT
                    / "skills/create-project/assets/project/AGENTS.md.tmpl"
                ).read_text(encoding="utf-8"),
                encoding="utf-8",
            )
            readme = target / "README.md"
            readme.write_text(
                readme.read_text(encoding="utf-8")
                + "\n[Outside](../outside.md)\n",
                encoding="utf-8",
            )
            validation = self.run_tool(
                VALIDATE,
                "--target", str(target),
                "--allow-draft",
            )
            self.assertNotEqual(validation.returncode, 0)
            self.assertIn("local link escapes project root", validation.stderr)

    def test_validator_ignores_dependency_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "draft"
            created = self.run_tool(
                BOOTSTRAP,
                "--target", str(target),
                "--name", "Draft",
                "--profile", "minimal",
                "--agents", "codex",
            )
            self.assertEqual(created.returncode, 0, created.stderr)
            dependency = target / "node_modules/dependency/README.md"
            dependency.parent.mkdir(parents=True)
            dependency.write_text(
                "{{UNRESOLVED}} [TODO: dependency-owned]\n",
                encoding="utf-8",
            )
            validation = self.run_tool(
                VALIDATE,
                "--target", str(target),
                "--allow-draft",
            )
            self.assertEqual(validation.returncode, 0, validation.stderr)

    def test_complete_generated_project_passes_final_validation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = self.create_final_ready_project(Path(temporary))
            validation = self.run_tool(
                VALIDATE,
                "--target", str(target),
            )
            self.assertEqual(validation.returncode, 0, validation.stderr)
            self.assertIn("VALID: profile=minimal", validation.stdout)

    def test_sqlserver_final_profile_requires_matching_scaffold_assets(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            parent = Path(temporary)
            stack_profile = parent / "sqlserver-stack-profile.json"
            selected = self.run_tool(
                SELECT,
                "--stack", "sqlserver@16.0",
                "--path", "sqlserver=database/**",
                "--source-ref",
                "sqlserver=sql-server-ver16@2026-07-28",
                "--approval-record",
                "requirements-final:2026-07-28:test-owner",
                "--as-of", "2026-07-28",
                "--out", str(stack_profile),
            )
            self.assertEqual(selected.returncode, 0, selected.stderr)

            matching = parent / "matching"
            created = self.run_tool(
                BOOTSTRAP,
                "--target", str(matching),
                "--name", "SQL Matching",
                "--profile", "minimal",
                "--agents", "codex",
                "--stacks", "sqlserver",
                "--stack-profile", str(stack_profile),
            )
            self.assertEqual(created.returncode, 0, created.stderr)
            self.resolve_draft_markdown(matching)
            validation = self.run_tool(
                VALIDATE,
                "--target", str(matching),
            )
            self.assertEqual(validation.returncode, 0, validation.stderr)

            missing = parent / "missing"
            created = self.run_tool(
                BOOTSTRAP,
                "--target", str(missing),
                "--name", "SQL Missing",
                "--profile", "minimal",
                "--agents", "codex",
                "--stack-profile", str(stack_profile),
            )
            self.assertEqual(created.returncode, 0, created.stderr)
            self.resolve_draft_markdown(missing)
            validation = self.run_tool(
                VALIDATE,
                "--target", str(missing),
            )
            self.assertNotEqual(validation.returncode, 0)
            self.assertIn(
                "scaffold.stacks must match stack-specific assets",
                validation.stderr,
            )

    def test_final_validation_rejects_tampered_rule_provenance(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = self.create_final_ready_project(Path(temporary))
            stack_path = target / ".cerebro/stack-profile.json"
            stack_profile = json.loads(stack_path.read_text(encoding="utf-8"))
            stack_profile["selected_rule_ids"].append("FAKE-001")
            stack_profile["rule_bindings"].append(
                {
                    "id": "FAKE-001",
                    "scope": "nodejs",
                    "paths": ["../../outside/**"],
                }
            )
            stack_path.write_text(
                json.dumps(stack_profile, indent=2) + "\n",
                encoding="utf-8",
            )
            manifest_path = target / ".cerebro/project.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["stack_profile"]["sha256"] = hashlib.sha256(
                stack_path.read_bytes()
            ).hexdigest()
            manifest_path.write_text(
                json.dumps(manifest, indent=2) + "\n",
                encoding="utf-8",
            )

            validation = self.run_tool(
                VALIDATE,
                "--target", str(target),
            )
            self.assertNotEqual(validation.returncode, 0)
            self.assertIn(
                "cannot be reproduced from canonical rules",
                validation.stderr,
            )

    def test_final_validation_rejects_valid_rule_on_wrong_path(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = self.create_final_ready_project(Path(temporary))
            stack_path = target / ".cerebro/stack-profile.json"
            stack_profile = json.loads(stack_path.read_text(encoding="utf-8"))
            stack_profile["rule_bindings"][0]["paths"] = ["other/**"]
            stack_path.write_text(
                json.dumps(stack_profile, indent=2) + "\n",
                encoding="utf-8",
            )
            manifest_path = target / ".cerebro/project.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["stack_profile"]["sha256"] = hashlib.sha256(
                stack_path.read_bytes()
            ).hexdigest()
            manifest_path.write_text(
                json.dumps(manifest, indent=2) + "\n",
                encoding="utf-8",
            )

            validation = self.run_tool(VALIDATE, "--target", str(target))
            self.assertNotEqual(validation.returncode, 0)
            self.assertIn(
                "cannot be reproduced from canonical rules",
                validation.stderr,
            )

    def test_validator_rejects_tampered_required_file_manifest(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "draft"
            created = self.run_tool(
                BOOTSTRAP,
                "--target", str(target),
                "--name", "Draft",
                "--profile", "minimal",
                "--agents", "codex",
            )
            self.assertEqual(created.returncode, 0, created.stderr)
            manifest_path = target / ".cerebro/project.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["scaffold"]["required_files"].remove("docs/PRODUCT.md")
            manifest_path.write_text(
                json.dumps(manifest, indent=2) + "\n",
                encoding="utf-8",
            )

            validation = self.run_tool(
                VALIDATE,
                "--target", str(target),
                "--allow-draft",
            )
            self.assertNotEqual(validation.returncode, 0)
            self.assertIn(
                "required_files do not match the canonical scaffold plan",
                validation.stderr,
            )

    def test_blocking_gap_parser_accepts_none_and_rejects_real_gap(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = self.create_final_ready_project(Path(temporary))
            requirements = target / "docs/REQUIREMENTS.md"
            text = requirements.read_text(encoding="utf-8")
            requirements.write_text(
                text.replace(
                    "- Blocking gaps: None",
                    "  - Blocking gaps:   nOnE  ",
                ),
                encoding="utf-8",
            )
            accepted = self.run_tool(VALIDATE, "--target", str(target))
            self.assertEqual(accepted.returncode, 0, accepted.stderr)

            requirements.write_text(
                requirements.read_text(encoding="utf-8").replace(
                    "Blocking gaps:   nOnE",
                    "Blocking gaps: Missing production credentials",
                ),
                encoding="utf-8",
            )
            rejected = self.run_tool(VALIDATE, "--target", str(target))
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn(
                "still contains a blocking gap marker",
                rejected.stderr,
            )

    def test_final_validation_rejects_unresolved_template_content(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "draft"
            created = self.run_tool(
                BOOTSTRAP,
                "--target", str(target),
                "--name", "Draft",
                "--profile", "minimal",
                "--agents", "codex",
            )
            self.assertEqual(created.returncode, 0, created.stderr)
            validation = self.run_tool(
                VALIDATE,
                "--target", str(target),
                "--profile", "minimal",
                "--agents", "codex",
            )
            self.assertNotEqual(validation.returncode, 0)
            self.assertIn(
                "does not declare an exact IMPLEMENTATION_READY phase",
                validation.stderr,
            )


if __name__ == "__main__":
    unittest.main()
