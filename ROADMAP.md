# Roadmap

Public, honest, subject to change. If a phase slips, the dates update here rather than silently.

## Phase 0 — Planning and scaffolding

**Status: in progress (started 2026-04-20).**

- [x] Architecture doc, protocol spec, repo layout
- [x] MIT license, code of conduct, contribution guide
- [x] Public GitHub repo visible to community
- [ ] Hardware validation spike: Cardputter ADV + PN532 I2C comms work on Evil-Cardputter ADV base

## Phase 1 — Firmware foundation

**Target: 2-3 weeks after Phase 0 hardware spike confirms.**

- [ ] Fork Evil-Cardputter ADV into `firmware/`
- [ ] Strip to minimal boot
- [ ] Add `SerialCli` subsystem with command dispatcher and response formatter
- [ ] Implement protocol v1 commands: `version`, `help`, `status`
- [ ] Unity-based unit tests on PlatformIO native platform (no hardware required for CI)
- [ ] GitHub Actions CI green on PRs

## Phase 2 — NFC read (v0.1 headline feature)

**Target: 2-3 weeks after Phase 1.**

- [ ] PN532 I2C driver wired (reuse from upstream or Bruce reference if needed)
- [ ] `nfc.read` command returns UID for MIFARE Classic, DESFire, HID iCLASS (non-SE)
- [ ] Wiegand 26-bit decoder for HID prox — returns facility code + card number
- [ ] `nfc.info` command identifies tag type
- [ ] Bench-tested against real HID reader and known test cards
- [ ] Honest README entry: what works, what doesn't (iCLASS SE/Seos do not)

## Phase 3 — MCP server v0.1

**Target: 1 week after Phase 2.**

- [ ] Python MCP server scaffolded with official `mcp` SDK
- [ ] Tools: `read_card()`, `device_info()`, `raw(command: str)`
- [ ] Serial link with auto-reconnect, typed errors, command timeouts
- [ ] Pytest coverage with mocked serial (no hardware required for CI)
- [ ] Config snippets for Claude Desktop and Claude Code in docs

## Phase 4 — v0.1.0 public release

**Target: 1 week after Phase 3.**

- [ ] End-to-end demo video / GIF recorded
- [ ] All docs finalized and reviewed
- [ ] Tagged `v0.1.0` release with binaries (firmware .bin and .uf2) and Python package
- [ ] Announcements: r/M5Stack, r/Cardputter, r/cybersecurity, Hacker News, personal blog

## Phase 5+ — Community-driven growth

**No committed timeline.** Scope expands based on real demand and maintainer capacity.

Potential directions (not in priority order):
- WiFi scan and recon commands
- IR TX/RX
- SubGHz (requires M5 CC1101 module)
- Wiegand direct sniff (requires custom wiring)
- Glass2 HUD status display
- LoRa mesh reporting to a base station
- Multi-Cardputter coordination
- Integration with findings-logging backends (Synapse, Obsidian, plain JSON)

## Non-goals (explicitly NOT on the roadmap)

- Becoming a Bruce / Porkchop / Evil-Cardputter replacement — they cover their scope better
- Supporting the original Cardputter (non-ADV) variant unless community PRs it
- On-device LLM inference — the LLM runs on a host, full stop
- Commercial licensing — stays MIT open source
