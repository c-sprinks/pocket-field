"""Protocol constant smoke tests."""

from pocket_field_mcp.protocol import PROTOCOL_VERSION, ErrorCode


def test_protocol_version_is_v1() -> None:
    assert PROTOCOL_VERSION == "1"


def test_error_codes_match_spec() -> None:
    # Spot check — full catalog lives in docs/protocol-v1.md
    assert ErrorCode.UNKNOWN_COMMAND == 1
    assert ErrorCode.HARDWARE_MISSING == 10
    assert ErrorCode.TIMEOUT == 20
    assert ErrorCode.NFC_NO_TAG == 42
    assert ErrorCode.INTERNAL_ERROR == 255
