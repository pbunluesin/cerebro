from __future__ import annotations

import json
import hashlib
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXTRACT = (
    ROOT / "skills" / "create-project" / "scripts" / "extract_stack_rules.py"
)
SELECT = (
    ROOT / "skills" / "create-project" / "scripts" / "select_stack_rules.py"
)
STATUS = (
    ROOT
    / "skills"
    / "create-project"
    / "scripts"
    / "check_stack_pack_status.py"
)
RULES = (
    ROOT
    / "skills"
    / "create-project"
    / "references"
    / "stack-packs"
    / "rules.json"
)
CATALOG = (
    ROOT
    / "skills"
    / "create-project"
    / "references"
    / "official-sources.json"
)
HOUSE_STANDARD = (
    ROOT
    / "skills"
    / "create-project"
    / "references"
    / "stack-packs"
    / "sqlserver-house-standard.md"
)
OBJECT_HOUSE_STANDARD = (
    ROOT
    / "skills"
    / "create-project"
    / "references"
    / "stack-packs"
    / "sqlserver-object-house-standard.md"
)
ENGINEERING_GUIDE = (
    ROOT
    / "skills"
    / "create-project"
    / "references"
    / "stack-packs"
    / "sqlserver-engineering-practices.md"
)


class StackPackTests(unittest.TestCase):
    def run_tool(
        self, script: Path, *arguments: str
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(script), *arguments],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )

    def test_generated_rules_are_current_and_cover_primary_stacks(self) -> None:
        result = self.run_tool(EXTRACT, "--check", "--as-of", "2026-07-28")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(RULES.read_text(encoding="utf-8"))
        self.assertEqual(payload["schema_version"], 2)
        scopes = {rule["scope"] for rule in payload["rules"]}
        self.assertTrue(
            {"nodejs", "react", "nestjs", "sqlserver"}.issubset(scopes)
        )
        extractor_text = EXTRACT.read_text(encoding="utf-8")
        self.assertNotIn("import yaml", extractor_text)
        self.assertNotIn("from yaml", extractor_text)
        house_ids = {
            rule["id"]
            for rule in payload["rules"]
            if rule["id"].startswith("MSSQL-HOUSE-")
        }
        self.assertEqual(
            house_ids,
            {
                "MSSQL-HOUSE-DELETE-001",
                "MSSQL-HOUSE-ERROR-001",
                "MSSQL-HOUSE-EXCEPTION-001",
                "MSSQL-HOUSE-FORMAT-001",
                "MSSQL-HOUSE-GET-001",
                "MSSQL-HOUSE-HEADER-001",
                "MSSQL-HOUSE-INSERT-001",
                "MSSQL-HOUSE-ISOLATION-001",
                "MSSQL-HOUSE-NAME-001",
                "MSSQL-HOUSE-NESTED-001",
                "MSSQL-HOUSE-NOMAGIC-001",
                "MSSQL-HOUSE-OBJECT-EXCEPTION-001",
                "MSSQL-HOUSE-OBJECT-HEADER-001",
                "MSSQL-HOUSE-OBJECT-NAME-001",
                "MSSQL-HOUSE-OBJECT-VERIFY-001",
                "MSSQL-HOUSE-PARAM-001",
                "MSSQL-HOUSE-PLAN-001",
                "MSSQL-HOUSE-FUNCTION-001",
                "MSSQL-HOUSE-FUNCTION-PLAN-001",
                "MSSQL-HOUSE-TRIGGER-OBJECT-001",
                "MSSQL-HOUSE-TRIGGER-VERSION-001",
                "MSSQL-HOUSE-TYPE-OBJECT-001",
                "MSSQL-HOUSE-TYPE-VERSION-001",
                "MSSQL-HOUSE-UPDATE-001",
                "MSSQL-HOUSE-VERIFY-001",
                "MSSQL-HOUSE-WRITE-001",
            },
        )
        self.assertTrue(
            all(
                rule["pairing"] == "exact"
                for rule in payload["rules"]
                if rule["id"] in house_ids
            )
        )
        rule_ids = {rule["id"] for rule in payload["rules"]}
        self.assertTrue(
            {
                "MSSQL-DESIGN-NORMAL-001",
                "MSSQL-INDEX-EVIDENCE-001",
                "MSSQL-INDEX-MAINT-001",
                "MSSQL-OPT-QUERYSTORE-001",
                "MSSQL-OPT-STATS-001",
            }.issubset(rule_ids)
        )

    def test_sqlserver_local_references_are_versioned_and_hash_pinned(self) -> None:
        import hashlib

        catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
        standards = catalog["stacks"]["sqlserver"]["house_standards"]
        self.assertEqual(
            [standard["id"] for standard in standards],
            ["DBHS-01", "DBHS-02"],
        )
        standard = standards[0]
        self.assertEqual(
            standard["sha256"],
            hashlib.sha256(HOUSE_STANDARD.read_bytes()).hexdigest(),
        )
        object_standard = standards[1]
        self.assertEqual(object_standard["version"], "1.0.0")
        self.assertEqual(object_standard["scope"], "functions-triggers-types")
        self.assertEqual(
            object_standard["sha256"],
            hashlib.sha256(OBJECT_HOUSE_STANDARD.read_bytes()).hexdigest(),
        )
        guides = catalog["stacks"]["sqlserver"]["engineering_guides"]
        self.assertEqual([guide["id"] for guide in guides], ["DBEP-01"])
        self.assertEqual(
            guides[0]["sha256"],
            hashlib.sha256(ENGINEERING_GUIDE.read_bytes()).hexdigest(),
        )
        text = HOUSE_STANDARD.read_text(encoding="utf-8")
        self.assertIn('authority: user-team-policy', text)
        self.assertIn('standard_version: "1.0.0"', text)
        self.assertIn("universal Microsoft or industry best practice", text)
        object_text = OBJECT_HOUSE_STANDARD.read_text(encoding="utf-8")
        self.assertIn("Author", object_text)
        self.assertIn("functions, triggers, and", object_text)
        guide_text = ENGINEERING_GUIDE.read_text(encoding="utf-8")
        self.assertIn("normalization", guide_text)
        self.assertIn("Index maintenance", guide_text)

    def test_extractor_fails_closed_on_house_standard_hash_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
            catalog["stacks"]["sqlserver"]["house_standards"][0][
                "sha256"
            ] = "0" * 64
            changed_catalog = Path(temporary) / "official-sources.json"
            changed_catalog.write_text(
                json.dumps(catalog, indent=2) + "\n", encoding="utf-8"
            )
            result = self.run_tool(
                EXTRACT,
                "--source-catalog",
                str(changed_catalog),
                "--check",
                "--as-of",
                "2026-07-28",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("house standard hash is stale", result.stdout)

    def test_extractor_fails_closed_on_engineering_guide_hash_drift(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
            catalog["stacks"]["sqlserver"]["engineering_guides"][0][
                "sha256"
            ] = "0" * 64
            changed_catalog = Path(temporary) / "official-sources.json"
            changed_catalog.write_text(
                json.dumps(catalog, indent=2) + "\n", encoding="utf-8"
            )
            result = self.run_tool(
                EXTRACT,
                "--source-catalog",
                str(changed_catalog),
                "--check",
                "--as-of",
                "2026-07-28",
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("engineering guide hash is stale", result.stdout)

    def test_selector_emits_compact_approved_version_and_path_profile(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "stack-profile.json"
            result = self.run_tool(
                SELECT,
                "--stack",
                "nodejs@24.18.0",
                "--stack",
                "nextjs@16.1.0",
                "--stack",
                "react@19.2.0",
                "--stack",
                "typescript@6.0.3",
                "--stack",
                "a11y@2.2",
                "--path",
                "nextjs=apps/web/**",
                "--source-ref",
                "nodejs=node@v24.18.0",
                "--source-ref",
                "nextjs=create-next-app@16.1.0",
                "--source-ref",
                "react=react@19.2.0",
                "--source-ref",
                "typescript=typescript@6.0.3",
                "--source-ref",
                "a11y=WCAG-2.2@2023-10-05",
                "--approval-record",
                "requirements-final:2026-07-28:test-owner",
                "--as-of",
                "2026-07-28",
                "--out",
                str(output),
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            profile = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(profile["status"], "approved")
            self.assertGreater(len(profile["selected_rule_ids"]), 0)
            self.assertEqual(
                [binding["id"] for binding in profile["rule_bindings"]],
                profile["selected_rule_ids"],
            )
            self.assertNotIn("rules", profile)
            self.assertRegex(
                profile["pack"]["source_catalog_sha256"], r"^[0-9a-f]{64}$"
            )
            self.assertRegex(
                profile["pack"]["version_policy_sha256"], r"^[0-9a-f]{64}$"
            )
            react = next(
                stack for stack in profile["stacks"] if stack["scope"] == "react"
            )
            self.assertEqual(react["paths"], ["apps/web/**"])

    def test_selector_rejects_missing_included_version(self) -> None:
        result = self.run_tool(
            SELECT,
            "--stack",
            "nextjs@16.1.0",
            "--path",
            "nextjs=apps/web/**",
            "--source-ref",
            "nextjs=create-next-app@16.1.0",
            "--as-of",
            "2026-07-28",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("exact version required for included scope", result.stderr)

    def test_selector_records_sqlserver_house_standard(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "stack-profile.json"
            result = self.run_tool(
                SELECT,
                "--stack",
                "sqlserver@16.0",
                "--path",
                "sqlserver=database/**",
                "--source-ref",
                "sqlserver=sql-server-ver16@2026-07-28",
                "--approval-record",
                "requirements-final:2026-07-28:test-owner",
                "--as-of",
                "2026-07-28",
                "--out",
                str(output),
            )
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            profile = json.loads(output.read_text(encoding="utf-8"))
            reference = next(
                item
                for item in profile["official_references"]
                if item["scope"] == "sqlserver"
            )
            self.assertEqual(
                [item["id"] for item in reference["house_standards"]],
                ["DBHS-01", "DBHS-02"],
            )
            self.assertEqual(
                [item["id"] for item in reference["engineering_guides"]],
                ["DBEP-01"],
            )
            for item in (
                reference["house_standards"]
                + reference["engineering_guides"]
            ):
                self.assertEqual(item["version"], "1.0.0")
                self.assertRegex(item["sha256"], r"^[0-9a-f]{64}$")
            self.assertIn(
                "MSSQL-HOUSE-GET-001", profile["selected_rule_ids"]
            )
            self.assertIn(
                "MSSQL-HOUSE-FUNCTION-001", profile["selected_rule_ids"]
            )
            self.assertIn(
                "MSSQL-INDEX-EVIDENCE-001", profile["selected_rule_ids"]
            )

    def test_selector_rejects_unsupported_version(self) -> None:
        result = self.run_tool(
            SELECT,
            "--stack",
            "sqlserver@15.0",
            "--path",
            "sqlserver=database/**",
            "--source-ref",
            "sqlserver=sql-server-ver15@2026-07-28",
            "--as-of",
            "2026-07-28",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("outside approved range", result.stderr)

    def test_selector_rejects_default_branch_source_ref(self) -> None:
        result = self.run_tool(
            SELECT,
            "--stack",
            "sqlserver@16.0",
            "--path",
            "sqlserver=database/**",
            "--source-ref",
            "sqlserver=main",
            "--as-of",
            "2026-07-28",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("not a stable exact ref", result.stderr)

    def test_selector_rejects_non_lts_node_major_inside_numeric_range(self) -> None:
        result = self.run_tool(
            SELECT,
            "--stack",
            "nodejs@23.1.0",
            "--path",
            "nodejs=apps/**",
            "--source-ref",
            "nodejs=node@v23.1.0",
            "--as-of",
            "2026-07-28",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("allowed majors are 22, 24", result.stderr)

    def test_selector_rejects_fabricated_ref_path_and_approval(self) -> None:
        cases = (
            (
                (
                    "--stack", "nodejs@24.18.0",
                    "--path", "nodejs=src/**",
                    "--source-ref", "nodejs=banana1",
                ),
                "does not match the approved format",
            ),
            (
                (
                    "--stack", "nodejs@24.18.0",
                    "--path", "nodejs=../../outside/**",
                    "--source-ref", "nodejs=node@v24.18.0",
                ),
                "normalized project-relative glob",
            ),
            (
                (
                    "--stack", "nodejs@24.18.0",
                    "--path", "nodejs=/outside/**",
                    "--source-ref", "nodejs=node@v24.18.0",
                ),
                "normalized project-relative glob",
            ),
            (
                (
                    "--stack", "nodejs@24.18.0",
                    "--path", r"nodejs=src\\**",
                    "--source-ref", "nodejs=node@v24.18.0",
                ),
                "normalized project-relative glob",
            ),
            (
                (
                    "--stack", "nodejs@24.18.0",
                    "--path", "nodejs=src/**",
                    "--source-ref", "nodejs=node@v24.18.0",
                    "--approval-record", "x",
                ),
                "requirements-final:<YYYY-MM-DD>:<approver>",
            ),
        )
        for arguments, expected in cases:
            with self.subTest(arguments=arguments):
                result = self.run_tool(
                    SELECT,
                    *arguments,
                    "--as-of", "2026-07-28",
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(expected, result.stderr)

    def test_selector_rejects_unreviewed_custom_bundle_for_approval(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            custom_catalog = Path(temporary) / "official-sources.json"
            custom_catalog.write_bytes(CATALOG.read_bytes())
            result = self.run_tool(
                SELECT,
                "--stack", "nodejs@24.18.0",
                "--path", "nodejs=src/**",
                "--source-ref", "nodejs=node@v24.18.0",
                "--approval-record",
                "requirements-final:2026-07-28:test-owner",
                "--as-of", "2026-07-28",
                "--source-catalog", str(custom_catalog),
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "approved profiles require the installed canonical bundle",
                result.stderr,
            )

            catalog = json.loads(custom_catalog.read_text(encoding="utf-8"))
            catalog["catalog_version"] = "999.0.0"
            custom_catalog.write_text(
                json.dumps(catalog, indent=2) + "\n",
                encoding="utf-8",
            )
            result = self.run_tool(
                SELECT,
                "--stack", "nodejs@24.18.0",
                "--path", "nodejs=src/**",
                "--source-ref", "nodejs=node@v24.18.0",
                "--as-of", "2026-07-28",
                "--source-catalog", str(custom_catalog),
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(
                "source catalog content does not match rules.json",
                result.stderr,
            )

    def test_full_review_due_blocks_status_and_selection(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            temporary_root = Path(temporary)
            catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
            catalog["next_full_review_at"] = "2026-07-27"
            custom_catalog = temporary_root / "official-sources.json"
            custom_catalog.write_text(
                json.dumps(catalog, indent=2) + "\n",
                encoding="utf-8",
            )
            status = self.run_tool(
                STATUS,
                "--as-of", "2026-07-28",
                "--source-catalog", str(custom_catalog),
                "--json",
            )
            self.assertEqual(status.returncode, 1, status.stderr)
            self.assertEqual(
                json.loads(status.stdout)["status"],
                "full-review-due",
            )
            extraction = self.run_tool(
                EXTRACT,
                "--source-catalog", str(custom_catalog),
                "--check",
                "--as-of", "2026-07-28",
            )
            self.assertNotEqual(extraction.returncode, 0)
            self.assertIn(
                "official source catalog full semantic review: stale",
                extraction.stdout,
            )

            rules = json.loads(RULES.read_text(encoding="utf-8"))
            rules["source_catalog"]["sha256"] = hashlib.sha256(
                custom_catalog.read_bytes()
            ).hexdigest()
            custom_rules = temporary_root / "rules.json"
            custom_rules.write_text(
                json.dumps(rules, indent=2) + "\n",
                encoding="utf-8",
            )
            selected = self.run_tool(
                SELECT,
                "--stack", "nodejs@24.18.0",
                "--path", "nodejs=src/**",
                "--source-ref", "nodejs=node@v24.18.0",
                "--as-of", "2026-07-28",
                "--rules", str(custom_rules),
                "--source-catalog", str(custom_catalog),
            )
            self.assertNotEqual(selected.returncode, 0)
            self.assertIn(
                "full semantic review is stale",
                selected.stderr,
            )

    def test_selector_fails_closed_after_source_deadline(self) -> None:
        result = self.run_tool(
            SELECT,
            "--stack",
            "sqlserver@16.0",
            "--path",
            "sqlserver=database/**",
            "--source-ref",
            "sqlserver=sql-server-ver16@2026-07-28",
            "--as-of",
            "2026-08-29",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("is stale", result.stderr)

    def test_status_distinguishes_deferred_and_compatibility_reviews(self) -> None:
        result = self.run_tool(
            STATUS, "--as-of", "2026-07-28", "--json"
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        actions = {
            stack["scope"]: stack["next_action"] for stack in payload["stacks"]
        }
        self.assertEqual(actions["nodejs"], "reviewed-deferred")
        self.assertEqual(
            actions["typescript"], "project-compatibility-review-required"
        )
        self.assertEqual(
            payload["house_standards"],
            [
                {
                    "scope": "sqlserver",
                    "id": "DBHS-01",
                    "version": "1.0.0",
                    "status": "approved",
                    "sha256": json.loads(
                        CATALOG.read_text(encoding="utf-8")
                    )["stacks"]["sqlserver"]["house_standards"][0]["sha256"],
                    "next_review_at": "2026-10-28",
                    "next_action": "current",
                },
                {
                    "scope": "sqlserver",
                    "id": "DBHS-02",
                    "version": "1.0.0",
                    "status": "approved",
                    "sha256": json.loads(
                        CATALOG.read_text(encoding="utf-8")
                    )["stacks"]["sqlserver"]["house_standards"][1]["sha256"],
                    "next_review_at": "2026-10-28",
                    "next_action": "current",
                },
            ],
        )
        self.assertEqual(
            payload["engineering_guides"],
            [
                {
                    "scope": "sqlserver",
                    "id": "DBEP-01",
                    "version": "1.0.0",
                    "status": "approved",
                    "sha256": json.loads(
                        CATALOG.read_text(encoding="utf-8")
                    )["stacks"]["sqlserver"]["engineering_guides"][0][
                        "sha256"
                    ],
                    "next_review_at": "2026-10-28",
                    "next_action": "current",
                }
            ],
        )


if __name__ == "__main__":
    unittest.main()
