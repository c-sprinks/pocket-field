# pocket-field

**LLM-native firmware + MCP server for the M5Stack Cardputter ADV.**

Drive your Cardputter from Claude (or any MCP client) over USB serial. Ask in natural language — "read this access card, tell me the facility code and card number" — and get a real answer back from real hardware.

> **Status: pre-release / in development.** Nothing ships yet. Target first release: v0.1.0 with NFC card read over MCP. See [ROADMAP](ROADMAP.md).

---

## What this is

Two components in one monorepo:

1. **`firmware/`** — C++/Arduino firmware for the M5Stack Cardputter ADV (ESP32-S3), forked from [Evil-Cardputer ADV](https://github.com/7h30th3r0n3/Evil-M5Project). Exposes a versioned text protocol over USB serial that an LLM can reliably parse.
2. **`mcp/`** — Python MCP ([Model Context Protocol](https://modelcontextprotocol.io/)) server that wraps the firmware's serial CLI as Claude tools. Runs on any Linux host (laptop, Raspberry Pi) that can USB-connect to the Cardputter.

The two talk over a **versioned text protocol** so they can evolve independently.

## Who this is for

Field technicians, pentesters, and hobbyists who already own a Cardputter ADV and want to drive it from an LLM instead of a menu. Not a replacement for Bruce, Porkchop, or Evil-Cardputter — a different philosophy: narrow scope, machine-readable, automation-first.

## Authorized use

This tool interacts with access control hardware. Use it only on systems you own or have explicit written authorization to test. Users are responsible for legal compliance in their jurisdiction.

## Hardware prerequisites

- **M5Stack Cardputter ADV** (ESP32-S3FN8) — note: the *ADV* variant specifically; regular Cardputter is untested
- **M5Stack NFC Unit (PN532)** via Grove I2C — required for v0.1 card-read feature
- USB-C cable for programming and serial
- An LLM with MCP support (Claude Desktop, Claude Code, or any MCP client)

## Quickstart

> Not usable yet. This section documents the target UX for v0.1.0.

```bash
# 1. Flash firmware
git clone https://github.com/c-sprinks/pocket-field.git
cd pocket-field/firmware
pio run -t upload

# 2. Install MCP server
cd ../mcp
uv pip install -e .

# 3. Register with Claude Desktop (config snippet in docs/getting-started.md)
```

Then ask Claude: *"Read the card I just held up to the reader."*

## Documentation

- [ARCHITECTURE.md](ARCHITECTURE.md) — system design and why
- [ROADMAP.md](ROADMAP.md) — phased plan to v0.1.0 and beyond
- [docs/protocol-v1.md](docs/protocol-v1.md) — firmware ↔ MCP wire format
- [docs/getting-started.md](docs/getting-started.md) — flash + install + configure
- [docs/hardware.md](docs/hardware.md) — Cardputter ADV + PN532 wiring

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md). Issues and PRs welcome. Code of conduct applies.

## License

[MIT](LICENSE) — © 2026 Chris Sprinkles and contributors.
