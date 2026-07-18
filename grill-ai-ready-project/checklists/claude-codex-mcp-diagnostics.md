# Claude / Codex / MCP Diagnostics

Use this checklist to determine whether Codex is available globally through Claude Code MCP, project-local MCP, Codex CLI, or not configured.

## Claude Code

```bash
which claude
claude --version
claude auth status --text
claude mcp list
```

Inside Claude Code, run:

```txt
/mcp
```

## MCP Scope Checks

```bash
python3 - <<'PY_CHECK_MCP'
import json, pathlib
p=pathlib.Path.home()/'.claude.json'
if not p.exists():
    print('NO ~/.claude.json')
else:
    data=json.loads(p.read_text())
    print('Top-level mcpServers:', list((data.get('mcpServers') or {}).keys()))
    print('Project entries with MCP:')
    for path,cfg in (data.get('projects') or {}).items():
        servers=(cfg.get('mcpServers') or {})
        if servers:
            print('-', path, list(servers.keys()))
PY_CHECK_MCP

find . -maxdepth 2 -name '.mcp.json' -print -exec cat {} \;
```

Interpretation:

- `~/.claude.json` top-level `mcpServers` = user/global scope.
- `~/.claude.json` under `projects.<path>.mcpServers` = local to that project path.
- `<project>/.mcp.json` = project scope, shareable in repo, approval required.

## Codex CLI

```bash
which codex
codex --version
codex --help | head -40
codex exec --help | head -80
```

Do not print secrets or tokens.
