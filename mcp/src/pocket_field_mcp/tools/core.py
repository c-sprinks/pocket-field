"""Core MCP tool handlers.

Each tool is a plain async function; the server registers them with FastMCP.
Tools call into backends via the BackendRegistry. They never import pyserial or
FastMCP directly — that keeps the tool logic unit-testable.
"""

from __future__ import annotations

from typing import Any

from ..backends.base import BackendError
from ..backends.cardputter import CardputterBackend
from ..backends.registry import BackendRegistry


async def list_backends(registry: BackendRegistry) -> list[dict[str, Any]]:
    """Return a summary of every registered backend."""
    return [
        {
            "name": info.name,
            "model": info.model,
            "firmware": info.firmware,
            "connected": info.connected,
            "capabilities": sorted(str(c) for c in info.capabilities),
        }
        for b in registry.all()
        for info in (b.info(),)
    ]


async def device_info(registry: BackendRegistry, backend: str = "cardputter") -> dict[str, Any]:
    """Return detailed device info for the named backend.

    Attempts to connect if not already connected. Pulls live status for the
    Cardputter backend when available.
    """
    b = registry.get(backend)
    if b is None:
        return {"error": f"unknown backend: {backend!r}"}

    try:
        b.connect()
    except BackendError as e:
        return {
            "backend": backend,
            "connected": False,
            "error": str(e),
        }
    except Exception as e:
        return {
            "backend": backend,
            "connected": False,
            "error": f"{type(e).__name__}: {e}",
        }

    info = b.info()
    result: dict[str, Any] = {
        "name": info.name,
        "model": info.model,
        "firmware": info.firmware,
        "connected": info.connected,
        "capabilities": sorted(str(c) for c in info.capabilities),
    }

    if isinstance(b, CardputterBackend) and info.connected:
        try:
            result["status"] = b.status()
        except Exception as e:
            result["status_error"] = f"{type(e).__name__}: {e}"

    return result


async def raw(registry: BackendRegistry, command: str, args: str = "") -> dict[str, Any]:
    """Send a raw protocol v1 command to the Cardputter backend.

    Escape hatch for commands that are not exposed as dedicated tools yet.
    """
    b = registry.get("cardputter")
    if b is None:
        return {"error": "cardputter backend not registered"}
    try:
        b.connect()
        assert isinstance(b, CardputterBackend)
        return b.raw(command, args)
    except Exception as e:
        return {"error": f"{type(e).__name__}: {e}"}


async def read_card(registry: BackendRegistry) -> dict[str, Any]:
    """Read an access-control card from the best available NFC backend.

    Placeholder until Phase 2 (firmware gains nfc.read via PN532 integration)
    or Phase 5 (Proxmark3 backend).
    """
    return {
        "status": "not_implemented",
        "phase": "awaiting Phase 2 (PN532 firmware support) or Phase 5 (Proxmark3 backend)",
        "message": (
            "The firmware does not yet expose an nfc.* command group, and the "
            "Proxmark3 backend is not implemented. See the project ROADMAP."
        ),
    }
