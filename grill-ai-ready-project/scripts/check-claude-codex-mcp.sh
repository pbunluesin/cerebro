#!/usr/bin/env bash
set -euo pipefail

echo "== Claude Code binary =="
command -v claude || true
claude --version 2>/dev/null || true

echo
echo "== Claude auth =="
claude auth status --text 2>/dev/null || claude auth status 2>/dev/null || true

echo
echo "== Claude MCP list =="
claude mcp list 2>/dev/null || true

echo
echo "== MCP config scope scan =="
python3 - <<'PY_CHECK_SCRIPT'
import json, pathlib
p = pathlib.Path.home() / '.claude.json'
if not p.exists():
    print('NO ~/.claude.json found')
else:
    try:
        data = json.loads(p.read_text())
    except Exception as e:
        print('Could not parse ~/.claude.json:', e)
    else:
        top = data.get('mcpServers') or {}
        print('User/global mcpServers:', list(top.keys()) or '(none)')
        projects = data.get('projects') or {}
        found = False
        for path, cfg in projects.items():
            servers = (cfg or {}).get('mcpServers') or {}
            if servers:
                found = True
                print(f'Local/project-path MCP: {path} -> {list(servers.keys())}')
        if not found:
            print('Local/project-path MCP: (none found)')
PY_CHECK_SCRIPT

echo
echo "== Current directory project-shared .mcp.json =="
if [ -f .mcp.json ]; then
  echo "FOUND $(pwd)/.mcp.json"
  python3 - <<'PY_MCP_JSON'
import json, pathlib
p=pathlib.Path('.mcp.json')
try:
    data=json.loads(p.read_text())
    print('Project .mcp.json servers:', list((data.get('mcpServers') or {}).keys()))
except Exception as e:
    print('Could not parse .mcp.json:', e)
PY_MCP_JSON
else
  echo "No .mcp.json in current directory"
fi

echo
echo "== Codex CLI =="
command -v codex || true
codex --version 2>/dev/null || true

echo
echo "== Suggested next check inside Claude Code =="
echo "Run: /mcp"
echo "If Codex appears there with tools, MCP-first review can be used."
