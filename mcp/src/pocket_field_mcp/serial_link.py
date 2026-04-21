"""USB serial wrapper for the pocket-field firmware.

Phase 0 skeleton. Phase 1 implements open/reconnect/timeout logic.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class SerialConfig:
    port: str
    baud: int = 115200
    timeout_s: float = 5.0


class SerialLink:
    """Manages a single USB serial connection to the firmware.

    Responsibilities (Phase 1):
      - Open and hold the port
      - Send REQ frames with monotonic request IDs
      - Receive and parse OK / ERR / STREAM / END frames
      - Surface typed errors to callers
      - Reconnect on unexpected disconnect
    """

    def __init__(self, config: SerialConfig) -> None:
        self._config = config
        # Phase 1: open pyserial.Serial here

    def close(self) -> None:
        """Close the serial port."""
        # Phase 1 impl
