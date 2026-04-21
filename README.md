# pocket-field

**MCP server + firmware for driving access control hardware from an LLM.**

Ask Claude — "what's connected?" or "read this access card" — and route the request through real firmware on real hardware. Starts with the M5Stack Cardputter ADV; designed from day 1 to add more hardware backends (Proxmark3, contact smart card readers, etc.) behind the same MCP tool surface.

> **Current release: v0.1.0 (foundation) — 2026-04-20.**
>
> Protocol, firmware, MCP server, and Cardputter backend are live and verified
> end-to-end. **NFC card reading is not implemented yet** — see [CHANGELOG](CHANGELOG.md)
> for what works today and [ROADMAP](ROADMAP.md) for what's next.

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

```bash
# 1. Flash firmware to a connected Cardputter ADV
git clone https://github.com/c-sprinks/pocket-field.git
cd pocket-field/firmware
pio run -e cardputter-adv -t upload

# 2. Install MCP server
cd ../mcp
python3 -m venv .venv
source .venv/bin/activate
pip install -e .

# 3. Register with Claude Desktop (config snippet in docs/getting-started.md)
```

Then ask Claude: *"What's connected? What's the Cardputter's status?"* — Claude
will call `list_backends` and `device_info`, open the serial port, negotiate
protocol v1, and return live firmware data.

Card reading is not supported in v0.1.0 — see [CHANGELOG](CHANGELOG.md) and
[ROADMAP](ROADMAP.md).

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
