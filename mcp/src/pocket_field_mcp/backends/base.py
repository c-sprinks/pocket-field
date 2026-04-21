"""Abstract Backend interface.

Every hardware backend (Cardputter, Proxmark3, future contact readers, etc.)
implements this interface. The MCP server routes tool calls to whichever
backend is currently connected and best-suited for the task.

Design notes:
- Backends are stateful — they hold open hardware connections.
- Backends advertise `capabilities` so the server / LLM can pick the right one.
- Errors are typed (see `BackendError` subclasses), not free-form strings.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum


class Capability(str, Enum):
    """What a backend can do. Used for routing decisions."""

    NFC_READ_13_56_MHZ = "nfc_read_13_56_mhz"
    NFC_READ_125_KHZ = "nfc_read_125_khz"
    NFC_EMULATE = "nfc_emulate"
    NFC_WRITE = "nfc_write"
    WIFI_SCAN = "wifi_scan"
    BLE_SCAN = "ble_scan"
    IR_TX = "ir_tx"
    IR_RX = "ir_rx"
    HID_KEYBOARD = "hid_keyboard"


@dataclass(frozen=True)
class BackendInfo:
    """Summary returned by `device_info()` and `list_backends()`."""

    name: str
    model: str
    firmware: str
    capabilities: frozenset[Capability]
    connected: bool


class BackendError(Exception):
    """Base class for backend errors."""


class BackendUnavailable(BackendError):
    """Backend hardware is not currently connected."""


class BackendTimeout(BackendError):
    """Backend took too long to respond."""


class Backend(ABC):
    """Abstract interface every hardware backend must implement."""

    name: str
    capabilities: frozenset[Capability]

    @abstractmethod
    def connect(self) -> None:
        """Open the hardware connection."""

    @abstractmethod
    def disconnect(self) -> None:
        """Close the hardware connection."""

    @abstractmethod
    def is_connected(self) -> bool:
        """Whether the hardware connection is currently live."""

    @abstractmethod
    def info(self) -> BackendInfo:
        """Return structured backend metadata."""

    def supports(self, cap: Capability) -> bool:
        """Whether this backend advertises the given capability."""
        return cap in self.capabilities
