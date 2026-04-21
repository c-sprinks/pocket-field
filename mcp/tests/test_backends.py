"""Smoke tests for the backend abstraction."""

import pytest

from pocket_field_mcp.backends.base import Capability
from pocket_field_mcp.backends.cardputter import CardputterBackend, CardputterConfig
from pocket_field_mcp.backends.proxmark3 import Proxmark3Backend


def test_cardputter_advertises_13_56_mhz() -> None:
    b = CardputterBackend(CardputterConfig(serial_port="/dev/null"))
    assert b.supports(Capability.NFC_READ_13_56_MHZ)
    assert not b.supports(Capability.NFC_READ_125_KHZ)


def test_proxmark3_advertises_both_frequencies() -> None:
    b = Proxmark3Backend()
    assert b.supports(Capability.NFC_READ_13_56_MHZ)
    assert b.supports(Capability.NFC_READ_125_KHZ)
    assert b.supports(Capability.NFC_EMULATE)


def test_proxmark3_connect_raises_until_phase_5() -> None:
    b = Proxmark3Backend()
    with pytest.raises(Exception) as exc:
        b.connect()
    assert "not implemented" in str(exc.value).lower()
