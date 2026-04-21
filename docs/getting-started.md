# Getting started

> This guide documents the target UX for v0.1.0. Not all commands work yet — see [ROADMAP.md](../ROADMAP.md) for current status.

## Hardware you need

- **M5Stack Cardputter ADV** (ESP32-S3FN8)
- **M5Stack NFC Unit (PN532)** connected via Grove I2C
- **USB-C cable**
- A Linux/macOS host (Windows not yet tested)

## 1. Flash the firmware

```bash
git clone https://github.com/c-sprinks/pocket-field.git
cd pocket-field/firmware
pio run -t upload
```

Expected output: upload succeeds, Cardputter reboots, serial monitor shows `# ready`.

## 2. Install the MCP server

```bash
cd ../mcp
uv venv
source .venv/bin/activate
uv pip install -e .
```

Verify:

```bash
pocket-field-mcp --help
```

## 3. Find your serial port

```bash
ls /dev/ttyACM*      # Linux — usually /dev/ttyACM0
ls /dev/tty.usb*     # macOS
```

## 4. Register with your MCP client

### Claude Desktop

Edit `~/.config/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "pocket-field": {
      "command": "pocket-field-mcp",
      "args": ["--serial-port", "/dev/ttyACM0"]
    }
  }
}
```

Restart Claude Desktop.

### Claude Code

Create or edit `.claude/mcp.json` in your workspace:

```json
{
  "servers": {
    "pocket-field": {
      "command": "pocket-field-mcp",
      "args": ["--serial-port", "/dev/ttyACM0"]
    }
  }
}
```

## 5. Use it

Open a Claude conversation and try:

> *Read the card I'm holding up to the reader and tell me the facility code and card number.*

Claude will call the `read_card` tool, the firmware will scan the PN532, and Claude will summarize the result.

## Troubleshooting

### `Permission denied` on `/dev/ttyACM0`

Add yourself to the `dialout` group (Linux):

```bash
sudo usermod -a -G dialout $USER
# log out and back in
```

### MCP server can't find the Cardputter

- Confirm the port path with `pio device list`
- Check the firmware is actually running (`# ready` message on the serial monitor)
- Verify no other process has the port open (another terminal, PlatformIO monitor, etc.)

### `PROTOCOL_VERSION_MISMATCH`

The installed MCP server and the flashed firmware speak different protocol versions. Update whichever is older.
