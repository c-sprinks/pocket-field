"""CardputterBackend tests using a fake serial transport.

We monkeypatch pyserial.Serial at import time so connect() uses the fake.
"""

from __future__ import annotations

from typing import Any

import pytest

from pocket_field_mcp.backends.base import Capability
from pocket_field_mcp.backends.cardputter import CardputterBackend, CardputterConfig
from pocket_field_mcp.protocol import ErrorCode, ProtocolError


class FakeSerial:
    """Mimics pyserial.Serial well enough for CardputterBackend."""

    def __init__(self, port: str, baud: int, timeout: float) -> None:
        self.port = port
        self.baud = baud
        self.timeout = timeout
        self.is_open = True
        self.written: list[bytes] = []
        self._script: list[bytes] = []

    def queue(self, *lines: str) -> None:
        for line in lines:
            self._script.append(line.encode() + b"\n")

    def write(self, data: bytes) -> int:
        self.written.append(data)
        return len(data)

    def readline(self) -> bytes:
        if not self._script:
            return b""
        return self._script.pop(0)

    def reset_input_buffer(self) -> None:
        pass

    def close(self) -> None:
        self.is_open = False


def test_connect_and_status_roundtrip(monkeypatch: pytest.MonkeyPatch) -> None:
    """Full round trip: connect (handshake), then status() returns parsed JSON."""
    captured: dict[str, Any] = {}

    class ScriptedFake(FakeSerial):
        def __init__(self, port: str, baud: int, timeout: float) -> None:
            super().__init__(port, baud, timeout)
            captured["fake"] = self
            # Pre-seed scripted responses.
            self.queue('OK 1 {"protocol":"1","firmware":"0.0.1-test","hardware":"cardputter-adv"}')
            self.queue('OK 2 {"uptime_ms":12345,"battery_pct":-1,"peripherals":{"pn532":false}}')

    monkeypatch.setattr("pocket_field_mcp.backends.cardputter.serial.Serial", ScriptedFake)

    b = CardputterBackend(CardputterConfig(serial_port="/dev/null"))
    b.connect()
    assert b.is_connected()
    info = b.info()
    assert info.connected
    assert info.firmware == "0.0.1-test"

    status = b.status()
    assert status["uptime_ms"] == 12345
    assert status["peripherals"]["pn532"] is False

    # Verify wire traffic matches expectations.
    fake = captured["fake"]
    assert fake.written[0] == b"REQ 1 system.version\n"
    assert fake.written[1] == b"REQ 2 system.status\n"


def test_connect_rejects_wrong_protocol_version(monkeypatch: pytest.MonkeyPatch) -> None:
    class ScriptedFake(FakeSerial):
        def __init__(self, port: str, baud: int, timeout: float) -> None:
            super().__init__(port, baud, timeout)
            self.queue('OK 1 {"protocol":"2","firmware":"x","hardware":"cardputter-adv"}')

    monkeypatch.setattr("pocket_field_mcp.backends.cardputter.serial.Serial", ScriptedFake)

    b = CardputterBackend(CardputterConfig(serial_port="/dev/null"))
    with pytest.raises(ProtocolError) as exc:
        b.connect()
    assert exc.value.code == ErrorCode.PROTOCOL_VERSION_MISMATCH


def test_capabilities_advertised() -> None:
    b = CardputterBackend(CardputterConfig(serial_port="/dev/null"))
    assert b.supports(Capability.NFC_READ_13_56_MHZ)
    assert not b.supports(Capability.NFC_READ_125_KHZ)
