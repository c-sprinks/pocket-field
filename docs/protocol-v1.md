# Protocol v1 — firmware ↔ MCP wire format

**Status: draft.** Stable with `v0.1.0`.

## Transport

- **Physical**: USB serial (CDC-ACM on ESP32-S3)
- **Baud**: 115200
- **Framing**: 8 data bits, no parity, 1 stop bit
- **Flow control**: none
- **Line terminator**: `\n` (0x0A) — NOT `\r\n`
- **Encoding**: UTF-8

## Frame structure

Every line is exactly one of four frame types, distinguished by the first token.

### Request

```
REQ <id> <command> [space-separated args…]\n
```

- `<id>` — integer 1-65535, chosen by the host. Echoed in all responses.
- `<command>` — dotted path, e.g. `nfc.read`, `system.version`
- Args are free-form; feature modules define their own syntax.

Example:
```
REQ 42 nfc.read timeout=5000
```

### Success response

```
OK <id> <json_result>\n
```

- `<id>` — same as the request
- `<json_result>` — valid JSON object

Example:
```
OK 42 {"uid":"04:A3:FC:92","type":"mifare_classic","facility_code":103,"card_number":4821}
```

### Error response

```
ERR <id> <error_code> <human_message>\n
```

- `<error_code>` — integer from the error catalog below
- `<human_message>` — UTF-8 string, no newlines

Example:
```
ERR 42 42 no tag detected within timeout
```

### Streaming frames (for long-running commands)

```
STREAM <id> <json_chunk>\n
STREAM <id> <json_chunk>\n
…
END <id>\n
```

- Every STREAM frame carries a valid JSON object chunk
- Stream is terminated by exactly one END frame with the same id
- A command MAY emit zero or more STREAM frames before the final OK/ERR/END
- Error during streaming: an ERR frame replaces END

## Version negotiation

The MCP server MUST issue `system.version` as the first command after opening the serial port. The firmware responds with:

```
OK <id> {"protocol":"1","firmware":"0.1.0","hardware":"cardputter-adv"}
```

If `protocol` is not `"1"`, the MCP server refuses to proceed and surfaces an error to the LLM.

Breaking changes bump `protocol` to `"2"`. Additive, backwards-compatible changes stay at `"1"` and use the firmware version to gate feature usage.

## Error code catalog

| Code | Name | Meaning |
|------|------|---------|
| 1 | `UNKNOWN_COMMAND` | The command name is not registered. |
| 2 | `BAD_ARGUMENTS` | Argument parsing failed. |
| 3 | `NOT_IMPLEMENTED` | Recognized command, no implementation yet. |
| 10 | `HARDWARE_MISSING` | Required peripheral not detected (e.g., PN532 not on I2C). |
| 11 | `HARDWARE_BUSY` | Peripheral is in use by another command. |
| 12 | `HARDWARE_FAILURE` | Peripheral returned an unexpected error. |
| 20 | `TIMEOUT` | Command did not complete within its timeout. |
| 30 | `PROTOCOL_VERSION_MISMATCH` | Host spoke an incompatible protocol version. |
| 42 | `NFC_NO_TAG` | No tag within NFC field during scan. |
| 43 | `NFC_UNSUPPORTED_TAG` | Tag detected but type is not supported. |
| 44 | `NFC_READ_FAILURE` | Tag detected, read attempt failed. |
| 255 | `INTERNAL_ERROR` | Unexpected firmware state. Bug report welcome. |

Codes 100-199 reserved for feature modules to define as needed.

## v1 commands (initial set)

Feature modules MAY register additional commands. The `system.help` command returns a machine-readable list of all commands registered in the running firmware.

### `system.version`
Returns firmware and protocol version.

Response JSON:
```json
{"protocol":"1","firmware":"0.1.0","hardware":"cardputter-adv"}
```

### `system.help`
Returns a list of registered commands and their descriptions.

Response JSON:
```json
{"commands":[
  {"name":"system.version","description":"firmware and protocol version"},
  {"name":"nfc.read","description":"scan for one NFC tag and return its data"}
]}
```

### `system.status`
Returns runtime device state.

Response JSON:
```json
{"uptime_ms":12345,"battery_pct":87,"peripherals":{"pn532":true}}
```

### `nfc.read`
Scans for a single NFC/RFID tag and returns decoded data.

Args:
- `timeout=<ms>` — optional, default 5000, max 30000

Response JSON (success):
```json
{
  "uid":"04:A3:FC:92:8B:71:23",
  "type":"mifare_classic",
  "facility_code":103,
  "card_number":4821,
  "raw_bytes":"0x67130B85"
}
```

Fields `facility_code` and `card_number` are present only when the tag was decoded as HID Wiegand 26-bit. `raw_bytes` is always present.

Possible errors: `HARDWARE_MISSING`, `NFC_NO_TAG`, `NFC_UNSUPPORTED_TAG`, `NFC_READ_FAILURE`, `TIMEOUT`.

## Design notes

- Text protocol is chosen deliberately. LLMs reason better about human-readable frames than binary RPC. See ARCHITECTURE.md §3.
- Every response echoes the request `id` so clients can correlate replies even if the firmware emits unsolicited messages in future extensions.
- Streaming is optional; commands may return a single OK/ERR if they complete fast enough.
- No authentication or encryption. USB serial is a physical-access channel; add auth only if a network transport is added later.
