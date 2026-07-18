# Optional Tooling Integrations

## Contents

1. Safety policy
2. Detection workflow
3. RTK
4. Caveman
5. Test isolation
6. Additional tools
7. Verification record

## Safety policy

Tool setup is optional and occurs only after project requirements and profile selection. Never let a convenience tool become an undocumented project dependency.

Before installation or configuration:

1. Identify the official project and documentation.
2. Detect existing binaries, versions, hooks, rules, and conflicting packages.
3. Explain installation scope: project, user, or system.
4. Explain files and settings that will change.
5. Explain telemetry, network, and secret implications when documented.
6. Request explicit approval.
7. Prefer a reversible command and record an uninstall path.

Never pipe a remote script into a shell without explicit approval. Never reuse a similarly named package without verifying its origin.

## Detection workflow

Use read-only checks first:

```bash
command -v <tool>
<tool> --version
```

When the plugin checkout is available, use its detector to produce a consistent report:

```bash
python3 scripts/check_tooling.py --target <project>
```

Inspect only the documented configuration paths. Do not assume absence because one path is missing.

Classify each integration:

- `READY`: supported version and intended agent integration verified.
- `BINARY_ONLY`: binary exists but agent integration is absent.
- `OUTDATED`: installed version is below the required capability.
- `CONFLICT`: wrong package, duplicate hook, or incompatible configuration detected.
- `ABSENT`: no verified installation.
- `UNKNOWN`: tool identity or official setup source is unresolved.

## RTK

RTK refers to `rtk-ai/rtk`, a command-output proxy for AI coding agents. Verify identity before setup; another package may also use the `rtk` name.

Read-only checks:

```bash
command -v rtk
rtk --version
rtk gain
rtk init --show
rtk init --codex --dry-run
```

Offer these documented integration scopes after approval:

```bash
# Claude Code, user-global hook
rtk init --global

# Codex, current project guidance
rtk init --codex

# Codex, user-global guidance
rtk init --global --codex
```

For a project that targets both agents, do not assume one command configures both. Detect each integration separately. Prefer project-scoped Codex guidance and ask before changing global Claude settings.

After configuration:

```bash
rtk init --show
rtk telemetry status
```

Record the telemetry choice without changing it implicitly. RTK must degrade safely; if filtered output hides diagnostic detail, use its documented raw-output or disable mechanism for that command.

## Caveman

Caveman refers specifically to [JuliusBrussee/caveman](https://github.com/JuliusBrussee/caveman). It is a response-compression skill/plugin; it changes communication style and can add Claude hooks, but it is not a correctness or review engine.

Read-only checks:

```bash
claude plugin list --json
claude plugin marketplace list --json
claude plugin details caveman@caveman
```

Also inspect the documented active-mode flag without printing unrelated settings:

```bash
test -f "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/.caveman-active"
```

After explicit approval, prefer the native per-agent installation paths over a remote script pipe:

```bash
# Claude Code, user scope
claude plugin marketplace add JuliusBrussee/caveman
claude plugin install caveman@caveman

# Codex skill integration
npx skills add JuliusBrussee/caveman -a codex
```

Both commands download content and change user-scoped agent configuration. Normally classify that as R1 because reversal is possible but the blast radius spans projects; still obtain explicit approval because user-global installation is a separate authority boundary. Before updating an existing installation, compare the installed snapshot with the current upstream release and explain changed hooks/rules. Do not assume `installed` means `current`.

Verify Claude installation with `claude plugin details caveman@caveman`, a new session, `/caveman`, and the active-mode flag. Verify Codex through the installed skill inventory and an explicit `/caveman` invocation in a new session. Record the exact installed snapshot/version.

## Test isolation

RTK and Caveman do not execute during Python unit tests, manifest validation, or static file checks. They do affect live Claude Code sessions:

- RTK can rewrite supported shell commands and compress command output through its hook.
- Caveman loads prompt context/hooks and changes response style when enabled.

Run both modes when behavior matters:

```bash
# Baseline: skip user hooks/plugins and load only the plugin under test.
claude --bare --plugin-dir <cerebro-path>

# Integration: normal new Claude session with RTK and Caveman enabled.
claude --plugin-dir <cerebro-path>
```

Do not compare prose snapshots, token counts, or hook-sensitive command traces across these modes as though they were equivalent. Record which mode produced each result. Static validation does not prove live integration behavior.

## Additional tools

For an ambiguous nickname or new tool:

1. Search the current repository for a pinned source or configuration.
2. Ask for the official name or repository URL if no authoritative reference exists.
3. Do not create a placeholder installer that guesses the package.
4. Once identified, document detection, supported versions, scopes, changed files, approval boundary, verification, and uninstall steps in this reference.

Use the same policy for linters, LSP servers, MCP servers, package managers, container runtimes, and agent plugins. Install only tools justified by the confirmed stack and workflow.

## Verification record

Write a concise entry in `PROJECT_STATE.md` after approved setup:

```text
Tool:
Version:
Scope:
Integration:
Files/settings changed:
Verification:
Telemetry/privacy choice:
Rollback/uninstall:
```

Do not place machine-specific absolute paths or secrets in committed project state.
