# Architecture

This document describes *why* pocket-field is built the way it is. Code-level specifics live in [docs/protocol-v1.md](docs/protocol-v1.md), backend docs, and module READMEs.

## System diagram

```
               ┌──────────────────────────────┐
               │  LLM client                  │
               │  (Claude Desktop, Claude Code│
               │   claude.ai via remote MCP…) │
               └──────────────┬───────────────┘
                              │  MCP (JSON-RPC over stdio/HTTP)
                              ▼
               ┌──────────────────────────────┐
               │  pocket-field-mcp            │   Python, official MCP SDK
               │  Exposes tools:              │
               │    read_card()               │
               │    device_info()             │
               │    raw(command: str)         │
               │    list_backends()           │
               └──────────────┬───────────────┘
                              │  routes each tool call to the
                              │  best available backend
             ┌────────────────┼────────────────┐
             ▼                ▼                ▼
     ┌──────────────┐ ┌──────────────┐ ┌──────────────┐
     │ Cardputter   │ │ Proxmark3    │ │ Future       │
     │ backend      │ │ backend      │ │ backends     │
     │ (v0.1)       │ │ (v0.3+)      │ │ …            │
     └──────┬───────┘ └──────┬───────┘ └──────────────┘
            │                │
     ┌──────▼───────┐ ┌──────▼───────┐
     │ Cardputter   │ │ Proxmark3    │
     │ ADV + PN532  │ │ Easy / RDV4  │
     │ USB serial   │ │ USB + pm3    │
     └──────────────┘ └──────────────┘
```

## Multi-backend design (the single most important decision)

`pocket-field-mcp` is **not a Cardputter wrapper**. It's a control plane for access control hardware. The same MCP tool (e.g., `read_card()`) routes to whichever backend is currently available and best-suited for the task:

| Task | Cardputter backend | Proxmark3 backend |
|---|---|---|
| Read MIFARE / iCLASS UID at 13.56 MHz | ✓ (via PN532 unit) | ✓ |
| Read HID Prox at 125 kHz | ❌ | ✓ |
| Deep RFID write/emulate/clone | ❌ | ✓ |
| WiFi recon / BLE scan | ✓ | ❌ |
| IR TX/RX | ✓ | ❌ |
| HID keyboard / BadUSB | ✓ | ❌ |
| Portable field UI (screen + keyboard) | ✓ | ❌ |

**Claude chooses.** When the user says "read this card," the MCP server checks which backends are connected and which is best-suited, and either picks automatically or asks the user. Both backends can be connected at once.

This is why v0.1 ships with only Cardputter but the code structure already has the `backends/` abstraction: adding Proxmark3 in Phase 3 is a new backend file, not a rewrite.

## Design decisions

### 1. Firmware language: C++/Arduino (PlatformIO)

Considered alternatives:
- **MicroPython**: preferred user stack (Python), BUT unknown ADV keyboard chip support, slower real-time performance on ESP32-S3, smaller community for offensive-tooling drivers.
- **ESP-IDF**: more power, steeper learning curve, no advantage for this project's scope.

**Decision**: Arduino-on-PlatformIO. Same stack as every proven Cardputter ADV firmware (Evil-Cardputer ADV, Bruce, Porkchop), so we inherit all hardware work. Python stays at the MCP layer where it's a better fit.

### 2. Firmware base: fork Evil-Cardputter ADV

Considered alternatives:
- **From scratch**: total control, but months of driver work duplicating what exists.
- **Fork Bruce**: largest feature surface, but a kitchen-sink codebase we'd fight against for narrow scope.
- **Fork Porkchop**: WiFi-focused, not relevant to our access-control-first goals.

**Decision**: Evil-Cardputter ADV. It was built specifically for the ADV variant's keyboard chip, has a clean codebase, and maps well to the "strip to essentials, add CLI" plan. Upstream uses Arduino IDE `.ino` files — we port the Cardputter target to PlatformIO as part of Phase 1. We track upstream periodically; if it goes dormant, we carry on.

### 3. Firmware ↔ MCP transport: USB serial, plain text, versioned protocol

Considered alternatives:
- **Protobuf/binary RPC** (like Flipper Zero): typed, efficient, BUT harder for LLMs to reason about and debug. [0xIvan's pi-flipper findings](https://blog.navcore.io/AI-Agents/Giving-a-Pi.dev-Agent-Hands-on-a-Flipper-Zero) confirm this empirically.
- **HTTP/WebSocket over WiFi**: convenient for remote, BUT requires WiFi provisioning on every boot and adds attack surface.
- **BLE**: similar to WiFi but lower throughput.

**Decision**: USB serial, text, JSON responses, explicit request/response IDs. LLMs read text well. USB is always available. Protocol is versioned so firmware and MCP can evolve on different cadences.

Full wire format in [docs/protocol-v1.md](docs/protocol-v1.md).

### 4. Proxmark3 ↔ MCP transport: the `pm3` CLI over subprocess

Considered alternatives:
- **Protobuf/custom serial protocol to Proxmark3**: Proxmark3 already has a well-maintained `pm3` CLI with stable command syntax. Reinventing the wheel is silly.
- **libpm3 native bindings**: possible but adds build complexity.

**Decision**: `pocket-field-mcp` spawns `pm3` as a subprocess and feeds it commands, parses output. Standard pattern for wrapping mature CLI tools. Implementation lands in Phase 3+.

### 5. Repo structure: monorepo

Firmware and MCP server ship together until there's a reason to split. For an early-stage project with one maintainer, the friction of multiple repos outweighs the theoretical "clean separation" benefit.

### 6. Protocol versioning (Cardputter backend)

Firmware reports its protocol version via the `system.version` command. MCP server refuses to operate against incompatible versions. Breaking changes bump the major version (v1 → v2); additive changes bump minor.

This is the single most important protocol-level decision. It lets each side iterate without a synchronized flag-day release.

### 7. Error model

Backends return **typed error codes** (not free-form strings). The MCP server translates error codes into structured exceptions visible to the LLM. Rationale: LLMs reason better about "error: NFC_NO_TAG_DETECTED (code 42)" than "something didn't work."

Cardputter error codes are catalogued in [docs/protocol-v1.md](docs/protocol-v1.md). Proxmark3 error translation lands with the Proxmark3 backend.

### 8. Scope discipline

v0.1.0 ships **one capability through one backend**: NFC card read via Cardputter + PN532. Not WiFi, not IR, not SubGHz, not LoRa, not Proxmark3. This is deliberate — narrow ship > broken wide ship. Features grow in subsequent releases driven by:
1. Real use cases encountered by the maintainer
2. Community demand via GitHub issues

See [ROADMAP.md](ROADMAP.md) for planned expansion.

## Component responsibilities

### Firmware (`firmware/`)

- Boots the Cardputter ADV into a ready state
- Listens on USB serial at 115200 baud for protocol v1 commands
- Dispatches commands to feature modules (NFC, system, …)
- Returns structured responses
- Never makes autonomous decisions — executes only what the host asks

### MCP server (`mcp/`)

- Exposes access control capabilities as MCP tools with typed schemas
- Discovers and manages backends (Cardputter, Proxmark3, …)
- Routes tool calls to the appropriate backend
- Parses backend responses into MCP tool results
- Validates requests before sending to backends
- Never hides backend errors — surfaces them faithfully to the LLM

### Cardputter backend (`mcp/.../backends/cardputter.py`)

- Manages the Cardputter's USB serial connection (open, reconnect, timeout, disconnect)
- Implements protocol v1 frame parsing
- Translates between MCP tool args and firmware CLI commands

### Proxmark3 backend (`mcp/.../backends/proxmark3.py`) — stub in v0.1, implemented Phase 3+

- Spawns and manages the `pm3` CLI subprocess
- Parses `pm3` output into structured results
- Handles Proxmark3-specific quirks (standalone mode, firmware versioning)

### The LLM

- Chooses when to call tools based on user intent
- Interprets structured results for the user
- Handles multi-step workflows (e.g., "read card, compare to enrollment list, tell me what's missing")

Each layer has one job. Keep it that way.
