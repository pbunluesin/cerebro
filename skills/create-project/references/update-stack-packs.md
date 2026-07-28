# Updating Versioned Stack Packs

## Goal

Keep Good/Bad rules aligned with supported technology versions without letting
an automated refresh silently change project policy.

## Fast path

1. Check deadlines and the current observed/approved state:

   ```bash
   python3 skills/create-project/scripts/check_stack_pack_status.py
   ```

2. Inspect only affected current official release/support docs, initializer
   help, migration notes, and focused official examples.
3. Update `official-sources.json` `observed_ref`, `observation_status`,
   `observation_note`, and evidence first. Use `reviewed-deferred` when an
   upstream release was inspected but intentionally not approved. Do not move
   `approved_ref` yet.
4. Classify the upstream diff:

   - metadata/link/patch clarification: patch pack release;
   - additive Good/Bad rule or new supported minor: minor pack release;
   - changed level, meaning, scope, version applicability, precedence, removal,
     or generator schema: major pack release plus migration note.

5. Update the affected rows in `stack-packs/best-practices.md` and
   `stack-packs/anti-patterns.md`, then update
   `stack-version-policy.json` only when version applicability changed.
   For a SQL Server local-reference change, update the relevant standard/guide,
   its affected SQL templates/rules, and its `official-sources.json`
   version/hash entry in the same reviewed patch. Compute every changed content
   hash explicitly:

   ```bash
   shasum -a 256 skills/create-project/references/stack-packs/sqlserver-house-standard.md
   shasum -a 256 skills/create-project/references/stack-packs/sqlserver-object-house-standard.md
   shasum -a 256 skills/create-project/references/stack-packs/sqlserver-engineering-practices.md
   ```

   The extractor fails closed and prints the expected hash when the registry
   was not updated.
6. After semantic review, move `approved_ref`, bump catalog/pack versions, and
   update all review dates in the same patch.
7. Regenerate and verify:

   ```bash
   python3 skills/create-project/scripts/extract_stack_rules.py
   python3 skills/create-project/scripts/extract_stack_rules.py --check
   python3 scripts/validate_all.py
   python3 -m unittest discover -s tests -p 'test_*.py'
   ```

8. Review the `rules.json` semantic diff, especially rule IDs, levels, classes,
   applicability constraints, source hashes, and removals. Commit only after
   Dissent and normal commit approval.

## Safety rules

- A source scan may update `observed_ref`; it must never auto-promote
  `approved_ref`.
- Never reuse an ID for changed meaning. Add a new ID or publish a major
  migration.
- Never broaden a version range solely to make selection pass.
- Never delete a rule without a migration note and downstream impact review.
- Treat DBHS-01 and DBHS-02 as user-authorized project policy, not universal
  Microsoft best practice. Treat DBEP-01 as Microsoft-derived guidance rather
  than a team naming contract. Never infer naming for uncovered objects.
- A changed local standard/guide file must change its registered content hash.
  Semantic changes also require the appropriate standard/guide, pack, and
  catalog version bump plus explicit regeneration review.
- When a deadline expires, selection fails closed. Refresh the evidence; do not
  disable the freshness check.
- Existing projects do not receive semantic rule changes automatically.
  Regenerate their `.cerebro/stack-profile.json`, review the diff, and approve
  exceptions or migrations explicitly.
