# pocket-field

**MCP server + firmware for driving access control hardware from an LLM.**

Ask Claude — "read this access card, tell me the facility code and card number" — and get a real answer back from real hardware. Starts with the M5Stack Cardputter ADV; designed from day 1 to add more hardware backends (Proxmark3, contact smart card readers, etc.) behind the same MCP tool surface.

> **Status: pre-release / in development.** Nothing ships yet. Target first release: v0.1.0 with Cardputter + NFC card read. See [ROADMAP](ROADMAP.md).

---

## What this is

Three pieces in one monorepo:

1. **`firmware/`** — C++/Arduino firmware for the M5Stack Cardputter ADV (ESP32-S3), forked from [Evil-Cardputer ADV](https://github.com/7h30th3r0n3/Evil-M5Project). Exposes a versioned text protocol over USB serial that an LLM can reliably parse.
2. **`mcp/`** — Python MCP ([Model Context Protocol](https://modelcontextprotocol.io/)) server that exposes access control tools to Claude. Supports **multiple hardware backends** — Cardputter today, Proxmark3 and others on the roadmap.
3. **Versioned protocols** between components, so firmware and MCP server can ship independently.

## Who this is for

Field technicians, pentesters, and hobbyists who work with access control hardware and want to drive it from an LLM instead of a GUI or menu. Particularly useful for **card enrollment, reader commissioning, and on-site diagnostics**.

Not a replacement for Bruce, Porkchop, Evil-Cardputter, or the Proxmark3 client — a different philosophy: **one MCP tool surface across all your hardware**, machine-readable, automation-first.

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
