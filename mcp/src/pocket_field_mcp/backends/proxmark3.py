"""Proxmark3 backend — wraps the pm3 CLI subprocess.

Phase 5+ implementation. The stub below defines the interface and
capability surface so the rest of the code can route around it safely
until the real driver lands.

Why subprocess wrapper: the pm3 project maintains a mature CLI with
stable command syntax. Reinventing a native Proxmark3 protocol client
is wasted effort — we spawn pm3, feed it commands, parse its output.
"""

from __future__ import annotations

from dataclasses import dataclass

from .base import Backend, BackendInfo, BackendUnavailable, Capability


@dataclass
class Proxmark3Config:
    pm3_binary: str = "pm3"  # default assumes pm3 is on PATH
    device_path: str | None = None  # /dev/ttyACM0 etc., auto-detect if None


class Proxmark3Backend(Backend):
    name = "proxmark3"
    capabilities = frozenset({
        Capability.NFC_READ_13_56_MHZ,
        Capability.NFC_READ_125_KHZ,
        Capability.NFC_EMULATE,
        Capability.NFC_WRITE,
    })

    def __init__(self, config: Proxmark3Config | None = None) -> None:
        self._config = config or Proxmark3Config()
        self._connected = False

    def connect(self) -> None:
        # Phase 5: spawn pm3 subprocess, wait for READY prompt, verify firmware version.
        raise BackendUnavailable(
            "Proxmark3 backend not implemented yet — scheduled for v0.2 (see ROADMAP.md Phase 5)"
        )

    def disconnect(self) -> None:
        raise NotImplementedError("Phase 5 implementation")

    def is_connected(self) -> bool:
        return self._connected

    def info(self) -> BackendInfo:
        return BackendInfo(
            name=self.name,
            model="Proxmark3 (stub)",
            firmware="not implemented",
            capabilities=self.capabilities,
            connected=False,
        )
