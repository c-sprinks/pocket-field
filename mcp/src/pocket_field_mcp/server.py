"""MCP server entry point.

Exposes pocket-field backends as MCP tools over stdio transport.
"""

from __future__ import annotations

import argparse
import sys
from typing import Any

from mcp.server.fastmcp import FastMCP

from .backends.cardputter import CardputterBackend, CardputterConfig
from .backends.proxmark3 import Proxmark3Backend
from .backends.registry import BackendRegistry
from .tools import core as core_tools

_mcp = FastMCP("pocket-field")
_registry = BackendRegistry()


@_mcp.tool()
async def list_backends() -> list[dict[str, Any]]:
    """List every registered hardware backend with its capabilities and
    current connection state."""
    return await core_tools.list_backends(_registry)


@_mcp.tool()
async def device_info(backend: str = "cardputter") -> dict[str, Any]:
    """Return detailed info for a backend (model, firmware version,
    capabilities, live status).

    Args:
        backend: Backend name (e.g. 'cardputter' or 'proxmark3').
    """
    return await core_tools.device_info(_registry, backend)


@_mcp.tool()
async def raw(command: str, args: str = "") -> dict[str, Any]:
    """Send a raw protocol v1 command to the Cardputter firmware.

    Escape hatch for firmware commands that are not yet exposed as their own
    MCP tool. Example: `raw(command='system.help')` returns the registered
    firmware command list.

    Args:
        command: Firmware command name, e.g. 'system.help'.
        args: Optional argument string passed verbatim to the firmware.
    """
    return await core_tools.raw(_registry, command, args)


@_mcp.tool()
async def read_card() -> dict[str, Any]:
    """Read an access-control card from the best available NFC backend.

    Currently a placeholder — returns `not_implemented` until a PN532-enabled
    firmware (Phase 2) or the Proxmark3 backend (Phase 5) is available.
    """
    return await core_tools.read_card(_registry)


def _configure_registry(serial_port: str) -> None:
    """Populate the global registry based on CLI args."""
    _registry.register(CardputterBackend(CardputterConfig(serial_port=serial_port)))
    _registry.register(Proxmark3Backend())


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="pocket-field-mcp",
        description="MCP server for pocket-field hardware backends.",
    )
    parser.add_argument(
        "--serial-port",
        default="/dev/ttyACM0",
        help="USB serial port the Cardputter is attached to (default: /dev/ttyACM0)",
    )
    args = parser.parse_args(argv)

    _configure_registry(args.serial_port)

    # FastMCP.run() runs the stdio server event loop.
    _mcp.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
