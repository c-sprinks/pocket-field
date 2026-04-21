"""MCP server entry point.

Phase 0 skeleton — registers no tools yet. Phase 3 wires the firmware
command surface into MCP tools.
"""

from __future__ import annotations

import argparse
import sys


def main() -> int:
    parser = argparse.ArgumentParser(
        prog="pocket-field-mcp",
        description="MCP server exposing pocket-field firmware over USB serial.",
    )
    parser.add_argument(
        "--serial-port",
        default="/dev/ttyACM0",
        help="USB serial port the Cardputter is attached to",
    )
    args = parser.parse_args()

    # Phase 3 will:
    #   1. Open SerialLink(SerialConfig(port=args.serial_port))
    #   2. Perform protocol version handshake
    #   3. Register MCP tools: read_card, device_info, raw
    #   4. Enter the MCP stdio server loop
    print(
        f"pocket-field-mcp placeholder — would connect to {args.serial_port}",
        file=sys.stderr,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
