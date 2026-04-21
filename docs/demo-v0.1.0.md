# v0.1.0 end-to-end demo transcript

Recorded 2026-04-20 against a real Cardputter ADV flashed with pocket-field
firmware 0.0.1-dev, driven by an MCP stdio client calling the four registered
tools.

## Setup

- Host: Linux (Ubuntu questing), `/dev/ttyACM0` owned by `dialout`
- Device: M5Stack Cardputter ADV running pocket-field firmware 0.0.1-dev
- MCP server: `pocket-field-mcp --serial-port /dev/ttyACM0`

## list_backends

```
{
  "name": "cardputter",
  "model": "M5Stack Cardputter ADV",
  "firmware": "(not connected)",
  "connected": false,
  "capabilities": ["nfc_read_13_56_mhz"]
}
```

Note: `firmware` reads `(not connected)` until `device_info` triggers the
open. `capabilities` describes what the backend can support *when the
hardware and firmware feature modules are in place* — not the currently
active command list. Use `device_info` for the live status.

## device_info

```
{
  "name": "cardputter",
  "model": "M5Stack Cardputter ADV",
  "firmware": "0.0.1-dev",
  "connected": true,
  "capabilities": ["nfc_read_13_56_mhz"],
  "status": {
    "uptime_ms": 396695,
    "battery_pct": -1,
    "peripherals": {"pn532": false}
  }
}
```

Every field is live from the firmware: `firmware` from `system.version`,
`uptime_ms` from `millis()`, `pn532: false` because no PN532 module is
attached yet.

## raw(command="system.help")

```
{
  "commands": [
    {"name": "system.version", "description": "firmware and protocol version"},
    {"name": "system.help",    "description": "list registered commands"},
    {"name": "system.status",  "description": "runtime device state"}
  ]
}
```

The escape-hatch tool. Any firmware command name works here — useful for
debugging or driving commands that aren't yet first-class MCP tools.

## read_card (placeholder)

```
{
  "status": "not_implemented",
  "phase": "awaiting Phase 2 (PN532 firmware support) or Phase 5 (Proxmark3 backend)",
  "message": "The firmware does not yet expose an nfc.* command group, and the Proxmark3 backend is not implemented. See the project ROADMAP."
}
```

Deliberately honest placeholder. Returns immediately, surfaces the fact
that v0.1.0 has no NFC support, and points users to the roadmap.
