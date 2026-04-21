# Changelog

All notable changes to pocket-field are documented here.
Format loosely follows [Keep a Changelog](https://keepachangelog.com/).

## [Unreleased]

No entries yet.

## [0.1.0] — 2026-04-20

First public release. **Foundation release — architecture complete, hardware
features land in subsequent versions.** See the ROADMAP for what's next.

### What works

- **Firmware** (C++/Arduino, ESP32-S3) runs on M5Stack Cardputter ADV:
  - USB CDC serial at 115200 baud (`/dev/ttyACM0`)
  - Protocol v1 text wire format (REQ / OK / ERR / STREAM / END)
  - `SerialCli` subsystem: command registry + dispatcher + typed errors
  - Built-in commands: `system.version`, `system.help`, `system.status`
  - Green boot screen on the Cardputter display
  - 17 Unity unit tests (native platform, no hardware needed for CI)

- **MCP server** (Python, `FastMCP` stdio transport):
  - `list_backends` — enumerate hardware backends
  - `device_info` — live firmware + protocol + status from the Cardputter
  - `raw` — escape hatch to send any firmware command
  - `read_card` — placeholder, returns `not_implemented`
  - `ProtocolV1Client` handles framing, timeouts, streaming, typed errors
  - Protocol version handshake on connect; refuses incompatible firmware
  - 24 pytest tests with mocked serial (no hardware required for CI)

- **Multi-backend architecture** locked in:
  - `Backend` abstract base class + `Capability` enum
  - `CardputterBackend` fully implemented
  - `Proxmark3Backend` stub raising `BackendUnavailableError` — interface
    locked for v0.2 implementation

### What doesn't work yet

- **NFC read** — the `read_card` tool returns `not_implemented`. Firmware
  has no `nfc.*` commands because no PN532 driver is wired in. Targeted for
  v0.2.0 (hardware: Adafruit PN532 breakout on Cardputter's Grove I2C).
- **125 kHz HID Prox** — needs the Proxmark3 backend (v0.3+).
- **WiFi / BLE / IR / HID keyboard / SubGHz / LoRa** — on the roadmap, not
  implemented in the firmware yet.
- **Cardputter keyboard input** — intentionally not wired in Phase 1. The
  ADV variant uses a different keyboard chip; adding it is a later concern.

### Breaking changes

None — this is the first release.

### Security / authorized use

This tool interacts with access control hardware. Use only on systems you
own or have written authorization to test. See README and `authorized use`
disclaimer.

### Verified

- `pio test -e native` → 17 Unity tests pass
- `pio run -e cardputter-adv` → firmware builds (775 KB, 23% flash)
- `pytest` → 24 Python tests pass
- `ruff check .` + `mypy src/` → clean
- Flashed and booted on a real Cardputter ADV (2026-04-20)
- End-to-end MCP round trip verified: MCP stdio client → pocket-field-mcp
  → firmware on `/dev/ttyACM0` returns live device data

[Unreleased]: https://github.com/c-sprinks/pocket-field/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/c-sprinks/pocket-field/releases/tag/v0.1.0
