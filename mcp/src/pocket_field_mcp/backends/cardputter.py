"""Cardputter backend — M5Stack Cardputter ADV over USB serial.

Talks to the pocket-field firmware using protocol v1.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import serial  # type: ignore[import-untyped]

from ..protocol import (
    PROTOCOL_VERSION,
    ErrorCode,
    ProtocolError,
    ProtocolV1Client,
)
from .base import Backend, BackendInfo, Capability


@dataclass
class CardputterConfig:
    serial_port: str
    baud: int = 115200
    timeout_s: float = 5.0


class CardputterBackend(Backend):
    name = "cardputter"
    # These describe what this backend *can* support once the matching firmware
    # feature modules are wired. Phase 1 firmware only exposes system.*; Phase 2
    # adds NFC. Callers should consult `info().firmware` and `help()` for live
    # capability details.
    capabilities = frozenset({Capability.NFC_READ_13_56_MHZ})

    def __init__(self, config: CardputterConfig) -> None:
        self._config = config
        self._serial: serial.Serial | None = None
        self._client: ProtocolV1Client | None = None
        self._firmware_info: dict[str, Any] | None = None

    # ---- lifecycle ----------------------------------------------------------

    def connect(self) -> None:
        if self._serial is not None and self._serial.is_open:
            return
        self._serial = serial.Serial(
            self._config.serial_port,
            self._config.baud,
            timeout=self._config.timeout_s,
        )
        self._client = ProtocolV1Client(self._serial)
        # Immediately do the protocol version handshake.
        info = self._client.send_request("system.version")
        fw_proto = info.get("protocol")
        if fw_proto != PROTOCOL_VERSION:
            self.disconnect()
            raise ProtocolError(
                ErrorCode.PROTOCOL_VERSION_MISMATCH,
                f"firmware speaks protocol {fw_proto!r}, "
                f"mcp server expects {PROTOCOL_VERSION!r}",
            )
        self._firmware_info = info

    def disconnect(self) -> None:
        if self._serial is not None:
            try:
                self._serial.close()
            except Exception:
                # best-effort — we're tearing down anyway
                pass
        self._serial = None
        self._client = None
        self._firmware_info = None

    def is_connected(self) -> bool:
        return self._serial is not None and self._serial.is_open

    # ---- info ---------------------------------------------------------------

    def info(self) -> BackendInfo:
        firmware = "(not connected)"
        if self._firmware_info:
            firmware = str(self._firmware_info.get("firmware", "unknown"))
        return BackendInfo(
            name=self.name,
            model="M5Stack Cardputter ADV",
            firmware=firmware,
            capabilities=self.capabilities,
            connected=self.is_connected(),
        )

    # ---- typed commands -----------------------------------------------------

    def status(self) -> dict[str, Any]:
        """Return parsed `system.status` from the firmware."""
        self._ensure_connected()
        assert self._client is not None
        return self._client.send_request("system.status")

    def help(self) -> dict[str, Any]:
        """Return firmware-registered command list (`system.help`)."""
        self._ensure_connected()
        assert self._client is not None
        return self._client.send_request("system.help")

    def raw(self, command: str, args: str = "") -> dict[str, Any]:
        """Escape hatch — send any command the firmware exposes."""
        self._ensure_connected()
        assert self._client is not None
        return self._client.send_request(command, args)

    # ---- internal -----------------------------------------------------------

    def _ensure_connected(self) -> None:
        if not self.is_connected():
            self.connect()
