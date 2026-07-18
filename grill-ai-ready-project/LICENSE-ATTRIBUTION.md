# License and Attribution

This skill package, `grill-ai-ready-project`, is an original adaptation created for AI-ready project bootstrapping and requirement grilling workflows.

It is inspired by concepts from Matt Pocock's `mattpocock/skills` repository, especially:

- `skills/productivity/grill-me/SKILL.md`
- `skills/engineering/grill-with-docs/SKILL.md`

The upstream repository is published under the MIT License.

## Upstream attribution

MIT License

Copyright (c) 2026 Matt Pocock

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## Notes

This package does not attempt to replace the upstream skills. It adapts the requirement-grilling and docs-aware ideas into a project bootstrapping workflow that generates a standardized AI-ready documentation structure.

## Bundled upstream reference files

This package includes local reference copies of the upstream `grill-me`, `grill-with-docs`, `CONTEXT-FORMAT.md`, and `ADR-FORMAT.md` files for auditability and context preservation. These references are provided under the upstream MIT License above.


## Local v1.2 Additions

The v1.2 package adds original subagent templates and delegation checklists while retaining upstream attribution and reference material from the v1.1 package.


## Additional Inspiration: chaseai-yt/grill-me-codex

Version 1.3 adapts the cross-model adversarial plan-review concept from `chaseai-yt/grill-me-codex`:

- source: https://github.com/chaseai-yt/grill-me-codex
- concept: Claude locks `PLAN.md`, Codex reviews read-only, Claude revises, review rounds are logged, user signs off before code

This package does not vendor Chase AI's skill files directly; it adapts the workflow concept into an MCP-first `grill-ai-ready-project` process. Preserve this attribution when distributing substantial derivatives.
