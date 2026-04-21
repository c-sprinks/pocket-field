"""ProtocolV1Client tests with a mock serial transport."""

from __future__ import annotations

import pytest

from pocket_field_mcp.protocol import (
    EndFrame,
    ErrFrame,
    ErrorCode,
    OkFrame,
    ProtocolError,
    ProtocolV1Client,
    StreamFrame,
    parse_frame,
)

# ---------------------------------------------------------------------------
# parse_frame
# ---------------------------------------------------------------------------

def test_parse_ok_frame() -> None:
    f = parse_frame('OK 42 {"protocol":"1","firmware":"0.1.0"}')
    assert isinstance(f, OkFrame)
    assert f.request_id == 42
    assert f.result["protocol"] == "1"


def test_parse_err_frame() -> None:
    f = parse_frame("ERR 7 42 no tag detected")
    assert isinstance(f, ErrFrame)
    assert f.request_id == 7
    assert f.code == ErrorCode.NFC_NO_TAG
    assert f.message == "no tag detected"


def test_parse_err_frame_with_spaces_in_message() -> None:
    f = parse_frame("ERR 1 1 command not registered: nfc.read")
    assert isinstance(f, ErrFrame)
    assert f.message == "command not registered: nfc.read"


def test_parse_stream_frame() -> None:
    f = parse_frame('STREAM 5 {"i":1,"x":2}')
    assert isinstance(f, StreamFrame)
    assert f.chunk == {"i": 1, "x": 2}


def test_parse_end_frame() -> None:
    f = parse_frame("END 5")
    assert isinstance(f, EndFrame)
    assert f.request_id == 5


def test_parse_unknown_prefix_raises() -> None:
    with pytest.raises(ProtocolError) as exc:
        parse_frame("WEIRD 1 blah")
    assert exc.value.code == ErrorCode.INTERNAL_ERROR


# ---------------------------------------------------------------------------
# ProtocolV1Client over a fake transport
# ---------------------------------------------------------------------------

class FakeSerial:
    """In-memory serial transport for ProtocolV1Client tests."""

    def __init__(self, script: list[bytes]) -> None:
        self.written: list[bytes] = []
        self._responses = list(script)

    def write(self, data: bytes) -> int:
        self.written.append(data)
        return len(data)

    def readline(self) -> bytes:
        if not self._responses:
            return b""
        return self._responses.pop(0)

    def reset_input_buffer(self) -> None:
        # no-op for the fake
        pass


def test_client_sends_req_and_parses_ok() -> None:
    fake = FakeSerial([b'OK 1 {"protocol":"1","firmware":"x","hardware":"cardputter-adv"}\n'])
    c = ProtocolV1Client(fake)
    result = c.send_request("system.version")
    assert result["protocol"] == "1"
    # The client should have sent REQ 1 system.version\n
    assert fake.written == [b"REQ 1 system.version\n"]


def test_client_ignores_comment_lines() -> None:
    fake = FakeSerial([
        b"# firmware boot banner\n",
        b"# ready\n",
        b'OK 1 {"ok":true}\n',
    ])
    c = ProtocolV1Client(fake)
    assert c.send_request("system.version") == {"ok": True}


def test_client_raises_on_err_frame() -> None:
    fake = FakeSerial([b"ERR 1 1 command not registered: bogus\n"])
    c = ProtocolV1Client(fake)
    with pytest.raises(ProtocolError) as exc:
        c.send_request("bogus")
    assert exc.value.code == ErrorCode.UNKNOWN_COMMAND


def test_client_timeout_when_no_response() -> None:
    fake = FakeSerial([b""])  # readline returns empty -> timeout
    c = ProtocolV1Client(fake)
    with pytest.raises(ProtocolError) as exc:
        c.send_request("system.version")
    assert exc.value.code == ErrorCode.TIMEOUT


def test_client_handles_stream_then_end() -> None:
    fake = FakeSerial([
        b'STREAM 1 {"i":1}\n',
        b'STREAM 1 {"i":2}\n',
        b"END 1\n",
    ])
    c = ProtocolV1Client(fake)
    result = c.send_request("something.streamy")
    assert result == {"stream": [{"i": 1}, {"i": 2}]}


def test_client_increments_request_ids() -> None:
    fake = FakeSerial([
        b'OK 1 {"a":1}\n',
        b'OK 2 {"b":2}\n',
    ])
    c = ProtocolV1Client(fake)
    c.send_request("first")
    c.send_request("second")
    assert fake.written == [b"REQ 1 first\n", b"REQ 2 second\n"]
