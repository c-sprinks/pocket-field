"""Cardputter backend — M5Stack Cardputter ADV over USB serial.

Talks to the pocket-field firmware using protocol v1 (docs/protocol-v1.md).
Phase 3 implementation lives here.
"""

from __future__ import annotations

from dataclasses import dataclass

from .base import Backend, BackendInfo, Capability


@dataclass
class CardputterConfig:
    serial_port: str
    baud: int = 115200
    timeout_s: float = 5.0


class CardputterBackend(Backend):
    name = "cardputter"
    capabilities = frozenset({
        Capability.NFC_READ_13_56_MHZ,
        # WiFi, BLE, IR, HID added in subsequent phases.
    })

    def __init__(self, config: CardputterConfig) -> None:
        self._config = config
        self._connected = False

    def connect(self) -> None:
        # Phase 3: open pyserial.Serial, perform protocol handshake (system.version).
        raise NotImplementedError("Phase 3 implementation")

    def disconnect(self) -> None:
        # Phase 3: close the serial port gracefully.
        raise NotImplementedError("Phase 3 implementation")

    def is_connected(self) -> bool:
        return self._connected

    def info(self) -> BackendInfo:
        return BackendInfo(
            name=self.name,
            model="M5Stack Cardputter ADV",
            firmware="unknown (not connected)" if not self._connected else "todo",
            capabilities=self.capabilities,
            connected=self._connected,
        )
