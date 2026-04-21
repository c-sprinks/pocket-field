"""BackendRegistry tests."""

from __future__ import annotations

import pytest

from pocket_field_mcp.backends.base import Backend, BackendInfo, Capability
from pocket_field_mcp.backends.registry import BackendRegistry


class _StubBackend(Backend):
    def __init__(self, name: str, caps: frozenset[Capability], connected: bool = False) -> None:
        self.name = name
        self.capabilities = caps
        self._connected = connected

    def connect(self) -> None:
        self._connected = True

    def disconnect(self) -> None:
        self._connected = False

    def is_connected(self) -> bool:
        return self._connected

    def info(self) -> BackendInfo:
        return BackendInfo(
            name=self.name,
            model="stub",
            firmware="stub",
            capabilities=self.capabilities,
            connected=self._connected,
        )


def test_register_and_get() -> None:
    r = BackendRegistry()
    b = _StubBackend("foo", frozenset({Capability.NFC_READ_13_56_MHZ}))
    r.register(b)
    assert r.get("foo") is b
    assert r.get("bar") is None


def test_double_register_raises() -> None:
    r = BackendRegistry()
    r.register(_StubBackend("foo", frozenset()))
    with pytest.raises(ValueError, match="already registered"):
        r.register(_StubBackend("foo", frozenset()))


def test_with_capability_filters() -> None:
    r = BackendRegistry()
    a = _StubBackend("a", frozenset({Capability.NFC_READ_13_56_MHZ}))
    b = _StubBackend("b", frozenset({Capability.NFC_READ_125_KHZ}))
    c = _StubBackend("c", frozenset({Capability.NFC_READ_13_56_MHZ, Capability.NFC_READ_125_KHZ}))
    for x in (a, b, c):
        r.register(x)
    hi = r.with_capability(Capability.NFC_READ_13_56_MHZ)
    assert set(hi) == {a, c}
    lo = r.with_capability(Capability.NFC_READ_125_KHZ)
    assert set(lo) == {b, c}


def test_connected_returns_only_connected() -> None:
    r = BackendRegistry()
    a = _StubBackend("a", frozenset(), connected=True)
    b = _StubBackend("b", frozenset(), connected=False)
    r.register(a)
    r.register(b)
    assert r.connected() == [a]
