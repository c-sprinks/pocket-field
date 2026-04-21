# Roadmap

Public, honest, subject to change. If a phase slips, the dates update here rather than silently.

## Phase 0 — Planning and scaffolding

**Status: complete (2026-04-20).**

- [x] Architecture doc with multi-backend design
- [x] Protocol v1 spec
- [x] Repo layout (monorepo with `firmware/` + `mcp/` + backends abstraction)
- [x] MIT license, contribution guide
- [x] Public GitHub repo visible to community
- [x] CI stubs (PlatformIO build + Python lint/typecheck/test)
- [x] Hardware validation spike (2026-04-20): firmware builds + flashes + boots on real Cardputter ADV; USB CDC works; protocol v1 validated end-to-end with system.version/help/status + proper error frames. PN532 integration deferred to Phase 2 (awaiting hardware).

## Phase 1 — Firmware foundation (Cardputter)

**Target: 2-3 weeks after Phase 0 hardware spike confirms.**

- [ ] Fork Evil-Cardputter ADV (Arduino IDE source) and port the Cardputter target to PlatformIO (`firmware/`)
- [ ] Strip to minimal boot (remove captive portal, beacon spam, wardriving, etc. — out of scope)
- [ ] Add `SerialCli` subsystem with command dispatcher and response formatter
- [ ] Implement protocol v1 commands: `system.version`, `system.help`, `system.status`
- [ ] Unity-based unit tests on PlatformIO native platform (no hardware required for CI)
- [ ] GitHub Actions CI green on PRs

## Phase 2 — NFC read via Cardputter backend (v0.1 headline feature)

**Target: 2-3 weeks after Phase 1. Requires Adafruit PN532 breakout (~$10).**

- [ ] PN532 I2C driver wired into firmware
- [ ] `nfc.read` command returns UID for MIFARE Classic, DESFire, NTAG, CAC contactless
- [ ] Wiegand 26-bit decoder for HID cards at 13.56 MHz — returns facility code + card number
- [ ] `nfc.info` command identifies tag type
- [ ] Bench-tested against real HID reader and known test cards
- [ ] Honest README entry: what works, what doesn't (iCLASS SE/Seos payload is crypto-secured, 125 kHz HID Prox not supported on this backend)

## Phase 3 — MCP server v0.1 (Cardputter backend only)

**Target: 1 week after Phase 2.**

- [ ] Python MCP server scaffolded with official `mcp` SDK
- [ ] `Backend` abstract base class
- [ ] `CardputterBackend` implementation (serial link + protocol v1)
- [ ] `Proxmark3Backend` STUB that raises `NotImplementedError` — placeholder to lock the interface
- [ ] Tools: `read_card()`, `device_info()`, `raw(command: str)`, `list_backends()`
- [ ] Serial link with auto-reconnect, typed errors, command timeouts
- [ ] Pytest coverage with mocked serial (no hardware required for CI)
- [ ] Config snippets for Claude Desktop and Claude Code in docs

## Phase 4 — v0.1.0 public release

**Target: 1 week after Phase 3.**

- [ ] End-to-end demo video / GIF recorded (Cardputter reading a test card, Claude summarizing)
- [ ] All docs finalized and reviewed
- [ ] Tagged `v0.1.0` release with firmware binaries (.bin) and Python package
- [ ] Announcements: r/M5Stack, r/Cardputter, r/cybersecurity, Hacker News, personal blog

## Phase 5 — Proxmark3 backend (v0.2 expansion)

**Target: when Proxmark3 hardware arrives + ~4 weeks of dev. Not scheduled yet.**

- [ ] `Proxmark3Backend` implemented — subprocess wrapper around `pm3` CLI
- [ ] Support 125 kHz HID Prox, EM4100 reads via Proxmark3
- [ ] Support 13.56 MHz reads via Proxmark3 (covers iCLASS SE UIDs that Cardputter+PN532 struggles with)
- [ ] `read_card()` tool auto-routes to the best available backend — Proxmark3 preferred when connected
- [ ] `list_backends()` shows both Cardputter and Proxmark3 with capability flags
- [ ] Honest doc: what each backend can/can't do, when Claude should choose which

## Phase 6+ — Community-driven growth

**No committed timeline.** Scope expands based on real demand and maintainer capacity.

Potential directions (not in priority order):
- **Cardputter WiFi backend**: scan, recon, network discovery as MCP tools
- **Cardputter IR backend**: TX/RX as MCP tools
- **Cardputter HID/BadUSB backend**: keyboard automation (e.g., enroll card number into Pro-Watch form)
- **Cardputter SubGHz backend**: if M5 CC1101 module added
- **Contact smart card backend**: USB PC-SC reader (ACR38U, ~$15-25) for CAC contact chip work
- **Glass2 HUD**: use Cardputter's Glass2 accessory as a status display
- **Roller Switch UI integration**
- **LoRa mesh reporting**: send findings to a base station when out of WiFi range
- **Integration with findings-logging backends**: Synapse (Chris's memory system), Obsidian, plain JSON
- **Multi-device coordination**: multiple Cardputters + one Proxmark3 in a crew

## Non-goals (explicitly NOT on the roadmap)

- Becoming a Bruce / Porkchop / Evil-Cardputter replacement — they cover their scope better
- Supporting the original Cardputter (non-ADV) variant unless community PRs it
- On-device LLM inference — the LLM runs on a host, full stop
- Commercial licensing — stays MIT open source
- iCLASS SE / Seos crypto breaking — out of scope, respect the crypto
- CAC PKI authentication — out of scope, that's DoD infrastructure
