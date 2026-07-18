from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILLS = ROOT / "skills"


class SkillCompositionTests(unittest.TestCase):
    def read_skill(self, name: str) -> str:
        return (SKILLS / name / "SKILL.md").read_text(encoding="utf-8")

    def test_create_project_composes_domain_and_design_skills(self) -> None:
        text = self.read_skill("create-project")
        self.assertIn("[domain-modeling](../domain-modeling/SKILL.md)", text)
        self.assertIn("[codebase-design](../codebase-design/SKILL.md)", text)
        self.assertIn("Do not force deep-module machinery", text)

    def test_domain_modeling_preserves_cerebro_document_contract(self) -> None:
        text = self.read_skill("domain-modeling")
        self.assertIn("docs/CONTEXT.md", text)
        self.assertIn("docs/CONTEXT_MAP.md", text)
        self.assertIn("docs/decisions/", text)
        self.assertNotIn("docs/adr/", text)

    def test_architecture_improvement_separates_discovery_design_and_mutation(self) -> None:
        text = self.read_skill("improve-codebase-architecture")
        self.assertIn("Present before designing", text)
        self.assertIn("Ask which candidate", text)
        self.assertIn("Stop before implementation", text)
        self.assertIn("No candidate is a valid outcome", text)
        self.assertIn("architecture-report.md", text)


if __name__ == "__main__":
    unittest.main()
