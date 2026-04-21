# Architecture

This document describes *why* pocket-field is built the way it is. Code-level specifics live in [docs/protocol-v1.md](docs/protocol-v1.md) and module READMEs.

## System diagram

```
┌──────────────────────────┐       Claude API         ┌──────────────────┐
│  LLM client              │ ◄──────────────────────► │  Anthropic cloud │
│  (Claude Desktop,        │                          └──────────────────┘
│   Claude Code, claude.ai │
│   with remote MCP, etc.) │
└─────────┬────────────────┘
          │  MCP (JSON-RPC over stdio or HTTP)
          ▼
┌──────────────────────────┐
│  pocket-field-mcp        │    Python, official MCP SDK, pyserial
│  (local or on PocketPi)  │    Tools: read_card, device_info, raw
└─────────┬────────────────┘
          │  USB serial — 115200 baud, protocol v1
          ▼
┌──────────────────────────┐
│  pocket-field-fw         │    C++/Arduino, fork of Evil-Cardputter ADV
│  (Cardputter ADV)        │    Serial CLI + feature modules (NFC, …)
└─────────┬────────────────┘
          │  I2C (Grove)
          ▼
┌──────────────────────────┐
│  PN532 NFC Unit          │    13.56 MHz NFC/RFID
└──────────────────────────┘
```

## Design decisions

### 1. Firmware language: C++/Arduino (PlatformIO)

Considered alternatives:
- **MicroPython**: preferred user stack (Python), BUT unknown ADV keyboard chip support, slower real-time performance on ESP32-S3, smaller community for offensive-tooling drivers.
- **ESP-IDF**: more power, steeper learning curve, no advantage for this project's scope.

**Decision**: Arduino-on-PlatformIO. Same stack as every proven Cardputter ADV firmware (Evil-Cardputter ADV, Bruce, Porkchop), so we inherit all hardware work. Python stays at the MCP layer where it's a better fit.

### 2. Firmware base: fork Evil-Cardputter ADV

Considered alternatives:
- **From scratch**: total control, but months of driver work duplicating what exists.
- **Fork Bruce**: largest feature surface, but a kitchen-sink codebase we'd fight against for narrow scope.
- **Fork Porkchop**: WiFi-focused, not relevant to our access-control-first goals.

**Decision**: Evil-Cardputter ADV. It was built specifically for the ADV variant's keyboard chip, has a clean codebase, and maps well to the "strip to essentials, add CLI" plan. We track upstream periodically; if it goes dormant, we carry on.

### 3. Transport: USB serial, plain text, versioned protocol

Considered alternatives:
- **Protobuf/binary RPC** (like Flipper Zero): typed, efficient, BUT harder for LLMs to reason about and debug. [0xIvan's pi-flipper findings](https://blog.navcore.io/AI-Agents/Giving-a-Pi.dev-Agent-Hands-on-a-Flipper-Zero) confirm this empirically.
- **HTTP/WebSocket over WiFi**: convenient for remote, BUT requires WiFi provisioning on every boot and adds attack surface.
- **BLE**: similar to WiFi but lower throughput.

**Decision**: USB serial, text, JSON responses, explicit request/response IDs. LLMs read text well. USB is always available. Protocol is versioned so firmware and MCP can evolve on different cadences.

Full wire format in [docs/protocol-v1.md](docs/protocol-v1.md).

### 4. Repo structure: monorepo

Firmware and MCP server ship together until there's a reason to split. For a v0.1 project with one maintainer, the friction of two repos outweighs the theoretical "clean separation" benefit.

Path forward if it grows: split `firmware/` and `mcp/` into separate repos with a shared `protocol/` repo.

### 5. Protocol versioning

Firmware reports its protocol version via the `version` command. MCP server refuses to operate against incompatible versions. Breaking changes to the wire format bump the major version (v1 → v2); additive changes bump the minor.

This is the single most important design decision. It lets each side iterate without a synchronized flag-day release.

### 6. Error model

The firmware returns **typed error codes** (numbers) plus human-readable messages. The MCP server translates error codes into structured exceptions. Rationale: LLMs reason better about "error: NFC_NO_TAG_DETECTED (code 42)" than "something didn't work."

Error codes are catalogued in [docs/protocol-v1.md](docs/protocol-v1.md).

### 7. Scope discipline

v0.1.0 ships **one** capability: NFC card read. Not WiFi, not IR, not SubGHz, not LoRa. This is deliberate — narrow ship > broken wide ship. Features grow in subsequent releases driven by:
1. Real use cases encountered by the maintainer
2. Community demand via GitHub issues

See [ROADMAP.md](ROADMAP.md) for planned expansion.

## Component responsibilities

### Firmware (`firmware/`)

- Boots the Cardputter ADV into a ready state
- Listens on USB serial at 115200 baud for protocol v1 commands
- Dispatches commands to feature modules (NFC, system, …)
- Returns structured responses
- Never makes autonomous decisions — it only executes what the host asks

### MCP server (`mcp/`)

- Exposes firmware capabilities as MCP tools with typed schemas
- Manages the serial connection (open, reconnect, timeout, disconnect)
- Parses protocol v1 responses into MCP tool results
- Validates requests before sending to firmware
- Never hides firmware errors — surfaces them faithfully to the LLM

### The LLM

- Chooses when to call tools based on user intent
- Interprets structured results for the user
- Handles multi-step workflows (e.g., "read card, compare to enrollment list, tell me what's missing")

Each layer has one job. Keep it that way.
