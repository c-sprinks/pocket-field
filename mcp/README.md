# pocket-field-mcp

Python MCP server that wraps pocket-field firmware as Claude tools over USB serial. Part of the [pocket-field](../README.md) project.

## Prerequisites

- Python 3.11+
- A Cardputter ADV running pocket-field firmware (see [../firmware/README.md](../firmware/README.md))
- USB-C cable

## Install

```bash
cd mcp
uv venv
source .venv/bin/activate
uv pip install -e .
```

## Register with Claude

### Claude Desktop

Add to `~/.config/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "pocket-field": {
      "command": "pocket-field-mcp",
      "args": ["--serial-port", "/dev/ttyACM0"]
    }
  }
}
```

### Claude Code

Add to `.claude/mcp.json` in your project:

```json
{
  "servers": {
    "pocket-field": {
      "command": "pocket-field-mcp",
      "args": ["--serial-port", "/dev/ttyACM0"]
    }
  }
}
```

## Run tests (mocked serial, no hardware required)

```bash
pytest
ruff check .
mypy src/
```

## Status

Phase 0 skeleton. No MCP tools wired yet. See [../ROADMAP.md](../ROADMAP.md).
